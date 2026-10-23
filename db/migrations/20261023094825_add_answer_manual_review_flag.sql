ALTER TABLE answers ADD COLUMN IF NOT EXISTS needs_manual boolean NOT NULL DEFAULT false;
