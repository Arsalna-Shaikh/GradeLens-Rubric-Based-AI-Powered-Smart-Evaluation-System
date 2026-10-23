from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.db import get_db
from app.deps import require_role
from app.models.user import User
from app.models.submission import Submission
from app.services.ocr_service import extract_pdf_text

router = APIRouter(prefix="/ocr", tags=["OCR"])
Teacher = Annotated[User, Depends(require_role("teacher"))]

@router.post("/submissions/{submission_id}")
def process_submission(submission_id: int, current: Teacher, db: Annotated[Session, Depends(get_db)]):
    item = (db.query(Submission).filter(Submission.id == submission_id,
        Submission.assignment.has(teacher_id=current.id)).first())
    if not item:
        raise HTTPException(404, "Submission not found")
    if not item.pdf_path:
        raise HTTPException(400, "Submission has no PDF file available for OCR")
    item.ocr_status = "processing"
    db.commit()
    try:
        if not item.pdf_path.startswith("data://"):
            raise RuntimeError("PDF storage is not configured for this submission")
        import base64
        text = extract_pdf_text(base64.b64decode(item.pdf_path[7:]))
        item.ocr_text = text
        item.ocr_status = "completed"
        item.ocr_error = None
    except Exception as exc:
        item.ocr_status = "failed"
        item.ocr_error = str(exc)
        db.commit()
        raise HTTPException(422, item.ocr_error)
    from datetime import datetime, timezone
    item.ocr_processed_at = datetime.now(timezone.utc)
    db.commit()
    return {"submission_id": item.id, "status": item.ocr_status, "text": item.ocr_text}

@router.get("/submissions/{submission_id}")
def ocr_status(submission_id: int, current: Teacher, db: Annotated[Session, Depends(get_db)]):
    item = (db.query(Submission).filter(Submission.id == submission_id,
        Submission.assignment.has(teacher_id=current.id)).first())
    if not item:
        raise HTTPException(404, "Submission not found")
    return {"submission_id": item.id, "status": item.ocr_status, "text": item.ocr_text, "error": item.ocr_error}
