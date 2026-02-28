"""
pages/3_SWOT_Analysis.py — Dynamic SWOT + Strategic Roadmap
"""
import streamlit as st
from components.styles import load_css
from components.sidebar import render_sidebar
from components.cards import section_title, swot_card, roadmap_card, glow_divider, metric_card
from utils.career_engine import generate_swot, rank_careers

st.set_page_config(page_title="SPECTRA — SWOT Analysis", page_icon="📊", layout="wide")
load_css()
render_sidebar()

profile = st.session_state.get("student_profile", {})
ranked  = st.session_state.get("ranked_careers", [])

st.markdown(section_title("📊", "Data-Driven", "SWOT Analysis"), unsafe_allow_html=True)

if not profile:
    st.warning("⚠️ Complete the Student Intake form first.")
    if st.button("✏️ Go to Intake Form"):
        st.switch_page("pages/0_Student_Intake.py")
    st.stop()

top_career = ranked[0] if ranked else {"title": "AI/ML Engineer", "fit": 0}
swot = generate_swot(profile, top_career)

# ── Student context banner ────────────────────────────────────────────────
name   = profile.get("name", "Student")
branch = profile.get("branch", "—")
cgpa   = profile.get("cgpa", 0)

st.markdown(f"""
<div class="glass-panel" style="margin-bottom:1.5rem; display:flex; justify-content:space-between; align-items:center; flex-wrap:wrap; gap:1rem;">
    <div>
        <div style="font-family:'Syne',sans-serif; font-size:1.1rem; font-weight:700; color:#E2E8F0;">
            {name}
        </div>
        <div style="color:#7A90B0; font-size:0.85rem;">{branch} · Sem {profile.get('semester','—')} · CGPA {cgpa}</div>
    </div>
    <div style="color:#7A90B0; font-size:0.85rem;">
        Target: <strong style="color:#00D4FF;">{top_career['title']}</strong> 
        &nbsp;·&nbsp; Fit: <strong style="color:#FFB800;">{top_career['fit']}%</strong>
    </div>
</div>
""", unsafe_allow_html=True)

# ── SWOT Grid ─────────────────────────────────────────────────────────────
c1, c2 = st.columns(2)

with c1:
    st.markdown(swot_card("strength", "Strengths", "💪", swot["strengths"]), unsafe_allow_html=True)
    st.markdown(swot_card("weakness", "Weaknesses", "🔻", swot["weaknesses"]), unsafe_allow_html=True)

with c2:
    st.markdown(swot_card("opportunity", "Opportunities", "✨", swot["opportunities"]), unsafe_allow_html=True)
    st.markdown(swot_card("threat", "Threats", "⚠️", swot["threats"]), unsafe_allow_html=True)

st.markdown(glow_divider(), unsafe_allow_html=True)

# ── SWOT Score summary ────────────────────────────────────────────────────
st.markdown("#### 🎯 SWOT Score Summary")

s_score = min(len(swot["strengths"]) * 18, 90)
w_score = max(100 - len(swot["weaknesses"]) * 20, 20)
o_score = min(len(swot["opportunities"]) * 20, 85)
t_score = max(100 - len(swot["threats"]) * 18, 25)

sc1, sc2, sc3, sc4 = st.columns(4)
with sc1: st.markdown(metric_card("Strength Index", f"{s_score}/100", "Based on your profile", "up"), unsafe_allow_html=True)
with sc2: st.markdown(metric_card("Resilience Index", f"{w_score}/100", "Weakness mitigation", "neutral"), unsafe_allow_html=True)
with sc3: st.markdown(metric_card("Opportunity Score", f"{o_score}/100", "Growth potential", "up"), unsafe_allow_html=True)
with sc4: st.markdown(metric_card("Risk Score", f"{t_score}/100", "Threat exposure", "neutral"), unsafe_allow_html=True)

st.markdown(glow_divider(), unsafe_allow_html=True)

# ── Strategic Roadmap ──────────────────────────────────────────────────────
st.markdown("#### 🗺️ Strategic Action Roadmap")

# Dynamic roadmap based on profile
projects     = profile.get("projects", 0)
internships  = profile.get("internships", 0)
certifications = profile.get("certifications", 0)
extracurriculars = profile.get("extracurriculars", 0)

immediate_items = []
if projects < 2:     immediate_items.append(f"Complete {2 - projects} more hands-on projects")
if certifications < 1: immediate_items.append("Earn 1 relevant certification")
if extracurriculars < 2: immediate_items.append("Join 1 tech club or community")
immediate_items.append("Start daily LeetCode practice (2 problems/day)")
if not immediate_items: immediate_items = ["Continue current momentum", "Optimise LinkedIn profile"]

short_items = []
if internships < 1: short_items.append(f"Apply for {top_career['title']} internship")
short_items.append(f"Complete advanced course aligned to {top_career['title']}")
short_items.append("Participate in 1 hackathon")
if cgpa < 8.0:  short_items.append("Target CGPA improvement by 0.5 this semester")

long_items = [
    "Build and publish portfolio website",
    f"Network with 10+ professionals in {top_career['title']} space",
    "Prepare for placement / higher studies application",
    "Develop signature project for resume lead",
]

rc1, rc2, rc3 = st.columns(3)
with rc1: st.markdown(roadmap_card("Phase 1 — 0 to 3 Months", "Quick Wins", immediate_items[:4], "cyan"), unsafe_allow_html=True)
with rc2: st.markdown(roadmap_card("Phase 2 — 3 to 6 Months", "Build Momentum", short_items[:4], "amber"), unsafe_allow_html=True)
with rc3: st.markdown(roadmap_card("Phase 3 — 6 to 12 Months", "Career Launch", long_items[:4], "green"), unsafe_allow_html=True)
