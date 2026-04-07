from app.db.models import Customer, Order, Product
from app.db.session import SessionLocal


def get_customer_orders(customer_email: str) -> dict:
    db = SessionLocal()
    try:
        customer = db.query(Customer).filter(Customer.email == customer_email).first()

        if not customer:
            return {
                "success": False,
                "message": f"không tìm thấy khách hàng với email {customer_email}"
            }

        orders = db.query(Order).filter(Order.customer_id == customer.id).all()

        data = []
        for order in orders:
            order_data = {
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
                    order_data["product_category"] = product.category
                    order_data["warranty_months"] = product.warranty_months

            data.append(order_data)

        return {
            "success": True,
            "customer_name": customer.name,
            "customer_email": customer.email,
            "count": len(data),
            "orders": data
        }
    finally:
        db.close()
