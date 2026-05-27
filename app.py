# -*- coding: utf-8 -*-
"""AEB - 学术演化生物圈 / Academic Evolutionary Biosphere
主页面: 学术生态总览 / Academic Ecology Overview
"""

import streamlit as st
import yaml
import json
import os

st.set_page_config(
    page_title="AEB - Academic Evolutionary Biosphere",
    page_icon="🌍",
    layout="wide",
    initial_sidebar_state="expanded",
)

@st.cache_data
def load_config():
    cfg_path = os.path.join(os.path.dirname(__file__), "config.yaml")
    try:
        with open(cfg_path, "r", encoding="utf-8") as f:
            return yaml.safe_load(f)
    except Exception:
        return {"app": {}, "model": {}, "ecology": {}, "export": {}}

CONFIG = load_config()

from utils.i18n import init_lang, toggle_lang, t
from utils.aeb_model import get_model_manager, render_model_panel, render_ai_panel, ai_analyze
from utils.file_parser import parse_multiple_files
from utils.data_engine import get_engine
from utils.export_utils import render_export_panel

init_lang()

# --- Custom CSS ---
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600;700&display=swap');
[data-testid="stSidebar"] { background: linear-gradient(180deg, #060d1f 0%, #0a1628 100%); }
.eco-metric-card {
    background: linear-gradient(135deg, rgba(6,13,31,0.95), rgba(10,22,40,0.95));
    border: 1px solid rgba(0,255,170,0.25);
    border-radius: 12px;
    padding: 20px 16px;
    text-align: center;
    color: #00ffaa;
    transition: all 0.3s;
    backdrop-filter: blur(8px);
}
.eco-metric-card:hover { border-color: rgba(0,255,170,0.6); transform: translateY(-2px); box-shadow: 0 8px 25px rgba(0,255,136,0.12); }
.eco-metric-card h3 { margin: 0 0 8px 0; font-size: 12px; opacity: 0.6; letter-spacing: 1px; text-transform: uppercase; }
.eco-metric-card .value { font-size: 32px; font-weight: 700; background: linear-gradient(135deg, #00ffaa, #00ddff); -webkit-background-clip: text; -webkit-text-fill-color: transparent; }
.degraded-banner {
    background: linear-gradient(90deg, #ff3355, #cc2244);
    color: white; text-align: center; padding: 10px; font-weight: 600; font-size: 14px;
    border-radius: 8px; margin-bottom: 12px;
}
.eco-warning { color: #ff4466; font-weight: 600; animation: pulse 2s infinite; }
@keyframes pulse { 0%,100%{opacity:1;} 50%{opacity:0.5;} }
.stTabs [data-baseweb="tab-list"] { gap: 8px; }
.stTabs [data-baseweb="tab"] { border-radius: 8px 8px 0 0; }
</style>
""", unsafe_allow_html=True)

# --- Sidebar ---
with st.sidebar:
    st.title(t("sidebar_title"))
    if st.button(t("lang_switch"), key="lang_btn", use_container_width=True):
        toggle_lang()
        st.rerun()

    st.markdown("---")
    st.subheader(t("upload_title"))
    uploaded_files = st.file_uploader(
        t("upload_help"),
        type=["txt", "pdf", "md", "markdown", "doc", "docx", "json", "jsonl",
              "csv", "tsv", "xlsx", "xls", "html", "htm", "xml", "yaml", "yml"],
        accept_multiple_files=True, key="file_upload",
    )

    if uploaded_files:
        if st.button(t("start_loading"), key="parse_btn", use_container_width=True, type="primary"):
            engine = get_engine()
            progress_bar = st.progress(0)
            log_area = st.empty()

            def parse_progress(pct, fname):
                progress_bar.progress(pct)
                log_area.text(t("parsing_file", f=fname))

            results = parse_multiple_files(uploaded_files, parse_progress)
            engine.ingest(results)

            success = sum(1 for r in results if r["success"])
            st.success(f"✅ {success}/{len(results)} files parsed")

            st.markdown("---")
            compute_bar = st.progress(0)
            compute_log = st.empty()

            def compute_progress(pct, msg):
                compute_bar.progress(pct)
                compute_log.text(msg)

            engine.compute_all(CONFIG, compute_progress)
            compute_bar.progress(1.0)
            compute_log.text(t("done"))
            st.success("✅ " + t("done"))

    # Display Settings
    st.markdown("---")
    st.subheader("🏷️ 显示设置 / Display Settings")
    st.session_state["show_node_labels"] = st.toggle(
        "实时显示节点名称 / Show Node Labels",
        value=st.session_state.get("show_node_labels", False),
        key="toggle_node_labels",
        help="开启后所有图表将显示全部节点名称；关闭后仅鼠标悬浮显示 / When ON, all node names are visible; when OFF, names appear only on hover"
    )

    # Ecological Balance
    engine = get_engine()
    if engine.is_computed and not engine.keywords_df.empty:
        st.markdown("---")
        st.subheader(t("shannon_index"))
        si = engine.shannon_index
        mr = engine.monopoly_ratio
        st.metric(t("shannon_index"), f"{si:.3f}")
        st.metric(t("monopoly_ratio"), f"{mr:.1%}")
        threshold = CONFIG.get("ecology", {}).get("shannon_warning_threshold", 1.5)
        if 0 < si < threshold:
            top_kw = engine.keywords_df.iloc[0]["keyword"] if not engine.keywords_df.empty else "?"
            st.markdown(f'<div class="eco-warning">{t("eco_collapse_warning", kw=top_kw)}</div>', unsafe_allow_html=True)

    # Model panel
    render_model_panel(CONFIG.get("model", {}))


# --- Main Content ---
mgr = get_model_manager()
if mgr.is_degraded and mgr.backend is not None:
    st.markdown(f'<div class="degraded-banner">{t("degraded_warning")}</div>', unsafe_allow_html=True)

st.title(t("eco_overview"))

engine = get_engine()

if not engine.is_computed or engine.keywords_df.empty:
    st.info(t("no_data"))
    st.markdown("""
    ### 🚀 Quick Start / 快速开始

    1. **上传文献** / Upload papers → 侧边栏文件上传区
    2. **点击加载** / Click Start Loading → 解析文件并计算生态指标
    3. **配置AI** / Configure AI → 侧边栏底部选择 GGUF/Ollama/OpenAI
    4. **浏览页面** / Explore pages → 左侧导航栏进入各功能页面

    支持格式 / Supported: `txt, pdf, md, docx, json, csv, xlsx, html, xml, yaml`
    """)
else:
    # --- Overview Metrics ---
    c1, c2, c3, c4, c5 = st.columns(5)
    metrics = [
        (c1, t("total_papers"), len(engine.papers_df)),
        (c2, t("total_keywords"), len(engine.keywords_df)),
        (c3, t("top_predators"), len(engine.get_keywords_by_role("top_predator"))),
        (c4, t("dominant_species"), len(engine.get_keywords_by_role("dominant"))),
        (c5, t("extinct_species"), len(engine.extinct_keywords)),
    ]
    for col, label, value in metrics:
        with col:
            st.markdown(f"""<div class="eco-metric-card">
                <h3>{label}</h3><div class="value">{value}</div>
            </div>""", unsafe_allow_html=True)

    st.markdown("---")

    # --- Tabs for overview ---
    tab1, tab2, tab3 = st.tabs([f"🦁 {t('top_predators')}", f"🌲 {t('dominant_species')}", f"🏘️ {t('niche_cluster')}"])

    with tab1:
        tp_df = engine.get_keywords_by_role("top_predator")
        if not tp_df.empty:
            st.dataframe(
                tp_df[["keyword", "tfidf_mean", "centrality", "pagerank", "carbon_sink", "niche_level"]].head(20),
                use_container_width=True, hide_index=True,
            )

    with tab2:
        dom_df = engine.get_keywords_by_role("dominant")
        if not dom_df.empty:
            st.dataframe(
                dom_df[["keyword", "tfidf_mean", "centrality", "community", "niche_level"]].head(30),
                use_container_width=True, hide_index=True,
            )

    with tab3:
        if engine.communities:
            from collections import Counter
            comm_counts = Counter(engine.communities.values())
            for cid, cnt in sorted(comm_counts.items(), key=lambda x: -x[1])[:10]:
                comm_kws = engine.get_community_keywords(cid)
                top3 = ", ".join(comm_kws.head(3)["keyword"].tolist())
                st.text(f"  Community {cid}: {cnt} keywords — {top3}...")

    # --- AI Analysis ---
    st.markdown("---")
    tp_df = engine.get_keywords_by_role("top_predator")
    if st.button(t("run_ai"), key="ai_overview_btn", type="primary"):
        prompt = f"""你是一个学术生态分析AI。请用中英双语分析以下学术关键词生态系统:
- 总论文数: {len(engine.papers_df)}
- 总关键词数: {len(engine.keywords_df)}
- Shannon多样性指数: {engine.shannon_index:.3f}
- 垄断占比: {engine.monopoly_ratio:.1%}
- 顶级捕食者: {', '.join(tp_df.head(5)['keyword'].tolist()) if not tp_df.empty else 'N/A'}
- 群落数: {len(set(engine.communities.values())) if engine.communities else 0}
请评估: 1)生态健康度 2)是否存在垄断风险 3)多样性评级 4)建议关注的关键词"""
        with st.spinner(t("analyzing")):
            result = ai_analyze(prompt)
            st.session_state["ai_result_overview"] = result

    render_ai_panel("overview")

    render_export_panel(
        "overview",
        data=engine.to_json(),
        text_content=st.session_state.get("ai_result_overview", ""),
        df=engine.keywords_df,
    )
