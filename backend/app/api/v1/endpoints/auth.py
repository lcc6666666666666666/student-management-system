from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.deps import get_current_user
from app.core.response import success
from app.schemas.auth import LoginRequest
from app.services.auth_service import authenticate_user, build_current_user_payload, issue_token

router = APIRouter()


@router.post("/login", summary="账号登录")
def login(payload: LoginRequest, db: Session = Depends(get_db)):
    user = authenticate_user(db, payload.username, payload.password)
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="用户名或密码错误")
    token = issue_token(user)
    user_data = build_current_user_payload(db, user)
    return success(
        {
            "access_token": token["access_token"],
            "token_type": "Bearer",
            "expires_in": token["expires_in"],
            "user": user_data,
        },
        "登录成功",
    )


@router.get("/me", summary="获取当前登录用户")
def get_me(current_user=Depends(get_current_user), db: Session = Depends(get_db)):
    return success(build_current_user_payload(db, current_user), "获取成功")
