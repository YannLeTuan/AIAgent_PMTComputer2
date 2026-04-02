from app.db.models import Customer, Order
from app.db.session import SessionLocal


def get_customer_orders(customer_email: str) -> dict:
    db = SessionLocal()
    try:
        customer = db.query(Customer).filter(Customer.email == customer_email).first()

        if not customer:
            return {
                "success": False,
                "message": f"khong tim thay khach hang voi email {customer_email}"
            }

        orders = db.query(Order).filter(Order.customer_id == customer.id).all()

        data = []
        for order in orders:
            data.append({
                "order_code": order.order_code,
                "product_name": order.product_name,
                "quantity": order.quantity,
                "total_amount": order.total_amount,
                "status": order.status,
                "note": order.note
            })

        return {
            "success": True,
            "customer_name": customer.name,
            "customer_email": customer.email,
            "count": len(data),
            "orders": data
        }
    finally:
        db.close()