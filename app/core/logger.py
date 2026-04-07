import json
import re
import time
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parent.parent.parent
LOG_DIR = BASE_DIR / "logs"
LOG_DIR.mkdir(parents=True, exist_ok=True)

LOG_FILE = LOG_DIR / "app.log"
MAX_LOG_SIZE = 10 * 1024 * 1024  # 10 MB
MAX_LOG_FILES = 5                 # max backups

_EMAIL_RE = re.compile(r"([\w\.-]{2})([\w\.-]*)([\w\.-]{1})(@[\w\.-]+\.\w+)")
_PHONE_RE = re.compile(r"(0\d{2})(\d{4,5})(\d{3})")


def _mask_email(match: re.Match) -> str:
    return f"{match.group(1)}***{match.group(3)}{match.group(4)}"


def _mask_phone(match: re.Match) -> str:
    return f"{match.group(1)}****{match.group(3)}"


def mask_sensitive(text: str) -> str:
    if not text:
        return text
    text = _EMAIL_RE.sub(_mask_email, text)
    text = _PHONE_RE.sub(_mask_phone, text)
    return text


def _sanitize_payload(obj):
    if isinstance(obj, str):
        return mask_sensitive(obj)
    if isinstance(obj, dict):
        return {k: _sanitize_payload(v) for k, v in obj.items()}
    if isinstance(obj, list):
        return [_sanitize_payload(item) for item in obj]
    return obj


def _rotate_if_needed():
    if not LOG_FILE.exists():
        return
    if LOG_FILE.stat().st_size < MAX_LOG_SIZE:
        return
    for i in range(MAX_LOG_FILES - 1, 0, -1):
        old = LOG_DIR / f"app.log.{i}"
        new = LOG_DIR / f"app.log.{i + 1}"
        if old.exists():
            old.rename(new)
    LOG_FILE.rename(LOG_DIR / "app.log.1")


def write_log(event_type: str, payload: dict):
    _rotate_if_needed()

    sanitized = _sanitize_payload(payload)
    record = {
        "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
        "event_type": event_type,
        "payload": sanitized
    }

    with LOG_FILE.open("a", encoding="utf-8") as f:
        f.write(json.dumps(record, ensure_ascii=False) + "\n")
