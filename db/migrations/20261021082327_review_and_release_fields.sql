ALTER TABLE submissions ADD COLUMN IF NOT EXISTS released_at timestamptz;
ALTER TABLE submissions ADD COLUMN IF NOT EXISTS released_by integer REFERENCES users(id);
CREATE INDEX IF NOT EXISTS ix_submissions_status ON submissions(status);
