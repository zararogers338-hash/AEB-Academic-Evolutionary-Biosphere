# -*- coding: utf-8 -*-
"""AEB Page: 物种库收藏夹 / Species Collection"""
import streamlit as st
import json
from utils.i18n import init_lang, t
from utils.data_engine import get_engine, compute_shannon_index
from utils.aeb_model import render_ai_panel, ai_analyze
from utils.export_utils import render_export_panel
import pandas as pd

init_lang()
st.set_page_config(page_title=f"AEB - {t('collection')}", layout="wide")
st.title(f"📚 {t('collection')}")

engine = get_engine()
if not engine.is_computed or engine.keywords_df.empty:
    st.info(t("no_data")); st.stop()

if "collections" not in st.session_state:
    st.session_state.collections = {}

st.subheader(t("add_to_collection"))
col1, col2 = st.columns(2)
with col1:
    coll_name = st.text_input(t("collection_name"), key="coll_name_input")
with col2:
    selected_kws = st.multiselect(t("select_keyword"), engine.keywords_df["keyword"].tolist(), key="coll_kw_select")

if st.button(t("add_to_collection"), key="coll_add_btn", type="primary"):
    if coll_name and selected_kws:
        if coll_name not in st.session_state.collections:
            st.session_state.collections[coll_name] = []
        for kw in selected_kws:
            if kw not in st.session_state.collections[coll_name]:
                st.session_state.collections[coll_name].append(kw)
        st.success(f"Added {len(selected_kws)} keywords to '{coll_name}'")
    else:
        st.warning("请输入名称并选择关键词 / Enter name and select keywords")

st.markdown("---")
collections = st.session_state.collections
if not collections:
    st.info("暂无收藏集 / No collections yet")
else:
    for name, kws in collections.items():
        with st.expander(f"📁 {name} ({len(kws)} keywords)", expanded=True):
            if kws:
                coll_df = engine.keywords_df[engine.keywords_df["keyword"].isin(kws)]
                if not coll_df.empty:
                    st.dataframe(coll_df[["keyword", "tfidf_mean", "centrality", "eco_role", "carbon_sink", "niche_level"]],
                        use_container_width=True, hide_index=True)
                    c1, c2, c3 = st.columns(3)
                    c1.metric(t("diversity_score"), f"{compute_shannon_index(coll_df):.3f}")
                    c2.metric("Avg Score", f"{coll_df['score'].mean():.4f}" if "score" in coll_df.columns else "N/A")
                    c3.metric("Roles", str(coll_df["eco_role"].value_counts().to_dict()))
            if st.button(f"🗑️ Delete '{name}'", key=f"del_{name}"):
                del st.session_state.collections[name]; st.rerun()

    st.markdown("---")
    st.subheader(t("compare_collections"))
    coll_names = list(collections.keys())
    if len(coll_names) >= 2:
        sel_colls = st.multiselect("Select collections", coll_names, default=coll_names[:2], key="coll_compare_sel")
        if len(sel_colls) >= 2:
            comparison = {}
            for n in sel_colls:
                kws = set(collections[n])
                coll_df = engine.keywords_df[engine.keywords_df["keyword"].isin(kws)]
                comparison[n] = {"keywords": len(kws),
                    "shannon": round(compute_shannon_index(coll_df), 3),
                    "avg_score": round(float(coll_df["score"].mean()), 4) if not coll_df.empty and "score" in coll_df.columns else 0,
                    "kw_set": kws}

            cols = st.columns(len(sel_colls))
            for i, n in enumerate(sel_colls):
                with cols[i]:
                    st.markdown(f"**{n}**")
                    st.text(f"Keywords: {comparison[n]['keywords']}")
                    st.text(f"Shannon: {comparison[n]['shannon']}")
                    st.text(f"Avg Score: {comparison[n]['avg_score']}")

            st.markdown("#### Overlap / 重叠度")
            for i in range(len(sel_colls)):
                for j in range(i+1, len(sel_colls)):
                    a, b = sel_colls[i], sel_colls[j]
                    overlap = comparison[a]["kw_set"] & comparison[b]["kw_set"]
                    union = comparison[a]["kw_set"] | comparison[b]["kw_set"]
                    jaccard = len(overlap)/len(union) if union else 0
                    st.text(f"  {a} ↔ {b}: {len(overlap)} shared, Jaccard={jaccard:.3f}")

st.markdown("---")
if st.button(t("run_ai"), key="coll_ai_btn", type="primary") and collections:
    coll_summary = {n: kws[:10] for n, kws in collections.items()}
    prompt = f"""分析收藏集: {coll_summary}
请用中英双语: 1)各收藏集方向 2)关联性 3)收藏策略建议 4)盲区"""
    st.session_state["ai_result_coll"] = ai_analyze(prompt)
render_ai_panel("coll")
if collections:
    render_export_panel("collection", data={"collections": {n: kws for n, kws in collections.items()}})
