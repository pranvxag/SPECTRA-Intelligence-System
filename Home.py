"""
Home.py — SPECTRA Entry Point
Renders the landing page with hero, nav, and quick overview.
"""
import streamlit as st
from components.styles import load_css
from components.sidebar import render_sidebar

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

st.set_page_config(
    page_title="SPECTRA — Student Intelligence System",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded",
)

load_css()
render_sidebar()

# ── Session state defaults ─────────────────────────────────────────────────
if "student_profile" not in st.session_state:
    st.session_state.student_profile = {}
if "top_career_fit" not in st.session_state:
    st.session_state.top_career_fit = 0

# ── Hero Header ────────────────────────────────────────────────────────────
st.markdown("""
<div class="spectra-hero">
    <div class="hero-wordmark">⚡ SPECTRA</div>
    <p class="hero-tagline">Student Intelligence &amp; Career Guidance System</p>
    <div class="hero-pill">🏆 IIT Techkriti 2026 Innovation Challenge</div>
</div>
""", unsafe_allow_html=True)

# ── Navigation Row ─────────────────────────────────────────────────────────
pages = [
    ("🎯", "Intelligence Hub",   "pages/1_Intelligence_Hub.py"),
    ("🗺️", "Career Mapper",      "pages/2_Career_Mapper.py"),
    ("📊", "SWOT Analysis",      "pages/3_SWOT_Analysis.py"),
    ("📈", "Growth Tracker",     "pages/4_Growth_Tracker.py"),
    ("🏛️", "Institutional View", "pages/5_Institutional_View.py"),
    ("❓", "About",              "pages/6_About.py"),
]

cols = st.columns(len(pages) + 1)
for i, (icon, label, path) in enumerate(pages):
    with cols[i]:
        if st.button(f"{icon} {label}", use_container_width=True, key=f"nav_{i}"):
            st.switch_page(path)

with cols[-1]:
    if st.button("🚀 ANALYZE ME", use_container_width=True, type="primary", key="cta"):
        st.switch_page("pages/0_Student_Intake.py")

# ── Divider ────────────────────────────────────────────────────────────────
st.markdown('<div class="glow-divider"></div>', unsafe_allow_html=True)

# ── Platform Overview ──────────────────────────────────────────────────────
st.markdown("""
<div class="section-title">🌐 What is <span class="accent">SPECTRA?</span></div>
""", unsafe_allow_html=True)

c1, c2, c3 = st.columns(3)
features = [
    ("🧠", "AI-Powered Intelligence",
     "Goes beyond grades — analyses behaviour, effort, interest alignment and growth trajectory to generate a holistic student intelligence score."),
    ("🎯", "Career Alignment Engine",
     "Weighted multi-factor scoring matches you to careers based on your unique academic + skill + interest fingerprint — not generic lists."),
    ("📊", "Data-Driven SWOT",
     "Dynamically generated SWOT analysis with actionable roadmaps tailored specifically to your profile, semester, and career targets."),
]

from components.cards import about_feature
for col, (icon, title, desc) in zip([c1, c2, c3], features):
    with col:
        st.markdown(about_feature(icon, title, desc), unsafe_allow_html=True)

st.markdown('<div class="glow-divider"></div>', unsafe_allow_html=True)

# ── Stats Row ──────────────────────────────────────────────────────────────
st.markdown("""
<div class="section-title">📐 Platform <span class="accent">by the Numbers</span></div>
""", unsafe_allow_html=True)

s1, s2, s3, s4 = st.columns(4)
stats = [
    ("6", "Career Pathways Mapped"),
    ("12+", "Intelligence Dimensions"),
    ("4", "Growth Metrics Tracked"),
    ("100%", "Data-Driven Decisions"),
]

from components.cards import metric_card
for col, (val, label) in zip([s1, s2, s3, s4], stats):
    with col:
        st.markdown(metric_card(label, val, trend_dir="neutral"), unsafe_allow_html=True)

# ── CTA Block ──────────────────────────────────────────────────────────────
st.markdown("<br>", unsafe_allow_html=True)
st.markdown("""
<div style="text-align:center; padding: 2.5rem; background: rgba(0,212,255,0.04);
            border: 1px solid rgba(0,212,255,0.15); border-radius: 24px;">
    <div style="font-family:'Syne',sans-serif; font-size:1.8rem; font-weight:800;
                color:#E2E8F0; margin-bottom:0.5rem;">
        Ready to discover your intelligence profile?
    </div>
    <div style="color:#7A90B0; margin-bottom:1.5rem; font-size:0.95rem;">
        Fill out the student intake form and get your personalised career alignment report in seconds.
    </div>
</div>
""", unsafe_allow_html=True)

_, mid, _ = st.columns([2, 1, 2])
with mid:
    if st.button("🚀 Start Analysis →", use_container_width=True, type="primary"):
        st.switch_page("pages/0_Student_Intake.py")
