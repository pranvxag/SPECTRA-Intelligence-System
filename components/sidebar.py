"""
components/sidebar.py  —  Shared sidebar rendered on every page
Always shows: quick profile form + live intelligence stats + quick actions
"""
import streamlit as st
from components.styles import load_css
from utils.career_engine import compute_intelligence_score, rank_careers
from utils.database import db
from utils.auth import render_auth_sidebar


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
        @import url('https://fonts.googleapis.com/css2?family=Syne:wght@800&display=swap');

        @keyframes logoGlow {
            0%   { box-shadow: 0 0 10px rgba(0,212,255,0.15); border-color: rgba(0,212,255,0.2); }
            50%  { box-shadow: 0 0 28px rgba(0,212,255,0.45); border-color: rgba(0,212,255,0.6); }
            100% { box-shadow: 0 0 10px rgba(0,212,255,0.15); border-color: rgba(0,212,255,0.2); }
        }
        @keyframes shimmer {
            0%   { background-position: -200% center; }
            100% { background-position: 200% center; }
        }
        .spectra-logo-btn {
            display: flex !important;
            flex-direction: column;
            align-items: center;
            justify-content: center;
            text-align: center;
            width: 100%;
            background: rgba(0,212,255,0.03);
            border: 1px solid rgba(0,212,255,0.2);
            border-radius: 16px;
            padding: 1rem 1rem 0.8rem;
            margin-bottom: 1.2rem;
            cursor: pointer;
            text-decoration: none !important;
            -webkit-text-decoration: none !important;
            transition: all 0.3s ease;
            animation: logoGlow 3s ease-in-out infinite;
        }
        .spectra-logo-btn:hover {
            background: rgba(0,212,255,0.08) !important;
            transform: scale(1.02);
            animation: none;
            box-shadow: 0 0 35px rgba(0,212,255,0.4);
            border-color: rgba(0,212,255,0.7) !important;
        }
        .spectra-logo-text {
            font-family: 'Syne', sans-serif !important;
            font-size: 1.9rem;
            font-weight: 800;
            letter-spacing: -1px;
            line-height: 1;
            background: linear-gradient(90deg, #ffffff 0%, #00D4FF 35%, #ffffff 55%, #00D4FF 100%);
            background-size: 250% auto;
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
            animation: shimmer 3.5s linear infinite;
            text-decoration: none !important;
        }
        .spectra-logo-sub {
            font-size: 0.58rem;
            color: #2A3A58;
            letter-spacing: 3px;
            text-transform: uppercase;
            margin-top: 0.3rem;
            text-decoration: none !important;
        }
        /* Hide Streamlit default sidebar nav */
        section[data-testid="stSidebar"] [data-testid="stSidebarNav"],
        section[data-testid="stSidebar"] ul { display: none !important; }
        /* ── Nuclear fix for arrow_double bug on expander ── */
        [data-testid="stExpanderToggleIcon"],
        [data-testid="stExpanderToggleIcon"] * { display: none !important; }
        details > summary > span:first-child { display: none !important; }
        </style>
        <a class="spectra-logo-btn" href="/" target="_self">
            <div class="spectra-logo-text">⚡ SPECTRA</div>
            <div class="spectra-logo-sub">Intelligence System</div>
        </a>
        """, unsafe_allow_html=True)

        # ── Student Profile Header ──────────────────────────────────────
        st.image("https://img.icons8.com/fluency/96/student-center.png", width=60)
        st.markdown("""
        <div style="margin-bottom:0.8rem;">
            <div style="font-family:'Syne',sans-serif; font-size:1.1rem; font-weight:700;
                        color:#00D4FF;">👤 Student Profile</div>
            <div style="font-size:0.72rem; color:#4A5A7A; letter-spacing:1px;
                        text-transform:uppercase; margin-top:0.15rem;">Find or build your profile</div>
        </div>
        """, unsafe_allow_html=True)

        # ── Live student DB from SQLite ─────────────────────────────────
        STUDENT_DB = db.get_all_students()

        # If no students in DB yet, show placeholder
        if not STUDENT_DB:
            st.markdown("""
            <div style="background:rgba(255,184,0,0.07); border:1px solid rgba(255,184,0,0.2);
                        border-radius:10px; padding:0.7rem; margin-bottom:0.8rem; font-size:0.78rem; color:#FFB800;">
                ⚠️ No students in database yet.<br>
                Upload data via <strong>Institutional View → Upload Data</strong>
                or fill the intake form.
            </div>
            """, unsafe_allow_html=True)

        all_names = [s.get("name","") for s in STUDENT_DB]
        all_ids   = [s.get("student_id","") for s in STUDENT_DB]

        # ── Search fields ──────────────────────────────────────────────
        st.markdown("""
        <div style="font-size:0.72rem; font-weight:600; color:#4A5A7A;
                    text-transform:uppercase; letter-spacing:1.5px; margin-bottom:0.5rem;">
            🔍 Search Profile
        </div>
        """, unsafe_allow_html=True)

        # Name autocomplete
        sb_name = st.selectbox(
            "Student Name",
            options=[""] + all_names,
            index=0 if not profile.get("name") else
                  ([""] + all_names).index(profile["name"])
                  if profile.get("name") in all_names else 0,
            format_func=lambda x: "Type or select name..." if x == "" else x,
            help="Start typing to find a student by name",
        )

        # Auto-fill ID and college from name selection
        matched = next((s for s in STUDENT_DB if s.get("name") == sb_name), None)

        # Student ID autocomplete (auto-filled if name matched)
        sb_id = st.selectbox(
            "Student ID",
            options=[""] + all_ids,
            index=0 if not matched else
                  ([""] + all_ids).index(matched["student_id"]),
            format_func=lambda x: "Type or select ID..." if x == "" else x,
            help="Select or type student ID — auto-fills from name",
        )

        # If ID selected directly, override match
        if sb_id and not matched:
            matched = next((s for s in STUDENT_DB if s.get("student_id") == sb_id), None)

        # College (auto-filled, editable)
        colleges = ["","IIT Kanpur","IIT Bombay","IIT Delhi","IIT Madras",
                    "NIT Trichy","NIT Warangal","BITS Pilani","VIT Vellore","COEP Pune","Other"]
        auto_college = matched.get("college","") if matched else (profile.get("college","") if profile else "")
        col_index = colleges.index(auto_college) if auto_college in colleges else 0
        sb_college = st.selectbox("College / Institute", colleges,
                                  index=col_index,
                                  format_func=lambda x: "Select college..." if x == "" else x)

        # Show matched profile preview
        if matched:
            st.markdown(f"""
            <div style="background:rgba(0,212,255,0.06); border:1px solid rgba(0,212,255,0.2);
                        border-radius:10px; padding:0.7rem 0.9rem; margin:0.6rem 0; font-size:0.8rem;">
                <div style="color:#00D4FF; font-weight:700; margin-bottom:0.3rem;">
                    ✅ Profile Found
                </div>
                <div style="color:#E2E8F0;">{matched['name']}</div>
                <div style="color:#7A90B0;">{matched.get('branch','')} · CGPA {matched.get('cgpa','')}</div>
                <div style="color:#7A90B0;">{matched.get('college','')}</div>
            </div>
            """, unsafe_allow_html=True)

        # ── Action buttons ─────────────────────────────────────────────
        st.markdown("<div style='height:0.3rem;'></div>", unsafe_allow_html=True)

        if st.button("🔍 Analyse This Student", use_container_width=True, type="primary"):
            if matched:
                # Load full profile from DB (has all skills, interests etc.)
                sid = matched.get("student_id","")
                full = db.get_student(sid) if sid else None
                if full:
                    st.session_state.student_profile    = full
                    # Load cached career results
                    cached_careers = db.get_student_career_results(sid)
                    if cached_careers:
                        st.session_state.ranked_careers  = cached_careers
                        st.session_state.top_career_fit  = cached_careers[0]["fit"]
                    st.session_state.intelligence_score  = full.get("intelligence_score", 0)
                    st.session_state.ml_ran              = True  # skip re-analysis
                    st.success(f"✅ Loaded: {full['name']}")
                else:
                    # Partial profile from DB row
                    updated = {**profile, **matched}
                    st.session_state.student_profile = updated
                    st.session_state.ml_ran = False
                    st.info(f"⚡ Loaded {matched['name']} — run full intake for complete analysis")
                st.rerun()
            elif sb_name or sb_id:
                st.warning("⚠️ No match found. Build a new profile below.")
            else:
                st.warning("⚠️ Select a name or ID first.")

        st.markdown("<div style='height:0.3rem;'></div>", unsafe_allow_html=True)

        if st.button("✏️ Build Your Profile", use_container_width=True):
            st.switch_page("pages/0_Student_Intake.py")

        st.divider()

        # ── Intelligence Stats (shown only if profile loaded) ──────────
        if profile and profile.get("cgpa"):
            st.markdown("""
            <div style="font-size:0.72rem; font-weight:600; color:#4A5A7A;
                        text-transform:uppercase; letter-spacing:1.5px; margin-bottom:0.5rem;">
                🧠 Intelligence Stats
            </div>
            """, unsafe_allow_html=True)

            effort_labels = {1: "Low", 2: "Fair", 3: "Good", 4: "High", 5: "Elite"}
            col1, col2 = st.columns(2)
            with col1:
                st.metric("Intelligence", intel_score if intel_score else "—",
                          delta="+5" if intel_score else None)
                st.metric("Career Fit",
                          f"{career_fit}%" if career_fit else "—",
                          delta="+8%" if career_fit else None)
            with col2:
                st.metric("CGPA", f"{profile.get('cgpa', '—')}")
                effort_val = profile.get("effort", 0)
                st.metric("Effort", effort_labels.get(effort_val, "—"),
                          delta="↑" if effort_val >= 4 else None)

            if profile.get("skills"):
                st.markdown("<div style='height:0.3rem;'></div>", unsafe_allow_html=True)
                if st.button("🎯 View Full Analysis", use_container_width=True):
                    st.switch_page("pages/1_Intelligence_Hub.py")

                import pandas as pd
                effort_labels2 = {1: "Low", 2: "Fair", 3: "Good", 4: "High", 5: "Elite"}
                csv = pd.DataFrame({
                    "Field": ["Name","Branch","Semester","CGPA","Intelligence Score","Top Career","Career Fit","Effort"],
                    "Value": [
                        profile.get("name","—"), profile.get("branch","—"),
                        profile.get("semester","—"), profile.get("cgpa","—"),
                        intel_score,
                        ranked[0]["title"] if ranked else "—",
                        f"{career_fit}%" if career_fit else "—",
                        effort_labels2.get(profile.get("effort",0),"—"),
                    ]
                }).to_csv(index=False)
                st.download_button(
                    "📥 Download Report", data=csv,
                    file_name=f"spectra_{profile.get('name','student').replace(' ','_')}.csv",
                    mime="text/csv", use_container_width=True,
                )
            st.divider()

        st.markdown("""
        <div style="font-size:0.72rem; color:#2A3A58; text-align:center; padding-top:0.3rem;">
            SPECTRA v2.0 · IIT Techkriti 2026
        </div>
        """, unsafe_allow_html=True)

        # ── Auth / Logout widget ─────────────────────────────────
        st.markdown("<div style='height:0.5rem;'></div>", unsafe_allow_html=True)
        render_auth_sidebar()
