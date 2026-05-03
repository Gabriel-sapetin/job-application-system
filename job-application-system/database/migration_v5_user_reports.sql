-- ══════════════════════════════════════════════════════════
-- MIGRATION V5 — User Reports
-- Run in Supabase SQL Editor
-- ══════════════════════════════════════════════════════════

CREATE TABLE IF NOT EXISTS user_reports (
    id           BIGSERIAL    PRIMARY KEY,
    reported_id  BIGINT       REFERENCES users(id) ON DELETE CASCADE,
    reporter_id  BIGINT       REFERENCES users(id) ON DELETE SET NULL,
    reason       TEXT         NOT NULL,
    details      TEXT,
    status       TEXT         NOT NULL DEFAULT 'pending'
                              CHECK (status IN ('pending', 'reviewed', 'dismissed', 'actioned')),
    admin_notes  TEXT,
    created_at   TIMESTAMPTZ  DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_user_reports_reported ON user_reports(reported_id);
CREATE INDEX IF NOT EXISTS idx_user_reports_reporter ON user_reports(reporter_id);
CREATE INDEX IF NOT EXISTS idx_user_reports_status   ON user_reports(status);