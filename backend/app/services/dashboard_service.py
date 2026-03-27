from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models.course import Course
from app.models.enrollment import Enrollment
from app.models.enums import RoleEnum
from app.models.student import Student
from app.models.teacher import Teacher
from app.models.user import User
from app.services.student_service import _get_student_by_user_id
from app.services.teacher_service import _get_teacher_by_user_id


def _admin_overview(db: Session) -> dict:
    total_courses = db.scalar(select(func.count(Course.id))) or 0
    total_students = db.scalar(select(func.count(Student.id))) or 0
    total_teachers = db.scalar(select(func.count(Teacher.id))) or 0
    total_enrollments = db.scalar(select(func.count(Enrollment.id))) or 0

    top_courses_rows = db.execute(
        select(Course.name, Course.course_code, func.count(Enrollment.id).label("selected_count"))
        .outerjoin(Enrollment, Enrollment.course_id == Course.id)
        .group_by(Course.id)
        .order_by(func.count(Enrollment.id).desc(), Course.created_at.desc())
        .limit(5)
    ).all()

    return {
        "role": RoleEnum.admin.value,
        "cards": [
            {"title": "课程总数", "value": int(total_courses), "desc": "当前系统课程数量", "theme": "primary"},
            {"title": "选课总数", "value": int(total_enrollments), "desc": "所有学生选课记录", "theme": "emerald"},
            {"title": "学生人数", "value": int(total_students), "desc": "已注册学生数量", "theme": "amber"},
            {"title": "教师人数", "value": int(total_teachers), "desc": "在编教师账号数量", "theme": "violet"},
        ],
        "highlights": [
            {"label": row[0], "value": int(row[2] or 0), "extra": row[1]} for row in top_courses_rows
        ],
        "announcements": [
            "管理员可在课程管理页执行增删改查。",
            "课程删除前会校验是否存在选课记录。",
            "仪表盘数据实时来源于数据库统计结果。",
        ],
    }


def _teacher_overview(db: Session, user: User) -> dict:
    teacher = _get_teacher_by_user_id(db, user.id)
    course_count = db.scalar(select(func.count(Course.id)).where(Course.teacher_id == teacher.id)) or 0
    student_count = db.scalar(
        select(func.count(Enrollment.id)).join(Course, Course.id == Enrollment.course_id).where(Course.teacher_id == teacher.id)
    ) or 0
    graded_count = db.scalar(
        select(func.count(Enrollment.id))
        .join(Course, Course.id == Enrollment.course_id)
        .where(Course.teacher_id == teacher.id, Enrollment.score.is_not(None))
    ) or 0
    avg_score = db.scalar(
        select(func.avg(Enrollment.score)).join(Course, Course.id == Enrollment.course_id).where(Course.teacher_id == teacher.id)
    )

    courses = db.execute(
        select(Course.name, Course.term, func.count(Enrollment.id), func.avg(Enrollment.score))
        .outerjoin(Enrollment, Enrollment.course_id == Course.id)
        .where(Course.teacher_id == teacher.id)
        .group_by(Course.id)
        .order_by(Course.created_at.desc())
        .limit(6)
    ).all()

    return {
        "role": RoleEnum.teacher.value,
        "cards": [
            {"title": "授课课程", "value": int(course_count), "desc": "当前承担课程数量", "theme": "primary"},
            {"title": "选课学生", "value": int(student_count), "desc": "课程总选课人数", "theme": "emerald"},
            {"title": "已录成绩", "value": int(graded_count), "desc": "已完成评分记录", "theme": "amber"},
            {"title": "平均成绩", "value": round(float(avg_score), 2) if avg_score is not None else "--", "desc": "教师名下课程均分", "theme": "violet"},
        ],
        "highlights": [
            {
                "label": row[0],
                "value": int(row[2] or 0),
                "extra": f"{row[1]} / 均分 {round(float(row[3]), 2) if row[3] is not None else '--'}",
            }
            for row in courses
        ],
        "announcements": [
            "进入成绩管理页可以直接录入与修改成绩。",
            "课程学生名单仅展示当前教师本人授课数据。",
            "成绩区间校验由前后端与数据库共同保证。",
        ],
    }


def _student_overview(db: Session, user: User) -> dict:
    student = _get_student_by_user_id(db, user.id)
    selected_count = db.scalar(select(func.count(Enrollment.id)).where(Enrollment.student_id == student.id)) or 0
    graded_count = db.scalar(
        select(func.count(Enrollment.id)).where(Enrollment.student_id == student.id, Enrollment.score.is_not(None))
    ) or 0
    avg_score = db.scalar(select(func.avg(Enrollment.score)).where(Enrollment.student_id == student.id))
    available_count = db.scalar(select(func.count(Course.id)).where(Course.status == "open")) or 0

    rows = db.execute(
        select(Course.name, Course.term, Enrollment.score)
        .join(Enrollment, Enrollment.course_id == Course.id)
        .where(Enrollment.student_id == student.id)
        .order_by(Enrollment.selected_at.desc())
        .limit(6)
    ).all()

    return {
        "role": RoleEnum.student.value,
        "cards": [
            {"title": "可选课程", "value": int(available_count), "desc": "当前开放课程数量", "theme": "primary"},
            {"title": "我的课程", "value": int(selected_count), "desc": "已选课程总数", "theme": "emerald"},
            {"title": "已出成绩", "value": int(graded_count), "desc": "已完成评分课程", "theme": "amber"},
            {"title": "平均成绩", "value": round(float(avg_score), 2) if avg_score is not None else "--", "desc": "已录入成绩均分", "theme": "violet"},
        ],
        "highlights": [
            {
                "label": row[0],
                "value": "--" if row[2] is None else round(float(row[2]), 2),
                "extra": row[1],
            }
            for row in rows
        ],
        "announcements": [
            "开放状态课程支持在线选课与退课。",
            "已录入成绩的课程会同步展示在成绩页。",
            "个人信息页支持维护手机号、邮箱与班级信息。",
        ],
    }


def get_dashboard_overview(db: Session, user: User) -> dict:
    if user.role == RoleEnum.admin:
        return _admin_overview(db)
    if user.role == RoleEnum.teacher:
        return _teacher_overview(db, user)
    return _student_overview(db, user)
