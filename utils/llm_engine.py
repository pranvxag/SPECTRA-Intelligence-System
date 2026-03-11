"""
utils/llm_engine.py — Interface for Gemini and Groq APIs
"""
import streamlit as st
import google.generativeai as genai
from groq import Groq
import json
import re

# ── Clients ─────────────────────────────────────────────────────────────

def init_gemini(api_key: str):
    """Initialize the Gemini client."""
    genai.configure(api_key=api_key)

def _get_groq_client():
    """Get Groq client from secrets or session state."""
    api_key = st.secrets.get("GROQ_API_KEY") or st.session_state.get("groq_key")
    if api_key:
        try:
            return Groq(api_key=api_key)
        except Exception:
            return None
    return None

# ── AI Coach ───────────────────────────────────────────────────────────

def get_coach_response(user_message: str, chat_history: list, profile: dict, intelligence_score: float, top_career: str) -> str:
    """Generate a response using Groq (LLaMA-3) or Gemini."""
    
    system_instruction = f"""
    You are SPECTRA, an elite AI career coach for a university student.
    Your goal is to guide the student towards their top career fit, answer their questions, and provide actionable advice.
    You must be encouraging, professional, structured, and use emoji where appropriate.
    
    Student Context:
    - Name: {profile.get("name", "Student")}
    - College: {profile.get("college", "Unknown")}
    - Branch: {profile.get("branch", "Unknown")}
    - CGPA: {profile.get("cgpa", "Unknown")}
    - Intelligence Score: {intelligence_score}
    - Top Recommended Career: {top_career}
    - Skills & Comfort Levels: {profile.get("skills", {})}
    - Interests: {', '.join(profile.get("interests", []))}
    - Career Goal: {profile.get("career_goal", "Unknown")}
    
    Keep your answers concise, empathetic, and highly personalized to the student's data.
    """

    # Try Groq first
    client = _get_groq_client()
    if client:
        try:
            messages = [{"role": "system", "content": system_instruction}]
            for msg in chat_history:
                # Groq uses standard "user"/"assistant" roles
                messages.append({"role": msg["role"], "content": msg["content"]})
            messages.append({"role": "user", "content": user_message})

            completion = client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=messages,
                temperature=0.7,
                max_tokens=1024,
            )
            return completion.choices[0].message.content
        except Exception as e:
            st.warning(f"Groq API Error: {e}. Falling back to Gemini...")

    # Fallback to Gemini
    try:
        # Use gemini-1.5-flash as default fallback
        model = genai.GenerativeModel('models/gemini-1.5-flash', system_instruction=system_instruction)
        gemini_history = []
        for msg in chat_history:
            role = "model" if msg["role"] == "assistant" else "user"
            gemini_history.append({"role": role, "parts": [msg["content"]]})
        
        chat = model.start_chat(history=gemini_history)
        response = chat.send_message(user_message)
        return response.text
    except Exception as e:
        return f"⚠️ SPECTRA Coach is currently unavailable. Error: {str(e)}"

# ── Dynamic SWOT ───────────────────────────────────────────────────────

def generate_dynamic_swot(profile: dict, top_career: dict) -> dict:
    """Generate a personalized SWOT using Groq or Gemini."""
    skills_str = ", ".join([f"{k}: {v}/100" for k, v in profile.get("skills", {}).items()])
    prompt = f"""
Analyze the following student profile for the career: "{top_career.get('title', 'Software Engineer')}".
Profile: Branch {profile.get('branch')}, CGPA {profile.get('cgpa')}, Skills: {skills_str}.

Respond ONLY with a valid JSON object:
{{
  "strengths": ["point 1", "point 2", "point 3", "point 4"],
  "weaknesses": ["point 1", "point 2", "point 3", "point 4"],
  "opportunities": ["point 1", "point 2", "point 3", "point 4"],
  "threats": ["point 1", "point 2", "point 3", "point 4"]
}}
"""

    # Try Groq
    client = _get_groq_client()
    if client:
        try:
            chat_completion = client.chat.completions.create(
                messages=[{"role": "user", "content": prompt}],
                model="llama-3.3-70b-versatile",
                response_format={"type": "json_object"},
            )
            return json.loads(chat_completion.choices[0].message.content)
        except Exception:
            pass

    # Fallback to Gemini
    try:
        model = genai.GenerativeModel('models/gemini-1.5-flash')
        response = model.generate_content(prompt)
        text = response.text.strip()
        text = re.sub(r"```(?:json)?", "", text).strip().rstrip("```").strip()
        return json.loads(text)
    except Exception:
        return {
            "strengths": ["Profile loaded — SWOT generation failed."],
            "weaknesses": [],
            "opportunities": [],
            "threats": [],
        }

# ── Dynamic Roadmap ──────────────────────────────────────────────────────

def generate_dynamic_roadmap(profile: dict, top_career: dict) -> dict:
    """Generate a personalized 3-phase roadmap using Groq or Gemini."""
    skills_str = ", ".join([f"{k}: {v}/100" for k, v in profile.get("skills", {}).items()])
    prompt = f"""
Create a personalized 3-phase action roadmap for career: "{top_career.get('title', 'Software Engineer')}".
Student: {profile.get('branch')}, CGPA {profile.get('cgpa')}, Skills: {skills_str}.

Generate 4 tasks per phase. Respond ONLY with JSON:
{{
  "immediate": ["task 1", "task 2", "task 3", "task 4"],
  "short": ["task 1", "task 2", "task 3", "task 4"],
  "long": ["task 1", "task 2", "task 3", "task 4"]
}}
"""
    # Try Groq
    client = _get_groq_client()
    if client:
        try:
            chat_completion = client.chat.completions.create(
                messages=[{"role": "user", "content": prompt}],
                model="llama-3.3-70b-versatile",
                response_format={"type": "json_object"},
            )
            return json.loads(chat_completion.choices[0].message.content)
        except Exception:
            pass

    # Fallback to Gemini
    try:
        model = genai.GenerativeModel('models/gemini-1.5-flash')
        response = model.generate_content(prompt)
        text = response.text.strip()
        text = re.sub(r"```(?:json)?", "", text).strip().rstrip("```").strip()
        return json.loads(text)
    except Exception:
        return {"immediate": ["Roadmap generation failed."], "short": [], "long": []}

# ── Resume Review ───────────────────────────────────────────────────────

def review_resume_or_profile(text: str, profile: dict, top_career: dict) -> dict:
    """Review a resume against top_career requirements using Groq or Gemini."""
    career_title = top_career.get("title", "Software Engineer")
    prompt = f"""
Review this resume for the role: {career_title}.
Content: {text[:4000]}

Respond ONLY with JSON:
{{
  "score": <0-100>,
  "summary": "<text>",
  "strengths": ["<text>"],
  "gaps": ["<text>"],
  "suggestions": ["<text>"],
  "keywords_missing": ["<text>"]
}}
"""
    # Try Groq
    client = _get_groq_client()
    if client:
        try:
            chat_completion = client.chat.completions.create(
                messages=[{"role": "user", "content": prompt}],
                model="llama-3.3-70b-versatile",
                response_format={"type": "json_object"},
            )
            return json.loads(chat_completion.choices[0].message.content)
        except Exception:
            pass

    # Fallback to Gemini
    try:
        model = genai.GenerativeModel('models/gemini-1.5-flash')
        response = model.generate_content(prompt)
        text_resp = response.text.strip()
        text_resp = re.sub(r"```(?:json)?", "", text_resp).strip().rstrip("```").strip()
        return json.loads(text_resp)
    except Exception:
        return {
            "score": 0,
            "summary": "Review generation failed.",
            "strengths": [],
            "gaps": [],
            "suggestions": [],
            "keywords_missing": [],
        }
