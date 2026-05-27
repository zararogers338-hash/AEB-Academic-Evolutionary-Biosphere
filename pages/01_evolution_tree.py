# -*- coding: utf-8 -*-
"""AEB Page: 进化树 / Evolution Tree"""
import streamlit as st
from utils.i18n import init_lang, t
from utils.data_engine import get_engine
from utils.threejs_components import render_evolution_tree
from utils.aeb_model import render_ai_panel, ai_analyze
from utils.export_utils import render_export_panel

init_lang()
st.set_page_config(page_title=f"AEB - {t('evolution_tree')}", layout="wide")
st.title(f"🌳 {t('evolution_tree')}")

engine = get_engine()
if not engine.is_computed or engine.keywords_df.empty:
    st.info(t("no_data")); st.stop()

col1, col2 = st.columns([1, 3])
with col1:
    max_depth = st.slider("Tree Depth / 树深度", 2, 8, 5, key="tree_depth")
    min_score = st.slider("Min Score", 0.0, 0.1, 0.001, 0.001, key="tree_min_score")

with col2:
    tree_data = engine.evolution_tree
    if tree_data and tree_data.get("children"):
        show_labels = st.session_state.get("show_node_labels", False)
        render_evolution_tree(tree_data, width=800, height=550, show_labels=show_labels)
    else:
        st.warning("Evolution tree is empty / 进化树为空")

if not engine.papers_df.empty:
    years = sorted(engine.papers_df["year"].unique())
    if len(years) >= 2:
        year_range = st.slider(t("time_range"), int(min(years)), int(max(years)),
            (int(min(years)), int(max(years))), key="tree_year_range")

st.markdown("---")
st.subheader("Keyword Detail / 关键词详情")
kw_list = engine.keywords_df["keyword"].tolist()
selected_kw = st.selectbox(t("select_keyword"), kw_list, key="tree_kw_sel")
if selected_kw:
    row = engine.keywords_df[engine.keywords_df["keyword"] == selected_kw].iloc[0]
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("TF-IDF", f"{row['tfidf_mean']:.4f}")
    c2.metric("Centrality", f"{row['centrality']:.4f}")
    c3.metric("PageRank", f"{row['pagerank']:.4f}")
    c4.metric("Eco Role", row["eco_role"])
    neighbors = engine.get_keyword_neighbors(selected_kw)[:15]
    if neighbors:
        st.text("Co-occurring / 共现关键词:")
        for n, w in neighbors: st.text(f"  → {n} (weight: {w})")

st.markdown("---")
if st.button(t("run_ai"), key="tree_ai_btn", type="primary"):
    prompt = f"""分析关键词进化树。根: {engine.evolution_tree.get('name','?')}, 子节点: {len(engine.evolution_tree.get('children',[]))}。
请用中英双语: 1)进化路径 2)分支模式 3)即将灭绝的分支"""
    st.session_state["ai_result_tree"] = ai_analyze(prompt)
render_ai_panel("tree")
render_export_panel("evolution_tree", data=engine.evolution_tree, df=engine.keywords_df)
