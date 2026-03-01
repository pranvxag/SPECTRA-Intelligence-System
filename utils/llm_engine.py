"""
utils/llm_engine.py — Interface for Google Gemini API
"""
import google.generativeai as genai

def init_gemini(api_key: str):
    """Initialize the Gemini client with the given API key."""
    genai.configure(api_key=api_key)

def get_coach_response(user_message: str, chat_history: list, profile: dict, intelligence_score: float, top_career: str) -> str:
    """
    Generate a response from the LLM based on user message and context.
    chat_history: list of dicts [{"role": "user"/"assistant", "content": "..."}]
    profile: student profile dictionary
    """
    
    # Construct the System Prompt
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
    If the student wants gaps analyzed, look at their listed skills vs the standard skills for their top career.
    """
    
    # Initialize the model using gemini-2.5-flash (fast, free tier available)
    model = genai.GenerativeModel('models/gemini-2.5-flash',
                                  system_instruction=system_instruction)
    
    # Convert Streamlit chat history to Gemini format.
    gemini_history = []
    for msg in chat_history:
        # Streamlit uses "assistant", Gemini uses "model"
        role = "model" if msg["role"] == "assistant" else "user"
        content = msg["content"]
        gemini_history.append({"role": role, "parts": [content]})
    
    chat = model.start_chat(history=gemini_history)
    
    try:
        response = chat.send_message(user_message)
        return response.text
    except Exception as e:
        return f"⚠️ SPECTRA Coach is currently unavailable. Error: {str(e)}"
