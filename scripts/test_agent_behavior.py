from app.agent.orchestrator import chat_with_agent


def main():
    questions = [
        "PMT Computer là cửa hàng gì?",
        "Phạm Minh Tuấn là ai?",
        "SSD và HDD khác nhau thế nào?",
        "Mainboard có cần đúng socket với CPU không?",
        "Shop có hỗ trợ tư vấn build máy không?",
        "Chủ cửa hàng PMT là ai?",
        "Danh sách sản phẩm",
        "Tôi muốn tìm SSD Samsung",
        "Khách phamminhtuan.pmt@gmail.com đã đặt gì?",
        "Đơn ORD003 có hủy được không?"
    ]

    for q in questions:
        print("\n" + "=" * 70)
        print("user:", q)
        print("bot :", chat_with_agent(q))


if __name__ == "__main__":
    main()