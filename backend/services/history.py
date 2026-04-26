import json, os
from datetime import datetime

HISTORY_FILE = os.path.join(os.path.dirname(__file__), "../data/audit_history.json")

def _load():
    if not os.path.exists(HISTORY_FILE):
        os.makedirs(os.path.dirname(HISTORY_FILE), exist_ok=True)
        return []
    try:
        with open(HISTORY_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    except:
        return []

def _save(data):
    os.makedirs(os.path.dirname(HISTORY_FILE), exist_ok=True)
    with open(HISTORY_FILE, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2)

def save_audit_to_history(entry: dict):
    history = _load()
    history.insert(0, {**entry, "timestamp": datetime.now().isoformat()})
    _save(history)

def get_all_history():
    return _load()

def get_audit_by_id(audit_id: str):
    return next((h for h in _load() if h.get("audit_id") == audit_id), None)

def delete_audit(audit_id: str):
    history = [h for h in _load() if h.get("audit_id") != audit_id]
    _save(history)

def clear_all_history():
    _save([])
