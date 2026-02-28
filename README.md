# ⚡ SPECTRA v2.0 — Student Intelligence & Career Guidance System

**Visit us at: https://v3spectraedu.streamlit.app/**

> IIT Techkriti 2026 Innovation Challenge

## 🗂️ Project Structure

```
spectra/
├── Home.py                         # Entry point (landing page + nav)
├── requirements.txt
├── .streamlit/
│   └── config.toml                 # Dark theme config
│
├── assets/
│   └── style.css                   # Full design system (600+ lines)
│
├── components/
│   ├── __init__.py
│   ├── styles.py                   # CSS loader (load_css())
│   ├── cards.py                    # Reusable HTML card components
│   ├── charts.py                   # Plotly chart factory (themed)
│   └── sidebar.py                  # Shared sidebar (all pages)
│
├── utils/
│   ├── __init__.py
│   └── career_engine.py            # Career fit scoring + SWOT logic
│
└── pages/
    ├── 0_Student_Intake.py         # Profile form (feeds everything)
    ├── 1_Intelligence_Hub.py       # KPIs, radar chart, trajectory
    ├── 2_Career_Mapper.py          # Career fit scores + pathways
    ├── 3_SWOT_Analysis.py          # Dynamic SWOT + roadmap
    ├── 4_Growth_Tracker.py         # Historical trends + forecast
    ├── 5_Institutional_View.py     # Admin analytics dashboard
    └── 6_About.py                  # Science + tech stack
```

## 🚀 Run Locally

```bash
pip install -r requirements.txt
streamlit run Home.py
```

## 🔑 Key Improvements Over v1

| Area | v1 | v2 |
|------|----|----|
| Architecture | Single 800-line `app.py` | Multipage with shared components |
| Data | All hardcoded | Real intake form → session state |
| Career Scoring | None (static list) | Weighted formula engine |
| SWOT | Hardcoded bullets | Dynamically generated from profile |
| CSS | Inline in Python string | External `assets/style.css` |
| Charts | Repeated dark theme code | `charts.py` factory (DRY) |
| Cards | Repeated HTML strings | `cards.py` component library |
| Navigation | Manual `if/elif` router + `st.rerun()` | `st.switch_page()` |
| Caching | None | `@st.cache_data` ready |
| Download | Fake `st.success` | Real CSV download |
| Sidebar | Isolated per-page | Shared `render_sidebar()` |

## 📐 Career Fit Formula

```
Career Fit Score = (Academic × 0.25) + (Interest Alignment × 0.30) 
                 + (Skill Match × 0.25) + (Effort Level × 0.20)
```

## 🎨 Design System

- **Font:** Syne (display) + Plus Jakarta Sans (body)
- **Palette:** Deep Slate (#080C14) + Electric Cyan (#00D4FF) + Amber (#FFB800)
- **Components:** Glassmorphism cards, animated skill bars, hover effects
- **Charts:** Consistent dark theme via `apply_dark_theme()` factory
