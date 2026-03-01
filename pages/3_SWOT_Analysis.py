"""
pages/3_SWOT_Analysis.py — Dynamic SWOT + Strategic Roadmap (LLM-powered)
"""
import streamlit as st
from components.styles import load_css
from components.sidebar import render_sidebar
from components.navbar import render_navbar
from components.cards import section_title, swot_card, roadmap_card, glow_divider, metric_card
from utils.database import db
from utils.report_generator import generate_student_excel, generate_profile_json

st.set_page_config(page_title="SPECTRA — SWOT Analysis", page_icon="📊", layout="wide")
load_css()
from utils.auth import require_login
require_login()
render_sidebar()
st.session_state["_current_page"] = "SWOT Analysis"
render_navbar()

profile = st.session_state.get("student_profile", {})
ranked  = st.session_state.get("ranked_careers", [])

st.markdown(section_title("📊", "AI-Powered", "SWOT Analysis"), unsafe_allow_html=True)

if not profile:
    st.warning("⚠️ Complete the Student Intake form first.")
    if st.button("✏️ Go to Intake Form"):
        st.switch_page("pages/0_Student_Intake.py")
    st.stop()

top_career = ranked[0] if ranked else {"title": "Software Engineer", "fit": 0}
top_career_fit = top_career.get("fit", 0) if isinstance(top_career, dict) else 0

# ── LLM-powered SWOT (with DB cache) ─────────────────────────────────────
student_id = profile.get("student_id", "")

# Check if a regeneration was forced
force_regen = st.session_state.pop("force_swot_regen", False)

# Try to load from DB cache first (skip if forced)
swot      = None
roadmap   = None
from_cache = False

if not force_regen and student_id:
    cached = db.get_swot(student_id)
    if cached and "strengths" in cached:
        swot      = cached.get("swot")
        roadmap   = cached.get("roadmap")
        from_cache = bool(swot and roadmap)

# If not cached (or forced), generate via Gemini
if not swot or not roadmap:
    # Check if Gemini is initialized
    api_key = ""
    try:
        api_key = st.secrets["GEMINI_API_KEY"]
    except (KeyError, FileNotFoundError):
        pass
    if not api_key:
        api_key = st.session_state.get("gemini_key", "")

    if api_key:
        from utils.llm_engine import init_gemini, generate_dynamic_swot, generate_dynamic_roadmap
        init_gemini(api_key)

        with st.spinner("🤖 SPECTRA AI is generating your personalized SWOT analysis..."):
            swot    = generate_dynamic_swot(profile, top_career)
            roadmap = generate_dynamic_roadmap(profile, top_career)

        # Save to DB cache
        if student_id:
            db.save_swot(student_id, {"swot": swot, "roadmap": roadmap})
    else:
        # Fallback to rule-based if no API key configured
        from utils.analytics_engine import compute_swot, skill_gap_analysis
        swot = compute_swot(profile, top_career_fit)
        projects    = profile.get("projects", 0)
        internships = profile.get("internships", 0)
        certifications = profile.get("certifications", 0)
        cgpa = profile.get("cgpa", 0)
        short_items = []
        if internships < 1: short_items.append(f"Apply for {top_career['title']} internship")
        short_items += [f"Complete advanced course aligned to {top_career['title']}", "Participate in 1 hackathon"]
        if cgpa < 8.0: short_items.append("Target CGPA improvement by 0.5 this semester")
        immediate_items = []
        if projects < 2:     immediate_items.append(f"Complete {2 - projects} more hands-on projects")
        if certifications < 1: immediate_items.append("Earn 1 relevant certification")
        immediate_items += ["Join 1 tech club or community", "Start daily LeetCode practice (2 problems/day)"]
        long_items = ["Build and publish portfolio website",
                      f"Network with 10+ professionals in {top_career['title']} space",
                      "Prepare for placement / higher studies application",
                      "Develop signature project for resume lead"]
        roadmap = {"immediate": immediate_items[:4], "short": short_items[:4], "long": long_items[:4]}
        st.info("💡 Add your Gemini API key to get AI-generated SWOT. Using rule-based fallback.")

# ── Student context banner ─────────────────────────────────────────────────
name   = profile.get("name", "Student")
branch = profile.get("branch", "—")
cgpa   = profile.get("cgpa", 0)

# Cache / Regenerate control row
banner_col, regen_col = st.columns([5, 1])
with banner_col:
    st.markdown(f"""
    <div class="glass-panel" style="margin-bottom:1.5rem; display:flex; justify-content:space-between; align-items:center; flex-wrap:wrap; gap:1rem;">
        <div>
            <div style="font-family:'Syne',sans-serif; font-size:1.1rem; font-weight:700; color:#E2E8F0;">
                {name}
                {"<span style='font-size:0.7rem; color:#00E887; background:rgba(0,232,135,0.1); border:1px solid rgba(0,232,135,0.25); padding:0.15rem 0.6rem; border-radius:20px; margin-left:0.8rem;'>🤖 AI-Generated</span>" if not st.session_state.get("swot_fallback") else ""}
            </div>
            <div style="color:#7A90B0; font-size:0.85rem;">{branch} · Sem {profile.get('semester','—')} · CGPA {cgpa}</div>
        </div>
        <div style="color:#7A90B0; font-size:0.85rem;">
            Target: <strong style="color:#00D4FF;">{top_career['title']}</strong>
            &nbsp;·&nbsp; Fit: <strong style="color:#FFB800;">{top_career_fit}%</strong>
            {"&nbsp;·&nbsp; <span style='color:#4A5A7A; font-size:0.75rem;'>📦 Cached</span>" if from_cache else ""}
        </div>
    </div>
    """, unsafe_allow_html=True)
with regen_col:
    if st.button("🔄 Regenerate", help="Re-generate SWOT using AI (uses an API call)", use_container_width=True):
        # Clear the DB cache and rerun
        if student_id:
            db.save_swot(student_id, {})
        st.session_state["force_swot_regen"] = True
        st.rerun()

st.markdown(glow_divider(), unsafe_allow_html=True)

# ── SWOT Grid ──────────────────────────────────────────────────────────────
c1, c2 = st.columns(2)

with c1:
    st.markdown(swot_card("strength",    "Strengths",     "💪", swot.get("strengths",     [])), unsafe_allow_html=True)
    st.markdown(swot_card("weakness",    "Weaknesses",    "🔻", swot.get("weaknesses",    [])), unsafe_allow_html=True)
with c2:
    st.markdown(swot_card("opportunity", "Opportunities", "✨", swot.get("opportunities", [])), unsafe_allow_html=True)
    st.markdown(swot_card("threat",      "Threats",       "⚠️", swot.get("threats",       [])), unsafe_allow_html=True)

st.markdown(glow_divider(), unsafe_allow_html=True)

# ── SWOT Score summary ─────────────────────────────────────────────────────
st.markdown("#### 🎯 SWOT Score Summary")

s_score = min(len(swot.get("strengths", [])) * 18, 90)
w_score = max(100 - len(swot.get("weaknesses", [])) * 20, 20)
o_score = min(len(swot.get("opportunities", [])) * 20, 85)
t_score = max(100 - len(swot.get("threats", [])) * 18, 25)

sc1, sc2, sc3, sc4 = st.columns(4)
with sc1: st.markdown(metric_card("Strength Index",    f"{s_score}/100", "Based on your profile",  "up"),      unsafe_allow_html=True)
with sc2: st.markdown(metric_card("Resilience Index",  f"{w_score}/100", "Weakness mitigation",    "neutral"), unsafe_allow_html=True)
with sc3: st.markdown(metric_card("Opportunity Score", f"{o_score}/100", "Growth potential",       "up"),      unsafe_allow_html=True)
with sc4: st.markdown(metric_card("Risk Score",        f"{t_score}/100", "Threat exposure",        "neutral"), unsafe_allow_html=True)

st.markdown(glow_divider(), unsafe_allow_html=True)

# ── Strategic Roadmap (LLM-generated) ──────────────────────────────────────
st.markdown("#### 🗺️ AI Strategic Action Roadmap")

rc1, rc2, rc3 = st.columns(3)
with rc1: st.markdown(roadmap_card("Phase 1 — 0 to 3 Months", "Quick Wins",          roadmap.get("immediate", [])[:4], "cyan"),  unsafe_allow_html=True)
with rc2: st.markdown(roadmap_card("Phase 2 — 3 to 6 Months", "Build Momentum",      roadmap.get("short",     [])[:4], "amber"), unsafe_allow_html=True)
with rc3: st.markdown(roadmap_card("Phase 3 — 6 to 12 Months","Career Launch",        roadmap.get("long",      [])[:4], "green"), unsafe_allow_html=True)