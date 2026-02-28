"""
pages/2_Career_Mapper.py — Career Alignment Engine
"""
import streamlit as st
import pandas as pd
from components.styles import load_css
from components.sidebar import render_sidebar
from components.navbar import render_navbar
from components.cards import section_title, skill_bar, formula_box, glow_divider, pill
from components.charts import scatter_bubble, donut_chart
from utils.career_engine import rank_careers, CAREERS

st.set_page_config(page_title="SPECTRA — Career Mapper", page_icon="🗺️", layout="wide")
load_css()
render_sidebar()
st.session_state["_current_page"] = "Career Mapper"
render_navbar()

profile = st.session_state.get("student_profile", {})
ranked  = st.session_state.get("ranked_careers", [])

st.markdown(section_title("🗺️", "Career Alignment", "Engine"), unsafe_allow_html=True)

if not profile:
    st.warning("⚠️ Complete the Student Intake form first.")
    if st.button("✏️ Go to Intake Form"):
        st.switch_page("pages/0_Student_Intake.py")
    st.stop()

# ── Formula explainer ─────────────────────────────────────────────────────
st.markdown(formula_box(
    "Career Fit Score = (Academic × 0.25) + (Interest Alignment × 0.30) + "
    "(Skill Match × 0.25) + (Effort Level × 0.20)"
), unsafe_allow_html=True)

st.markdown(glow_divider(), unsafe_allow_html=True)

# ── Side-by-side: interests & skills ──────────────────────────────────────
c1, c2 = st.columns(2)

with c1:
    st.markdown("#### 💡 Your Interest Profile")
    interest_labels = {
        "programming":    "💻 Programming",
        "mathematics":    "📐 Mathematics",
        "ai_ml":          "🤖 AI / ML",
        "research":       "🔬 Research",
        "product_design": "🎨 Product Design",
        "management":     "📋 Management",
        "core_engg":      "⚙️ Core Engineering",
        "finance":        "💰 Finance / Quant",
    }
    selected = profile.get("interests", [])
    for key, label in interest_labels.items():
        val = 100 if key in selected else 20
        color = "#00D4FF" if key in selected else "#2A3A58"
        active_pill = f' <span class="pill pill-cyan">Selected</span>' if key in selected else ""
        st.markdown(f"""
        <div class="skill-row">
            <div class="skill-label">
                <span>{label}{active_pill}</span>
                <span style="color:{color};">{'■' * (5 if key in selected else 1)}{'□' * (5 if key not in selected else 0)}</span>
            </div>
            <div class="skill-bar-bg">
                <div class="skill-bar-fill" style="width:{val}%; background:{color};"></div>
            </div>
        </div>
        """, unsafe_allow_html=True)

with c2:
    st.markdown("#### 🔧 Your Skill Matrix")
    skills = profile.get("skills", {})
    for key, val in skills.items():
        st.markdown(skill_bar(key.title(), val), unsafe_allow_html=True)

st.markdown(glow_divider(), unsafe_allow_html=True)

# ── Ranked career cards ────────────────────────────────────────────────────
st.markdown("#### 🚀 Personalised Career Pathways")

for career in ranked:
    fit = career["fit"]
    badge_color = "green" if fit >= 80 else ("amber" if fit >= 60 else "rose")
    badge_text  = "Strong Fit" if fit >= 80 else ("Moderate Fit" if fit >= 60 else "Low Fit")

    with st.expander(f"{career['title']} — {fit}% Match", expanded=(fit >= 80)):
        ec1, ec2, ec3, ec4 = st.columns(4)
        with ec1: st.metric("Career Fit",     f"{fit}%")
        with ec2: st.metric("Salary Range",   career["salary"])
        with ec3: st.metric("Market Demand",  career["demand"])
        with ec4: st.metric("Fit Category",   badge_text)

        st.markdown(f"""
        <div style="margin-top:0.8rem;">
            <div style="color:#7A90B0; font-size:0.85rem; margin-bottom:0.3rem;">
                <strong style="color:#E2E8F0;">Skills to Develop:</strong>
                {", ".join(career['skills_needed'])}
            </div>
            <div style="color:#7A90B0; font-size:0.85rem;">
                <strong style="color:#E2E8F0;">Suggested Path:</strong>
                {career['path']}
            </div>
        </div>
        <div class="skill-row" style="margin-top:1rem;">
            <div class="skill-label"><span>Fit Score</span><span style="color:#FFB800;">{fit}%</span></div>
            <div class="skill-bar-bg">
                <div class="career-bar-fill" style="width:{fit}%;"></div>
            </div>
        </div>
        """, unsafe_allow_html=True)

        if st.button(f"📋 Create Learning Plan", key=f"plan_{career['id']}"):
            st.info(f"📌 **{career['title']} Learning Plan:**\n\n{career['path']}\n\n"
                    f"**Key skills:** {', '.join(career['skills_needed'])}")

st.markdown(glow_divider(), unsafe_allow_html=True)

# ── Bubble chart: all careers ──────────────────────────────────────────────
st.markdown("#### 📊 Career Landscape Overview")

bubble_df = pd.DataFrame([{
    "Career":   c["title"],
    "Fit Score": c["fit"],
    "Demand Score": {"Very High": 95, "High": 75, "Moderate": 55, "Low": 35}.get(c["demand"], 60),
    "Size":     c["fit"] * 1.2,
} for c in ranked])

st.plotly_chart(
    scatter_bubble(bubble_df, "Demand Score", "Fit Score", "Size", "Career",
                   "Career Fit vs Market Demand", height=400),
    use_container_width=True
)

# ── Fit distribution donut ─────────────────────────────────────────────────
d1, d2 = st.columns([1, 2])
with d1:
    labels = [c["title"].split("/")[0].strip() for c in ranked]
    values = [c["fit"] for c in ranked]
    st.plotly_chart(donut_chart(labels, values, "Fit Distribution"), use_container_width=True)

with d2:
    st.markdown("""
    <div class="glass-panel">
        <div style="font-family:'Syne',sans-serif; font-size:1rem; font-weight:700;
                    color:#E2E8F0; margin-bottom:1rem;">
            📖 How to Read Your Score
        </div>
        <div class="swot-item"><div class="swot-dot" style="background:#00E887;"></div>
            <span><strong style="color:#00E887;">80–100%</strong> — Strong Fit: Pursue actively. Your profile aligns well.</span></div>
        <div class="swot-item"><div class="swot-dot" style="background:#FFB800;"></div>
            <span><strong style="color:#FFB800;">60–79%</strong> — Moderate Fit: Achievable with targeted skill development.</span></div>
        <div class="swot-item"><div class="swot-dot" style="background:#FF4D6A;"></div>
            <span><strong style="color:#FF4D6A;">Below 60%</strong> — Low Fit: Possible but requires significant repositioning.</span></div>
        <div style="color:#4A5A7A; font-size:0.8rem; margin-top:1rem;">
            Scores are computed using: Academic (25%) + Interest (30%) + Skill (25%) + Effort (20%)
        </div>
    </div>
    """, unsafe_allow_html=True)