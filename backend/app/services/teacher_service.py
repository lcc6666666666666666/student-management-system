from fastapi import HTTPException, status
from sqlalchemy import case, func, select
from sqlalchemy.orm import Session, joinedload

from app.models.course import Course
from app.models.enrollment import Enrollment
from app.models.student import Student
from app.models.teacher import Teacher
from app.schemas.teacher import TeacherProfileUpdate


def _get_teacher_by_user_id(db: Session, user_id: int) -> Teacher:
    stmt = (
        select(Teacher)
        .options(joinedload(Teacher.user), joinedload(Teacher.department))
        .where(Teacher.user_id == user_id)
    )
    teacher = db.scalar(stmt)
    if not teacher:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="教师信息不存在")
    return teacher


def _get_owned_course(db: Session, user_id: int, course_id: int) -> Course:
    teacher = _get_teacher_by_user_id(db, user_id)
    stmt = (
        select(Course)
        .options(joinedload(Course.teacher).joinedload(Teacher.user), joinedload(Course.department))
        .where(Course.id == course_id, Course.teacher_id == teacher.id)
    )
    course = db.scalar(stmt)
    if not course:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="课程不存在或不属于当前教师")
    return course


def get_teacher_profile(db: Session, user_id: int) -> dict:
    teacher = _get_teacher_by_user_id(db, user_id)
    return {
        "id": teacher.id,
        "user_id": teacher.user_id,
        "username": teacher.user.username,
        "real_name": teacher.user.real_name,
        "phone": teacher.user.phone,
        "email": teacher.user.email,
        "teacher_no": teacher.teacher_no,
        "title": teacher.title,
        "office": teacher.office,
        "department_id": teacher.department_id,
        "department_name": teacher.department.name if teacher.department else None,
    }


def update_teacher_profile(db: Session, user_id: int, payload: TeacherProfileUpdate) -> dict:
    teacher = _get_teacher_by_user_id(db, user_id)
    teacher.user.real_name = payload.real_name
    teacher.user.phone = payload.phone
    teacher.user.email = payload.email
    teacher.title = payload.title
    teacher.office = payload.office
    db.commit()
    db.refresh(teacher)
    return get_teacher_profile(db, user_id)


def list_teacher_courses(db: Session, user_id: int) -> dict:
    teacher = _get_teacher_by_user_id(db, user_id)
    stmt = (
        select(Course)
        .options(joinedload(Course.department))
        .where(Course.teacher_id == teacher.id)
        .order_by(Course.created_at.desc())
    )
    courses = db.scalars(stmt).all()
    course_ids = [course.id for course in courses]
    count_map = {}
    avg_map = {}
    if course_ids:
        count_rows = db.execute(
            select(Enrollment.course_id, func.count(Enrollment.id), func.avg(Enrollment.score))
            .where(Enrollment.course_id.in_(course_ids))
            .group_by(Enrollment.course_id)
        ).all()
        count_map = {row[0]: int(row[1]) for row in count_rows}
        avg_map = {row[0]: round(float(row[2]), 2) if row[2] is not None else None for row in count_rows}

    items = []
    total_students = 0
    for course in courses:
        selected_count = count_map.get(course.id, 0)
        total_students += selected_count
        items.append(
            {
                "id": course.id,
                "course_code": course.course_code,
                "name": course.name,
                "term": course.term,
                "credit": float(course.credit),
                "hours": course.hours,
                "capacity": course.capacity,
                "status": course.status.value,
                "department_name": course.department.name if course.department else None,
                "selected_count": selected_count,
                "avg_score": avg_map.get(course.id),
            }
        )

    return {
        "summary": {
            "course_count": len(items),
            "student_count": total_students,
            "graded_course_count": len([item for item in items if item["avg_score"] is not None]),
        },
        "items": items,
    }


def list_teacher_course_students(db: Session, user_id: int, course_id: int) -> dict:
    course = _get_owned_course(db, user_id, course_id)
    stmt = (
        select(Enrollment)
        .options(joinedload(Enrollment.student).joinedload(Student.user), joinedload(Enrollment.student).joinedload(Student.department))
        .where(Enrollment.course_id == course_id)
        .order_by(Enrollment.selected_at.asc())
    )
    enrollments = db.scalars(stmt).unique().all()
    items = []
    for enrollment in enrollments:
        student = enrollment.student
        items.append(
            {
                "enrollment_id": enrollment.id,
                "student_id": student.id,
                "student_no": student.student_no,
                "student_name": student.user.real_name,
                "grade": student.grade,
                "class_name": student.class_name,
                "department_name": student.department.name if student.department else None,
                "score": float(enrollment.score) if enrollment.score is not None else None,
                "selected_at": enrollment.selected_at,
            }
        )
    return {
        "course": {
            "id": course.id,
            "course_code": course.course_code,
            "name": course.name,
            "term": course.term,
            "capacity": course.capacity,
        },
        "items": items,
    }


def update_score(db: Session, user_id: int, enrollment_id: int, score: float | None) -> dict:
    teacher = _get_teacher_by_user_id(db, user_id)
    stmt = (
        select(Enrollment)
        .options(joinedload(Enrollment.course), joinedload(Enrollment.student).joinedload(Student.user))
        .where(Enrollment.id == enrollment_id)
    )
    enrollment = db.scalar(stmt)
    if not enrollment:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="选课记录不存在")
    if enrollment.course.teacher_id != teacher.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="不能修改非本人课程成绩")
    enrollment.score = score
    db.commit()
    db.refresh(enrollment)
    return {
        "enrollment_id": enrollment.id,
        "course_id": enrollment.course_id,
        "student_name": enrollment.student.user.real_name,
        "score": float(enrollment.score) if enrollment.score is not None else None,
    }


def teacher_course_statistics(db: Session, user_id: int, course_id: int) -> dict:
    course = _get_owned_course(db, user_id, course_id)
    row = db.execute(
        select(
            func.count(Enrollment.id),
            func.avg(Enrollment.score),
            func.max(Enrollment.score),
            func.min(Enrollment.score),
            func.sum(case((Enrollment.score >= 60, 1), else_=0)),
        ).where(Enrollment.course_id == course_id)
    ).one()
    total = int(row[0] or 0)
    pass_count = int(row[4] or 0)
    return {
        "course_id": course.id,
        "course_name": course.name,
        "selected_count": total,
        "avg_score": round(float(row[1]), 2) if row[1] is not None else None,
        "max_score": float(row[2]) if row[2] is not None else None,
        "min_score": float(row[3]) if row[3] is not None else None,
        "pass_count": pass_count,
        "fail_count": total - pass_count,
        "pass_rate": round((pass_count / total) * 100, 2) if total else None,
    }
