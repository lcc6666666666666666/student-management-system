from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.deps import get_current_user
from app.core.response import success
from app.services.course_service import get_course_detail, list_courses

router = APIRouter()


@router.get("", summary="课程列表")
def course_list(
    keyword: str | None = Query(default=None, description="课程名称/编号关键字"),
    status: str | None = Query(default=None, description="课程状态"),
    term: str | None = Query(default=None, description="学期"),
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=10, ge=1, le=100),
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db),
):
    data = list_courses(
        db=db,
        page=page,
        page_size=page_size,
        keyword=keyword,
        status=status,
        term=term,
        current_user=current_user,
    )
    return success(data, "获取成功")


@router.get("/{course_id}", summary="课程详情")
def course_detail(course_id: int, current_user=Depends(get_current_user), db: Session = Depends(get_db)):
    return success(get_course_detail(db, course_id, current_user), "获取成功")
