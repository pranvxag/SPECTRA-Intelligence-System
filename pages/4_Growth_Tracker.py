"""
pages/4_Growth_Tracker.py — Growth Analytics & Predictions
"""
import streamlit as st
import pandas as pd
import numpy as np
from components.styles import load_css
from components.sidebar import render_sidebar
from components.cards import section_title, achievement_item, glow_divider, metric_card
from components.charts import line_chart, area_chart
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


st.set_page_config(page_title="SPECTRA — Growth Tracker", page_icon="📈", layout="wide")
load_css()
render_sidebar()

profile = st.session_state.get("student_profile", {})

st.markdown(section_title("📈", "Growth Tracker", "& Progress Analytics"), unsafe_allow_html=True)

if not profile:
    st.warning("⚠️ Complete the Student Intake form first.")
    if st.button("✏️ Go to Intake Form"):
        st.switch_page("pages/0_Student_Intake.py")
    st.stop()

cgpa     = profile.get("cgpa", 7.0)
skills   = profile.get("skills", {})
effort   = profile.get("effort", 3)
projects = profile.get("projects", 0)
trend    = profile.get("academic_trend", "Stable")

# ── Period selector ────────────────────────────────────────────────────────
period = st.selectbox("📅 Time Period", ["Last 6 Months", "Last Year", "Full History"])
months_map = {"Last 6 Months": 6, "Last Year": 12, "Full History": 18}
n = months_map[period]

# ── Simulate historical data based on current state ────────────────────────
all_months = ["Aug", "Sep", "Oct", "Nov", "Dec", "Jan",
              "Feb", "Mar", "Apr", "May", "Jun", "Jul",
              "Aug'", "Sep'", "Oct'", "Nov'", "Dec'", "Jan'"][:n]

# Work backwards from current CGPA
trend_factor = {"Improving": 0.25, "Stable": 0.08, "Declining": -0.15}[trend]
skill_avg = sum(skills.values()) / len(skills) if skills else 60

cgpa_series  = [round(max(5.0, cgpa - (n - i - 1) * trend_factor), 1) for i in range(n)]
skill_series = [round(max(30, skill_avg - (n - i - 1) * 1.8), 1) for i in range(n)]
effort_series = [round(max(20, effort * 18 - (n - i - 1) * 0.8), 1) for i in range(n)]

hist_df = pd.DataFrame({
    "Month":  all_months,
    "CGPA (×10)": [c * 10 for c in cgpa_series],
    "Skill Score": skill_series,
    "Effort Index": effort_series,
})

st.markdown(glow_divider(), unsafe_allow_html=True)

# ── KPIs ──────────────────────────────────────────────────────────────────
delta_cgpa  = round(cgpa_series[-1] - cgpa_series[0], 1)
delta_skill = round(skill_series[-1] - skill_series[0], 1)

c1, c2, c3, c4 = st.columns(4)
with c1: st.markdown(metric_card("CGPA Now",          f"{cgpa}/10",          f"+{delta_cgpa} over period" if delta_cgpa >= 0 else str(delta_cgpa)), unsafe_allow_html=True)
with c2: st.markdown(metric_card("Skill Score Now",   f"{round(skill_avg)}%", f"+{delta_skill}% growth"), unsafe_allow_html=True)
with c3: st.markdown(metric_card("Projects Completed", str(projects),          "Hands-on work", "neutral"), unsafe_allow_html=True)
with c4: st.markdown(metric_card("Effort Rating",      ["—","Low","Fair","Good","High","Elite"][effort], "Self-assessed", "neutral"), unsafe_allow_html=True)

st.markdown(glow_divider(), unsafe_allow_html=True)

# ── Charts ─────────────────────────────────────────────────────────────────
ch1, ch2 = st.columns(2)

with ch1:
    st.markdown("#### 📊 Multi-Metric Growth")
    st.plotly_chart(
        line_chart(hist_df, "Month", ["CGPA (×10)", "Skill Score", "Effort Index"],
                   "Semester Growth Trajectory"),
        use_container_width=True
    )

with ch2:
    st.markdown("#### 🏆 Milestones & Achievements")

    # Dynamically generate achievements from profile
    achievements_raw = []
    if projects >= 1:  achievements_raw.append(("🤖", f"First Project Completed", "Semester 1"))
    if projects >= 3:  achievements_raw.append(("🚀", f"{projects} Projects Done", "This Semester"))
    if profile.get("hackathons", 0) >= 1:
        achievements_raw.append(("💻", "Hackathon Participant", "Recent"))
    if cgpa >= 8.0:    achievements_raw.append(("📚", "CGPA ≥ 8.0 Achieved", "Current"))
    if cgpa >= 9.0:    achievements_raw.append(("🏅", "Dean's List Candidate", "Current"))
    if profile.get("internships", 0) >= 1:
        achievements_raw.append(("💼", "Internship Experience", "Completed"))
    if profile.get("certifications", 0) >= 1:
        achievements_raw.append(("🎖️", f"{profile['certifications']} Certifications", "Earned"))

    if not achievements_raw:
        achievements_raw = [("🌱", "Journey Just Started", "Keep going!")]

    for icon, name, date in achievements_raw:
        st.markdown(achievement_item(icon, name, date), unsafe_allow_html=True)

st.markdown(glow_divider(), unsafe_allow_html=True)

# ── CGPA Forecast ─────────────────────────────────────────────────────────
st.markdown("#### 🔮 CGPA Forecast — Next 5 Months")

future_months = ["Feb", "Mar", "Apr", "May", "Jun"]
# Simple linear projection with diminishing returns near 10
growth_rate = trend_factor if trend_factor > 0 else 0.05
predicted = [round(min(10.0, cgpa + (i + 1) * growth_rate * (1 - cgpa / 11)), 2) for i in range(5)]

st.plotly_chart(
    area_chart(future_months, predicted, "CGPA Projection (AI-estimated)", height=300),
    use_container_width=True,
)

col_a, col_b = st.columns(2)
with col_a:
    st.markdown(f"""
    <div class="glass-panel">
        <div style="font-size:0.8rem; color:#7A90B0; margin-bottom:0.3rem;">Projected End-of-Year CGPA</div>
        <div style="font-family:'Syne',sans-serif; font-size:2.5rem; font-weight:800; color:#00D4FF;">{predicted[-1]}</div>
        <div style="font-size:0.8rem; color:#00E887;">Based on {trend.lower()} trend</div>
    </div>
    """, unsafe_allow_html=True)

with col_b:
    st.markdown(f"""
    <div class="glass-panel">
        <div style="font-size:0.8rem; color:#7A90B0; margin-bottom:0.3rem;">Target Recommendation</div>
        <div style="font-family:'Syne',sans-serif; font-size:1.5rem; font-weight:700; color:#E2E8F0;">
            {'Maintain Pace 🎯' if trend == 'Improving' else 'Increase Effort 🔥' if trend == 'Stable' else 'Urgent Recovery 🚨'}
        </div>
        <div style="font-size:0.8rem; color:#7A90B0; margin-top:0.5rem;">
            {'+0.5 CGPA' if cgpa < 9.0 else 'Excellence level — maintain'} is the immediate target
        </div>
    </div>
    """, unsafe_allow_html=True)
