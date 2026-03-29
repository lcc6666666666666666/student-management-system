from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session, joinedload

from app.models.course import Course
from app.models.course_schedule import CourseSchedule
from app.schemas.course import CourseScheduleCreate, CourseScheduleUpdate

WEEKDAY_LABELS = {
    1: "周一",
    2: "周二",
    3: "周三",
    4: "周四",
    5: "周五",
    6: "周六",
    7: "周日",
}


def get_weekday_label(weekday: int) -> str:
    return WEEKDAY_LABELS.get(weekday, f"周{weekday}")


def _get_schedule_value(schedule, field_name: str):
    if isinstance(schedule, dict):
        return schedule[field_name]
    return getattr(schedule, field_name)


def schedules_conflict(left, right) -> bool:
    if _get_schedule_value(left, "weekday") != _get_schedule_value(right, "weekday"):
        return False

    section_overlap = max(_get_schedule_value(left, "start_section"), _get_schedule_value(right, "start_section")) <= min(
        _get_schedule_value(left, "end_section"), _get_schedule_value(right, "end_section")
    )
    week_overlap = max(_get_schedule_value(left, "start_week"), _get_schedule_value(right, "start_week")) <= min(
        _get_schedule_value(left, "end_week"), _get_schedule_value(right, "end_week")
    )
    return section_overlap and week_overlap


def format_schedule_brief(schedule) -> str:
    weekday = _get_schedule_value(schedule, "weekday")
    start_section = _get_schedule_value(schedule, "start_section")
    end_section = _get_schedule_value(schedule, "end_section")
    start_week = _get_schedule_value(schedule, "start_week")
    end_week = _get_schedule_value(schedule, "end_week")
    location = _get_schedule_value(schedule, "location")
    return f"{get_weekday_label(weekday)} 第{start_section}-{end_section}节 第{start_week}-{end_week}周 @{location}"


def serialize_course_schedule(schedule: CourseSchedule) -> dict:
    return {
        "id": schedule.id,
        "course_id": schedule.course_id,
        "weekday": schedule.weekday,
        "weekday_label": get_weekday_label(schedule.weekday),
        "start_section": schedule.start_section,
        "end_section": schedule.end_section,
        "start_week": schedule.start_week,
        "end_week": schedule.end_week,
        "location": schedule.location,
        "display_text": format_schedule_brief(schedule),
        "created_at": schedule.created_at,
        "updated_at": schedule.updated_at,
    }


def serialize_course_schedules(schedules: list[CourseSchedule]) -> list[dict]:
    ordered = sorted(schedules, key=lambda item: (item.weekday, item.start_section, item.start_week, item.id))
    return [serialize_course_schedule(schedule) for schedule in ordered]


def _ensure_course_exists(db: Session, course_id: int) -> Course:
    stmt = select(Course).options(joinedload(Course.teacher), joinedload(Course.department)).where(Course.id == course_id)
    course = db.scalar(stmt)
    if not course:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="课程不存在")
    return course


def _build_schedule_payload(payload: CourseScheduleCreate | CourseScheduleUpdate, course_id: int) -> dict:
    return {
        "course_id": course_id,
        "weekday": payload.weekday,
        "start_section": payload.start_section,
        "end_section": payload.end_section,
        "start_week": payload.start_week,
        "end_week": payload.end_week,
        "location": payload.location.strip(),
    }


def _validate_schedule_overlap(
    db: Session,
    course_id: int,
    payload: CourseScheduleCreate | CourseScheduleUpdate,
    exclude_schedule_id: int | None = None,
):
    stmt = select(CourseSchedule).where(CourseSchedule.course_id == course_id)
    if exclude_schedule_id is not None:
        stmt = stmt.where(CourseSchedule.id != exclude_schedule_id)

    current_schedules = db.scalars(stmt).all()
    schedule_data = _build_schedule_payload(payload, course_id)
    for current in current_schedules:
        if schedules_conflict(current, schedule_data):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"课程时间安排冲突：与现有安排 {format_schedule_brief(current)} 重叠",
            )


def list_course_schedules(db: Session, course_id: int) -> dict:
    course = _ensure_course_exists(db, course_id)
    schedules = db.scalars(select(CourseSchedule).where(CourseSchedule.course_id == course_id)).all()
    return {
        "course": {
            "id": course.id,
            "course_code": course.course_code,
            "name": course.name,
            "term": course.term,
        },
        "items": serialize_course_schedules(schedules),
    }


def create_course_schedule(db: Session, course_id: int, payload: CourseScheduleCreate) -> dict:
    _ensure_course_exists(db, course_id)
    _validate_schedule_overlap(db, course_id, payload)

    schedule = CourseSchedule(**_build_schedule_payload(payload, course_id))
    db.add(schedule)
    db.commit()
    db.refresh(schedule)
    return serialize_course_schedule(schedule)


def update_course_schedule(db: Session, schedule_id: int, payload: CourseScheduleUpdate) -> dict:
    schedule = db.scalar(select(CourseSchedule).where(CourseSchedule.id == schedule_id))
    if not schedule:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="课程时间安排不存在")

    _validate_schedule_overlap(db, schedule.course_id, payload, exclude_schedule_id=schedule_id)

    schedule.weekday = payload.weekday
    schedule.start_section = payload.start_section
    schedule.end_section = payload.end_section
    schedule.start_week = payload.start_week
    schedule.end_week = payload.end_week
    schedule.location = payload.location.strip()
    db.commit()
    db.refresh(schedule)
    return serialize_course_schedule(schedule)


def delete_course_schedule(db: Session, schedule_id: int) -> dict:
    schedule = db.scalar(select(CourseSchedule).where(CourseSchedule.id == schedule_id))
    if not schedule:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="课程时间安排不存在")

    course_id = schedule.course_id
    db.delete(schedule)
    db.commit()
    return {"id": schedule_id, "course_id": course_id}
