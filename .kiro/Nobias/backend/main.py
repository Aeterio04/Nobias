from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

app = FastAPI(title="Nobias API", version="1.0.0")

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
    uvicorn.run(app, host="127.0.0.1", port=8000, reload=True)
