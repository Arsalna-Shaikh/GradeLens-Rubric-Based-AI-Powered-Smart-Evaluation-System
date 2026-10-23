"""Server-side grading helpers. LLM drafts are never teacher fields."""
import asyncio
import json
import httpx
from sqlalchemy.orm import Session
from app.config import settings
from app.db import SessionLocal
from app.models.submission import Submission
from app.models.question import Question
from app.models.answer import Answer

def _prompt(q, answer):
    return f'''Evaluate this answer using the rubric. Return JSON only with score (0-{q.marks}), justification, strengths, lackings, suggestions.
Question: {q.text}
Marks: {q.marks}
Rubric: {q.rubric or "Use correctness, relevance, and completeness."}
Sample answer: {q.sample_answer or "none"}
Student answer: {answer}'''


def _validate(value, marks):
    if not isinstance(value, dict) or not all(k in value for k in ("score", "justification", "strengths", "lackings", "suggestions")):
        raise ValueError("LLM response missing required fields")
    score = value["score"]
    lists = (value["strengths"], value["lackings"], value["suggestions"])
    if not isinstance(score, (int, float)) or not 0 <= score <= marks or any(not isinstance(x, list) or any(not isinstance(s, str) for s in x) for x in lists):
        raise ValueError("Invalid LLM grading JSON")
    return {"score": int(score), "justification": str(value["justification"]), "strengths": value["strengths"], "lackings": value["lackings"], "suggestions": value["suggestions"]}

async def evaluate_written(q, answer: str) -> dict:
    if not settings.GROQ_API_KEY:
        raise RuntimeError("GROQ_API_KEY is not configured; written answers require manual grading")
    body = {"model": settings.GROQ_MODEL, "messages": [{"role":"system", "content":"Return valid JSON only."}, {"role":"user", "content":_prompt(q, answer)}], "temperature": 0.1}
    async with httpx.AsyncClient(timeout=45) as client:
        for attempt in range(2):
            response = await client.post("https://api.groq.com/openai/v1/chat/completions", json=body, headers={"Authorization": f"Bearer {settings.GROQ_API_KEY}"})
            if response.status_code == 429 and attempt == 0:
                await asyncio.sleep(1); continue
            response.raise_for_status()
            raw = response.json()["choices"][0]["message"]["content"].replace("```json", "").replace("```", "").strip()
            try: return _validate(json.loads(raw), q.marks)
            except (ValueError, json.JSONDecodeError):
                if attempt == 1: raise
    raise RuntimeError("LLM grading failed")


def grade_submission_in_background(submission_id: int):
    db: Session = SessionLocal()
    try:
        submission = db.query(Submission).filter_by(id=submission_id).first()
        if not submission: return
        questions = db.query(Question).filter_by(assignment_id=submission.assignment_id).order_by(Question.id).all()
        lines = (submission.content_text or "").splitlines()
        for index, question in enumerate(questions):
            answer = db.query(Answer).filter_by(submission_id=submission.id, question_id=question.id).first() or Answer(submission_id=submission.id, question_id=question.id)
            text = lines[index].strip() if index < len(lines) else ""
            answer.extracted_text = text
            if question.type == "mcq":
                normalized = text.casefold().strip(" .()[]")
                if normalized.startswith("option "): normalized = normalized[-1:]
                expected = (question.correct_answer or "").casefold().strip(" .()[]")
                answer.ai_score = question.marks if normalized == expected else 0
            else:
                try:
                    result = asyncio.run(evaluate_written(question, text))
                    answer.ai_score, answer.ai_feedback = result["score"], result["justification"]
                    answer.ai_strengths, answer.ai_lackings, answer.ai_suggestions = result["strengths"], result["lackings"], result["suggestions"]
                except Exception:
                    answer.needs_manual = True
            db.add(answer)
        submission.status = "graded_draft"
        db.commit()
    finally:
        db.close()


# Compatibility entry point for the optional synchronous grading router.
async def grade_submission(submission_id: int, db: Session):
    submission = db.query(Submission).filter_by(id=submission_id).first()
    if not submission:
        return []
    grade_submission_in_background(submission_id)
    return db.query(Answer).filter_by(submission_id=submission_id).all()
