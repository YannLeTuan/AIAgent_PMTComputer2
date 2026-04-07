from pathlib import Path

from app.core.config import settings
from app.rag.retriever import embed_texts, store as retriever_store
from app.rag.vector_store import LocalFaissStore

_CHUNK_CONFIG = {
    "compact": {"chunk_size": 600, "overlap": 120},
    "standard": {"chunk_size": 900, "overlap": 180},
    "large":    {"chunk_size": 1200, "overlap": 220},
}

_FILENAME_CHUNK_TYPE: dict[str, str] = {
    "02_chinh_sach_doi_tra":              "compact",
    "03_chinh_sach_bao_hanh":             "compact",
    "08_ghi_chu_noi_bo_va_khach_hang":    "compact",
    "10_tuong_thich_linh_kien":           "compact",
    "06_faq_linh_kien_may_tinh":          "large",
    "07_tu_van_mua_hang_co_ban":          "large",
    "11_faq_bao_gia_ton_kho_khuyen_mai":  "large",
    "12_kich_ban_hoi_dap_thuc_te":        "large",
}


def _get_chunk_config(file_path: Path) -> dict:
    stem = file_path.stem
    for key, chunk_type in _FILENAME_CHUNK_TYPE.items():
        if key in stem:
            return _CHUNK_CONFIG[chunk_type]
    return _CHUNK_CONFIG["standard"]


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
        cfg = _get_chunk_config(file_path)
        chunks = split_text(raw_text, chunk_size=cfg["chunk_size"], overlap=cfg["overlap"])

        chunk_type = next(
            (v for k, v in _FILENAME_CHUNK_TYPE.items() if k in file_path.stem),
            "standard"
        )
        print(f"  {file_path.name}: {len(chunks)} chunks [{chunk_type}, size={cfg['chunk_size']}, overlap={cfg['overlap']}]")

        for chunk in chunks:
            all_chunks.append(f"[FILE: {file_path.name}]\n{chunk}")

    if not all_chunks:
        raise ValueError("Không tạo được chunk nào từ dữ liệu đầu vào.")

    embeddings = embed_texts(all_chunks)

    store = LocalFaissStore(settings.VECTOR_INDEX_PATH)
    store.build(embeddings, all_chunks)
    store.save()

    retriever_store.reload()

    print("ingest xong")
    print("so file:", len(txt_files))
    print("so chunks:", len(all_chunks))


if __name__ == "__main__":
    ingest_folder("data/raw")