from datetime import datetime, timezone
from typing import Optional
from sqlalchemy import String, DateTime, Integer, ForeignKey, Boolean, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db import Base


class FeedbackReport(Base):
    __tablename__ = "feedback_reports"
    __table_args__ = (
        UniqueConstraint("submission_id", name="uq_feedback_report_submission"),
    )

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    submission_id: Mapped[int] = mapped_column(ForeignKey("submissions.id", ondelete="CASCADE"), nullable=False)
    pdf_path: Mapped[str] = mapped_column(String(512), nullable=False)
    generated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=datetime.now(timezone.utc), nullable=False
    )
    is_downloaded: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

    submission: Mapped["Submission"] = relationship("Submission", back_populates="feedback_report")
