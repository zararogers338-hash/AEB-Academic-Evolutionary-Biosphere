# -*- coding: utf-8 -*-
"""AEB Page: 沉积速率监控 / Sedimentation Rate Monitor"""
import streamlit as st
import plotly.graph_objects as go
from collections import Counter
from utils.i18n import init_lang, t
from utils.data_engine import get_engine
from utils.aeb_model import render_ai_panel, ai_analyze
from utils.export_utils import render_export_panel
from utils.chart_theme import apply_theme

init_lang()
st.set_page_config(page_title=f"AEB - {t('sedimentation')}", layout="wide")
st.title(f"⛰️ {t('sedimentation')}")

engine = get_engine()
if not engine.is_computed or engine.papers_df.empty:
    st.info(t("no_data")); st.stop()

year_counts = Counter(engine.papers_df["year"].tolist())
years = sorted(year_counts.keys())
counts = [year_counts[y] for y in years]
rates = [0] + [counts[i] - counts[i-1] for i in range(1, len(counts))]
threshold = st.slider("Warning Threshold / 警告阈值", 1, 100, 50, key="sed_thresh")

max_rate = max(counts) if counts else 0
if max_rate > threshold:
    st.markdown(f"""<div style="background:linear-gradient(90deg,#ff3355,#cc2244);color:white;text-align:center;
    padding:12px;font-weight:600;border-radius:8px;margin-bottom:15px;">
    ⚠️ {t('sedimentation_warning')} — Max: {max_rate}/year</div>""", unsafe_allow_html=True)

fig = go.Figure()
fig.add_trace(go.Bar(
    x=years, y=counts, name="Papers/Year",
    marker=dict(color=["#ff4466" if c > threshold else "#00ffaa" for c in counts],
                line=dict(width=0)),
    hovertemplate="Year: %{x}<br>Papers: %{y}<extra></extra>",
))
fig.add_trace(go.Scatter(
    x=years, y=rates, name="Rate Change", mode="lines+markers",
    line=dict(color="#ffcc00", width=2.5, shape="spline"),
    marker=dict(size=5, color="#ffcc00"),
    yaxis="y2",
))
fig.add_hline(y=threshold, line_dash="dash", line_color="rgba(255,68,102,0.6)",
    annotation_text=f"Threshold: {threshold}", annotation_font_color="#ff4466")
apply_theme(fig, height=480, title_text="Sedimentation Rate / 沉积速率",
    xaxis_title="Year", yaxis_title="Papers",
    yaxis2=dict(title="Rate Change", overlaying="y", side="right", gridcolor="rgba(255,204,0,0.05)"),
    barmode="overlay")
st.plotly_chart(fig, use_container_width=True)

c1, c2, c3, c4 = st.columns(4)
c1.metric("Total Papers", sum(counts))
c2.metric("Peak Year", years[counts.index(max(counts))] if counts else "N/A")
c3.metric("Peak Rate", max(counts))
c4.metric("Avg Rate", f"{sum(counts)/len(counts):.1f}" if counts else "0")

st.markdown("---")
if st.button(t("run_ai"), key="sed_ai_btn", type="primary"):
    prompt = f"""分析学术沉积速率: 年度论文数: {dict(zip(years, counts))}, 峰值: {max(counts)}/year, 阈值: {threshold}
请用中英双语分析: 1)趋势 2)知识爆炸? 3)爆发期与冷却期 4)对生态系统影响"""
    st.session_state["ai_result_sed"] = ai_analyze(prompt)
render_ai_panel("sed")
render_export_panel("sedimentation", data={"years": years, "counts": counts, "rates": rates})
