from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.db import get_db
from app.deps import require_role
from app.models.user import User
from app.models.submission import Submission
from app.models.answer import Answer
from app.models.question import Question
from app.models.assignment import Assignment
from app.services.grading_service import evaluate_written, grade_submission
from app.schemas.grading import GradingOut, AnswerOut

router = APIRouter(prefix="/grading", tags=["grading"])
Teacher = Annotated[User, Depends(require_role("teacher"))]

@router.post("/submissions/{submission_id}", response_model=GradingOut)
async def grade_submission_route(submission_id: int, current: Teacher, db: Annotated[Session, Depends(get_db)]):
    submission = db.query(Submission).join(Assignment).filter(Submission.id == submission_id, Assignment.class_.has(teacher_id=current.id)).first()
    if not submission: raise HTTPException(404, "Submission not found")
    questions = db.query(Question).filter(Question.assignment_id == submission.assignment_id).order_by(Question.id).all()
    answers = []
    # Typed submissions use one line per question (a practical deterministic MVP format).
    lines = (submission.content_text or "").splitlines()
    for index, question in enumerate(questions):
        text = lines[index].strip() if index < len(lines) else ""
        item = db.query(Answer).filter_by(submission_id=submission.id, question_id=question.id).first() or Answer(submission_id=submission.id, question_id=question.id)
        item.extracted_text = text
        item.is_approved = False
        if question.type == "mcq":
            normalized = text.strip().casefold().strip(".()[]")
            expected = (question.correct_answer or "").strip().casefold().strip(".()[]")
            if normalized.startswith("option "): normalized = normalized[-1:]
            item.ai_score = question.marks if normalized == expected else 0
            item.ai_feedback = "Correct answer." if item.ai_score else "Answer does not match the configured correct answer."
            item.ai_strengths, item.ai_lackings, item.ai_suggestions = [], [], []
        else:
            try:
                result = await evaluate_written(question, text)
                item.ai_score = result["score"]; item.ai_feedback = result["justification"]
                item.ai_strengths = result["strengths"]; item.ai_lackings = result["lackings"]; item.ai_suggestions = result["suggestions"]
            except Exception as exc:
                item.ai_feedback = f"Manual grading required: {exc}"; item.ai_score = None
        db.add(item); answers.append(item)
    db.flush()
    submission.status = "graded_draft"; db.commit()
    for item in answers: db.refresh(item)
    total = sum(a.ai_score or 0 for a in answers)
    return {"submission_id": submission.id, "total_score": total, "answers":[{**AnswerOut.model_validate(a).model_dump(), "status": "draft"} for a in answers]}
