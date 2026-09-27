from pydantic import BaseModel, Field


class ProvisionRequest(BaseModel):
    template_key: str = Field(min_length=1, max_length=100)
    lab_id: int
    user_id: int


class ReferenceRequest(BaseModel):
    external_reference: str = Field(min_length=1, max_length=1000)
