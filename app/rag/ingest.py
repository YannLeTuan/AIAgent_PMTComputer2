from pathlib import Path

from app.core.config import settings
from app.rag.retriever import embed_texts
from app.rag.vector_store import LocalFaissStore


def read_text_file(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def find_split_point(text: str, start: int, max_end: int) -> int:
    window = text[start:max_end]

    for sep in ["\n\n", "\n", ". ", "! ", "? ", "; ", ", ", " "]:
        idx = window.rfind(sep)
        if idx > int(len(window) * 0.6):
            return start + idx + len(sep)

    return max_end


def split_text(text: str, chunk_size: int = 900, overlap: int = 180):
    chunks = []
    text = text.strip()

    if not text:
        return chunks

    start = 0
    text_len = len(text)

    while start < text_len:
        max_end = min(start + chunk_size, text_len)
        end = find_split_point(text, start, max_end)

        if end <= start:
            end = max_end

        chunk = text[start:end].strip()
        if chunk:
            chunks.append(chunk)

        if end >= text_len:
            break

        next_start = end - overlap

        # đảm bảo start luôn tiến lên, không bị kẹt
        if next_start <= start:
            next_start = end

        start = next_start

    return chunks


def ingest_folder(folder_path: str):
    folder = Path(folder_path)

    if not folder.exists():
        raise FileNotFoundError(f"Không tìm thấy thư mục dữ liệu: {folder.resolve()}")

    txt_files = sorted(folder.glob("*.txt"))
    if not txt_files:
        raise FileNotFoundError(f"Không tìm thấy file .txt nào trong: {folder.resolve()}")

    all_chunks = []

    for file_path in txt_files:
        raw_text = read_text_file(file_path)
        chunks = split_text(raw_text)

        for chunk in chunks:
            all_chunks.append(f"[FILE: {file_path.name}]\n{chunk}")

    if not all_chunks:
        raise ValueError("Không tạo được chunk nào từ dữ liệu đầu vào.")

    embeddings = embed_texts(all_chunks)

    store = LocalFaissStore(settings.VECTOR_INDEX_PATH)
    store.build(embeddings, all_chunks)
    store.save()

    print("ingest xong")
    print("so file:", len(txt_files))
    print("so chunks:", len(all_chunks))


if __name__ == "__main__":
    ingest_folder("data/raw")