from fastapi import HTTPException, status
from sqlalchemy import func, select
from sqlalchemy.orm import Session, joinedload

from app.models.admin import Admin
from app.models.course import Course
from app.models.department import Department
from app.models.enrollment import Enrollment
from app.models.teacher import Teacher
from app.schemas.course import CourseCreate, CourseUpdate
from app.services.course_service import list_courses


def _get_admin_by_user_id(db: Session, user_id: int) -> Admin:
    stmt = select(Admin).options(joinedload(Admin.user)).where(Admin.user_id == user_id)
    admin = db.scalar(stmt)
    if not admin:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="管理员信息不存在")
    return admin


def _validate_course_refs(db: Session, teacher_id: int, department_id: int | None):
    teacher = db.scalar(select(Teacher).where(Teacher.id == teacher_id))
    if not teacher:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="授课教师不存在")
    if department_id is not None:
        department = db.scalar(select(Department).where(Department.id == department_id))
        if not department:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="所属院系不存在")


def get_admin_profile(db: Session, user_id: int) -> dict:
    admin = _get_admin_by_user_id(db, user_id)
    return {
        "id": admin.id,
        "user_id": admin.user_id,
        "username": admin.user.username,
        "real_name": admin.user.real_name,
        "phone": admin.user.phone,
        "email": admin.user.email,
        "admin_no": admin.admin_no,
        "level": admin.level,
    }


def list_courses_for_admin(
    db: Session,
    page: int,
    page_size: int,
    keyword: str | None,
    status: str | None,
    term: str | None,
    current_user,
):
    return list_courses(db, page, page_size, keyword, status, term, current_user)


def create_course_by_admin(db: Session, payload: CourseCreate) -> dict:
    exists = db.scalar(select(Course).where(Course.course_code == payload.course_code))
    if exists:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="课程编号已存在")
    _validate_course_refs(db, payload.teacher_id, payload.department_id)

    course = Course(
        course_code=payload.course_code,
        name=payload.name,
        credit=payload.credit,
        hours=payload.hours,
        capacity=payload.capacity,
        term=payload.term,
        status=payload.status,
        description=payload.description,
        teacher_id=payload.teacher_id,
        department_id=payload.department_id,
    )
    db.add(course)
    db.commit()
    db.refresh(course)
    return {"id": course.id}


def update_course_by_admin(db: Session, course_id: int, payload: CourseUpdate) -> dict:
    course = db.scalar(select(Course).where(Course.id == course_id))
    if not course:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="课程不存在")
    code_conflict = db.scalar(select(Course).where(Course.course_code == payload.course_code, Course.id != course_id))
    if code_conflict:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="课程编号已存在")
    _validate_course_refs(db, payload.teacher_id, payload.department_id)

    course.course_code = payload.course_code
    course.name = payload.name
    course.credit = payload.credit
    course.hours = payload.hours
    course.capacity = payload.capacity
    course.term = payload.term
    course.status = payload.status
    course.description = payload.description
    course.teacher_id = payload.teacher_id
    course.department_id = payload.department_id
    db.commit()
    db.refresh(course)
    return {"id": course.id}


def delete_course_by_admin(db: Session, course_id: int) -> dict:
    course = db.scalar(select(Course).where(Course.id == course_id))
    if not course:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="课程不存在")
    enrollment_exists = db.scalar(select(func.count(Enrollment.id)).where(Enrollment.course_id == course_id)) or 0
    if enrollment_exists:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="当前课程已有选课记录，不能删除")
    db.delete(course)
    db.commit()
    return {"id": course_id}


def get_course_statistics_overview(db: Session) -> dict:
    total_courses = db.scalar(select(func.count(Course.id))) or 0
    open_courses = db.scalar(select(func.count(Course.id)).where(Course.status == "open")) or 0
    total_enrollments = db.scalar(select(func.count(Enrollment.id))) or 0
    average_capacity = db.scalar(select(func.avg(Course.capacity)))
    course_rows = db.execute(
        select(
            Course.id,
            Course.course_code,
            Course.name,
            Course.term,
            Course.capacity,
            func.count(Enrollment.id).label("selected_count"),
        )
        .outerjoin(Enrollment, Enrollment.course_id == Course.id)
        .group_by(Course.id)
        .order_by(func.count(Enrollment.id).desc(), Course.created_at.desc())
    ).all()
    hot_courses = [
        {
            "course_id": row[0],
            "course_code": row[1],
            "course_name": row[2],
            "term": row[3],
            "capacity": row[4],
            "selected_count": int(row[5] or 0),
            "occupancy_rate": round((int(row[5] or 0) / row[4]) * 100, 2) if row[4] else 0,
        }
        for row in course_rows[:6]
    ]
    return {
        "summary": {
            "total_courses": int(total_courses),
            "open_courses": int(open_courses),
            "closed_courses": int(total_courses - open_courses),
            "total_enrollments": int(total_enrollments),
            "average_capacity": round(float(average_capacity), 2) if average_capacity is not None else None,
        },
        "hot_courses": hot_courses,
    }


def get_course_form_options(db: Session) -> dict:
    departments = db.execute(select(Department.id, Department.name, Department.code).order_by(Department.id.asc())).all()
    teacher_entities = db.execute(select(Teacher).options(joinedload(Teacher.user), joinedload(Teacher.department))).scalars().all()
    teachers = [
        {
            "id": teacher.id,
            "teacher_no": teacher.teacher_no,
            "name": teacher.user.real_name,
            "title": teacher.title,
            "department_id": teacher.department_id,
            "department_name": teacher.department.name if teacher.department else None,
        }
        for teacher in teacher_entities
    ]
    return {
        "teachers": teachers,
        "departments": [{"id": row[0], "name": row[1], "code": row[2]} for row in departments],
        "status_options": [
            {"label": "开放", "value": "open"},
            {"label": "关闭", "value": "closed"},
        ],
    }
