from sqlalchemy import ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class Student(Base):
    __tablename__ = "student"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("sys_user.id"), unique=True, nullable=False)
    student_no: Mapped[str] = mapped_column(String(20), unique=True, index=True, nullable=False)
    department_id: Mapped[int | None] = mapped_column(ForeignKey("department.id"))
    gender: Mapped[str | None] = mapped_column(String(10))
    grade: Mapped[str | None] = mapped_column(String(20))
    class_name: Mapped[str | None] = mapped_column(String(50))
    admission_year: Mapped[int | None] = mapped_column(Integer)

    user = relationship("User", back_populates="student")
    department = relationship("Department", back_populates="students")
    enrollments = relationship("Enrollment", back_populates="student", cascade="all, delete-orphan")
