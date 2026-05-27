# -*- coding: utf-8 -*-
"""AEB Page: 生态位层级 / Niche Hierarchy"""
import streamlit as st
from utils.i18n import init_lang, t
from utils.data_engine import get_engine
from utils.threejs_components import render_niche_hierarchy
from utils.aeb_model import render_ai_panel, ai_analyze
from utils.export_utils import render_export_panel

init_lang()
st.set_page_config(page_title=f"AEB - {t('niche_hierarchy')}", layout="wide")
st.title(f"🏗️ {t('niche_hierarchy')}")

engine = get_engine()
if not engine.is_computed or engine.keywords_df.empty:
    st.info(t("no_data")); st.stop()

df = engine.keywords_df.copy()
if "niche_level" not in df.columns: st.warning("No niche level data"); st.stop()

LEVEL_NAMES = {
    1: {"zh": "L1 基础理论层", "en": "L1 Foundation Theory"},
    2: {"zh": "L2 方法论层", "en": "L2 Methodology"},
    3: {"zh": "L3 技术实现层", "en": "L3 Technical Implementation"},
    4: {"zh": "L4 应用集成层", "en": "L4 Application Integration"},
    5: {"zh": "L5 领域应用层", "en": "L5 Domain Application"},
}
lang = st.session_state.get("lang", "zh")

levels = []
for lvl in sorted(df["niche_level"].unique()):
    lvl_df = df[df["niche_level"] == lvl].sort_values("score", ascending=False)
    levels.append({"level": int(lvl), "keywords": lvl_df.head(15)["keyword"].tolist()})

show_labels = st.session_state.get("show_node_labels", False)
render_niche_hierarchy(levels, width=850, height=520, show_labels=show_labels)

st.markdown("---")
for lvl_data in levels:
    lvl = lvl_data["level"]
    name = LEVEL_NAMES.get(lvl, {}).get(lang, f"Level {lvl}")
    lvl_df = df[df["niche_level"] == lvl].sort_values("score", ascending=False)
    with st.expander(f"{name} ({len(lvl_df)} keywords)", expanded=(lvl <= 2)):
        st.dataframe(lvl_df[["keyword", "tfidf_mean", "centrality", "eco_role", "carbon_sink"]].head(25),
            use_container_width=True, hide_index=True)

st.markdown("---")
if st.button(t("run_ai"), key="nh_ai_btn", type="primary"):
    level_summary = {f"L{l['level']}": l["keywords"][:5] for l in levels}
    prompt = f"""分析生态位层级: {level_summary}
请用中英双语: 1)各层级代表什么 2)依赖关系 3)层级失衡? 4)建议"""
    st.session_state["ai_result_nh"] = ai_analyze(prompt)
render_ai_panel("nh")
render_export_panel("niche_hierarchy", data={"levels": levels}, df=df)
