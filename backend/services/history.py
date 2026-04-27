import json, os
from datetime import datetime

HISTORY_FILE = os.path.join(os.path.dirname(__file__), "../data/audit_history.json")


def _ensure_dir():
    os.makedirs(os.path.dirname(HISTORY_FILE), exist_ok=True)


def load_all():
    _ensure_dir()
    if not os.path.exists(HISTORY_FILE):
        return []
    try:
        with open(HISTORY_FILE, encoding="utf-8") as f:
            return json.load(f)
    except (json.JSONDecodeError, IOError):
        return []


def save_all(data: list):
    _ensure_dir()
    with open(HISTORY_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, default=str)


def save_audit_to_history(entry: dict):
    history = load_all()
    history.insert(0, {**entry, "timestamp": datetime.now().isoformat()})
    save_all(history[:100])


def get_all_history():
    return load_all()


def get_audit_by_id(audit_id: str):
    return next((h for h in load_all() if h.get("audit_id") == audit_id), None)


def delete_audit(audit_id: str):
    save_all([h for h in load_all() if h.get("audit_id") != audit_id])


def clear_all_history():
    save_all([])
