from decimal import Decimal

from pydantic import BaseModel, Field


class CourseBase(BaseModel):
    course_code: str = Field(..., min_length=2, max_length=20)
    name: str = Field(..., min_length=2, max_length=100)
    credit: Decimal = Field(..., ge=0.5, le=10)
    hours: int = Field(..., ge=8, le=200)
    capacity: int = Field(..., ge=1, le=500)
    term: str = Field(..., min_length=4, max_length=30)
    status: str = Field(..., pattern="^(open|closed)$")
    description: str | None = Field(default=None, max_length=2000)
    teacher_id: int = Field(..., ge=1)
    department_id: int | None = Field(default=None, ge=1)


class CourseCreate(CourseBase):
    pass


class CourseUpdate(CourseBase):
    pass
