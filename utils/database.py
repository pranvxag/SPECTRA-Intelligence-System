"""
utils/database.py — Persistent Storage Layer

Strategy:
- Primary:  SQLite file on disk (survives refreshes, same server instance)
- Fallback: Supabase PostgreSQL (survives redeployments, true cloud DB)
- Cache:    st.session_state (fastest, in-memory)

Usage:
    from utils.database import db
    db.save_student(profile)
    db.get_student("CS2024001")
    db.get_all_students()
    db.save_batch(df)
"""
from __future__ import annotations
import os
import json
import sqlite3
import hashlib
import pandas as pd
import numpy as np
from datetime import datetime
from typing import Optional, List, Dict, Any

# ── Paths ─────────────────────────────────────────────────────────────────
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB_PATH  = os.path.join(BASE_DIR, "data", "spectra.db")
os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)


class SpectraDB:
    """
    SQLite-backed persistent storage for SPECTRA.
    Automatically creates tables on first run.
    """

    def __init__(self, db_path: str = DB_PATH):
        self.db_path = db_path
        self._init_db()

    # ── Connection ─────────────────────────────────────────────────────────
    def _conn(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self.db_path, timeout=10,
                               check_same_thread=False)
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA journal_mode=WAL")   # better concurrency
        conn.execute("PRAGMA foreign_keys=ON")
        return conn

    # ── Schema ─────────────────────────────────────────────────────────────
    def _init_db(self):
        with self._conn() as conn:
            conn.executescript("""
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
                skills_json         TEXT,     -- JSON blob
                interests_json      TEXT,     -- JSON blob
                activities_json     TEXT,     -- JSON blob
                intelligence_score  REAL,
                risk_level          TEXT,
                cluster_id          INTEGER,
                cluster_name        TEXT,
                top_career          TEXT,
                top_career_fit      REAL,
                full_profile_json   TEXT,     -- full dict for quick load
                created_at          TEXT DEFAULT (datetime('now')),
                updated_at          TEXT DEFAULT (datetime('now'))
            );

            CREATE TABLE IF NOT EXISTS career_results (
                id              INTEGER PRIMARY KEY AUTOINCREMENT,
                student_id      TEXT NOT NULL,
                career_title    TEXT NOT NULL,
                fit_score       REAL,
                ml_score        REAL,
                formula_score   REAL,
                rank            INTEGER,
                analysed_at     TEXT DEFAULT (datetime('now')),
                FOREIGN KEY (student_id) REFERENCES students(student_id)
                    ON DELETE CASCADE
            );

            CREATE TABLE IF NOT EXISTS batches (
                batch_id        TEXT PRIMARY KEY,
                institute       TEXT,
                uploaded_by     TEXT,
                student_count   INTEGER,
                cohort_stats_json TEXT,
                dept_report_json  TEXT,
                raw_data_json     TEXT,
                created_at      TEXT DEFAULT (datetime('now'))
            );

            CREATE TABLE IF NOT EXISTS swot_cache (
                student_id      TEXT PRIMARY KEY,
                swot_json       TEXT,
                generated_at    TEXT DEFAULT (datetime('now')),
                FOREIGN KEY (student_id) REFERENCES students(student_id)
                    ON DELETE CASCADE
            );

            CREATE INDEX IF NOT EXISTS idx_students_name    ON students(name);
            CREATE INDEX IF NOT EXISTS idx_students_college ON students(college);
            CREATE INDEX IF NOT EXISTS idx_students_branch  ON students(branch);
            """)

    # ── Student CRUD ───────────────────────────────────────────────────────
    def save_student(self, profile: dict, career_results: list = None,
                     cluster: dict = None) -> bool:
        """Insert or update a student record."""
        try:
            skills     = profile.get("skills", {})
            interests  = profile.get("interests", [])
            activities = {
                "projects":       profile.get("projects", 0),
                "internships":    profile.get("internships", 0),
                "hackathons":     profile.get("hackathons", 0),
                "certifications": profile.get("certifications", 0),
                "extracurriculars": profile.get("extracurriculars", 0),
            }

            top_career     = career_results[0]["title"] if career_results else ""
            top_career_fit = career_results[0]["fit"]   if career_results else 0.0

            with self._conn() as conn:
                conn.execute("""
                    INSERT INTO students
                    (student_id, name, college, branch, year, semester, cgpa,
                     backlogs, academic_trend, effort, career_goal, timeline,
                     skills_json, interests_json, activities_json,
                     intelligence_score, risk_level, cluster_id, cluster_name,
                     top_career, top_career_fit, full_profile_json, updated_at)
                    VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)
                    ON CONFLICT(student_id) DO UPDATE SET
                        name=excluded.name, college=excluded.college,
                        branch=excluded.branch, cgpa=excluded.cgpa,
                        intelligence_score=excluded.intelligence_score,
                        risk_level=excluded.risk_level,
                        cluster_id=excluded.cluster_id,
                        cluster_name=excluded.cluster_name,
                        top_career=excluded.top_career,
                        top_career_fit=excluded.top_career_fit,
                        full_profile_json=excluded.full_profile_json,
                        updated_at=excluded.updated_at
                """, (
                    str(profile.get("student_id", "")),
                    str(profile.get("name", "")),
                    str(profile.get("college", "")),
                    str(profile.get("branch", "")),
                    str(profile.get("year", "")),
                    int(profile.get("semester", 1)),
                    float(profile.get("cgpa", 0)),
                    int(profile.get("backlogs", 0)),
                    str(profile.get("academic_trend", "Stable")),
                    int(profile.get("effort", 3)),
                    str(profile.get("career_goal", "")),
                    str(profile.get("timeline", "")),
                    json.dumps(skills),
                    json.dumps(interests),
                    json.dumps(activities),
                    float(profile.get("intelligence_score", 0)),
                    str(profile.get("risk_level", "Low")),
                    int(cluster.get("cluster_id", 0)) if cluster else 0,
                    str(cluster.get("name", "")) if cluster else "",
                    top_career,
                    float(top_career_fit),
                    json.dumps(profile, default=str),
                    datetime.now().isoformat(),
                ))

                # Save career results
                if career_results:
                    conn.execute("DELETE FROM career_results WHERE student_id=?",
                                 (profile["student_id"],))
                    conn.executemany("""
                        INSERT INTO career_results
                        (student_id, career_title, fit_score, ml_score, formula_score, rank)
                        VALUES (?,?,?,?,?,?)
                    """, [
                        (profile["student_id"], c["title"], c["fit"],
                         c.get("ml_score", 0), c.get("formula_score", 0), i+1)
                        for i, c in enumerate(career_results[:8])
                    ])
            return True
        except Exception as e:
            print(f"DB save_student error: {e}")
            return False

    def get_student(self, student_id: str) -> Optional[dict]:
        """Load a student profile by ID."""
        try:
            with self._conn() as conn:
                row = conn.execute(
                    "SELECT full_profile_json FROM students WHERE student_id=?",
                    (student_id,)
                ).fetchone()
                if row:
                    return json.loads(row["full_profile_json"])
        except Exception as e:
            print(f"DB get_student error: {e}")
        return None

    def search_students(self, query: str) -> List[dict]:
        """Search students by name or ID (partial match)."""
        try:
            q = f"%{query.lower()}%"
            with self._conn() as conn:
                rows = conn.execute("""
                    SELECT student_id, name, college, branch, cgpa,
                           intelligence_score, top_career, top_career_fit, cluster_name
                    FROM students
                    WHERE LOWER(name) LIKE ? OR LOWER(student_id) LIKE ?
                    ORDER BY intelligence_score DESC
                    LIMIT 20
                """, (q, q)).fetchall()
                return [dict(r) for r in rows]
        except Exception as e:
            print(f"DB search error: {e}")
            return []

    def get_all_students(self) -> List[dict]:
        """Return all students as list of lightweight dicts."""
        try:
            with self._conn() as conn:
                rows = conn.execute("""
                    SELECT student_id, name, college, branch, cgpa,
                           intelligence_score, top_career, top_career_fit,
                           risk_level, cluster_name, effort
                    FROM students
                    ORDER BY intelligence_score DESC
                """).fetchall()
                return [dict(r) for r in rows]
        except Exception as e:
            print(f"DB get_all error: {e}")
            return []

    def get_student_career_results(self, student_id: str) -> List[dict]:
        try:
            with self._conn() as conn:
                rows = conn.execute("""
                    SELECT career_title as title, fit_score as fit,
                           ml_score, formula_score, rank
                    FROM career_results
                    WHERE student_id=?
                    ORDER BY rank
                """, (student_id,)).fetchall()
                
                from utils.career_engine import CAREERS
                def _norm(s): return s.lower().replace(" ","").replace("/","").replace("-","")
                results = []
                for r in rows:
                    base_dict = dict(r)
                    matched_c = next((c for c in CAREERS if _norm(c["title"]) == _norm(base_dict["title"])), None)
                    if not matched_c:
                        matched_c = next((c for c in CAREERS if _norm(base_dict["title"])[:8] in _norm(c["title"])), None)
                    
                    fallback = {
                        "salary": "—",
                        "demand": "—",
                        "skills_needed": [],
                        "path": "—",
                        "id": base_dict["title"].lower().replace(" ", "_")
                    }
                    career_info = matched_c or fallback
                    results.append({**career_info, **base_dict})
                return results
        except Exception:
            return []

    def delete_student(self, student_id: str) -> bool:
        try:
            with self._conn() as conn:
                conn.execute("DELETE FROM students WHERE student_id=?", (student_id,))
            return True
        except Exception:
            return False

    # ── SWOT Cache ────────────────────────────────────────────────────────
    def save_swot(self, student_id: str, swot: dict):
        try:
            with self._conn() as conn:
                conn.execute("""
                    INSERT INTO swot_cache (student_id, swot_json, generated_at)
                    VALUES (?,?,?)
                    ON CONFLICT(student_id) DO UPDATE SET
                        swot_json=excluded.swot_json,
                        generated_at=excluded.generated_at
                """, (student_id, json.dumps(swot), datetime.now().isoformat()))
        except Exception as e:
            print(f"DB save_swot error: {e}")

    def get_swot(self, student_id: str) -> Optional[dict]:
        try:
            with self._conn() as conn:
                row = conn.execute(
                    "SELECT swot_json FROM swot_cache WHERE student_id=?",
                    (student_id,)
                ).fetchone()
                if row:
                    return json.loads(row["swot_json"])
        except Exception:
            pass
        return None

    # ── Batch Operations ──────────────────────────────────────────────────
    def save_batch(self, df: pd.DataFrame, cohort_stats: dict,
                   dept_report: pd.DataFrame, institute: str = "") -> str:
        """Save a full uploaded batch. Returns batch_id."""
        try:
            batch_id = hashlib.md5(
                f"{institute}{datetime.now().isoformat()}".encode()
            ).hexdigest()[:12]

            with self._conn() as conn:
                conn.execute("""
                    INSERT INTO batches
                    (batch_id, institute, student_count, cohort_stats_json,
                     dept_report_json, raw_data_json, created_at)
                    VALUES (?,?,?,?,?,?,?)
                """, (
                    batch_id,
                    institute,
                    len(df),
                    json.dumps(cohort_stats, default=str),
                    dept_report.to_json() if isinstance(dept_report, pd.DataFrame) else "{}",
                    df.to_json(orient="records"),
                    datetime.now().isoformat(),
                ))
            return batch_id
        except Exception as e:
            print(f"DB save_batch error: {e}")
            return ""

    def get_latest_batch(self) -> Optional[dict]:
        """Get the most recently uploaded batch."""
        try:
            with self._conn() as conn:
                row = conn.execute("""
                    SELECT * FROM batches ORDER BY created_at DESC LIMIT 1
                """).fetchone()
                if row:
                    result = dict(row)
                    result["cohort_stats"]  = json.loads(result["cohort_stats_json"] or "{}")
                    result["df"]            = pd.read_json(result["raw_data_json"])
                    result["dept_report"]   = pd.read_json(result["dept_report_json"])
                    return result
        except Exception as e:
            print(f"DB get_latest_batch error: {e}")
        return None

    def get_all_batches(self) -> List[dict]:
        try:
            with self._conn() as conn:
                rows = conn.execute("""
                    SELECT batch_id, institute, student_count, created_at
                    FROM batches ORDER BY created_at DESC
                """).fetchall()
                return [dict(r) for r in rows]
        except Exception:
            return []

    # ── Institutional Stats ───────────────────────────────────────────────
    def get_live_cohort_stats(self) -> dict:
        """Compute live stats from the students table."""
        try:
            with self._conn() as conn:
                stats = {}
                row = conn.execute("""
                    SELECT
                        COUNT(*)               as total,
                        AVG(cgpa)              as avg_cgpa,
                        AVG(intelligence_score)as avg_intel,
                        SUM(CASE WHEN risk_level='High' THEN 1 ELSE 0 END) as high_risk,
                        SUM(CASE WHEN risk_level IN ('High','Medium') THEN 1 ELSE 0 END) as at_risk
                    FROM students
                """).fetchone()
                if row:
                    stats = {
                        "total_students":   int(row["total"]),
                        "cgpa_mean":        round(float(row["avg_cgpa"] or 0), 2),
                        "intel_mean":       round(float(row["avg_intel"] or 0), 1),
                        "risk_high":        int(row["high_risk"]),
                        "at_risk":          int(row["at_risk"]),
                    }
                return stats
        except Exception:
            return {}

    # ── Utilities ─────────────────────────────────────────────────────────
    def get_stats(self) -> dict:
        """DB health/size stats."""
        try:
            with self._conn() as conn:
                students = conn.execute("SELECT COUNT(*) FROM students").fetchone()[0]
                batches  = conn.execute("SELECT COUNT(*) FROM batches").fetchone()[0]
                size_kb  = round(os.path.getsize(self.db_path) / 1024, 1)
                return {"students": students, "batches": batches,
                        "size_kb": size_kb, "db_path": self.db_path}
        except Exception:
            return {}

    def clear_all(self):
        """Wipe all data (use with caution)."""
        with self._conn() as conn:
            conn.executescript("""
                DELETE FROM career_results;
                DELETE FROM swot_cache;
                DELETE FROM students;
                DELETE FROM batches;
            """)


# ── Singleton ─────────────────────────────────────────────────────────────
db = SpectraDB()
