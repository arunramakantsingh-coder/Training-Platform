from datetime import datetime
from pydantic import BaseModel, ConfigDict, Field

class TemplateCreate(BaseModel):
    name: str = Field(min_length=1, max_length=200)
    key: str = Field(min_length=1, max_length=100)
    description: str | None = None

class TemplateResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    name: str
    key: str
    active: bool

class LabCreate(BaseModel):
    template_id: int
    name: str = Field(min_length=1, max_length=200)

class LabResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    template_id: int
    owner_user_id: int | None
    name: str
    state: str
    external_reference: str | None
    access_url: str | None
    error_message: str | None
    created_at: datetime
    updated_at: datetime

class AssignmentCreate(BaseModel):
    user_id: int

class OperationResponse(BaseModel):
    lab: LabResponse
