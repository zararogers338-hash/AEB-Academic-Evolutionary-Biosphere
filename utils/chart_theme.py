# -*- coding: utf-8 -*-
"""AEB 统一图表主题 / Unified Chart Theme"""

# Plotly dark theme with AEB branding
AEB_LAYOUT = dict(
    template="plotly_dark",
    paper_bgcolor="rgba(6,13,31,0.9)",
    plot_bgcolor="rgba(6,13,31,0.6)",
    font=dict(family="Segoe UI, system-ui, sans-serif", color="#c0d8e8"),
    title_font=dict(size=16, color="#00ffaa"),
    xaxis=dict(gridcolor="rgba(0,255,170,0.08)", zerolinecolor="rgba(0,255,170,0.15)"),
    yaxis=dict(gridcolor="rgba(0,255,170,0.08)", zerolinecolor="rgba(0,255,170,0.15)"),
    legend=dict(bgcolor="rgba(6,13,31,0.7)", bordercolor="rgba(0,255,170,0.2)", borderwidth=1),
    margin=dict(l=50, r=30, t=60, b=50),
    hoverlabel=dict(bgcolor="rgba(6,13,31,0.95)", bordercolor="#00ffaa", font_color="#00ffaa"),
)

# Color palettes
PALETTE_NEON = ["#00ffaa", "#ff8844", "#4488ff", "#ff44aa", "#ffcc00", "#44ffcc", "#ff4466", "#88ff44", "#8844ff", "#ff8888"]
PALETTE_NATURE = ["#2ecc71", "#e74c3c", "#3498db", "#f39c12", "#9b59b6", "#1abc9c", "#e67e22", "#34495e"]
PALETTE_STATUS = {"alive": "#00ffaa", "fading": "#ffaa00", "extinct": "#ff4466"}

ROLE_COLORS = {"top_predator": "#ff2255", "dominant": "#00ffaa", "symbiotic": "#4488ff"}
COMMUNITY_COLORS = PALETTE_NEON


def apply_theme(fig, height=450, **kwargs):
    """Apply unified AEB theme to a Plotly figure."""
    layout_update = {**AEB_LAYOUT, "height": height}
    layout_update.update(kwargs)
    fig.update_layout(**layout_update)
    return fig
