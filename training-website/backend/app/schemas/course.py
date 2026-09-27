from typing import Literal

from pydantic import BaseModel, ConfigDict, Field

CourseStatus = Literal["draft", "review", "published", "retired"]
CourseVisibility = Literal["public", "private", "organization"]
LessonContentType = Literal["text", "video", "document", "quiz", "lab_reference"]
ResourceType = Literal["link", "document", "video", "other"]


class CourseCategoryBase(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True)
    name: str = Field(min_length=2, max_length=120)
    slug: str = Field(min_length=2, max_length=120)
    description: str | None = Field(default=None, max_length=2000)


class CourseCategoryResponse(CourseCategoryBase):
    model_config = ConfigDict(from_attributes=True)
    id: int


class CourseCreateRequest(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True)
    title: str = Field(min_length=2, max_length=200)
    slug: str = Field(min_length=2, max_length=200)
    short_description: str | None = Field(default=None, max_length=500)
    description: str | None = None
    category_id: int | None = None
    visibility: CourseVisibility = "public"
    level: str | None = Field(default=None, max_length=32)
    estimated_hours: int | None = Field(default=None, ge=0, le=10000)
    prerequisite_course_ids: list[int] = Field(default_factory=list)


class CourseUpdateRequest(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True)
    title: str | None = Field(default=None, min_length=2, max_length=200)
    slug: str | None = Field(default=None, min_length=2, max_length=200)
    short_description: str | None = Field(default=None, max_length=500)
    description: str | None = None
    category_id: int | None = None
    visibility: CourseVisibility | None = None
    level: str | None = Field(default=None, max_length=32)
    estimated_hours: int | None = Field(default=None, ge=0, le=10000)
    prerequisite_course_ids: list[int] | None = None


class CourseResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    title: str
    slug: str
    short_description: str | None
    description: str | None
    category_id: int | None
    status: CourseStatus
    visibility: CourseVisibility
    level: str | None
    estimated_hours: int | None
    is_active: bool
    created_by_user_id: int


class CourseModuleCreateRequest(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True)
    title: str = Field(min_length=2, max_length=200)
    description: str | None = None
    order_index: int = Field(ge=0)


class CourseModuleUpdateRequest(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True)
    title: str | None = Field(default=None, min_length=2, max_length=200)
    description: str | None = None
    order_index: int | None = Field(default=None, ge=0)


class CourseModuleResponse(CourseModuleCreateRequest):
    model_config = ConfigDict(from_attributes=True)
    id: int
    course_id: int


class LessonCreateRequest(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True)
    title: str = Field(min_length=2, max_length=200)
    slug: str = Field(min_length=2, max_length=200)
    content_type: LessonContentType = "text"
    content: str | None = None
    order_index: int = Field(ge=0)
    estimated_minutes: int | None = Field(default=None, ge=0, le=100000)
    is_required: bool = True


class LessonUpdateRequest(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True)
    title: str | None = Field(default=None, min_length=2, max_length=200)
    slug: str | None = Field(default=None, min_length=2, max_length=200)
    content_type: LessonContentType | None = None
    content: str | None = None
    order_index: int | None = Field(default=None, ge=0)
    estimated_minutes: int | None = Field(default=None, ge=0, le=100000)
    is_required: bool | None = None


class LessonResponse(LessonCreateRequest):
    model_config = ConfigDict(from_attributes=True)
    id: int
    module_id: int


class TopicCreateRequest(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True)
    title: str = Field(min_length=2, max_length=200)
    content: str | None = None
    order_index: int = Field(ge=0)


class TopicResponse(TopicCreateRequest):
    model_config = ConfigDict(from_attributes=True)
    id: int
    lesson_id: int


class ResourceCreateRequest(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True)
    name: str = Field(min_length=2, max_length=200)
    resource_type: ResourceType = "link"
    url: str = Field(min_length=1, max_length=1000)
    description: str | None = None


class ResourceResponse(ResourceCreateRequest):
    model_config = ConfigDict(from_attributes=True)
    id: int
    lesson_id: int


class LabReferenceCreateRequest(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True)
    reference_key: str = Field(min_length=1, max_length=200)
    display_name: str | None = Field(default=None, max_length=200)
    metadata_json: str | None = None


class LabReferenceResponse(LabReferenceCreateRequest):
    model_config = ConfigDict(from_attributes=True)
    id: int
    lesson_id: int
