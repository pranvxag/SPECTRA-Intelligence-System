"""
components/sidebar.py  —  Shared sidebar rendered on every page
Always shows: quick profile form + live intelligence stats + quick actions
"""
import streamlit as st
from components.styles import load_css
from utils.career_engine import compute_intelligence_score, rank_careers


def render_sidebar():
    """Call at the top of every page."""
    load_css()

    # Force sidebar always open - belt & braces
    st.markdown("""
    <style>
    [data-testid="stSidebarCollapseButton"],
    [data-testid="collapsedControl"] { display: none !important; }
    section[data-testid="stSidebar"] {
        transform: none !important;
        min-width: 21rem !important;
        display: flex !important;
    }
    </style>
    """, unsafe_allow_html=True)

    profile     = st.session_state.get("student_profile", {})
    intel_score = st.session_state.get("intelligence_score", 0)
    career_fit  = st.session_state.get("top_career_fit", 0)
    ranked      = st.session_state.get("ranked_careers", [])

    with st.sidebar:

        # ── SPECTRA Clickable Logo ──────────────────────────────────────
        st.markdown("""
        <style>
        @keyframes logoGlow {
            0%   { box-shadow: 0 0 10px rgba(0,212,255,0.2); }
            50%  { box-shadow: 0 0 25px rgba(0,212,255,0.5); }
            100% { box-shadow: 0 0 10px rgba(0,212,255,0.2); }
        }
        @keyframes textShimmer {
            0%   { background-position: -200% center; }
            100% { background-position: 200% center; }
        }
        .spectra-logo-btn {
            display: block;
            width: 100%;
            background: rgba(0,212,255,0.04);
            border: 1px solid rgba(0,212,255,0.15);
            border-radius: 14px;
            padding: 0.9rem 1.1rem;
            margin-bottom: 1rem;
            cursor: pointer;
            text-decoration: none;
            transition: all 0.3s ease;
            animation: logoGlow 3s ease-in-out infinite;
        }
        .spectra-logo-btn:hover {
            background: rgba(0,212,255,0.1) !important;
            border-color: rgba(0,212,255,0.5) !important;
            transform: scale(1.02);
            animation: none;
            box-shadow: 0 0 30px rgba(0,212,255,0.4);
        }
        .spectra-logo-text {
            font-family: 'Syne', sans-serif;
            font-size: 1.7rem;
            font-weight: 800;
            background: linear-gradient(90deg, #fff 0%, #00D4FF 40%, #fff 60%, #00D4FF 100%);
            background-size: 200% auto;
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            letter-spacing: -1px;
            animation: textShimmer 4s linear infinite;
        }
        .spectra-logo-sub {
            font-size: 0.6rem;
            color: #2A3A58;
            letter-spacing: 2.5px;
            text-transform: uppercase;
            margin-top: 0.1rem;
        }
        /* Hide default sidebar nav page links */
        section[data-testid="stSidebar"] [data-testid="stSidebarNav"],
        section[data-testid="stSidebar"] ul { display: none !important; }
        /* Fix expander arrow_double text bug */
        [data-testid="stExpanderToggleIcon"] { display: none !important; }
        details summary::-webkit-details-marker { display: none; }
        </style>
        <a class="spectra-logo-btn" href="/" target="_self">
            <div class="spectra-logo-text">⚡ SPECTRA</div>
            <div class="spectra-logo-sub">Intelligence System · Home</div>
        </a>
        """, unsafe_allow_html=True)

        # ── Student Profile Header ──────────────────────────────────────
        st.image("https://img.icons8.com/fluency/96/student-center.png", width=60)
        st.markdown("""
        <div style="margin-bottom:0.3rem;">
            <div style="font-family:'Syne',sans-serif; font-size:1.1rem; font-weight:700;
                        color:#00D4FF;">👤 Student Profile</div>
        </div>
        """, unsafe_allow_html=True)

        # ── Quick Profile Form (always visible) ────────────────────────
        with st.expander("📋 Quick Student Info", expanded=True):
            sb_name     = st.text_input("Name",       value=profile.get("name", ""), placeholder="Your name")
            sb_id       = st.text_input("Student ID", value=profile.get("student_id", ""), placeholder="e.g. CS2024001")
            sb_semester = st.selectbox("Current Semester", list(range(1, 9)),
                                       index=profile.get("semester", 1) - 1)
            sb_branch   = st.selectbox("Branch",
                                       ["Computer Science", "Electronics", "Mechanical",
                                        "Civil", "Electrical", "Information Technology", "Other"],
                                       index=["Computer Science", "Electronics", "Mechanical",
                                              "Civil", "Electrical", "Information Technology", "Other"]
                                       .index(profile.get("branch", "Computer Science"))
                                       if profile.get("branch", "Computer Science") in
                                       ["Computer Science", "Electronics", "Mechanical",
                                        "Civil", "Electrical", "Information Technology", "Other"] else 0)

            if st.button("💾 Save Quick Profile", use_container_width=True):
                # Merge quick form into existing profile
                updated = {**profile,
                           "name": sb_name,
                           "student_id": sb_id,
                           "semester": sb_semester,
                           "branch": sb_branch}
                st.session_state.student_profile = updated

                # Recompute scores if profile has skills
                if updated.get("skills"):
                    ranked_new = rank_careers(updated)
                    st.session_state.ranked_careers    = ranked_new
                    st.session_state.top_career_fit    = ranked_new[0]["fit"] if ranked_new else 0
                    st.session_state.intelligence_score = compute_intelligence_score(updated)

                st.success("✅ Saved!")
                st.rerun()

        st.divider()

        # ── Intelligence Stats ─────────────────────────────────────────
        st.markdown("### 🧠 Intelligence Stats")

        col1, col2 = st.columns(2)
        with col1:
            cgpa_val = profile.get("cgpa", 0)
            st.metric("Intelligence Score", intel_score if intel_score else "—",
                      delta="+5" if intel_score else None)
            st.metric("Growth Rate",
                      f"{profile.get('effort', 0) * 3}%" if profile.get("effort") else "—",
                      delta="+2%" if profile.get("effort") else None)
        with col2:
            st.metric("Career Fit",
                      f"{career_fit}%" if career_fit else "—",
                      delta="+8%" if career_fit else None)
            effort_labels = {1: "Low", 2: "Fair", 3: "Good", 4: "High", 5: "Elite"}
            effort_val = profile.get("effort", 0)
            st.metric("Consistency",
                      effort_labels.get(effort_val, "—"),
                      delta="↑" if effort_val >= 4 else None)

        st.divider()

        # ── Quick Actions ──────────────────────────────────────────────
        st.markdown("### ⚡ Quick Actions")

        if st.button("📊 Generate New Analysis", use_container_width=True):
            st.switch_page("pages/0_Student_Intake.py")

        if profile.get("skills"):
            if st.button("🎯 View Intelligence Hub", use_container_width=True):
                st.switch_page("pages/1_Intelligence_Hub.py")

            # Real CSV download
            import pandas as pd, io
            report_data = {
                "Field": ["Name", "Branch", "Semester", "CGPA", "Intelligence Score",
                          "Top Career", "Career Fit", "Effort"],
                "Value": [
                    profile.get("name", "—"),
                    profile.get("branch", "—"),
                    profile.get("semester", "—"),
                    profile.get("cgpa", "—"),
                    intel_score,
                    ranked[0]["title"] if ranked else "—",
                    f"{career_fit}%" if career_fit else "—",
                    effort_labels.get(profile.get("effort", 0), "—"),
                ]
            }
            csv = pd.DataFrame(report_data).to_csv(index=False)
            st.download_button(
                "📥 Download Report",
                data=csv,
                file_name=f"spectra_{profile.get('name','student').replace(' ','_')}.csv",
                mime="text/csv",
                use_container_width=True,
            )
        else:
            st.caption("Complete the intake form to unlock full analysis.")

        st.divider()
        st.markdown("""
        <div style="font-size:0.72rem; color:#2A3A58; text-align:center; padding-top:0.3rem;">
            SPECTRA v2.0 · IIT Techkriti 2026
        </div>
        """, unsafe_allow_html=True)
