from datetime import datetime
from pydantic import BaseModel, ConfigDict, Field

class TrainingSessionCreateRequest(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True)
    name: str = Field(min_length=2, max_length=200)
    slug: str = Field(min_length=2, max_length=200)
    description: str | None = None
    trainer_user_id: int | None = None
    start_at: datetime | None = None
    end_at: datetime | None = None
    enrollment_limit: int | None = Field(default=None, ge=1, le=100000)

class TrainingSessionUpdateRequest(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True)
    name: str | None = Field(default=None, min_length=2, max_length=200)
    slug: str | None = Field(default=None, min_length=2, max_length=200)
    description: str | None = None
    trainer_user_id: int | None = None
    start_at: datetime | None = None
    end_at: datetime | None = None
    enrollment_limit: int | None = Field(default=None, ge=1, le=100000)
    status: str | None = None

class TrainingSessionResponse(TrainingSessionCreateRequest):
    model_config = ConfigDict(from_attributes=True)
    id: int
    course_id: int
    status: str

class EnrollmentResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    course_id: int
    training_session_id: int | None
    user_id: int
    organization_id: int | None
    status: str
    enrolled_at: datetime
    completed_at: datetime | None

class EnrollmentCreateRequest(BaseModel):
    training_session_id: int | None = None
    user_id: int | None = None
    organization_id: int | None = None

class ProgressUpdateRequest(BaseModel):
    status: str = Field(pattern="^(not_started|in_progress|completed)$")

class ProgressResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    enrollment_id: int
    lesson_id: int
    status: str
    completed_at: datetime | None

class LearnerCourseResponse(BaseModel):
    course: dict
    modules: list[dict]
    enrollment: EnrollmentResponse | None
    progress_percent: int
