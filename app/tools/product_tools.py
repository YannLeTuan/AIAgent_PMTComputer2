from sqlalchemy import or_

from app.core.utils import normalize_text
from app.db.models import Product
from app.db.session import SessionLocal


def expand_keywords(keyword: str):
    k = normalize_text(keyword)

    alias_map = {
        "o cung": ["ssd", "hdd", "storage"],
        "ổ cứng": ["ssd", "hdd", "storage"],
        "ssd": ["ssd", "nvme", "sata"],
        "hdd": ["hdd"],
        "card man hinh": ["vga", "gpu", "rtx", "gtx"],
        "card màn hình": ["vga", "gpu", "rtx", "gtx"],
        "vga": ["vga", "gpu", "rtx", "gtx"],
        "chuot": ["mouse", "chuot", "logitech", "razer"],
        "chuột": ["mouse", "chuot", "logitech", "razer"],
        "ban phim": ["keyboard", "ban phim", "akko", "logitech"],
        "bàn phím": ["keyboard", "ban phim", "akko", "logitech"],
        "nguon": ["psu", "power", "nguon", "corsair", "seasonic", "cooler master"],
        "nguồn": ["psu", "power", "nguon", "corsair", "seasonic", "cooler master"],
        "main": ["mainboard", "motherboard", "main", "asus", "msi", "gigabyte"],
        "mainboard": ["mainboard", "motherboard", "main", "asus", "msi", "gigabyte"],
        "ram": ["ram", "ddr4", "ddr5", "kingston", "corsair"],
        "cpu": ["cpu", "intel", "amd", "ryzen", "core"],
        "man hinh": ["monitor", "man hinh", "dell", "lg", "aoc"],
        "màn hình": ["monitor", "man hinh", "dell", "lg", "aoc"],
        "webcam": ["webcam", "camera"],
        "tai nghe": ["headset", "tai nghe", "hyperx"]
    }

    for key, values in alias_map.items():
        if key in k:
            return list(dict.fromkeys([k] + values))

    return [k]


def build_search_conditions(tokens: list[str]):
    clauses = []
    for token in tokens:
        if not token:
            continue
        pattern = f"%{token}%"
        clauses.extend([
            Product.name.ilike(pattern),
            Product.category.ilike(pattern),
            Product.brand.ilike(pattern),
            Product.sku.ilike(pattern)
        ])
    return clauses


def get_product_details(sku_or_name: str) -> dict:
    db = SessionLocal()
    try:
        product = db.query(Product).filter(Product.sku == sku_or_name).first()
        if not product:
            pattern = f"%{sku_or_name}%"
            product = db.query(Product).filter(Product.name.ilike(pattern)).first()

        if not product:
            return {"success": False, "message": f"không tìm thấy sản phẩm '{sku_or_name}'"}

        result = {
            "success": True,
            "sku": product.sku,
            "name": product.name,
            "category": product.category,
            "brand": product.brand,
            "price": product.price,
            "stock": product.stock,
            "warranty_months": product.warranty_months,
        }
        if product.specs:
            result["specs"] = product.specs
        return result
    finally:
        db.close()


def search_product(keyword: str, limit: int = 20) -> dict:
    db = SessionLocal()
    try:
        tokens = expand_keywords(keyword)
        clauses = build_search_conditions(tokens)

        if not clauses:
            return {
                "success": True,
                "count": 0,
                "results": []
            }

        products = (
            db.query(Product)
            .filter(or_(*clauses))
            .order_by(Product.price.asc())
            .limit(max(1, min(limit, 50)))
            .all()
        )

        results = []
        for p in products:
            results.append({
                "sku": p.sku,
                "name": p.name,
                "category": p.category,
                "brand": p.brand,
                "price": p.price,
                "stock": p.stock,
                "warranty_months": p.warranty_months
            })

        return {
            "success": True,
            "count": len(results),
            "results": results
        }
    finally:
        db.close()


def list_products(category: str | None = None, brand: str | None = None, max_price: float | None = None, limit: int = 10) -> dict:
    db = SessionLocal()
    try:
        query = db.query(Product)

        if category:
            category_tokens = expand_keywords(category)
            category_clauses = []
            for token in category_tokens:
                pattern = f"%{token}%"
                category_clauses.extend([
                    Product.category.ilike(pattern),
                    Product.name.ilike(pattern)
                ])
            query = query.filter(or_(*category_clauses))

        if brand:
            brand_pattern = f"%{brand.strip()}%"
            query = query.filter(Product.brand.ilike(brand_pattern))

        if max_price is not None:
            query = query.filter(Product.price <= max_price)

        products = (
            query.order_by(Product.price.asc())
            .limit(max(1, min(limit, 20)))
            .all()
        )

        results = []
        for p in products:
            results.append({
                "sku": p.sku,
                "name": p.name,
                "category": p.category,
                "brand": p.brand,
                "price": p.price,
                "stock": p.stock,
                "warranty_months": p.warranty_months
            })

        return {
            "success": True,
            "count": len(results),
            "results": results,
            "filters": {
                "category": category,
                "brand": brand,
                "max_price": max_price,
                "limit": limit
            }
        }
    finally:
        db.close()