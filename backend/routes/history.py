from fastapi import APIRouter, HTTPException
from services.history import load_all, get_audit_by_id, delete_audit, clear_all_history

router = APIRouter()


@router.get("/")
def list_history():
    return load_all()


@router.get("/{audit_id}")
def get_one(audit_id: str):
    item = get_audit_by_id(audit_id)
    if not item:
        raise HTTPException(404, f"Audit {audit_id} not found")
    return item


@router.delete("/{audit_id}")
def delete_one(audit_id: str):
    delete_audit(audit_id)
    return {"deleted": True, "audit_id": audit_id}


@router.delete("/")
def clear_all():
    clear_all_history()
    return {"cleared": True}
