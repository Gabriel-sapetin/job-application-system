-- ══════════════════════════════════════════════════════════
-- MIGRATION V6 — Chat / Messaging
-- Run in Supabase SQL Editor
-- ══════════════════════════════════════════════════════════

CREATE TABLE IF NOT EXISTS messages (
    id             BIGSERIAL    PRIMARY KEY,
    application_id BIGINT       NOT NULL REFERENCES applications(id) ON DELETE CASCADE,
    sender_id      BIGINT       NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    body           TEXT         NOT NULL,
    created_at     TIMESTAMPTZ  DEFAULT NOW(),
    is_read        BOOLEAN      DEFAULT FALSE
);

CREATE INDEX IF NOT EXISTS idx_messages_app_id    ON messages(application_id);
CREATE INDEX IF NOT EXISTS idx_messages_sender    ON messages(sender_id);
CREATE INDEX IF NOT EXISTS idx_messages_unread    ON messages(is_read) WHERE is_read = FALSE;