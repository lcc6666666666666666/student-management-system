from enum import Enum


class RoleEnum(str, Enum):
    student = "student"
    teacher = "teacher"
    admin = "admin"


class CourseStatusEnum(str, Enum):
    open = "open"
    closed = "closed"


class EnrollmentOperationTypeEnum(str, Enum):
    student_select = "student_select"
    student_drop = "student_drop"
    admin_assign = "admin_assign"
    admin_drop = "admin_drop"
