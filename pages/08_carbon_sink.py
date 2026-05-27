# -*- coding: utf-8 -*-
"""AEB Page: 碳汇计算 / Carbon Sink Calculation"""
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
from utils.i18n import init_lang, t
from utils.data_engine import get_engine
from utils.aeb_model import render_ai_panel, ai_analyze
from utils.export_utils import render_export_panel
from utils.chart_theme import apply_theme

init_lang()
st.set_page_config(page_title=f"AEB - {t('carbon_sink')}", layout="wide")
st.title(f"🌿 {t('carbon_sink')}")

engine = get_engine()
if not engine.is_computed or engine.keywords_df.empty:
    st.info(t("no_data")); st.stop()

df = engine.keywords_df.copy()
df = df[df["carbon_sink"] > 0].sort_values("carbon_sink", ascending=False).head(60)
if df.empty: st.warning("No carbon sink data / 无碳汇数据"); st.stop()

col_a, col_b = st.columns(2)
show_labels = st.session_state.get("show_node_labels", False)
with col_a:
    fig = px.treemap(df, path=["eco_role", "keyword"], values="carbon_sink",
        color="carbon_sink", color_continuous_scale="YlGn", title="Carbon Sink Treemap / 碳汇树状图")
    apply_theme(fig, height=500)
    fig.update_traces(textinfo="label+value" if show_labels else "label", textfont_size=11)
    st.plotly_chart(fig, use_container_width=True)

with col_b:
    top20 = df.head(20)
    fig2 = go.Figure()
    fig2.add_trace(go.Bar(
        y=top20["keyword"], x=top20["carbon_sink"], orientation="h",
        marker=dict(color=top20["carbon_sink"], colorscale="YlGn", line=dict(width=0)),
        text=top20["carbon_sink"], textposition="auto", textfont_size=11,
    ))
    apply_theme(fig2, height=500, title_text="Top 20 Carbon Sink Keywords",
        xaxis_title="Carbon Sink Value", yaxis_title="", yaxis=dict(autorange="reversed"))
    st.plotly_chart(fig2, use_container_width=True)

st.markdown("### Contribution Chain / 贡献链")
sel = st.selectbox(t("select_keyword"), df["keyword"].tolist(), key="cs_kw")
if sel:
    row = df[df["keyword"] == sel].iloc[0]
    c1, c2 = st.columns(2)
    c1.metric("Carbon Sink", int(row["carbon_sink"]))
    matching = engine.papers_df[engine.papers_df["text"].str.contains(sel, case=False, na=False)]
    c2.metric("Papers / 论文数", len(matching))
    neighbors = engine.get_keyword_neighbors(sel)[:15]
    if neighbors:
        st.text("Contributes to / 贡献给:")
        for n, w in neighbors: st.text(f"  🌱 {n} (weight: {w})")

st.markdown("---")
if st.button(t("run_ai"), key="cs_ai_btn", type="primary"):
    top5 = df.head(5)[["keyword", "carbon_sink"]].to_dict("records")
    prompt = f"""分析学术关键词碳汇(知识贡献度):
Top5碳汇关键词: {top5}
总关键词数: {len(engine.keywords_df)}, 有碳汇的: {len(df)}
请用中英双语分析: 1)最大碳汇(知识贡献源) 2)碳汇分布健康度 3)低碳汇关键词策略 4)碳汇与生态稳定性"""
    st.session_state["ai_result_cs"] = ai_analyze(prompt)
render_ai_panel("cs")
render_export_panel("carbon_sink", data=df.to_dict("records"), df=df)
