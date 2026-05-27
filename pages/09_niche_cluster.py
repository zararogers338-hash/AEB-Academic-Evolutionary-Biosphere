# -*- coding: utf-8 -*-
"""AEB Page: 生态位聚类 / Niche Cluster"""
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
from utils.i18n import init_lang, t
from utils.data_engine import get_engine
from utils.aeb_model import render_ai_panel, ai_analyze
from utils.export_utils import render_export_panel
from utils.chart_theme import apply_theme, PALETTE_NEON

init_lang()
st.set_page_config(page_title=f"AEB - {t('niche_cluster')}", layout="wide")
st.title(f"🏘️ {t('niche_cluster')}")

engine = get_engine()
if not engine.is_computed or engine.keywords_df.empty:
    st.info(t("no_data")); st.stop()

df = engine.keywords_df.copy()
if "community" not in df.columns: st.warning("No community data"); st.stop()

from collections import Counter
comm_counts = Counter(df["community"].tolist())
n_comm = len(comm_counts)

c1, c2, c3 = st.columns(3)
c1.metric("Total Communities / 总群落数", n_comm)
c2.metric("Largest Community", max(comm_counts.values()) if comm_counts else 0)
c3.metric("Shannon Index", f"{engine.shannon_index:.3f}")

# Enhanced scatter with size encoding
plot_df = df.head(100).copy()
plot_df["community_str"] = plot_df["community"].astype(str)
show_labels = st.session_state.get("show_node_labels", False)
fig = px.scatter(
    plot_df, x="tfidf_mean", y="centrality", color="community_str",
    size="carbon_sink", hover_name="keyword", size_max=25,
    text="keyword" if show_labels else None,
    color_discrete_sequence=PALETTE_NEON,
    title="Niche Clusters (TF-IDF vs Centrality)",
)
if show_labels:
    fig.update_traces(textposition="top center", textfont=dict(size=9, color="rgba(0,255,170,0.8)"))
apply_theme(fig, height=520, xaxis_title="TF-IDF Mean", yaxis_title="Centrality")
fig.update_traces(marker=dict(line=dict(width=1, color="rgba(255,255,255,0.15)")))
st.plotly_chart(fig, use_container_width=True)

# Pie chart for community sizes
fig_pie = go.Figure(go.Pie(
    labels=[f"C{k}" for k in sorted(comm_counts.keys())[:12]],
    values=[comm_counts[k] for k in sorted(comm_counts.keys())[:12]],
    hole=0.45, marker_colors=PALETTE_NEON,
    textinfo="label+percent", textfont_size=11,
))
apply_theme(fig_pie, height=380, title_text="Community Size Distribution")
st.plotly_chart(fig_pie, use_container_width=True)

st.markdown("### Community Detail / 群落详情")
for cid in sorted(comm_counts.keys()):
    comm_df = engine.get_community_keywords(cid)
    top_kws = ", ".join(comm_df.head(5)["keyword"].tolist())
    with st.expander(f"Community {cid} ({len(comm_df)} keywords) — {top_kws}", expanded=False):
        st.dataframe(comm_df[["keyword", "tfidf_mean", "centrality", "eco_role", "carbon_sink"]].head(20),
            use_container_width=True, hide_index=True)

st.markdown("---")
if st.button(t("run_ai"), key="nc_ai_btn", type="primary"):
    comm_summary = {str(cid): {"count": cnt, "top": engine.get_community_keywords(cid).head(3)["keyword"].tolist()}
                    for cid, cnt in list(comm_counts.items())[:10]}
    prompt = f"""分析学术关键词生态位聚类: 群落数: {n_comm}, 群落摘要: {comm_summary}
请用中英双语分析: 1)各群落的学术主题 2)竞争/共生关系 3)扩张/萎缩趋势 4)生态位稳定性"""
    st.session_state["ai_result_nc"] = ai_analyze(prompt)
render_ai_panel("nc")
render_export_panel("niche_cluster", data={"n_communities": n_comm, "communities": dict(comm_counts)}, df=df)
