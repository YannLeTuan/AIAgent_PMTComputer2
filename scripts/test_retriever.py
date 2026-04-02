from app.rag.retriever import retrieve_context


def main():
    questions = [
        "VGA bao hanh bao lau?",
        "SSD loi trong 7 ngay co doi tra duoc khong?",
        "don hang shipped co huy duoc khong?",
        "PMT Computer hoan tien trong bao lau?",
        "chuot gaming bi double click co duoc bao hanh khong?"
    ]

    for q in questions:
        print("\n======================")
        print("cau hoi:", q)
        results = retrieve_context(q, top_k=3)

        for i, item in enumerate(results, 1):
            print(f"\nchunk {i}:")
            print(item)


if __name__ == "__main__":
    main()