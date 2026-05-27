# -*- coding: utf-8 -*-
"""AEB Page: 神经元图 / Neuron Graph"""
import streamlit as st
from utils.i18n import init_lang, t
from utils.data_engine import get_engine
from utils.threejs_components import render_force_graph
from utils.aeb_model import render_ai_panel, ai_analyze
from utils.export_utils import render_export_panel
from utils.chart_theme import ROLE_COLORS, COMMUNITY_COLORS

init_lang()
st.set_page_config(page_title=f"AEB - {t('neuron_graph')}", layout="wide")
st.title(f"🧠 {t('neuron_graph')}")

engine = get_engine()
if not engine.is_computed or engine.keywords_df.empty:
    st.info(t("no_data")); st.stop()

col1, col2, col3 = st.columns(3)
with col1: top_n = st.slider("Top N Keywords", 10, 200, 50, key="ng_topn")
with col2: min_edge = st.slider("Min Edge Weight", 1, 20, 2, key="ng_minedge")
with col3: color_by = st.selectbox("Color By", ["community", "eco_role", "niche_level"], key="ng_color")

df = engine.keywords_df.head(top_n)
nodes = []
for _, row in df.iterrows():
    if color_by == "eco_role":
        color = ROLE_COLORS.get(row["eco_role"], "#00ff88")
    elif color_by == "community":
        color = COMMUNITY_COLORS[int(row.get("community", 0)) % len(COMMUNITY_COLORS)]
    else:
        color = COMMUNITY_COLORS[int(row.get("niche_level", 1)) % len(COMMUNITY_COLORS)]
    nodes.append({"id": row["keyword"], "size": float(row["score"]), "color": color,
        "group": int(row.get("community", 0)), "label": row["keyword"]})

kw_set = set(df["keyword"])
edges = []
for i, r1 in df.iterrows():
    for j, r2 in df.iterrows():
        if r1["keyword"] < r2["keyword"]:
            try: w = int(engine.cooccurrence.at[r1["keyword"], r2["keyword"]])
            except: w = 0
            if w >= min_edge:
                edges.append({"source": r1["keyword"], "target": r2["keyword"], "weight": w})

show_labels = st.session_state.get("show_node_labels", False)
render_force_graph(nodes, edges, width=850, height=620, show_labels=show_labels)
st.caption(f"Nodes: {len(nodes)} | Edges: {len(edges)}")

st.markdown("---")
st.subheader("Node Detail / 节点详情")
sel = st.selectbox(t("select_keyword"), df["keyword"].tolist(), key="ng_kw_sel")
if sel:
    row = engine.keywords_df[engine.keywords_df["keyword"] == sel].iloc[0]
    c1, c2, c3, c4, c5 = st.columns(5)
    c1.metric("TF-IDF", f"{row['tfidf_mean']:.4f}")
    c2.metric("Centrality", f"{row['centrality']:.4f}")
    c3.metric("Community", int(row.get("community", -1)))
    c4.metric("Carbon Sink", int(row.get("carbon_sink", 0)))
    c5.metric("Role", row["eco_role"])

st.markdown("---")
if st.button(t("run_ai"), key="ng_ai_btn", type="primary"):
    prompt = f"""分析关键词网络。节点: {len(df)}, 社区: {len(set(engine.communities.values())) if engine.communities else 0}。
请用中英双语: 1)网络结构 2)核心枢纽 3)桥接关键词 4)网络健康度"""
    st.session_state["ai_result_ng"] = ai_analyze(prompt)
render_ai_panel("ng")
render_export_panel("neuron_graph", data={"nodes": len(df)}, df=df)
