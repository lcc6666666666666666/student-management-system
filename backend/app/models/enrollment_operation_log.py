from sqlalchemy import DateTime, Enum as SqlEnum, ForeignKey, String, func
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base
from app.models.enums import EnrollmentOperationTypeEnum


class EnrollmentOperationLog(Base):
    __tablename__ = "enrollment_operation_log"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    student_id: Mapped[int] = mapped_column(ForeignKey("student.id"), nullable=False, index=True)
    course_id: Mapped[int] = mapped_column(ForeignKey("course.id"), nullable=False, index=True)
    operator_user_id: Mapped[int] = mapped_column(ForeignKey("sys_user.id"), nullable=False, index=True)
    operation_type: Mapped[EnrollmentOperationTypeEnum] = mapped_column(SqlEnum(EnrollmentOperationTypeEnum), nullable=False)
    reason: Mapped[str | None] = mapped_column(String(255))
    created_at: Mapped[DateTime] = mapped_column(DateTime, server_default=func.now(), nullable=False)
