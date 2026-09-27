from pydantic import BaseModel, Field

class ProvisionRequest(BaseModel):
    template_path: str = Field(min_length=1, max_length=1000)
    lab_path: str = Field(min_length=1, max_length=1000)

class LabPathRequest(BaseModel):
    lab_path: str = Field(min_length=1, max_length=1000)
