# ⚡ SPECTRA v4.0.0 — Student Intelligence & Career Guidance System

**🎯 Demo:** https://v3spectraedu.streamlit.app/  
**🏆 Innovation Challenge:** IIT Techkriti 2026

---

## 🌟 What's New in v4.0.0

### Major Features
- 🤖 **Ask SPECTRA** - AI chatbot for career guidance (powered by Google Generative AI)
- 📄 **Resume Reviewer** - Intelligent resume analysis and scoring with improvement suggestions
- 🧠 **Enhanced ML Pipeline** - Improved student clustering algorithm (K-Means + Silhouette optimization)
- 🔐 **Role-Based Access Control** - Admin dashboards for institutional analytics
- 📊 **Growth Forecasting** - Predict future intelligence scores based on trajectory
- 🎨 **Improved UI/UX** - Glassmorphism cards, smooth animations, dark theme optimization

### Under the Hood
- SQLite + JSON for hybrid relational-document storage
- Pre-trained ML models (career classifier, student clusterer, feature scaler)
- Streamlit caching for fast page transitions
- WAL mode SQLite for better concurrency

---

## 📂 Project Architecture

```
spectra/
├── Home.py                              # Landing page + navigation
├── requirements.txt                     # Python dependencies
├── README.md                            # This file
│
├── .streamlit/
│   ├── config.toml                      # Dark theme configuration
│   └── secrets.toml (TEMPLATE ONLY)     # ⚠️ Create with your credentials
│
├── assets/
│   ├── style.css                        # Global design system (Syne + Plus Jakarta Sans)
│   └── SPECTRA_Student_Data_Template.xlsx
│
├── components/                          # Reusable UI components
│   ├── cards.py                         # HTML card factory (feature cards, metrics, results)
│   ├── charts.py                        # Plotly chart templates (dark-themed)
│   ├── navbar.py                        # Top navigation (pages, logout)
│   ├── sidebar.py                       # Shared sidebar (user info, quick stats)
│   └── styles.py                        # CSS loader utility
│
├── pages/                               # Streamlit multipage routes
│   ├── 0_Student_Intake.py             # 📋 Profile form (name, CGPA, interests, skills)
│   ├── 1_Intelligence_Hub.py           # 🧠 Dashboard (intelligence score, radar, trajectory)
│   ├── 2_Career_Mapper.py              # 🗺️ Career fit scores + career pathways
│   ├── 3_SWOT_Analysis.py              # 📊 Dynamic SWOT + actionable roadmaps
│   ├── 4_Growth_Tracker.py             # 📈 Historical trends + forecasts
│   ├── 5_Institutional_View.py         # 🏛️ Admin dashboard (cohort analytics, batch uploads)
│   ├── 6_About.py                       # ℹ️ System documentation
│   ├── 7_Ask_Spectra.py                # 🤖 AI chatbot for Q&A
│   └── 8_Resume_Reviewer.py            # 📄 Resume analysis + scoring
│
├── utils/                               # Core business logic
│   ├── auth.py                         # 🔐 Authentication & RBAC (local + Google OAuth)
│   ├── database.py                     # 💾 SQLite ORM (students, careers, batches, SWOT cache)
│   ├── data_engine.py                  # 📥 Excel import + data transformation
│   ├── ml_engine.py                    # 🤖 ML pipeline (clustering, prediction)
│   ├── career_engine.py                # 🎯 Career fit formula + ranking
│   ├── analytics_engine.py             # 📊 Cohort analytics (risk, CGPA distribution)
│   ├── llm_engine.py                   # 🧠 LLM integration (Google Generative AI)
│   └── report_generator.py             # 📄 PDF/CSV export functionality
│
├── models/                              # Pre-trained ML models (binary format)
│   ├── career_classifier.pkl           # Multi-class career classifier
│   ├── student_clusterer.pkl           # K-Means clustering model
│   ├── feature_scaler.pkl              # StandardScaler for features
│   └── career_label_encoder.pkl        # Label encoding for career titles
│
└── data/
    ├── spectra.db                       # SQLite database (persistent storage)
    └── (auto-generated, excluded from git)
```

---

## 🚀 Quick Start

### Prerequisites
- Python 3.8+
- Git

### Installation

```bash
# 1. Clone the repository
git clone https://github.com/your-org/spectra.git
cd spectra

# 2. Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Set up secrets (development only)
cp .streamlit/secrets.toml.template .streamlit/secrets.toml
# Edit .streamlit/secrets.toml with your credentials:
# - Google OAuth client_id and secret (optional, but required for Google login)
# - Admin email list
# - Local users (bcrypt password hashes for demo auth)

# 5. Run locally
streamlit run Home.py
```

**Access:** http://localhost:8501

---

## 🔑 Key Features Explained

### 1. 🧠 Intelligence Scoring
Combines 4 weighted dimensions:
```
Intelligence Score = (Academic × 0.25) + (Interest Alignment × 0.30) 
                   + (Skill Match × 0.25) + (Effort × 0.20)

Range: 0-100 (normalized)
Risk Levels: Low (>70), Medium (50-70), High (<50)
```

### 2. 🎯 Career Fit Formula
Multi-factor matching engine:
```
Fit Score = (Academic Match × 0.25) + (Interest Alignment × 0.30) 
          + (Skill Proficiency × 0.25) + (Effort Required × 0.20)

Output: Ranked list of 6 careers with fit scores (0-100)
```

**Careers Covered:**
- Software Engineering
- Data Science
- Product Management
- DevOps/Cloud
- Machine Learning Engineer
- Business Analyst

### 3. 📊 Student Clustering
K-Means algorithm groups students into 3-5 clusters:
- **High Performers:** 80+ CGPA, consistent growth
- **Solid Performers:** 70-80, steady improvement
- **At-Risk:** <70, declining grades, low engagement
- **Emerging Stars:** Average grades, high effort
- **Special Interests:** Unique skill/interest combinations

### 4. 🤖 Ask SPECTRA (AI Chat)
Real-time chatbot powered by Google Generative AI:
- Ask career questions: "What skills do I need for ML engineering?"
- Get personalized advice: "Based on my profile, what should I focus on?"
- Explore paths: "What companies hire for [career]?"
- Conversation history stored per session

### 5. 📄 Resume Reviewer
Analyze uploaded PDF resumes:
- **Scoring:** ATS compatibility (0-100), content quality, skill alignment
- **Feedback:** Section-by-section recommendations
- **Enhancement:** AI suggestions for improvement
- **Export:** Download detailed analysis report

### 6. 📈 Growth Tracker
Track intelligence and CGPA evolution:
- Historical timeline (per semester)
- Trend analysis (improving, stable, declining)
- Forecast (3-semester projection using linear regression)
- Peer benchmarking (compare to cluster average)

### 7. 🏛️ Institutional View (Admin Only)
Cohort-level analytics dashboard:
- **Upload Batches:** Import Excel with 100+ students
- **Live Cohort Stats:** Total students, avg CGPA, at-risk count
- **Department Reports:** By branch/major
- **Risk Stratification:** Students needing intervention
- **Career Distribution:** Which paths students are pursuing

---

## 📊 Career Fit Formula Deep Dive

Each career has a unique "ideal profile." System matches your profile to each:

```python
# Example: Software Engineering ideal profile
ideal = {
    "academic": 0.80,           # Expects strong CS fundamentals
    "interests": ["coding", "problem-solving", "tech"],
    "skills": ["Python", "Java", "SQL", "DSA"],
    "effort_capacity": 0.8,     # Requires high effort
}

# Your profile scoring:
your_fit = {
    "academic_match": 0.75,     # Your CGPA percentile vs cohort
    "interest_alignment": 0.85, # How many interests match
    "skill_proficiency": 0.70,  # Avg skill level normalized
    "effort_capacity": 0.80,    # Self-rated effort level
}

# Final score = weighted sum of matches
fit_score = (0.75 * 0.25) + (0.85 * 0.30) + (0.70 * 0.25) + (0.80 * 0.20)
          = 0.78 * 100 = 78/100 (Good fit)
```

---

## 🔐 Authentication & Authorization

### Auth Methods
1. **Local Username/Password**
   - Hashed with bcrypt
   - Configured in `secrets.toml`

2. **Google OAuth 2.0** (Optional)
   - Sign in with Google account
   - Automatic role assignment from allowlist

### Role-Based Access
| Role | Access |
|------|--------|
| **Student** | All personal pages (intake, intelligence, career, SWOT, growth, chat, resume) |
| **Admin** | All student features + Institutional View (batch uploads, cohort analytics) |

### Protecting a Page
```python
# At top of page file:
from utils.auth import require_login, is_admin, require_role

require_login()  # Block unauthenticated users

# For admin-only pages:
if not is_admin():
    st.error("Admin access required")
    st.stop()
```

---

## 💾 Database Schema

### `students` table
Stores complete student profile:
```sql
student_id (PK)          — Unique identifier (e.g., "CS2024001")
name, college, branch, year, semester
cgpa, backlogs, academic_trend
effort, career_goal, timeline
skills_json              — JSON list of skills
interests_json           — JSON list of interests  
activities_json          — Projects, internships, certs, etc.
intelligence_score       — Computed 0-100 score
risk_level               — Low/Medium/High
cluster_id, cluster_name — ML clustering result
top_career, top_career_fit — Best-matching career + score
full_profile_json        — Complete profile snapshot (for quick loads)
created_at, updated_at   — Timestamps
```

### `career_results` table
Ranked career matches per student:
```sql
id (PK)
student_id (FK)
career_title            — Name of career path
fit_score, ml_score, formula_score — Different scoring methods
rank                    — 1-6 ranking
analysed_at
```

### `batches` table
Institutional batch uploads:
```sql
batch_id (PK)
institute               — Name of college/organization
student_count
cohort_stats_json       — Aggregate stats (avg CGPA, etc.)
dept_report_json        — Department breakdowns
raw_data_json           — Full uploaded data
created_at
```

### `swot_cache` table
Cached SWOT analyses (regenerated per update):
```sql
student_id (PK)
swot_json               — Strengths, weaknesses, opportunities, threats
generated_at
```

---

## 🎨 Design System

### Color Palette
| Color | Hex | Usage |
|-------|-----|-------|
| **Deep Slate** | #080C14 | Background (hero, cards) |
| **Slate Surface** | #0F1419 | Default background |
| **Slate Border** | #1E2230 | Dividers, borders |
| **Electric Cyan** | #00D4FF | Accents, highlights, hovers |
| **Amber** | #FFB800 | Call-to-action buttons |
| **Success Green** | #10B981 | Positive metrics, growth |
| **Error Red** | #EF4444 | Risk indicators, errors |
| **Text Primary** | #E2E8F0 | Main text |
| **Text Secondary** | #7A90B0 | Muted text, hints |

### Typography
- **Display:** Syne (bold, 800 weight) — Headings
- **Body:** Plus Jakarta Sans (regular, 400) — Content
- **Mono:** Courier New — Code snippets

### Components
- **Cards:** Glassmorphism (semi-transparent + blur)
- **Buttons:** Gradient from slate → cyan on hover
- **Charts:** Dark theme, cyan gridlines, muted labels
- **Animations:** Smooth hover transitions (200ms)
- **Spacing:** 8px grid (8, 16, 24, 32, 40px)

---

## 🔧 Configuration

### `secrets.toml` Template
```toml
# Local User Authentication (optional)
[local_users]
admin = { display_name = "Admin User", password_hash = "bcrypt_hash_here", role = "admin" }
student = { display_name = "Student Demo", password_hash = "bcrypt_hash_here", role = "student" }

# Google OAuth 2.0 (optional)
[google_oauth]
client_id = "your-google-oauth-client-id"
client_secret = "your-google-oauth-client-secret"

# Role-based access control
[roles]
admin_emails = ["admin@college.edu"]

# LLM Configuration
[llm]
google_api_key = "your-google-generative-ai-key"
model = "gemini-1.5-flash"
```

### `.streamlit/config.toml`
```toml
[theme]
primaryColor = "#00D4FF"
backgroundColor = "#080C14"
secondaryBackgroundColor = "#0F1419"
textColor = "#E2E8F0"
font = "sans serif"

[client]
showErrorDetails = true
toolbarMode = "developer"

[logger]
level = "info"
```

---

## 📦 Dependencies

| Package | Version | Purpose |
|---------|---------|---------|
| **streamlit** | >=1.35.0 | Web framework |
| **pandas** | >=2.0.0 | Data manipulation |
| **numpy** | >=1.26.0 | Numerical computing |
| **plotly** | >=5.18.0 | Interactive charts |
| **scikit-learn** | >=1.4.0 | ML models (clustering, scaling) |
| **joblib** | >=1.3.0 | Model serialization |
| **openpyxl** | 3.1.5 | Excel parsing |
| **google-generativeai** | >=0.5.0 | Google AI API |
| **pdfplumber** | >=0.10.0 | PDF text extraction |
| **bcrypt** | >=4.0.0 | Password hashing ⚠️ *Missing in original* |

---

## 🐛 Known Issues & Workarounds

### 1. Model Loading Slow on First Access
**Issue:** First-time model load takes 5-10 seconds  
**Workaround:** Already cached with `@st.cache_resource` in `ml_engine.py`

### 2. PDF Resume Parsing
**Issue:** Scanned PDFs (image-based) cannot be parsed  
**Workaround:** Convert to text-based PDF first or manually enter resume

### 3. Session State Refresh
**Issue:** Hard-refresh (Ctrl+Shift+R) clears session but keeps DB data  
**Expected:** This is correct behavior (safety feature)

### 4. Concurrent Admin Uploads
**Issue:** Multiple simultaneous batch uploads may have race conditions  
**Workaround:** Add queue system in future version

---

## 🧪 Testing

### Run Unit Tests
```bash
pytest tests/ -v
```

### Manual Test Cases
- [ ] Create new student profile (all fields)
- [ ] Verify intelligence score calculation
- [ ] Check career ranking matches formula
- [ ] Upload batch Excel (100+ students)
- [ ] Ask SPECTRA question and verify response
- [ ] Upload and analyze resume PDF
- [ ] Admin: View cohort dashboard
- [ ] Logout and re-login

---

## 📈 Performance Tips

1. **Cache ML Models**  
   ✅ Already implemented with `@st.cache_resource`

2. **Database Queries**  
   ✅ Using indexes on `name`, `college`, `branch`

3. **Session State**  
   ⚠️ Consider: Move large objects to database, fetch on demand

4. **CSS & Assets**  
   ⚠️ Consider: Minify CSS (currently 18KB)

---

## 🚀 Deployment

### Streamlit Cloud
```bash
# 1. Push to GitHub
git push origin main

# 2. Create new app on streamlit.io
# 3. Connect to GitHub repo
# 4. Add secrets via Settings tab:
#    - google_oauth credentials
#    - local_users (bcrypt hashes)
#    - admin_emails
# 5. App auto-deploys on git push
```

### Docker
```dockerfile
FROM python:3.11-slim
WORKDIR /app
COPY . .
RUN pip install -r requirements.txt
EXPOSE 8501
CMD ["streamlit", "run", "Home.py"]
```

### Self-Hosted (Ubuntu)
```bash
# Install dependencies
sudo apt update && sudo apt install python3.11 python3.11-venv python3.11-dev

# Set up app
git clone https://github.com/your-org/spectra.git /opt/spectra
cd /opt/spectra
python3.11 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Run with PM2 or systemd
pm2 start "streamlit run Home.py" --name spectra --max-restarts 10
```

---

## 📞 Support & Contributing

### Report Bugs
Open issue on GitHub with:
- [ ] Steps to reproduce
- [ ] Expected vs. actual behavior
- [ ] Browser/OS version
- [ ] Error screenshot or log

### Contribute
```bash
git checkout -b feature/your-feature
# Make changes
git commit -am "Add your feature"
git push origin feature/your-feature
# Open Pull Request
```

---

## 📜 License

MIT License - See LICENSE file for details

---

## 🙏 Credits

**Built for:** IIT Techkriti 2026 Innovation Challenge  
**Team:** SPECTRA Development Team  
**Inspiration:** Student career guidance gap in emerging markets

---

## 📊 Version Timeline

| Version | Date | Key Updates |
|---------|------|-----------|
| **V4.0.0** | Mar 2026 | ⭐ Resume Reviewer, Ask SPECTRA, improved clustering |
| v3.1.0 | Jan 2026 | Admin dashboard, batch uploads, risk analytics |
| v3.0.0 | Nov 2025 | Complete rewrite: ML pipeline, LLM integration |
| v2.0.0 | Sep 2024 | Multipage architecture, career engine |
| v1.0.0 | Mar 2024 | MVP: single-page app |

---

**Last Updated:** March 1, 2026  
**Next Major Update:** Q3 2026 (v5.0 - Mobile App)

---

## 🌟 Star History

If you find SPECTRA useful, please ⭐ on GitHub!

```
⭐⭐⭐⭐⭐ v4.0.0 (Current)
  ↓
⭐⭐⭐⭐  v3.1.0
  ↓
⭐⭐⭐   v3.0.0
  ↓
⭐⭐    v2.0.0
  ↓
⭐     v1.0.0
```

---

**Questions?** Create an issue or email: prnanvxag@gmailcom
