-- ============================================================
-- JobTrack — Supabase SQL Schema
-- Run this in your Supabase SQL Editor to set up the database
-- ============================================================


-- ── USERS ────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS users (
    id         BIGSERIAL    PRIMARY KEY,
    name       TEXT         NOT NULL,
    email      TEXT         NOT NULL UNIQUE,
    password   TEXT         NOT NULL,
    role       TEXT         NOT NULL CHECK (role IN ('applicant', 'employer')),
    created_at TIMESTAMPTZ  DEFAULT NOW()
);


-- ── JOBS ─────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS jobs (
    id          BIGSERIAL    PRIMARY KEY,
    title       TEXT         NOT NULL,
    company     TEXT         NOT NULL,
    location    TEXT         NOT NULL,
    type        TEXT         NOT NULL CHECK (type IN ('Full-Time', 'Part-Time', 'Internship', 'Remote')),
    salary      TEXT,
    description TEXT,
    employer_id BIGINT       REFERENCES users(id) ON DELETE SET NULL,
    created_at  TIMESTAMPTZ  DEFAULT NOW()
);


-- ── APPLICATIONS ─────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS applications (
    id           BIGSERIAL    PRIMARY KEY,
    job_id       BIGINT       NOT NULL REFERENCES jobs(id) ON DELETE CASCADE,
    user_id      BIGINT       NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    name         TEXT         NOT NULL,
    email        TEXT         NOT NULL,
    cover_letter TEXT,
    resume_url   TEXT,
    status       TEXT         NOT NULL DEFAULT 'pending'
                              CHECK (status IN ('pending', 'reviewed', 'accepted', 'rejected')),
    created_at   TIMESTAMPTZ  DEFAULT NOW(),

    -- Prevent duplicate applications
    UNIQUE (job_id, user_id)
);


-- ── INDEXES ──────────────────────────────────────────────────
CREATE INDEX IF NOT EXISTS idx_jobs_type        ON jobs(type);
CREATE INDEX IF NOT EXISTS idx_jobs_location    ON jobs(location);
CREATE INDEX IF NOT EXISTS idx_apps_job_id      ON applications(job_id);
CREATE INDEX IF NOT EXISTS idx_apps_email       ON applications(email);
CREATE INDEX IF NOT EXISTS idx_apps_status      ON applications(status);
