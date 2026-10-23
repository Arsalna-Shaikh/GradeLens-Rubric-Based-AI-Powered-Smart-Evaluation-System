from pydantic import BaseModel

class TopicAnalytics(BaseModel):
    topic: str
    question_count: int
    response_count: int
    average_score: float
    max_marks: int
    mastery_percent: float
    needs_instruction: bool

class MistakeItem(BaseModel):
    text: str
    count: int

class ClassAnalytics(BaseModel):
    class_id: int
    class_name: str
    subject: str
    submission_count: int
    released_submission_count: int
    average_score: float
    average_percent: float
    topics: list[TopicAnalytics]
    common_mistakes: list[MistakeItem]
