from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.deps import require_roles
from app.core.response import success
from app.models.enums import RoleEnum
from app.schemas.student import StudentProfileUpdate
from app.services.student_service import (
    drop_course,
    enroll_course,
    get_student_profile,
    list_student_courses,
    list_student_grades,
    update_student_profile,
)

router = APIRouter(dependencies=[Depends(require_roles(RoleEnum.student))])


@router.get("/me/profile", summary="获取学生个人信息")
def student_profile(current_user=Depends(require_roles(RoleEnum.student)), db: Session = Depends(get_db)):
    return success(get_student_profile(db, current_user.id), "获取成功")


@router.put("/me/profile", summary="更新学生个人信息")
def update_profile(
    payload: StudentProfileUpdate,
    current_user=Depends(require_roles(RoleEnum.student)),
    db: Session = Depends(get_db),
):
    return success(update_student_profile(db, current_user.id, payload), "更新成功")


@router.get("/courses", summary="获取学生已选课程")
def my_courses(current_user=Depends(require_roles(RoleEnum.student)), db: Session = Depends(get_db)):
    return success(list_student_courses(db, current_user.id), "获取成功")


@router.post("/courses/{course_id}/enroll", summary="学生选课")
def course_enroll(course_id: int, current_user=Depends(require_roles(RoleEnum.student)), db: Session = Depends(get_db)):
    return success(enroll_course(db, current_user.id, course_id), "选课成功")


@router.delete("/courses/{course_id}/enroll", summary="学生退课")
def course_drop(course_id: int, current_user=Depends(require_roles(RoleEnum.student)), db: Session = Depends(get_db)):
    return success(drop_course(db, current_user.id, course_id), "退课成功")


@router.get("/grades", summary="学生成绩查询")
def my_grades(current_user=Depends(require_roles(RoleEnum.student)), db: Session = Depends(get_db)):
    return success(list_student_grades(db, current_user.id), "获取成功")
