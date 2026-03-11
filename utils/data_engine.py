"""
utils/data_engine.py — Data Ingestion, Validation & Preprocessing Pipeline

Handles:
- Reading uploaded Excel/CSV student data
- Schema validation with detailed error reporting
- Feature engineering (derived features)
- Normalisation / encoding for ML models
- Generating the internal student record format
"""
from __future__ import annotations
import pandas as pd
import numpy as np
from typing import Tuple, List, Dict, Any

# ── Expected schema ────────────────────────────────────────────────────────
REQUIRED_COLUMNS = [
    "Student ID", "Full Name", "Department / Branch",
    "CGPA (0–10)", "Technical Skills", "Analytical Thinking",
    "Effort Level (1–5)", "Career Goal", "Academic Trend",
]

OPTIONAL_COLUMNS = {
    "College / Institute":   "Unknown Institute",
    "Year of Study":         "2nd Year",
    "Current Semester":      4,
    "Active Backlogs":       0,
    "Creative Thinking":     50,
    "Communication":         55,
    "Leadership":            45,
    "Consistency":           60,
    "Primary Interest":      "Programming",
    "Secondary Interest":    "",
    "Tertiary Interest":     "",
    "Projects Completed":    0,
    "Internships Done":      0,
    "Hackathons":            0,
    "Certifications":        0,
    "Extracurriculars":      0,
    "Target Timeline":       "1–2 years",
    "10th % / GPA":          75,
    "12th % / GPA":          75,
}

# Column alias map (human-readable → internal key)
COL_ALIASES = {
    "Student ID":                "student_id",
    "Full Name":                 "name",
    "College / Institute":   "college",
    "Department / Branch":   "branch",
    "Year of Study":         "year",
    "Current Semester":      "semester",
    "CGPA (0–10)":           "cgpa",
    "Active Backlogs":           "backlogs",
    "Academic Trend":        "academic_trend",
    "10th % / GPA":              "grade_10",
    "12th % / GPA":              "grade_12",
    "Technical Skills":      "skill_technical",
    "Analytical Thinking":   "skill_analytical",
    "Creative Thinking":         "skill_creative",
    "Communication":             "skill_communication",
    "Leadership":                "skill_leadership",
    "Consistency":               "skill_consistency",
    "Primary Interest":      "interest_1",
    "Secondary Interest":        "interest_2",
    "Tertiary Interest":         "interest_3",
    "Projects Completed":    "projects",
    "Internships Done":          "internships",
    "Hackathons":                "hackathons",
    "Certifications":            "certifications",
    "Extracurriculars":          "extracurriculars",
    "Effort Level (1–5)":    "effort",
    "Career Goal":           "career_goal",
    "Target Timeline":           "timeline",
}

SKILL_COLS = ["skill_technical", "skill_analytical", "skill_creative",
              "skill_communication", "skill_leadership", "skill_consistency"]

INTEREST_MAP = {
    "ai/ml": "ai_ml", "ai / ml": "ai_ml", "machine learning": "ai_ml",
    "programming": "programming", "coding": "programming",
    "mathematics": "mathematics", "maths": "mathematics",
    "research": "research",
    "product design": "product_design", "design": "product_design",
    "management": "management", "leadership": "management",
    "core engineering": "core_engg", "core": "core_engg",
    "finance": "finance", "quant": "finance",
    "data science": "ai_ml", "data": "ai_ml",
    "embedded": "core_engg", "electronics": "core_engg",
}


# ── Public API ─────────────────────────────────────────────────────────────

def load_file(file_obj) -> Tuple[pd.DataFrame | None, List[str]]:
    """
    Load an uploaded Streamlit file object (Excel or CSV).
    Auto-detects the header row (scans first 10 rows for 'Student ID').
    Returns (DataFrame, list_of_errors).
    """
    errors = []
    try:
        name = getattr(file_obj, "name", "") if hasattr(file_obj, "name") else ""

        if str(name).endswith(".csv"):
            df = pd.read_csv(file_obj)
        else:
            # Try reading 'Student Data' sheet; fall back to first sheet
            try:
                raw = pd.read_excel(file_obj, sheet_name="Student Data", header=None)
            except Exception:
                raw = pd.read_excel(file_obj, header=None)

            # Auto-detect header row: find the row containing 'Student ID'
            header_row = 0
            for i in range(min(10, len(raw))):
                row_vals = [str(v).strip().lower() for v in raw.iloc[i].values]
                if any("student id" in v for v in row_vals):
                    header_row = i
                    break

            # Re-read with correct header row
            try:
                df = pd.read_excel(file_obj, sheet_name="Student Data", header=header_row)
            except Exception:
                df = pd.read_excel(file_obj, header=header_row)

        # ── Normalise column names: strip [R] markers, extra spaces ──────
        df.columns = [_normalise_col(c) for c in df.columns]

        # Drop rows where Student ID is blank (title/spacer rows)
        if "Student ID" in df.columns:
            df = df[df["Student ID"].notna() & (df["Student ID"].astype(str).str.strip() != "")]

        return df.reset_index(drop=True), errors

    except Exception as e:
        errors.append(f"File read error: {e}")
        return None, errors


def _normalise_col(col_name: str) -> str:
    """Strip [R] markers, extra whitespace from column headers."""
    import re
    s = str(col_name).strip()
    s = re.sub(r"\s*\[R\]\s*", "", s)   # remove [R]
    s = re.sub(r"\s+", " ", s).strip()      # collapse whitespace
    return s


def validate(df: pd.DataFrame) -> Tuple[bool, List[str], List[str]]:
    """
    Validate DataFrame against expected schema.
    Returns (is_valid, errors, warnings).
    """
    errors, warnings = [], []

    # Check required columns
    for col in REQUIRED_COLUMNS:
        if col not in df.columns:
            # Try fuzzy match
            close = [c for c in df.columns if col.replace(" [R]","").lower() in c.lower()]
            if close:
                warnings.append(f"Column '{col}' not found — using '{close[0]}' instead")
            else:
                errors.append(f"Required column missing: '{col}'")

    if errors:
        return False, errors, warnings

    # Value range checks
    if "CGPA (0–10)" in df.columns:
        invalid_cgpa = df[~df["CGPA (0–10)"].between(0, 10, inclusive="both")]["Student ID"].tolist()
        if invalid_cgpa:
            warnings.append(f"CGPA out of 0–10 range for IDs: {invalid_cgpa[:5]}")

    for skill_col in ["Technical Skills", "Analytical Thinking"]:
        if skill_col in df.columns:
            invalid = df[~df[skill_col].between(0, 100)]["Student ID"].tolist()
            if invalid:
                warnings.append(f"Skill score out of 0–100 for '{skill_col}': {invalid[:5]}")

    if "Effort Level (1–5)" in df.columns:
        invalid_effort = df[~df["Effort Level (1–5)"].between(1, 5)]["Student ID"].tolist()
        if invalid_effort:
            warnings.append(f"Effort out of 1–5 range for IDs: {invalid_effort[:5]}")

    return True, errors, warnings


def preprocess(df: pd.DataFrame) -> pd.DataFrame:
    """
    Full preprocessing pipeline:
    1. Fill missing optional columns with defaults
    2. Rename to internal keys
    3. Type coercion
    4. Feature engineering
    5. Normalisation
    Returns clean DataFrame with internal column names.
    """
    df = df.copy()

    # Fill missing optional columns
    for col, default in OPTIONAL_COLUMNS.items():
        if col not in df.columns:
            df[col] = default
        else:
            df[col] = df[col].fillna(default)

    # Rename columns to internal keys
    rename_map = {k: v for k, v in COL_ALIASES.items() if k in df.columns}
    df = df.rename(columns=rename_map)

    # Type coercion
    num_cols = ["cgpa", "backlogs", "grade_10", "grade_12", "projects",
                "internships", "hackathons", "certifications", "extracurriculars",
                "effort", "semester"] + SKILL_COLS
    for col in num_cols:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce").fillna(0)

    # Clamp ranges
    df["cgpa"]   = df["cgpa"].clip(0, 10)
    df["effort"] = df["effort"].clip(1, 5)
    for sc in SKILL_COLS:
        if sc in df.columns:
            df[sc] = df[sc].clip(0, 100)

    # ── Feature engineering ────────────────────────────────────────────
    df = _engineer_features(df)

    return df


def _engineer_features(df: pd.DataFrame) -> pd.DataFrame:
    """Derive higher-level features used by ML models."""

    # Skill average
    avail_skills = [s for s in SKILL_COLS if s in df.columns]
    df["skill_avg"]    = df[avail_skills].mean(axis=1).round(2)
    df["skill_spread"] = df[avail_skills].std(axis=1).round(2)  # specialisation indicator

    # STEM score (technical + analytical weighted)
    df["stem_score"] = (
        df.get("skill_technical",   pd.Series(50, index=df.index)) * 0.5 +
        df.get("skill_analytical",  pd.Series(50, index=df.index)) * 0.5
    ).round(2)

    # Soft skill score
    df["soft_score"] = (
        df.get("skill_communication", pd.Series(50, index=df.index)) * 0.4 +
        df.get("skill_leadership",    pd.Series(50, index=df.index)) * 0.3 +
        df.get("skill_creative",      pd.Series(50, index=df.index)) * 0.3
    ).round(2)

    # Activity index (weighted portfolio score)
    df["activity_index"] = (
        df.get("projects",        pd.Series(0, index=df.index)) * 3.0 +
        df.get("internships",     pd.Series(0, index=df.index)) * 4.0 +
        df.get("hackathons",      pd.Series(0, index=df.index)) * 2.0 +
        df.get("certifications",  pd.Series(0, index=df.index)) * 1.5 +
        df.get("extracurriculars",pd.Series(0, index=df.index)) * 1.0
    ).round(2)

    # Normalised activity (cap at 30)
    df["activity_score"] = (df["activity_index"].clip(0, 30) / 30 * 100).round(2)

    # Academic score (CGPA * 10 → 0-100 scale)
    df["academic_score"] = (df["cgpa"] / 10 * 100).round(2)

    # Effort score (1-5 → 0-100)
    df["effort_score"] = ((df["effort"] - 1) / 4 * 100).round(2)

    # Risk flags
    df["risk_academic"]  = (df["cgpa"] < 6.0).astype(int)
    df["risk_effort"]    = (df["effort"] <= 2).astype(int)
    df["risk_backlogs"]  = (df.get("backlogs", pd.Series(0, index=df.index)) > 2).astype(int)
    df["risk_score"]     = (df["risk_academic"] + df["risk_effort"] + df["risk_backlogs"])
    df["risk_level"]     = pd.cut(df["risk_score"],
                                  bins=[-1, 0, 1, 3],
                                  labels=["Low", "Medium", "High"])

    # Composite intelligence score
    df["intelligence_score"] = (
        df["academic_score"]  * 0.30 +
        df["skill_avg"]       * 0.40 +
        df["effort_score"]    * 0.20 +
        df["activity_score"]  * 0.10
    ).round(1)

    # Interest normalisation
    for col in ["interest_1", "interest_2", "interest_3"]:
        if col in df.columns:
            df[col] = df[col].str.lower().str.strip().map(
                lambda x: INTEREST_MAP.get(x, x) if isinstance(x, str) else ""
            )

    # Trend encoding
    trend_map = {"Improving": 1, "Stable": 0, "Declining": -1}
    if "academic_trend" in df.columns:
        df["trend_score"] = df["academic_trend"].map(trend_map).fillna(0)

    return df


def df_to_profile(row: pd.Series) -> dict:
    """Convert a preprocessed DataFrame row to SPECTRA profile dict."""
    skills = {
        "technical":     float(row.get("skill_technical", 50)),
        "analytical":    float(row.get("skill_analytical", 50)),
        "creative":      float(row.get("skill_creative", 50)),
        "communication": float(row.get("skill_communication", 55)),
        "leadership":    float(row.get("skill_leadership", 45)),
        "consistency":   float(row.get("skill_consistency", 60)),
    }
    interests = [
        i for i in [row.get("interest_1",""), row.get("interest_2",""), row.get("interest_3","")]
        if i and i != "nan"
    ]
    return {
        "name":           str(row.get("name", "Unknown")),
        "student_id":     str(row.get("student_id", "")),
        "college":        str(row.get("college", "")),
        "branch":         str(row.get("branch", "")),
        "year":           str(row.get("year", "")),
        "semester":       int(row.get("semester", 1)),
        "cgpa":           float(row.get("cgpa", 0)),
        "backlogs":       int(row.get("backlogs", 0)),
        "academic_trend": str(row.get("academic_trend", "Stable")),
        "skills":         skills,
        "interests":      interests,
        "projects":       int(row.get("projects", 0)),
        "internships":    int(row.get("internships", 0)),
        "hackathons":     int(row.get("hackathons", 0)),
        "certifications": int(row.get("certifications", 0)),
        "extracurriculars": int(row.get("extracurriculars", 0)),
        "effort":         int(row.get("effort", 3)),
        "career_goal":    str(row.get("career_goal", "")),
        "timeline":       str(row.get("timeline", "")),
        # Derived
        "intelligence_score": float(row.get("intelligence_score", 0)),
        "risk_level":         str(row.get("risk_level", "Low")),
        "activity_score":     float(row.get("activity_score", 0)),
        "stem_score":         float(row.get("stem_score", 0)),
        "soft_score":         float(row.get("soft_score", 0)),
    }


def get_feature_vector(profile: dict) -> np.ndarray:
    """
    Convert a profile dict to a numeric feature vector for ML models.
    Order must match training data exactly.
    """
    skills = profile.get("skills", {})
    interests = profile.get("interests", [])

    interest_flags = {
        "ai_ml":          int("ai_ml"        in interests),
        "programming":    int("programming"  in interests),
        "mathematics":    int("mathematics"  in interests),
        "research":       int("research"     in interests),
        "product_design": int("product_design" in interests),
        "management":     int("management"   in interests),
        "core_engg":      int("core_engg"    in interests),
        "finance":        int("finance"      in interests),
    }

    return np.array([
        profile.get("cgpa", 0) / 10,
        profile.get("effort", 3) / 5,
        skills.get("technical", 50) / 100,
        skills.get("analytical", 50) / 100,
        skills.get("creative", 50) / 100,
        skills.get("communication", 50) / 100,
        skills.get("leadership", 50) / 100,
        skills.get("consistency", 50) / 100,
        min(profile.get("projects", 0), 10) / 10,
        min(profile.get("internships", 0), 5) / 5,
        min(profile.get("hackathons", 0), 10) / 10,
        min(profile.get("certifications", 0), 10) / 10,
        min(profile.get("extracurriculars", 0), 10) / 10,
        interest_flags["ai_ml"],
        interest_flags["programming"],
        interest_flags["mathematics"],
        interest_flags["research"],
        interest_flags["product_design"],
        interest_flags["management"],
        interest_flags["core_engg"],
        interest_flags["finance"],
    ], dtype=np.float32)


FEATURE_NAMES = [
    "cgpa_norm", "effort_norm",
    "skill_technical", "skill_analytical", "skill_creative",
    "skill_communication", "skill_leadership", "skill_consistency",
    "projects_norm", "internships_norm", "hackathons_norm",
    "certifications_norm", "extracurriculars_norm",
    "interest_ai_ml", "interest_programming", "interest_mathematics",
    "interest_research", "interest_product_design", "interest_management",
    "interest_core_engg", "interest_finance",
]
