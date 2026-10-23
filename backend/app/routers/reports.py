from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import Response
from sqlalchemy.orm import Session, joinedload
from app.db import get_db
from app.deps import require_role
from app.models.user import User
from app.models.submission import Submission
from app.models.assignment import Assignment
from app.models.feedback_report import FeedbackReport
from app.services.report_service import build_feedback_pdf
from pathlib import Path
import secrets

router = APIRouter(tags=["PDF reports"])
Student = Annotated[User, Depends(require_role("student"))]

# Keep the public download URL stable and unambiguous.  The route is deliberately
# student-scoped; approval is checked before any report generation or metadata is
# returned.


def get_student_submission(submission_id, current, db):
    item = (db.query(Submission).options(joinedload(Submission.answers), joinedload(Submission.student),
        joinedload(Submission.assignment)).filter(Submission.id == submission_id, Submission.student_id == current.id,
        Submission.status == "released").first())
    if not item:
        raise HTTPException(404, "Released submission not found")
    return item


@router.get("/submissions/{submission_id}/feedback-pdf")
def feedback_pdf_alias(submission_id: int, current: Student, db: Annotated[Session, Depends(get_db)]):
    return download_report(submission_id, current, db)

@router.get("/submissions/{submission_id}.pdf")
def download_report(submission_id: int, current: Student, db: Annotated[Session, Depends(get_db)]):
    submission = get_student_submission(submission_id, current, db)
    report = db.query(FeedbackReport).filter_by(submission_id=submission.id).first()
    # Generate on demand and persist generation metadata. Bytes are returned
    # directly; the recorded path is never treated as a client-controlled path.
    pdf = build_feedback_pdf(submission, current.name, submission.assignment.title)
    storage = Path(__file__).resolve().parents[2] / "storage" / "reports"
    storage.mkdir(parents=True, exist_ok=True)
    path = storage / f"feedback-{submission.id}-{secrets.token_urlsafe(8)}.pdf"
    path.write_bytes(pdf)
    if not report:
        report = FeedbackReport(submission_id=submission.id, pdf_path=str(path.relative_to(Path(__file__).resolve().parents[2])))
        db.add(report)
    else:
        report.pdf_path = str(path.relative_to(Path(__file__).resolve().parents[2]))
    report.is_downloaded = True
    db.commit()
    return Response(pdf, media_type="application/pdf", headers={"Content-Disposition": f'inline; filename="feedback-{submission.id}.pdf"'})
