"""
pages/6_About.py — The Science Behind SPECTRA
"""
import streamlit as st
from components.styles import load_css
from components.sidebar import render_sidebar
from components.navbar import render_navbar
from components.cards import section_title, about_feature, formula_box, glow_divider

st.set_page_config(page_title="SPECTRA — About", page_icon="❓", layout="wide")
load_css()
from utils.auth import require_login
require_login()
render_sidebar()
st.session_state["_current_page"] = "About"
render_navbar()

st.markdown(section_title("❓", "The Science Behind", "SPECTRA"), unsafe_allow_html=True)

# ── Mission ───────────────────────────────────────────────────────────────
st.markdown("""
<div class="glass-panel" style="margin-bottom:1.5rem; text-align:center;">
    <div style="font-family:'Syne',sans-serif; font-size:1.6rem; font-weight:800;
                background: linear-gradient(135deg, #fff 30%, #00D4FF);
                -webkit-background-clip:text; -webkit-text-fill-color:transparent; margin-bottom:0.5rem;">
        Turning Student Data into Career Clarity
    </div>
    <div style="color:#7A90B0; max-width:700px; margin:0 auto; font-size:0.95rem; line-height:1.7;">
        SPECTRA goes beyond GPA. It synthesizes academic performance, interests, effort patterns,
        and skill self-assessments into a multi-dimensional intelligence profile — then maps it to
        careers using a transparent, weighted scoring engine.
    </div>
</div>
""", unsafe_allow_html=True)

# ── Core modules ──────────────────────────────────────────────────────────
st.markdown("#### 🏗️ Core Modules")
col1, col2, col3 = st.columns(3)
modules = [
    ("🎯", "Intelligence Hub",
     "Aggregates 12+ profile dimensions into a composite score. Radar chart maps your unique skill fingerprint."),
    ("🗺️", "Career Mapper",
     "Weighted multi-factor scoring (Academic 25%, Interest 30%, Skill 25%, Effort 20%) generates personalised career fit scores."),
    ("📊", "SWOT Analysis",
     "Rule-based engine generates personalised SWOT from profile data — strengths, weaknesses, opportunities, and threats tailored to you."),
    ("📈", "Growth Tracker",
     "Simulates historical trajectory and projects future CGPA using trend analysis. Tracks milestones and achievements."),
    ("🏛️", "Institutional View",
     "Aggregated analytics for administrators — department performance, career preference distributions, and at-risk identification."),
    ("✏️", "Student Intake",
     "Rich multi-section form captures identity, academics, interests, skills, activities, and goals — feeds every other module."),
]

for i, (icon, title, desc) in enumerate(modules):
    col = [col1, col2, col3][i % 3]
    with col:
        st.markdown(about_feature(icon, title, desc), unsafe_allow_html=True)

st.markdown(glow_divider(), unsafe_allow_html=True)

# ── Scoring formula ────────────────────────────────────────────────────────
st.markdown("#### 📐 Career Fit Formula")
st.markdown(formula_box(
    "Career Fit Score = (Academic Score × 0.25) + (Interest Alignment × 0.30) "
    "+ (Skill Match × 0.25) + (Effort Level × 0.20)"
), unsafe_allow_html=True)

c1, c2 = st.columns(2)
with c1:
    st.markdown("""
    <div class="glass-panel">
        <div style="font-family:'Syne',sans-serif; font-weight:700; color:#E2E8F0; margin-bottom:1rem;">
            Weight Rationale
        </div>
        <div class="swot-item"><div class="swot-dot" style="background:#00D4FF;"></div>
            <span><strong style="color:#00D4FF;">Interest (30%)</strong> — Biggest driver of long-term career success and satisfaction</span></div>
        <div class="swot-item"><div class="swot-dot" style="background:#FFB800;"></div>
            <span><strong style="color:#FFB800;">Academic (25%)</strong> — Baseline signal for cognitive ability and discipline</span></div>
        <div class="swot-item"><div class="swot-dot" style="background:#00E887;"></div>
            <span><strong style="color:#00E887;">Skill (25%)</strong> — Current competency match to career requirements</span></div>
        <div class="swot-item"><div class="swot-dot" style="background:#A78BFA;"></div>
            <span><strong style="color:#A78BFA;">Effort (20%)</strong> — Proxy for work ethic and growth potential</span></div>
    </div>
    """, unsafe_allow_html=True)

with c2:
    st.markdown("""
    <div class="glass-panel">
        <div style="font-family:'Syne',sans-serif; font-weight:700; color:#E2E8F0; margin-bottom:1rem;">
            Intelligence Score Formula
        </div>
        <div style="font-family:'Courier New', monospace; color:#00D4FF; font-size:0.85rem; line-height:2;">
            Intelligence = Academic (30%)<br>
            &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;+ Skill Average (40%)<br>
            &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;+ Effort Score (20%)<br>
            &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;+ Project Portfolio (10%)
        </div>
        <div style="font-size:0.78rem; color:#4A5A7A; margin-top:0.8rem;">
            Resulting composite score: 0–100
        </div>
    </div>
    """, unsafe_allow_html=True)

st.markdown(glow_divider(), unsafe_allow_html=True)

# ── Tech stack ────────────────────────────────────────────────────────────
st.markdown("#### 🛠️ Technology Stack")
stack = [
    ("🐍", "Python 3.11+", "Core language"),
    ("⚡", "Streamlit", "Multi-page web framework"),
    ("🐼", "Pandas + NumPy", "Data processing"),
    ("📊", "Plotly", "Interactive visualisations"),
    ("🤖", "Scikit-learn", "ML pipeline (extensible)"),
    ("🎨", "Custom CSS", "Glassmorphism design system"),
]
cols = st.columns(6)
for col, (icon, name, role) in zip(cols, stack):
    with col:
        st.markdown(f"""
        <div class="about-feature" style="padding:1rem;">
            <div class="about-icon" style="font-size:1.8rem;">{icon}</div>
            <div class="about-feature-title" style="font-size:0.85rem;">{name}</div>
            <div class="about-feature-desc" style="font-size:0.75rem;">{role}</div>
        </div>
        """, unsafe_allow_html=True)

st.markdown(glow_divider(), unsafe_allow_html=True)

# ── Footer ─────────────────────────────────────────────────────────────────
st.markdown("""
<div style="text-align:center; padding: 2rem; color:#2A3A58; font-size:0.8rem;">
    <div style="font-family:'Syne',sans-serif; font-size:1.2rem; color:#4A5A7A; margin-bottom:0.5rem;">
        ⚡ SPECTRA v2.0
    </div>
    Built for IIT Techkriti 2026 Innovation Challenge<br>
    Student Intelligence &amp; Career Alignment Platform
</div>
""", unsafe_allow_html=True)