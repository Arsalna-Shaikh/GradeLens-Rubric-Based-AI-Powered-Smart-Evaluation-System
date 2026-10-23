from pydantic import BaseModel

class ReviewAnswer(BaseModel):
    id: int
    question_id: int
    extracted_text: str | None = None
    ai_score: int | None = None
    ai_feedback: str | None = None
    teacher_score: int | None = None
    teacher_feedback: str | None = None
    is_approved: bool

class ReviewSubmission(BaseModel):
    id: int
    assignment_id: int
    student_id: int
    status: str
    released_at: object | None = None
    answers: list[ReviewAnswer]

class AnswerEdit(BaseModel):
    teacher_score: int | None = None
    teacher_feedback: str | None = None

class ReleaseOut(BaseModel):
    submission_id: int
    status: str
    released: bool
