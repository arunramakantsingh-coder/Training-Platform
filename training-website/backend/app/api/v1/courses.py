import re

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.api.dependencies import require_platform_admin
from app.core.database import get_db
from app.models.course import Course, CourseCategory, CourseModule, CoursePrerequisite, Lesson, LessonLabReference, LessonResource, LessonTopic
from app.models.user import User
from app.schemas.course import CourseCategoryBase, CourseCategoryResponse, CourseCreateRequest, CourseModuleCreateRequest, CourseModuleResponse, CourseModuleUpdateRequest, CourseResponse, CourseUpdateRequest, LabReferenceCreateRequest, LabReferenceResponse, LessonCreateRequest, LessonResponse, LessonUpdateRequest, ResourceCreateRequest, ResourceResponse, TopicCreateRequest, TopicResponse

router = APIRouter(prefix="/courses", tags=["courses"])
admin_router = APIRouter(prefix="/admin/courses", tags=["admin-courses"])


def slugify(value: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", value.lower()).strip("-") or "course"


def unique_course_slug(db: Session, slug: str, course_id: int | None = None) -> str:
    base = slugify(slug)
    candidate, suffix = base, 2
    while True:
        stmt = select(Course).where(Course.slug == candidate)
        if course_id is not None:
            stmt = stmt.where(Course.id != course_id)
        if db.scalar(stmt) is None:
            return candidate
        candidate = f"{base}-{suffix}"
        suffix += 1


def validate_prerequisites(db: Session, course_id: int | None, ids: list[int]) -> None:
    if course_id is not None and course_id in ids:
        raise HTTPException(status_code=400, detail="A course cannot be its own prerequisite")
    if ids:
        existing = set(db.scalars(select(Course.id).where(Course.id.in_(ids))).all())
        missing = sorted(set(ids) - existing)
        if missing:
            raise HTTPException(status_code=400, detail=f"Prerequisite course(s) not found: {missing}")


def replace_prerequisites(db: Session, course_id: int, ids: list[int]) -> None:
    db.query(CoursePrerequisite).filter(CoursePrerequisite.course_id == course_id).delete(synchronize_session=False)
    for prerequisite_id in dict.fromkeys(ids):
        db.add(CoursePrerequisite(course_id=course_id, prerequisite_course_id=prerequisite_id))


def get_course(db: Session, course_id: int) -> Course:
    course = db.get(Course, course_id)
    if course is None:
        raise HTTPException(status_code=404, detail="Course not found")
    return course


def get_lesson_for_course(db: Session, course_id: int, module_id: int, lesson_id: int) -> Lesson:
    lesson = db.get(Lesson, lesson_id)
    module = db.get(CourseModule, module_id)
    if lesson is None or module is None or lesson.module_id != module_id or module.course_id != course_id:
        raise HTTPException(status_code=404, detail="Lesson does not belong to course")
    return lesson


@router.get("", response_model=list[CourseResponse])
def list_published_courses(db: Session = Depends(get_db)) -> list[Course]:
    return list(db.scalars(select(Course).where(Course.status == "published", Course.is_active.is_(True), Course.visibility == "public").order_by(Course.title.asc())).all())


@router.get("/{slug}", response_model=CourseResponse)
def get_published_course(slug: str, db: Session = Depends(get_db)) -> Course:
    course = db.scalar(select(Course).where(Course.slug == slug, Course.status == "published", Course.is_active.is_(True), Course.visibility == "public"))
    if course is None:
        raise HTTPException(status_code=404, detail="Course not found")
    return course


@router.get("/{slug}/structure")
def get_published_course_structure(slug: str, db: Session = Depends(get_db)) -> dict:
    course = db.scalar(select(Course).where(Course.slug == slug, Course.status == "published", Course.is_active.is_(True), Course.visibility == "public"))
    if course is None:
        raise HTTPException(status_code=404, detail="Course not found")
    modules = db.scalars(select(CourseModule).where(CourseModule.course_id == course.id).order_by(CourseModule.order_index.asc())).all()
    return {
        "course": CourseResponse.model_validate(course).model_dump(),
        "modules": [
            {
                "id": module.id,
                "title": module.title,
                "description": module.description,
                "order_index": module.order_index,
                "lessons": [
                    {
                        "id": lesson.id,
                        "title": lesson.title,
                        "slug": lesson.slug,
                        "content_type": lesson.content_type,
                        "content": lesson.content,
                        "order_index": lesson.order_index,
                        "estimated_minutes": lesson.estimated_minutes,
                        "is_required": lesson.is_required,
                    }
                    for lesson in db.scalars(select(Lesson).where(Lesson.module_id == module.id).order_by(Lesson.order_index.asc())).all()
                ],
            }
            for module in modules
        ],
    }


@admin_router.get("", response_model=list[CourseResponse])
def list_courses(_: User = Depends(require_platform_admin), db: Session = Depends(get_db)) -> list[Course]:
    return list(db.scalars(select(Course).order_by(Course.updated_at.desc())).all())


@admin_router.post("", response_model=CourseResponse, status_code=status.HTTP_201_CREATED)
def create_course(payload: CourseCreateRequest, current_user: User = Depends(require_platform_admin), db: Session = Depends(get_db)) -> Course:
    if payload.category_id is not None and db.get(CourseCategory, payload.category_id) is None:
        raise HTTPException(status_code=400, detail="Course category not found")
    validate_prerequisites(db, None, payload.prerequisite_course_ids)
    course = Course(
        title=payload.title, slug=unique_course_slug(db, payload.slug),
        short_description=payload.short_description, description=payload.description,
        category_id=payload.category_id, visibility=payload.visibility, level=payload.level,
        estimated_hours=payload.estimated_hours, created_by_user_id=current_user.id,
    )
    db.add(course)
    db.flush()
    replace_prerequisites(db, course.id, payload.prerequisite_course_ids)
    db.commit()
    db.refresh(course)
    return course


@admin_router.patch("/{course_id}", response_model=CourseResponse)
def update_course(course_id: int, payload: CourseUpdateRequest, _: User = Depends(require_platform_admin), db: Session = Depends(get_db)) -> Course:
    course = get_course(db, course_id)
    if course.status in {"published", "retired"}:
        raise HTTPException(status_code=409, detail="Published or retired courses cannot be edited")
    values = payload.model_dump(exclude_unset=True, exclude={"prerequisite_course_ids"})
    if "category_id" in values and values["category_id"] is not None and db.get(CourseCategory, values["category_id"]) is None:
        raise HTTPException(status_code=400, detail="Course category not found")
    if "slug" in values:
        values["slug"] = unique_course_slug(db, values["slug"], course.id)
    for key, value in values.items():
        setattr(course, key, value)
    if payload.prerequisite_course_ids is not None:
        validate_prerequisites(db, course.id, payload.prerequisite_course_ids)
        replace_prerequisites(db, course.id, payload.prerequisite_course_ids)
    db.commit()
    db.refresh(course)
    return course


@admin_router.get("/{course_id}/prerequisites", response_model=list[CourseResponse])
def list_prerequisites(course_id: int, _: User = Depends(require_platform_admin), db: Session = Depends(get_db)) -> list[Course]:
    course = get_course(db, course_id)
    ids = db.scalars(select(CoursePrerequisite.prerequisite_course_id).where(CoursePrerequisite.course_id == course.id)).all()
    if not ids:
        return []
    return list(db.scalars(select(Course).where(Course.id.in_(ids)).order_by(Course.title.asc())).all())


@admin_router.post("/{course_id}/submit-review", response_model=CourseResponse)
def submit_review(course_id: int, _: User = Depends(require_platform_admin), db: Session = Depends(get_db)) -> Course:
    course = get_course(db, course_id)
    if course.status != "draft":
        raise HTTPException(status_code=409, detail="Only draft courses can be submitted for review")
    course.status = "review"
    db.commit()
    db.refresh(course)
    return course


@admin_router.post("/{course_id}/publish", response_model=CourseResponse)
def publish_course(course_id: int, _: User = Depends(require_platform_admin), db: Session = Depends(get_db)) -> Course:
    course = get_course(db, course_id)
    if course.status != "review":
        raise HTTPException(status_code=409, detail="Only courses in review can be published")
    course.status, course.is_active = "published", True
    db.commit()
    db.refresh(course)
    return course


@admin_router.post("/{course_id}/retire", response_model=CourseResponse)
def retire_course(course_id: int, _: User = Depends(require_platform_admin), db: Session = Depends(get_db)) -> Course:
    course = get_course(db, course_id)
    if course.status != "published":
        raise HTTPException(status_code=409, detail="Only published courses can be retired")
    course.status, course.is_active = "retired", False
    db.commit()
    db.refresh(course)
    return course


@admin_router.post("/categories", response_model=CourseCategoryResponse, status_code=status.HTTP_201_CREATED)
def create_category(payload: CourseCategoryBase, _: User = Depends(require_platform_admin), db: Session = Depends(get_db)) -> CourseCategory:
    slug = slugify(payload.slug)
    if db.scalar(select(CourseCategory).where(CourseCategory.slug == slug)):
        raise HTTPException(status_code=409, detail="Course category slug already exists")
    category = CourseCategory(name=payload.name, slug=slug, description=payload.description)
    db.add(category)
    db.commit()
    db.refresh(category)
    return category


@admin_router.get("/categories", response_model=list[CourseCategoryResponse])
def list_categories(_: User = Depends(require_platform_admin), db: Session = Depends(get_db)) -> list[CourseCategory]:
    return list(db.scalars(select(CourseCategory).order_by(CourseCategory.name.asc())).all())


@admin_router.post("/{course_id}/modules", response_model=CourseModuleResponse, status_code=status.HTTP_201_CREATED)
def create_module(course_id: int, payload: CourseModuleCreateRequest, _: User = Depends(require_platform_admin), db: Session = Depends(get_db)) -> CourseModule:
    course = get_course(db, course_id)
    if course.status in {"published", "retired"}:
        raise HTTPException(status_code=409, detail="Published or retired courses cannot be edited")
    if db.scalar(select(CourseModule).where(CourseModule.course_id == course_id, CourseModule.order_index == payload.order_index)):
        raise HTTPException(status_code=409, detail="Module order already exists")
    module = CourseModule(course_id=course_id, **payload.model_dump())
    db.add(module)
    db.commit()
    db.refresh(module)
    return module


@admin_router.patch("/{course_id}/modules/{module_id}", response_model=CourseModuleResponse)
def update_module(course_id: int, module_id: int, payload: CourseModuleUpdateRequest, _: User = Depends(require_platform_admin), db: Session = Depends(get_db)) -> CourseModule:
    module = db.get(CourseModule, module_id)
    course = get_course(db, course_id)
    if module is None or module.course_id != course_id:
        raise HTTPException(status_code=404, detail="Course module not found")
    if course.status in {"published", "retired"}:
        raise HTTPException(status_code=409, detail="Published or retired courses cannot be edited")
    values = payload.model_dump(exclude_unset=True)
    if "order_index" in values and values["order_index"] != module.order_index:
        if db.scalar(select(CourseModule).where(CourseModule.course_id == course_id, CourseModule.order_index == values["order_index"], CourseModule.id != module_id)):
            raise HTTPException(status_code=409, detail="Module order already exists")
    for key, value in values.items():
        setattr(module, key, value)
    db.commit(); db.refresh(module); return module

@admin_router.get("/{course_id}/modules", response_model=list[CourseModuleResponse])
def list_modules(course_id: int, _: User = Depends(require_platform_admin), db: Session = Depends(get_db)) -> list[CourseModule]:
    get_course(db, course_id)
    return list(db.scalars(select(CourseModule).where(CourseModule.course_id == course_id).order_by(CourseModule.order_index.asc())).all())


@admin_router.post("/{course_id}/modules/{module_id}/lessons", response_model=LessonResponse, status_code=status.HTTP_201_CREATED)
def create_lesson(course_id: int, module_id: int, payload: LessonCreateRequest, _: User = Depends(require_platform_admin), db: Session = Depends(get_db)) -> Lesson:
    module = db.get(CourseModule, module_id)
    if module is None or module.course_id != course_id:
        raise HTTPException(status_code=404, detail="Course module not found")
    course = get_course(db, course_id)
    if course.status in {"published", "retired"}:
        raise HTTPException(status_code=409, detail="Published or retired courses cannot be edited")
    if db.scalar(select(Lesson).where(Lesson.module_id == module_id, Lesson.order_index == payload.order_index)):
        raise HTTPException(status_code=409, detail="Lesson order already exists")
    lesson = Lesson(module_id=module_id, **payload.model_dump())
    db.add(lesson)
    db.commit()
    db.refresh(lesson)
    return lesson


@admin_router.patch("/{course_id}/modules/{module_id}/lessons/{lesson_id}", response_model=LessonResponse)
def update_lesson(course_id: int, module_id: int, lesson_id: int, payload: LessonUpdateRequest, _: User = Depends(require_platform_admin), db: Session = Depends(get_db)) -> Lesson:
    lesson = get_lesson_for_course(db, course_id, module_id, lesson_id)
    course = get_course(db, course_id)
    if course.status in {"published", "retired"}:
        raise HTTPException(status_code=409, detail="Published or retired courses cannot be edited")
    values = payload.model_dump(exclude_unset=True)
    if "order_index" in values and values["order_index"] != lesson.order_index:
        if db.scalar(select(Lesson).where(Lesson.module_id == module_id, Lesson.order_index == values["order_index"], Lesson.id != lesson_id)):
            raise HTTPException(status_code=409, detail="Lesson order already exists")
    for key, value in values.items():
        setattr(lesson, key, value)
    db.commit(); db.refresh(lesson); return lesson

@admin_router.get("/{course_id}/modules/{module_id}/lessons", response_model=list[LessonResponse])
def list_lessons(course_id: int, module_id: int, _: User = Depends(require_platform_admin), db: Session = Depends(get_db)) -> list[Lesson]:
    module = db.get(CourseModule, module_id)
    if module is None or module.course_id != course_id:
        raise HTTPException(status_code=404, detail="Course module not found")
    return list(db.scalars(select(Lesson).where(Lesson.module_id == module_id).order_by(Lesson.order_index.asc())).all())


@admin_router.get("/{course_id}/modules/{module_id}/lessons/{lesson_id}/topics", response_model=list[TopicResponse])
def list_topics(course_id: int, module_id: int, lesson_id: int, _: User = Depends(require_platform_admin), db: Session = Depends(get_db)) -> list[LessonTopic]:
    lesson = get_lesson_for_course(db, course_id, module_id, lesson_id)
    return list(db.scalars(select(LessonTopic).where(LessonTopic.lesson_id == lesson.id).order_by(LessonTopic.order_index.asc())).all())


@admin_router.post("/{course_id}/modules/{module_id}/lessons/{lesson_id}/topics", response_model=TopicResponse, status_code=status.HTTP_201_CREATED)
def create_topic(course_id: int, module_id: int, lesson_id: int, payload: TopicCreateRequest, _: User = Depends(require_platform_admin), db: Session = Depends(get_db)) -> LessonTopic:
    lesson = get_lesson_for_course(db, course_id, module_id, lesson_id)
    course = get_course(db, course_id)
    if course.status in {"published", "retired"}:
        raise HTTPException(status_code=409, detail="Published or retired courses cannot be edited")
    if db.scalar(select(LessonTopic).where(LessonTopic.lesson_id == lesson.id, LessonTopic.order_index == payload.order_index)):
        raise HTTPException(status_code=409, detail="Topic order already exists")
    topic = LessonTopic(lesson_id=lesson.id, **payload.model_dump())
    db.add(topic)
    db.commit()
    db.refresh(topic)
    return topic


@admin_router.get("/{course_id}/modules/{module_id}/lessons/{lesson_id}/resources", response_model=list[ResourceResponse])
def list_resources(course_id: int, module_id: int, lesson_id: int, _: User = Depends(require_platform_admin), db: Session = Depends(get_db)) -> list[LessonResource]:
    lesson = get_lesson_for_course(db, course_id, module_id, lesson_id)
    return list(db.scalars(select(LessonResource).where(LessonResource.lesson_id == lesson.id).order_by(LessonResource.id.asc())).all())


@admin_router.post("/{course_id}/modules/{module_id}/lessons/{lesson_id}/resources", response_model=ResourceResponse, status_code=status.HTTP_201_CREATED)
def create_resource(course_id: int, module_id: int, lesson_id: int, payload: ResourceCreateRequest, _: User = Depends(require_platform_admin), db: Session = Depends(get_db)) -> LessonResource:
    lesson = get_lesson_for_course(db, course_id, module_id, lesson_id)
    course = get_course(db, course_id)
    if course.status in {"published", "retired"}:
        raise HTTPException(status_code=409, detail="Published or retired courses cannot be edited")
    resource = LessonResource(lesson_id=lesson.id, **payload.model_dump())
    db.add(resource)
    db.commit()
    db.refresh(resource)
    return resource


@admin_router.get("/{course_id}/modules/{module_id}/lessons/{lesson_id}/lab-references", response_model=list[LabReferenceResponse])
def list_lab_references(course_id: int, module_id: int, lesson_id: int, _: User = Depends(require_platform_admin), db: Session = Depends(get_db)) -> list[LessonLabReference]:
    lesson = get_lesson_for_course(db, course_id, module_id, lesson_id)
    return list(db.scalars(select(LessonLabReference).where(LessonLabReference.lesson_id == lesson.id).order_by(LessonLabReference.id.asc())).all())


@admin_router.post("/{course_id}/modules/{module_id}/lessons/{lesson_id}/lab-references", response_model=LabReferenceResponse, status_code=status.HTTP_201_CREATED)
def create_lab_reference(course_id: int, module_id: int, lesson_id: int, payload: LabReferenceCreateRequest, _: User = Depends(require_platform_admin), db: Session = Depends(get_db)) -> LessonLabReference:
    lesson = get_lesson_for_course(db, course_id, module_id, lesson_id)
    course = get_course(db, course_id)
    if course.status in {"published", "retired"}:
        raise HTTPException(status_code=409, detail="Published or retired courses cannot be edited")
    reference = LessonLabReference(lesson_id=lesson.id, **payload.model_dump())
    db.add(reference)
    db.commit()
    db.refresh(reference)
    return reference
