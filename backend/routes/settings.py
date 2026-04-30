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
    provider = settings.get("llm_provider", "openai")
    api_key  = settings.get("api_key", "")
    model    = settings.get("llm_model", "")

    try:
        if provider == "openai":
            import openai
            client = openai.OpenAI(api_key=api_key)
            client.models.list()
            return {"connected": True, "message": f"Connected — {model} available"}

        elif provider == "anthropic":
            import anthropic
            client = anthropic.Anthropic(api_key=api_key)
            client.messages.create(
                model=model or "claude-3-5-sonnet-20241022",
                max_tokens=1,
                messages=[{"role": "user", "content": "hi"}],
            )
            return {"connected": True, "message": f"Connected — {model} available"}

        elif provider == "groq":
            import httpx
            r = httpx.get(
                "https://api.groq.com/openai/v1/models",
                headers={"Authorization": f"Bearer {api_key}"},
                timeout=10,
            )
            if r.status_code == 200:
                return {"connected": True, "message": "Connected — Groq API reachable"}
            else:
                return {"connected": False, "message": f"Groq returned HTTP {r.status_code}"}

        elif provider == "gemini":
            import google.generativeai as genai
            genai.configure(api_key=api_key)
            models_list = list(genai.list_models())
            gemini_models = [m.name for m in models_list if "generateContent" in (m.supported_generation_methods or [])]
            return {"connected": True, "message": f"Connected — {len(gemini_models)} Gemini model(s) available"}

        elif provider == "ollama":
            import httpx
            ollama_url = settings.get("ollama_url", "http://localhost:11434")
            r = httpx.get(f"{ollama_url}/api/tags", timeout=5)
            models_list = [m['name'] for m in r.json().get('models', [])]
            return {"connected": True, "message": f"Connected — {len(models_list)} models available"}

        else:
            return {"connected": False, "message": f"Unknown provider: {provider}"}

    except Exception as e:
        return {"connected": False, "message": str(e)}
