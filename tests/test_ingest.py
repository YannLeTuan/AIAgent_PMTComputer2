"""Tests cho B-2: _get_chunk_config trả về (config, chunk_type) không cần loop lại."""


def test_get_chunk_config_returns_tuple_with_chunk_type():
    """_get_chunk_config phải trả về (dict, str) để tránh duplicate loop."""
    from app.rag.ingest import _get_chunk_config
    from pathlib import Path

    result = _get_chunk_config(Path("02_chinh_sach_doi_tra.txt"))
    assert isinstance(result, tuple), (
        "_get_chunk_config phải trả về tuple (config_dict, chunk_type_str)"
    )
    cfg, chunk_type = result
    assert isinstance(cfg, dict)
    assert "chunk_size" in cfg and "overlap" in cfg
    assert chunk_type == "compact"


def test_get_chunk_config_returns_standard_for_unknown_file():
    from app.rag.ingest import _get_chunk_config
    from pathlib import Path

    cfg, chunk_type = _get_chunk_config(Path("unknown_file.txt"))
    assert chunk_type == "standard"
    assert cfg["chunk_size"] == 900


def test_get_chunk_config_returns_large_for_faq_file():
    from app.rag.ingest import _get_chunk_config
    from pathlib import Path

    cfg, chunk_type = _get_chunk_config(Path("06_faq_linh_kien_may_tinh.txt"))
    assert chunk_type == "large"
    assert cfg["chunk_size"] == 1200
