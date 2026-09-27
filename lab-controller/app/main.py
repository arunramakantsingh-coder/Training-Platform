from fastapi import FastAPI
from app.api import router

app = FastAPI(title="Training Platform Lab Controller", version="0.1.0")
app.include_router(router)

@app.get("/health")
def health():
    return {"status": "ok", "service": "lab-controller"}
