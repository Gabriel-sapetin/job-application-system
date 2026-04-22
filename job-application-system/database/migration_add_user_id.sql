-- ============================================================
-- MIGRATION: Add user_id to applications table
-- Run this in Supabase SQL Editor if you already ran schema.sql
-- ============================================================

-- Add user_id column
ALTER TABLE applications
  ADD COLUMN IF NOT EXISTS user_id BIGINT REFERENCES users(id) ON DELETE CASCADE;

-- Drop old unique constraint (job_id, email) and replace with (job_id, user_id)
ALTER TABLE applications DROP CONSTRAINT IF EXISTS applications_job_id_email_key;
ALTER TABLE applications ADD CONSTRAINT applications_job_id_user_id_key UNIQUE (job_id, user_id);

-- Update index
CREATE INDEX IF NOT EXISTS idx_apps_user_id ON applications(user_id);
