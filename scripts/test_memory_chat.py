from app.agent.orchestrator import chat_with_agent


def main():
    history = []
    context_state = {}

    questions = [
        "Kiểm tra đơn hàng ORD003",
        "Đơn này có hủy được không?",
        "Vậy nếu đã thanh toán rồi thì hoàn tiền mất bao lâu?",
        "Khách phamminhtuan.pmt@gmail.com đã đặt gì?",
        "Trong các đơn đó, đơn nào đang xử lý?"
    ]

    for q in questions:
        result = chat_with_agent(q, history, context_state)
        history = result["history"]
        context_state = result["context_state"]

        print("\n" + "=" * 70)
        print("user:", q)
        print("bot :", result["answer"])


if __name__ == "__main__":
    main()