from datetime import datetime, timezone
from fastapi import HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session
from app.models import Lab, LabAssignment, LabTemplate, LabUsage
from app.provider import LabProvider

def get_lab(db: Session, lab_id: int) -> Lab:
    lab = db.scalar(select(Lab).where(Lab.id == lab_id))
    if lab is None:
        raise HTTPException(status_code=404, detail="Lab not found")
    return lab

def require_access(db: Session, lab: Lab, user_id: int) -> None:
    if lab.owner_user_id == user_id:
        return
    assignment = db.scalar(select(LabAssignment).where(LabAssignment.lab_id == lab.id, LabAssignment.user_id == user_id, LabAssignment.status == "active"))
    if assignment is None:
        raise HTTPException(status_code=403, detail="Lab access denied")

def create_lab(db: Session, user_id: int, template_id: int, name: str) -> Lab:
    template = db.scalar(select(LabTemplate).where(LabTemplate.id == template_id, LabTemplate.active.is_(True)))
    if template is None:
        raise HTTPException(status_code=404, detail="Active lab template not found")
    lab = Lab(template_id=template.id, owner_user_id=user_id, name=name)
    db.add(lab); db.commit(); db.refresh(lab)
    return lab

def assign_lab(db: Session, lab: Lab, owner_id: int, target_user_id: int) -> Lab:
    if lab.owner_user_id != owner_id:
        raise HTTPException(status_code=403, detail="Only the lab owner can assign the lab")
    existing = db.scalar(select(LabAssignment).where(LabAssignment.lab_id == lab.id, LabAssignment.user_id == target_user_id))
    if existing is None:
        db.add(LabAssignment(lab_id=lab.id, user_id=target_user_id, status="active"))
    else:
        existing.status = "active"; existing.released_at = None
    db.commit()
    return lab

def provision(db: Session, lab: Lab, user_id: int, provider: LabProvider) -> Lab:
    require_access(db, lab, user_id)
    if lab.state in {"provisioned", "stopped", "running"}: return lab
    if lab.state not in {"created", "assigned", "released", "error"}: raise HTTPException(status_code=409, detail=f"Cannot provision from state '{lab.state}'")
    template = db.scalar(select(LabTemplate).where(LabTemplate.id == lab.template_id))
    lab.state = "provisioning"; lab.error_message = None; db.commit()
    try:
        result = provider.provision(template.key, lab.id, user_id)
        lab.external_reference = result.external_reference; lab.access_url = result.access_url; lab.state = "provisioned"
    except Exception:
        lab.state = "error"; lab.error_message = "Provider provisioning failed"; db.commit()
        raise HTTPException(status_code=502, detail="Lab provider provisioning failed")
    db.commit(); return lab

def start(db: Session, lab: Lab, user_id: int, provider: LabProvider) -> Lab:
    require_access(db, lab, user_id)
    if lab.state == "running": return lab
    if lab.state not in {"provisioned", "stopped"}: raise HTTPException(status_code=409, detail=f"Cannot start from state '{lab.state}'")
    provider.start(lab.external_reference or "")
    lab.state = "running"
    usage = db.scalar(select(LabUsage).where(LabUsage.lab_id == lab.id, LabUsage.stopped_at.is_(None)))
    if usage is None: db.add(LabUsage(lab_id=lab.id, started_at=datetime.now(timezone.utc)))
    db.commit(); return lab

def stop(db: Session, lab: Lab, user_id: int, provider: LabProvider) -> Lab:
    require_access(db, lab, user_id)
    if lab.state == "stopped": return lab
    if lab.state != "running": raise HTTPException(status_code=409, detail=f"Cannot stop from state '{lab.state}'")
    provider.stop(lab.external_reference or "")
    now = datetime.now(timezone.utc)
    usage = db.scalar(select(LabUsage).where(LabUsage.lab_id == lab.id, LabUsage.stopped_at.is_(None)))
    if usage: usage.stopped_at = now; usage.seconds_used = max(0, int((now - usage.started_at).total_seconds())) if usage.started_at else 0
    lab.state = "stopped"; db.commit(); return lab

def reset(db: Session, lab: Lab, user_id: int, provider: LabProvider) -> Lab:
    require_access(db, lab, user_id)
    if lab.state not in {"provisioned", "stopped", "running"}: raise HTTPException(status_code=409, detail=f"Cannot reset from state '{lab.state}'")
    provider.reset(lab.external_reference or "")
    lab.state = "stopped" if lab.state == "stopped" else "provisioned"; db.commit(); return lab

def release(db: Session, lab: Lab, user_id: int, provider: LabProvider) -> Lab:
    require_access(db, lab, user_id)
    if lab.state == "released": return lab
    if lab.state == "running": raise HTTPException(status_code=409, detail="Stop the lab before release")
    provider.release(lab.external_reference or "")
    assignment = db.scalar(select(LabAssignment).where(LabAssignment.lab_id == lab.id, LabAssignment.user_id == user_id, LabAssignment.status == "active"))
    if assignment: assignment.status = "released"; assignment.released_at = datetime.now(timezone.utc)
    lab.owner_user_id = None; lab.state = "released"; db.commit(); return lab

def delete(db: Session, lab: Lab, user_id: int, provider: LabProvider) -> None:
    if lab.owner_user_id != user_id: raise HTTPException(status_code=403, detail="Lab access denied")
    if lab.state == "running": raise HTTPException(status_code=409, detail="Stop the lab before delete")
    if lab.external_reference: provider.delete(lab.external_reference)
    lab.state = "deleted"; db.commit()