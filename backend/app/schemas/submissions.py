from datetime import datetime
from typing import Optional
from pydantic import BaseModel, ConfigDict

class SubmissionOut(BaseModel):
    """Teacher-safe submission metadata; never includes answer drafts."""
    model_config = ConfigDict(from_attributes=True)
    id: int
    assignment_id: int
    student_id: int
    pdf_path: Optional[str] = None
    content_text: Optional[str] = None
    original_filename: Optional[str] = None
    mime_type: Optional[str] = None
    file_size: Optional[int] = None
    status: str
    submitted_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

class StudentSubmissionOut(BaseModel):
    """Minimal student status contract. Draft scores and extracted work stay server-side."""
    model_config = ConfigDict(from_attributes=True)
    id: int
    assignment_id: int
    student_id: int
    status: str
    submitted_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
