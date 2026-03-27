from pydantic import BaseModel, EmailStr, Field


class StudentProfileUpdate(BaseModel):
    real_name: str = Field(..., min_length=2, max_length=50)
    phone: str | None = Field(default=None, max_length=20)
    email: EmailStr | None = None
    gender: str | None = Field(default=None, max_length=10)
    grade: str | None = Field(default=None, max_length=20)
    class_name: str | None = Field(default=None, max_length=50)
