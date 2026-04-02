from app.tools.customer_tools import get_customer_orders
from app.tools.order_tools import check_order_status, cancel_order
from app.tools.product_tools import search_product


def main():
    print("check_order_status ORD001")
    print(check_order_status("ORD001"))

    print("\ncheck_order_status ORD003")
    print(check_order_status("ORD003"))

    print("\nsearch_product RAM")
    print(search_product("RAM"))

    print("\nsearch_product Logitech")
    print(search_product("Logitech"))

    print("\nget_customer_orders phamminhtuan.pmt@gmail.com")
    print(get_customer_orders("phamminhtuan.pmt@gmail.com"))

    print("\ncancel_order ORD001")
    print(cancel_order("ORD001", "khach doi y"))

    print("\ncheck_order_status ORD001 sau khi huy")
    print(check_order_status("ORD001"))

    print("\ncancel_order ORD003")
    print(cancel_order("ORD003", "khach muon huy sau khi da gui hang"))


if __name__ == "__main__":
    main()