from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.deps import require_roles
from app.core.response import success
from app.models.enums import RoleEnum
from app.schemas.course import CourseCreate, CourseUpdate
from app.services.admin_service import (
    create_course_by_admin,
    delete_course_by_admin,
    get_admin_profile,
    get_course_form_options,
    get_course_statistics_overview,
    list_courses_for_admin,
    update_course_by_admin,
)
from app.services.course_service import get_course_detail

router = APIRouter(dependencies=[Depends(require_roles(RoleEnum.admin))])


@router.get("/me/profile", summary="获取管理员信息")
def admin_profile(current_user=Depends(require_roles(RoleEnum.admin)), db: Session = Depends(get_db)):
    return success(get_admin_profile(db, current_user.id), "获取成功")


@router.get("/courses", summary="管理员课程列表")
def admin_courses(
    keyword: str | None = Query(default=None),
    status: str | None = Query(default=None),
    term: str | None = Query(default=None),
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=10, ge=1, le=100),
    current_user=Depends(require_roles(RoleEnum.admin)),
    db: Session = Depends(get_db),
):
    data = list_courses_for_admin(db, page, page_size, keyword, status, term, current_user)
    return success(data, "获取成功")


@router.post("/courses", summary="管理员新增课程")
def create_course(
    payload: CourseCreate,
    current_user=Depends(require_roles(RoleEnum.admin)),
    db: Session = Depends(get_db),
):
    return success(create_course_by_admin(db, payload), "课程创建成功")


@router.get("/courses/{course_id}", summary="管理员查看课程详情")
def course_detail(course_id: int, current_user=Depends(require_roles(RoleEnum.admin)), db: Session = Depends(get_db)):
    return success(get_course_detail(db, course_id, current_user), "获取成功")


@router.put("/courses/{course_id}", summary="管理员更新课程")
def update_course(
    course_id: int,
    payload: CourseUpdate,
    current_user=Depends(require_roles(RoleEnum.admin)),
    db: Session = Depends(get_db),
):
    return success(update_course_by_admin(db, course_id, payload), "课程更新成功")


@router.delete("/courses/{course_id}", summary="管理员删除课程")
def delete_course(
    course_id: int,
    current_user=Depends(require_roles(RoleEnum.admin)),
    db: Session = Depends(get_db),
):
    return success(delete_course_by_admin(db, course_id), "课程删除成功")


@router.get("/statistics/courses", summary="管理员课程选课统计")
def course_statistics(current_user=Depends(require_roles(RoleEnum.admin)), db: Session = Depends(get_db)):
    return success(get_course_statistics_overview(db), "获取成功")


@router.get("/options/course-form", summary="课程表单基础数据")
def course_form_options(current_user=Depends(require_roles(RoleEnum.admin)), db: Session = Depends(get_db)):
    return success(get_course_form_options(db), "获取成功")
