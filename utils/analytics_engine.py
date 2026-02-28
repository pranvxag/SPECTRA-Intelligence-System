"""
utils/analytics_engine.py — Analytical Intelligence Layer

Computes:
- Cohort-level statistics from batch DataFrames
- Peer benchmarking (where does this student rank vs cohort)
- Department / institute breakdowns
- At-risk segmentation
- Growth trajectory analysis across semesters
"""
from __future__ import annotations
import pandas as pd
import numpy as np
from typing import Dict, List, Tuple, Optional


# ── Individual Benchmarking ───────────────────────────────────────────────

def benchmark_student(profile: dict, df: pd.DataFrame) -> Dict:
    """
    Compare a single student against the full cohort.
    Returns percentile rankings and peer group stats.
    """
    if df is None or len(df) == 0:
        return {}

    result = {}

    # CGPA percentile
    cgpa = profile.get("cgpa", 0)
    if "cgpa" in df.columns:
        result["cgpa_percentile"]    = round(float((df["cgpa"] < cgpa).mean() * 100), 1)
        result["cgpa_cohort_avg"]    = round(float(df["cgpa"].mean()), 2)
        result["cgpa_cohort_median"] = round(float(df["cgpa"].median()), 2)

    # Intelligence score percentile
    intel = profile.get("intelligence_score", 0)
    if "intelligence_score" in df.columns:
        result["intel_percentile"] = round(float((df["intelligence_score"] < intel).mean() * 100), 1)
        result["intel_cohort_avg"] = round(float(df["intelligence_score"].mean()), 1)

    # Skill percentiles
    skill_map = {
        "skill_technical":     "technical",
        "skill_analytical":    "analytical",
        "skill_creative":      "creative",
        "skill_communication": "communication",
        "skill_leadership":    "leadership",
        "skill_consistency":   "consistency",
    }
    skills = profile.get("skills", {})
    result["skill_percentiles"] = {}
    for col, key in skill_map.items():
        if col in df.columns:
            val = skills.get(key, 0)
            pct = float((df[col] < val).mean() * 100)
            result["skill_percentiles"][key] = round(pct, 1)

    # Activity percentile
    activities = (
        profile.get("projects", 0) * 3 +
        profile.get("internships", 0) * 4 +
        profile.get("hackathons", 0) * 2 +
        profile.get("certifications", 0) * 1.5 +
        profile.get("extracurriculars", 0) * 1
    )
    if "activity_index" in df.columns:
        result["activity_percentile"] = round(float((df["activity_index"] < activities).mean() * 100), 1)

    # Peer group (same branch, same year)
    branch = profile.get("branch", "")
    peer_df = df[df.get("branch", pd.Series()) == branch] if "branch" in df.columns else df
    result["peer_count"] = len(peer_df)
    if len(peer_df) > 0 and "cgpa" in peer_df.columns:
        result["peer_cgpa_avg"]   = round(float(peer_df["cgpa"].mean()), 2)
        result["peer_intel_avg"]  = round(float(peer_df.get("intelligence_score", pd.Series([0])).mean()), 1)
        result["peer_cgpa_rank"]  = int((peer_df["cgpa"] > cgpa).sum()) + 1

    return result


# ── Cohort / Batch Statistics ─────────────────────────────────────────────

def compute_cohort_stats(df: pd.DataFrame) -> Dict:
    """
    Full statistical breakdown of a batch DataFrame.
    Used for Institutional View dashboard.
    """
    if df is None or len(df) == 0:
        return _empty_cohort_stats()

    stats = {}

    # ── Headcount
    stats["total_students"] = len(df)

    # ── CGPA distribution
    if "cgpa" in df.columns:
        stats["cgpa_mean"]   = round(float(df["cgpa"].mean()), 2)
        stats["cgpa_median"] = round(float(df["cgpa"].median()), 2)
        stats["cgpa_std"]    = round(float(df["cgpa"].std()), 2)
        stats["cgpa_min"]    = round(float(df["cgpa"].min()), 2)
        stats["cgpa_max"]    = round(float(df["cgpa"].max()), 2)
        buckets = [0, 5, 6, 7, 8, 9, 10.1]
        labels  = ["<5.0", "5.0-6.0", "6.0-7.0", "7.0-8.0", "8.0-9.0", "9.0+"]
        counts  = pd.cut(df["cgpa"], bins=buckets, labels=labels, right=False).value_counts()
        stats["cgpa_distribution"] = counts.to_dict()

    # ── Intelligence score
    if "intelligence_score" in df.columns:
        stats["intel_mean"]   = round(float(df["intelligence_score"].mean()), 1)
        stats["intel_median"] = round(float(df["intelligence_score"].median()), 1)

    # ── Risk breakdown
    if "risk_level" in df.columns:
        risk_counts = df["risk_level"].value_counts().to_dict()
        stats["risk_high"]   = int(risk_counts.get("High",   0))
        stats["risk_medium"] = int(risk_counts.get("Medium", 0))
        stats["risk_low"]    = int(risk_counts.get("Low",    0))
        stats["at_risk"]     = stats["risk_high"] + stats["risk_medium"]

    # ── Effort distribution
    if "effort" in df.columns:
        stats["effort_avg"] = round(float(df["effort"].mean()), 2)
        stats["effort_dist"] = df["effort"].value_counts().sort_index().to_dict()

    # ── Skills
    skill_cols = ["skill_technical","skill_analytical","skill_creative",
                  "skill_communication","skill_leadership","skill_consistency"]
    stats["skill_averages"] = {}
    for col in skill_cols:
        if col in df.columns:
            key = col.replace("skill_", "")
            stats["skill_averages"][key] = round(float(df[col].mean()), 1)

    # ── Activities
    if "projects" in df.columns:
        stats["avg_projects"]      = round(float(df["projects"].mean()), 1)
        stats["avg_internships"]   = round(float(df.get("internships", pd.Series([0])).mean()), 1)
        stats["avg_hackathons"]    = round(float(df.get("hackathons", pd.Series([0])).mean()), 1)

    # ── Career goal distribution
    if "career_goal" in df.columns:
        stats["career_dist"] = df["career_goal"].value_counts().head(8).to_dict()

    # ── Branch breakdown
    if "branch" in df.columns:
        branch_stats = df.groupby("branch").agg(
            count=("cgpa", "count"),
            avg_cgpa=("cgpa", "mean"),
            avg_intel=("intelligence_score", "mean") if "intelligence_score" in df.columns else ("cgpa", "mean"),
        ).round(2).to_dict("index")
        stats["branch_breakdown"] = branch_stats

    # ── Interest distribution
    if "interest_1" in df.columns:
        all_interests = pd.concat([
            df.get("interest_1", pd.Series()),
            df.get("interest_2", pd.Series()),
            df.get("interest_3", pd.Series()),
        ]).dropna()
        all_interests = all_interests[all_interests != ""]
        stats["interest_dist"] = all_interests.value_counts().head(8).to_dict()

    # ── Placement readiness (intel > 65 + cgpa > 7.0 + effort >= 3)
    if all(c in df.columns for c in ["intelligence_score", "cgpa", "effort"]):
        ready = df[
            (df["intelligence_score"] >= 65) &
            (df["cgpa"] >= 7.0) &
            (df["effort"] >= 3)
        ]
        stats["placement_ready"]   = len(ready)
        stats["placement_ready_pct"] = round(len(ready) / len(df) * 100, 1)

    # ── Backlogs
    if "backlogs" in df.columns:
        stats["students_with_backlogs"] = int((df["backlogs"] > 0).sum())
        stats["avg_backlogs"]           = round(float(df["backlogs"].mean()), 2)

    return stats


def _empty_cohort_stats() -> Dict:
    return {
        "total_students": 0, "cgpa_mean": 0, "cgpa_median": 0,
        "intel_mean": 0, "at_risk": 0, "placement_ready": 0,
        "placement_ready_pct": 0, "skill_averages": {},
        "career_dist": {}, "branch_breakdown": {},
    }


# ── Department / Institute Breakdowns ────────────────────────────────────

def department_report(df: pd.DataFrame) -> pd.DataFrame:
    """
    Returns a per-department summary DataFrame.
    """
    if df is None or "branch" not in df.columns:
        return pd.DataFrame()

    agg = {}
    agg["Students"] = df.groupby("branch")["cgpa"].count()
    agg["Avg CGPA"] = df.groupby("branch")["cgpa"].mean().round(2)

    if "intelligence_score" in df.columns:
        agg["Avg Intel Score"] = df.groupby("branch")["intelligence_score"].mean().round(1)
    if "effort" in df.columns:
        agg["Avg Effort"] = df.groupby("branch")["effort"].mean().round(2)
    if "risk_level" in df.columns:
        at_risk_count = df[df["risk_level"] == "High"].groupby("branch")["cgpa"].count()
        agg["High Risk"] = at_risk_count
    if "projects" in df.columns:
        agg["Avg Projects"] = df.groupby("branch")["projects"].mean().round(1)

    result = pd.DataFrame(agg).fillna(0)
    result["High Risk"] = result["High Risk"].astype(int)
    return result.sort_values("Avg CGPA", ascending=False)


# ── Trend / Growth Analysis ───────────────────────────────────────────────

def growth_timeline(profile: dict) -> Dict:
    """
    Reconstruct an approximate historical performance timeline
    and project forward. Used in Growth Tracker page.
    """
    cgpa    = profile.get("cgpa", 7.0)
    effort  = profile.get("effort", 3)
    trend   = profile.get("academic_trend", "Stable")
    sem     = profile.get("semester", 4)

    trend_delta = {"Improving": 0.15, "Stable": 0.0, "Declining": -0.12}[trend]

    # Reconstruct past semesters working backwards
    past = []
    current = cgpa
    for i in range(sem - 1, 0, -1):
        noise = np.random.normal(0, 0.05)
        prev  = round(max(4.0, min(10.0, current - trend_delta * 0.5 + noise)), 2)
        past.insert(0, prev)
        current = prev
    past.append(cgpa)

    # Project forward
    future = []
    effort_bonus = (effort - 3) * 0.03
    base_growth  = trend_delta * 0.5 + effort_bonus
    proj = cgpa
    for _ in range(4):
        headroom = (10.0 - proj) / 10.0
        proj = round(min(10.0, proj + base_growth * headroom), 2)
        future.append(proj)

    sem_labels_past   = [f"Sem {i+1}" for i in range(len(past))]
    sem_labels_future = [f"Sem {sem + i + 1}" for i in range(len(future))]

    return {
        "past_semesters":   sem_labels_past,
        "past_cgpa":        past,
        "future_semesters": sem_labels_future,
        "future_cgpa":      future,
        "all_labels":       sem_labels_past + sem_labels_future,
        "all_cgpa":         past + future,
        "cutoff_index":     len(past) - 1,
    }


def skill_gap_analysis(profile: dict, target_career: str) -> Dict:
    """
    Compare current skills vs what's required for the target career.
    Returns gap per skill and recommended focus areas.
    """
    CAREER_REQUIREMENTS = {
        "AI/ML Engineer":       {"technical": 80, "analytical": 85, "creative": 55, "communication": 60, "leadership": 45, "consistency": 75},
        "Data Scientist":       {"technical": 75, "analytical": 88, "creative": 60, "communication": 65, "leadership": 50, "consistency": 70},
        "Software Engineer":    {"technical": 85, "analytical": 75, "creative": 55, "communication": 60, "leadership": 50, "consistency": 80},
        "Product Manager":      {"technical": 60, "analytical": 75, "creative": 72, "communication": 85, "leadership": 82, "consistency": 70},
        "Research Scientist":   {"technical": 78, "analytical": 90, "creative": 65, "communication": 65, "leadership": 50, "consistency": 82},
        "UX Designer":          {"technical": 55, "analytical": 65, "creative": 88, "communication": 80, "leadership": 58, "consistency": 68},
        "Core Engineer":        {"technical": 78, "analytical": 72, "creative": 55, "communication": 62, "leadership": 52, "consistency": 75},
        "Finance/Quant":        {"technical": 70, "analytical": 88, "creative": 60, "communication": 72, "leadership": 68, "consistency": 78},
    }

    required = CAREER_REQUIREMENTS.get(target_career, {})
    current  = profile.get("skills", {})
    gaps     = {}
    priority = []

    for skill, req_val in required.items():
        curr_val = current.get(skill, 0)
        gap      = req_val - curr_val
        gaps[skill] = {
            "current":  curr_val,
            "required": req_val,
            "gap":      max(0, gap),
            "met":      curr_val >= req_val,
        }
        if gap > 15:
            priority.append((skill, gap))

    priority.sort(key=lambda x: -x[1])
    overall_readiness = round(
        sum(1 for g in gaps.values() if g["met"]) / len(gaps) * 100, 1
    ) if gaps else 0

    return {
        "gaps":               gaps,
        "priority_skills":    [p[0] for p in priority[:3]],
        "overall_readiness":  overall_readiness,
        "target_career":      target_career,
    }


def compute_swot(profile: dict, career_fit: float = 0) -> Dict:
    """
    Dynamic rule-based SWOT analysis that uses every available data point.
    More sophisticated than the original career_engine version.
    """
    skills   = profile.get("skills", {})
    cgpa     = profile.get("cgpa", 0)
    effort   = profile.get("effort", 3)
    projects = profile.get("projects", 0)
    internships   = profile.get("internships", 0)
    hackathons    = profile.get("hackathons", 0)
    certs         = profile.get("certifications", 0)
    extras        = profile.get("extracurriculars", 0)
    trend         = profile.get("academic_trend", "Stable")
    interests     = profile.get("interests", [])
    intel         = profile.get("intelligence_score", 0)
    branch        = profile.get("branch", "")

    strengths, weaknesses, opportunities, threats = [], [], [], []

    # ── Strengths ──────────────────────────────────────────────────────
    if cgpa >= 8.5:
        strengths.append(f"Exceptional academic record (CGPA {cgpa}/10) — top 10% threshold")
    elif cgpa >= 7.5:
        strengths.append(f"Strong academic performance (CGPA {cgpa}/10)")

    if skills.get("technical", 0) >= 75:
        strengths.append(f"High technical proficiency ({skills['technical']}/100) — above industry entry bar")
    if skills.get("analytical", 0) >= 75:
        strengths.append(f"Strong analytical thinking ({skills['analytical']}/100) — key for data/research roles")
    if skills.get("communication", 0) >= 75:
        strengths.append(f"Excellent communication skills ({skills['communication']}/100)")
    if skills.get("leadership", 0) >= 70:
        strengths.append(f"Demonstrated leadership capability ({skills['leadership']}/100)")

    if projects >= 4:
        strengths.append(f"Strong project portfolio ({projects} projects) — demonstrates applied skills")
    elif projects >= 2:
        strengths.append(f"Has practical project experience ({projects} projects)")

    if internships >= 2:
        strengths.append(f"Real-world industry exposure ({internships} internships)")
    elif internships == 1:
        strengths.append("Industry internship experience — competitive advantage")

    if effort >= 4:
        strengths.append(f"High effort & consistency rating ({effort}/5) — strong work ethic")

    if trend == "Improving":
        strengths.append("Academic trajectory is improving — momentum is positive")

    if hackathons >= 2:
        strengths.append(f"Active hackathon participation ({hackathons}) — problem-solving mindset")

    # ── Weaknesses ─────────────────────────────────────────────────────
    if cgpa < 6.0:
        weaknesses.append(f"CGPA below competitive threshold (6.0). Current: {cgpa}/10")
    elif cgpa < 7.0:
        weaknesses.append(f"CGPA below strong-hire benchmark (7.5). Current: {cgpa}/10")

    if profile.get("backlogs", 0) > 0:
        weaknesses.append(f"{profile['backlogs']} active academic backlog(s) — must be cleared")

    if skills.get("communication", 0) < 55:
        weaknesses.append(f"Communication skills need development ({skills.get('communication',0)}/100)")
    if skills.get("leadership", 0) < 45:
        weaknesses.append(f"Leadership skills underdeveloped ({skills.get('leadership',0)}/100)")
    if skills.get("technical", 0) < 55:
        weaknesses.append(f"Technical skills below entry-level bar ({skills.get('technical',0)}/100)")

    if projects == 0:
        weaknesses.append("No projects on record — resume lacks tangible deliverables")
    if internships == 0:
        weaknesses.append("No internship experience — gap vs peers in hiring pools")
    if certs == 0:
        weaknesses.append("No certifications — missing quick credibility signal for technical roles")

    if effort <= 2:
        weaknesses.append(f"Effort rating low ({effort}/5) — consistency gap may limit growth")

    if trend == "Declining":
        weaknesses.append("Declining academic trend — requires immediate course correction")

    if extras == 0:
        weaknesses.append("No extracurricular activities — weaker holistic profile")

    # ── Opportunities ──────────────────────────────────────────────────
    if "ai_ml" in interests or skills.get("technical", 0) >= 70:
        opportunities.append("High demand for AI/ML talent — 40%+ YoY job growth in this sector")
    if "research" in interests and cgpa >= 7.5:
        opportunities.append("Strong profile for research fellowships, RA positions, or top MS programmes")
    if "management" in interests or skills.get("leadership", 0) >= 65:
        opportunities.append("Leadership profile suits MBA/PM tracks at top firms & startups")

    if internships == 0 and effort >= 3:
        opportunities.append("First internship could significantly boost career fit score (+15–20 points)")
    if projects <= 2:
        opportunities.append("2–3 targeted open-source or Kaggle projects could transform resume in 60 days")
    if certs == 0:
        opportunities.append("1–2 platform certifications (AWS/GCP, Coursera) are low-effort, high-signal")
    if hackathons == 0:
        opportunities.append("Hackathon participation builds network + portfolio simultaneously")

    if cgpa >= 8.0 and internships >= 1:
        opportunities.append("Strong candidacy for PPO (Pre-Placement Offer) or fast-track campus placement")

    # ── Threats ────────────────────────────────────────────────────────
    if trend == "Declining":
        threats.append("Declining CGPA trend threatens placement eligibility if it falls below 6.5")
    if profile.get("backlogs", 0) > 2:
        threats.append("Multiple backlogs risk semester drop / eligibility disqualification")

    threats.append("Increasing competition: 60%+ of CS/IT graduates targeting same tech roles")

    if "ai_ml" in interests and skills.get("technical", 0) < 70:
        threats.append("AI/ML market requires strong Python/math base — current technical score is below threshold")

    if effort <= 2 and cgpa < 7.0:
        threats.append("Compound risk: low effort + low CGPA creates significant placement barrier")

    if internships == 0 and extras == 0:
        threats.append("Thin extracurricular profile — screening algorithms filter this out early")

    threats.append("Industry shifting toward practical skills over degrees — portfolio gaps are costly")

    return {
        "strengths":     strengths[:5],
        "weaknesses":    weaknesses[:4],
        "opportunities": opportunities[:4],
        "threats":       threats[:4],
        "scores": {
            "strength_index":    min(100, len(strengths) * 18 + career_fit * 0.2),
            "resilience_index":  max(0, 100 - len(weaknesses) * 22),
            "opportunity_score": min(100, len(opportunities) * 22 + effort * 4),
            "risk_score":        min(100, len(threats) * 24),
        }
    }
