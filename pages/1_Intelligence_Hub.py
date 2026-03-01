"""
pages/1_Intelligence_Hub.py — Student Intelligence Hub
"""
import streamlit as st
import pandas as pd
from components.styles import load_css
from components.sidebar import render_sidebar
from components.navbar import render_navbar
from components.cards import metric_card, career_card, section_title, glow_divider
from components.charts import radar_chart, line_chart, gauge_chart
from utils.career_engine import compute_intelligence_score, rank_careers
from utils.database import db
from utils.ml_engine import predict_career_fit, predict_student_cluster, predict_cgpa_trajectory
from utils.analytics_engine import benchmark_student, skill_gap_analysis, growth_timeline
from utils.data_engine import get_feature_vector

st.set_page_config(page_title="SPECTRA — Intelligence Hub", page_icon="🎯", layout="wide")
load_css()
render_sidebar()
st.session_state["_current_page"] = "Intelligence Hub"
render_navbar()

# ── Restore session from DB on refresh ───────────────────────────────────
if "student_profile" not in st.session_state or not st.session_state.get("student_profile"):
    # Try to load the most recently analysed student from DB
    all_students = db.get_all_students()
    if all_students:
        sid = all_students[0]["student_id"]
        full = db.get_student(sid)
        if full:
            st.session_state.student_profile = full
            cached = db.get_student_career_results(sid)
            if cached:
                st.session_state.ranked_careers = cached
                st.session_state.top_career_fit = cached[0]["fit"]
            st.session_state.intelligence_score = full.get("intelligence_score", 0)
            st.session_state.ml_ran = True

profile  = st.session_state.get("student_profile", {})

# ── Run ML backend if profile has skills ──────────────────────────────────
if profile and profile.get("skills") and not st.session_state.get("ml_ran"):
    with st.spinner("🤖 Running AI analysis..."):
        try:
            ml_careers = predict_career_fit(profile)
            st.session_state.ranked_careers     = ml_careers
            st.session_state.top_career_fit     = ml_careers[0]["fit"] if ml_careers else 0
            st.session_state.student_cluster    = predict_student_cluster(profile)
            st.session_state.cgpa_trajectory    = predict_cgpa_trajectory(profile, 4)
            st.session_state.ml_ran             = True
        except Exception as e:
            st.warning(f"ML engine fallback: {e}")

ranked    = st.session_state.get("ranked_careers", [])
cluster   = st.session_state.get("student_cluster", {})
traj_data = st.session_state.get("cgpa_trajectory", [])
intel    = st.session_state.get("intelligence_score", 0)

# ── Header ────────────────────────────────────────────────────────────────
st.markdown(section_title("🎯", "Student Intelligence", "Hub"), unsafe_allow_html=True)

if not profile:
    st.warning("⚠️ No profile found. Please complete the Student Intake form first.")
    if st.button("✏️ Go to Intake Form"):
        st.switch_page("pages/0_Student_Intake.py")
    st.stop()

# ── KPI Row ───────────────────────────────────────────────────────────────
skills   = profile.get("skills", {})
cgpa     = profile.get("cgpa", 0)
effort   = profile.get("effort", 3)
projects = profile.get("projects", 0)
top_fit  = ranked[0]["fit"] if ranked else 0

skill_avg = round(sum(skills.values()) / len(skills)) if skills else 0
consistency = skills.get("consistency", 0)

c1, c2, c3, c4 = st.columns(4)
kpis = [
    (c1, "Academic Index",   f"{cgpa:.1f}/10",   "0.6 from last sem",       "up"),
    (c2, "Skill Strength",   f"{skill_avg}%",     "Self-assessed average",    "neutral"),
    (c3, "Intelligence Score",f"{intel}/100",      "Composite AI score",       "up"),
    (c4, "Top Career Fit",   f"{top_fit}%",       f"{ranked[0]['title'] if ranked else '—'}", "up"),
]
for col, label, val, trend, tdir in kpis:
    with col:
        st.markdown(metric_card(label, val, trend, tdir), unsafe_allow_html=True)

st.markdown(glow_divider(), unsafe_allow_html=True)

# ── Two-column layout ─────────────────────────────────────────────────────
left, right = st.columns([1.4, 1])

with left:
    st.markdown("#### 📡 Multi-Dimensional Skill Radar")
    categories = ["Technical", "Analytical", "Creative", "Leadership", "Communication", "Consistency"]
    keys       = ["technical", "analytical", "creative", "leadership", "communication", "consistency"]
    values     = [skills.get(k, 50) for k in keys]
    st.plotly_chart(radar_chart(categories, values, profile.get("name", "Student")),
                    use_container_width=True)

with right:
    st.markdown("#### 🔥 Top Career Matches")
    for c in ranked[:4]:
        st.markdown(career_card(c["title"], c["fit"], f"Demand: {c['demand']}"),
                    unsafe_allow_html=True)

st.markdown(glow_divider(), unsafe_allow_html=True)

# ── Intelligence Score Gauge + Growth Projection ──────────────────────────
g1, g2 = st.columns([1, 2])

with g1:
    st.markdown("#### 🧠 Intelligence Score")
    st.plotly_chart(gauge_chart(intel, "Composite Score"), use_container_width=True)

with g2:
    st.markdown("#### 📈 Simulated Growth Trajectory")
    # Generate a realistic synthetic trajectory based on profile
    months = ["Aug", "Sep", "Oct", "Nov", "Dec", "Jan"]
    base_academic = max(cgpa - 1.5, 5.0)
    base_skill    = max(skill_avg - 20, 40)
    base_effort   = effort * 10

    trajectory = pd.DataFrame({
        "Month":    months,
        "Academic": [round(base_academic + i * 0.3, 1) for i in range(6)],
        "Skills":   [round(base_skill    + i * 2.5, 1) for i in range(6)],
        "Effort":   [round(base_effort   + i * 1.8, 1) for i in range(6)],
    })
    st.plotly_chart(line_chart(trajectory, "Month", ["Academic", "Skills", "Effort"],
                               "Growth This Semester"),
                    use_container_width=True)

# ── Skill Breakdown Table ─────────────────────────────────────────────────
st.markdown(glow_divider(), unsafe_allow_html=True)
st.markdown("#### 🔢 Full Skill Breakdown")

skill_display = {k.title(): v for k, v in skills.items()}
skill_df = pd.DataFrame(
    {"Skill": list(skill_display.keys()), "Score": list(skill_display.values())}
).sort_values("Score", ascending=False)

for _, row in skill_df.iterrows():
    bar_color = "#00E887" if row["Score"] >= 75 else ("#FFB800" if row["Score"] >= 55 else "#FF4D6A")
    st.markdown(f"""
    <div class="skill-row">
        <div class="skill-label">
            <span>{row['Skill']}</span>
            <span style="color:{bar_color};">{int(row['Score'])}/100</span>
        </div>
        <div class="skill-bar-bg">
            <div class="skill-bar-fill" style="width:{row['Score']}%;
                 background:linear-gradient(90deg, {bar_color}, {bar_color}88);"></div>
        </div>
    </div>
    """, unsafe_allow_html=True)