from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.deps import require_roles
from app.core.response import success
from app.models.enums import RoleEnum
from app.schemas.course import CourseCreate, CourseScheduleCreate, CourseScheduleUpdate, CourseUpdate
from app.schemas.department import DepartmentCreate, DepartmentUpdate
from app.services.admin_service import (
    assign_course_to_student_by_admin,
    create_course_by_admin,
    create_department_by_admin,
    delete_course_by_admin,
    delete_department_by_admin,
    drop_course_from_student_by_admin,
    get_admin_profile,
    get_course_form_options,
    get_course_statistics_overview,
    get_department_statistics_overview,
    get_student_courses_for_admin,
    list_departments_for_admin,
    list_courses_for_admin,
    list_students_for_admin,
    update_department_by_admin,
    update_course_by_admin,
)
from app.services.course_schedule_service import (
    create_course_schedule,
    delete_course_schedule,
    list_course_schedules,
    update_course_schedule,
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


@router.get("/students", summary="管理员查看学生列表")
def admin_students(
    keyword: str | None = Query(default=None),
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=10, ge=1, le=100),
    current_user=Depends(require_roles(RoleEnum.admin)),
    db: Session = Depends(get_db),
):
    return success(list_students_for_admin(db, page, page_size, keyword), "获取成功")


@router.get("/departments", summary="管理员查看院系列表")
def admin_departments(
    keyword: str | None = Query(default=None),
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=10, ge=1, le=100),
    current_user=Depends(require_roles(RoleEnum.admin)),
    db: Session = Depends(get_db),
):
    return success(list_departments_for_admin(db, page, page_size, keyword), "获取成功")


@router.post("/departments", summary="管理员新增院系")
def create_department(
    payload: DepartmentCreate,
    current_user=Depends(require_roles(RoleEnum.admin)),
    db: Session = Depends(get_db),
):
    return success(create_department_by_admin(db, payload), "院系创建成功")


@router.put("/departments/{department_id}", summary="管理员更新院系")
def update_department(
    department_id: int,
    payload: DepartmentUpdate,
    current_user=Depends(require_roles(RoleEnum.admin)),
    db: Session = Depends(get_db),
):
    return success(update_department_by_admin(db, department_id, payload), "院系更新成功")


@router.delete("/departments/{department_id}", summary="管理员删除院系")
def delete_department(
    department_id: int,
    current_user=Depends(require_roles(RoleEnum.admin)),
    db: Session = Depends(get_db),
):
    return success(delete_department_by_admin(db, department_id), "院系删除成功")


@router.get("/students/{student_id}/courses", summary="管理员查看学生已选课程")
def admin_student_courses(student_id: int, current_user=Depends(require_roles(RoleEnum.admin)), db: Session = Depends(get_db)):
    return success(get_student_courses_for_admin(db, student_id), "获取成功")


@router.post("/students/{student_id}/courses/{course_id}", summary="管理员为学生代选课")
def admin_assign_course(
    student_id: int,
    course_id: int,
    current_user=Depends(require_roles(RoleEnum.admin)),
    db: Session = Depends(get_db),
):
    return success(assign_course_to_student_by_admin(db, current_user.id, student_id, course_id), "代选课成功")


@router.delete("/students/{student_id}/courses/{course_id}", summary="管理员为学生退课")
def admin_drop_course(
    student_id: int,
    course_id: int,
    current_user=Depends(require_roles(RoleEnum.admin)),
    db: Session = Depends(get_db),
):
    return success(drop_course_from_student_by_admin(db, current_user.id, student_id, course_id), "退课成功")


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


@router.get("/courses/{course_id}/schedules", summary="管理员查看课程时间安排")
def admin_course_schedules(course_id: int, current_user=Depends(require_roles(RoleEnum.admin)), db: Session = Depends(get_db)):
    return success(list_course_schedules(db, course_id), "获取成功")


@router.post("/courses/{course_id}/schedules", summary="管理员新增课程时间安排")
def admin_create_course_schedule(
    course_id: int,
    payload: CourseScheduleCreate,
    current_user=Depends(require_roles(RoleEnum.admin)),
    db: Session = Depends(get_db),
):
    return success(create_course_schedule(db, course_id, payload), "时间安排创建成功")


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


@router.put("/course-schedules/{schedule_id}", summary="管理员修改课程时间安排")
def admin_update_course_schedule(
    schedule_id: int,
    payload: CourseScheduleUpdate,
    current_user=Depends(require_roles(RoleEnum.admin)),
    db: Session = Depends(get_db),
):
    return success(update_course_schedule(db, schedule_id, payload), "时间安排更新成功")


@router.delete("/course-schedules/{schedule_id}", summary="管理员删除课程时间安排")
def admin_delete_course_schedule(
    schedule_id: int,
    current_user=Depends(require_roles(RoleEnum.admin)),
    db: Session = Depends(get_db),
):
    return success(delete_course_schedule(db, schedule_id), "时间安排删除成功")


@router.get("/statistics/courses", summary="管理员课程选课统计")
def course_statistics(current_user=Depends(require_roles(RoleEnum.admin)), db: Session = Depends(get_db)):
    return success(get_course_statistics_overview(db), "获取成功")


@router.get("/statistics/departments", summary="管理员院系统计")
def department_statistics(current_user=Depends(require_roles(RoleEnum.admin)), db: Session = Depends(get_db)):
    return success(get_department_statistics_overview(db), "获取成功")


@router.get("/options/course-form", summary="课程表单基础数据")
def course_form_options(current_user=Depends(require_roles(RoleEnum.admin)), db: Session = Depends(get_db)):
    return success(get_course_form_options(db), "获取成功")
