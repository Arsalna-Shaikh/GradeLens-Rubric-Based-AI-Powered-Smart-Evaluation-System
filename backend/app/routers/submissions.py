from typing import Annotated
from fastapi import APIRouter, BackgroundTasks, Depends, File, Form, HTTPException, UploadFile
from sqlalchemy.orm import Session
from datetime import datetime, timezone
from pathlib import Path
import secrets
from app.db import get_db
from app.deps import require_role
from app.models.user import User
from app.models.assignment import Assignment
from app.models.class_ import Class
from app.models.enrollment import Enrollment
from app.models.submission import Submission
from app.schemas.submissions import SubmissionOut, StudentSubmissionOut

router = APIRouter(prefix="/submissions", tags=["submissions"])
Student = Annotated[User, Depends(require_role("student"))]
MAX_BYTES = 10 * 1024 * 1024

@router.post("/assignments/{assignment_id}", response_model=SubmissionOut, status_code=201)
async def submit(assignment_id: int, background_tasks: BackgroundTasks, current: Student, db: Annotated[Session, Depends(get_db)], content_text: str | None = Form(None), file: UploadFile | None = File(None)):
    assignment = db.query(Assignment).join(Class).join(Enrollment, Enrollment.class_id == Class.id).filter(Assignment.id == assignment_id, Enrollment.student_id == current.id).first()
    if not assignment:
        raise HTTPException(404, "Assignment not found or you are not enrolled")
    if assignment.deadline and datetime.now(timezone.utc) > assignment.deadline:
        raise HTTPException(403, "The submission deadline has passed")
    if db.query(Submission).filter_by(assignment_id=assignment_id, student_id=current.id).first():
        raise HTTPException(409, "A submission already exists for this assignment")
    if content_text is not None and not content_text.strip():
        content_text = None
    if not content_text and not file:
        raise HTTPException(400, "Provide typed work or a PDF file")
    data = {"content_text": content_text.strip() if content_text else None, "pdf_path": None, "original_filename": None, "mime_type": None, "file_size": None}
    if file:
        if not file.filename or Path(file.filename).suffix.lower() != ".pdf":
            raise HTTPException(400, "Only .pdf uploads are accepted")
        if file.content_type not in (None, "application/pdf", "application/octet-stream"):
            raise HTTPException(400, "Only PDF uploads are accepted")
        blob = await file.read()
        if len(blob) > MAX_BYTES: raise HTTPException(413, "PDF must be 10 MB or smaller")
        if not blob.startswith(b"%PDF-"):
            raise HTTPException(400, "The uploaded file is not a valid PDF")
        storage = Path(__file__).resolve().parents[2] / "storage" / "submissions"
        storage.mkdir(parents=True, exist_ok=True)
        safe_name = f"{secrets.token_urlsafe(24)}.pdf"
        path = storage / safe_name
        path.write_bytes(blob)
        data.update(pdf_path=str(path.relative_to(Path(__file__).resolve().parents[2])), original_filename=file.filename, mime_type="application/pdf", file_size=len(blob))
    item = Submission(assignment_id=assignment_id, student_id=current.id)
    for key, value in data.items(): setattr(item, key, value)
    item.status = "submitted"
    db.add(item); db.commit(); db.refresh(item)
    # Grading is deliberately queued after persistence; failures remain a draft/manual concern.
    from app.services.grading_service import grade_submission_in_background
    background_tasks.add_task(grade_submission_in_background, item.id)
    return item

@router.get("/mine", response_model=list[StudentSubmissionOut])
def mine(current: Student, db: Annotated[Session, Depends(get_db)]):
    # Status metadata is safe before release; response schema excludes work,
    # scores, feedback, and every ai_* draft field.
    return db.query(Submission).filter(Submission.student_id == current.id).order_by(Submission.updated_at.desc()).all()

@router.get("/assignments/{assignment_id}/status", response_model=StudentSubmissionOut | None)
def status(assignment_id: int, current: Student, db: Annotated[Session, Depends(get_db)]):
    item = db.query(Submission).filter_by(assignment_id=assignment_id, student_id=current.id).first()
    return item if item and item.status in ("submitted", "graded_draft", "released") else None

Teacher = Annotated[User, Depends(require_role("teacher"))]

@router.get("/for-grading", response_model=list[SubmissionOut])
def for_grading(current: Teacher, db: Annotated[Session, Depends(get_db)]):
    # Assignment ownership is enforced in the query; no client-supplied teacher
    # or class id is trusted.
    return (db.query(Submission).join(Assignment).filter(Assignment.class_.has(teacher_id=current.id))
            .order_by(Submission.updated_at.desc()).all())

@router.get("/assignments/{assignment_id}/submissions", response_model=list[SubmissionOut])
def assignment_submissions(assignment_id: int, current: Teacher, db: Annotated[Session, Depends(get_db)]):
    """Owner-only listing used by the teacher dashboard."""
    rows = (db.query(Submission).join(Assignment).filter(
        Submission.assignment_id == assignment_id,
        Assignment.class_.has(teacher_id=current.id),
    ).order_by(Submission.updated_at.desc()).all())
    if not db.query(Assignment).filter(Assignment.id == assignment_id, Assignment.class_.has(teacher_id=current.id)).first():
        raise HTTPException(404, "Assignment not found")
    return rows

@router.post("/{submission_id}/regrade", response_model=SubmissionOut)
def regrade(submission_id: int, background_tasks: BackgroundTasks, current: Teacher, db: Annotated[Session, Depends(get_db)]):
    item = (db.query(Submission).join(Assignment).filter(
        Submission.id == submission_id, Assignment.class_.has(teacher_id=current.id)).first())
    if not item:
        raise HTTPException(404, "Submission not found")
    from app.services.grading_service import grade_submission_in_background
    item.status = "submitted"
    db.commit()
    background_tasks.add_task(grade_submission_in_background, item.id)
    return item
