from pydantic import BaseModel, EmailStr, Field


class TeacherProfileUpdate(BaseModel):
    real_name: str = Field(..., min_length=2, max_length=50)
    phone: str | None = Field(default=None, max_length=20)
    email: EmailStr | None = None
    title: str | None = Field(default=None, max_length=30)
    office: str | None = Field(default=None, max_length=50)


class ScoreUpdateRequest(BaseModel):
    score: float | None = Field(default=None, ge=0, le=100)
