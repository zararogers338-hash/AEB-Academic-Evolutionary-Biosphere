# -*- coding: utf-8 -*-
"""AEB Page: 物种起源追溯 / Species Origin Trace"""
import streamlit as st
import plotly.graph_objects as go
from utils.i18n import init_lang, t
from utils.data_engine import get_engine
from utils.aeb_model import render_ai_panel, ai_analyze
from utils.export_utils import render_export_panel
from utils.chart_theme import apply_theme

init_lang()
st.set_page_config(page_title=f"AEB - {t('origin_trace')}", layout="wide")
st.title(f"🔬 {t('origin_trace')}")

engine = get_engine()
if not engine.is_computed or engine.keywords_df.empty:
    st.info(t("no_data")); st.stop()

kw_list = engine.keywords_df["keyword"].tolist()
selected = st.selectbox(t("select_keyword"), kw_list, key="ot_kw")
if not selected: st.stop()

# Trace back
st.subheader(f"Origin Trace: {selected}")
trace_chain = [selected]
visited = {selected}
current = selected
for _ in range(10):
    neighbors = engine.get_keyword_neighbors(current)
    found = False
    for n, w in neighbors:
        if n not in visited:
            n_row = engine.keywords_df[engine.keywords_df["keyword"] == n]
            c_row = engine.keywords_df[engine.keywords_df["keyword"] == current]
            if not n_row.empty and not c_row.empty:
                if n_row.iloc[0].get("first_year", 2020) <= c_row.iloc[0].get("first_year", 2020):
                    trace_chain.append(n); visited.add(n); current = n; found = True; break
    if not found:
        for n, w in neighbors:
            if n not in visited:
                trace_chain.append(n); visited.add(n); current = n; break
        else:
            break

# Tree display
st.markdown("### 🌱 Ancestry Chain / 祖先链")
for i, kw in enumerate(reversed(trace_chain)):
    prefix = "  " * i + ("🌱" if i == 0 else "├─" if i < len(trace_chain) - 1 else "└─")
    row = engine.keywords_df[engine.keywords_df["keyword"] == kw]
    score = f"{row.iloc[0]['score']:.4f}" if not row.empty else "?"
    st.text(f"{prefix} {kw} (score: {score})")

# Chart
if len(trace_chain) > 1:
    scores = []
    for kw in trace_chain:
        row = engine.keywords_df[engine.keywords_df["keyword"] == kw]
        scores.append(float(row.iloc[0]["score"]) if not row.empty else 0)
    show_labels = st.session_state.get("show_node_labels", False)
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=list(range(len(trace_chain))), y=scores, mode="lines+markers+text" if show_labels else "lines+markers",
        text=trace_chain if show_labels else None, textposition="top center", textfont=dict(size=10, color="#00ffaa"),
        marker=dict(size=14, color=scores, colorscale="Viridis", line=dict(width=2, color="#00ffaa")),
        line=dict(width=3, color="#00ffaa", shape="spline"),
        fill="tozeroy", fillcolor="rgba(0,255,170,0.05)",
        hovertext=trace_chain,
        hoverinfo="text+y",
    ))
    apply_theme(fig, height=420, title_text=f"Origin Trace: {selected} → Root",
        xaxis_title="Depth (deeper = older)", yaxis_title="Score")
    st.plotly_chart(fig, use_container_width=True)

st.markdown("### 📄 Origin Papers")
for kw in trace_chain:
    matching = engine.papers_df[engine.papers_df["text"].str.contains(kw, case=False, na=False)]
    if not matching.empty:
        st.text(f"  📄 {kw}: found in {len(matching)} papers (earliest: {matching['year'].min()})")

st.markdown("---")
if st.button(t("run_ai"), key="ot_ai_btn", type="primary"):
    chain_str = " → ".join(reversed(trace_chain))
    prompt = f"""分析关键词的物种起源追溯链:
目标: {selected}
祖先链: {chain_str}
请用中英双语描述: 1)起源故事 2)每个祖先词的历史地位 3)进化中的关键突变 4)当前物种与祖先的差异"""
    st.session_state["ai_result_ot"] = ai_analyze(prompt)
render_ai_panel("ot")
render_export_panel("origin_trace", data={"keyword": selected, "chain": trace_chain})
