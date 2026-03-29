from fastapi import HTTPException, status
from sqlalchemy import func, select
from sqlalchemy.orm import Session, joinedload, selectinload

from app.models.course import Course
from app.models.enrollment import Enrollment
from app.models.enrollment_operation_log import EnrollmentOperationLog
from app.models.enums import CourseStatusEnum, EnrollmentOperationTypeEnum
from app.models.student import Student
from app.models.teacher import Teacher
from app.services.course_schedule_service import format_schedule_brief, schedules_conflict


def get_student_by_user_id(db: Session, user_id: int) -> Student:
    stmt = (
        select(Student)
        .options(joinedload(Student.user), joinedload(Student.department))
        .where(Student.user_id == user_id)
    )
    student = db.scalar(stmt)
    if not student:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="学生信息不存在")
    return student


def get_student_by_id(db: Session, student_id: int) -> Student:
    stmt = (
        select(Student)
        .options(joinedload(Student.user), joinedload(Student.department))
        .where(Student.id == student_id)
    )
    student = db.scalar(stmt)
    if not student:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="学生不存在")
    return student


def _get_course_for_enrollment(db: Session, course_id: int) -> Course:
    stmt = (
        select(Course)
        .options(joinedload(Course.teacher).joinedload(Teacher.user), joinedload(Course.department), selectinload(Course.schedules))
        .where(Course.id == course_id)
    )
    course = db.scalar(stmt)
    if not course:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="课程不存在")
    return course


def _create_operation_log(
    db: Session,
    student_id: int,
    course_id: int,
    operator_user_id: int,
    operation_type: EnrollmentOperationTypeEnum,
    reason: str | None = None,
):
    db.add(
        EnrollmentOperationLog(
            student_id=student_id,
            course_id=course_id,
            operator_user_id=operator_user_id,
            operation_type=operation_type,
            reason=reason,
        )
    )


def _ensure_no_schedule_conflict(db: Session, student_id: int, course: Course):
    if not course.schedules:
        return

    stmt = (
        select(Enrollment)
        .options(
            joinedload(Enrollment.course).joinedload(Course.teacher).joinedload(Teacher.user),
            joinedload(Enrollment.course).selectinload(Course.schedules),
        )
        .where(Enrollment.student_id == student_id, Enrollment.course_id != course.id)
    )
    current_enrollments = db.scalars(stmt).unique().all()

    for enrollment in current_enrollments:
        current_course = enrollment.course
        if current_course.term != course.term or not current_course.schedules:
            continue

        for target_schedule in course.schedules:
            for current_schedule in current_course.schedules:
                if schedules_conflict(target_schedule, current_schedule):
                    teacher_name = (
                        current_course.teacher.user.real_name
                        if current_course.teacher and current_course.teacher.user
                        else "-"
                    )
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail=(
                            f"课程时间冲突：与《{current_course.name}》"
                            f"（教师：{teacher_name}）的 {format_schedule_brief(current_schedule)} 冲突"
                        ),
                    )


def create_enrollment(
    db: Session,
    student_id: int,
    course_id: int,
    operator_user_id: int,
    operation_type: EnrollmentOperationTypeEnum,
    reason: str | None = None,
) -> dict:
    student = get_student_by_id(db, student_id)
    course = _get_course_for_enrollment(db, course_id)

    if course.status != CourseStatusEnum.open:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="当前课程未开放选课")

    exists = db.scalar(select(Enrollment.id).where(Enrollment.student_id == student.id, Enrollment.course_id == course_id))
    if exists:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="不能重复选课")

    selected_count = db.scalar(select(func.count(Enrollment.id)).where(Enrollment.course_id == course_id)) or 0
    if selected_count >= course.capacity:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="课程容量已满")

    _ensure_no_schedule_conflict(db, student.id, course)

    enrollment = Enrollment(student_id=student.id, course_id=course_id)
    db.add(enrollment)
    _create_operation_log(db, student.id, course_id, operator_user_id, operation_type, reason)
    db.commit()
    db.refresh(enrollment)
    return {"enrollment_id": enrollment.id, "course_id": course_id, "student_id": student.id}


def remove_enrollment(
    db: Session,
    student_id: int,
    course_id: int,
    operator_user_id: int,
    operation_type: EnrollmentOperationTypeEnum,
    reason: str | None = None,
) -> dict:
    student = get_student_by_id(db, student_id)
    enrollment = db.scalar(select(Enrollment).where(Enrollment.student_id == student.id, Enrollment.course_id == course_id))
    if not enrollment:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="未找到选课记录")
    if enrollment.score is not None:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="成绩已录入的课程不允许退课")

    db.delete(enrollment)
    _create_operation_log(db, student.id, course_id, operator_user_id, operation_type, reason)
    db.commit()
    return {"course_id": course_id, "student_id": student.id}


def enroll_course_for_student_user(db: Session, user_id: int, course_id: int) -> dict:
    student = get_student_by_user_id(db, user_id)
    return create_enrollment(db, student.id, course_id, user_id, EnrollmentOperationTypeEnum.student_select)


def drop_course_for_student_user(db: Session, user_id: int, course_id: int) -> dict:
    student = get_student_by_user_id(db, user_id)
    return remove_enrollment(db, student.id, course_id, user_id, EnrollmentOperationTypeEnum.student_drop)


def assign_course_by_admin(db: Session, operator_user_id: int, student_id: int, course_id: int) -> dict:
    return create_enrollment(db, student_id, course_id, operator_user_id, EnrollmentOperationTypeEnum.admin_assign)


def drop_course_by_admin(db: Session, operator_user_id: int, student_id: int, course_id: int) -> dict:
    return remove_enrollment(db, student_id, course_id, operator_user_id, EnrollmentOperationTypeEnum.admin_drop)
