import re

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.api.dependencies import get_current_user
from app.core.database import get_db
from app.models.membership import Membership
from app.models.organization import Organization
from app.models.user import User
from app.schemas.organization import MembershipCreateRequest, MembershipResponse, OrganizationCreateRequest, OrganizationResponse

router = APIRouter(prefix="/organizations", tags=["organizations"])

def slugify(value: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", value.lower()).strip("-") or "organization"

def is_org_admin(db: Session, user_id: int, organization_id: int) -> bool:
    return db.scalar(select(Membership).where(Membership.user_id == user_id, Membership.organization_id == organization_id, Membership.role == "organization_admin")) is not None

@router.post("", response_model=OrganizationResponse, status_code=status.HTTP_201_CREATED)
def create_organization(payload: OrganizationCreateRequest, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)) -> Organization:
    base = slugify(payload.name)
    slug = base
    suffix = 2
    while db.scalar(select(Organization).where(Organization.slug == slug)):
        slug = f"{base}-{suffix}"
        suffix += 1
    organization = Organization(name=payload.name, slug=slug)
    db.add(organization)
    db.flush()
    db.add(Membership(user_id=current_user.id, organization_id=organization.id, role="organization_admin"))
    db.commit()
    db.refresh(organization)
    return organization

@router.get("", response_model=list[OrganizationResponse])
def list_my_organizations(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)) -> list[Organization]:
    stmt = select(Organization).join(Membership, Membership.organization_id == Organization.id).where(Membership.user_id == current_user.id).order_by(Organization.name.asc())
    return list(db.scalars(stmt).all())

@router.post("/{organization_id}/members", response_model=MembershipResponse, status_code=status.HTTP_201_CREATED)
def add_member(organization_id: int, payload: MembershipCreateRequest, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)) -> Membership:
    if db.get(Organization, organization_id) is None:
        raise HTTPException(status_code=404, detail="Organization not found")
    if not current_user.is_platform_admin and not is_org_admin(db, current_user.id, organization_id):
        raise HTTPException(status_code=403, detail="Organization administrator access required")
    if db.get(User, payload.user_id) is None:
        raise HTTPException(status_code=404, detail="User not found")
    if db.scalar(select(Membership).where(Membership.user_id == payload.user_id, Membership.organization_id == organization_id)):
        raise HTTPException(status_code=409, detail="User is already a member")
    membership = Membership(user_id=payload.user_id, organization_id=organization_id, role=payload.role)
    db.add(membership)
    db.commit()
    db.refresh(membership)
    return membership
