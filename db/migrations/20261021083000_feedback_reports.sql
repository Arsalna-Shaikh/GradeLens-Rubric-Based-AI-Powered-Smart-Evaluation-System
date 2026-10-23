CREATE TABLE IF NOT EXISTS feedback_reports (
  id SERIAL PRIMARY KEY,
  submission_id INTEGER NOT NULL UNIQUE REFERENCES submissions(id) ON DELETE CASCADE,
  pdf_path VARCHAR(512) NOT NULL,
  generated_at TIMESTAMPTZ NOT NULL DEFAULT now(),
  is_downloaded BOOLEAN NOT NULL DEFAULT false
);
CREATE INDEX IF NOT EXISTS ix_feedback_reports_submission_id ON feedback_reports(submission_id);
