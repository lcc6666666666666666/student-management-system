from pydantic import BaseModel, Field


class LoginRequest(BaseModel):
    username: str = Field(..., min_length=3, max_length=50, description="账号")
    password: str = Field(..., min_length=6, max_length=32, description="密码")
