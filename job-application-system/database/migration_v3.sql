-- ══════════════════════════════════════════════════════════
-- MIGRATION V3 — FIXED
-- Run each block SEPARATELY if "JWT failed verification" appears
-- Role must be "postgres" (shown top-right of SQL Editor)
-- ══════════════════════════════════════════════════════════

-- BLOCK 1: Add columns to users table
ALTER TABLE users
  ADD COLUMN IF NOT EXISTS banner_url TEXT,
  ADD COLUMN IF NOT EXISTS phone      TEXT,
  ADD COLUMN IF NOT EXISTS website    TEXT;

-- BLOCK 2: Add column to jobs table
ALTER TABLE jobs
  ADD COLUMN IF NOT EXISTS image_url TEXT;

-- BLOCK 3: Add application notes column (Improvement #4)
ALTER TABLE applications
  ADD COLUMN IF NOT EXISTS employer_notes TEXT;

-- BLOCK 4: Add job view tracking (Improvement #5 analytics)
ALTER TABLE jobs
  ADD COLUMN IF NOT EXISTS view_count INT DEFAULT 0;

-- BLOCK 5: Indexes
CREATE INDEX IF NOT EXISTS idx_users_website  ON users(website)      WHERE website IS NOT NULL;
CREATE INDEX IF NOT EXISTS idx_jobs_image     ON jobs(image_url)     WHERE image_url IS NOT NULL;
CREATE INDEX IF NOT EXISTS idx_jobs_views     ON jobs(view_count);

-- ══ NOTE: If you still get "JWT failed verification" ══
-- 1. Log out of Supabase dashboard and log back in
-- 2. Run each BLOCK separately (highlight lines → Run)
-- 3. Or use: Dashboard → Database → Migrations instead
