"""
utils/career_engine.py  —  Career fit calculation & SWOT logic
"""
from __future__ import annotations
import numpy as np

# ── Career definitions ──────────────────────────────────────────────────────
CAREERS = [
    {
        "id": "ai_ml",
        "title": "AI / ML Engineer",
        "salary": "₹15–25 LPA",
        "demand": "Very High",
        "required_interests": {"ai_ml", "programming", "mathematics"},
        "required_skills": {"technical", "analytical"},
        "skills_needed": ["Python", "Machine Learning", "Deep Learning", "Statistics"],
        "path": "Advanced ML courses → Portfolio projects → Research internship",
    },
    {
        "id": "data_sci",
        "title": "Data Scientist",
        "salary": "₹12–20 LPA",
        "demand": "High",
        "required_interests": {"mathematics", "programming", "research"},
        "required_skills": {"analytical", "technical"},
        "skills_needed": ["Python", "SQL", "Statistics", "Data Viz"],
        "path": "Master statistics → Kaggle competitions → Industry projects",
    },
    {
        "id": "product_mgr",
        "title": "Product Manager",
        "salary": "₹18–30 LPA",
        "demand": "Very High",
        "required_interests": {"management", "product_design"},
        "required_skills": {"communication", "leadership"},
        "skills_needed": ["Business Acumen", "Agile", "User Research", "Data"],
        "path": "Product frameworks → Side projects → APM roles",
    },
    {
        "id": "research_sci",
        "title": "Research Scientist",
        "salary": "₹10–18 LPA",
        "demand": "Moderate",
        "required_interests": {"research", "mathematics", "ai_ml"},
        "required_skills": {"analytical", "technical"},
        "skills_needed": ["Research Methods", "ML", "Academic Writing", "Statistics"],
        "path": "Publications → Masters/PhD → Lab roles",
    },
    {
        "id": "swe",
        "title": "Software Engineer",
        "salary": "₹10–22 LPA",
        "demand": "Very High",
        "required_interests": {"programming"},
        "required_skills": {"technical"},
        "skills_needed": ["DSA", "System Design", "DBMS", "Dev Tools"],
        "path": "LeetCode → Open source → FAANG internships",
    },
    {
        "id": "ux_designer",
        "title": "UX / Product Designer",
        "salary": "₹8–18 LPA",
        "demand": "High",
        "required_interests": {"product_design"},
        "required_skills": {"creative", "communication"},
        "skills_needed": ["Figma", "User Research", "Prototyping", "Design Systems"],
        "path": "Portfolio → Freelance → Design teams",
    },
]


def calculate_career_fit(profile: dict, career: dict) -> float:
    """
    Weighted career fit score.
    Formula: (academic × 0.25) + (interest × 0.30) + (skill × 0.25) + (effort × 0.20)
    Returns a float 0–100.
    """
    cgpa        = profile.get("cgpa", 7.0)
    interests   = set(profile.get("interests", []))
    skill_map   = profile.get("skills", {})
    effort      = profile.get("effort", 3) / 5  # normalise 1-5 → 0-1

    # Academic score (CGPA out of 10 → 0-1)
    academic_score = min(cgpa / 10, 1.0)

    # Interest alignment
    req_interests = career["required_interests"]
    interest_score = len(interests & req_interests) / max(len(req_interests), 1)

    # Skill alignment
    req_skills = career["required_skills"]
    skill_scores = [skill_map.get(s, 50) / 100 for s in req_skills]
    skill_score = np.mean(skill_scores) if skill_scores else 0.5

    fit = (
        academic_score  * 0.25 +
        interest_score  * 0.30 +
        skill_score     * 0.25 +
        effort          * 0.20
    )
    return round(fit * 100, 1)


def rank_careers(profile: dict) -> list[dict]:
    """Return careers sorted by fit score descending."""
    results = []
    for career in CAREERS:
        score = calculate_career_fit(profile, career)
        results.append({**career, "fit": score})
    return sorted(results, key=lambda c: c["fit"], reverse=True)


def generate_swot(profile: dict, top_career: dict) -> dict:
    """Dynamically generate SWOT based on student profile."""
    cgpa          = profile.get("cgpa", 7.0)
    skills        = profile.get("skills", {})
    interests     = profile.get("interests", [])
    extracurriculars = profile.get("extracurriculars", 0)
    projects      = profile.get("projects", 0)
    effort        = profile.get("effort", 3)

    strengths, weaknesses, opportunities, threats = [], [], [], []

    # ── Strengths
    if cgpa >= 8.0:
        strengths.append(f"Strong academic record — CGPA {cgpa}/10 (top academic tier)")
    if skills.get("analytical", 0) >= 75:
        strengths.append(f"High analytical aptitude ({skills['analytical']}th percentile)")
    if skills.get("technical", 0) >= 70:
        strengths.append("Solid technical fundamentals")
    if effort >= 4:
        strengths.append("High effort index — consistent self-motivated learner")
    if projects >= 3:
        strengths.append(f"{projects} projects completed — practical experience demonstrated")
    if not strengths:
        strengths.append("Growth mindset and willingness to learn")

    # ── Weaknesses
    if cgpa < 6.5:
        weaknesses.append("Academic score below target threshold — needs improvement")
    if skills.get("communication", 0) < 60:
        weaknesses.append("Communication skills below average — limit team & leadership roles")
    if skills.get("creative", 0) < 55:
        weaknesses.append("Creative/design thinking is a relative gap")
    if extracurriculars < 2:
        weaknesses.append("Limited extracurricular profile — impacts holistic evaluation")
    if projects < 2:
        weaknesses.append("Thin project portfolio — needs more hands-on work")
    if not weaknesses:
        weaknesses.append("Continuous improvement required to stay ahead in competitive market")

    # ── Opportunities
    if "ai_ml" in interests:
        opportunities.append("AI/ML sector booming — aligned interest creates strong upside")
    if skills.get("analytical", 0) >= 70 and skills.get("technical", 0) >= 70:
        opportunities.append("Dual strength in analytics + tech ideal for data science roles")
    if projects < 4:
        opportunities.append("Growing project portfolio can rapidly improve career fit score")
    opportunities.append(f"Target career '{top_career['title']}' shows {top_career['fit']}% alignment")
    opportunities.append("Industry certifications can compensate for experience gaps")

    # ── Threats
    threats.append("Rapidly evolving tech landscape requires continuous skill upgrades")
    if extracurriculars < 2:
        threats.append("Peers with stronger extracurricular profiles may be preferred")
    if effort < 3:
        threats.append("Low effort consistency may compound academic underperformance")
    threats.append("High competition in target roles requires differentiated portfolio")

    return {
        "strengths": strengths[:5],
        "weaknesses": weaknesses[:4],
        "opportunities": opportunities[:4],
        "threats": threats[:4],
    }


def compute_intelligence_score(profile: dict) -> int:
    """Composite intelligence score 0–100."""
    cgpa     = profile.get("cgpa", 7.0)
    skills   = profile.get("skills", {})
    effort   = profile.get("effort", 3)
    projects = profile.get("projects", 0)

    academic  = (cgpa / 10) * 30
    skill_avg = (np.mean(list(skills.values())) / 100 * 40) if skills else 20
    effort_s  = (effort / 5) * 20
    project_s = min(projects / 5, 1.0) * 10

    return int(round(academic + skill_avg + effort_s + project_s))
