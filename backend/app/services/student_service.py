from fastapi import HTTPException, status
from sqlalchemy import func, select
from sqlalchemy.orm import Session, joinedload

from app.models.course import Course
from app.models.enrollment import Enrollment
from app.models.enums import CourseStatusEnum
from app.models.student import Student
from app.models.teacher import Teacher
from app.schemas.student import StudentProfileUpdate


def _get_student_by_user_id(db: Session, user_id: int) -> Student:
    stmt = (
        select(Student)
        .options(joinedload(Student.user), joinedload(Student.department))
        .where(Student.user_id == user_id)
    )
    student = db.scalar(stmt)
    if not student:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="学生信息不存在")
    return student


def get_student_profile(db: Session, user_id: int) -> dict:
    student = _get_student_by_user_id(db, user_id)
    return {
        "id": student.id,
        "user_id": student.user_id,
        "username": student.user.username,
        "real_name": student.user.real_name,
        "phone": student.user.phone,
        "email": student.user.email,
        "student_no": student.student_no,
        "gender": student.gender,
        "grade": student.grade,
        "class_name": student.class_name,
        "admission_year": student.admission_year,
        "department_id": student.department_id,
        "department_name": student.department.name if student.department else None,
    }


def update_student_profile(db: Session, user_id: int, payload: StudentProfileUpdate) -> dict:
    student = _get_student_by_user_id(db, user_id)
    student.user.real_name = payload.real_name
    student.user.phone = payload.phone
    student.user.email = payload.email
    student.gender = payload.gender
    student.grade = payload.grade
    student.class_name = payload.class_name
    db.commit()
    db.refresh(student)
    return get_student_profile(db, user_id)


def list_student_courses(db: Session, user_id: int) -> dict:
    student = _get_student_by_user_id(db, user_id)
    stmt = (
        select(Enrollment)
        .options(
            joinedload(Enrollment.course).joinedload(Course.teacher).joinedload(Teacher.user),
            joinedload(Enrollment.course).joinedload(Course.department),
        )
        .where(Enrollment.student_id == student.id)
        .order_by(Enrollment.selected_at.desc())
    )
    enrollments = db.scalars(stmt).unique().all()
    items = []
    for enrollment in enrollments:
        course = enrollment.course
        items.append(
            {
                "enrollment_id": enrollment.id,
                "course_id": course.id,
                "course_code": course.course_code,
                "course_name": course.name,
                "teacher_name": course.teacher.user.real_name if course.teacher and course.teacher.user else "-",
                "department_name": course.department.name if course.department else None,
                "term": course.term,
                "credit": float(course.credit),
                "hours": course.hours,
                "status": course.status.value,
                "score": float(enrollment.score) if enrollment.score is not None else None,
                "selected_at": enrollment.selected_at,
            }
        )
    return {"total": len(items), "items": items}


def list_student_grades(db: Session, user_id: int) -> dict:
    student = _get_student_by_user_id(db, user_id)
    stmt = (
        select(Enrollment)
        .options(joinedload(Enrollment.course).joinedload(Course.teacher).joinedload(Teacher.user))
        .where(Enrollment.student_id == student.id)
        .order_by(Enrollment.selected_at.desc())
    )
    enrollments = db.scalars(stmt).unique().all()
    grade_items = []
    scores = []
    for enrollment in enrollments:
        score = float(enrollment.score) if enrollment.score is not None else None
        if score is not None:
            scores.append(score)
        grade_items.append(
            {
                "enrollment_id": enrollment.id,
                "course_code": enrollment.course.course_code,
                "course_name": enrollment.course.name,
                "teacher_name": enrollment.course.teacher.user.real_name if enrollment.course.teacher and enrollment.course.teacher.user else "-",
                "term": enrollment.course.term,
                "credit": float(enrollment.course.credit),
                "score": score,
                "status": "已录入" if score is not None else "待录入",
            }
        )

    passed = len([score for score in scores if score >= 60])
    return {
        "summary": {
            "graded_count": len(scores),
            "passed_count": passed,
            "failed_count": len(scores) - passed,
            "avg_score": round(sum(scores) / len(scores), 2) if scores else None,
        },
        "items": grade_items,
    }


def enroll_course(db: Session, user_id: int, course_id: int) -> dict:
    student = _get_student_by_user_id(db, user_id)
    course = db.scalar(select(Course).where(Course.id == course_id))
    if not course:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="课程不存在")
    if course.status != CourseStatusEnum.open:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="当前课程未开放选课")

    exists = db.scalar(select(Enrollment).where(Enrollment.student_id == student.id, Enrollment.course_id == course_id))
    if exists:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="不能重复选课")

    selected_count = db.scalar(select(func.count(Enrollment.id)).where(Enrollment.course_id == course_id)) or 0
    if selected_count >= course.capacity:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="课程容量已满")

    enrollment = Enrollment(student_id=student.id, course_id=course_id)
    db.add(enrollment)
    db.commit()
    db.refresh(enrollment)
    return {"enrollment_id": enrollment.id, "course_id": course_id, "student_id": student.id}


def drop_course(db: Session, user_id: int, course_id: int) -> dict:
    student = _get_student_by_user_id(db, user_id)
    enrollment = db.scalar(select(Enrollment).where(Enrollment.student_id == student.id, Enrollment.course_id == course_id))
    if not enrollment:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="未找到选课记录")
    if enrollment.score is not None:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="成绩已录入的课程不允许退课")

    db.delete(enrollment)
    db.commit()
    return {"course_id": course_id, "student_id": student.id}
