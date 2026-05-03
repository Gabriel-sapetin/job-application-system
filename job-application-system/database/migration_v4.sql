-- ══════════════════════════════════════════════════════════
-- MIGRATION V4 — Admin Panel & Reports
-- Run in Supabase SQL Editor
-- ══════════════════════════════════════════════════════════

-- BLOCK 1: Add admin role to users table
ALTER TABLE users
  DROP CONSTRAINT IF EXISTS users_role_check;
ALTER TABLE users
  ADD CONSTRAINT users_role_check CHECK (role IN ('applicant', 'employer', 'admin'));

-- BLOCK 2: Create reports table
CREATE TABLE IF NOT EXISTS reports (
    id          BIGSERIAL    PRIMARY KEY,
    job_id      BIGINT       REFERENCES jobs(id) ON DELETE SET NULL,
    reporter_id BIGINT       REFERENCES users(id) ON DELETE SET NULL,
    reason      TEXT         NOT NULL,
    details     TEXT,
    status      TEXT         NOT NULL DEFAULT 'pending'
                             CHECK (status IN ('pending', 'reviewed', 'dismissed', 'actioned')),
    admin_notes TEXT,
    created_at  TIMESTAMPTZ  DEFAULT NOW()
);

-- BLOCK 3: Indexes
CREATE INDEX IF NOT EXISTS idx_reports_job_id    ON reports(job_id);
CREATE INDEX IF NOT EXISTS idx_reports_status    ON reports(status);
CREATE INDEX IF NOT EXISTS idx_reports_reporter  ON reports(reporter_id);

-- BLOCK 4: Create your admin account
-- Replace the email below with your own, then run.
-- After running, log in with this email + password "admin1234" and change it.
INSERT INTO users (name, email, password, role)
VALUES (
  'Admin',
  'jobrack31@gmail.com',
  'mynewaccount12052005',
  'admin'
)
ON CONFLICT (email) DO UPDATE SET role = 'admin';

-- NOTE: The password hash above = "admin1234"
-- Log in at /pages/login.html with admin@jobtrack.com / admin1234
-- Then go to /pages/admin.html
-- CHANGE YOUR PASSWORD IMMEDIATELY after first login.