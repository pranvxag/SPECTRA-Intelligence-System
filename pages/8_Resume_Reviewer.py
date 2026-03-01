"""
pages/8_Resume_Reviewer.py — AI-Powered Resume & LinkedIn Profile Reviewer
Upload your resume PDF or paste your LinkedIn/profile text to get
Gemini-powered feedback targeted at your recommended career path.
"""
import streamlit as st
from components.styles import load_css
from components.sidebar import render_sidebar
from components.navbar import render_navbar
from components.cards import section_title, glow_divider

st.set_page_config(page_title="SPECTRA — Resume Reviewer", page_icon="📄", layout="wide")
load_css()
from utils.auth import require_login
require_login()
render_sidebar()
st.session_state["_current_page"] = "Resume Reviewer"
render_navbar()

st.markdown(section_title("📄", "Resume & Profile", "AI Reviewer"), unsafe_allow_html=True)
st.markdown("""
<div style="font-size:0.9rem; color:#7A90B0; margin-bottom:1.5rem; line-height:1.7;">
    Upload your resume PDF <strong style="color:#E2E8F0;">or</strong> paste your LinkedIn/profile text below.
    SPECTRA will benchmark it against the industry requirements for your recommended career and give you
    a detailed, actionable report.
</div>
""", unsafe_allow_html=True)

# ── API Key ────────────────────────────────────────────────────────────────
api_key = ""
try:
    api_key = st.secrets["GEMINI_API_KEY"]
except (KeyError, FileNotFoundError):
    pass
if not api_key:
    api_key = st.session_state.get("gemini_key", "")

if not api_key:
    st.error("🔑 Gemini API Key not found. Please visit **Ask SPECTRA** first and enter your API key there.")
    if st.button("Go to Ask SPECTRA →"):
        st.switch_page("pages/7_Ask_Spectra.py")
    st.stop()

from utils.llm_engine import init_gemini, review_resume_or_profile
init_gemini(api_key)

# ── Profile Check ──────────────────────────────────────────────────────────
profile = st.session_state.get("student_profile", {})
ranked  = st.session_state.get("ranked_careers", [])

if not profile or not profile.get("name"):
    st.info("👋 Load a student profile first to get career-targeted feedback.")
    if st.button("Go to Student Intake →", type="primary"):
        st.switch_page("pages/0_Student_Intake.py")
    st.stop()

top_career = ranked[0] if ranked else {"title": "Software Engineer", "fit": 0, "skills_needed": []}

name = profile.get("name", "Student")
target_title = top_career.get("title", "Software Engineer")
target_fit   = top_career.get("fit", 0)

# ── Target Career Banner ───────────────────────────────────────────────────
st.markdown(f"""
<div class="glass-panel" style="margin-bottom:1.5rem; display:flex; justify-content:space-between; align-items:center; flex-wrap:wrap; gap:1rem;">
    <div>
        <div style="font-family:'Syne',sans-serif; font-size:1rem; font-weight:700; color:#E2E8F0;">
            👤 {name}
        </div>
        <div style="color:#7A90B0; font-size:0.82rem;">{profile.get('branch','—')} · {profile.get('college','—')}</div>
    </div>
    <div style="text-align:right;">
        <div style="font-size:0.78rem; color:#7A90B0;">Reviewing against target career</div>
        <div style="font-size:1rem; font-weight:700; color:#00D4FF;">🎯 {target_title}</div>
        <div style="font-size:0.78rem; color:#FFB800;">Current Fit: {target_fit}%</div>
    </div>
</div>
""", unsafe_allow_html=True)

# ── Input Section ──────────────────────────────────────────────────────────
tab1, tab2 = st.tabs(["📄 Upload PDF Resume", "📋 Paste LinkedIn / Profile Text"])

resume_text = ""

with tab1:
    st.markdown("""
    <div style="font-size:0.85rem; color:#7A90B0; margin-bottom:0.8rem; line-height:1.6;">
        Upload your resume as a PDF. Text will be automatically extracted.
        For best results use a <strong>text-based PDF</strong> (not a scanned image).
    </div>
    """, unsafe_allow_html=True)

    uploaded_file = st.file_uploader(
        "Upload Resume PDF",
        type=["pdf"],
        label_visibility="collapsed",
        help="Upload a PDF resume — text will be extracted automatically",
        key="resume_pdf_upload",
    )

    if uploaded_file:
        try:
            import pdfplumber, io
            with pdfplumber.open(io.BytesIO(uploaded_file.read())) as pdf:
                pages_text = [page.extract_text() or "" for page in pdf.pages]
            resume_text = "\n\n".join(pages_text).strip()
            word_count = len(resume_text.split())
            st.markdown(f"""
            <div style="background:rgba(0,232,135,0.06); border:1px solid rgba(0,232,135,0.2);
                        border-radius:10px; padding:0.8rem 1rem; margin-top:0.5rem;">
                ✅ <strong style="color:#00E887;">{uploaded_file.name}</strong>
                &nbsp;·&nbsp; <span style="color:#7A90B0;">{len(pages_text)} page(s) · ~{word_count} words extracted</span>
            </div>
            """, unsafe_allow_html=True)
            if word_count < 50:
                st.warning("⚠️ Very little text was extracted. This may be a scanned PDF. Try pasting the text manually in Tab 2.")
        except Exception as e:
            st.error(f"Failed to read PDF: {e}")
            resume_text = ""

with tab2:
    st.markdown("""
    <div style="font-size:0.85rem; color:#7A90B0; margin-bottom:0.8rem; line-height:1.6;">
        <strong>LinkedIn:</strong> Go to your profile → click "More" → "Save to PDF" → open the PDF → copy all text and paste here.<br>
        Or simply copy your <strong>About section + Experience + Education + Skills</strong> and paste below.
    </div>
    """, unsafe_allow_html=True)

    pasted_text = st.text_area(
        "Paste your LinkedIn/profile text here",
        placeholder="Paste your resume text, LinkedIn About + Experience sections, or any profile content here...",
        height=280,
        label_visibility="collapsed",
        key="resume_paste_area",
    )

    if pasted_text.strip():
        resume_text = pasted_text.strip()
        word_count = len(resume_text.split())
        st.markdown(f"""
        <div style="font-size:0.78rem; color:#7A90B0; margin-top:0.3rem;">
            ✅ {word_count} words ready for review.
        </div>
        """, unsafe_allow_html=True)

st.markdown(glow_divider(), unsafe_allow_html=True)

# ── Analyse Button ─────────────────────────────────────────────────────────
col_btn, col_clear = st.columns([3, 1])
with col_btn:
    run_review = st.button(
        f"🔍 Analyse My Resume for {target_title}",
        type="primary",
        use_container_width=True,
        disabled=(not resume_text),
    )
with col_clear:
    if st.button("🗑️ Clear Results", use_container_width=True):
        st.session_state.pop("review_result", None)
        st.rerun()

if not resume_text:
    st.markdown("""
    <div style="text-align:center; color:#4A5A7A; font-size:0.85rem; padding:2rem 0;">
        ⬆️ Upload a PDF or paste your text above to get started.
    </div>
    """, unsafe_allow_html=True)

# ── Run Review ─────────────────────────────────────────────────────────────
if run_review and resume_text:
    with st.spinner(f"🤖 Gemini is reviewing your resume for {target_title} suitability..."):
        result = review_resume_or_profile(resume_text, profile, top_career)
    st.session_state["review_result"] = result

# ── Display Results ────────────────────────────────────────────────────────
result = st.session_state.get("review_result")

if result:
    score = result.get("score", 0)
    summary = result.get("summary", "")

    # Score & summary
    st.markdown("---")

    # Score gauge row
    score_color = "#00E887" if score >= 70 else "#FFB800" if score >= 45 else "#FF4A6E"
    score_label = "Strong" if score >= 70 else "Moderate" if score >= 45 else "Needs Work"

    sc1, sc2 = st.columns([1, 3])
    with sc1:
        st.markdown(f"""
        <div style="text-align:center; background:rgba(0,0,0,0.3); border:2px solid {score_color};
                    border-radius:16px; padding:1.5rem 1rem;">
            <div style="font-size:3rem; font-weight:800; color:{score_color}; font-family:'Syne',sans-serif; line-height:1;">
                {score}
            </div>
            <div style="font-size:0.75rem; color:#7A90B0; margin-top:0.3rem;">out of 100</div>
            <div style="font-size:0.8rem; font-weight:700; color:{score_color}; margin-top:0.5rem;">
                {score_label}
            </div>
        </div>
        """, unsafe_allow_html=True)
    with sc2:
        st.markdown(f"""
        <div class="glass-panel" style="height:100%; display:flex; align-items:center;">
            <div>
                <div style="font-size:0.72rem; color:#4A5A7A; text-transform:uppercase; letter-spacing:1.5px; margin-bottom:0.5rem;">
                    🤖 AI Assessment Summary
                </div>
                <div style="font-size:0.95rem; color:#E2E8F0; line-height:1.7;">
                    {summary}
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # Detailed sections
    r1, r2 = st.columns(2)

    def _bullet_html(items: list, color: str, icon: str) -> str:
        if not items:
            return f'<div style="color:#4A5A7A; font-size:0.82rem; padding:0.3rem 0;">No items found.</div>'
        rows = "".join(
            f'<div style="display:flex; gap:0.5rem; margin-bottom:0.6rem;">'
            f'<span style="color:{color}; flex-shrink:0;">{icon}</span>'
            f'<span style="color:#CBD5E0; font-size:0.85rem; line-height:1.5;">{item}</span>'
            f'</div>'
            for item in items
        )
        return rows

    def _panel(title: str, icon: str, color: str, items: list, icon_each: str) -> str:
        return f"""
        <div class="glass-panel" style="margin-bottom:1rem;">
            <div style="font-family:'Syne',sans-serif; font-weight:700; font-size:0.9rem;
                        color:{color}; margin-bottom:0.9rem;">{icon} {title}</div>
            {_bullet_html(items, color, icon_each)}
        </div>
        """

    with r1:
        st.markdown(_panel("Strengths Found", "💪", "#00E887", result.get("strengths", []), "✓"), unsafe_allow_html=True)
        st.markdown(_panel("Critical Gaps", "🔻", "#FF4A6E", result.get("gaps", []), "✗"), unsafe_allow_html=True)

    with r2:
        st.markdown(_panel("Actionable Suggestions", "🎯", "#00D4FF", result.get("suggestions", []), "→"), unsafe_allow_html=True)
        st.markdown(_panel(f"Missing Keywords for {target_title}", "🏷️", "#FFB800", result.get("keywords_missing", []), "•"), unsafe_allow_html=True)

    # Progress bar for score (visual)
    st.markdown(glow_divider(), unsafe_allow_html=True)
    st.markdown(f"""
    <div style="margin-bottom:0.4rem; font-size:0.78rem; color:#7A90B0;">
        Resume Score for <strong style="color:#00D4FF;">{target_title}</strong>
    </div>
    <div style="background:#111827; border-radius:50px; height:12px; overflow:hidden; width:100%;">
        <div style="width:{score}%; height:100%; border-radius:50px;
                    background:linear-gradient(90deg, {score_color}, {score_color}88);
                    transition:width 0.8s ease;"></div>
    </div>
    <div style="display:flex; justify-content:space-between; font-size:0.72rem; color:#4A5A7A; margin-top:0.3rem;">
        <span>0</span><span>50</span><span>100</span>
    </div>
    """, unsafe_allow_html=True)

    # Download plain-text report
    report_lines = [
        f"SPECTRA Resume Review Report",
        f"Student: {name}  |  Target Career: {target_title}  |  Score: {score}/100",
        "", f"SUMMARY", summary, "",
        "STRENGTHS", *[f"  • {s}" for s in result.get("strengths", [])], "",
        "GAPS", *[f"  • {g}" for g in result.get("gaps", [])], "",
        "SUGGESTIONS", *[f"  • {s}" for s in result.get("suggestions", [])], "",
        "MISSING KEYWORDS", *[f"  • {k}" for k in result.get("keywords_missing", [])],
    ]
    report_text = "\n".join(report_lines)
    st.markdown("<br>", unsafe_allow_html=True)
    st.download_button(
        "📥 Download Review Report (.txt)",
        data=report_text,
        file_name=f"spectra_resume_review_{name.replace(' ', '_')}.txt",
        mime="text/plain",
        use_container_width=False,
    )
