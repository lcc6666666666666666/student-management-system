from enum import Enum


class RoleEnum(str, Enum):
    student = "student"
    teacher = "teacher"
    admin = "admin"


class CourseStatusEnum(str, Enum):
    open = "open"
    closed = "closed"
