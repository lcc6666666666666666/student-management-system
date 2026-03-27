from sqlalchemy import ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class Admin(Base):
    __tablename__ = "admin"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("sys_user.id"), unique=True, nullable=False)
    admin_no: Mapped[str] = mapped_column(String(20), unique=True, index=True, nullable=False)
    level: Mapped[str] = mapped_column(String(20), default="super", nullable=False)

    user = relationship("User", back_populates="admin")
