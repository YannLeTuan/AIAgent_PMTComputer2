from app.db.models import Customer, Order, Product
from app.db.session import SessionLocal


def check_order_status(order_code: str) -> dict:
    db = None
    try:
        db = SessionLocal()
        order = db.query(Order).filter(Order.order_code == order_code).first()

        if not order:
            return {
                "success": False,
                "message": f"không tìm thấy đơn hàng {order_code}"
            }

        result = {
            "success": True,
            "order_code": order.order_code,
            "product_name": order.product_name,
            "quantity": order.quantity,
            "total_amount": order.total_amount,
            "status": order.status,
            "note": order.note
        }

        if order.product_id:
            product = db.query(Product).filter(Product.id == order.product_id).first()
            if product:
                result["product_category"] = product.category
                result["product_brand"] = product.brand
                result["warranty_months"] = product.warranty_months
                result["current_price"] = product.price

        return result
    finally:
        if db is not None:
            db.close()


def cancel_order(order_code: str, reason: str, customer_email: str) -> dict:
    customer_email = (customer_email or "").strip()
    if not customer_email:
        return {
            "success": False,
            "message": "thiếu email xác thực. Vui lòng cung cấp email đã đặt hàng để xác thực danh tính."
        }

    db = None
    try:
        db = SessionLocal()
        order = db.query(Order).filter(Order.order_code == order_code).first()

        if not order:
            return {
                "success": False,
                "message": f"không tìm thấy đơn hàng {order_code}"
            }

        customer = db.query(Customer).filter(Customer.id == order.customer_id).first()
        if not customer or customer.email.lower() != customer_email.lower():
            return {
                "success": False,
                "message": f"email xác thực không khớp với đơn hàng {order_code}. Vui lòng kiểm tra lại email đã đặt hàng."
            }

        if order.status in ["shipped", "delivered", "cancelled"]:
            return {
                "success": False,
                "message": f"đơn {order_code} đang ở trạng thái {order.status}, không thể hủy"
            }

        old_status = order.status
        order.status = "cancelled"

        if order.note:
            order.note = f"{order.note} | hủy đơn: {reason}"
        else:
            order.note = f"hủy đơn: {reason}"

        # restore stock atomically with the cancel
        if order.product_id and order.quantity:
            product = db.query(Product).filter(Product.id == order.product_id).first()
            if product:
                product.stock += order.quantity

        db.commit()

        return {
            "success": True,
            "message": f"đã hủy đơn {order_code}",
            "old_status": old_status,
            "new_status": order.status,
            "reason": reason
        }
    except Exception:
        if db is not None:
            db.rollback()
        raise
    finally:
        if db is not None:
            db.close()


def cancel_multiple_orders(order_codes: list[str], reason: str, customer_email: str) -> dict:
    customer_email = (customer_email or "").strip()
    if not customer_email:
        return {
            "success": False,
            "message": "thiếu email xác thực. Vui lòng cung cấp email đã đặt hàng để xác thực danh tính."
        }

    db = None
    try:
        db = SessionLocal()
        results = []
        success_count = 0
        failed_count = 0

        for code in order_codes:
            order = db.query(Order).filter(Order.order_code == code).first()
            if not order:
                results.append({"order_code": code, "result": {"success": False, "message": f"không tìm thấy đơn hàng {code}"}})
                failed_count += 1
                continue

            customer = db.query(Customer).filter(Customer.id == order.customer_id).first()
            if not customer or customer.email.lower() != customer_email.lower():
                results.append({"order_code": code, "result": {"success": False, "message": f"email xác thực không khớp với đơn hàng {code}"}})
                failed_count += 1
                continue

            if order.status in ["shipped", "delivered", "cancelled"]:
                results.append({"order_code": code, "result": {"success": False, "message": f"đơn {code} đang ở trạng thái {order.status}, không thể hủy"}})
                failed_count += 1
                continue

            old_status = order.status
            order.status = "cancelled"
            order.note = f"{order.note} | hủy đơn: {reason}" if order.note else f"hủy đơn: {reason}"

            # restore stock atomically with the cancel
            if order.product_id and order.quantity:
                product = db.query(Product).filter(Product.id == order.product_id).first()
                if product:
                    product.stock += order.quantity

            results.append({"order_code": code, "result": {"success": True, "message": f"đã hủy đơn {code}", "old_status": old_status, "new_status": "cancelled", "reason": reason}})
            success_count += 1

        db.commit()
        return {"success": True, "success_count": success_count, "failed_count": failed_count, "results": results}

    except Exception:
        if db is not None:
            db.rollback()
        raise
    finally:
        if db is not None:
            db.close()
