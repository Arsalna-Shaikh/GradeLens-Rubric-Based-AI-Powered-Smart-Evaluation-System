from datetime import datetime
from pydantic import BaseModel, ConfigDict, Field, model_validator

class QuestionCreate(BaseModel):
    type: str = Field(pattern="^(mcq|written|short_answer)$")
    text: str = Field(min_length=1)
    marks: int = Field(ge=0)
    options: list[str] | None = None
    correct_answer: str | None = None
    rubric: str | None = None
    sample_answer: str | None = None

class QuestionOut(QuestionCreate):
    model_config = ConfigDict(from_attributes=True)
    id: int

class AssignmentCreate(BaseModel):
    title: str = Field(min_length=1, max_length=255)
    description: str | None = None
    deadline: datetime | None = None
    total_marks: int | None = Field(default=None, ge=1)
    pass_mark_percent: int = Field(default=50, ge=0, le=100)
    questions: list[QuestionCreate] = Field(default_factory=list)

    @model_validator(mode="after")
    def validate_questions(self):
        if not self.questions:
            raise ValueError("At least one question is required")
        if sum(q.marks for q in self.questions) != (self.total_marks if self.total_marks is not None else sum(q.marks for q in self.questions)):
            raise ValueError("Question marks must sum to total_marks")
        for q in self.questions:
            if q.type == "mcq" and (not q.options or len(q.options) != 4 or not q.correct_answer):
                raise ValueError("MCQ questions require four options and a correct answer")
            if q.type == "written" and not (q.rubric or q.sample_answer):
                raise ValueError("Written questions require a rubric or sample answer")
        return self

class StudentQuestionOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    type: str
    text: str
    marks: int
    options: list[str] | None = None

class StudentAssignmentOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    class_id: int
    title: str
    description: str | None
    total_marks: int
    pass_mark_percent: int = 50
    deadline: datetime | None
    questions: list[StudentQuestionOut] = []

class AssignmentOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    class_id: int
    title: str
    description: str | None
    total_marks: int
    pass_mark_percent: int = 50
    deadline: datetime | None
    questions: list[QuestionOut] = []
