"""
components/sidebar.py  —  Shared sidebar rendered on every page
"""
import streamlit as st
from components.styles import load_css
from utils.career_engine import compute_intelligence_score


def render_sidebar():
    """Call at the top of every page."""
    load_css()

    profile = st.session_state.get("student_profile", {})
    intel_score = compute_intelligence_score(profile) if profile else 0
    career_fit  = st.session_state.get("top_career_fit", 0)

    with st.sidebar:
        # Brand
        st.markdown("""
        <div style="padding: 0.5rem 0 1rem;">
            <div class="sidebar-brand">⚡ SPECTRA</div>
            <div style="font-size:0.75rem; color:#4A5A7A; letter-spacing:1px;">INTELLIGENCE SYSTEM</div>
        </div>
        """, unsafe_allow_html=True)

        st.divider()

        # Student identity
        if profile:
            st.markdown(f"""
            <div style="margin-bottom:1rem;">
                <div style="font-size:1rem; font-weight:700; color:#E2E8F0;">
                    {profile.get('name', 'Student')}
                </div>
                <div style="font-size:0.78rem; color:#4A5A7A;">
                    {profile.get('student_id', '—')} &nbsp;·&nbsp; Sem {profile.get('semester', '—')}
                </div>
                <div style="font-size:0.78rem; color:#4A5A7A; margin-top:0.2rem;">
                    {profile.get('branch', '—')}
                </div>
            </div>
            """, unsafe_allow_html=True)
        else:
            st.markdown("""
            <div style="margin-bottom:1rem; color:#4A5A7A; font-size:0.85rem;">
                No profile yet — complete the intake form first.
            </div>
            """, unsafe_allow_html=True)

        st.divider()

        # Stats grid
        st.markdown("**🧠 Intelligence Stats**")

        col1, col2 = st.columns(2)
        with col1:
            cgpa_val = profile.get("cgpa", 0) if profile else 0
            st.metric("Intelligence", f"{intel_score}", delta="+5" if intel_score else None)
            st.metric("CGPA", f"{cgpa_val:.1f}" if cgpa_val else "—")
        with col2:
            st.metric("Career Fit", f"{career_fit}%" if career_fit else "—", delta="+3%" if career_fit else None)
            effort = profile.get("effort", 0)
            labels = {1: "Low", 2: "Fair", 3: "Good", 4: "High", 5: "Elite"}
            st.metric("Effort", labels.get(effort, "—"))

        st.divider()

        # Quick actions
        st.markdown("**⚡ Quick Actions**")
        if st.button("✏️ Update Profile", use_container_width=True):
            st.switch_page("pages/0_Student_Intake.py")

        if profile:
            if st.button("📊 View Analysis", use_container_width=True):
                st.switch_page("pages/1_Intelligence_Hub.py")

        st.divider()
        st.markdown("""
        <div style="font-size:0.72rem; color:#2A3A58; text-align:center; padding-top:0.5rem;">
            SPECTRA v2.0 · IIT Techkriti 2026
        </div>
        """, unsafe_allow_html=True)
