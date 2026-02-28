"""
components/cards.py  —  Reusable HTML building blocks
All functions return HTML strings; call via st.markdown(..., unsafe_allow_html=True)
"""

def metric_card(label: str, value: str, trend: str = "", trend_dir: str = "up") -> str:
    """A KPI metric card."""
    trend_class = "down" if trend_dir == "down" else ("neutral" if trend_dir == "neutral" else "")
    trend_icon = "↓" if trend_dir == "down" else ("→" if trend_dir == "neutral" else "↑")
    trend_html = f'<div class="mc-trend {trend_class}">{trend_icon} {trend}</div>' if trend else ""
    return f"""
    <div class="metric-card">
        <div class="mc-label">{label}</div>
        <div class="mc-value">{value}</div>
        {trend_html}
    </div>
    """


def career_card(name: str, fit: int, trend: str = "") -> str:
    """A career match card with progress bar."""
    return f"""
    <div class="career-card">
        <div style="display:flex; justify-content:space-between; align-items:flex-start;">
            <span class="career-name">{name}</span>
            <span class="career-score">{fit}%</span>
        </div>
        <div class="career-bar-bg">
            <div class="career-bar-fill" style="width:{fit}%;"></div>
        </div>
        <div class="career-trend">{trend}</div>
    </div>
    """


def skill_bar(label: str, value: int, max_val: int = 100) -> str:
    """A horizontal skill progress bar."""
    pct = round((value / max_val) * 100)
    return f"""
    <div class="skill-row">
        <div class="skill-label">
            <span>{label}</span>
            <span>{value}{'' if max_val == 100 else f'/{max_val}'}</span>
        </div>
        <div class="skill-bar-bg">
            <div class="skill-bar-fill" style="width:{pct}%;"></div>
        </div>
    </div>
    """


def swot_card(card_type: str, title: str, icon: str, items: list) -> str:
    """SWOT quadrant card. card_type: strength | weakness | opportunity | threat"""
    items_html = "".join([
        f'<div class="swot-item"><div class="swot-dot"></div><span>{item}</span></div>'
        for item in items
    ])
    return f"""
    <div class="swot-card swot-{card_type}">
        <div class="swot-title">{icon} {title}</div>
        {items_html}
    </div>
    """


def achievement_item(icon: str, name: str, date: str) -> str:
    return f"""
    <div class="achievement-item">
        <div class="achievement-icon">{icon}</div>
        <div>
            <div class="achievement-name">{name}</div>
            <div class="achievement-date">{date}</div>
        </div>
    </div>
    """


def glass_panel(content: str) -> str:
    return f'<div class="glass-panel">{content}</div>'


def section_title(icon: str, text: str, accent: str = "") -> str:
    accent_html = f' <span class="accent">{accent}</span>' if accent else ""
    return f'<div class="section-title">{icon} {text}{accent_html}</div>'


def formula_box(formula: str) -> str:
    return f'<div class="formula-box">{formula}</div>'


def pill(text: str, color: str = "cyan") -> str:
    return f'<span class="pill pill-{color}">{text}</span>'


def roadmap_card(phase: str, title: str, items: list, color: str = "cyan") -> str:
    items_html = "".join([f'<div class="roadmap-item">• {item}</div>' for item in items])
    return f"""
    <div class="roadmap-card">
        <div class="roadmap-phase" style="color: {'#00D4FF' if color=='cyan' else '#FFB800' if color=='amber' else '#00E887'};">{phase}</div>
        <div class="roadmap-title">{title}</div>
        {items_html}
    </div>
    """


def glow_divider() -> str:
    return '<div class="glow-divider"></div>'


def about_feature(icon: str, title: str, desc: str) -> str:
    return f"""
    <div class="about-feature">
        <div class="about-icon">{icon}</div>
        <div class="about-feature-title">{title}</div>
        <div class="about-feature-desc">{desc}</div>
    </div>
    """
