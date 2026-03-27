from sqlalchemy import ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class Teacher(Base):
    __tablename__ = "teacher"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("sys_user.id"), unique=True, nullable=False)
    teacher_no: Mapped[str] = mapped_column(String(20), unique=True, index=True, nullable=False)
    department_id: Mapped[int | None] = mapped_column(ForeignKey("department.id"))
    title: Mapped[str | None] = mapped_column(String(30))
    office: Mapped[str | None] = mapped_column(String(50))

    user = relationship("User", back_populates="teacher")
    department = relationship("Department", back_populates="teachers")
    courses = relationship("Course", back_populates="teacher")
