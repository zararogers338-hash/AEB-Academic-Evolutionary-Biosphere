# -*- coding: utf-8 -*-
"""AEB Page: 地质化石层 / Geological Fossil Layers"""
import streamlit as st
from utils.i18n import init_lang, t
from utils.data_engine import get_engine
from utils.threejs_components import render_fossil_layers
from utils.aeb_model import render_ai_panel, ai_analyze
from utils.export_utils import render_export_panel

init_lang()
st.set_page_config(page_title=f"AEB - {t('fossil_layers')}", layout="wide")
st.title(f"🪨 {t('fossil_layers')}")

engine = get_engine()
if not engine.is_computed or engine.keywords_df.empty:
    st.info(t("no_data")); st.stop()

LAYER_RANGES = [
    ("2020-2026", "#8B7355", 0), ("2015-2019", "#7B6348", 1),
    ("2010-2014", "#6B533B", 2), ("2005-2009", "#5B432E", 3),
    ("2000-2004", "#4B3321", 4), ("1990-1999", "#3B2314", 5),
    ("1950-1989", "#2B1307", 6),
]

def year_in_range(year, range_str):
    parts = range_str.split("-")
    return int(parts[0]) <= year <= int(parts[1])

layers = []
for yr_range, color, depth in LAYER_RANGES:
    kws = [row["keyword"] for _, row in engine.keywords_df.iterrows()
           if year_in_range(row.get("first_year", 2020), yr_range)]
    layers.append({"year_range": yr_range, "keywords": kws[:20], "color": color, "depth": depth})

active_layer = st.slider("Active Layer / 活跃地层", 0, len(layers) - 1, 0, key="fossil_layer_idx")
st.info(f"**{layers[active_layer]['year_range']}** — {len(layers[active_layer]['keywords'])} keywords")

if layers[active_layer]["keywords"]:
    st.text("Fossils in this layer:")
    for kw in layers[active_layer]["keywords"]:
        st.text(f"  🦴 {kw}")

show_labels = st.session_state.get("show_node_labels", False)
render_fossil_layers(layers[:active_layer + 1], width=850, height=550, show_labels=show_labels)

st.markdown("---")
if st.button(t("run_ai"), key="fossil_ai_btn", type="primary"):
    layer = layers[active_layer]
    prompt = f"""分析地质层 {layer['year_range']}:
关键词化石: {', '.join(layer['keywords'][:15])}
请用中英双语: 1)学术主流 2)是否已被取代 3)取代链 4)\"活化石\"(至今活跃的旧词)"""
    st.session_state["ai_result_fossil"] = ai_analyze(prompt)
render_ai_panel("fossil")
render_export_panel("fossil_layers", data={"layers": layers}, df=engine.keywords_df)
