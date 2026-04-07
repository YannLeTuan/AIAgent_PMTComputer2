from app.db.models import Base, Customer, Order, Product
from app.db.session import SessionLocal, engine


def seed():
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)

    db = SessionLocal()

    customers = [
        Customer(name="Phạm Minh Tuấn",   email="phamminhtuan.pmt@gmail.com", phone="0903123456", city="Quảng Ninh",  note="khách quen, hồ sơ kiểm thử nội bộ"),
        Customer(name="Nguyễn Mạnh Hưng",  email="manhhung.nguyen@gmail.com",  phone="0915666777", city="Bắc Ninh",    note="khách nâng cấp máy cũ"),
        Customer(name="Nguyễn Hoàng Long", email="long.nguyen@gmail.com",      phone="0904111222", city="Hải Phòng",   note="khách thiên về gaming"),
        Customer(name="Trần Quốc Bảo",    email="bao.tran@gmail.com",         phone="0905333444", city="Đà Nẵng",     note="hay mua SSD và RAM"),
        Customer(name="Lê Minh Đức",      email="duc.le@gmail.com",           phone="0906777888", city="Hồ Chí Minh", note="khách mới"),
        Customer(name="Phạm Gia Huy",     email="huy.pham@gmail.com",         phone="0908999000", city="Cần Thơ",     note="ưu tiên giao nhanh"),
        Customer(name="Ngô Anh Tuấn",     email="anhtuan.ngo@gmail.com",      phone="0911222333", city="Hà Nội",      note="hay hỏi build PC"),
        Customer(name="Vũ Thu Hà",        email="thuha.vu@gmail.com",         phone="0913444555", city="Nam Định",    note="khách văn phòng"),
        Customer(name="Trịnh Hải Nam",    email="hainam.t@gmail.com",         phone="0917888999", city="Hà Nội",      note="quan tâm màn hình gaming"),
        Customer(name="Đỗ Minh Quân",     email="minhquan.do@gmail.com",      phone="0920000111", city="Hưng Yên",    note="thường hỏi VGA và nguồn"),
        Customer(name="Bùi Thị Lan",      email="buithilan@gmail.com",        phone="0922111333", city="Hà Nội",      note="hay mua bàn phím cơ và phụ kiện"),
        Customer(name="Hoàng Văn Khánh",  email="khanhvh@gmail.com",          phone="0933222444", city="Hải Dương",   note="quan tâm màn hình gaming"),
        Customer(name="Nguyễn Thị Mai",   email="mai.nguyen@yahoo.com",       phone="0944333555", city="Thái Nguyên", note="khách sinh viên, ngân sách thấp"),
        Customer(name="Lý Minh Khoa",     email="minhkhoa.ly@gmail.com",      phone="0955444666", city="Đà Lạt",      note="build máy streaming"),
        Customer(name="Vũ Đức Anh",       email="ducanh.vu@gmail.com",        phone="0966555777", city="Hà Nội",      note="quan tâm RAM DDR5 và CPU mới"),
    ]

    # 12 categories x 5 products = 60, sorted by price asc per category
    products = [

        # --- CPU ---
        Product(sku="CPU-AMD-R7-5700X",    name="AMD Ryzen 7 5700X",            category="CPU", brand="AMD",   price=5_690_000,  stock=7,  warranty_months=36),
        Product(sku="CPU-INTEL-I7-12700K", name="Intel Core i7 12700K",          category="CPU", brand="Intel", price=7_890_000,  stock=6,  warranty_months=36),
        Product(sku="CPU-INTEL-I9-13900K", name="Intel Core i9 13900K",          category="CPU", brand="Intel", price=13_990_000, stock=3,  warranty_months=36),
        Product(sku="CPU-INTEL-U9-285K",   name="Intel Core Ultra 9 285K",       category="CPU", brand="Intel", price=18_990_000, stock=4,  warranty_months=36),
        Product(sku="CPU-AMD-R9-9950X",    name="AMD Ryzen 9 9950X",             category="CPU", brand="AMD",   price=25_990_000, stock=2,  warranty_months=36),

        # --- RAM ---
        Product(sku="RAM-CORSAIR-16GB-DDR5",      name="Corsair Vengeance 16GB DDR5 5600",          category="RAM", brand="Corsair",  price=1_490_000, stock=15, warranty_months=36),
        Product(sku="RAM-KINGSTON-32GB-DDR4",      name="Kingston Fury Beast 32GB DDR4 3200",        category="RAM", brand="Kingston", price=1_790_000, stock=12, warranty_months=36),
        Product(sku="RAM-GSKILL-32GB-DDR5",        name="G.Skill Trident Z5 32GB DDR5 6000",         category="RAM", brand="G.Skill",  price=2_890_000, stock=6,  warranty_months=36),
        Product(sku="RAM-CORSAIR-32GB-DDR5-7200",  name="Corsair Dominator Titanium 32GB DDR5 7200", category="RAM", brand="Corsair",  price=4_990_000, stock=4,  warranty_months=36),
        Product(sku="RAM-GSKILL-64GB-DDR5",        name="G.Skill Trident Z5 RGB 64GB DDR5 7200",     category="RAM", brand="G.Skill",  price=8_990_000, stock=2,  warranty_months=36),

        # --- SSD ---
        Product(sku="SSD-CRUCIAL-MX500-1TB",  name="Crucial MX500 1TB SATA SSD",          category="SSD", brand="Crucial",         price=1_790_000, stock=9,  warranty_months=36),
        Product(sku="SSD-SAMSUNG-970EVO-1TB", name="Samsung 970 EVO Plus 1TB NVMe",        category="SSD", brand="Samsung",         price=1_890_000, stock=18, warranty_months=60),
        Product(sku="SSD-WD-SN770-1TB",       name="WD Black SN770 1TB NVMe",              category="SSD", brand="Western Digital", price=2_050_000, stock=11, warranty_months=60),
        Product(sku="SSD-SAMSUNG-990PRO-2TB", name="Samsung 990 Pro 2TB NVMe PCIe 4.0",   category="SSD", brand="Samsung",         price=4_990_000, stock=7,  warranty_months=60),
        Product(sku="SSD-WD-SN850X-4TB",      name="WD Black SN850X 4TB NVMe PCIe 4.0",  category="SSD", brand="Western Digital", price=9_990_000, stock=3,  warranty_months=60),

        # --- HDD ---
        Product(sku="HDD-WD-BLUE-1TB",    name="WD Blue 1TB 7200RPM",              category="HDD", brand="Western Digital", price=1_090_000,  stock=14, warranty_months=24),
        Product(sku="HDD-WD-BLUE-2TB",    name="WD Blue 2TB 5400RPM",              category="HDD", brand="Western Digital", price=1_390_000,  stock=9,  warranty_months=24),
        Product(sku="HDD-SEAGATE-2TB",    name="Seagate Barracuda 2TB 7200RPM",    category="HDD", brand="Seagate",         price=1_490_000,  stock=10, warranty_months=24),
        Product(sku="HDD-SEAGATE-4TB",    name="Seagate Barracuda 4TB 5400RPM",    category="HDD", brand="Seagate",         price=2_290_000,  stock=5,  warranty_months=24),
        Product(sku="HDD-SEAGATE-IW-20TB", name="Seagate IronWolf Pro 20TB NAS",  category="HDD", brand="Seagate",         price=12_990_000, stock=3,  warranty_months=60),

        # --- VGA ---
        Product(sku="VGA-MSI-RTX4060-8G",    name="MSI GeForce RTX 4060 Ventus 8G",            category="VGA", brand="MSI",      price=8_990_000,  stock=6, warranty_months=36),
        Product(sku="VGA-MSI-RTX4060TI",     name="MSI GeForce RTX 4060 Ti Gaming X 16G",      category="VGA", brand="MSI",      price=12_490_000, stock=4, warranty_months=36),
        Product(sku="VGA-GIGABYTE-RTX4070",  name="Gigabyte GeForce RTX 4070 Windforce 12G",   category="VGA", brand="Gigabyte", price=16_990_000, stock=3, warranty_months=36),
        Product(sku="VGA-MSI-RTX4080S-16G",  name="MSI GeForce RTX 4080 Super Gaming X Slim 16G", category="VGA", brand="MSI",  price=24_990_000, stock=2, warranty_months=36),
        Product(sku="VGA-ASUS-RTX4090-24G",  name="ASUS ROG Strix RTX 4090 OC 24GB",           category="VGA", brand="ASUS",    price=49_990_000, stock=1, warranty_months=36),

        # --- PSU ---
        Product(sku="PSU-CORSAIR-CV650",      name="Corsair CV650 650W 80 Plus Bronze",   category="PSU", brand="Corsair",      price=1_490_000, stock=16, warranty_months=36),
        Product(sku="PSU-COOLERMASTER-MWE750", name="Cooler Master MWE 750W Bronze V2",   category="PSU", brand="Cooler Master", price=1_890_000, stock=9,  warranty_months=36),
        Product(sku="PSU-SEASONIC-FOCUS650",  name="Seasonic Focus GX 650W Gold",         category="PSU", brand="Seasonic",     price=2_590_000, stock=7,  warranty_months=36),
        Product(sku="PSU-CORSAIR-RM750X",     name="Corsair RM750x 750W 80 Plus Gold",    category="PSU", brand="Corsair",      price=3_290_000, stock=5,  warranty_months=36),
        Product(sku="PSU-CORSAIR-HX1500I",    name="Corsair HX1500i 1500W 80 Plus Platinum", category="PSU", brand="Corsair",   price=8_990_000, stock=2,  warranty_months=84),

        # --- Mainboard ---
        Product(sku="MAIN-MSI-B550M",        name="MSI B550M PRO-VDH WiFi",                  category="Mainboard", brand="MSI",      price=2_790_000,  stock=10, warranty_months=36),
        Product(sku="MAIN-ASUS-B760M",       name="ASUS Prime B760M-A WiFi DDR4",             category="Mainboard", brand="ASUS",     price=3_290_000,  stock=9,  warranty_months=36),
        Product(sku="MAIN-ASUS-B550F",       name="ASUS ROG Strix B550-F Gaming WiFi",        category="Mainboard", brand="ASUS",     price=4_290_000,  stock=5,  warranty_months=36),
        Product(sku="MAIN-MSI-Z790-GODLIKE", name="MSI MEG Z790 Godlike DDR5",               category="Mainboard", brand="MSI",      price=16_990_000, stock=2,  warranty_months=36),
        Product(sku="MAIN-ASUS-Z790-APEX",   name="ASUS ROG Maximus Z790 Apex Encore DDR5",  category="Mainboard", brand="ASUS",     price=18_990_000, stock=2,  warranty_months=36),

        # --- Case ---
        Product(sku="CASE-MONTECH-AIR100", name="Montech Air 100 ARGB",         category="Case", brand="Montech",  price=1_290_000, stock=10, warranty_months=12),
        Product(sku="CASE-NZXT-H510",      name="NZXT H510",                    category="Case", brand="NZXT",     price=1_890_000, stock=5,  warranty_months=12),
        Product(sku="CASE-CORSAIR-4000D",  name="Corsair 4000D Airflow",        category="Case", brand="Corsair",  price=2_390_000, stock=7,  warranty_months=12),
        Product(sku="CASE-FRACTAL-TC",     name="Fractal Design Torrent Compact RGB", category="Case", brand="Fractal Design", price=3_490_000, stock=4, warranty_months=12),
        Product(sku="CASE-LIANLI-O11-XL",  name="Lian Li PC-O11 Dynamic EVO XL", category="Case", brand="Lian Li", price=4_990_000, stock=3, warranty_months=12),

        # --- Cooler ---
        Product(sku="COOLER-IDCOOLING-SE224", name="ID-Cooling SE-224-XTS",             category="Cooler", brand="ID-Cooling", price=690_000,   stock=12, warranty_months=12),
        Product(sku="COOLER-DEEPCOOL-AK400",  name="Deepcool AK400",                   category="Cooler", brand="Deepcool",   price=790_000,   stock=14, warranty_months=12),
        Product(sku="COOLER-NOCTUA-U12S",     name="Noctua NH-U12S Redux",              category="Cooler", brand="Noctua",     price=1_290_000, stock=6,  warranty_months=12),
        Product(sku="COOLER-CORSAIR-H150I",   name="Corsair iCUE H150i Elite LCD XT 360mm", category="Cooler", brand="Corsair", price=3_990_000, stock=3, warranty_months=24),
        Product(sku="COOLER-NZXT-KRAKEN360",  name="NZXT Kraken Elite 360 RGB AIO",    category="Cooler", brand="NZXT",       price=4_490_000, stock=2,  warranty_months=36),

        # --- Monitor ---
        Product(sku="MON-DELL-P2422H",  name="Dell P2422H 24 inch IPS",              category="Monitor", brand="Dell",    price=4_290_000,  stock=7, warranty_months=36),
        Product(sku="MON-AOC-27G2",     name="AOC 27G2 27 inch 144Hz",               category="Monitor", brand="AOC",     price=5_390_000,  stock=6, warranty_months=24),
        Product(sku="MON-SAMSUNG-27",   name="Samsung Odyssey G5 27 inch 144Hz",     category="Monitor", brand="Samsung", price=5_990_000,  stock=5, warranty_months=24),
        Product(sku="MON-ASUS-VG27AQ",  name="ASUS TUF Gaming VG27AQ 27 inch 165Hz", category="Monitor", brand="ASUS",   price=7_990_000,  stock=4, warranty_months=36),
        Product(sku="MON-ASUS-PG32UQX", name="ASUS ROG Swift PG32UQX 32 inch 4K 144Hz", category="Monitor", brand="ASUS", price=28_990_000, stock=2, warranty_months=36),

        # --- Mouse ---
        Product(sku="MOUSE-SS-RIVAL3",        name="SteelSeries Rival 3",              category="Mouse", brand="SteelSeries", price=490_000,   stock=20, warranty_months=24),
        Product(sku="MOUSE-RAZER-VIPERMINI",  name="Razer Viper Mini",                 category="Mouse", brand="Razer",       price=590_000,   stock=15, warranty_months=24),
        Product(sku="MOUSE-RAZER-DEATHADDER", name="Razer DeathAdder Essential",       category="Mouse", brand="Razer",       price=690_000,   stock=14, warranty_months=24),
        Product(sku="MOUSE-LOGI-G304",        name="Logitech G304 Wireless",           category="Mouse", brand="Logitech",    price=790_000,   stock=18, warranty_months=24),
        Product(sku="MOUSE-LOGI-GPX2",        name="Logitech G Pro X 2 Superlight Wireless", category="Mouse", brand="Logitech", price=2_990_000, stock=5, warranty_months=24),

        # --- Keyboard ---
        Product(sku="KB-LOGI-G413",      name="Logitech G413 Mechanical Keyboard",    category="Keyboard", brand="Logitech", price=1_790_000, stock=8,  warranty_months=24),
        Product(sku="KB-RAZER-BWIDOW",   name="Razer BlackWidow V3 TKL",              category="Keyboard", brand="Razer",    price=2_190_000, stock=6,  warranty_months=24),
        Product(sku="KB-CORSAIR-K70",    name="Corsair K70 RGB Pro Mechanical",       category="Keyboard", brand="Corsair",  price=3_290_000, stock=4,  warranty_months=24),
        Product(sku="KB-KEYCHRON-Q6MAX", name="Keychron Q6 Max QMK Wireless",         category="Keyboard", brand="Keychron", price=3_990_000, stock=5,  warranty_months=12),
        Product(sku="KB-ASUS-CLAYMORE2", name="ASUS ROG Claymore II Modular Wireless", category="Keyboard", brand="ASUS",   price=4_990_000, stock=3,  warranty_months=24),
    ]

    db.add_all(customers)
    db.add_all(products)
    db.commit()

    tuan  = db.query(Customer).filter_by(email="phamminhtuan.pmt@gmail.com").first()
    hung  = db.query(Customer).filter_by(email="manhhung.nguyen@gmail.com").first()
    long  = db.query(Customer).filter_by(email="long.nguyen@gmail.com").first()
    bao   = db.query(Customer).filter_by(email="bao.tran@gmail.com").first()
    duc   = db.query(Customer).filter_by(email="duc.le@gmail.com").first()
    huy   = db.query(Customer).filter_by(email="huy.pham@gmail.com").first()
    ngo   = db.query(Customer).filter_by(email="anhtuan.ngo@gmail.com").first()
    ha    = db.query(Customer).filter_by(email="thuha.vu@gmail.com").first()
    trinh = db.query(Customer).filter_by(email="hainam.t@gmail.com").first()
    mq    = db.query(Customer).filter_by(email="minhquan.do@gmail.com").first()
    lan   = db.query(Customer).filter_by(email="buithilan@gmail.com").first()
    khanh = db.query(Customer).filter_by(email="khanhvh@gmail.com").first()
    mai   = db.query(Customer).filter_by(email="mai.nguyen@yahoo.com").first()
    khoa  = db.query(Customer).filter_by(email="minhkhoa.ly@gmail.com").first()
    danh  = db.query(Customer).filter_by(email="ducanh.vu@gmail.com").first()

    p = {prod.name: prod.id for prod in db.query(Product).all()}

    orders = [
        # Phạm Minh Tuấn (5)
        Order(order_code="ORD001", customer_id=tuan.id, product_id=p["Intel Core Ultra 9 285K"],              product_name="Intel Core Ultra 9 285K",              quantity=1, total_amount=18_990_000, status="cancelled",  note="đổi ý sau khi đặt"),
        Order(order_code="ORD002", customer_id=tuan.id, product_id=p["G.Skill Trident Z5 RGB 64GB DDR5 7200"], product_name="G.Skill Trident Z5 RGB 64GB DDR5 7200", quantity=2, total_amount=17_980_000, status="processing", note="giao giờ hành chính"),
        Order(order_code="ORD009", customer_id=tuan.id, product_id=p["Samsung 970 EVO Plus 1TB NVMe"],         product_name="Samsung 970 EVO Plus 1TB NVMe",         quantity=1, total_amount=1_890_000,  status="delivered",  note="nâng cấp SSD"),
        Order(order_code="ORD010", customer_id=tuan.id, product_id=p["Logitech G Pro X 2 Superlight Wireless"], product_name="Logitech G Pro X 2 Superlight Wireless", quantity=1, total_amount=2_990_000, status="pending",   note="đơn thử chatbot"),
        Order(order_code="ORD023", customer_id=tuan.id, product_id=p["MSI B550M PRO-VDH WiFi"],               product_name="MSI B550M PRO-VDH WiFi",               quantity=1, total_amount=2_790_000,  status="pending",    note="chờ xác nhận – test hủy đơn"),

        # Nguyễn Mạnh Hưng (2)
        Order(order_code="ORD008", customer_id=hung.id, product_id=p["Cooler Master MWE 750W Bronze V2"],   product_name="Cooler Master MWE 750W Bronze V2",   quantity=1, total_amount=1_890_000, status="delivered",  note="nguồn cho build gaming"),
        Order(order_code="ORD036", customer_id=hung.id, product_id=p["Noctua NH-U12S Redux"],               product_name="Noctua NH-U12S Redux",               quantity=1, total_amount=1_290_000, status="processing", note="tản nhiệt cao cấp"),

        # Nguyễn Hoàng Long (2)
        Order(order_code="ORD003", customer_id=long.id, product_id=p["MSI GeForce RTX 4060 Ventus 8G"],     product_name="MSI GeForce RTX 4060 Ventus 8G",     quantity=1, total_amount=8_990_000, status="shipped",    note="đã thanh toán online"),
        Order(order_code="ORD021", customer_id=long.id, product_id=p["Samsung 970 EVO Plus 1TB NVMe"],      product_name="Samsung 970 EVO Plus 1TB NVMe",      quantity=1, total_amount=1_890_000, status="delivered",  note="nâng cấp storage lần 2"),

        # Trần Quốc Bảo (2)
        Order(order_code="ORD004", customer_id=bao.id,  product_id=p["Samsung 970 EVO Plus 1TB NVMe"],      product_name="Samsung 970 EVO Plus 1TB NVMe",      quantity=1, total_amount=1_890_000, status="delivered",  note="yêu cầu xuất hóa đơn"),
        Order(order_code="ORD022", customer_id=bao.id,  product_id=p["WD Black SN770 1TB NVMe"],            product_name="WD Black SN770 1TB NVMe",            quantity=1, total_amount=2_050_000, status="processing", note="SSD thứ 2"),

        # Lê Minh Đức (1)
        Order(order_code="ORD005", customer_id=duc.id,  product_id=p["Corsair CV650 650W 80 Plus Bronze"],  product_name="Corsair CV650 650W 80 Plus Bronze",  quantity=1, total_amount=1_490_000, status="cancelled",  note="đặt nhầm công suất nguồn"),

        # Phạm Gia Huy (1)
        Order(order_code="ORD006", customer_id=huy.id,  product_id=p["ASUS Prime B760M-A WiFi DDR4"],       product_name="ASUS Prime B760M-A WiFi DDR4",       quantity=1, total_amount=3_290_000, status="pending",    note="chờ xác nhận tồn kho"),

        # Ngô Anh Tuấn (1)
        Order(order_code="ORD031", customer_id=ngo.id,  product_id=p["Corsair 4000D Airflow"],              product_name="Corsair 4000D Airflow",              quantity=1, total_amount=2_390_000, status="delivered",  note="case cho build gaming mới"),

        # Vũ Thu Hà (1)
        Order(order_code="ORD007", customer_id=ha.id,   product_id=p["Dell P2422H 24 inch IPS"],            product_name="Dell P2422H 24 inch IPS",            quantity=2, total_amount=8_580_000, status="processing", note="màn hình văn phòng, giao buổi chiều"),

        # Trịnh Hải Nam (2)
        Order(order_code="ORD024", customer_id=trinh.id, product_id=p["AOC 27G2 27 inch 144Hz"],            product_name="AOC 27G2 27 inch 144Hz",             quantity=1, total_amount=5_390_000, status="shipped",    note="màn hình gaming"),
        Order(order_code="ORD032", customer_id=trinh.id, product_id=p["Samsung Odyssey G5 27 inch 144Hz"],  product_name="Samsung Odyssey G5 27 inch 144Hz",   quantity=1, total_amount=5_990_000, status="processing", note="màn hình gaming Samsung"),

        # Đỗ Minh Quân (2)
        Order(order_code="ORD025", customer_id=mq.id,   product_id=p["Gigabyte GeForce RTX 4070 Windforce 12G"], product_name="Gigabyte GeForce RTX 4070 Windforce 12G", quantity=1, total_amount=16_990_000, status="processing", note="VGA cao cấp, cần nguồn mạnh"),
        Order(order_code="ORD034", customer_id=mq.id,   product_id=p["Logitech G304 Wireless"],             product_name="Logitech G304 Wireless",             quantity=1, total_amount=790_000,    status="delivered",  note="chuột wireless làm việc"),

        # Bùi Thị Lan (4)
        Order(order_code="ORD011", customer_id=lan.id,  product_id=p["Keychron Q6 Max QMK Wireless"],       product_name="Keychron Q6 Max QMK Wireless",       quantity=1, total_amount=3_990_000,  status="pending",    note="switch blue"),
        Order(order_code="ORD016", customer_id=lan.id,  product_id=p["Logitech G Pro X 2 Superlight Wireless"], product_name="Logitech G Pro X 2 Superlight Wireless", quantity=1, total_amount=2_990_000, status="cancelled", note="đặt nhầm màu sắc"),
        Order(order_code="ORD026", customer_id=lan.id,  product_id=p["SteelSeries Rival 3"],                product_name="SteelSeries Rival 3",                quantity=1, total_amount=490_000,    status="delivered",  note="chuột gaming thêm cho bàn"),
        Order(order_code="ORD033", customer_id=lan.id,  product_id=p["Razer BlackWidow V3 TKL"],            product_name="Razer BlackWidow V3 TKL",            quantity=1, total_amount=2_190_000,  status="pending",    note="bàn phím cơ gaming"),

        # Hoàng Văn Khánh (4)
        Order(order_code="ORD012", customer_id=khanh.id, product_id=p["ASUS ROG Swift PG32UQX 32 inch 4K 144Hz"], product_name="ASUS ROG Swift PG32UQX 32 inch 4K 144Hz", quantity=1, total_amount=28_990_000, status="processing", note="giao trước cuối tuần"),
        Order(order_code="ORD017", customer_id=khanh.id, product_id=p["AOC 27G2 27 inch 144Hz"],            product_name="AOC 27G2 27 inch 144Hz",             quantity=1, total_amount=5_390_000,  status="delivered",  note="hài lòng, sẽ quay lại"),
        Order(order_code="ORD027", customer_id=khanh.id, product_id=p["Deepcool AK400"],                    product_name="Deepcool AK400",                     quantity=1, total_amount=790_000,    status="cancelled",  note="đặt trùng đơn cũ"),
        Order(order_code="ORD037", customer_id=khanh.id, product_id=p["Corsair K70 RGB Pro Mechanical"],    product_name="Corsair K70 RGB Pro Mechanical",     quantity=1, total_amount=3_290_000,  status="delivered",  note="bàn phím gaming cao cấp"),

        # Nguyễn Thị Mai (4)
        Order(order_code="ORD013", customer_id=mai.id,  product_id=p["WD Black SN850X 4TB NVMe PCIe 4.0"], product_name="WD Black SN850X 4TB NVMe PCIe 4.0",  quantity=1, total_amount=9_990_000,  status="delivered",  note="nâng cấp laptop"),
        Order(order_code="ORD018", customer_id=mai.id,  product_id=p["G.Skill Trident Z5 RGB 64GB DDR5 7200"], product_name="G.Skill Trident Z5 RGB 64GB DDR5 7200", quantity=1, total_amount=8_990_000, status="pending", note="chờ thanh toán"),
        Order(order_code="ORD028", customer_id=mai.id,  product_id=p["AMD Ryzen 9 9950X"],                  product_name="AMD Ryzen 9 9950X",                  quantity=1, total_amount=25_990_000, status="pending",    note="nâng cấp – test hủy đơn"),
        Order(order_code="ORD038", customer_id=mai.id,  product_id=p["Seagate IronWolf Pro 20TB NAS"],      product_name="Seagate IronWolf Pro 20TB NAS",      quantity=1, total_amount=12_990_000, status="pending",    note="HDD lưu trữ"),

        # Lý Minh Khoa (4)
        Order(order_code="ORD014", customer_id=khoa.id, product_id=p["AMD Ryzen 7 5700X"],                  product_name="AMD Ryzen 7 5700X",                  quantity=1, total_amount=5_690_000,  status="processing", note="build streaming, cần tư vấn tản nhiệt"),
        Order(order_code="ORD019", customer_id=khoa.id, product_id=p["Deepcool AK400"],                     product_name="Deepcool AK400",                     quantity=1, total_amount=790_000,    status="delivered",  note="tản nhiệt kèm build Ryzen 7"),
        Order(order_code="ORD029", customer_id=khoa.id, product_id=p["Corsair CV650 650W 80 Plus Bronze"],  product_name="Corsair CV650 650W 80 Plus Bronze",  quantity=1, total_amount=1_490_000,  status="delivered",  note="nguồn cho build streaming"),
        Order(order_code="ORD035", customer_id=khoa.id, product_id=p["ASUS TUF Gaming VG27AQ 27 inch 165Hz"], product_name="ASUS TUF Gaming VG27AQ 27 inch 165Hz", quantity=1, total_amount=7_990_000, status="shipped", note="màn hình cho bàn streaming"),

        # Vũ Đức Anh (3)
        Order(order_code="ORD015", customer_id=danh.id, product_id=p["Corsair Vengeance 16GB DDR5 5600"],   product_name="Corsair Vengeance 16GB DDR5 5600",   quantity=1, total_amount=1_490_000,  status="shipped",    note="DDR5 mới, dự kiến 2 ngày"),
        Order(order_code="ORD020", customer_id=danh.id, product_id=p["Intel Core Ultra 9 285K"],            product_name="Intel Core Ultra 9 285K",            quantity=1, total_amount=18_990_000, status="shipped",    note="đã thanh toán, đang vận chuyển"),
        Order(order_code="ORD030", customer_id=danh.id, product_id=p["ASUS ROG Strix RTX 4090 OC 24GB"],   product_name="ASUS ROG Strix RTX 4090 OC 24GB",   quantity=1, total_amount=49_990_000, status="shipped",    note="VGA flagship"),
    ]

    db.add_all(orders)
    db.commit()
    db.close()

    print("seeding complete")
    print("created 15 customers, 60 products (12 categories x 5), 38 orders in ecommerce.db")


if __name__ == "__main__":
    import sys
    import io
    if sys.platform == "win32":
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    seed()
