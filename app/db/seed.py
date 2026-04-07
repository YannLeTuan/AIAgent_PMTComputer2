from app.db.models import Base, Customer, Order, Product
from app.db.session import SessionLocal, engine


def seed():
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)

    db = SessionLocal()

    # =========================================================================
    # KHÁCH HÀNG (15)
    # =========================================================================
    customers = [
        Customer(name="Phạm Minh Tuấn",    email="phamminhtuan.pmt@gmail.com", phone="0903123456", city="Quảng Ninh",  note="khách quen, hồ sơ kiểm thử nội bộ"),
        Customer(name="Nguyễn Hoàng Long",  email="long.nguyen@gmail.com",      phone="0904111222", city="Hải Phòng",   note="khách thiên về gaming"),
        Customer(name="Trần Quốc Bảo",     email="bao.tran@gmail.com",         phone="0905333444", city="Đà Nẵng",     note="hay mua SSD và RAM"),
        Customer(name="Lê Minh Đức",       email="duc.le@gmail.com",           phone="0906777888", city="Hồ Chí Minh", note="khách mới"),
        Customer(name="Phạm Gia Huy",      email="huy.pham@gmail.com",         phone="0908999000", city="Cần Thơ",     note="ưu tiên giao nhanh"),
        Customer(name="Ngô Anh Tuấn",      email="anhtuan.ngo@gmail.com",      phone="0911222333", city="Hà Nội",      note="hay hỏi build PC"),
        Customer(name="Vũ Thu Hà",         email="thuha.vu@gmail.com",         phone="0913444555", city="Nam Định",    note="khách văn phòng"),
        Customer(name="Nguyễn Mạnh Hưng",  email="quanghuy.d@gmail.com",       phone="0915666777", city="Bắc Ninh",    note="khách nâng cấp máy cũ"),
        Customer(name="Trịnh Hải Nam",     email="hainam.t@gmail.com",         phone="0917888999", city="Hà Nội",      note="quan tâm màn hình"),
        Customer(name="Đỗ Minh Quân",      email="minhquan.do@gmail.com",      phone="0920000111", city="Hưng Yên",    note="thường hỏi VGA và nguồn"),
        Customer(name="Bùi Thị Lan",       email="buithilan@gmail.com",        phone="0922111333", city="Hà Nội",      note="hay mua bàn phím cơ và phụ kiện"),
        Customer(name="Hoàng Văn Khánh",   email="khanhvh@gmail.com",          phone="0933222444", city="Hải Dương",   note="quan tâm màn hình gaming"),
        Customer(name="Nguyễn Thị Mai",    email="mai.nguyen@yahoo.com",       phone="0944333555", city="Thái Nguyên", note="khách sinh viên, ngân sách thấp"),
        Customer(name="Lý Minh Khoa",      email="minhkhoa.ly@gmail.com",      phone="0955444666", city="Đà Lạt",      note="build máy streaming"),
        Customer(name="Vũ Đức Anh",        email="ducanh.vu@gmail.com",        phone="0966555777", city="Hà Nội",      note="quan tâm RAM DDR5 và CPU mới"),
    ]

    # =========================================================================
    # SẢN PHẨM (51) — nhóm theo danh mục, sắp xếp theo giá tăng dần
    # =========================================================================
    products = [

        # --- CPU (5) ---
        Product(sku="CPU-AMD-R5-5600",      name="AMD Ryzen 5 5600",            category="CPU",      brand="AMD",            price=3_190_000,  stock=10, warranty_months=36),
        Product(sku="CPU-INTEL-I5-12400F",  name="Intel Core i5 12400F",        category="CPU",      brand="Intel",          price=3_590_000,  stock=12, warranty_months=36),
        Product(sku="CPU-AMD-R7-5700X",     name="AMD Ryzen 7 5700X",           category="CPU",      brand="AMD",            price=5_690_000,  stock=7,  warranty_months=36),
        Product(sku="CPU-INTEL-I7-12700K",  name="Intel Core i7 12700K",        category="CPU",      brand="Intel",          price=7_890_000,  stock=6,  warranty_months=36),
        Product(sku="CPU-INTEL-I9-13900K",  name="Intel Core i9 13900K",        category="CPU",      brand="Intel",          price=13_990_000, stock=3,  warranty_months=36),

        # --- RAM (3) ---
        Product(sku="RAM-KINGSTON-16GB-DDR4", name="Kingston Fury Beast 16GB DDR4 3200", category="RAM", brand="Kingston", price=890_000,   stock=25, warranty_months=36),
        Product(sku="RAM-CORSAIR-16GB-DDR5",  name="Corsair Vengeance 16GB DDR5 5600",  category="RAM", brand="Corsair",  price=1_490_000, stock=15, warranty_months=36),
        Product(sku="RAM-KINGSTON-32GB-DDR4", name="Kingston Fury Beast 32GB DDR4 3200", category="RAM", brand="Kingston", price=1_790_000, stock=12, warranty_months=36),

        # --- SSD (4) ---
        Product(sku="SSD-KINGSTON-NV2-500GB", name="Kingston NV2 500GB NVMe",      category="SSD", brand="Kingston",        price=990_000,   stock=20, warranty_months=36),
        Product(sku="SSD-CRUCIAL-MX500-1TB",  name="Crucial MX500 1TB SATA SSD",   category="SSD", brand="Crucial",         price=1_790_000, stock=9,  warranty_months=36),
        Product(sku="SSD-SAMSUNG-970EVO-1TB", name="Samsung 970 EVO Plus 1TB NVMe", category="SSD", brand="Samsung",        price=1_890_000, stock=18, warranty_months=60),
        Product(sku="SSD-WD-SN770-1TB",       name="WD Black SN770 1TB NVMe",      category="SSD", brand="Western Digital", price=2_050_000, stock=11, warranty_months=60),

        # --- HDD (3) ---
        Product(sku="HDD-SEAGATE-1TB",    name="Seagate Barracuda 1TB 7200RPM", category="HDD", brand="Seagate",         price=1_050_000, stock=11, warranty_months=24),
        Product(sku="HDD-WD-BLUE-1TB",    name="WD Blue 1TB 7200RPM",           category="HDD", brand="Western Digital", price=1_090_000, stock=14, warranty_months=24),
        Product(sku="HDD-SEAGATE-2TB",    name="Seagate Barracuda 2TB 7200RPM", category="HDD", brand="Seagate",         price=1_490_000, stock=10, warranty_months=24),

        # --- VGA (3) ---
        Product(sku="VGA-ASUS-RTX3050",     name="ASUS Dual RTX 3050 8GB",              category="VGA", brand="ASUS",     price=6_290_000,  stock=8, warranty_months=36),
        Product(sku="VGA-MSI-RTX4060-8G",   name="MSI GeForce RTX 4060 Ventus 8G",      category="VGA", brand="MSI",      price=8_990_000,  stock=6, warranty_months=36),
        Product(sku="VGA-GIGABYTE-RTX4070",  name="Gigabyte GeForce RTX 4070 Windforce 12G", category="VGA", brand="Gigabyte", price=16_990_000, stock=4, warranty_months=36),

        # --- PSU (3) ---
        Product(sku="PSU-CORSAIR-CV650",       name="Corsair CV650 650W 80 Plus Bronze",  category="PSU", brand="Corsair",      price=1_490_000, stock=16, warranty_months=36),
        Product(sku="PSU-COOLERMASTER-MWE750",  name="Cooler Master MWE 750W Bronze V2",  category="PSU", brand="Cooler Master", price=1_890_000, stock=9,  warranty_months=36),
        Product(sku="PSU-SEASONIC-FOCUS650",    name="Seasonic Focus GX 650W Gold",        category="PSU", brand="Seasonic",     price=2_590_000, stock=7,  warranty_months=36),

        # --- Mainboard (3) ---
        Product(sku="MAIN-GIGABYTE-H610M", name="Gigabyte H610M H DDR4",        category="Mainboard", brand="Gigabyte", price=1_890_000, stock=13, warranty_months=36),
        Product(sku="MAIN-MSI-B550M",      name="MSI B550M PRO-VDH WiFi",       category="Mainboard", brand="MSI",      price=2_790_000, stock=10, warranty_months=36),
        Product(sku="MAIN-ASUS-B760M",     name="ASUS Prime B760M-A WiFi DDR4", category="Mainboard", brand="ASUS",     price=3_290_000, stock=9,  warranty_months=36),

        # --- Case (4) ---
        Product(sku="CASE-MONTECH-X3",    name="Montech X3 Mesh",       category="Case", brand="Montech",  price=990_000,   stock=13, warranty_months=12),
        Product(sku="CASE-MONTECH-AIR100", name="Montech Air 100 ARGB", category="Case", brand="Montech",  price=1_290_000, stock=10, warranty_months=12),
        Product(sku="CASE-NZXT-H510",     name="NZXT H510",             category="Case", brand="NZXT",     price=1_890_000, stock=5,  warranty_months=12),
        Product(sku="CASE-CORSAIR-4000D", name="Corsair 4000D Airflow", category="Case", brand="Corsair",  price=2_390_000, stock=7,  warranty_months=12),

        # --- Cooler (3) ---
        Product(sku="COOLER-IDCOOLING-SE224", name="ID-Cooling SE-224-XTS", category="Cooler", brand="ID-Cooling", price=690_000,   stock=12, warranty_months=12),
        Product(sku="COOLER-DEEPCOOL-AK400",  name="Deepcool AK400",        category="Cooler", brand="Deepcool",   price=790_000,   stock=14, warranty_months=12),
        Product(sku="COOLER-NOCTUA-U12S",     name="Noctua NH-U12S Redux",   category="Cooler", brand="Noctua",     price=1_290_000, stock=6,  warranty_months=12),

        # --- Màn hình (4) ---
        Product(sku="MON-LG-24GN600",    name="LG 24GN600 24 inch 144Hz",         category="Monitor", brand="LG",      price=3_990_000, stock=8, warranty_months=24),
        Product(sku="MON-DELL-P2422H",   name="Dell P2422H 24 inch IPS",          category="Monitor", brand="Dell",    price=4_290_000, stock=7, warranty_months=36),
        Product(sku="MON-AOC-27G2",      name="AOC 27G2 27 inch 144Hz",           category="Monitor", brand="AOC",     price=5_390_000, stock=6, warranty_months=24),
        Product(sku="MON-SAMSUNG-27",    name="Samsung Odyssey G5 27 inch 144Hz", category="Monitor", brand="Samsung", price=5_990_000, stock=5, warranty_months=24),

        # --- Chuột (4) ---
        Product(sku="MOUSE-LOGI-G102",       name="Logitech G102 Lightsync",    category="Mouse", brand="Logitech", price=420_000, stock=30, warranty_months=24),
        Product(sku="MOUSE-RAZER-VIPERMINI", name="Razer Viper Mini",           category="Mouse", brand="Razer",    price=590_000, stock=15, warranty_months=24),
        Product(sku="MOUSE-RAZER-DEATHADDER", name="Razer DeathAdder Essential", category="Mouse", brand="Razer",    price=690_000, stock=14, warranty_months=24),
        Product(sku="MOUSE-LOGI-G304",       name="Logitech G304 Wireless",     category="Mouse", brand="Logitech", price=790_000, stock=18, warranty_months=24),

        # --- Bàn phím (4) ---
        Product(sku="KB-AKKO-3068B",    name="Akko 3068B Plus Wireless",     category="Keyboard", brand="Akko",     price=1_390_000, stock=10, warranty_months=12),
        Product(sku="KB-AKKO-3087",     name="Akko 3087 Mechanical Keyboard", category="Keyboard", brand="Akko",    price=1_590_000, stock=11, warranty_months=12),
        Product(sku="KB-LOGI-G413",     name="Logitech G413 Mechanical Keyboard", category="Keyboard", brand="Logitech", price=1_790_000, stock=8, warranty_months=24),
        Product(sku="KB-RAZER-BWIDOW",  name="Razer BlackWidow V3 TKL",      category="Keyboard", brand="Razer",    price=2_190_000, stock=6,  warranty_months=24),

        # --- Tai nghe (3) ---
        Product(sku="HEADSET-RAZER-KRAKEN", name="Razer Kraken X USB",          category="Headset", brand="Razer",    price=990_000,   stock=12, warranty_months=24),
        Product(sku="HEADSET-HYPERX-CLOUD", name="HyperX Cloud Stinger",        category="Headset", brand="HyperX",   price=1_190_000, stock=9,  warranty_months=24),
        Product(sku="HEADSET-LOGI-G431",    name="Logitech G431 7.1 Surround",  category="Headset", brand="Logitech", price=1_490_000, stock=8,  warranty_months=24),

        # --- Webcam (3) ---
        Product(sku="WEBCAM-LOGI-C270",  name="Logitech C270 HD Webcam",       category="Webcam", brand="Logitech", price=690_000,   stock=12, warranty_months=12),
        Product(sku="WEBCAM-LOGI-C920",  name="Logitech C920 Full HD Webcam",  category="Webcam", brand="Logitech", price=1_590_000, stock=7,  warranty_months=12),
        Product(sku="WEBCAM-RAZER-KIYO", name="Razer Kiyo Streaming Webcam",   category="Webcam", brand="Razer",    price=2_290_000, stock=4,  warranty_months=12),
    ]

    db.add_all(customers)
    db.add_all(products)
    db.commit()

    # =========================================================================
    # Tra cứu để gán FK
    # =========================================================================
    tuan  = db.query(Customer).filter_by(email="phamminhtuan.pmt@gmail.com").first()
    long  = db.query(Customer).filter_by(email="long.nguyen@gmail.com").first()
    bao   = db.query(Customer).filter_by(email="bao.tran@gmail.com").first()
    duc   = db.query(Customer).filter_by(email="duc.le@gmail.com").first()
    huy   = db.query(Customer).filter_by(email="huy.pham@gmail.com").first()
    ngo   = db.query(Customer).filter_by(email="anhtuan.ngo@gmail.com").first()
    ha    = db.query(Customer).filter_by(email="thuha.vu@gmail.com").first()
    hung  = db.query(Customer).filter_by(email="quanghuy.d@gmail.com").first()
    trinh = db.query(Customer).filter_by(email="hainam.t@gmail.com").first()
    mq    = db.query(Customer).filter_by(email="minhquan.do@gmail.com").first()
    lan   = db.query(Customer).filter_by(email="buithilan@gmail.com").first()
    khanh = db.query(Customer).filter_by(email="khanhvh@gmail.com").first()
    mai   = db.query(Customer).filter_by(email="mai.nguyen@yahoo.com").first()
    khoa  = db.query(Customer).filter_by(email="minhkhoa.ly@gmail.com").first()
    danh  = db.query(Customer).filter_by(email="ducanh.vu@gmail.com").first()

    p = {prod.name: prod.id for prod in db.query(Product).all()}

    # =========================================================================
    # ĐƠN HÀNG (38) — đa dạng trạng thái, phủ nhiều khách và sản phẩm
    # =========================================================================
    orders = [
        # ORD001–ORD005: Phạm Minh Tuấn
        Order(order_code="ORD001", customer_id=tuan.id,  product_id=p["Intel Core i5 12400F"],               product_name="Intel Core i5 12400F",               quantity=1, total_amount=3_590_000,  status="cancelled",  note="khách đổi ý sau khi đặt"),
        Order(order_code="ORD002", customer_id=tuan.id,  product_id=p["Kingston Fury Beast 16GB DDR4 3200"],  product_name="Kingston Fury Beast 16GB DDR4 3200",  quantity=2, total_amount=1_780_000,  status="processing", note="giao giờ hành chính"),
        Order(order_code="ORD009", customer_id=tuan.id,  product_id=p["Samsung 970 EVO Plus 1TB NVMe"],       product_name="Samsung 970 EVO Plus 1TB NVMe",       quantity=1, total_amount=1_890_000,  status="delivered",  note="nâng cấp SSD"),
        Order(order_code="ORD010", customer_id=tuan.id,  product_id=p["Logitech G102 Lightsync"],             product_name="Logitech G102 Lightsync",             quantity=1, total_amount=420_000,    status="pending",    note="đơn thử chatbot"),
        Order(order_code="ORD023", customer_id=tuan.id,  product_id=p["MSI B550M PRO-VDH WiFi"],              product_name="MSI B550M PRO-VDH WiFi",              quantity=1, total_amount=2_790_000,  status="pending",    note="chờ xác nhận – dùng test hủy đơn"),

        # ORD003, ORD021: Nguyễn Hoàng Long
        Order(order_code="ORD003", customer_id=long.id,  product_id=p["MSI GeForce RTX 4060 Ventus 8G"],      product_name="MSI GeForce RTX 4060 Ventus 8G",      quantity=1, total_amount=8_990_000,  status="shipped",    note="đã thanh toán online"),
        Order(order_code="ORD021", customer_id=long.id,  product_id=p["Samsung 970 EVO Plus 1TB NVMe"],       product_name="Samsung 970 EVO Plus 1TB NVMe",       quantity=1, total_amount=1_890_000,  status="delivered",  note="nâng cấp storage lần 2"),

        # ORD004, ORD022: Trần Quốc Bảo
        Order(order_code="ORD004", customer_id=bao.id,   product_id=p["Samsung 970 EVO Plus 1TB NVMe"],       product_name="Samsung 970 EVO Plus 1TB NVMe",       quantity=1, total_amount=1_890_000,  status="delivered",  note="yêu cầu xuất hóa đơn"),
        Order(order_code="ORD022", customer_id=bao.id,   product_id=p["WD Black SN770 1TB NVMe"],             product_name="WD Black SN770 1TB NVMe",             quantity=1, total_amount=2_050_000,  status="processing", note="SSD thứ 2"),

        # ORD005: Lê Minh Đức
        Order(order_code="ORD005", customer_id=duc.id,   product_id=p["Corsair CV650 650W 80 Plus Bronze"],   product_name="Corsair CV650 650W 80 Plus Bronze",   quantity=1, total_amount=1_490_000,  status="cancelled",  note="đặt nhầm công suất nguồn"),

        # ORD006: Phạm Gia Huy
        Order(order_code="ORD006", customer_id=huy.id,   product_id=p["ASUS Prime B760M-A WiFi DDR4"],        product_name="ASUS Prime B760M-A WiFi DDR4",        quantity=1, total_amount=3_290_000,  status="pending",    note="chờ xác nhận tồn kho"),

        # ORD031: Ngô Anh Tuấn
        Order(order_code="ORD031", customer_id=ngo.id,   product_id=p["Corsair 4000D Airflow"],               product_name="Corsair 4000D Airflow",               quantity=1, total_amount=2_390_000,  status="delivered",  note="case cho build gaming mới"),

        # ORD007: Vũ Thu Hà
        Order(order_code="ORD007", customer_id=ha.id,    product_id=p["Dell P2422H 24 inch IPS"],             product_name="Dell P2422H 24 inch IPS",             quantity=2, total_amount=8_580_000,  status="processing", note="giao buổi chiều"),

        # ORD008, ORD036: Nguyễn Mạnh Hưng
        Order(order_code="ORD008", customer_id=hung.id,  product_id=p["Cooler Master MWE 750W Bronze V2"],    product_name="Cooler Master MWE 750W Bronze V2",    quantity=1, total_amount=1_890_000,  status="delivered",  note="build gaming"),
        Order(order_code="ORD036", customer_id=hung.id,  product_id=p["Noctua NH-U12S Redux"],                product_name="Noctua NH-U12S Redux",                quantity=1, total_amount=1_290_000,  status="processing", note="tản nhiệt cao cấp"),

        # ORD024, ORD032: Trịnh Hải Nam
        Order(order_code="ORD024", customer_id=trinh.id, product_id=p["AOC 27G2 27 inch 144Hz"],              product_name="AOC 27G2 27 inch 144Hz",              quantity=1, total_amount=5_390_000,  status="shipped",    note="màn hình gaming"),
        Order(order_code="ORD032", customer_id=trinh.id, product_id=p["Samsung Odyssey G5 27 inch 144Hz"],    product_name="Samsung Odyssey G5 27 inch 144Hz",    quantity=1, total_amount=5_990_000,  status="processing", note="màn hình gaming Samsung"),

        # ORD025, ORD034: Đỗ Minh Quân
        Order(order_code="ORD025", customer_id=mq.id,    product_id=p["Gigabyte GeForce RTX 4070 Windforce 12G"], product_name="Gigabyte GeForce RTX 4070 Windforce 12G", quantity=1, total_amount=16_990_000, status="processing", note="VGA cao cấp, cần nguồn mạnh"),
        Order(order_code="ORD034", customer_id=mq.id,    product_id=p["Logitech G304 Wireless"],              product_name="Logitech G304 Wireless",              quantity=1, total_amount=790_000,    status="delivered",  note="chuột wireless cho làm việc"),

        # ORD011, ORD016, ORD026, ORD033: Bùi Thị Lan
        Order(order_code="ORD011", customer_id=lan.id,   product_id=p["Akko 3087 Mechanical Keyboard"],       product_name="Akko 3087 Mechanical Keyboard",       quantity=1, total_amount=1_590_000,  status="pending",    note="switch blue"),
        Order(order_code="ORD016", customer_id=lan.id,   product_id=p["Logitech G102 Lightsync"],             product_name="Logitech G102 Lightsync",             quantity=1, total_amount=420_000,    status="cancelled",  note="đặt nhầm màu sắc"),
        Order(order_code="ORD026", customer_id=lan.id,   product_id=p["HyperX Cloud Stinger"],                product_name="HyperX Cloud Stinger",                quantity=1, total_amount=1_190_000,  status="delivered",  note="tai nghe gaming"),
        Order(order_code="ORD033", customer_id=lan.id,   product_id=p["Razer BlackWidow V3 TKL"],             product_name="Razer BlackWidow V3 TKL",             quantity=1, total_amount=2_190_000,  status="pending",    note="bàn phím cơ gaming"),

        # ORD012, ORD017, ORD027, ORD037: Hoàng Văn Khánh
        Order(order_code="ORD012", customer_id=khanh.id, product_id=p["LG 24GN600 24 inch 144Hz"],            product_name="LG 24GN600 24 inch 144Hz",            quantity=1, total_amount=3_990_000,  status="processing", note="giao trước cuối tuần"),
        Order(order_code="ORD017", customer_id=khanh.id, product_id=p["AOC 27G2 27 inch 144Hz"],              product_name="AOC 27G2 27 inch 144Hz",              quantity=1, total_amount=5_390_000,  status="delivered",  note="khách hài lòng, sẽ quay lại"),
        Order(order_code="ORD027", customer_id=khanh.id, product_id=p["Deepcool AK400"],                      product_name="Deepcool AK400",                      quantity=1, total_amount=790_000,    status="cancelled",  note="đặt trùng đơn cũ"),
        Order(order_code="ORD037", customer_id=khanh.id, product_id=p["Razer Kraken X USB"],                  product_name="Razer Kraken X USB",                  quantity=1, total_amount=990_000,    status="delivered",  note="tai nghe gaming giá tốt"),

        # ORD013, ORD018, ORD028, ORD038: Nguyễn Thị Mai
        Order(order_code="ORD013", customer_id=mai.id,   product_id=p["Kingston NV2 500GB NVMe"],              product_name="Kingston NV2 500GB NVMe",             quantity=1, total_amount=990_000,    status="delivered",  note="nâng cấp laptop"),
        Order(order_code="ORD018", customer_id=mai.id,   product_id=p["Kingston Fury Beast 16GB DDR4 3200"],   product_name="Kingston Fury Beast 16GB DDR4 3200", quantity=1, total_amount=890_000,    status="pending",    note="chờ thanh toán"),
        Order(order_code="ORD028", customer_id=mai.id,   product_id=p["AMD Ryzen 5 5600"],                     product_name="AMD Ryzen 5 5600",                    quantity=1, total_amount=3_190_000,  status="pending",    note="sinh viên nâng cấp – test hủy đơn"),
        Order(order_code="ORD038", customer_id=mai.id,   product_id=p["Seagate Barracuda 1TB 7200RPM"],        product_name="Seagate Barracuda 1TB 7200RPM",       quantity=1, total_amount=1_050_000,  status="pending",    note="HDD lưu trữ dữ liệu"),

        # ORD014, ORD019, ORD029, ORD035: Lý Minh Khoa
        Order(order_code="ORD014", customer_id=khoa.id,  product_id=p["AMD Ryzen 7 5700X"],                    product_name="AMD Ryzen 7 5700X",                   quantity=1, total_amount=5_690_000,  status="processing", note="build streaming, cần tư vấn tản nhiệt"),
        Order(order_code="ORD019", customer_id=khoa.id,  product_id=p["Deepcool AK400"],                       product_name="Deepcool AK400",                      quantity=1, total_amount=790_000,    status="delivered",  note="tản nhiệt kèm build Ryzen 7"),
        Order(order_code="ORD029", customer_id=khoa.id,  product_id=p["Corsair CV650 650W 80 Plus Bronze"],    product_name="Corsair CV650 650W 80 Plus Bronze",   quantity=1, total_amount=1_490_000,  status="delivered",  note="nguồn cho build streaming"),
        Order(order_code="ORD035", customer_id=khoa.id,  product_id=p["Logitech C920 Full HD Webcam"],         product_name="Logitech C920 Full HD Webcam",        quantity=1, total_amount=1_590_000,  status="shipped",    note="webcam streaming"),

        # ORD015, ORD020, ORD030: Vũ Đức Anh
        Order(order_code="ORD015", customer_id=danh.id,  product_id=p["Corsair Vengeance 16GB DDR5 5600"],     product_name="Corsair Vengeance 16GB DDR5 5600",    quantity=1, total_amount=1_490_000,  status="shipped",    note="DDR5 mới, dự kiến 2 ngày"),
        Order(order_code="ORD020", customer_id=danh.id,  product_id=p["Intel Core i5 12400F"],                 product_name="Intel Core i5 12400F",                quantity=1, total_amount=3_590_000,  status="shipped",    note="đã thanh toán, đang vận chuyển"),
        Order(order_code="ORD030", customer_id=danh.id,  product_id=p["ASUS Dual RTX 3050 8GB"],               product_name="ASUS Dual RTX 3050 8GB",              quantity=1, total_amount=6_290_000,  status="shipped",    note="VGA mid-range"),
    ]

    db.add_all(orders)
    db.commit()
    db.close()

    print("seeding complete")
    print("created 15 customers, 51 products, 38 orders in ecommerce.db")


if __name__ == "__main__":
    import sys
    import io
    if sys.platform == "win32":
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    seed()
