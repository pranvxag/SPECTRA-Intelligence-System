"""
utils/database.py — Persistent Storage Layer

Strategy (in priority order):
  1. Supabase PostgreSQL  — if [supabase] section is in secrets.toml
  2. SQLite on disk       — automatic fallback (great for local dev / offline)
  3. st.session_state     — in-memory last resort

Both backends expose the _exact same public API_ so no other file changes.

Usage:
    from utils.database import db
    db.save_student(profile)
    db.get_student("CS2024001")
    db.get_all_students()
"""
from __future__ import annotations
import os
import json
import hashlib
import sqlite3
import pandas as pd
from datetime import datetime
from typing import Optional, List, Dict, Any

# ── Paths ──────────────────────────────────────────────────────────────────
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB_PATH  = os.path.join(BASE_DIR, "data", "spectra.db")
os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)


# ══════════════════════════════════════════════════════════════════════════
#  SQLITE BACKEND
# ══════════════════════════════════════════════════════════════════════════

class SpectraDB:
    """SQLite-backed persistent storage for SPECTRA (local / offline)."""

    def __init__(self, db_path: str = DB_PATH):
        self.db_path = db_path
        self.backend = "sqlite"
        self._init_db()

    def _conn(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self.db_path, timeout=10, check_same_thread=False)
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA journal_mode=WAL")
        conn.execute("PRAGMA foreign_keys=ON")
        return conn

    def _init_db(self):
        with self._conn() as conn:
            conn.executescript("""
            CREATE TABLE IF NOT EXISTS students (
                student_id TEXT PRIMARY KEY, name TEXT NOT NULL, college TEXT,
                branch TEXT, year TEXT, semester INTEGER, cgpa REAL,
                backlogs INTEGER DEFAULT 0, academic_trend TEXT, effort INTEGER,
                career_goal TEXT, timeline TEXT, skills_json TEXT,
                interests_json TEXT, activities_json TEXT, intelligence_score REAL,
                risk_level TEXT, cluster_id INTEGER, cluster_name TEXT,
                top_career TEXT, top_career_fit REAL, full_profile_json TEXT,
                created_at TEXT DEFAULT (datetime('now')),
                updated_at TEXT DEFAULT (datetime('now'))
            );
            CREATE TABLE IF NOT EXISTS career_results (
                id INTEGER PRIMARY KEY AUTOINCREMENT, student_id TEXT NOT NULL,
                career_title TEXT NOT NULL, fit_score REAL, ml_score REAL,
                formula_score REAL, rank INTEGER,
                analysed_at TEXT DEFAULT (datetime('now')),
                FOREIGN KEY (student_id) REFERENCES students(student_id) ON DELETE CASCADE
            );
            CREATE TABLE IF NOT EXISTS batches (
                batch_id TEXT PRIMARY KEY, institute TEXT, uploaded_by TEXT,
                student_count INTEGER, cohort_stats_json TEXT, dept_report_json TEXT,
                raw_data_json TEXT, created_at TEXT DEFAULT (datetime('now'))
            );
            CREATE TABLE IF NOT EXISTS swot_cache (
                student_id TEXT PRIMARY KEY, swot_json TEXT,
                generated_at TEXT DEFAULT (datetime('now')),
                FOREIGN KEY (student_id) REFERENCES students(student_id) ON DELETE CASCADE
            );
            CREATE INDEX IF NOT EXISTS idx_students_name    ON students(name);
            CREATE INDEX IF NOT EXISTS idx_students_college ON students(college);
            CREATE INDEX IF NOT EXISTS idx_students_branch  ON students(branch);
            """)

    # ── Student CRUD ──────────────────────────────────────────────────────
    def save_student(self, profile: dict, career_results: list = None,
                     cluster: dict = None) -> bool:
        try:
            skills     = profile.get("skills", {})
            interests  = profile.get("interests", [])
            activities = {k: profile.get(k, 0) for k in
                          ["projects","internships","hackathons","certifications","extracurriculars"]}
            top_career     = career_results[0]["title"] if career_results else ""
            top_career_fit = career_results[0]["fit"]   if career_results else 0.0

            with self._conn() as conn:
                conn.execute("""
                    INSERT INTO students
                    (student_id,name,college,branch,year,semester,cgpa,backlogs,
                     academic_trend,effort,career_goal,timeline,skills_json,
                     interests_json,activities_json,intelligence_score,risk_level,
                     cluster_id,cluster_name,top_career,top_career_fit,full_profile_json,updated_at)
                    VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)
                    ON CONFLICT(student_id) DO UPDATE SET
                        name=excluded.name, college=excluded.college,
                        branch=excluded.branch, cgpa=excluded.cgpa,
                        intelligence_score=excluded.intelligence_score,
                        risk_level=excluded.risk_level,
                        cluster_id=excluded.cluster_id, cluster_name=excluded.cluster_name,
                        top_career=excluded.top_career, top_career_fit=excluded.top_career_fit,
                        full_profile_json=excluded.full_profile_json, updated_at=excluded.updated_at
                """, (
                    str(profile.get("student_id","")), str(profile.get("name","")),
                    str(profile.get("college","")), str(profile.get("branch","")),
                    str(profile.get("year","")), int(profile.get("semester",1)),
                    float(profile.get("cgpa",0)), int(profile.get("backlogs",0)),
                    str(profile.get("academic_trend","Stable")), int(profile.get("effort",3)),
                    str(profile.get("career_goal","")), str(profile.get("timeline","")),
                    json.dumps(skills), json.dumps(interests), json.dumps(activities),
                    float(profile.get("intelligence_score",0)), str(profile.get("risk_level","Low")),
                    int(cluster.get("cluster_id",0)) if cluster else 0,
                    str(cluster.get("name","")) if cluster else "",
                    top_career, float(top_career_fit),
                    json.dumps(profile, default=str), datetime.now().isoformat(),
                ))
                if career_results:
                    conn.execute("DELETE FROM career_results WHERE student_id=?",
                                 (profile["student_id"],))
                    conn.executemany("""
                        INSERT INTO career_results
                        (student_id,career_title,fit_score,ml_score,formula_score,rank)
                        VALUES (?,?,?,?,?,?)
                    """, [(profile["student_id"], str(c["title"]), float(c["fit"]),
                           float(c.get("ml_score",0)), float(c.get("formula_score",0)), int(i+1))
                          for i, c in enumerate(career_results[:8])])
            return True
        except Exception as e:
            print(f"SQLite save_student error: {e}")
            return False

    def get_student(self, student_id: str) -> Optional[dict]:
        try:
            with self._conn() as conn:
                row = conn.execute(
                    "SELECT full_profile_json FROM students WHERE student_id=?",
                    (student_id,)).fetchone()
                if row:
                    return json.loads(row["full_profile_json"])
        except Exception as e:
            print(f"SQLite get_student error: {e}")
        return None

    def search_students(self, query: str) -> List[dict]:
        try:
            q = f"%{query.lower()}%"
            with self._conn() as conn:
                rows = conn.execute("""
                    SELECT student_id,name,college,branch,cgpa,intelligence_score,
                           top_career,top_career_fit,cluster_name
                    FROM students WHERE LOWER(name) LIKE ? OR LOWER(student_id) LIKE ?
                    ORDER BY intelligence_score DESC LIMIT 20
                """, (q, q)).fetchall()
                return [dict(r) for r in rows]
        except Exception as e:
            print(f"SQLite search error: {e}")
            return []

    def get_all_students(self) -> List[dict]:
        try:
            with self._conn() as conn:
                rows = conn.execute("""
                    SELECT student_id,name,college,branch,cgpa,intelligence_score,
                           top_career,top_career_fit,risk_level,cluster_name,effort
                    FROM students ORDER BY intelligence_score DESC
                """).fetchall()
                return [dict(r) for r in rows]
        except Exception as e:
            print(f"SQLite get_all error: {e}")
            return []

    def get_student_career_results(self, student_id: str) -> List[dict]:
        try:
            with self._conn() as conn:
                rows = conn.execute("""
                    SELECT career_title as title, fit_score as fit,
                           ml_score, formula_score, rank
                    FROM career_results WHERE student_id=? ORDER BY rank
                """, (student_id,)).fetchall()
                return [dict(r) for r in rows]
        except Exception:
            return []

    def delete_student(self, student_id: str) -> bool:
        try:
            with self._conn() as conn:
                conn.execute("DELETE FROM students WHERE student_id=?", (student_id,))
            return True
        except Exception:
            return False

    def save_swot(self, student_id: str, swot: dict):
        try:
            with self._conn() as conn:
                conn.execute("""
                    INSERT INTO swot_cache (student_id, swot_json, generated_at)
                    VALUES (?,?,?)
                    ON CONFLICT(student_id) DO UPDATE SET
                        swot_json=excluded.swot_json, generated_at=excluded.generated_at
                """, (student_id, json.dumps(swot), datetime.now().isoformat()))
        except Exception as e:
            print(f"SQLite save_swot error: {e}")

    def get_swot(self, student_id: str) -> Optional[dict]:
        try:
            with self._conn() as conn:
                row = conn.execute(
                    "SELECT swot_json FROM swot_cache WHERE student_id=?",
                    (student_id,)).fetchone()
                if row:
                    return json.loads(row["swot_json"])
        except Exception:
            pass
        return None

    def save_batch(self, df: pd.DataFrame, cohort_stats: dict,
                   dept_report: pd.DataFrame, institute: str = "") -> str:
        try:
            batch_id = hashlib.md5(
                f"{institute}{datetime.now().isoformat()}".encode()
            ).hexdigest()[:12]
            with self._conn() as conn:
                conn.execute("""
                    INSERT INTO batches
                    (batch_id,institute,student_count,cohort_stats_json,
                     dept_report_json,raw_data_json,created_at)
                    VALUES (?,?,?,?,?,?,?)
                """, (batch_id, institute, len(df),
                      json.dumps(cohort_stats, default=str),
                      dept_report.to_json() if isinstance(dept_report, pd.DataFrame) else "{}",
                      df.to_json(orient="records"), datetime.now().isoformat()))
            return batch_id
        except Exception as e:
            print(f"SQLite save_batch error: {e}")
            return ""

    def get_latest_batch(self) -> Optional[dict]:
        try:
            with self._conn() as conn:
                row = conn.execute(
                    "SELECT * FROM batches ORDER BY created_at DESC LIMIT 1"
                ).fetchone()
                if row:
                    result = dict(row)
                    result["cohort_stats"] = json.loads(result["cohort_stats_json"] or "{}")
                    result["df"]           = pd.read_json(result["raw_data_json"])
                    result["dept_report"]  = pd.read_json(result["dept_report_json"])
                    return result
        except Exception as e:
            print(f"SQLite get_latest_batch error: {e}")
        return None

    def get_all_batches(self) -> List[dict]:
        try:
            with self._conn() as conn:
                rows = conn.execute("""
                    SELECT batch_id,institute,student_count,created_at
                    FROM batches ORDER BY created_at DESC
                """).fetchall()
                return [dict(r) for r in rows]
        except Exception:
            return []

    def get_live_cohort_stats(self) -> dict:
        try:
            with self._conn() as conn:
                row = conn.execute("""
                    SELECT COUNT(*) as total, AVG(cgpa) as avg_cgpa,
                           AVG(intelligence_score) as avg_intel,
                           SUM(CASE WHEN risk_level='High' THEN 1 ELSE 0 END) as high_risk,
                           SUM(CASE WHEN risk_level IN ('High','Medium') THEN 1 ELSE 0 END) as at_risk
                    FROM students
                """).fetchone()
                if row:
                    return {
                        "total_students": int(row["total"]),
                        "cgpa_mean":      round(float(row["avg_cgpa"] or 0), 2),
                        "intel_mean":     round(float(row["avg_intel"] or 0), 1),
                        "risk_high":      int(row["high_risk"]),
                        "at_risk":        int(row["at_risk"]),
                    }
        except Exception:
            pass
        return {}

    def get_stats(self) -> dict:
        try:
            with self._conn() as conn:
                students = conn.execute("SELECT COUNT(*) FROM students").fetchone()[0]
                batches  = conn.execute("SELECT COUNT(*) FROM batches").fetchone()[0]
                size_kb  = round(os.path.getsize(self.db_path) / 1024, 1)
                return {"students": students, "batches": batches,
                        "size_kb": size_kb, "db_path": self.db_path,
                        "backend": "SQLite"}
        except Exception:
            return {"backend": "SQLite"}

    def clear_all(self):
        with self._conn() as conn:
            conn.executescript("""
                DELETE FROM career_results; DELETE FROM swot_cache;
                DELETE FROM students; DELETE FROM batches;
            """)


# ══════════════════════════════════════════════════════════════════════════
#  SUPABASE / POSTGRESQL BACKEND
# ══════════════════════════════════════════════════════════════════════════

class SupabaseDB:
    """
    PostgreSQL-backed persistent storage using Supabase.
    Same public API as SpectraDB — drop-in replacement.
    """

    def __init__(self, db_url: str):
        self.db_url  = db_url
        self.backend = "supabase"
        self._init_schema()

    def _conn(self):
        import psycopg2
        import psycopg2.extras
        import streamlit as st
        
        # Dynamically fetch the latest URL from secrets in case it was updated while the app is running
        current_url = st.secrets.get("supabase", {}).get("db_url", self.db_url)
        
        conn = psycopg2.connect(current_url, connect_timeout=10)
        conn.autocommit = False
        return conn

    def _init_schema(self):
        """Create tables if they don't exist (idempotent)."""
        ddl = """
        CREATE TABLE IF NOT EXISTS students (
            student_id TEXT PRIMARY KEY, name TEXT NOT NULL, college TEXT,
            branch TEXT, year TEXT, semester INTEGER, cgpa REAL,
            backlogs INTEGER DEFAULT 0, academic_trend TEXT, effort INTEGER,
            career_goal TEXT, timeline TEXT, skills_json TEXT,
            interests_json TEXT, activities_json TEXT, intelligence_score REAL,
            risk_level TEXT, cluster_id INTEGER, cluster_name TEXT,
            top_career TEXT, top_career_fit REAL, full_profile_json TEXT,
            created_at TIMESTAMPTZ DEFAULT NOW(), updated_at TIMESTAMPTZ DEFAULT NOW()
        );
        CREATE TABLE IF NOT EXISTS career_results (
            id SERIAL PRIMARY KEY, student_id TEXT NOT NULL
                REFERENCES students(student_id) ON DELETE CASCADE,
            career_title TEXT NOT NULL, fit_score REAL, ml_score REAL,
            formula_score REAL, rank INTEGER, analysed_at TIMESTAMPTZ DEFAULT NOW()
        );
        CREATE TABLE IF NOT EXISTS batches (
            batch_id TEXT PRIMARY KEY, institute TEXT, uploaded_by TEXT,
            student_count INTEGER, cohort_stats_json TEXT, dept_report_json TEXT,
            raw_data_json TEXT, created_at TIMESTAMPTZ DEFAULT NOW()
        );
        CREATE TABLE IF NOT EXISTS swot_cache (
            student_id TEXT PRIMARY KEY
                REFERENCES students(student_id) ON DELETE CASCADE,
            swot_json TEXT, generated_at TIMESTAMPTZ DEFAULT NOW()
        );
        CREATE INDEX IF NOT EXISTS idx_students_name    ON students(name);
        CREATE INDEX IF NOT EXISTS idx_students_college ON students(college);
        CREATE INDEX IF NOT EXISTS idx_students_branch  ON students(branch);
        """
        try:
            with self._conn() as conn:
                with conn.cursor() as cur:
                    cur.execute(ddl)
                conn.commit()
        except Exception as e:
            print(f"Supabase schema init error: {e}")

    # ── helpers ───────────────────────────────────────────────────────────
    @staticmethod
    def _rows_to_dicts(cursor) -> List[dict]:
        cols = [d[0] for d in cursor.description]
        return [dict(zip(cols, row)) for row in cursor.fetchall()]

    # ── Student CRUD ──────────────────────────────────────────────────────
    def save_student(self, profile: dict, career_results: list = None,
                     cluster: dict = None) -> bool:
        try:
            skills     = profile.get("skills", {})
            interests  = profile.get("interests", [])
            activities = {k: profile.get(k, 0) for k in
                          ["projects","internships","hackathons","certifications","extracurriculars"]}
            top_career     = career_results[0]["title"] if career_results else ""
            top_career_fit = career_results[0]["fit"]   if career_results else 0.0

            with self._conn() as conn:
                with conn.cursor() as cur:
                    cur.execute("""
                        INSERT INTO students
                        (student_id,name,college,branch,year,semester,cgpa,backlogs,
                         academic_trend,effort,career_goal,timeline,skills_json,
                         interests_json,activities_json,intelligence_score,risk_level,
                         cluster_id,cluster_name,top_career,top_career_fit,
                         full_profile_json,updated_at)
                        VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
                        ON CONFLICT (student_id) DO UPDATE SET
                            name=EXCLUDED.name, college=EXCLUDED.college,
                            branch=EXCLUDED.branch, cgpa=EXCLUDED.cgpa,
                            intelligence_score=EXCLUDED.intelligence_score,
                            risk_level=EXCLUDED.risk_level,
                            cluster_id=EXCLUDED.cluster_id, cluster_name=EXCLUDED.cluster_name,
                            top_career=EXCLUDED.top_career, top_career_fit=EXCLUDED.top_career_fit,
                            full_profile_json=EXCLUDED.full_profile_json,
                            updated_at=EXCLUDED.updated_at
                    """, (
                        str(profile.get("student_id","")), str(profile.get("name","")),
                        str(profile.get("college","")), str(profile.get("branch","")),
                        str(profile.get("year","")), int(profile.get("semester",1)),
                        float(profile.get("cgpa",0)), int(profile.get("backlogs",0)),
                        str(profile.get("academic_trend","Stable")), int(profile.get("effort",3)),
                        str(profile.get("career_goal","")), str(profile.get("timeline","")),
                        json.dumps(skills), json.dumps(interests), json.dumps(activities),
                        float(profile.get("intelligence_score",0)), str(profile.get("risk_level","Low")),
                        int(cluster.get("cluster_id",0)) if cluster else 0,
                        str(cluster.get("name","")) if cluster else "",
                        top_career, float(top_career_fit),
                        json.dumps(profile, default=str), datetime.now().isoformat(),
                    ))
                    if career_results:
                        cur.execute("DELETE FROM career_results WHERE student_id=%s",
                                    (profile["student_id"],))
                        cur.executemany("""
                            INSERT INTO career_results
                            (student_id,career_title,fit_score,ml_score,formula_score,rank)
                            VALUES (%s,%s,%s,%s,%s,%s)
                        """, [(profile["student_id"], str(c["title"]), float(c["fit"]),
                               float(c.get("ml_score",0)), float(c.get("formula_score",0)), int(i+1))
                              for i, c in enumerate(career_results[:8])])
                conn.commit()
            return True
        except Exception as e:
            print(f"Supabase save_student error: {e}")
            return False

    def get_student(self, student_id: str) -> Optional[dict]:
        try:
            with self._conn() as conn:
                with conn.cursor() as cur:
                    cur.execute(
                        "SELECT full_profile_json FROM students WHERE student_id=%s",
                        (student_id,))
                    row = cur.fetchone()
                    if row:
                        return json.loads(row[0])
        except Exception as e:
            print(f"Supabase get_student error: {e}")
        return None

    def search_students(self, query: str) -> List[dict]:
        try:
            q = f"%{query.lower()}%"
            with self._conn() as conn:
                with conn.cursor() as cur:
                    cur.execute("""
                        SELECT student_id,name,college,branch,cgpa,intelligence_score,
                               top_career,top_career_fit,cluster_name
                        FROM students
                        WHERE LOWER(name) LIKE %s OR LOWER(student_id) LIKE %s
                        ORDER BY intelligence_score DESC LIMIT 20
                    """, (q, q))
                    return self._rows_to_dicts(cur)
        except Exception as e:
            print(f"Supabase search error: {e}")
            return []

    def get_all_students(self) -> List[dict]:
        try:
            with self._conn() as conn:
                with conn.cursor() as cur:
                    cur.execute("""
                        SELECT student_id,name,college,branch,cgpa,intelligence_score,
                               top_career,top_career_fit,risk_level,cluster_name,effort
                        FROM students ORDER BY intelligence_score DESC
                    """)
                    return self._rows_to_dicts(cur)
        except Exception as e:
            print(f"Supabase get_all error: {e}")
            return []

    def get_student_career_results(self, student_id: str) -> List[dict]:
        try:
            with self._conn() as conn:
                with conn.cursor() as cur:
                    cur.execute("""
                        SELECT career_title as title, fit_score as fit,
                               ml_score, formula_score, rank
                        FROM career_results WHERE student_id=%s ORDER BY rank
                    """, (student_id,))
                    return self._rows_to_dicts(cur)
        except Exception:
            return []

    def delete_student(self, student_id: str) -> bool:
        try:
            with self._conn() as conn:
                with conn.cursor() as cur:
                    cur.execute("DELETE FROM students WHERE student_id=%s", (student_id,))
                conn.commit()
            return True
        except Exception:
            return False

    def save_swot(self, student_id: str, swot: dict):
        try:
            with self._conn() as conn:
                with conn.cursor() as cur:
                    cur.execute("""
                        INSERT INTO swot_cache (student_id, swot_json, generated_at)
                        VALUES (%s, %s, %s)
                        ON CONFLICT (student_id) DO UPDATE SET
                            swot_json=EXCLUDED.swot_json,
                            generated_at=EXCLUDED.generated_at
                    """, (student_id, json.dumps(swot), datetime.now().isoformat()))
                conn.commit()
        except Exception as e:
            print(f"Supabase save_swot error: {e}")

    def get_swot(self, student_id: str) -> Optional[dict]:
        try:
            with self._conn() as conn:
                with conn.cursor() as cur:
                    cur.execute(
                        "SELECT swot_json FROM swot_cache WHERE student_id=%s",
                        (student_id,))
                    row = cur.fetchone()
                    if row:
                        return json.loads(row[0])
        except Exception:
            pass
        return None

    def save_batch(self, df: pd.DataFrame, cohort_stats: dict,
                   dept_report: pd.DataFrame, institute: str = "") -> str:
        try:
            batch_id = hashlib.md5(
                f"{institute}{datetime.now().isoformat()}".encode()
            ).hexdigest()[:12]
            with self._conn() as conn:
                with conn.cursor() as cur:
                    cur.execute("""
                        INSERT INTO batches
                        (batch_id,institute,student_count,cohort_stats_json,
                         dept_report_json,raw_data_json,created_at)
                        VALUES (%s,%s,%s,%s,%s,%s,%s)
                    """, (batch_id, institute, len(df),
                          json.dumps(cohort_stats, default=str),
                          dept_report.to_json() if isinstance(dept_report, pd.DataFrame) else "{}",
                          df.to_json(orient="records"), datetime.now().isoformat()))
                conn.commit()
            return batch_id
        except Exception as e:
            print(f"Supabase save_batch error: {e}")
            return ""

    def get_latest_batch(self) -> Optional[dict]:
        try:
            with self._conn() as conn:
                with conn.cursor() as cur:
                    cur.execute("SELECT * FROM batches ORDER BY created_at DESC LIMIT 1")
                    row = cur.fetchone()
                    if row:
                        cols   = [d[0] for d in cur.description]
                        result = dict(zip(cols, row))
                        result["cohort_stats"] = json.loads(result["cohort_stats_json"] or "{}")
                        result["df"]           = pd.read_json(result["raw_data_json"])
                        result["dept_report"]  = pd.read_json(result["dept_report_json"])
                        return result
        except Exception as e:
            print(f"Supabase get_latest_batch error: {e}")
        return None

    def get_all_batches(self) -> List[dict]:
        try:
            with self._conn() as conn:
                with conn.cursor() as cur:
                    cur.execute("""
                        SELECT batch_id,institute,student_count,created_at
                        FROM batches ORDER BY created_at DESC
                    """)
                    return self._rows_to_dicts(cur)
        except Exception:
            return []

    def get_live_cohort_stats(self) -> dict:
        try:
            with self._conn() as conn:
                with conn.cursor() as cur:
                    cur.execute("""
                        SELECT
                            COUNT(*)                                          AS total,
                            AVG(cgpa)                                         AS avg_cgpa,
                            AVG(intelligence_score)                           AS avg_intel,
                            SUM(CASE WHEN risk_level='High' THEN 1 ELSE 0 END) AS high_risk,
                            SUM(CASE WHEN risk_level IN ('High','Medium') THEN 1 ELSE 0 END) AS at_risk
                        FROM students
                    """)
                    row = cur.fetchone()
                    if row:
                        return {
                            "total_students": int(row[0] or 0),
                            "cgpa_mean":      round(float(row[1] or 0), 2),
                            "intel_mean":     round(float(row[2] or 0), 1),
                            "risk_high":      int(row[3] or 0),
                            "at_risk":        int(row[4] or 0),
                        }
        except Exception as e:
            print(f"Supabase cohort_stats error: {e}")
        return {}

    def get_stats(self) -> dict:
        try:
            with self._conn() as conn:
                with conn.cursor() as cur:
                    cur.execute("SELECT COUNT(*) FROM students")
                    students = cur.fetchone()[0]
                    cur.execute("SELECT COUNT(*) FROM batches")
                    batches = cur.fetchone()[0]
            return {"students": students, "batches": batches,
                    "backend": "Supabase ☁️",
                    "project": "rcrpxjijpscgcuekhdqn.supabase.co"}
        except Exception:
            return {"backend": "Supabase ☁️"}

    def clear_all(self):
        try:
            with self._conn() as conn:
                with conn.cursor() as cur:
                    cur.execute("DELETE FROM career_results")
                    cur.execute("DELETE FROM swot_cache")
                    cur.execute("DELETE FROM students")
                    cur.execute("DELETE FROM batches")
                conn.commit()
        except Exception as e:
            print(f"Supabase clear_all error: {e}")


# ══════════════════════════════════════════════════════════════════════════
#  AUTO-SELECT BACKEND (singleton)
# ══════════════════════════════════════════════════════════════════════════

def _create_db():
    """
    Returns Supabase backend if credentials are configured,
    otherwise falls back to SQLite.
    """
    try:
        import streamlit as st
        cfg = st.secrets.get("supabase", {})
        db_url = cfg.get("db_url", "")
        if db_url:
            instance = SupabaseDB(db_url)
            # Quick connectivity test
            instance.get_stats()
            print("✅ Connected to Supabase PostgreSQL ☁️")
            return instance
    except Exception as e:
        print(f"⚠️  Supabase unavailable ({e}) — falling back to SQLite")

    print("📁 Using SQLite (local)")
    return SpectraDB()


db = _create_db()
