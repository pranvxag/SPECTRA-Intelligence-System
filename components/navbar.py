"""
components/navbar.py — Shared top navigation bar
Import and call render_navbar() at the top of EVERY page.
"""
import streamlit as st


def render_navbar():
    """Renders the SPECTRA nav bar with page buttons. Call after set_page_config."""

    st.markdown("""
    <style>
    /* Nav container override */
    .spectra-nav-row { margin-bottom: 1.5rem; }
    div[data-testid="stHorizontalBlock"] .stButton > button {
        background: rgba(20, 29, 46, 0.9) !important;
        border: 1px solid #1C2740 !important;
        color: #7A90B0 !important;
        border-radius: 12px !important;
        font-family: 'Plus Jakarta Sans', sans-serif !important;
        font-weight: 500 !important;
        font-size: 0.82rem !important;
        padding: 0.55rem 0.4rem !important;
        transition: all 0.2s ease !important;
        white-space: nowrap !important;
        box-shadow: none !important;
        width: 100% !important;
    }
    div[data-testid="stHorizontalBlock"] .stButton > button:hover {
        background: rgba(0, 212, 255, 0.08) !important;
        border-color: rgba(0, 212, 255, 0.3) !important;
        color: #00D4FF !important;
        transform: translateY(-2px) !important;
        box-shadow: 0 4px 15px rgba(0, 212, 255, 0.15) !important;
    }
    div[data-testid="stHorizontalBlock"] .stButton > button[kind="primary"] {
        background: linear-gradient(135deg, #00D4FF, #0099CC) !important;
        border-color: transparent !important;
        color: #000 !important;
        font-weight: 700 !important;
        box-shadow: 0 4px 20px rgba(0, 212, 255, 0.35) !important;
    }
    div[data-testid="stHorizontalBlock"] .stButton > button[kind="primary"]:hover {
        transform: translateY(-3px) !important;
        box-shadow: 0 8px 30px rgba(0, 212, 255, 0.5) !important;
        color: #000 !important;
    }
    </style>
    """, unsafe_allow_html=True)

    current = st.session_state.get("_current_page", "")

    pages = [
        ("🎯", "Intelligence Hub",   "pages/1_Intelligence_Hub.py"),
        ("🗺️", "Career Mapper",      "pages/2_Career_Mapper.py"),
        ("📊", "SWOT Analysis",      "pages/3_SWOT_Analysis.py"),
        ("📈", "Growth Tracker",     "pages/4_Growth_Tracker.py"),
        ("🏛️", "Institutional",      "pages/5_Institutional_View.py"),
        ("🤖", "Ask SPECTRA",        "pages/7_Ask_Spectra.py"),
        ("❓", "About",              "pages/6_About.py"),
    ]

    cols = st.columns(len(pages) + 1)

    for i, (icon, label, path) in enumerate(pages):
        with cols[i]:
            is_active = current == label
            if st.button(
                f"{icon} {label}",
                key=f"nav_top_{label}",
                type="primary" if is_active else "secondary",
                use_container_width=True,
            ):
                st.switch_page(path)

    with cols[-1]:
        if st.button("🚀 ANALYZE ME", key="nav_analyze", type="primary", use_container_width=True):
            st.switch_page("pages/0_Student_Intake.py")

    # Thin cyan divider line under nav
    st.markdown('<div class="glow-divider"></div>', unsafe_allow_html=True)
