from sqlalchemy import select
from sqlalchemy.orm import Session, joinedload

from app.core.security import create_access_token, verify_password
from app.models.enums import RoleEnum
from app.models.user import User


def authenticate_user(db: Session, username: str, password: str) -> User | None:
    stmt = (
        select(User)
        .options(joinedload(User.student), joinedload(User.teacher), joinedload(User.admin))
        .where(User.username == username, User.is_active.is_(True))
    )
    user = db.scalar(stmt)
    if not user or not verify_password(password, user.password_hash):
        return None
    return user


def build_current_user_payload(db: Session, user: User) -> dict:
    base = {
        "id": user.id,
        "username": user.username,
        "role": user.role.value,
        "real_name": user.real_name,
        "phone": user.phone,
        "email": user.email,
    }
    if user.role == RoleEnum.student and user.student:
        base["profile"] = {"student_id": user.student.id, "student_no": user.student.student_no}
    elif user.role == RoleEnum.teacher and user.teacher:
        base["profile"] = {"teacher_id": user.teacher.id, "teacher_no": user.teacher.teacher_no}
    elif user.role == RoleEnum.admin and user.admin:
        base["profile"] = {"admin_id": user.admin.id, "admin_no": user.admin.admin_no}
    else:
        base["profile"] = None
    return base


def issue_token(user: User) -> dict:
    return create_access_token(str(user.id), user.role.value)
