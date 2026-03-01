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


def generate_dynamic_swot(profile: dict, top_career: dict) -> dict:
    """
    Use Gemini to generate a personalized SWOT analysis for a student.
    Returns a dict with keys: strengths, weaknesses, opportunities, threats.
    Falls back to empty lists on failure.
    """
    import json, re

    skills_str = ", ".join([f"{k}: {v}/100" for k, v in profile.get("skills", {}).items()])
    interests_str = ", ".join(profile.get("interests", []))

    prompt = f"""
You are an expert academic and career advisor. Analyze the following student profile and generate a highly personalized, insightful SWOT analysis targeting the career: "{top_career.get('title', 'Software Engineer')}".

Student Profile:
- Name: {profile.get('name', 'Student')}
- Branch: {profile.get('branch', 'Engineering')}
- CGPA: {profile.get('cgpa', 7.0)}/10
- Semester: {profile.get('semester', 4)}
- Skills (score/100): {skills_str}
- Interests: {interests_str}
- Career Goal: {profile.get('career_goal', 'Not specified')}
- Projects Completed: {profile.get('projects', 0)}
- Internships: {profile.get('internships', 0)}
- Hackathons: {profile.get('hackathons', 0)}
- Certifications: {profile.get('certifications', 0)}
- Effort Level: {profile.get('effort', 3)}/5
- Career Fit Score for "{top_career.get('title', '')}": {top_career.get('fit', 0)}%

Generate exactly 4-5 points each for Strengths, Weaknesses, Opportunities, and Threats. Each point should be:
- Specific to THIS student's data (reference actual CGPA, skill scores, projects)
- Written as a natural, actionable sentence (not just a word)
- Highly relevant to the target career

Respond ONLY with a valid JSON object in this exact format (no markdown, no backticks):
{{
  "strengths": ["point 1", "point 2", "point 3", "point 4"],
  "weaknesses": ["point 1", "point 2", "point 3", "point 4"],
  "opportunities": ["point 1", "point 2", "point 3", "point 4"],
  "threats": ["point 1", "point 2", "point 3", "point 4"]
}}
"""
    try:
        model = genai.GenerativeModel('models/gemini-2.5-flash')
        response = model.generate_content(prompt)
        text = response.text.strip()
        # Strip markdown code fences if present
        text = re.sub(r"```(?:json)?", "", text).strip().rstrip("```").strip()
        return json.loads(text)
    except Exception as e:
        # Graceful fallback
        return {
            "strengths": [f"Profile loaded — Gemini SWOT unavailable: {str(e)[:80]}"],
            "weaknesses": ["Could not generate weaknesses at this time."],
            "opportunities": ["Could not generate opportunities at this time."],
            "threats": ["Could not generate threats at this time."],
        }


def generate_dynamic_roadmap(profile: dict, top_career: dict) -> dict:
    """
    Use Gemini to generate a personalized 3-phase action roadmap for a student.
    Returns a dict with keys: immediate (0-3mo), short (3-6mo), long (6-12mo).
    Falls back to empty lists on failure.
    """
    import json, re

    skills_str = ", ".join([f"{k}: {v}/100" for k, v in profile.get("skills", {}).items()])

    prompt = f"""
You are an expert career coach. Create a personalized 3-phase action roadmap for this student targeting a career as "{top_career.get('title', 'Software Engineer')}".

Student Profile:
- Branch: {profile.get('branch', 'Engineering')}
- CGPA: {profile.get('cgpa', 7.0)}/10
- Skills (score/100): {skills_str}
- Projects: {profile.get('projects', 0)}, Internships: {profile.get('internships', 0)}
- Hackathons: {profile.get('hackathons', 0)}, Certifications: {profile.get('certifications', 0)}
- Career Fit for "{top_career.get('title', '')}": {top_career.get('fit', 0)}%

Generate exactly 4 specific, actionable tasks per phase. Be concrete — reference exact skills to learn, tools to use, or platforms to use.

Respond ONLY with a valid JSON object in this exact format (no markdown, no backticks):
{{
  "immediate": ["task 1", "task 2", "task 3", "task 4"],
  "short": ["task 1", "task 2", "task 3", "task 4"],
  "long": ["task 1", "task 2", "task 3", "task 4"]
}}
"""
    try:
        model = genai.GenerativeModel('models/gemini-2.5-flash')
        response = model.generate_content(prompt)
        text = response.text.strip()
        text = re.sub(r"```(?:json)?", "", text).strip().rstrip("```").strip()
        return json.loads(text)
    except Exception as e:
        return {
            "immediate": [f"Roadmap generation unavailable: {str(e)[:80]}"],
            "short": ["Please check your API key and try again."],
            "long": ["Navigate to Ask SPECTRA for personalized advice."],
        }


def review_resume_or_profile(text: str, profile: dict, top_career: dict) -> dict:
    """
    Use Gemini to review a resume or LinkedIn/profile text against the student's
    top_career requirements.

    Returns a dict:
        {
          "score": int (0-100),
          "summary": str,
          "strengths": [str, ...],
          "gaps": [str, ...],
          "suggestions": [str, ...],
          "keywords_missing": [str, ...]
        }
    """
    import json, re

    skills_needed = top_career.get("skills_needed", [])
    career_title  = top_career.get("title", "Software Engineer")
    career_path   = top_career.get("path", "")

    prompt = f"""
You are a world-class technical recruiter and career coach who specializes in evaluating resumes and LinkedIn profiles for engineering students.

TARGET CAREER: {career_title}
Required skills for this role: {', '.join(skills_needed) if skills_needed else 'General technical skills'}
Suggested career path: {career_path}

STUDENT PROFILE CONTEXT:
- Branch: {profile.get('branch', 'Engineering')}
- CGPA: {profile.get('cgpa', 0)}/10
- Semester: {profile.get('semester', '')}
- Known skills: {', '.join(str(k) for k in profile.get('skills', {}).keys())}
- Interests: {', '.join(profile.get('interests', []))}

RESUME / PROFILE TEXT TO REVIEW:
\"\"\"
{text[:4000]}
\"\"\"

Perform a comprehensive review. Be specific and reference actual content from the text above.

Respond ONLY with a valid JSON object in this exact format (no markdown, no backticks):
{{
  "score": <integer 0-100 representing overall resume quality for the target career>,
  "summary": "<2-3 sentence overall assessment>",
  "strengths": ["<specific strength found in the text>", "<strength 2>", "<strength 3>"],
  "gaps": ["<critical gap or missing element>", "<gap 2>", "<gap 3>"],
  "suggestions": ["<concrete, actionable suggestion>", "<suggestion 2>", "<suggestion 3>", "<suggestion 4>"],
  "keywords_missing": ["<important keyword/skill missing for {career_title}>", "<keyword 2>", "<keyword 3>", "<keyword 4>"]
}}
"""
    try:
        model = genai.GenerativeModel('models/gemini-2.5-flash')
        response = model.generate_content(prompt)
        text_resp = response.text.strip()
        text_resp = re.sub(r"```(?:json)?", "", text_resp).strip().rstrip("```").strip()
        return json.loads(text_resp)
    except Exception as e:
        return {
            "score": 0,
            "summary": f"Review unavailable: {str(e)[:120]}",
            "strengths": [],
            "gaps": [],
            "suggestions": ["Please check your Gemini API key and retry."],
            "keywords_missing": [],
        }

