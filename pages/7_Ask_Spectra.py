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
    SPECTRA uses Google's Gemini 1.5 Flash (Free Tier) to answer your questions, analyze your profile, and give you actionable career advice.
</div>
""", unsafe_allow_html=True)

# ── API Key Setup ──────────────────────────────────────────────────────────
api_key = ""
try:
    api_key = st.secrets["GEMINI_API_KEY"]
except (KeyError, FileNotFoundError):
    pass

if not api_key:
    if "gemini_key" in st.session_state:
        api_key = st.session_state["gemini_key"]

if not api_key:
    st.markdown("""
    <div style="background:rgba(255,184,0,0.07); border:1px solid rgba(255,184,0,0.2);
                border-radius:10px; padding:1.2rem; margin-bottom:1rem;">
        <h4 style="color:#FFB800; margin-top:0;">🔑 Gemini API Key Required</h4>
        <div style="font-size:0.9rem; color:#E2E8F0; line-height:1.6;">
            To use the AI Coach, you need a free Google Gemini API Key.<br>
            <strong>Good news: It's 100% Free for educational and personal use!</strong><br><br>
            1. Go to <a href="https://aistudio.google.com/app/apikey" target="_blank" style="color:#00D4FF;">Google AI Studio</a> and sign in with your Google account.<br>
            2. Click <strong>Create API Key</strong>.<br>
            3. Paste it below (it will only be stored securely in your temporary browser session).
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    user_key = st.text_input("Enter your Gemini API Key:", type="password")
    if user_key:
        st.session_state["gemini_key"] = user_key
        st.rerun()
    st.stop()
else:
    try:
        init_gemini(api_key)
    except Exception as e:
        st.error(f"Failed to initialize Gemini: {e}")
        st.stop()

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

# Initialize chat history
if "spectra_messages" not in st.session_state:
    st.session_state.spectra_messages = [
        {"role": "assistant", "content": f"Hi {profile.get('name', 'there')}! I'm SPECTRA, your AI career coach. Based on your profile, your top career match is **{top_career}**. How can I help you achieve your goals today?"}
    ]

# Display chat messages from history on app rerun
for message in st.session_state.spectra_messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# React to user input
if prompt := st.chat_input("Ask SPECTRA about your career, resume, or skills..."):
    # Display user message in chat message container
    st.chat_message("user").markdown(prompt)
    
    # Get response from Gemini
    with st.spinner("SPECTRA is thinking..."):
        # We pass history EXCLUDING the new prompt
        response_text = get_coach_response(prompt, st.session_state.spectra_messages, profile, intel_score, top_career)
        
    # Add user message to state
    st.session_state.spectra_messages.append({"role": "user", "content": prompt})

    # Display assistant response in chat message container
    with st.chat_message("assistant"):
        st.markdown(response_text)
    
    # Add assistant response to chat history
    st.session_state.spectra_messages.append({"role": "assistant", "content": response_text})
