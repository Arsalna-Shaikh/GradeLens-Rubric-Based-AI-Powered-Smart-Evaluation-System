from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session, joinedload
from app.db import get_db
from app.deps import require_role
from app.models.user import User
from app.models.submission import Submission
from app.models.assignment import Assignment
from app.models.answer import Answer
from app.schemas.review import ReviewSubmission, AnswerEdit, ReleaseOut

router = APIRouter(prefix="/review", tags=["teacher review"])
Teacher = Annotated[User, Depends(require_role("teacher"))]


def owned(submission_id: int, current: User, db: Session):
    item = (db.query(Submission).join(Assignment)
        .filter(Submission.id == submission_id, Assignment.class_.has(teacher_id=current.id))
        .options(joinedload(Submission.answers)).first())
    if not item: raise HTTPException(404, "Submission not found")
    return item

@router.get("/submissions/{submission_id}", response_model=ReviewSubmission)
def get_review(submission_id: int, current: Teacher, db: Annotated[Session, Depends(get_db)]):
    return owned(submission_id, current, db)

@router.patch("/submissions/{submission_id}/answers/{answer_id}", response_model=ReviewSubmission)
def edit_answer(submission_id: int, answer_id: int, payload: AnswerEdit, current: Teacher, db: Annotated[Session, Depends(get_db)]):
    item = owned(submission_id, current, db)
    answer = next((a for a in item.answers if a.id == answer_id), None)
    if not answer: raise HTTPException(404, "Answer not found")
    if payload.teacher_score is not None: answer.teacher_score = payload.teacher_score
    if payload.teacher_feedback is not None: answer.teacher_feedback = payload.teacher_feedback
    db.commit(); db.refresh(item)
    return item

@router.patch("/submissions/{submission_id}/approve", response_model=ReleaseOut)
def approve_alias(submission_id: int, current: Teacher, db: Annotated[Session, Depends(get_db)]):
    return release(submission_id, current, db)

@router.post("/submissions/{submission_id}/release", response_model=ReleaseOut)
def release(submission_id: int, current: Teacher, db: Annotated[Session, Depends(get_db)]):
    item = owned(submission_id, current, db)
    if item.status == "released":
        raise HTTPException(409, "Submission is already released")
    if item.status == "released":
        raise HTTPException(409, "Submission is already released")
    if not item.answers:
        raise HTTPException(400, "Submission has no answers")
    for answer in item.answers:
        question = answer.question
        if answer.teacher_score is not None and not 0 <= answer.teacher_score <= question.marks:
            raise HTTPException(422, f"Score for question {question.id} is out of range")
        if answer.needs_manual and answer.teacher_score is None:
            raise HTTPException(400, "Answers flagged for manual grading require a teacher score")
        if answer.teacher_score is None and answer.ai_score is None:
            raise HTTPException(400, "Every answer needs a teacher score or valid AI draft")
        answer.is_approved = True
    item.status = "released"; item.released_by = current.id
    from datetime import datetime, timezone
    item.released_at = datetime.now(timezone.utc)
    db.commit()
    return {"submission_id": item.id, "status": item.status, "released": True}
