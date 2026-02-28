"""
components/charts.py  —  Plotly chart factory
All charts share the same dark theme. Import and call these instead of
building figures inline.
"""
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd

# ── Shared theme ──────────────────────────────────────────────────
CYAN   = "#00D4FF"
AMBER  = "#FFB800"
GREEN  = "#00E887"
ROSE   = "#FF4D6A"
PURPLE = "#A78BFA"

COLOR_SEQ = [CYAN, AMBER, GREEN, ROSE, PURPLE, "#FF8C42"]

DARK_LAYOUT = dict(
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="rgba(8,12,20,0.6)",
    font=dict(family="Plus Jakarta Sans", color="#7A90B0", size=12),
    margin=dict(l=10, r=10, t=40, b=10),
    hoverlabel=dict(
        bgcolor="#141D2E",
        font_color="#E2E8F0",
        bordercolor="#2A3A58",
    ),
)

GRID = dict(gridcolor="rgba(42,58,88,0.6)", zerolinecolor="rgba(42,58,88,0.6)")


def apply_theme(fig: go.Figure, height: int = 380, title: str = ""):
    """Apply shared dark theme to any figure."""
    fig.update_layout(
        **DARK_LAYOUT,
        height=height,
        title=dict(text=title, font=dict(family="Syne", color="#E2E8F0", size=15)),
    )
    return fig


# ── Chart builders ────────────────────────────────────────────────

def radar_chart(categories: list, values: list, name: str = "Student") -> go.Figure:
    fig = go.Figure()
    fig.add_trace(go.Scatterpolar(
        r=values + [values[0]],
        theta=categories + [categories[0]],
        fill="toself",
        name=name,
        line=dict(color=CYAN, width=2.5),
        fillcolor="rgba(0, 212, 255, 0.12)",
        marker=dict(size=6, color=CYAN),
    ))
    fig.update_layout(
        **DARK_LAYOUT,
        height=400,
        polar=dict(
            bgcolor="rgba(13, 20, 33, 0.8)",
            radialaxis=dict(
                visible=True, range=[0, 100],
                gridcolor="rgba(42,58,88,0.8)",
                linecolor="rgba(42,58,88,0.8)",
                tickfont=dict(size=10, color="#4A5A7A"),
            ),
            angularaxis=dict(
                linecolor="rgba(42,58,88,0.8)",
                gridcolor="rgba(42,58,88,0.5)",
                tickfont=dict(size=11, color="#7A90B0"),
            ),
        ),
        showlegend=False,
    )
    return fig


def line_chart(df: pd.DataFrame, x: str, y_cols: list,
               title: str = "", height: int = 380) -> go.Figure:
    fig = go.Figure()
    for i, col in enumerate(y_cols):
        fig.add_trace(go.Scatter(
            x=df[x], y=df[col],
            mode="lines+markers",
            name=col,
            line=dict(color=COLOR_SEQ[i], width=2.5),
            marker=dict(size=7, color=COLOR_SEQ[i],
                        line=dict(color="#080C14", width=2)),
        ))
    fig.update_layout(**DARK_LAYOUT, height=height,
                      title=dict(text=title, font=dict(family="Syne", color="#E2E8F0", size=14)))
    fig.update_xaxes(**GRID)
    fig.update_yaxes(**GRID)
    return fig


def area_chart(x: list, y: list, title: str = "", height: int = 320) -> go.Figure:
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=x, y=y, mode="lines+markers",
        fill="tozeroy",
        line=dict(color=CYAN, width=2.5),
        fillcolor="rgba(0, 212, 255, 0.08)",
        marker=dict(size=7, color=CYAN, line=dict(color="#080C14", width=2)),
    ))
    fig.update_layout(**DARK_LAYOUT, height=height,
                      title=dict(text=title, font=dict(family="Syne", color="#E2E8F0", size=14)))
    fig.update_xaxes(**GRID)
    fig.update_yaxes(**GRID)
    return fig


def stacked_bar(df: pd.DataFrame, x: str, y_cols: list,
                title: str = "", height: int = 380) -> go.Figure:
    fig = go.Figure()
    for i, col in enumerate(y_cols):
        fig.add_trace(go.Bar(
            x=df[x], y=df[col], name=col,
            marker_color=COLOR_SEQ[i],
            marker_line_color="rgba(0,0,0,0)",
        ))
    fig.update_layout(
        **DARK_LAYOUT, barmode="stack", height=height,
        title=dict(text=title, font=dict(family="Syne", color="#E2E8F0", size=14)),
        bargap=0.3,
        legend=dict(
            bgcolor="rgba(13,20,33,0.8)",
            bordercolor="#2A3A58",
            font=dict(color="#7A90B0"),
        ),
    )
    fig.update_xaxes(**GRID)
    fig.update_yaxes(**GRID)
    return fig


def gauge_chart(value: float, title: str = "", max_val: float = 100) -> go.Figure:
    fig = go.Figure(go.Indicator(
        mode="gauge+number",
        value=value,
        title=dict(text=title, font=dict(family="Syne", color="#E2E8F0", size=14)),
        number=dict(font=dict(family="Syne", color="#E2E8F0", size=32), suffix="%"),
        gauge=dict(
            axis=dict(range=[0, max_val], tickcolor="#4A5A7A",
                      tickfont=dict(color="#4A5A7A")),
            bar=dict(color=CYAN),
            bgcolor="rgba(13,20,33,0.8)",
            bordercolor="#2A3A58",
            steps=[
                dict(range=[0, 50], color="rgba(255,77,106,0.1)"),
                dict(range=[50, 75], color="rgba(255,184,0,0.1)"),
                dict(range=[75, 100], color="rgba(0,232,135,0.1)"),
            ],
            threshold=dict(line=dict(color=AMBER, width=3), value=value),
        ),
    ))
    fig.update_layout(**DARK_LAYOUT, height=280)
    return fig


def scatter_bubble(df: pd.DataFrame, x: str, y: str, size: str, color: str,
                   title: str = "", height: int = 380) -> go.Figure:
    fig = px.scatter(
        df, x=x, y=y, size=size, color=color,
        title=title,
        color_discrete_sequence=COLOR_SEQ,
    )
    fig.update_layout(**DARK_LAYOUT, height=height,
                      title=dict(text=title, font=dict(family="Syne", color="#E2E8F0", size=14)))
    fig.update_xaxes(**GRID)
    fig.update_yaxes(**GRID)
    return fig


def donut_chart(labels: list, values: list, title: str = "") -> go.Figure:
    fig = go.Figure(go.Pie(
        labels=labels, values=values, hole=0.6,
        marker=dict(colors=COLOR_SEQ, line=dict(color="#080C14", width=2)),
        textfont=dict(color="#E2E8F0"),
    ))
    fig.update_layout(
        **DARK_LAYOUT, height=300,
        title=dict(text=title, font=dict(family="Syne", color="#E2E8F0", size=14)),
        showlegend=True,
        legend=dict(bgcolor="rgba(0,0,0,0)", font=dict(color="#7A90B0")),
    )
    return fig
