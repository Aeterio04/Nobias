from fastapi import APIRouter
from pydantic import BaseModel
import json, os

SETTINGS_FILE = os.path.join(os.path.dirname(__file__), "../data/settings.json")
router = APIRouter()

DEFAULT_SETTINGS = {
    "llm_provider": "openai",
    "llm_model": "gpt-4o",
    "api_key": "",
    "ollama_url": "http://localhost:11434",
    "default_audit_mode": "standard",
    "default_export_formats": ["pdf", "json"],
}

class SettingsUpdate(BaseModel):
    llm_provider: str = None
    llm_model: str = None
    api_key: str = None
    ollama_url: str = None
    default_audit_mode: str = None
    default_export_formats: list = None

def _load_settings():
    if not os.path.exists(SETTINGS_FILE):
        return DEFAULT_SETTINGS.copy()
    with open(SETTINGS_FILE, encoding='utf-8') as f:
        return {**DEFAULT_SETTINGS, **json.load(f)}

def _save_settings(data):
    os.makedirs(os.path.dirname(SETTINGS_FILE), exist_ok=True)
    with open(SETTINGS_FILE, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2)

@router.get("/")
def get_settings():
    s = _load_settings()
    s_safe = {**s, "api_key": "***" if s.get("api_key") else ""}
    return s_safe

@router.post("/")
def update_settings(update: SettingsUpdate):
    current = _load_settings()
    update_dict = {k: v for k, v in update.dict().items() if v is not None}
    current.update(update_dict)
    _save_settings(current)
    return {"saved": True}

@router.post("/test-connection")
async def test_connection():
    settings = _load_settings()
    try:
        if settings["llm_provider"] == "openai":
            import openai
            client = openai.OpenAI(api_key=settings["api_key"])
            models = client.models.list()
            return {"connected": True, "message": f"Connected — {settings['llm_model']} available"}
        elif settings["llm_provider"] == "anthropic":
            import anthropic
            client = anthropic.Anthropic(api_key=settings["api_key"])
            return {"connected": True, "message": "Connected — Claude available"}
        elif settings["llm_provider"] == "ollama":
            import httpx
            r = httpx.get(f"{settings['ollama_url']}/api/tags")
            models = [m['name'] for m in r.json().get('models', [])]
            return {"connected": True, "message": f"Connected — {len(models)} models available"}
        else:
            return {"connected": False, "message": "Unknown provider"}
    except Exception as e:
        return {"connected": False, "message": str(e)}
