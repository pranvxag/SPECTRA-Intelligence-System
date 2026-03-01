"""
pages/7_Ask_Spectra.py — LLM-Powered Chatbot Coach
"""
import streamlit as st
from components.styles import load_css
from components.sidebar import render_sidebar
from components.navbar import render_navbar
from components.cards import section_title, glow_divider
from utils.llm_engine import init_gemini, get_coach_response

st.set_page_config(page_title="SPECTRA — Ask Coach", page_icon="🤖", layout="wide")
load_css()
from utils.auth import require_login
require_login()
render_sidebar()
st.session_state["_current_page"] = "Ask SPECTRA"
render_navbar()

st.markdown(section_title("🤖", "Ask SPECTRA", "Your Personal AI Career Coach"), unsafe_allow_html=True)
st.markdown("""
<div style="font-size:0.9rem; color:#7A90B0; margin-bottom: 1.5rem;">
    SPECTRA uses Groq (LLaMA-3) or Google's Gemini to answer your questions, analyze your profile, and give you actionable career advice.
</div>
""", unsafe_allow_html=True)

# ── API Key Setup ──────────────────────────────────────────────────────────
# Check secrets first
gemini_key = st.secrets.get("GEMINI_API_KEY") or st.session_state.get("gemini_key")
groq_key = st.secrets.get("GROQ_API_KEY") or st.session_state.get("groq_key")

if not gemini_key and not groq_key:
    st.markdown("""
    <div style="background:rgba(0,212,255,0.07); border:1px solid rgba(0,212,255,0.2);
                border-radius:10px; padding:1.2rem; margin-bottom:1rem;">
        <h4 style="color:#00D4FF; margin-top:0;">🔑 AI Engine Key Required</h4>
        <div style="font-size:0.9rem; color:#E2E8F0; line-height:1.6;">
            To use the AI Coach, you need an API Key from either <b>Groq</b> or <b>Google Gemini</b>.<br><br>
            <b>Option A: Groq (Recommended - Fast)</b><br>
            1. Go to <a href="https://console.groq.com/keys" target="_blank" style="color:#00D4FF;">Groq Console</a>.<br>
            2. Create a key and paste it below.<br><br>
            <b>Option B: Google Gemini (Free)</b><br>
            1. Go to <a href="https://aistudio.google.com/app/apikey" target="_blank" style="color:#00D4FF;">Google AI Studio</a>.<br>
            2. Create a key and paste it below.
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    with col1:
        u_groq = st.text_input("Enter Groq API Key:", type="password", placeholder="gsk_...")
        if u_groq:
            st.session_state["groq_key"] = u_groq
            st.rerun()
    with col2:
        u_gem = st.text_input("Enter Gemini API Key:", type="password", placeholder="AIza...")
        if u_gem:
            st.session_state["gemini_key"] = u_gem
            st.rerun()
    st.stop()
else:
    # Initialize if Gemini is the only thing we have
    if gemini_key and not groq_key:
        try:
            init_gemini(gemini_key)
        except Exception as e:
            st.error(f"Failed to initialize Gemini: {e}")

# ── Profile Check ──────────────────────────────────────────────────────────
profile = st.session_state.get("student_profile", {})
if not profile or not profile.get("name"):
    st.info("👋 Hi! To get personalized career coaching, please create or load your profile first in the Student Intake form.")
    if st.button("Go to Student Intake", type="primary"):
        st.switch_page("pages/0_Student_Intake.py")
    st.stop()

intel_score = st.session_state.get("intelligence_score", 0)
ranked_careers = st.session_state.get("ranked_careers", [{"title": "Unknown"}])
top_career = ranked_careers[0]["title"] if ranked_careers else "Unknown"

# ── Chat Interface ─────────────────────────────────────────────────────────

if "spectra_messages" not in st.session_state:
    st.session_state.spectra_messages = [
        {"role": "assistant", "content": f"Hi {profile.get('name', 'there')}! I'm SPECTRA, your AI career coach powered by **{'Groq' if groq_key else 'Gemini'}**. How can I help you today?"}
    ]

for message in st.session_state.spectra_messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

if prompt := st.chat_input("Ask SPECTRA about your career, resume, or skills..."):
    st.chat_message("user").markdown(prompt)
    
    with st.spinner("SPECTRA is thinking..."):
        response_text = get_coach_response(prompt, st.session_state.spectra_messages, profile, intel_score, top_career)
        
    st.session_state.spectra_messages.append({"role": "user", "content": prompt})
    with st.chat_message("assistant"):
        st.markdown(response_text)
    st.session_state.spectra_messages.append({"role": "assistant", "content": response_text})
