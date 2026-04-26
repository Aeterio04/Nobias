from fastapi import APIRouter, HTTPException
from services.history import get_all_history, delete_audit, clear_all_history

router = APIRouter()

@router.get("/")
def list_history():
    return get_all_history()

@router.delete("/{audit_id}")
def delete_history_item(audit_id: str):
    delete_audit(audit_id)
    return {"deleted": True}

@router.delete("/")
def clear_history():
    clear_all_history()
    return {"cleared": True}
