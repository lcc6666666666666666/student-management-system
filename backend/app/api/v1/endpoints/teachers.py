from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.deps import require_roles
from app.core.response import success
from app.models.enums import RoleEnum
from app.schemas.teacher import ScoreUpdateRequest, TeacherProfileUpdate
from app.services.teacher_service import (
    get_teacher_profile,
    list_teacher_course_students,
    list_teacher_courses,
    teacher_course_statistics,
    update_score,
    update_teacher_profile,
)
#不是教师无法访问
router = APIRouter(dependencies=[Depends(require_roles(RoleEnum.teacher))])


@router.get("/me/profile", summary="获取教师个人信息")
def teacher_profile(current_user=Depends(require_roles(RoleEnum.teacher)), db: Session = Depends(get_db)):
    return success(get_teacher_profile(db, current_user.id), "获取成功")


@router.put("/me/profile", summary="更新教师个人信息")
def update_profile(
    payload: TeacherProfileUpdate,#被解析成 TeacherProfileUpdate 这个 schema
    current_user=Depends(require_roles(RoleEnum.teacher)),
    db: Session = Depends(get_db),
):
    return success(update_teacher_profile(db, current_user.id, payload), "更新成功")


@router.get("/courses", summary="获取教师授课课程")
def teacher_courses(current_user=Depends(require_roles(RoleEnum.teacher)), db: Session = Depends(get_db)):
    return success(list_teacher_courses(db, current_user.id), "获取成功")


@router.get("/courses/{course_id}/students", summary="获取课程学生名单")
def course_students(course_id: int, current_user=Depends(require_roles(RoleEnum.teacher)), db: Session = Depends(get_db)):
    return success(list_teacher_course_students(db, current_user.id, course_id), "获取成功")


@router.get("/courses/{course_id}/stats", summary="课程成绩统计")
def course_stats(course_id: int, current_user=Depends(require_roles(RoleEnum.teacher)), db: Session = Depends(get_db)):
    return success(teacher_course_statistics(db, current_user.id, course_id), "获取成功")


@router.put("/enrollments/{enrollment_id}/score", summary="录入或修改成绩")
def update_enrollment_score(
    enrollment_id: int,#不是按 student_id 改，而是按 enrollment_id 改
    payload: ScoreUpdateRequest,
    current_user=Depends(require_roles(RoleEnum.teacher)),
    db: Session = Depends(get_db),
):
    return success(update_score(db, current_user.id, enrollment_id, payload.score), "成绩已保存")
