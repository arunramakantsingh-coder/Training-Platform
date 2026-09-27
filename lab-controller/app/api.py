from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.orm import Session
from app.auth import current_user_id
from app.database import get_db
from app.models import Lab, LabTemplate
from app.provider import MockLabProvider
from app.schemas import AssignmentCreate, LabCreate, LabResponse, OperationResponse, TemplateCreate, TemplateResponse
from app.service import assign_lab, create_lab, delete, get_lab, provision, release, reset, require_access, start, stop

router = APIRouter(prefix="/api/v1/labs", tags=["labs"])
provider = MockLabProvider()

@router.get("/templates", response_model=list[TemplateResponse])
def templates(db: Session = Depends(get_db), _: int = Depends(current_user_id)):
    return list(db.scalars(select(LabTemplate).where(LabTemplate.active.is_(True)).order_by(LabTemplate.id)))

@router.post("/templates", response_model=TemplateResponse)
def create_template(payload: TemplateCreate, db: Session = Depends(get_db), _: int = Depends(current_user_id)):
    item = LabTemplate(**payload.model_dump())
    db.add(item); db.commit(); db.refresh(item); return item

@router.post("", response_model=LabResponse)
def create(payload: LabCreate, db: Session = Depends(get_db), user_id: int = Depends(current_user_id)):
    return create_lab(db, user_id, payload.template_id, payload.name)

@router.get("/{lab_id}", response_model=LabResponse)
def read(lab_id: int, db: Session = Depends(get_db), user_id: int = Depends(current_user_id)):
    lab = get_lab(db, lab_id); require_access(db, lab, user_id); return lab

@router.post("/{lab_id}/assign", response_model=LabResponse)
def assign(lab_id: int, payload: AssignmentCreate, db: Session = Depends(get_db), user_id: int = Depends(current_user_id)):
    return assign_lab(db, get_lab(db, lab_id), user_id, payload.user_id)

@router.post("/{lab_id}/provision", response_model=OperationResponse)
def provision_route(lab_id: int, db: Session = Depends(get_db), user_id: int = Depends(current_user_id)):
    return {"lab": provision(db, get_lab(db, lab_id), user_id, provider)}

@router.post("/{lab_id}/start", response_model=OperationResponse)
def start_route(lab_id: int, db: Session = Depends(get_db), user_id: int = Depends(current_user_id)):
    return {"lab": start(db, get_lab(db, lab_id), user_id, provider)}

@router.post("/{lab_id}/stop", response_model=OperationResponse)
def stop_route(lab_id: int, db: Session = Depends(get_db), user_id: int = Depends(current_user_id)):
    return {"lab": stop(db, get_lab(db, lab_id), user_id, provider)}

@router.post("/{lab_id}/reset", response_model=OperationResponse)
def reset_route(lab_id: int, db: Session = Depends(get_db), user_id: int = Depends(current_user_id)):
    return {"lab": reset(db, get_lab(db, lab_id), user_id, provider)}

@router.get("/{lab_id}/status", response_model=LabResponse)
def status(lab_id: int, db: Session = Depends(get_db), user_id: int = Depends(current_user_id)):
    lab = get_lab(db, lab_id); require_access(db, lab, user_id)
    if lab.external_reference: provider.status(lab.external_reference)
    return lab

@router.post("/{lab_id}/release", response_model=OperationResponse)
def release_route(lab_id: int, db: Session = Depends(get_db), user_id: int = Depends(current_user_id)):
    return {"lab": release(db, get_lab(db, lab_id), user_id, provider)}

@router.delete("/{lab_id}")
def delete_route(lab_id: int, db: Session = Depends(get_db), user_id: int = Depends(current_user_id)):
    delete(db, get_lab(db, lab_id), user_id, provider)
    return {"status": "deleted", "lab_id": lab_id}