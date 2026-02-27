"""
🎓 SPECTRA - Student Intelligence & Career Guidance System
IIT Techkriti 2026 Innovation Challenge
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import joblib
import os
import time
from datetime import datetime
import warnings
warnings.filterwarnings('ignore')

# Page configuration
st.set_page_config(
    page_title="SPECTRA - Student Intelligence System",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for futuristic design
st.markdown("""
<style>
    /* Import futuristic font */
    @import url('https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@300;400;500;600;700&display=swap');
    
    * {
        font-family: 'Space Grotesk', sans-serif;
    }
    
    /* Gradient background */
    .stApp {
        background: linear-gradient(135deg, #0A0F1E 0%, #1A1F2E 100%);
    }
    
    /* Glassmorphism containers */
    .glass-panel {
        background: rgba(255, 255, 255, 0.05);
        backdrop-filter: blur(10px);
        border-radius: 30px;
        padding: 2rem;
        border: 1px solid rgba(255, 255, 255, 0.1);
        box-shadow: 0 20px 40px rgba(0, 0, 0, 0.4);
    }
    
    /* Professional Header */
    .hero-header {
        text-align: center;
        padding: 3rem 2rem;
        margin-bottom: 2rem;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        border-radius: 40px;
        color: white;
        box-shadow: 0 30px 60px rgba(102, 126, 234, 0.3);
    }
    
    .hero-title {
        font-size: 4rem;
        font-weight: 800;
        margin: 0;
        letter-spacing: -1px;
        text-shadow: 0 4px 20px rgba(0,0,0,0.3);
    }
    
    .hero-subtitle {
        font-size: 1.5rem;
        opacity: 0.95;
        margin-top: 1rem;
        font-weight: 300;
    }
    
    .hero-badge {
        background: rgba(255,255,255,0.2);
        padding: 0.5rem 2rem;
        border-radius: 50px;
        display: inline-block;
        margin-top: 1rem;
        font-weight: 500;
        border: 1px solid rgba(255,255,255,0.3);
    }
    
    /* Navigation - Game Jam Style */
    .nav-container {
        background: rgba(20, 25, 40, 0.95);
        backdrop-filter: blur(20px);
        border-radius: 60px;
        padding: 0.8rem 1.5rem;
        margin: 1rem auto 3rem auto;
        max-width: 1300px;
        border: 1px solid rgba(255, 255, 255, 0.1);
        box-shadow: 0 20px 40px rgba(0, 0, 0, 0.5);
        display: flex;
        justify-content: space-between;
        align-items: center;
    }
    
    .nav-brand {
        display: flex;
        align-items: center;
        gap: 1rem;
    }
    
    .nav-logo {
        font-size: 2rem;
        background: linear-gradient(135deg, #FFD700, #FFA500);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }
    
    .nav-title {
        font-size: 1.3rem;
        font-weight: 700;
        background: linear-gradient(135deg, #fff, #FFD700);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }
    
    .nav-badge {
        background: rgba(255, 215, 0, 0.15);
        padding: 0.3rem 1rem;
        border-radius: 30px;
        font-size: 0.8rem;
        color: #FFD700;
        border: 1px solid rgba(255, 215, 0, 0.3);
    }
    
    .nav-links {
        display: flex;
        gap: 0.5rem;
        align-items: center;
        flex-wrap: wrap;
    }
    
    .nav-container .stButton > button {
        background: transparent;
        border: none;
        color: rgba(255, 255, 255, 0.7);
        font-weight: 500;
        padding: 0.6rem 1.2rem;
        border-radius: 40px;
        transition: all 0.3s;
        box-shadow: none;
        font-size: 1rem;
    }
    
    .nav-container .stButton > button:hover {
        background: rgba(255, 255, 255, 0.1);
        color: white;
        transform: translateY(-2px);
    }
    
    .nav-container .stButton > button[kind="primary"] {
        background: linear-gradient(135deg, #FF6B6B, #FF8E53);
        color: white;
        box-shadow: 0 10px 20px rgba(255, 107, 107, 0.3);
    }
    
    /* Section headers */
    .section-header {
        font-size: 2rem;
        font-weight: 700;
        background: linear-gradient(135deg, #667eea, #764ba2);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin: 2rem 0 1rem 0;
    }
    
    /* Metric cards */
    .metric-card {
        background: rgba(255, 255, 255, 0.05);
        backdrop-filter: blur(10px);
        padding: 1.5rem;
        border-radius: 25px;
        border: 1px solid rgba(255, 255, 255, 0.1);
        text-align: center;
        transition: all 0.3s;
        height: 100%;
    }
    
    .metric-card:hover {
        transform: translateY(-5px);
        border-color: #667eea;
        box-shadow: 0 20px 40px rgba(102, 126, 234, 0.2);
    }
    
    .metric-label {
        font-size: 0.9rem;
        color: #94A3B8;
        text-transform: uppercase;
        letter-spacing: 1px;
    }
    
    .metric-value {
        font-size: 2.5rem;
        font-weight: 700;
        color: white;
        margin: 0.5rem 0;
    }
    
    .metric-trend {
        font-size: 0.9rem;
        color: #10B981;
    }
    
    /* Career fit cards */
    .career-card {
        background: linear-gradient(135deg, rgba(102, 126, 234, 0.1), rgba(118, 75, 162, 0.1));
        border-radius: 20px;
        padding: 1.5rem;
        border-left: 4px solid #667eea;
        margin: 1rem 0;
    }
    
    .fit-score {
        font-size: 2rem;
        font-weight: 700;
        color: #FFD700;
    }
    
    /* SWOT sections */
    .swot-strength {
        background: rgba(16, 185, 129, 0.1);
        border-left: 4px solid #10B981;
        padding: 1rem;
        border-radius: 15px;
        margin: 0.5rem 0;
    }
    
    .swot-weakness {
        background: rgba(239, 68, 68, 0.1);
        border-left: 4px solid #EF4444;
        padding: 1rem;
        border-radius: 15px;
        margin: 0.5rem 0;
    }
    
    .swot-opportunity {
        background: rgba(245, 158, 11, 0.1);
        border-left: 4px solid #F59E0B;
        padding: 1rem;
        border-radius: 15px;
        margin: 0.5rem 0;
    }
    
    .swot-threat {
        background: rgba(139, 92, 246, 0.1);
        border-left: 4px solid #8B5CF6;
        padding: 1rem;
        border-radius: 15px;
        margin: 0.5rem 0;
    }
    
    /* Animations */
    @keyframes float {
        0% { transform: translateY(0px); }
        50% { transform: translateY(-10px); }
        100% { transform: translateY(0px); }
    }
    
    .float-animation {
        animation: float 6s ease-in-out infinite;
    }
    
    /* Progress bars */
    .progress-container {
        background: rgba(255,255,255,0.1);
        border-radius: 10px;
        height: 10px;
        overflow: hidden;
    }
    
    .progress-fill {
        background: linear-gradient(90deg, #667eea, #764ba2);
        height: 100%;
        border-radius: 10px;
        transition: width 1s ease;
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state
def init_session_state():
    if 'authenticated' not in st.session_state:
        st.session_state.authenticated = True
    if 'predictions' not in st.session_state:
        st.session_state.predictions = []
    if 'current_page' not in st.session_state:
        st.session_state.current_page = 'Intelligence Hub'
    if 'student_profile' not in st.session_state:
        st.session_state.student_profile = {}
    if 'career_matches' not in st.session_state:
        st.session_state.career_matches = []

init_session_state()

# Hero Header
st.markdown("""
<div class="hero-header">
    <h1 class="hero-title">🎓 SPECTRA</h1>
    <p class="hero-subtitle">Student Intelligence & Career Guidance System</p>
    <div class="hero-badge">IIT Techkriti 2026 Innovation Challenge</div>
</div>
""", unsafe_allow_html=True)

# Navigation Bar
st.markdown("""
<div class="nav-container">
    <div class="nav-brand">
        <span class="nav-logo">⚡</span>
        <span class="nav-title">SPECTRA</span>
        <span class="nav-badge">AI-POWERED</span>
    </div>
    <div class="nav-links">
""", unsafe_allow_html=True)

# Navigation items - Reflecting the new vision
nav_items = [
    {"name": "Intelligence Hub", "page": "Intelligence Hub", "icon": "🎯", "desc": "Student Overview"},
    {"name": "Career Mapper", "page": "Career Mapper", "icon": "🗺️", "desc": "Career Alignment"},
    {"name": "SWOT Analysis", "page": "SWOT Analysis", "icon": "📊", "desc": "Strengths & Weaknesses"},
    {"name": "Growth Tracker", "page": "Growth Tracker", "icon": "📈", "desc": "Progress Over Time"},
    {"name": "Institutional View", "page": "Institutional View", "icon": "🏛️", "desc": "College Analytics"},
    {"name": "About", "page": "About", "icon": "❓", "desc": "The Science Behind It"},
]

# Create columns for navigation
nav_cols = st.columns(len(nav_items) + 1)

# Add navigation links
for idx, item in enumerate(nav_items):
    with nav_cols[idx]:
        is_active = st.session_state.current_page == item['page']
        if st.button(
            f"{item['icon']} {item['name']}",
            key=f"nav_{item['page']}",
            type="primary" if is_active else "secondary",
            use_container_width=True,
            help=item['desc']
        ):
            st.session_state.current_page = item['page']
            st.rerun()

# CTA Button
with nav_cols[-1]:
    if st.button(
        "🚀 ANALYZE ME",
        key="analyze_btn",
        type="primary",
        use_container_width=True
    ):
        st.session_state.current_page = "Student Intake"
        st.rerun()

st.markdown("</div></div>", unsafe_allow_html=True)

# Sidebar - Student Profile Summary
with st.sidebar:
    st.image("https://img.icons8.com/fluency/96/student-center.png", width=80)
    st.markdown("## 👤 Student Profile")
    
    # Quick profile form
    with st.expander("Quick Student Info", expanded=True):
        student_name = st.text_input("Name", "Alex Johnson")
        student_id = st.text_input("Student ID", "CS2024001")
        semester = st.selectbox("Current Semester", [1,2,3,4,5,6,7,8])
        branch = st.selectbox("Branch", ["Computer Science", "Electronics", "Mechanical", "Civil", "Electrical"])
    
    st.markdown("---")
    
    # Real-time Intelligence Stats
    st.markdown("### 🧠 Intelligence Stats")
    
    # Generate some dynamic stats
    col1, col2 = st.columns(2)
    with col1:
        st.metric("Intelligence Score", "87", "+5")
        st.metric("Growth Rate", "12%", "+2%")
    with col2:
        st.metric("Career Fit", "92%", "+8%")
        st.metric("Consistency", "A-", "↑")
    
    st.markdown("---")
    
    # Quick Actions
    st.markdown("### ⚡ Quick Actions")
    if st.button("📊 Generate New Analysis", use_container_width=True):
        st.session_state.current_page = "Student Intake"
        st.rerun()
    
    if st.button("📥 Download Report", use_container_width=True):
        st.success("Report generated!")

# Main Content Area - Page Router
if st.session_state.current_page == "Intelligence Hub":
    st.markdown('<div class="section-header">🎯 Student Intelligence Hub</div>', unsafe_allow_html=True)
    
    # Top metrics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown("""
        <div class="metric-card">
            <div class="metric-label">Academic Index</div>
            <div class="metric-value">8.4/10</div>
            <div class="metric-trend">↑ 0.6 from last sem</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div class="metric-card">
            <div class="metric-label">Skill Strength</div>
            <div class="metric-value">84%</div>
            <div class="metric-trend">↑ 12% this year</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown("""
        <div class="metric-card">
            <div class="metric-label">Engagement Score</div>
            <div class="metric-value">92%</div>
            <div class="metric-trend">Top 15% of class</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col4:
        st.markdown("""
        <div class="metric-card">
            <div class="metric-label">Career Readiness</div>
            <div class="metric-value">78%</div>
            <div class="metric-trend">On track</div>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # Two column layout for detailed view
    col1, col2 = st.columns([1.5, 1])
    
    with col1:
        st.markdown("### 📊 Multi-Dimensional Analysis")
        
        # Radar chart for skills
        categories = ['Technical', 'Analytical', 'Creative', 'Leadership', 'Communication', 'Consistency']
        values = [85, 92, 68, 75, 70, 88]
        
        fig = go.Figure()
        fig.add_trace(go.Scatterpolar(
            r=values,
            theta=categories,
            fill='toself',
            name='Student Profile',
            line_color='#667eea',
            fillcolor='rgba(102, 126, 234, 0.3)'
        ))
        
        fig.update_layout(
            polar=dict(
                radialaxis=dict(visible=True, range=[0, 100]),
                bgcolor='rgba(255,255,255,0.05)'
            ),
            showlegend=False,
            height=400,
            paper_bgcolor='rgba(0,0,0,0)',
            font_color='white'
        )
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        st.markdown("### 🔥 Top Career Matches")
        
        careers = [
            {"name": "AI/ML Engineer", "fit": 94, "trend": "+5%"},
            {"name": "Data Scientist", "fit": 89, "trend": "+3%"},
            {"name": "Product Manager", "fit": 82, "trend": "+8%"},
            {"name": "Research Scientist", "fit": 78, "trend": "-2%"},
        ]
        
        for career in careers:
            st.markdown(f"""
            <div class="career-card">
                <div style="display: flex; justify-content: space-between; align-items: center;">
                    <span style="font-weight: 600;">{career['name']}</span>
                    <span class="fit-score">{career['fit']}%</span>
                </div>
                <div style="margin-top: 0.5rem;">
                    <div class="progress-container">
                        <div class="progress-fill" style="width: {career['fit']}%;"></div>
                    </div>
                </div>
                <div style="display: flex; justify-content: flex-end; margin-top: 0.5rem; color: #10B981;">
                    {career['trend']}
                </div>
            </div>
            """, unsafe_allow_html=True)
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # Growth trend
    st.markdown("### 📈 Growth Trajectory")
    
    # Sample data
    months = ['Aug', 'Sep', 'Oct', 'Nov', 'Dec', 'Jan']
    academic = [72, 75, 78, 82, 85, 88]
    skills = [65, 68, 72, 78, 82, 84]
    engagement = [80, 78, 82, 85, 88, 92]
    
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=months, y=academic, mode='lines+markers', name='Academic', line=dict(color='#667eea', width=3)))
    fig.add_trace(go.Scatter(x=months, y=skills, mode='lines+markers', name='Skills', line=dict(color='#10B981', width=3)))
    fig.add_trace(go.Scatter(x=months, y=engagement, mode='lines+markers', name='Engagement', line=dict(color='#FFD700', width=3)))
    
    fig.update_layout(
        height=400,
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font_color='white',
        xaxis=dict(gridcolor='rgba(255,255,255,0.1)'),
        yaxis=dict(gridcolor='rgba(255,255,255,0.1)')
    )
    st.plotly_chart(fig, use_container_width=True)

elif st.session_state.current_page == "Career Mapper":
    st.markdown('<div class="section-header">🗺️ Career Alignment Engine</div>', unsafe_allow_html=True)
    
    st.markdown("""
    <div class="glass-panel" style="margin-bottom: 2rem;">
        <h3 style="color: white;">How Career Fit Is Calculated</h3>
        <p style="color: rgba(255,255,255,0.7);">Career Fit Score = (Academic Strength × 0.3) + (Interest Alignment × 0.3) + (Skill Match × 0.2) + (Effort Level × 0.2)</p>
    </div>
    """, unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### 🎯 Your Interest Profile")
        
        interests = {
            "Programming": 5,
            "Mathematics": 4,
            "AI/ML": 5,
            "Research": 3,
            "Product Design": 2,
            "Management": 4
        }
        
        for interest, score in interests.items():
            st.markdown(f"""
            <div style="margin: 1rem 0;">
                <div style="display: flex; justify-content: space-between; color: white;">
                    <span>{interest}</span>
                    <span>{score}/5</span>
                </div>
                <div class="progress-container">
                    <div class="progress-fill" style="width: {score*20}%;"></div>
                </div>
            </div>
            """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("### 🔧 Your Skill Matrix")
        
        skills = {
            "Technical": 85,
            "Analytical": 92,
            "Creative": 68,
            "Communication": 75,
        }
        
        for skill, score in skills.items():
            st.markdown(f"""
            <div style="margin: 1rem 0;">
                <div style="display: flex; justify-content: space-between; color: white;">
                    <span>{skill}</span>
                    <span>{score}%</span>
                </div>
                <div class="progress-container">
                    <div class="progress-fill" style="width: {score}%;"></div>
                </div>
            </div>
            """, unsafe_allow_html=True)
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # Career Recommendations
    st.markdown("### 🚀 Personalized Career Pathways")
    
    career_recommendations = [
        {
            "title": "AI/ML Engineer",
            "fit": 94,
            "salary": "₹15-25 LPA",
            "demand": "Very High",
            "skills": ["Python", "Machine Learning", "Deep Learning", "Statistics"],
            "path": "Take advanced ML courses → Build portfolio → Apply for internships"
        },
        {
            "title": "Data Scientist",
            "fit": 89,
            "salary": "₹12-20 LPA",
            "demand": "High",
            "skills": ["Python", "SQL", "Statistics", "Visualization"],
            "path": "Master statistics → Learn SQL → Work on Kaggle projects"
        },
        {
            "title": "Product Manager",
            "fit": 82,
            "salary": "₹18-30 LPA",
            "demand": "Very High",
            "skills": ["Business Acumen", "Technical Understanding", "Communication"],
            "path": "Learn product frameworks → Build side projects → Apply for APM roles"
        }
    ]
    
    for career in career_recommendations:
        with st.expander(f"{career['title']} - {career['fit']}% Match", expanded=True):
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Expected Salary", career['salary'])
            with col2:
                st.metric("Market Demand", career['demand'])
            with col3:
                st.metric("Your Fit", f"{career['fit']}%")
            
            st.markdown(f"**Skills Needed:** {', '.join(career['skills'])}")
            st.markdown(f"**Suggested Path:** {career['path']}")
            
            if st.button(f"📝 Create Learning Plan for {career['title']}", key=f"plan_{career['title']}"):
                st.success(f"Personalized learning plan generated for {career['title']}!")

elif st.session_state.current_page == "SWOT Analysis":
    st.markdown('<div class="section-header">📊 Data-Driven SWOT Analysis</div>', unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("""
        <div class="swot-strength">
            <h3 style="color: #10B981;">💪 Strengths</h3>
            <ul style="color: white;">
                <li>Strong analytical skills (92nd percentile)</li>
                <li>Consistent academic improvement (+16% over 2 semesters)</li>
                <li>Excellent programming fundamentals</li>
                <li>High engagement in technical activities</li>
                <li>Self-motivated learning behavior</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("""
        <div class="swot-weakness">
            <h3 style="color: #EF4444;">🔻 Weaknesses</h3>
            <ul style="color: white;">
                <li>Below-average creative/design thinking</li>
                <li>Limited team collaboration experience</li>
                <li>Inconsistent in non-technical subjects</li>
                <li>Low participation in extracurriculars</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div class="swot-opportunity">
            <h3 style="color: #F59E0B;">✨ Opportunities</h3>
            <ul style="color: white;">
                <li>High interest + moderate performance in AI = growth potential</li>
                <li>Emerging field of AI/ML has high demand</li>
                <li>Can leverage programming skills for research opportunities</li>
                <li>Industry certifications could boost profile</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("""
        <div class="swot-threat">
            <h3 style="color: #8B5CF6;">⚠️ Threats</h3>
            <ul style="color: white;">
                <li>Interest in AI high but project work limited</li>
                <li>Competition from peers with more practical experience</li>
                <li>Quickly evolving industry requirements</li>
                <li>Risk of burnout from high consistency focus</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # Strategic Recommendations
    st.markdown("### 🎯 Strategic Recommendations")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("""
        <div class="metric-card">
            <h4 style="color: #667eea;">Immediate (0-3 months)</h4>
            <ul style="color: white; text-align: left;">
                <li>Complete 2 ML projects</li>
                <li>Join a tech community</li>
                <li>Start LeetCode practice</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div class="metric-card">
            <h4 style="color: #667eea;">Short-term (3-6 months)</h4>
            <ul style="color: white; text-align: left;">
                <li>Apply for research internship</li>
                <li>Complete advanced ML course</li>
                <li>Participate in hackathon</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown("""
        <div class="metric-card">
            <h4 style="color: #667eea;">Long-term (6-12 months)</h4>
            <ul style="color: white; text-align: left;">
                <li>Build portfolio website</li>
                <li>Network with industry pros</li>
                <li>Prepare for placements</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)

elif st.session_state.current_page == "Growth Tracker":
    st.markdown('<div class="section-header">📈 Growth Tracker & Progress Analytics</div>', unsafe_allow_html=True)
    
    # Time period selector
    period = st.selectbox("Select Time Period", ["Last 6 months", "Last year", "Full academic history"])
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### 📊 Key Metrics Over Time")
        
        # Sample timeline data
        timeline_data = pd.DataFrame({
            'Month': ['Aug', 'Sep', 'Oct', 'Nov', 'Dec', 'Jan'],
            'CGPA': [7.2, 7.5, 7.8, 8.1, 8.3, 8.5],
            'Skill Score': [65, 68, 72, 78, 82, 85],
            'Projects': [1, 1, 2, 2, 3, 4]
        })
        
        fig = px.line(timeline_data, x='Month', y=['CGPA', 'Skill Score'], 
                     title="Growth Trajectory",
                     color_discrete_sequence=['#667eea', '#10B981'])
        fig.update_layout(height=400, paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font_color='white')
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        st.markdown("### 🏆 Achievements Milestone")
        
        achievements = [
            {"name": "First ML Project", "date": "Oct 2025", "icon": "🤖"},
            {"name": "Hackathon Participation", "date": "Nov 2025", "icon": "💻"},
            {"name": "CGPA > 8.0", "date": "Dec 2025", "icon": "📚"},
            {"name": "Published Article", "date": "Jan 2026", "icon": "📝"},
        ]
        
        for ach in achievements:
            st.markdown(f"""
            <div style="display: flex; align-items: center; gap: 1rem; background: rgba(255,255,255,0.05); padding: 1rem; border-radius: 15px; margin: 0.5rem 0;">
                <span style="font-size: 2rem;">{ach['icon']}</span>
                <div>
                    <div style="font-weight: 600; color: white;">{ach['name']}</div>
                    <div style="color: #94A3B8;">{ach['date']}</div>
                </div>
            </div>
            """, unsafe_allow_html=True)
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # Predictive Growth
    st.markdown("### 🔮 Predicted Growth Trajectory")
    
    future_months = ['Feb', 'Mar', 'Apr', 'May', 'Jun']
    predicted = [8.7, 8.9, 9.0, 9.1, 9.2]
    
    fig = px.area(x=future_months, y=predicted, title="CGPA Forecast (Next 5 Months)",
                 labels={'x': 'Month', 'y': 'Predicted CGPA'})
    fig.update_traces(line_color='#667eea', fillcolor='rgba(102, 126, 234, 0.3)')
    fig.update_layout(height=300, paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font_color='white')
    st.plotly_chart(fig, use_container_width=True)

elif st.session_state.current_page == "Institutional View":
    st.markdown('<div class="section-header">🏛️ Institutional Intelligence Dashboard</div>', unsafe_allow_html=True)
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown("""
        <div class="metric-card">
            <div class="metric-label">Total Students</div>
            <div class="metric-value">2,847</div>
            <div class="metric-trend">↑ 8% from 2025</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div class="metric-card">
            <div class="metric-label">Avg. Intelligence Score</div>
            <div class="metric-value">76.4</div>
            <div class="metric-trend">↑ 5.2 points</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown("""
        <div class="metric-card">
            <div class="metric-label">At-Risk Students</div>
            <div class="metric-value">342</div>
            <div class="metric-trend">↓ 12% from last sem</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col4:
        st.markdown("""
        <div class="metric-card">
            <div class="metric-label">Top Career Choice</div>
            <div class="metric-value">AI/ML</div>
            <div class="metric-trend">42% of students</div>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### 🎯 Department-wise Career Preferences")
        
        dept_data = pd.DataFrame({
            'Department': ['CSE', 'ECE', 'ME', 'Civil', 'Electrical'],
            'AI/ML': [45, 28, 12, 8, 22],
            'Core': [15, 42, 58, 67, 48],
            'Management': [25, 18, 22, 18, 20],
            'Research': [15, 12, 8, 7, 10]
        })
        
        fig = px.bar(dept_data, x='Department', y=['AI/ML', 'Core', 'Management', 'Research'],
                     title="Career Preferences by Department",
                     barmode='stack',
                     color_discrete_sequence=['#667eea', '#10B981', '#FFD700', '#FF6B6B'])
        fig.update_layout(height=400, paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font_color='white')
        st.plotly_chart(fig, use_container_width=True)
    
    