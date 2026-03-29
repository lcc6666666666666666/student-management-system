from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.security import get_password_hash
from app.models.admin import Admin
from app.models.course import Course
from app.models.course_schedule import CourseSchedule
from app.models.department import Department
from app.models.enrollment import Enrollment
from app.models.enums import CourseStatusEnum, RoleEnum
from app.models.student import Student
from app.models.teacher import Teacher
from app.models.user import User


def init_demo_data(db: Session):
    if db.scalar(select(User.id).limit(1)):
        return

    departments = [
        Department(name="计算机学院", code="CS", description="负责软件、数据与人工智能方向教学"),
        Department(name="数学学院", code="MATH", description="负责数学建模与分析课程"),
        Department(name="管理学院", code="MGMT", description="负责管理类通识课程"),
    ]
    db.add_all(departments)
    db.flush()

    users = [
        User(username="student01", password_hash=get_password_hash("123456"), role=RoleEnum.student, real_name="张明", phone="13800000001", email="student01@example.com"),
        User(username="student02", password_hash=get_password_hash("123456"), role=RoleEnum.student, real_name="李华", phone="13800000002", email="student02@example.com"),
        User(username="student03", password_hash=get_password_hash("123456"), role=RoleEnum.student, real_name="王蕾", phone="13800000003", email="student03@example.com"),
        User(username="teacher01", password_hash=get_password_hash("123456"), role=RoleEnum.teacher, real_name="陈老师", phone="13900000001", email="teacher01@example.com"),
        User(username="teacher02", password_hash=get_password_hash("123456"), role=RoleEnum.teacher, real_name="刘老师", phone="13900000002", email="teacher02@example.com"),
        User(username="admin01", password_hash=get_password_hash("123456"), role=RoleEnum.admin, real_name="系统管理员", phone="13700000001", email="admin01@example.com"),
    ]
    db.add_all(users)
    db.flush()

    students = [
        Student(user_id=users[0].id, student_no="S2023001", department_id=departments[0].id, gender="男", grade="2023级", class_name="计科1班", admission_year=2023),
        Student(user_id=users[1].id, student_no="S2023002", department_id=departments[0].id, gender="女", grade="2023级", class_name="计科2班", admission_year=2023),
        Student(user_id=users[2].id, student_no="S2023003", department_id=departments[1].id, gender="女", grade="2023级", class_name="数科1班", admission_year=2023),
    ]
    teachers = [
        Teacher(user_id=users[3].id, teacher_no="T2020001", department_id=departments[0].id, title="副教授", office="信息楼 A-308"),
        Teacher(user_id=users[4].id, teacher_no="T2020002", department_id=departments[1].id, title="讲师", office="理科楼 B-512"),
    ]
    admin = Admin(user_id=users[5].id, admin_no="A0001", level="super")
    db.add_all(students + teachers + [admin])
    db.flush()

    courses = [
        Course(course_code="DB101", name="数据库系统原理", credit=3.5, hours=48, capacity=60, term="2025-2026-2", status=CourseStatusEnum.open, description="面向数据库课程设计的核心课程，涵盖 SQL、事务与范式设计。", teacher_id=teachers[0].id, department_id=departments[0].id),
        Course(course_code="SE202", name="软件工程", credit=3.0, hours=40, capacity=45, term="2025-2026-2", status=CourseStatusEnum.open, description="面向项目开发流程、需求分析与系统设计。", teacher_id=teachers[0].id, department_id=departments[0].id),
        Course(course_code="NW301", name="计算机网络", credit=3.0, hours=40, capacity=50, term="2025-2026-2", status=CourseStatusEnum.closed, description="课程已关闭选课，用于演示状态控制。", teacher_id=teachers[0].id, department_id=departments[0].id),
        Course(course_code="MA103", name="高等数学实践", credit=4.0, hours=56, capacity=80, term="2025-2026-2", status=CourseStatusEnum.open, description="通过建模案例训练数学分析能力。", teacher_id=teachers[1].id, department_id=departments[1].id),
        Course(course_code="DA204", name="数据分析基础", credit=2.5, hours=32, capacity=55, term="2025-2026-2", status=CourseStatusEnum.open, description="面向统计分析与可视化展示的基础课程。", teacher_id=teachers[1].id, department_id=departments[1].id),
    ]
    db.add_all(courses)
    db.flush()

    schedules = [
        CourseSchedule(course_id=courses[0].id, weekday=1, start_section=1, end_section=2, start_week=1, end_week=16, location="博学楼 A101"),
        CourseSchedule(course_id=courses[0].id, weekday=3, start_section=3, end_section=4, start_week=1, end_week=16, location="博学楼 A101"),
        CourseSchedule(course_id=courses[1].id, weekday=1, start_section=3, end_section=4, start_week=1, end_week=16, location="博学楼 A202"),
        CourseSchedule(course_id=courses[2].id, weekday=2, start_section=1, end_section=2, start_week=1, end_week=16, location="网络实验室 1"),
        CourseSchedule(course_id=courses[3].id, weekday=3, start_section=1, end_section=2, start_week=1, end_week=16, location="理学楼 B301"),
        CourseSchedule(course_id=courses[4].id, weekday=1, start_section=1, end_section=2, start_week=1, end_week=16, location="理学楼 B402"),
    ]
    db.add_all(schedules)

    enrollments = [
        Enrollment(student_id=students[0].id, course_id=courses[0].id, score=92),
        Enrollment(student_id=students[0].id, course_id=courses[1].id, score=None),
        Enrollment(student_id=students[1].id, course_id=courses[0].id, score=86),
        Enrollment(student_id=students[1].id, course_id=courses[3].id, score=90),
        Enrollment(student_id=students[2].id, course_id=courses[1].id, score=78),
        Enrollment(student_id=students[2].id, course_id=courses[4].id, score=None),
    ]
    db.add_all(enrollments)
    db.flush()
    db.commit()
