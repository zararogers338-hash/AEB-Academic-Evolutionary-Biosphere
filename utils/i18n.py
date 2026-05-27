# -*- coding: utf-8 -*-
"""AEB 国际化模块 / Internationalization Module"""

import streamlit as st

TEXTS = {
    "app_title": {"zh": "学术演化生物圈 AEB", "en": "Academic Evolutionary Biosphere"},
    "sidebar_title": {"zh": "AEB 控制面板", "en": "AEB Control Panel"},
    "lang_switch": {"zh": "🌐 Switch to English", "en": "🌐 切换到中文"},
    "upload_title": {"zh": "📄 上传学术文献", "en": "📄 Upload Academic Papers"},
    "upload_help": {"zh": "支持 txt/pdf/md/docx/json/csv/xlsx/html/xml/yaml 等格式", "en": "Supports txt/pdf/md/docx/json/csv/xlsx/html/xml/yaml"},
    "model_panel": {"zh": "模型状态面板", "en": "Model Status Panel"},
    "model_backend": {"zh": "当前后端", "en": "Current Backend"},
    "model_name": {"zh": "模型名称", "en": "Model Name"},
    "model_status": {"zh": "加载状态", "en": "Load Status"},
    "model_latency": {"zh": "延迟", "en": "Latency"},
    "health_check": {"zh": "健康检查", "en": "Health Check"},
    "degraded_warning": {"zh": "⚠️ 降级模式 - 推理精度受限", "en": "⚠️ Degraded Mode - Limited precision"},
    "start_loading": {"zh": "开始加载", "en": "Start Loading"},
    "loading": {"zh": "加载中...", "en": "Loading..."},
    "done": {"zh": "完成", "en": "Done"},
    "export_png": {"zh": "导出PNG", "en": "Export PNG"},
    "export_svg": {"zh": "导出SVG", "en": "Export SVG"},
    "export_json": {"zh": "导出JSON", "en": "Export JSON"},
    "export_txt": {"zh": "导出TXT", "en": "Export TXT"},
    "export_zip": {"zh": "导出ZIP", "en": "Export ZIP"},
    "ai_analysis": {"zh": "AI 分析结果", "en": "AI Analysis Results"},
    "eco_overview": {"zh": "学术生态总览", "en": "Academic Ecology Overview"},
    "total_papers": {"zh": "论文总数", "en": "Total Papers"},
    "total_keywords": {"zh": "关键词总数", "en": "Total Keywords"},
    "top_predators": {"zh": "顶级捕食者", "en": "Top Predators"},
    "dominant_species": {"zh": "优势种", "en": "Dominant Species"},
    "extinct_species": {"zh": "灭绝种", "en": "Extinct Species"},
    "shannon_index": {"zh": "Shannon多样性指数", "en": "Shannon Diversity Index"},
    "monopoly_ratio": {"zh": "垄断占比", "en": "Monopoly Ratio"},
    "eco_collapse_warning": {"zh": "⚠️ 生态崩溃风险：{kw}关键词过度垄断", "en": "⚠️ Ecosystem Collapse Risk: {kw} keyword over-monopoly"},
    "sedimentation_warning": {"zh": "⚠️ 知识爆炸导致混乱 - 沉积速率过高", "en": "⚠️ Knowledge Explosion Causing Chaos - Sedimentation rate too high"},
    "evolution_tree": {"zh": "进化树", "en": "Evolution Tree"},
    "neuron_graph": {"zh": "神经元图", "en": "Neuron Graph"},
    "fossil_layers": {"zh": "地质化石层", "en": "Fossil Layers"},
    "extinction_sim": {"zh": "灭绝事件模拟", "en": "Extinction Simulation"},
    "fitness_curve": {"zh": "适应度曲线", "en": "Fitness Curve"},
    "migration_path": {"zh": "迁徙路径", "en": "Migration Path"},
    "origin_trace": {"zh": "物种起源追溯", "en": "Origin Trace"},
    "carbon_sink": {"zh": "碳汇计算", "en": "Carbon Sink"},
    "niche_cluster": {"zh": "生态位聚类", "en": "Niche Cluster"},
    "sedimentation": {"zh": "沉积速率监控", "en": "Sedimentation Monitor"},
    "fossil_report": {"zh": "化石挖掘报告", "en": "Fossil Report"},
    "niche_hierarchy": {"zh": "生态位层级", "en": "Niche Hierarchy"},
    "collection": {"zh": "物种库收藏夹", "en": "Species Collection"},
    "no_data": {"zh": "暂无数据，请先上传文献并加载", "en": "No data yet. Please upload papers and start loading."},
    "parsing_file": {"zh": "正在解析文件: {f}", "en": "Parsing file: {f}"},
    "parse_success": {"zh": "解析成功: {f}", "en": "Parse success: {f}"},
    "parse_fail": {"zh": "解析失败: {f} - {e}", "en": "Parse failed: {f} - {e}"},
    "analyzing": {"zh": "AI正在分析生态系统...", "en": "AI analyzing ecosystem..."},
    "fossil_summary": {"zh": "该词在{peak}年巅峰，后被{replaced}取代", "en": "This keyword peaked in {peak}, later replaced by {replaced}"},
    "layer_summary": {"zh": "这一层代表{era}时代主流，已被{new_era}取代", "en": "This layer represents {era} era mainstream, replaced by {new_era}"},
    "select_keyword": {"zh": "选择关键词", "en": "Select Keyword"},
    "time_range": {"zh": "时间范围", "en": "Time Range"},
    "year_slider": {"zh": "年份", "en": "Year"},
    "niche_level": {"zh": "生态位层级", "en": "Niche Level"},
    "collection_name": {"zh": "收藏集名称", "en": "Collection Name"},
    "add_to_collection": {"zh": "添加到收藏", "en": "Add to Collection"},
    "compare_collections": {"zh": "对比收藏集", "en": "Compare Collections"},
    "overlap_degree": {"zh": "重叠度", "en": "Overlap Degree"},
    "diversity_score": {"zh": "多样性评分", "en": "Diversity Score"},
    "stability_score": {"zh": "稳定性评分", "en": "Stability Score"},
    "run_ai": {"zh": "🧬 AI 分析", "en": "🧬 AI Analyze"},
    "render_3d": {"zh": "🎨 渲染3D视图", "en": "🎨 Render 3D View"},
}


def t(key: str, **kwargs) -> str:
    lang = st.session_state.get("lang", "zh")
    entry = TEXTS.get(key, {})
    text = entry.get(lang, entry.get("zh", key))
    if kwargs:
        try:
            text = text.format(**kwargs)
        except (KeyError, IndexError):
            pass
    return text


def init_lang():
    if "lang" not in st.session_state:
        st.session_state.lang = "zh"


def toggle_lang():
    st.session_state.lang = "en" if st.session_state.lang == "zh" else "zh"
