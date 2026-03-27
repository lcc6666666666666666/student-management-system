from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException, Request
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.api.v1.api import api_router
from app.core.config import settings
from app.core.database import Base, SessionLocal, engine
from app.services.init_data import init_demo_data


@asynccontextmanager
async def lifespan(_: FastAPI):
    Base.metadata.create_all(bind=engine)
    if settings.init_demo_data:
        with SessionLocal() as db:
            init_demo_data(db)
    yield


app = FastAPI(
    title=settings.app_name,
    version="1.0.0",
    lifespan=lifespan,
    description="教学管理系统课程设计后端，提供学生、教师、管理员三类角色接口。",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.exception_handler(HTTPException)
async def http_exception_handler(_: Request, exc: HTTPException):
    return JSONResponse(status_code=exc.status_code, content={"code": exc.status_code, "message": exc.detail, "data": None})


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(_: Request, exc: RequestValidationError):
    errors = []
    for error in exc.errors():
        location = " -> ".join(str(item) for item in error.get("loc", []))
        errors.append(f"{location}: {error.get('msg')}")
    return JSONResponse(status_code=422, content={"code": 422, "message": "请求参数校验失败", "data": errors})


@app.exception_handler(Exception)
async def common_exception_handler(_: Request, exc: Exception):
    return JSONResponse(status_code=500, content={"code": 500, "message": f"服务器内部错误: {exc}", "data": None})


@app.get("/", summary="健康检查")
def root():
    return {"code": 0, "message": "教学管理系统后端运行中", "data": {"docs": "/docs"}}


app.include_router(api_router, prefix=settings.api_v1_prefix)
