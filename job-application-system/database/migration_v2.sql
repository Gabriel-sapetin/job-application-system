-- ══════════════════════════════════════════════
-- MIGRATION V2 — Run in Supabase SQL Editor
-- ══════════════════════════════════════════════

-- Add new columns to jobs
ALTER TABLE jobs
  ADD COLUMN IF NOT EXISTS category       TEXT,
  ADD COLUMN IF NOT EXISTS max_applicants INT,
  ADD COLUMN IF NOT EXISTS deadline       DATE,
  ADD COLUMN IF NOT EXISTS status         TEXT DEFAULT 'open'
    CHECK (status IN ('open','closed','full'));

-- Add profile columns to users
ALTER TABLE users
  ADD COLUMN IF NOT EXISTS profile_pic TEXT,
  ADD COLUMN IF NOT EXISTS about_me    TEXT,
  ADD COLUMN IF NOT EXISTS instagram   TEXT,
  ADD COLUMN IF NOT EXISTS facebook    TEXT;

-- Add user_id FK to applications if not present
ALTER TABLE applications
  ADD COLUMN IF NOT EXISTS user_id BIGINT REFERENCES users(id) ON DELETE CASCADE;

-- Set all existing jobs to open
UPDATE jobs SET status = 'open' WHERE status IS NULL;

-- Indexes
CREATE INDEX IF NOT EXISTS idx_jobs_category ON jobs(category);
CREATE INDEX IF NOT EXISTS idx_jobs_status   ON jobs(status);
CREATE INDEX IF NOT EXISTS idx_apps_user_id  ON applications(user_id);
