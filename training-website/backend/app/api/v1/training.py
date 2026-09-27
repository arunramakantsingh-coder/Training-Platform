from datetime import datetime, timezone
import re
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import func, select
from sqlalchemy.orm import Session
from app.api.dependencies import get_current_user, require_platform_admin
from app.core.database import get_db
from app.models.course import Course, CourseModule, Lesson
from app.models.training import Enrollment, LessonProgress, TrainingSession
from app.models.user import User
from app.schemas.training import EnrollmentCreateRequest, EnrollmentResponse, LearnerCourseResponse, ProgressResponse, ProgressUpdateRequest, TrainingSessionCreateRequest, TrainingSessionResponse, TrainingSessionUpdateRequest

router = APIRouter(prefix="/training", tags=["training"])
admin_router = APIRouter(prefix="/admin/training", tags=["admin-training"])

def slugify(value: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", value.lower()).strip("-") or "session"

def course_or_404(db: Session, course_id: int) -> Course:
    course = db.get(Course, course_id)
    if course is None: raise HTTPException(status_code=404, detail="Course not found")
    return course

def session_or_404(db: Session, session_id: int) -> TrainingSession:
    item = db.get(TrainingSession, session_id)
    if item is None: raise HTTPException(status_code=404, detail="Training session not found")
    return item

def enrollment_or_404(db: Session, enrollment_id: int) -> Enrollment:
    item = db.get(Enrollment, enrollment_id)
    if item is None: raise HTTPException(status_code=404, detail="Enrollment not found")
    return item

def active_enrollment(db: Session, course_id: int, user_id: int) -> Enrollment | None:
    return db.scalar(select(Enrollment).where(Enrollment.course_id == course_id, Enrollment.user_id == user_id, Enrollment.status.in_(["active", "completed"])))

def course_structure(db: Session, course: Course) -> tuple[list[dict], list[int]]:
    modules = db.scalars(select(CourseModule).where(CourseModule.course_id == course.id).order_by(CourseModule.order_index.asc())).all()
    lesson_ids=[]; output=[]
    for module in modules:
        lessons=db.scalars(select(Lesson).where(Lesson.module_id == module.id).order_by(Lesson.order_index.asc())).all()
        lesson_ids.extend(x.id for x in lessons)
        output.append({"id":module.id,"title":module.title,"description":module.description,"order_index":module.order_index,"lessons":[{"id":x.id,"title":x.title,"slug":x.slug,"content_type":x.content_type,"content":x.content,"order_index":x.order_index,"estimated_minutes":x.estimated_minutes,"is_required":x.is_required} for x in lessons]})
    return output, lesson_ids

@router.get("/courses", response_model=list[dict])
def public_courses(db: Session=Depends(get_db)) -> list[dict]:
    courses=db.scalars(select(Course).where(Course.status=="published",Course.is_active.is_(True),Course.visibility=="public").order_by(Course.title.asc())).all()
    return [{"id":c.id,"title":c.title,"slug":c.slug,"short_description":c.short_description,"level":c.level,"estimated_hours":c.estimated_hours} for c in courses]

@router.get("/courses/{slug}", response_model=LearnerCourseResponse)
def learner_course(slug:str,current_user:User=Depends(get_current_user),db:Session=Depends(get_db)) -> LearnerCourseResponse:
    course=db.scalar(select(Course).where(Course.slug==slug,Course.status=="published",Course.is_active.is_(True),Course.visibility=="public"))
    if course is None: raise HTTPException(status_code=404,detail="Course not found")
    modules,lesson_ids=course_structure(db,course); enrollment=active_enrollment(db,course.id,current_user.id); percent=0
    if enrollment and lesson_ids:
        completed=db.scalar(select(func.count(LessonProgress.id)).where(LessonProgress.enrollment_id==enrollment.id,LessonProgress.lesson_id.in_(lesson_ids),LessonProgress.status=="completed")) or 0
        percent=round(completed*100/len(lesson_ids))
    return LearnerCourseResponse(course={"id":course.id,"title":course.title,"slug":course.slug,"short_description":course.short_description,"description":course.description,"level":course.level,"estimated_hours":course.estimated_hours},modules=modules,enrollment=enrollment,progress_percent=percent)

@router.post("/courses/{course_id}/enroll",response_model=EnrollmentResponse,status_code=status.HTTP_201_CREATED)
def enroll_self(course_id:int,payload:EnrollmentCreateRequest|None=None,current_user:User=Depends(get_current_user),db:Session=Depends(get_db))->Enrollment:
    course=course_or_404(db,course_id)
    if course.status!="published" or not course.is_active or course.visibility!="public": raise HTTPException(status_code=409,detail="Course is not open for public enrollment")
    existing=active_enrollment(db,course_id,current_user.id)
    if existing: return existing
    session_id=payload.training_session_id if payload else None
    if session_id is not None:
        session=session_or_404(db,session_id)
        if session.course_id!=course_id or session.status!="open": raise HTTPException(status_code=409,detail="Training session is not open")
        if session.enrollment_limit is not None:
            count=db.scalar(select(func.count(Enrollment.id)).where(Enrollment.training_session_id==session.id,Enrollment.status=="active")) or 0
            if count>=session.enrollment_limit: raise HTTPException(status_code=409,detail="Training session is full")
    enrollment=Enrollment(course_id=course_id,training_session_id=session_id,user_id=current_user.id,status="active")
    db.add(enrollment);db.commit();db.refresh(enrollment);return enrollment

@router.post("/enrollments/{enrollment_id}/progress/{lesson_id}",response_model=ProgressResponse)
def update_progress(enrollment_id:int,lesson_id:int,payload:ProgressUpdateRequest,current_user:User=Depends(get_current_user),db:Session=Depends(get_db))->LessonProgress:
    enrollment=enrollment_or_404(db,enrollment_id)
    if enrollment.user_id!=current_user.id and not current_user.is_platform_admin: raise HTTPException(status_code=403,detail="Enrollment access required")
    lesson=db.get(Lesson,lesson_id); module=db.get(CourseModule,lesson.module_id) if lesson else None
    if lesson is None or module is None or module.course_id!=enrollment.course_id: raise HTTPException(status_code=400,detail="Lesson does not belong to enrollment course")
    item=db.scalar(select(LessonProgress).where(LessonProgress.enrollment_id==enrollment_id,LessonProgress.lesson_id==lesson_id))
    if item is None: item=LessonProgress(enrollment_id=enrollment_id,lesson_id=lesson_id);db.add(item)
    item.status=payload.status;item.completed_at=datetime.now(timezone.utc) if payload.status=="completed" else None
    if payload.status=="completed":
        total=db.scalar(select(func.count(Lesson.id)).join(CourseModule,Lesson.module_id==CourseModule.id).where(CourseModule.course_id==enrollment.course_id)) or 0
        completed=db.scalar(select(func.count(LessonProgress.id)).where(LessonProgress.enrollment_id==enrollment.id,LessonProgress.status=="completed")) or 0
        if total and completed>=total: enrollment.status="completed";enrollment.completed_at=datetime.now(timezone.utc)
    db.commit();db.refresh(item);return item

@router.get("/enrollments/{enrollment_id}/progress",response_model=list[ProgressResponse])
def list_progress(enrollment_id:int,current_user:User=Depends(get_current_user),db:Session=Depends(get_db))->list[LessonProgress]:
    enrollment=enrollment_or_404(db,enrollment_id)
    if enrollment.user_id!=current_user.id and not current_user.is_platform_admin: raise HTTPException(status_code=403,detail="Enrollment access required")
    return list(db.scalars(select(LessonProgress).where(LessonProgress.enrollment_id==enrollment_id).order_by(LessonProgress.lesson_id.asc())).all())

@admin_router.get("/sessions",response_model=list[TrainingSessionResponse])
def list_sessions(_:User=Depends(require_platform_admin),db:Session=Depends(get_db))->list[TrainingSession]:
    return list(db.scalars(select(TrainingSession).order_by(TrainingSession.start_at.asc().nullslast(),TrainingSession.name.asc())).all())

@admin_router.post("/courses/{course_id}/sessions",response_model=TrainingSessionResponse,status_code=status.HTTP_201_CREATED)
def create_session(course_id:int,payload:TrainingSessionCreateRequest,_:User=Depends(require_platform_admin),db:Session=Depends(get_db))->TrainingSession:
    course=course_or_404(db,course_id);slug=slugify(payload.slug)
    if db.scalar(select(TrainingSession).where(TrainingSession.course_id==course_id,TrainingSession.slug==slug)): raise HTTPException(status_code=409,detail="Training session slug already exists for this course")
    if payload.trainer_user_id is not None and db.get(User,payload.trainer_user_id) is None: raise HTTPException(status_code=400,detail="Trainer user not found")
    item=TrainingSession(course_id=course.id,**payload.model_dump(exclude={"slug"}),slug=slug);db.add(item);db.commit();db.refresh(item);return item

@admin_router.get("/courses/{course_id}/sessions",response_model=list[TrainingSessionResponse])
def course_sessions(course_id:int,_:User=Depends(require_platform_admin),db:Session=Depends(get_db))->list[TrainingSession]:
    course_or_404(db,course_id)
    return list(db.scalars(select(TrainingSession).where(TrainingSession.course_id==course_id).order_by(TrainingSession.start_at.asc().nullslast())).all())

@admin_router.patch("/sessions/{session_id}",response_model=TrainingSessionResponse)
def update_session(session_id:int,payload:TrainingSessionUpdateRequest,_:User=Depends(require_platform_admin),db:Session=Depends(get_db))->TrainingSession:
    item=session_or_404(db,session_id);values=payload.model_dump(exclude_unset=True)
    if "trainer_user_id" in values and values["trainer_user_id"] is not None and db.get(User,values["trainer_user_id"]) is None: raise HTTPException(status_code=400,detail="Trainer user not found")
    if "slug" in values: values["slug"]=slugify(values["slug"])
    for key,value in values.items(): setattr(item,key,value)
    db.commit();db.refresh(item);return item

@admin_router.get("/enrollments",response_model=list[EnrollmentResponse])
def admin_enrollments(_:User=Depends(require_platform_admin),db:Session=Depends(get_db))->list[Enrollment]:
    return list(db.scalars(select(Enrollment).order_by(Enrollment.enrolled_at.desc())).all())

@admin_router.post("/courses/{course_id}/enrollments",response_model=EnrollmentResponse,status_code=status.HTTP_201_CREATED)
def admin_enroll(course_id:int,payload:EnrollmentCreateRequest,_:User=Depends(require_platform_admin),db:Session=Depends(get_db))->Enrollment:
    course=course_or_404(db,course_id)
    if payload.user_id is None: raise HTTPException(status_code=400,detail="user_id is required")
    if db.get(User,payload.user_id) is None: raise HTTPException(status_code=404,detail="User not found")
    existing=db.scalar(select(Enrollment).where(Enrollment.course_id==course_id,Enrollment.user_id==payload.user_id,Enrollment.status.in_(["active","completed"])))
    if existing:return existing
    session=session_or_404(db,payload.training_session_id) if payload.training_session_id else None
    if session and session.course_id!=course_id: raise HTTPException(status_code=400,detail="Training session does not belong to course")
    item=Enrollment(course_id=course.id,training_session_id=session.id if session else None,user_id=payload.user_id,organization_id=payload.organization_id,status="active")
    db.add(item);db.commit();db.refresh(item);return item
