from decimal import Decimal

from pydantic import BaseModel, Field, model_validator


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


class CourseScheduleBase(BaseModel):
    weekday: int = Field(..., ge=1, le=7)
    start_section: int = Field(..., ge=1, le=20)
    end_section: int = Field(..., ge=1, le=20)
    start_week: int = Field(..., ge=1, le=30)
    end_week: int = Field(..., ge=1, le=30)
    location: str = Field(..., min_length=1, max_length=100)

    @model_validator(mode="after")
    def validate_ranges(self):
        if self.start_section > self.end_section:
            raise ValueError("开始节次不能大于结束节次")
        if self.start_week > self.end_week:
            raise ValueError("起始周不能大于结束周")
        return self


class CourseScheduleCreate(CourseScheduleBase):
    pass


class CourseScheduleUpdate(CourseScheduleBase):
    pass
