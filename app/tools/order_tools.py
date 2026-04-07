from app.db.models import Customer, Order, Product
from app.db.session import SessionLocal


def check_order_status(order_code: str) -> dict:
    db = SessionLocal()
    try:
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
        db.close()


def cancel_order(order_code: str, reason: str, customer_email: str) -> dict:
    if not customer_email or not customer_email.strip():
        return {
            "success": False,
            "message": "thiếu email xác thực. Vui lòng cung cấp email đã đặt hàng để xác thực danh tính."
        }

    db = SessionLocal()
    try:
        order = db.query(Order).filter(Order.order_code == order_code).first()

        if not order:
            return {
                "success": False,
                "message": f"không tìm thấy đơn hàng {order_code}"
            }

        customer = db.query(Customer).filter(Customer.id == order.customer_id).first()
        if not customer or customer.email.lower() != customer_email.strip().lower():
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

        db.commit()

        return {
            "success": True,
            "message": f"đã hủy đơn {order_code}",
            "old_status": old_status,
            "new_status": order.status,
            "reason": reason
        }
    finally:
        db.close()


def cancel_multiple_orders(order_codes: list[str], reason: str, customer_email: str) -> dict:
    if not customer_email or not customer_email.strip():
        return {
            "success": False,
            "message": "thiếu email xác thực. Vui lòng cung cấp email đã đặt hàng để xác thực danh tính."
        }

    results = []
    success_count = 0
    failed_count = 0

    for code in order_codes:
        result = cancel_order(code, reason, customer_email=customer_email)
        results.append({
            "order_code": code,
            "result": result
        })

        if result.get("success"):
            success_count += 1
        else:
            failed_count += 1

    return {
        "success": True,
        "success_count": success_count,
        "failed_count": failed_count,
        "results": results
    }
