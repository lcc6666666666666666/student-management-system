from fastapi import HTTPException, status
from sqlalchemy import func, or_, select
from sqlalchemy.orm import Session, joinedload

from app.models.admin import Admin
from app.models.course import Course
from app.models.department import Department
from app.models.enrollment import Enrollment
from app.models.student import Student
from app.models.teacher import Teacher
from app.models.user import User
from app.schemas.course import CourseCreate, CourseUpdate
from app.schemas.department import DepartmentCreate, DepartmentUpdate
from app.services.course_service import list_courses
from app.services.enrollment_service import assign_course_by_admin, drop_course_by_admin
from app.services.student_service import _get_student_by_id, list_student_courses_by_student_id


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


def _get_department_by_id(db: Session, department_id: int) -> Department:
    department = db.scalar(select(Department).where(Department.id == department_id))
    if not department:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="院系不存在")
    return department


def _normalize_department_payload(payload: DepartmentCreate | DepartmentUpdate) -> tuple[str, str, str | None]:
    name = payload.name.strip()
    code = payload.code.strip()
    description = payload.description.strip() if payload.description else None
    if not name:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="院系名称不能为空")
    if not code:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="院系编码不能为空")
    return name, code, description or None


def _validate_department_uniqueness(db: Session, name: str, code: str, exclude_id: int | None = None):
    name_stmt = select(Department).where(Department.name == name)
    code_stmt = select(Department).where(Department.code == code)
    if exclude_id is not None:
        name_stmt = name_stmt.where(Department.id != exclude_id)
        code_stmt = code_stmt.where(Department.id != exclude_id)

    if db.scalar(name_stmt):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="院系名称已存在")
    if db.scalar(code_stmt):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="院系编码已存在")


def _build_department_count_maps(db: Session, department_ids: list[int]) -> tuple[dict[int, int], dict[int, int], dict[int, int]]:
    if not department_ids:
        return {}, {}, {}

    student_rows = db.execute(
        select(Student.department_id, func.count(Student.id))
        .where(Student.department_id.in_(department_ids))
        .group_by(Student.department_id)
    ).all()
    teacher_rows = db.execute(
        select(Teacher.department_id, func.count(Teacher.id))
        .where(Teacher.department_id.in_(department_ids))
        .group_by(Teacher.department_id)
    ).all()
    course_rows = db.execute(
        select(Course.department_id, func.count(Course.id))
        .where(Course.department_id.in_(department_ids))
        .group_by(Course.department_id)
    ).all()

    student_map = {int(row[0]): int(row[1]) for row in student_rows if row[0] is not None}
    teacher_map = {int(row[0]): int(row[1]) for row in teacher_rows if row[0] is not None}
    course_map = {int(row[0]): int(row[1]) for row in course_rows if row[0] is not None}
    return student_map, teacher_map, course_map


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


def list_departments_for_admin(db: Session, page: int, page_size: int, keyword: str | None) -> dict:
    stmt = select(Department).order_by(Department.id.asc())
    if keyword:
        like_keyword = f"%{keyword.strip()}%"
        stmt = stmt.where(or_(Department.name.like(like_keyword), Department.code.like(like_keyword)))

    total = db.scalar(select(func.count()).select_from(stmt.order_by(None).subquery())) or 0
    departments = db.scalars(stmt.offset((page - 1) * page_size).limit(page_size)).all()
    department_ids = [department.id for department in departments]
    student_map, teacher_map, course_map = _build_department_count_maps(db, department_ids)

    items = [
        {
            "id": department.id,
            "name": department.name,
            "code": department.code,
            "description": department.description,
            "created_at": department.created_at.isoformat() if department.created_at else None,
            "student_count": student_map.get(department.id, 0),
            "teacher_count": teacher_map.get(department.id, 0),
            "course_count": course_map.get(department.id, 0),
        }
        for department in departments
    ]
    return {"total": total, "page": page, "page_size": page_size, "items": items}


def create_department_by_admin(db: Session, payload: DepartmentCreate) -> dict:
    name, code, description = _normalize_department_payload(payload)
    _validate_department_uniqueness(db, name, code)

    department = Department(name=name, code=code, description=description)
    db.add(department)
    db.commit()
    db.refresh(department)
    return {"id": department.id}


def update_department_by_admin(db: Session, department_id: int, payload: DepartmentUpdate) -> dict:
    department = _get_department_by_id(db, department_id)
    name, code, description = _normalize_department_payload(payload)
    _validate_department_uniqueness(db, name, code, exclude_id=department_id)

    department.name = name
    department.code = code
    department.description = description
    db.commit()
    db.refresh(department)
    return {"id": department.id}


def delete_department_by_admin(db: Session, department_id: int) -> dict:
    department = _get_department_by_id(db, department_id)

    student_count = db.scalar(select(func.count(Student.id)).where(Student.department_id == department_id)) or 0
    teacher_count = db.scalar(select(func.count(Teacher.id)).where(Teacher.department_id == department_id)) or 0
    course_count = db.scalar(select(func.count(Course.id)).where(Course.department_id == department_id)) or 0

    if student_count or teacher_count or course_count:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="当前院系已关联学生、教师或课程，不能删除",
        )

    db.delete(department)
    db.commit()
    return {"id": department_id}


def list_students_for_admin(db: Session, page: int, page_size: int, keyword: str | None) -> dict:
    stmt = (
        select(Student)
        .join(User, User.id == Student.user_id)
        .options(joinedload(Student.user), joinedload(Student.department))
        .order_by(Student.id.asc())
    )
    if keyword:
        like_keyword = f"%{keyword.strip()}%"
        stmt = stmt.where(
            or_(
                Student.student_no.like(like_keyword),
                User.real_name.like(like_keyword),
                User.username.like(like_keyword),
            )
        )

    total = db.scalar(select(func.count()).select_from(stmt.order_by(None).subquery())) or 0
    students = db.scalars(stmt.offset((page - 1) * page_size).limit(page_size)).unique().all()

    selected_map = {}
    student_ids = [student.id for student in students]
    if student_ids:
        rows = db.execute(
            select(Enrollment.student_id, func.count(Enrollment.id))
            .where(Enrollment.student_id.in_(student_ids))
            .group_by(Enrollment.student_id)
        ).all()
        selected_map = {row[0]: int(row[1]) for row in rows}

    items = [
        {
            "id": student.id,
            "user_id": student.user_id,
            "student_no": student.student_no,
            "username": student.user.username,
            "real_name": student.user.real_name,
            "grade": student.grade,
            "class_name": student.class_name,
            "department_name": student.department.name if student.department else None,
            "selected_course_count": selected_map.get(student.id, 0),
        }
        for student in students
    ]
    return {"total": total, "page": page, "page_size": page_size, "items": items}


def get_student_courses_for_admin(db: Session, student_id: int) -> dict:
    student = _get_student_by_id(db, student_id)
    course_data = list_student_courses_by_student_id(db, student.id)
    return {
        "student": {
            "id": student.id,
            "student_no": student.student_no,
            "real_name": student.user.real_name,
            "username": student.user.username,
            "grade": student.grade,
            "class_name": student.class_name,
            "department_name": student.department.name if student.department else None,
        },
        "total": course_data["total"],
        "items": course_data["items"],
    }


def assign_course_to_student_by_admin(db: Session, operator_user_id: int, student_id: int, course_id: int) -> dict:
    return assign_course_by_admin(db, operator_user_id, student_id, course_id)


def drop_course_from_student_by_admin(db: Session, operator_user_id: int, student_id: int, course_id: int) -> dict:
    return drop_course_by_admin(db, operator_user_id, student_id, course_id)


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


def get_department_statistics_overview(db: Session) -> dict:
    departments = db.scalars(select(Department).order_by(Department.id.asc())).all()
    department_ids = [department.id for department in departments]
    student_map, teacher_map, course_map = _build_department_count_maps(db, department_ids)

    hot_departments = [
        {
            "department_id": department.id,
            "name": department.name,
            "code": department.code,
            "student_count": student_map.get(department.id, 0),
            "teacher_count": teacher_map.get(department.id, 0),
            "course_count": course_map.get(department.id, 0),
            "total_related": student_map.get(department.id, 0) + teacher_map.get(department.id, 0) + course_map.get(department.id, 0),
        }
        for department in departments
    ]
    hot_departments.sort(key=lambda item: (-item["total_related"], -item["course_count"], item["department_id"]))

    return {
        "summary": {
            "total_departments": len(departments),
            "assigned_students": int(sum(student_map.values())),
            "assigned_teachers": int(sum(teacher_map.values())),
            "assigned_courses": int(sum(course_map.values())),
        },
        "hot_departments": hot_departments[:6],
    }


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
