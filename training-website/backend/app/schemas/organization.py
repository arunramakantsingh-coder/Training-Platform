from pydantic import BaseModel, Field

class OrganizationCreateRequest(BaseModel):
    name: str = Field(min_length=2, max_length=160)

class OrganizationResponse(BaseModel):
    id: int
    name: str
    slug: str
    status: str

class MembershipCreateRequest(BaseModel):
    user_id: int
    role: str = Field(pattern=r"^(student|trainer|organization_admin)$")

class MembershipResponse(BaseModel):
    id: int
    user_id: int
    organization_id: int
    role: str
