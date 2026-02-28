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

    profile     = st.session_state.get("student_profile", {})
    intel_score = st.session_state.get("intelligence_score", 0)
    career_fit  = st.session_state.get("top_career_fit", 0)
    ranked      = st.session_state.get("ranked_careers", [])

    with st.sidebar:

        # ── Brand ──────────────────────────────────────────────────────
        st.image("https://img.icons8.com/fluency/96/student-center.png", width=72)
        st.markdown("""
        <div style="margin-bottom:0.5rem;">
            <div class="sidebar-brand">👤 Student Profile</div>
        </div>
        """, unsafe_allow_html=True)

        # ── Quick Profile Form (always visible) ────────────────────────
        with st.expander("Quick Student Info", expanded=True):
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