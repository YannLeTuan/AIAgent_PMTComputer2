from app.db.models import Product
from app.db.session import SessionLocal

UPGRADE_PRIORITY = {
    "gaming":    ["VGA", "CPU", "RAM", "SSD", "PSU", "Mainboard", "Cooler", "Case"],
    "office":    ["CPU", "RAM", "SSD", "Mainboard", "PSU", "Cooler", "Case"],
    "streaming": ["CPU", "VGA", "RAM", "SSD", "PSU", "Mainboard", "Cooler", "Case"],
    "graphics":  ["VGA", "CPU", "RAM", "SSD", "PSU", "Mainboard", "Cooler", "Case"],
}

BUILD_CATEGORIES = ["CPU", "Mainboard", "RAM", "VGA", "SSD", "PSU", "Case", "Cooler"]


def _find_compatible(db, category: str, max_price: float,
                     socket: str | None = None,
                     mem_type: str | None = None,
                     brand: str | None = None,
                     min_watt: int = 0,
                     mb_ff: str | None = None,
                     order_desc: bool = True):
    query = db.query(Product).filter(
        Product.category == category,
        Product.stock > 0,
        Product.price <= max_price,
    )
    if brand:
        query = query.filter(Product.brand.ilike(f"%{brand}%"))

    if order_desc:
        candidates = query.order_by(Product.price.desc()).all()
    else:
        candidates = query.order_by(Product.price.asc()).all()

    for p in candidates:
        specs = p.specs or {}
        if category == "Mainboard" and socket:
            if specs.get("socket") != socket:
                continue
        if category == "Mainboard" and mem_type:
            if mem_type not in (specs.get("memory_type") or []):
                continue
        if category == "RAM" and mem_type:
            if specs.get("type") != mem_type:
                continue
        if category == "Cooler" and socket:
            if socket not in (specs.get("socket_support") or []):
                continue
        if category == "PSU" and min_watt:
            if (specs.get("wattage") or 0) < min_watt:
                continue
        if category == "Case" and mb_ff:
            if mb_ff not in (specs.get("form_factor_support") or []):
                continue
        return p
    return None


def _to_dict(p: Product) -> dict:
    result = {
        "sku": p.sku, "name": p.name, "category": p.category,
        "brand": p.brand, "price": p.price, "warranty_months": p.warranty_months,
    }
    if p.specs:
        result["specs"] = p.specs
    return result


def build_pc_config(budget: float, use_case: str = "gaming", brand_preference: str | None = None) -> dict:
    use_key = use_case.strip().lower()
    if use_key not in UPGRADE_PRIORITY:
        return {
            "success": False,
            "message": f"use_case '{use_case}' không hợp lệ. Chọn: gaming, office, streaming, graphics."
        }
    if budget < 8_000_000:
        return {
            "success": False,
            "message": "Ngân sách tối thiểu để build PC là 8.000.000 VND."
        }

    skip_vga = (use_key == "office")
    db = None
    try:
        db = SessionLocal()
        warnings = []
        huge = 999_999_999

        cpu = _find_compatible(db, "CPU", huge, brand=brand_preference, order_desc=False)
        if not cpu:
            cpu = _find_compatible(db, "CPU", huge, order_desc=False)
        if not cpu:
            return {"success": False, "message": "Không còn CPU nào trong kho."}

        cpu_socket = (cpu.specs or {}).get("socket")

        mb = _find_compatible(db, "Mainboard", huge, socket=cpu_socket, order_desc=False)
        if not mb:
            warnings.append(f"Không có Mainboard tương thích socket {cpu_socket} trong kho. Chọn mainboard gần nhất.")
            mb = _find_compatible(db, "Mainboard", huge, order_desc=False)

        mb_specs = (mb.specs or {}) if mb else {}
        mb_ff = mb_specs.get("form_factor")
        supported_mem = mb_specs.get("memory_type", [])
        ram_type = "DDR5" if "DDR5" in supported_mem else ("DDR4" if "DDR4" in supported_mem else None)

        ram = _find_compatible(db, "RAM", huge, mem_type=ram_type, order_desc=False)

        vga = None
        if not skip_vga:
            vga = _find_compatible(db, "VGA", huge, brand=brand_preference, order_desc=False)
            if not vga:
                vga = _find_compatible(db, "VGA", huge, order_desc=False)

        ssd = _find_compatible(db, "SSD", huge, order_desc=False)

        cpu_tdp = (cpu.specs or {}).get("tdp", 65)
        vga_tdp = (vga.specs or {}).get("tdp", 0) if vga else 0
        min_watt = int((cpu_tdp + vga_tdp + 100) * 1.2)
        psu = _find_compatible(db, "PSU", huge, min_watt=min_watt, order_desc=False)

        case = _find_compatible(db, "Case", huge, mb_ff=mb_ff, order_desc=False)
        cooler = _find_compatible(db, "Cooler", huge, socket=cpu_socket, order_desc=False)

        picks = {"CPU": cpu, "Mainboard": mb, "RAM": ram, "SSD": ssd, "PSU": psu, "Case": case, "Cooler": cooler}
        if not skip_vga:
            picks["VGA"] = vga

        missing = [cat for cat, p in picks.items() if p is None]
        if missing:
            return {
                "success": False,
                "message": f"Kho hàng thiếu linh kiện: {', '.join(missing)}. Không thể build."
            }

        min_total = sum(p.price for p in picks.values())
        if min_total > budget:
            return {
                "success": False,
                "message": f"Ngân sách {budget:,.0f}đ không đủ. Cấu hình tối thiểu cần {min_total:,.0f}đ.",
                "minimum_build_cost": min_total,
            }

        remaining = budget - min_total
        priority = UPGRADE_PRIORITY[use_key]

        for cat in priority:
            if cat not in picks:
                continue
            current = picks[cat]
            upgrade_budget = current.price + remaining

            kwargs = {"order_desc": True}
            if cat == "Mainboard":
                kwargs["socket"] = cpu_socket
                kwargs["mem_type"] = ram_type
            elif cat == "RAM":
                kwargs["mem_type"] = ram_type
            elif cat == "Cooler":
                kwargs["socket"] = cpu_socket
            elif cat == "PSU":
                kwargs["min_watt"] = min_watt
            elif cat == "Case":
                kwargs["mb_ff"] = mb_ff
            if cat in ("CPU", "VGA") and brand_preference:
                kwargs["brand"] = brand_preference

            better = _find_compatible(db, cat, upgrade_budget, **kwargs)
            if not better and brand_preference and cat in ("CPU", "VGA"):
                kwargs.pop("brand", None)
                better = _find_compatible(db, cat, upgrade_budget, **kwargs)

            if better and better.id != current.id and better.price > current.price:
                gained = better.price - current.price
                remaining -= gained
                old_picks = dict(picks)
                picks[cat] = better

                # CPU socket change: re-verify mainboard, RAM, cooler compatibility
                if cat == "CPU":
                    new_socket = (better.specs or {}).get("socket")
                    if new_socket != cpu_socket:
                        new_mb = _find_compatible(db, "Mainboard", old_picks["Mainboard"].price + remaining, socket=new_socket, order_desc=True)
                        if not new_mb:
                            new_mb = _find_compatible(db, "Mainboard", huge, socket=new_socket, order_desc=False)
                        if new_mb:
                            mb_cost_diff = new_mb.price - picks["Mainboard"].price
                            new_mb_specs = new_mb.specs or {}
                            new_mem_types = new_mb_specs.get("memory_type", [])
                            new_ram_type = "DDR5" if "DDR5" in new_mem_types else ("DDR4" if "DDR4" in new_mem_types else None)
                            new_ram = _find_compatible(db, "RAM", old_picks["RAM"].price + remaining - mb_cost_diff, mem_type=new_ram_type, order_desc=True)
                            if not new_ram:
                                new_ram = _find_compatible(db, "RAM", huge, mem_type=new_ram_type, order_desc=False)
                            new_cooler = _find_compatible(db, "Cooler", old_picks["Cooler"].price + remaining - mb_cost_diff, socket=new_socket, order_desc=True)
                            if not new_cooler:
                                new_cooler = _find_compatible(db, "Cooler", huge, socket=new_socket, order_desc=False)

                            if new_ram and new_cooler:
                                extra_cost = mb_cost_diff + (new_ram.price - picks["RAM"].price) + (new_cooler.price - picks["Cooler"].price)
                                if remaining >= extra_cost:
                                    remaining -= extra_cost
                                    picks["Mainboard"] = new_mb
                                    picks["RAM"] = new_ram
                                    picks["Cooler"] = new_cooler
                                    cpu_socket = new_socket
                                    ram_type = new_ram_type
                                    mb_ff = new_mb_specs.get("form_factor")
                                    current_vga_tdp = (picks["VGA"].specs or {}).get("tdp", 0) if "VGA" in picks else 0
                                    min_watt = int(((better.specs or {}).get("tdp", 65) + current_vga_tdp + 100) * 1.2)
                                    continue
                        # rollback: no compatible combo found for new socket
                        picks = old_picks
                        remaining += gained
                        continue

        selected = {}
        total = 0
        for cat in BUILD_CATEGORIES:
            if cat in picks:
                selected[cat] = _to_dict(picks[cat])
                total += picks[cat].price

        if skip_vga:
            cpu_specs = (picks["CPU"].specs or {})
            if cpu_specs.get("igpu"):
                selected["VGA"] = {"name": "Dùng GPU tích hợp của CPU", "price": 0}
            else:
                warnings.append("CPU không có GPU tích hợp. Cần bổ sung VGA rời cho build office.")

        result = {
            "success": True,
            "use_case": use_key,
            "budget": budget,
            "total_price": total,
            "remaining_budget": budget - total,
            "components": selected,
        }
        if warnings:
            result["warnings"] = warnings

        compat = _check_selected_compatibility(selected)
        if compat["issues"]:
            result["compatibility_issues"] = compat["issues"]
        if compat["warnings"]:
            result.setdefault("warnings", []).extend(compat["warnings"])

        return result
    finally:
        if db is not None:
            db.close()


def _check_selected_compatibility(selected: dict) -> dict:
    issues = []
    warnings = []

    cpu_specs = (selected.get("CPU") or {}).get("specs", {})
    mb_specs = (selected.get("Mainboard") or {}).get("specs", {})
    ram_specs = (selected.get("RAM") or {}).get("specs", {})
    vga_specs = (selected.get("VGA") or {}).get("specs", {})
    psu_specs = (selected.get("PSU") or {}).get("specs", {})
    case_specs = (selected.get("Case") or {}).get("specs", {})
    cooler_specs = (selected.get("Cooler") or {}).get("specs", {})

    cpu_socket = cpu_specs.get("socket")
    mb_socket = mb_specs.get("socket")
    if cpu_socket and mb_socket and cpu_socket != mb_socket:
        issues.append(f"CPU socket {cpu_socket} không tương thích với Mainboard socket {mb_socket}.")

    ram_type = ram_specs.get("type")
    mb_mem_types = mb_specs.get("memory_type", [])
    if ram_type and mb_mem_types and ram_type not in mb_mem_types:
        issues.append(f"RAM {ram_type} không tương thích với Mainboard (hỗ trợ {', '.join(mb_mem_types)}).")

    mb_ff = mb_specs.get("form_factor")
    case_ff_support = case_specs.get("form_factor_support", [])
    if mb_ff and case_ff_support and mb_ff not in case_ff_support:
        issues.append(f"Case không hỗ trợ form factor {mb_ff} của Mainboard.")

    cooler_sockets = cooler_specs.get("socket_support", [])
    if cpu_socket and cooler_sockets and cpu_socket not in cooler_sockets:
        issues.append(f"Cooler không hỗ trợ socket {cpu_socket} của CPU.")

    cpu_tdp = cpu_specs.get("tdp", 0)
    vga_tdp = vga_specs.get("tdp", 0)
    psu_watt = psu_specs.get("wattage", 0)
    total_draw = cpu_tdp + vga_tdp + 100
    if psu_watt and total_draw > psu_watt:
        issues.append(f"PSU {psu_watt}W có thể không đủ cho hệ thống ({total_draw}W ước tính).")
    elif psu_watt and total_draw > psu_watt * 0.85:
        warnings.append(f"PSU {psu_watt}W đang gần ngưỡng tối đa (ước tính hệ thống dùng {total_draw}W). Nên cân nhắc nâng PSU.")

    vga_len = vga_specs.get("length_mm", 0)
    max_gpu_len = case_specs.get("max_gpu_length_mm", 9999)
    if vga_len and vga_len > max_gpu_len:
        issues.append(f"VGA dài {vga_len}mm vượt quá giới hạn {max_gpu_len}mm của Case.")

    cooler_type = cooler_specs.get("type", "")
    cooler_height = cooler_specs.get("height_mm", 0)
    max_cooler_h = case_specs.get("max_cooler_height_mm", 9999)
    if cooler_type == "air" and cooler_height and cooler_height > max_cooler_h:
        issues.append(f"Cooler cao {cooler_height}mm vượt quá giới hạn {max_cooler_h}mm của Case.")

    return {"issues": issues, "warnings": warnings}


def check_compatibility(component_skus: list[str]) -> dict:
    db = None
    try:
        db = SessionLocal()
        components = {}
        not_found = []
        for sku in component_skus:
            prod = db.query(Product).filter(Product.sku == sku).first()
            if not prod:
                prod = db.query(Product).filter(Product.name.ilike(f"%{sku}%")).first()
            if prod:
                components[prod.category] = _to_dict(prod)
            else:
                not_found.append(sku)

        if not_found:
            return {
                "success": False,
                "message": f"Không tìm thấy sản phẩm: {', '.join(not_found)}"
            }

        compat = _check_selected_compatibility(components)
        compatible = len(compat["issues"]) == 0
        result = {
            "success": True,
            "compatible": compatible,
            "components_checked": {cat: comp["name"] for cat, comp in components.items()},
        }
        if compat["issues"]:
            result["issues"] = compat["issues"]
        if compat["warnings"]:
            result["warnings"] = compat["warnings"]
        if compatible and not compat["warnings"]:
            result["message"] = "Tất cả linh kiện tương thích với nhau."
        return result
    finally:
        if db is not None:
            db.close()
