ALTER TABLE assignments ADD COLUMN IF NOT EXISTS pass_mark_percent integer NOT NULL DEFAULT 50;
