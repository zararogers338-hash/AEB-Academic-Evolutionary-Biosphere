# -*- coding: utf-8 -*-
"""AEB Page: 适应度曲线 / Fitness Curve"""
import streamlit as st
import plotly.graph_objects as go
from utils.i18n import init_lang, t
from utils.data_engine import get_engine
from utils.aeb_model import render_ai_panel, ai_analyze
from utils.export_utils import render_export_panel
from utils.chart_theme import apply_theme, PALETTE_NEON

init_lang()
st.set_page_config(page_title=f"AEB - {t('fitness_curve')}", layout="wide")
st.title(f"📈 {t('fitness_curve')}")

engine = get_engine()
if not engine.is_computed or engine.keywords_df.empty:
    st.info(t("no_data")); st.stop()

kw_list = engine.keywords_df["keyword"].tolist()
selected_kws = st.multiselect(t("select_keyword"), kw_list, default=kw_list[:5], key="fc_kws")
if not selected_kws: st.info("请至少选择一个关键词 / Select at least one keyword"); st.stop()

fig = go.Figure()
analysis_data = {}
for idx, kw in enumerate(selected_kws):
    fitness = engine.get_fitness_data(kw)
    if not fitness: continue
    years = [d["year"] for d in fitness]
    counts = [d["count"] for d in fitness]
    color = PALETTE_NEON[idx % len(PALETTE_NEON)]
    fig.add_trace(go.Scatter(
        x=years, y=counts, mode="lines+markers", name=kw,
        line=dict(color=color, width=2.5), marker=dict(size=6, color=color),
        hovertemplate=f"<b>{kw}</b><br>Year: %{{x}}<br>Count: %{{y}}<extra></extra>",
        fill="tozeroy", fillcolor=f"rgba({int(color[1:3],16)},{int(color[3:5],16)},{int(color[5:7],16)},0.05)",
    ))
    if counts:
        peak_idx = counts.index(max(counts))
        peak_year, peak_val = years[peak_idx], counts[peak_idx]
        analysis_data[kw] = {"peak_year": peak_year, "peak_count": peak_val, "current_count": counts[-1]}
        fig.add_annotation(x=peak_year, y=peak_val, text=f"⬆ {kw}", showarrow=True,
            arrowhead=2, arrowcolor=color, font=dict(size=10, color=color), bgcolor="rgba(6,13,31,0.8)")

apply_theme(fig, height=500, title_text="Keyword Fitness Over Time / 关键词适应度时间曲线",
    xaxis_title="Year / 年份", yaxis_title="Frequency / 频率",
    legend=dict(orientation="h", yanchor="bottom", y=1.02, bgcolor="rgba(6,13,31,0.7)"))
st.plotly_chart(fig, use_container_width=True)

st.markdown("### Period Analysis / 时期分析")
cols = st.columns(min(len(analysis_data), 4))
for i, (kw, info) in enumerate(analysis_data.items()):
    ratio = info["current_count"] / info["peak_count"] if info["peak_count"] > 0 else 0
    status = "🟢 Thriving" if ratio > 0.8 else "🟡 Declining" if ratio > 0.3 else "🔴 Near-extinct"
    with cols[i % len(cols)]:
        st.metric(kw, f"Peak: {info['peak_year']}", delta=status)

st.markdown("---")
if st.button(t("run_ai"), key="fc_ai_btn", type="primary"):
    prompt = f"""分析以下关键词的适应度曲线:
关键词: {', '.join(selected_kws)}
各关键词峰值数据: {analysis_data}
请用中英双语分析: 1)各关键词的生命周期阶段 2)巅峰期/衰退期 3)未来趋势预测 4)哪些可能复兴"""
    st.session_state["ai_result_fc"] = ai_analyze(prompt)
render_ai_panel("fc")
render_export_panel("fitness_curve", data=analysis_data, df=engine.keywords_df[engine.keywords_df["keyword"].isin(selected_kws)])
