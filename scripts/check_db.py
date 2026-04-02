from app.db.models import Customer, Order, Product
from app.db.session import SessionLocal


def main():
    db = SessionLocal()

    customers = db.query(Customer).all()
    products = db.query(Product).all()
    orders = db.query(Order).all()

    print("customers:")
    for x in customers:
        print(x.id, x.name, x.email, x.city, x.note)

    print("\nproducts:")
    for x in products:
        print(x.id, x.sku, x.name, x.category, x.brand, x.price, x.stock)

    print("\norders:")
    for x in orders:
        print(x.id, x.order_code, x.product_name, x.status, x.total_amount, x.note)

    db.close()


if __name__ == "__main__":
    main()