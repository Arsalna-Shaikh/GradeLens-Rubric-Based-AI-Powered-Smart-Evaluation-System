from typing import Any
from pydantic import BaseModel, ConfigDict

class AnswerOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    question_id: int
    extracted_text: str | None = None
    ai_score: int | None = None
    ai_feedback: str | None = None
    ai_strengths: list[Any] | None = None
    ai_lackings: list[Any] | None = None
    ai_suggestions: list[Any] | None = None
    status: str

class GradingOut(BaseModel):
    submission_id: int
    total_score: int
    answers: list[AnswerOut]
