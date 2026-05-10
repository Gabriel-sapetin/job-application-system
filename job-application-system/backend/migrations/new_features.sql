-- ══════════════════════════════════════
-- JobTrack — New Feature Tables
-- Run this in Supabase SQL Editor
-- ══════════════════════════════════════

-- 1. Activity Log
CREATE TABLE IF NOT EXISTS activity_log (
  id          BIGSERIAL PRIMARY KEY,
  user_id     BIGINT NOT NULL REFERENCES users(id) ON DELETE CASCADE,
  action      TEXT NOT NULL,          -- 'login', 'profile_update', 'application_submit', etc.
  details     TEXT,
  ip_address  TEXT,
  user_agent  TEXT,
  created_at  TIMESTAMPTZ DEFAULT NOW()
);
CREATE INDEX IF NOT EXISTS idx_activity_log_user ON activity_log(user_id, created_at DESC);

-- 2. Message Reactions
CREATE TABLE IF NOT EXISTS message_reactions (
  id          BIGSERIAL PRIMARY KEY,
  message_id  BIGINT NOT NULL REFERENCES messages(id) ON DELETE CASCADE,
  user_id     BIGINT NOT NULL REFERENCES users(id) ON DELETE CASCADE,
  emoji       TEXT NOT NULL,
  created_at  TIMESTAMPTZ DEFAULT NOW(),
  UNIQUE(message_id, user_id, emoji)
);
CREATE INDEX IF NOT EXISTS idx_message_reactions_msg ON message_reactions(message_id);

-- 3. Application Attachments
CREATE TABLE IF NOT EXISTS application_attachments (
  id              BIGSERIAL PRIMARY KEY,
  application_id  BIGINT NOT NULL REFERENCES applications(id) ON DELETE CASCADE,
  user_id         BIGINT NOT NULL REFERENCES users(id) ON DELETE CASCADE,
  file_url        TEXT NOT NULL,
  file_name       TEXT,
  file_type       TEXT,
  file_size       BIGINT,
  label           TEXT DEFAULT 'Document',
  created_at      TIMESTAMPTZ DEFAULT NOW()
);
CREATE INDEX IF NOT EXISTS idx_app_attachments ON application_attachments(application_id);

-- Enable RLS (Row Level Security) for new tables
ALTER TABLE activity_log ENABLE ROW LEVEL SECURITY;
ALTER TABLE message_reactions ENABLE ROW LEVEL SECURITY;
ALTER TABLE application_attachments ENABLE ROW LEVEL SECURITY;

-- RLS Policies: allow service key full access (backend uses service key)
CREATE POLICY "service_all_activity_log" ON activity_log FOR ALL USING (true) WITH CHECK (true);
CREATE POLICY "service_all_message_reactions" ON message_reactions FOR ALL USING (true) WITH CHECK (true);
CREATE POLICY "service_all_application_attachments" ON application_attachments FOR ALL USING (true) WITH CHECK (true);
