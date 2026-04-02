from app.db.models import Base, Customer, Order, Product
from app.db.session import SessionLocal, engine


def seed():
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)

    db = SessionLocal()

    customers = [
        Customer(name="Phạm Minh Tuấn", email="phamminhtuan.pmt@gmail.com", phone="0903123456", city="Quảng Ninh", note="khách quen và hồ sơ test nội bộ"),
        Customer(name="Nguyễn Hoàng Long", email="long.nguyen@gmail.com", phone="0904111222", city="Hải Phòng", note="khách thiên về gaming"),
        Customer(name="Trần Quốc Bảo", email="bao.tran@gmail.com", phone="0905333444", city="Đà Nẵng", note="hay mua SSD và RAM"),
        Customer(name="Lê Minh Đức", email="duc.le@gmail.com", phone="0906777888", city="Hồ Chí Minh", note="khách mới"),
        Customer(name="Phạm Gia Huy", email="huy.pham@gmail.com", phone="0908999000", city="Cần Thơ", note="ưu tiên giao nhanh"),
        Customer(name="Ngô Anh Tuấn", email="anhtuan.ngo@gmail.com", phone="0911222333", city="Hà Nội", note="hay hỏi build PC"),
        Customer(name="Vũ Thu Hà", email="thuha.vu@gmail.com", phone="0913444555", city="Nam Định", note="khách văn phòng"),
        Customer(name="Đặng Quang Huy", email="quanghuy.d@gmail.com", phone="0915666777", city="Bắc Ninh", note="khách nâng cấp máy cũ"),
        Customer(name="Trịnh Hải Nam", email="hainam.t@gmail.com", phone="0917888999", city="Hà Nội", note="quan tâm màn hình"),
        Customer(name="Đỗ Minh Quân", email="minhquan.do@gmail.com", phone="0920000111", city="Hưng Yên", note="thường hỏi VGA và nguồn")
    ]

    products = [
        Product(sku="CPU-INTEL-I5-12400F", name="Intel Core i5 12400F", category="CPU", brand="Intel", price=3590000, stock=12, warranty_months=36),
        Product(sku="CPU-INTEL-I7-12700K", name="Intel Core i7 12700K", category="CPU", brand="Intel", price=7890000, stock=6, warranty_months=36),
        Product(sku="CPU-AMD-R5-5600", name="AMD Ryzen 5 5600", category="CPU", brand="AMD", price=3190000, stock=10, warranty_months=36),
        Product(sku="CPU-AMD-R7-5700X", name="AMD Ryzen 7 5700X", category="CPU", brand="AMD", price=5690000, stock=7, warranty_months=36),

        Product(sku="RAM-KINGSTON-16GB-DDR4", name="Kingston Fury Beast 16GB DDR4 3200", category="RAM", brand="Kingston", price=890000, stock=25, warranty_months=36),
        Product(sku="RAM-KINGSTON-32GB-DDR4", name="Kingston Fury Beast 32GB DDR4 3200", category="RAM", brand="Kingston", price=1790000, stock=12, warranty_months=36),
        Product(sku="RAM-CORSAIR-16GB-DDR5", name="Corsair Vengeance 16GB DDR5 5600", category="RAM", brand="Corsair", price=1490000, stock=15, warranty_months=36),

        Product(sku="SSD-SAMSUNG-970EVO-1TB", name="Samsung 970 EVO Plus 1TB NVMe", category="SSD", brand="Samsung", price=1890000, stock=18, warranty_months=60),
        Product(sku="SSD-WD-SN770-1TB", name="WD Black SN770 1TB NVMe", category="SSD", brand="Western Digital", price=2050000, stock=11, warranty_months=60),
        Product(sku="SSD-KINGSTON-NV2-500GB", name="Kingston NV2 500GB NVMe", category="SSD", brand="Kingston", price=990000, stock=20, warranty_months=36),
        Product(sku="SSD-CRUCIAL-MX500-1TB", name="Crucial MX500 1TB SATA SSD", category="SSD", brand="Crucial", price=1790000, stock=9, warranty_months=36),

        Product(sku="HDD-WD-BLUE-1TB", name="WD Blue 1TB 7200RPM", category="HDD", brand="Western Digital", price=1090000, stock=14, warranty_months=24),
        Product(sku="HDD-SEAGATE-2TB", name="Seagate Barracuda 2TB 7200RPM", category="HDD", brand="Seagate", price=1490000, stock=10, warranty_months=24),

        Product(sku="VGA-MSI-RTX4060-8G", name="MSI GeForce RTX 4060 Ventus 8G", category="VGA", brand="MSI", price=8990000, stock=6, warranty_months=36),
        Product(sku="VGA-GIGABYTE-RTX4070", name="Gigabyte GeForce RTX 4070 Windforce 12G", category="VGA", brand="Gigabyte", price=16990000, stock=4, warranty_months=36),
        Product(sku="VGA-ASUS-RTX3050", name="ASUS Dual RTX 3050 8GB", category="VGA", brand="ASUS", price=6290000, stock=8, warranty_months=36),

        Product(sku="PSU-CORSAIR-CV650", name="Corsair CV650 650W 80 Plus Bronze", category="PSU", brand="Corsair", price=1490000, stock=16, warranty_months=36),
        Product(sku="PSU-COOLERMASTER-MWE750", name="Cooler Master MWE 750W Bronze V2", category="PSU", brand="Cooler Master", price=1890000, stock=9, warranty_months=36),
        Product(sku="PSU-SEASONIC-FOCUS650", name="Seasonic Focus GX 650W Gold", category="PSU", brand="Seasonic", price=2590000, stock=7, warranty_months=36),

        Product(sku="MAIN-ASUS-B760M", name="ASUS Prime B760M-A WiFi DDR4", category="Mainboard", brand="ASUS", price=3290000, stock=9, warranty_months=36),
        Product(sku="MAIN-MSI-B550M", name="MSI B550M PRO-VDH WiFi", category="Mainboard", brand="MSI", price=2790000, stock=10, warranty_months=36),
        Product(sku="MAIN-GIGABYTE-H610M", name="Gigabyte H610M H DDR4", category="Mainboard", brand="Gigabyte", price=1890000, stock=13, warranty_months=36),

        Product(sku="CASE-MONTECH-AIR100", name="Montech Air 100 ARGB", category="Case", brand="Montech", price=1290000, stock=10, warranty_months=12),
        Product(sku="CASE-NZXT-H510", name="NZXT H510", category="Case", brand="NZXT", price=1890000, stock=5, warranty_months=12),

        Product(sku="COOLER-DEEPCOOL-AK400", name="Deepcool AK400", category="Cooler", brand="Deepcool", price=790000, stock=14, warranty_months=12),
        Product(sku="COOLER-IDCOOLING-SE224", name="ID-Cooling SE-224-XTS", category="Cooler", brand="ID-Cooling", price=690000, stock=12, warranty_months=12),

        Product(sku="MON-DELL-P2422H", name="Dell P2422H 24 inch IPS", category="Monitor", brand="Dell", price=4290000, stock=7, warranty_months=36),
        Product(sku="MON-LG-24GN600", name="LG 24GN600 24 inch 144Hz", category="Monitor", brand="LG", price=3990000, stock=8, warranty_months=24),
        Product(sku="MON-AOC-27G2", name="AOC 27G2 27 inch 144Hz", category="Monitor", brand="AOC", price=5390000, stock=6, warranty_months=24),

        Product(sku="MOUSE-LOGI-G102", name="Logitech G102 Lightsync", category="Mouse", brand="Logitech", price=420000, stock=30, warranty_months=24),
        Product(sku="MOUSE-RAZER-DEATHADDER", name="Razer DeathAdder Essential", category="Mouse", brand="Razer", price=690000, stock=14, warranty_months=24),

        Product(sku="KB-AKKO-3087", name="Akko 3087 Mechanical Keyboard", category="Keyboard", brand="Akko", price=1590000, stock=11, warranty_months=12),
        Product(sku="KB-LOGI-G413", name="Logitech G413 Mechanical Keyboard", category="Keyboard", brand="Logitech", price=1790000, stock=8, warranty_months=24),

        Product(sku="HEADSET-HYPERX-CLOUD", name="HyperX Cloud Stinger", category="Headset", brand="HyperX", price=1190000, stock=9, warranty_months=24),
        Product(sku="WEBCAM-LOGI-C270", name="Logitech C270 HD Webcam", category="Webcam", brand="Logitech", price=690000, stock=12, warranty_months=12)
    ]

    db.add_all(customers)
    db.add_all(products)
    db.commit()

    tuan = db.query(Customer).filter_by(email="phamminhtuan.pmt@gmail.com").first()
    long = db.query(Customer).filter_by(email="long.nguyen@gmail.com").first()
    bao = db.query(Customer).filter_by(email="bao.tran@gmail.com").first()
    duc = db.query(Customer).filter_by(email="duc.le@gmail.com").first()
    huy = db.query(Customer).filter_by(email="huy.pham@gmail.com").first()
    ha = db.query(Customer).filter_by(email="thuha.vu@gmail.com").first()
    quang = db.query(Customer).filter_by(email="quanghuy.d@gmail.com").first()

    orders = [
        Order(order_code="ORD001", customer_id=tuan.id, product_name="Intel Core i5 12400F", quantity=1, total_amount=3590000, status="cancelled", note="đơn của Phạm Minh Tuấn, khách đổi ý"),
        Order(order_code="ORD002", customer_id=tuan.id, product_name="Kingston Fury Beast 16GB DDR4 3200", quantity=2, total_amount=1780000, status="processing", note="khách muốn giao giờ hành chính"),
        Order(order_code="ORD003", customer_id=long.id, product_name="MSI GeForce RTX 4060 Ventus 8G", quantity=1, total_amount=8990000, status="shipped", note="khách đã thanh toán online"),
        Order(order_code="ORD004", customer_id=bao.id, product_name="Samsung 970 EVO Plus 1TB NVMe", quantity=1, total_amount=1890000, status="delivered", note="khách yêu cầu xuất hóa đơn"),
        Order(order_code="ORD005", customer_id=duc.id, product_name="Corsair CV650 650W 80 Plus Bronze", quantity=1, total_amount=1490000, status="cancelled", note="hủy do đặt nhầm công suất nguồn"),
        Order(order_code="ORD006", customer_id=huy.id, product_name="ASUS Prime B760M-A WiFi DDR4", quantity=1, total_amount=3290000, status="pending", note="chờ xác nhận tồn kho"),
        Order(order_code="ORD007", customer_id=ha.id, product_name="Dell P2422H 24 inch IPS", quantity=2, total_amount=8580000, status="processing", note="khách văn phòng, cần giao buổi chiều"),
        Order(order_code="ORD008", customer_id=quang.id, product_name="Cooler Master MWE 750W Bronze V2", quantity=1, total_amount=1890000, status="delivered", note="khách build gaming"),
        Order(order_code="ORD009", customer_id=tuan.id, product_name="Samsung 970 EVO Plus 1TB NVMe", quantity=1, total_amount=1890000, status="delivered", note="Phạm Minh Tuấn nâng cấp SSD"),
        Order(order_code="ORD010", customer_id=tuan.id, product_name="Logitech G102 Lightsync", quantity=1, total_amount=420000, status="pending", note="đơn test nội bộ cho chatbot")
    ]

    db.add_all(orders)
    db.commit()
    db.close()

    print("seed xong")
    print("đã tạo customers, products, orders trong ecommerce.db")


if __name__ == "__main__":
    seed()