from decimal import Decimal

from fastapi import HTTPException, status
from sqlalchemy import Select, func, select
from sqlalchemy.orm import Session, joinedload, selectinload

from app.models.course import Course
from app.models.enrollment import Enrollment
from app.models.enums import RoleEnum
from app.models.teacher import Teacher
from app.models.user import User
from app.services.course_schedule_service import serialize_course_schedules


def _apply_course_filters(stmt: Select, keyword: str | None, status_text: str | None, term: str | None) -> Select:
    if keyword:
        like_keyword = f"%{keyword.strip()}%"
        stmt = stmt.where((Course.name.like(like_keyword)) | (Course.course_code.like(like_keyword)))
    if status_text:
        stmt = stmt.where(Course.status == status_text)
    if term:
        stmt = stmt.where(Course.term == term)
    return stmt


def _paginate_courses(db: Session, stmt: Select, page: int, page_size: int) -> tuple[int, list[Course]]:
    total = db.scalar(select(func.count()).select_from(stmt.order_by(None).subquery())) or 0
    courses = db.scalars(stmt.offset((page - 1) * page_size).limit(page_size)).unique().all()
    return total, list(courses)


def _build_course_items(
    db: Session,
    courses: list[Course],
    current_user: User | None = None,
    include_schedules: bool = False,
) -> list[dict]:
    if not courses:
        return []

    course_ids = [course.id for course in courses]
    count_rows = db.execute(
        select(Enrollment.course_id, func.count(Enrollment.id))
        .where(Enrollment.course_id.in_(course_ids))
        .group_by(Enrollment.course_id)
    ).all()
    selected_map = {course_id: count for course_id, count in count_rows}
    selected_ids: set[int] = set()

    if current_user and current_user.role == RoleEnum.student and current_user.student:
        selected_ids = set(
            db.scalars(
                select(Enrollment.course_id).where(
                    Enrollment.student_id == current_user.student.id,
                    Enrollment.course_id.in_(course_ids),
                )
            ).all()
        )

    items = []
    for course in courses:
        selected_count = int(selected_map.get(course.id, 0))
        teacher_name = course.teacher.user.real_name if course.teacher and course.teacher.user else "-"
        department_name = course.department.name if course.department else None
        item = {
            "id": course.id,
            "course_code": course.course_code,
            "name": course.name,
            "credit": float(course.credit),
            "hours": course.hours,
            "capacity": course.capacity,
            "term": course.term,
            "status": course.status.value,
            "description": course.description,
            "teacher_id": course.teacher_id,
            "teacher_name": teacher_name,
            "department_id": course.department_id,
            "department_name": department_name,
            "selected_count": selected_count,
            "available_seats": max(course.capacity - selected_count, 0),
            "is_selected": course.id in selected_ids,
            "schedule_count": len(course.schedules),
        }
        if include_schedules:
            item["schedules"] = serialize_course_schedules(list(course.schedules))
        items.append(item)
    return items


def list_courses(
    db: Session,
    page: int,
    page_size: int,
    keyword: str | None,
    status: str | None,
    term: str | None,
    current_user: User | None = None,
):
    stmt = (
        select(Course)
        .options(joinedload(Course.teacher).joinedload(Teacher.user), joinedload(Course.department), selectinload(Course.schedules))
        .order_by(Course.created_at.desc())
    )
    stmt = _apply_course_filters(stmt, keyword, status, term)
    total, courses = _paginate_courses(db, stmt, page, page_size)
    items = _build_course_items(db, courses, current_user)
    return {"total": total, "page": page, "page_size": page_size, "items": items}


def get_course_detail(db: Session, course_id: int, current_user: User | None = None) -> dict:
    stmt = (
        select(Course)
        .options(joinedload(Course.teacher).joinedload(Teacher.user), joinedload(Course.department), selectinload(Course.schedules))
        .where(Course.id == course_id)
    )
    course = db.scalar(stmt)
    if not course:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="课程不存在")
    item = _build_course_items(db, [course], current_user=current_user, include_schedules=True)[0]
    score_rows = db.execute(
        select(
            func.count(Enrollment.id),
            func.avg(Enrollment.score),
            func.max(Enrollment.score),
            func.min(Enrollment.score),
        ).where(Enrollment.course_id == course_id)
    ).one()
    item["score_stats"] = {
        "student_count": int(score_rows[0] or 0),
        "avg_score": round(float(score_rows[1]), 2) if score_rows[1] is not None else None,
        "max_score": float(score_rows[2]) if isinstance(score_rows[2], Decimal) else score_rows[2],
        "min_score": float(score_rows[3]) if isinstance(score_rows[3], Decimal) else score_rows[3],
    }
    return item
