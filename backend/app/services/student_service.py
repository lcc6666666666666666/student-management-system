from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session, joinedload

from app.models.course import Course
from app.models.enrollment import Enrollment
from app.models.student import Student
from app.models.teacher import Teacher
from app.schemas.student import StudentProfileUpdate
from app.services.course_schedule_service import get_weekday_label
from app.services.enrollment_service import drop_course_for_student_user, enroll_course_for_student_user


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


def _get_student_by_id(db: Session, student_id: int) -> Student:
    stmt = (
        select(Student)
        .options(joinedload(Student.user), joinedload(Student.department))
        .where(Student.id == student_id)
    )
    student = db.scalar(stmt)
    if not student:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="学生不存在")
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


def _serialize_student_course_enrollment(enrollment: Enrollment) -> dict:
    course = enrollment.course
    return {
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


def _load_student_enrollments(db: Session, student_id: int) -> list[Enrollment]:
    stmt = (
        select(Enrollment)
        .options(
            joinedload(Enrollment.course).joinedload(Course.teacher).joinedload(Teacher.user),
            joinedload(Enrollment.course).joinedload(Course.department),
        )
        .where(Enrollment.student_id == student_id)
        .order_by(Enrollment.selected_at.desc())
    )
    return list(db.scalars(stmt).unique().all())


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
    items = [_serialize_student_course_enrollment(item) for item in _load_student_enrollments(db, student.id)]
    return {"total": len(items), "items": items}


def list_student_courses_by_student_id(db: Session, student_id: int) -> dict:
    student = _get_student_by_id(db, student_id)
    items = [_serialize_student_course_enrollment(item) for item in _load_student_enrollments(db, student.id)]
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
    return enroll_course_for_student_user(db, user_id, course_id)


def drop_course(db: Session, user_id: int, course_id: int) -> dict:
    return drop_course_for_student_user(db, user_id, course_id)


def get_student_timetable(db: Session, user_id: int, term: str | None = None) -> dict:
    student = _get_student_by_user_id(db, user_id)

    selected_term = term
    if not selected_term:
        selected_term = db.scalar(
            select(Course.term)
            .join(Enrollment, Enrollment.course_id == Course.id)
            .where(Enrollment.student_id == student.id)
            .distinct()
            .order_by(Course.term.desc())
            .limit(1)
        )

    weekday_items = {index: [] for index in range(1, 8)}
    weekdays = [{"value": index, "label": get_weekday_label(index), "items": weekday_items[index]} for index in range(1, 8)]
    if not selected_term:
        return {
            "term": None,
            "summary": {
                "total_courses": 0,
                "scheduled_courses": 0,
                "total_schedule_items": 0,
                "unscheduled_courses": 0,
            },
            "weekdays": weekdays,
            "items": [],
            "unscheduled_courses": [],
        }

    stmt = (
        select(Enrollment)
        .join(Course, Course.id == Enrollment.course_id)
        .options(
            joinedload(Enrollment.course).joinedload(Course.teacher).joinedload(Teacher.user),
            joinedload(Enrollment.course).joinedload(Course.department),
            joinedload(Enrollment.course).selectinload(Course.schedules),
        )
        .where(Enrollment.student_id == student.id, Course.term == selected_term)
        .order_by(Course.name.asc(), Enrollment.selected_at.asc())
    )
    enrollments = db.scalars(stmt).unique().all()

    items = []
    unscheduled_courses = []
    scheduled_course_ids: set[int] = set()

    for enrollment in enrollments:
        course = enrollment.course
        teacher_name = course.teacher.user.real_name if course.teacher and course.teacher.user else "-"
        if not course.schedules:
            unscheduled_courses.append(
                {
                    "course_id": course.id,
                    "course_code": course.course_code,
                    "course_name": course.name,
                    "teacher_name": teacher_name,
                    "term": course.term,
                }
            )
            continue

        scheduled_course_ids.add(course.id)
        for schedule in sorted(course.schedules, key=lambda item: (item.weekday, item.start_section, item.start_week, item.id)):
            timetable_item = {
                "course_id": course.id,
                "course_code": course.course_code,
                "course_name": course.name,
                "teacher_name": teacher_name,
                "location": schedule.location,
                "weekday": schedule.weekday,
                "weekday_label": get_weekday_label(schedule.weekday),
                "start_section": schedule.start_section,
                "end_section": schedule.end_section,
                "start_week": schedule.start_week,
                "end_week": schedule.end_week,
                "term": course.term,
            }
            items.append(timetable_item)
            weekday_items[schedule.weekday].append(timetable_item)

    for day_items in weekday_items.values():
        day_items.sort(key=lambda item: (item["start_section"], item["start_week"], item["course_name"]))

    return {
        "term": selected_term,
        "summary": {
            "total_courses": len(enrollments),
            "scheduled_courses": len(scheduled_course_ids),
            "total_schedule_items": len(items),
            "unscheduled_courses": len(unscheduled_courses),
        },
        "weekdays": weekdays,
        "items": items,
        "unscheduled_courses": unscheduled_courses,
    }
