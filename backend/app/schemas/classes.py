from datetime import datetime
from pydantic import BaseModel, ConfigDict, Field

class ClassCreate(BaseModel):
    name: str = Field(min_length=1, max_length=255)
    subject: str = Field(min_length=1, max_length=255)

class ClassUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=255)
    subject: str | None = Field(default=None, min_length=1, max_length=255)

class ClassOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    name: str
    subject: str
    join_code: str
    teacher_id: int
    created_at: datetime
    enrolled_count: int = 0
    invite_link: str | None = None

class EnrollRequest(BaseModel):
    join_code: str = Field(min_length=4, max_length=16)

class EnrollmentOut(BaseModel):
    id: int
    class_id: int
    student_id: int
    joined_at: datetime
    class_name: str
    subject: str
    join_code: str
