from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.api.dependencies import require_platform_admin
from app.core.database import get_db
from app.models.organization import Organization
from app.models.user import User
from app.schemas.auth import UserResponse
from app.schemas.organization import OrganizationResponse

router = APIRouter(prefix="/admin", tags=["admin"])

@router.get("/users", response_model=list[UserResponse])
def list_users(_: User = Depends(require_platform_admin), db: Session = Depends(get_db)) -> list[User]:
    return list(db.scalars(select(User).order_by(User.created_at.desc())).all())

@router.get("/organizations", response_model=list[OrganizationResponse])
def list_organizations(_: User = Depends(require_platform_admin), db: Session = Depends(get_db)) -> list[Organization]:
    return list(db.scalars(select(Organization).order_by(Organization.created_at.desc())).all())
