"""
pages/0_Student_Intake.py — Student Profile Intake Form
Collects real data that powers all other modules.
"""
import streamlit as st
from components.styles import load_css
from components.sidebar import render_sidebar
from utils.career_engine import rank_careers, compute_intelligence_score

st.set_page_config(page_title="SPECTRA — Student Intake", page_icon="✏️", layout="wide")
load_css()
render_sidebar()

# ── Page header ───────────────────────────────────────────────────────────
st.markdown("""
<div class="intake-hero">
    <h2>Build Your Intelligence Profile</h2>
    <p style="color:#7A90B0; font-size:0.95rem;">
        Answer honestly — the more accurate your inputs, the more precise your career alignment score.
    </p>
</div>
""", unsafe_allow_html=True)

# ── Form ──────────────────────────────────────────────────────────────────
with st.form("student_intake", clear_on_submit=False):

    # ── Section 1: Identity
    st.markdown("### 👤 Identity")
    c1, c2, c3 = st.columns(3)
    with c1:
        name       = st.text_input("Full Name", placeholder="e.g. Priya Sharma")
        student_id = st.text_input("Student ID", placeholder="e.g. CS2024001")
    with c2:
        branch   = st.selectbox("Branch", ["Computer Science", "Electronics", "Mechanical",
                                            "Civil", "Electrical", "Information Technology",
                                            "Chemical", "Other"])
        semester = st.selectbox("Current Semester", list(range(1, 9)))
    with c3:
        college = st.text_input("College / Institute", placeholder="e.g. IIT Kanpur")
        year    = st.selectbox("Year of Study", ["1st Year", "2nd Year", "3rd Year", "4th Year"])

    st.divider()

    # ── Section 2: Academics
    st.markdown("### 🎓 Academics")
    c1, c2, c3 = st.columns(3)
    with c1:
        cgpa = st.slider("Current CGPA", 0.0, 10.0, 7.5, step=0.1,
                         help="Your cumulative GPA on a 10-point scale")
    with c2:
        backlogs = st.number_input("Active Backlogs", 0, 20, 0)
    with c3:
        academic_trend = st.selectbox("Academic Trend", ["Improving", "Stable", "Declining"])

    st.divider()

    # ── Section 3: Interests
    st.markdown("### 💡 Interests")
    interest_options = {
        "programming":    "💻 Programming",
        "mathematics":    "📐 Mathematics",
        "ai_ml":          "🤖 AI / ML",
        "research":       "🔬 Research",
        "product_design": "🎨 Product Design",
        "management":     "📋 Management / Leadership",
        "core_engg":      "⚙️ Core Engineering",
        "finance":        "💰 Finance / Quant",
    }
    selected_interests = st.multiselect(
        "Select your top interests (pick all that genuinely apply)",
        options=list(interest_options.keys()),
        format_func=lambda k: interest_options[k],
        default=["programming", "ai_ml"],
    )

    st.divider()

    # ── Section 4: Skill Self-Assessment
    st.markdown("### 🔧 Skill Self-Assessment")
    st.caption("Rate yourself honestly on a scale of 0–100")

    c1, c2 = st.columns(2)
    with c1:
        skill_technical     = st.slider("Technical Skills",     0, 100, 70)
        skill_analytical    = st.slider("Analytical Thinking",  0, 100, 65)
        skill_creative      = st.slider("Creative Thinking",    0, 100, 50)
    with c2:
        skill_communication = st.slider("Communication",        0, 100, 55)
        skill_leadership    = st.slider("Leadership",           0, 100, 45)
        skill_consistency   = st.slider("Consistency / Discipline", 0, 100, 60)

    st.divider()

    # ── Section 5: Activities
    st.markdown("### 🏆 Activities & Portfolio")
    c1, c2, c3 = st.columns(3)
    with c1:
        projects        = st.number_input("Projects Completed", 0, 50, 1)
        internships     = st.number_input("Internships Done",   0, 10, 0)
    with c2:
        hackathons      = st.number_input("Hackathons Participated", 0, 30, 0)
        extracurriculars = st.number_input("Extracurricular Activities", 0, 20, 1)
    with c3:
        certifications  = st.number_input("Certifications Earned", 0, 30, 0)
        effort_level    = st.select_slider(
            "Effort Level (honest self-rating)",
            options=[1, 2, 3, 4, 5],
            value=3,
            format_func=lambda x: {1:"😴 Low", 2:"🙂 Fair", 3:"💪 Good", 4:"🔥 High", 5:"🚀 Elite"}[x],
        )

    st.divider()

    # ── Section 6: Goals
    st.markdown("### 🎯 Career Goals")
    c1, c2 = st.columns(2)
    with c1:
        career_goal = st.selectbox("Primary Career Goal", [
            "Not sure yet",
            "AI / ML Engineer",
            "Data Scientist",
            "Software Engineer",
            "Product Manager",
            "Research Scientist",
            "Core Engineering",
            "Entrepreneur",
            "Higher Studies (MS/PhD)",
            "Civil Services",
            "Finance / Quant",
        ])
    with c2:
        timeline = st.selectbox("Target Timeline", [
            "Placement (current final year)",
            "1–2 years",
            "2–3 years",
            "Post Masters/PhD",
        ])

    # ── Submit
    st.markdown("<br>", unsafe_allow_html=True)
    submitted = st.form_submit_button(
        "⚡ Generate My Intelligence Profile",
        use_container_width=True,
        type="primary",
    )

# ── Process form ──────────────────────────────────────────────────────────
if submitted:
    if not name.strip():
        st.error("Please enter your name to continue.")
        st.stop()

    profile = {
        # Identity
        "name":           name.strip(),
        "student_id":     student_id.strip() or "N/A",
        "branch":         branch,
        "semester":       semester,
        "college":        college.strip() or "Not specified",
        "year":           year,
        # Academics
        "cgpa":           cgpa,
        "backlogs":       backlogs,
        "academic_trend": academic_trend,
        # Interests
        "interests":      selected_interests,
        # Skills
        "skills": {
            "technical":     skill_technical,
            "analytical":    skill_analytical,
            "creative":      skill_creative,
            "communication": skill_communication,
            "leadership":    skill_leadership,
            "consistency":   skill_consistency,
        },
        # Activities
        "projects":        projects,
        "internships":     internships,
        "hackathons":      hackathons,
        "extracurriculars": extracurriculars,
        "certifications":  certifications,
        "effort":          effort_level,
        # Goals
        "career_goal":    career_goal,
        "timeline":       timeline,
    }

    # Run career engine
    ranked = rank_careers(profile)
    intel  = compute_intelligence_score(profile)

    st.session_state.student_profile  = profile
    st.session_state.ranked_careers   = ranked
    st.session_state.top_career_fit   = ranked[0]["fit"] if ranked else 0
    st.session_state.intelligence_score = intel

    st.success(f"✅ Profile created for **{name}**! Intelligence score: **{intel}/100**")
    st.balloons()

    col1, col2 = st.columns(2)
    with col1:
        if st.button("🎯 View Intelligence Hub →", use_container_width=True, type="primary"):
            st.switch_page("pages/1_Intelligence_Hub.py")
    with col2:
        if st.button("🗺️ View Career Mapper →", use_container_width=True):
            st.switch_page("pages/2_Career_Mapper.py")
