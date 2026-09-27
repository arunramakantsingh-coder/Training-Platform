from fastapi import APIRouter

from app.api.v1.admin import router as admin_router
from app.api.v1.auth import router as auth_router
from app.api.v1.courses import admin_router as admin_courses_router
from app.api.v1.courses import router as courses_router
from app.api.v1.organizations import router as organizations_router

api_router = APIRouter()
api_router.include_router(auth_router)
api_router.include_router(organizations_router)
api_router.include_router(admin_router)
api_router.include_router(courses_router)
api_router.include_router(admin_courses_router)
