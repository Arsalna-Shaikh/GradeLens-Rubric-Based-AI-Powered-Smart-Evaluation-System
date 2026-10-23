from collections import Counter, defaultdict
from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.db import get_db
from app.deps import require_role
from app.models.user import User
from app.models.class_ import Class
from app.models.assignment import Assignment
from app.models.submission import Submission
from app.models.answer import Answer
from app.models.question import Question
from app.schemas.analytics import ClassAnalytics

router = APIRouter(prefix="/analytics", tags=["analytics"])

# The canonical public endpoint is assignment-scoped; keep the existing
# class aggregate for backwards compatibility while enforcing the same owner guard.
Teacher = Annotated[User, Depends(require_role("teacher"))]

# Analytics intentionally aggregates released submissions only. Draft AI output
# never crosses this boundary.

@router.get("/classes/{class_id}", response_model=ClassAnalytics)
def class_analytics(class_id: int, current: Teacher, db: Annotated[Session, Depends(get_db)]):
    classroom = db.query(Class).filter_by(id=class_id, teacher_id=current.id).first()
    if not classroom:
        raise HTTPException(404, "Class not found")
    assignments = db.query(Assignment).filter_by(class_id=class_id).all()
    assignment_ids = [a.id for a in assignments]
    submissions = db.query(Submission).filter(Submission.assignment_id.in_(assignment_ids), Submission.status == "released").all() if assignment_ids else []
    released = [s for s in submissions if s.status == "released"]
    answers = db.query(Answer).join(Submission).join(Question).filter(
        Submission.assignment_id.in_(assignment_ids), Submission.status == "released", Answer.is_approved.is_(True)
    ).all() if assignment_ids else []
    questions = {q.id: q for q in db.query(Question).filter(Question.assignment_id.in_(assignment_ids)).all()} if assignment_ids else {}
    topic_scores = defaultdict(list); topic_marks = defaultdict(int); mistakes = Counter()
    for answer in answers:
        q = questions.get(answer.question_id)
        if not q: continue
        topic = (q.rubric or "General").strip().split("\n")[0][:80] or "General"
        score = answer.teacher_score if answer.teacher_score is not None else answer.ai_score
        if score is not None:
            topic_scores[topic].append((score, q.marks))
            topic_marks[topic] = max(topic_marks[topic], q.marks)
        if answer.teacher_feedback or answer.ai_feedback:
            feedback = (answer.teacher_feedback or answer.ai_feedback or "").strip()
            if feedback: mistakes[feedback[:120]] += 1
    topics = []
    for topic, values in topic_scores.items():
        average = sum(v[0] for v in values) / len(values)
        maximum = topic_marks[topic] or 1
        mastery = min(100, average / maximum * 100)
        topics.append({"topic": topic, "question_count": sum(1 for q in questions.values() if ((q.rubric or "General").strip().split("\n")[0][:80] or "General") == topic), "response_count": len(values), "average_score": round(average, 2), "max_marks": maximum, "mastery_percent": round(mastery, 2), "needs_instruction": mastery < 60})
    all_scores = [v[0] for vals in topic_scores.values() for v in vals]
    all_max = [v[1] for vals in topic_scores.values() for v in vals]
    avg = sum(all_scores) / len(all_scores) if all_scores else 0
    max_total = sum(all_max)
    return {"class_id": class_id, "class_name": classroom.name, "subject": classroom.subject, "submission_count": len(submissions), "released_submission_count": len(released), "average_score": round(avg, 2), "average_percent": round(avg / max_total * 100, 2) if max_total else 0, "topics": sorted(topics, key=lambda x: x["mastery_percent"]), "common_mistakes": [{"text": t, "count": n} for t, n in mistakes.most_common(5)]}
