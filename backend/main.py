from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import uvicorn, math, json

class SafeJSONResponse(JSONResponse):
    """JSONResponse that replaces inf/nan floats with null."""
    def render(self, content) -> bytes:
        def sanitize(obj):
            if isinstance(obj, float):
                if math.isnan(obj) or math.isinf(obj):
                    return None
                return obj
            if isinstance(obj, dict):
                return {k: sanitize(v) for k, v in obj.items()}
            if isinstance(obj, list):
                return [sanitize(i) for i in obj]
            return obj
        return json.dumps(sanitize(content), ensure_ascii=False, separators=(",", ":")).encode("utf-8")

app = FastAPI(title="Nobias API", version="1.0.0", default_response_class=SafeJSONResponse)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

from routes.dataset import router as dataset_router
from routes.model import router as model_router
from routes.agent import router as agent_router
from routes.history import router as history_router
from routes.settings import router as settings_router

app.include_router(dataset_router, prefix="/api/dataset")
app.include_router(model_router, prefix="/api/model")
app.include_router(agent_router, prefix="/api/agent")
app.include_router(history_router, prefix="/api/history")
app.include_router(settings_router, prefix="/api/settings")

@app.get("/api/health")
def health():
    return {"status": "ok", "version": "1.0.0"}

if __name__ == "__main__":
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)
