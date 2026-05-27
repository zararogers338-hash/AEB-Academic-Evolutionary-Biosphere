# -*- coding: utf-8 -*-
"""AEB Page: 迁徙路径 / Migration Path"""
import streamlit as st
import random
from utils.i18n import init_lang, t
from utils.data_engine import get_engine
from utils.threejs_components import render_migration_paths
from utils.aeb_model import render_ai_panel, ai_analyze
from utils.export_utils import render_export_panel

init_lang()
st.set_page_config(page_title=f"AEB - {t('migration_path')}", layout="wide")
st.title(f"🦅 {t('migration_path')}")

engine = get_engine()
if not engine.is_computed or engine.keywords_df.empty:
    st.info(t("no_data")); st.stop()

kw_list = engine.keywords_df["keyword"].tolist()
selected_kws = st.multiselect("Track Keywords / 追踪关键词", kw_list, default=kw_list[:3], key="mig_kws")
if not selected_kws: st.info("Select keywords to track"); st.stop()

paths = []
for kw in selected_kws:
    neighbors = engine.get_keyword_neighbors(kw)
    waypoints = [{"x": 0, "y": 0, "year": 2000, "field": "origin"}]
    for i, (n, w) in enumerate(neighbors[:8]):
        waypoints.append({"x": (i+1)*30+random.uniform(-10,10), "y": random.uniform(-50,50), "year": 2000+i*3, "field": n})
    paths.append({"keyword": kw, "waypoints": waypoints})

show_labels = st.session_state.get("show_node_labels", False)
render_migration_paths(paths, width=850, height=520, show_labels=show_labels)

st.markdown("---")
st.subheader("Migration Details / 迁徙详情")
for path in paths:
    with st.expander(f"🦅 {path['keyword']}", expanded=True):
        for wp in path["waypoints"]:
            st.text(f"  → Year {wp['year']}: {wp['field']}")

st.markdown("---")
if st.button(t("run_ai"), key="mig_ai_btn", type="primary"):
    prompt = f"""分析关键词迁徙: {', '.join(selected_kws)}
路径数据: {[{'kw': p['keyword'], 'stops': len(p['waypoints'])} for p in paths]}
请用中英双语: 1)迁徙模式 2)跨领域传播路径 3)迁徙速度 4)未来方向"""
    st.session_state["ai_result_mig"] = ai_analyze(prompt)
render_ai_panel("mig")
render_export_panel("migration", data={"paths": paths})
