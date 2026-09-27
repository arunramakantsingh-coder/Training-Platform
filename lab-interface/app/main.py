from fastapi import FastAPI

from app.api import router


app = FastAPI(title="Training Platform Lab Interface", version="0.1.0")


@app.get("/health")
def health():
    return {"status": "ok", "service": "lab-interface"}


app.include_router(router)
