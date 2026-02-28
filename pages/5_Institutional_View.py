"""
pages/5_Institutional_View.py — College-Level Analytics Dashboard
"""
import streamlit as st
import pandas as pd
import numpy as np
from components.styles import load_css
from components.sidebar import render_sidebar
from components.cards import section_title, metric_card, glow_divider
from components.charts import stacked_bar, line_chart, donut_chart

st.set_page_config(page_title="SPECTRA — Institutional View", page_icon="🏛️", layout="wide")
load_css()
render_sidebar()

st.markdown(section_title("🏛️", "Institutional Intelligence", "Dashboard"), unsafe_allow_html=True)

# ── Admin banner ──────────────────────────────────────────────────────────
st.markdown("""
<div class="glass-panel" style="margin-bottom:1.5rem;">
    <div style="display:flex; justify-content:space-between; align-items:center; flex-wrap:wrap; gap:1rem;">
        <div>
            <div style="font-family:'Syne',sans-serif; font-weight:700; font-size:1rem; color:#E2E8F0;">
                📍 Institute Overview — Academic Year 2025–26
            </div>
            <div style="font-size:0.8rem; color:#7A90B0; margin-top:0.2rem;">
                Aggregated analytics across all departments. Data refreshed every semester.
            </div>
        </div>
        <span class="pill pill-amber">Admin View</span>
    </div>
</div>
""", unsafe_allow_html=True)

# ── Top KPIs ──────────────────────────────────────────────────────────────
k1, k2, k3, k4 = st.columns(4)
kpis = [
    (k1, "Total Students",        "2,847",  "↑ 8% from 2024",   "up"),
    (k2, "Avg Intelligence Score","76.4",    "↑ 5.2 points",     "up"),
    (k3, "At-Risk Students",      "342",     "↓ 12% from last sem","up"),
    (k4, "Placement Rate",        "89%",     "↑ 4% from 2024",   "up"),
]
for col, label, val, trend, tdir in kpis:
    with col:
        st.markdown(metric_card(label, val, trend, tdir), unsafe_allow_html=True)

st.markdown(glow_divider(), unsafe_allow_html=True)

# ── Department analytics ───────────────────────────────────────────────────
c1, c2 = st.columns(2)

with c1:
    st.markdown("#### 🎓 Career Preferences by Department")
    dept_df = pd.DataFrame({
        "Department": ["CSE", "ECE", "ME", "Civil", "EE", "IT"],
        "AI/ML":      [45, 28, 10,  6, 20, 38],
        "Core":       [15, 42, 60, 68, 50, 20],
        "Management": [25, 18, 22, 18, 20, 22],
        "Research":   [15, 12,  8,  8, 10, 20],
    })
    st.plotly_chart(
        stacked_bar(dept_df, "Department", ["AI/ML", "Core", "Management", "Research"],
                    "Career Preference Distribution (%)"),
        use_container_width=True
    )

with c2:
    st.markdown("#### 📊 Campus CGPA Distribution")
    # Simulated normal distribution
    np.random.seed(42)
    cgpa_buckets = ["< 5.0", "5.0–6.0", "6.0–7.0", "7.0–8.0", "8.0–9.0", "9.0+"]
    cgpa_counts  = [52, 180, 480, 920, 810, 405]
    cgpa_df = pd.DataFrame({"CGPA Range": cgpa_buckets, "Students": cgpa_counts})

    st.plotly_chart(
        donut_chart(cgpa_buckets, cgpa_counts, "CGPA Distribution Across Campus"),
        use_container_width=True
    )

st.markdown(glow_divider(), unsafe_allow_html=True)

# ── Trend over semesters ───────────────────────────────────────────────────
c3, c4 = st.columns(2)

with c3:
    st.markdown("#### 📈 Intelligence Score Trend (Semester-wise)")
    semester_df = pd.DataFrame({
        "Semester": ["Sem 1", "Sem 2", "Sem 3", "Sem 4", "Sem 5", "Sem 6"],
        "Avg Intelligence": [68.2, 70.5, 71.8, 73.4, 75.1, 76.4],
        "Avg Career Fit":   [55.0, 58.3, 61.2, 64.8, 68.5, 71.2],
        "At-Risk %":        [18.0, 16.5, 15.8, 14.2, 13.5, 12.0],
    })
    st.plotly_chart(
        line_chart(semester_df, "Semester",
                   ["Avg Intelligence", "Avg Career Fit"],
                   "Campus Intelligence & Career Fit Trend"),
        use_container_width=True
    )

with c4:
    st.markdown("#### ⚠️ At-Risk Breakdown")
    risk_categories = ["Academic Risk", "Misalignment Risk", "Engagement Risk", "On Track"]
    risk_values     = [180, 95, 67, 2505]
    st.plotly_chart(
        donut_chart(risk_categories, risk_values, "Student Risk Distribution"),
        use_container_width=True
    )

st.markdown(glow_divider(), unsafe_allow_html=True)

# ── Department table ───────────────────────────────────────────────────────
st.markdown("#### 🗂️ Department Performance Summary")

dept_summary = pd.DataFrame({
    "Department":       ["Computer Science", "Electronics", "Mechanical", "Civil", "Electrical", "IT"],
    "Students":         [640, 520, 480, 380, 410, 417],
    "Avg CGPA":         [8.1, 7.9, 7.4, 7.2, 7.6, 8.0],
    "Avg Career Fit %": [78, 72, 61, 58, 65, 76],
    "At-Risk Count":    [48, 62, 95, 88, 71, 78],
    "Top Career":       ["AI/ML", "Embedded", "Core Engg", "Core Engg", "Power", "Data Science"],
})

st.dataframe(
    dept_summary.style
        .background_gradient(subset=["Avg CGPA", "Avg Career Fit %"], cmap="Blues")
        .highlight_max(subset=["Avg CGPA", "Avg Career Fit %"], color="#00E88722")
        .highlight_min(subset=["At-Risk Count"], color="#00E88722"),
    use_container_width=True,
    hide_index=True,
)

st.markdown(glow_divider(), unsafe_allow_html=True)

# ── Downloadable summary ───────────────────────────────────────────────────
csv = dept_summary.to_csv(index=False)
st.download_button(
    "📥 Download Department Report (CSV)",
    data=csv,
    file_name="spectra_institutional_report.csv",
    mime="text/csv",
    use_container_width=False,
)
