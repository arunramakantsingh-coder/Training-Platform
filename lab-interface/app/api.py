from fastapi import APIRouter, HTTPException

from app.contracts import LabInterfaceResult
from app.eve_ng import EveNGError, LabConnector
from app.schemas import ProvisionRequest, ReferenceRequest


router = APIRouter(prefix="/api/v1/lab-interface", tags=["lab-interface"])
adapter = LabConnector()


def _execute(fn) -> dict:
    try:
        result: LabInterfaceResult = fn()
        return {
            "external_reference": result.external_reference,
            "access_url": result.access_url,
            "state": result.state,
        }
    except EveNGError as exc:
        raise HTTPException(status_code=502, detail=str(exc)) from exc


@router.post("/provision")
def provision(payload: ProvisionRequest):
    return _execute(lambda: adapter.provision(payload.template_key, payload.lab_id, payload.user_id))


@router.post("/start")
def start(payload: ReferenceRequest):
    return _execute(lambda: adapter.start(payload.external_reference))


@router.post("/stop")
def stop(payload: ReferenceRequest):
    return _execute(lambda: adapter.stop(payload.external_reference))


@router.post("/reset")
def reset(payload: ReferenceRequest):
    return _execute(lambda: adapter.reset(payload.external_reference))


@router.post("/status")
def status(payload: ReferenceRequest):
    return _execute(lambda: adapter.status(payload.external_reference))


@router.post("/release")
def release(payload: ReferenceRequest):
    return _execute(lambda: adapter.release(payload.external_reference))


@router.post("/delete")
def delete(payload: ReferenceRequest):
    return _execute(lambda: adapter.delete(payload.external_reference))
