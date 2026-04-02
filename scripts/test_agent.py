from app.agent.orchestrator import chat_with_agent


def main():
    questions = [
        "CPU bao hanh bao lau?",
        "SSD loi trong 7 ngay co doi tra duoc khong?",
        "kiem tra don hang ORD003",
        "don ORD003 co huy duoc khong?",
        "tim VGA MSI",
        "khach phamminhtuan.pmt@gmail.com da dat nhung don nao?",
        "chuot gaming bi double click co duoc bao hanh khong?"
    ]

    for q in questions:
        print("\n" + "=" * 60)
        print("user:", q)
        print("bot:", chat_with_agent(q))


if __name__ == "__main__":
    main()