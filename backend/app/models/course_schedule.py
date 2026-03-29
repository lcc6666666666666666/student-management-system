from sqlalchemy import CheckConstraint, DateTime, ForeignKey, Integer, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class CourseSchedule(Base):
    __tablename__ = "course_schedule"
    __table_args__ = (
        CheckConstraint("weekday BETWEEN 1 AND 7", name="chk_course_schedule_weekday"),
        CheckConstraint("start_section BETWEEN 1 AND 20", name="chk_course_schedule_start_section"),
        CheckConstraint("end_section BETWEEN 1 AND 20", name="chk_course_schedule_end_section"),
        CheckConstraint("start_section <= end_section", name="chk_course_schedule_section_order"),
        CheckConstraint("start_week BETWEEN 1 AND 30", name="chk_course_schedule_start_week"),
        CheckConstraint("end_week BETWEEN 1 AND 30", name="chk_course_schedule_end_week"),
        CheckConstraint("start_week <= end_week", name="chk_course_schedule_week_order"),
    )

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    course_id: Mapped[int] = mapped_column(ForeignKey("course.id"), nullable=False, index=True)
    weekday: Mapped[int] = mapped_column(Integer, nullable=False)
    start_section: Mapped[int] = mapped_column(Integer, nullable=False)
    end_section: Mapped[int] = mapped_column(Integer, nullable=False)
    start_week: Mapped[int] = mapped_column(Integer, nullable=False)
    end_week: Mapped[int] = mapped_column(Integer, nullable=False)
    location: Mapped[str] = mapped_column(String(100), nullable=False)
    created_at: Mapped[DateTime] = mapped_column(DateTime, server_default=func.now(), nullable=False)
    updated_at: Mapped[DateTime] = mapped_column(DateTime, server_default=func.now(), onupdate=func.now(), nullable=False)

    course = relationship("Course", back_populates="schedules")
