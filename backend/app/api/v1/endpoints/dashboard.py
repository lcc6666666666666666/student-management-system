from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.deps import get_current_user
from app.core.response import success
from app.services.dashboard_service import get_dashboard_overview

router = APIRouter()


@router.get("/overview", summary="获取仪表盘概览")
def dashboard_overview(current_user=Depends(get_current_user), db: Session = Depends(get_db)):
    return success(get_dashboard_overview(db, current_user), "获取成功")
