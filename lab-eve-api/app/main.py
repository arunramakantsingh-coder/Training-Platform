from fastapi import FastAPI, HTTPException
from app.native import NativeEveBackend, NativeEveError
from app.schemas import LabPathRequest, ProvisionRequest

app = FastAPI(title="Lab EVE API", version="0.1.0")
backend = NativeEveBackend()

@app.get("/health")
def health():
    return {"status": "ok", "service": "lab-eve-api"}

@app.get("/v1/capabilities")
def capabilities():
    return {"service": "lab-eve-api", "platform": "eve-ng", "native": {"filesystem_clone": True, "start": False, "stop": False, "reset": False, "delete": True}}

def fail(exc: NativeEveError) -> HTTPException:
    return HTTPException(status_code=502, detail=str(exc))

@app.post("/v1/labs/provision")
def provision(payload: ProvisionRequest):
    try: return {"lab_path": backend.provision(payload.template_path, payload.lab_path), "state": "provisioned"}
    except NativeEveError as exc: raise fail(exc) from exc

@app.post("/v1/labs/start")
def start(payload: LabPathRequest):
    try:
        backend.start(payload.lab_path)
        return {"lab_path": payload.lab_path, "state": "running"}
    except NativeEveError as exc: raise fail(exc) from exc

@app.post("/v1/labs/stop")
def stop(payload: LabPathRequest):
    try:
        backend.stop(payload.lab_path)
        return {"lab_path": payload.lab_path, "state": "stopped"}
    except NativeEveError as exc: raise fail(exc) from exc

@app.post("/v1/labs/reset")
def reset(payload: LabPathRequest):
    try:
        backend.reset(payload.lab_path)
        return {"lab_path": payload.lab_path, "state": "provisioned"}
    except NativeEveError as exc: raise fail(exc) from exc

@app.get("/v1/labs")
def get_lab(lab_path: str):
    try: return backend.status(lab_path)
    except NativeEveError as exc: raise fail(exc) from exc

@app.delete("/v1/labs")
def delete(payload: LabPathRequest):
    try:
        backend.delete(payload.lab_path)
        return {"lab_path": payload.lab_path, "state": "deleted"}
    except NativeEveError as exc: raise fail(exc) from exc
