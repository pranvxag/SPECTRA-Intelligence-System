-- ============================================================
-- SPECTRA Database Schema for Supabase PostgreSQL
-- Run this ONCE in the Supabase SQL Editor:
--   Dashboard → SQL Editor → New Query → Paste & Run
-- ============================================================

-- Students table
CREATE TABLE IF NOT EXISTS students (
    student_id          TEXT PRIMARY KEY,
    name                TEXT NOT NULL,
    college             TEXT,
    branch              TEXT,
    year                TEXT,
    semester            INTEGER,
    cgpa                REAL,
    backlogs            INTEGER DEFAULT 0,
    academic_trend      TEXT,
    effort              INTEGER,
    career_goal         TEXT,
    timeline            TEXT,
    skills_json         TEXT,
    interests_json      TEXT,
    activities_json     TEXT,
    intelligence_score  REAL,
    risk_level          TEXT,
    cluster_id          INTEGER,
    cluster_name        TEXT,
    top_career          TEXT,
    top_career_fit      REAL,
    full_profile_json   TEXT,
    created_at          TIMESTAMPTZ DEFAULT NOW(),
    updated_at          TIMESTAMPTZ DEFAULT NOW()
);

-- Career results table
CREATE TABLE IF NOT EXISTS career_results (
    id              SERIAL PRIMARY KEY,
    student_id      TEXT NOT NULL REFERENCES students(student_id) ON DELETE CASCADE,
    career_title    TEXT NOT NULL,
    fit_score       REAL,
    ml_score        REAL,
    formula_score   REAL,
    rank            INTEGER,
    analysed_at     TIMESTAMPTZ DEFAULT NOW()
);

-- Batches table (admin batch uploads)
CREATE TABLE IF NOT EXISTS batches (
    batch_id            TEXT PRIMARY KEY,
    institute           TEXT,
    uploaded_by         TEXT,
    student_count       INTEGER,
    cohort_stats_json   TEXT,
    dept_report_json    TEXT,
    raw_data_json       TEXT,
    created_at          TIMESTAMPTZ DEFAULT NOW()
);

-- SWOT cache (stores LLM-generated SWOT)
CREATE TABLE IF NOT EXISTS swot_cache (
    student_id      TEXT PRIMARY KEY REFERENCES students(student_id) ON DELETE CASCADE,
    swot_json       TEXT,
    generated_at    TIMESTAMPTZ DEFAULT NOW()
);

-- Indexes
CREATE INDEX IF NOT EXISTS idx_students_name    ON students(name);
CREATE INDEX IF NOT EXISTS idx_students_college ON students(college);
CREATE INDEX IF NOT EXISTS idx_students_branch  ON students(branch);
