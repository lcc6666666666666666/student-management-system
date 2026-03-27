from fastapi import APIRouter

from app.api.v1.endpoints import admins, auth, courses, dashboard, students, teachers

api_router = APIRouter()
api_router.include_router(auth.router, prefix="/auth", tags=["认证"])
api_router.include_router(dashboard.router, prefix="/dashboard", tags=["仪表盘"])
api_router.include_router(courses.router, prefix="/courses", tags=["课程"])
api_router.include_router(students.router, prefix="/students", tags=["学生"])
api_router.include_router(teachers.router, prefix="/teachers", tags=["教师"])
api_router.include_router(admins.router, prefix="/admins", tags=["管理员"])
