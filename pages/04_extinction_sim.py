# -*- coding: utf-8 -*-
"""AEB Page: 灭绝事件模拟 / Extinction Event Simulation"""
import streamlit as st
import plotly.graph_objects as go
from utils.i18n import init_lang, t
from utils.data_engine import get_engine
from utils.aeb_model import render_ai_panel, ai_analyze
from utils.export_utils import render_export_panel
from utils.chart_theme import apply_theme, PALETTE_STATUS

init_lang()
st.set_page_config(page_title=f"AEB - {t('extinction_sim')}", layout="wide")
st.title(f"☄️ {t('extinction_sim')}")

engine = get_engine()
if not engine.is_computed or engine.keywords_df.empty:
    st.info(t("no_data")); st.stop()

st.subheader("Replacement Chain / 取代链")
st.markdown("""
- `RNN → LSTM → Attention → Transformer → LLM`
- `SVM → Random Forest → XGBoost → Deep Learning`
- `Bag-of-Words → Word2Vec → ELMo → BERT → GPT`
""")

years = sorted(engine.papers_df["year"].unique()) if not engine.papers_df.empty else [2000, 2025]
if len(years) < 2: years = [2000, 2025]
current_year = st.slider(t("year_slider"), int(min(years)), int(max(years)), int(max(years)), key="ext_year")

st.markdown("---")
st.subheader(f"Ecosystem at Year {current_year}")

df = engine.keywords_df.copy()
alive_kws, fading_kws, extinct_kws = [], [], []
for _, row in df.iterrows():
    fy = row.get("first_year", 2000)
    if fy > current_year: continue
    age = current_year - fy
    if age > 20: extinct_kws.append(row["keyword"])
    elif age > 10: fading_kws.append(row["keyword"])
    else: alive_kws.append(row["keyword"])

c1, c2, c3 = st.columns(3)
c1.metric("🟢 Alive / 存活", len(alive_kws))
c2.metric("🟡 Fading / 衰退", len(fading_kws))
c3.metric("🔴 Extinct / 灭绝", len(extinct_kws))

# Enhanced donut + bar chart
col_a, col_b = st.columns(2)
with col_a:
    fig_donut = go.Figure(go.Pie(
        labels=["Alive", "Fading", "Extinct"],
        values=[len(alive_kws), len(fading_kws), len(extinct_kws)],
        hole=0.55, marker_colors=[PALETTE_STATUS["alive"], PALETTE_STATUS["fading"], PALETTE_STATUS["extinct"]],
        textinfo="label+percent", textfont_size=12,
    ))
    apply_theme(fig_donut, height=380, title_text=f"Species Distribution at {current_year}")
    fig_donut.update_layout(showlegend=False,
        annotations=[dict(text=f"<b>{current_year}</b>", x=0.5, y=0.5, font_size=20, font_color="#00ffaa", showarrow=False)])
    st.plotly_chart(fig_donut, use_container_width=True)

with col_b:
    fig_bar = go.Figure()
    categories = ["Alive", "Fading", "Extinct"]
    values = [len(alive_kws), len(fading_kws), len(extinct_kws)]
    colors = [PALETTE_STATUS["alive"], PALETTE_STATUS["fading"], PALETTE_STATUS["extinct"]]
    fig_bar.add_trace(go.Bar(x=categories, y=values, marker_color=colors, text=values,
        textposition="auto", textfont_size=14, marker_line_color="rgba(255,255,255,0.1)", marker_line_width=1))
    apply_theme(fig_bar, height=380, title_text="Species Count by Status")
    st.plotly_chart(fig_bar, use_container_width=True)

with st.expander(f"🟢 Alive ({len(alive_kws)})", expanded=False):
    for kw in alive_kws[:30]: st.text(f"  ● {kw}")
with st.expander(f"🟡 Fading ({len(fading_kws)})", expanded=False):
    for kw in fading_kws[:30]: st.text(f"  ◐ {kw}")
with st.expander(f"🔴 Extinct ({len(extinct_kws)})", expanded=False):
    for kw in extinct_kws[:30]: st.text(f"  ✗ {kw}")

st.markdown("---")
if st.button(t("run_ai"), key="ext_ai_btn", type="primary"):
    prompt = f"""分析{current_year}年的关键词灭绝事件。
存活: {len(alive_kws)}, 衰退: {len(fading_kws)}, 灭绝: {len(extinct_kws)}。
灭绝样本: {', '.join(extinct_kws[:10])}
衰退样本: {', '.join(fading_kws[:10])}
请用中英双语分析: 1)灭绝原因 2)取代链 3)哪些可能复兴 4)生态系统韧性"""
    st.session_state["ai_result_ext"] = ai_analyze(prompt)
render_ai_panel("ext")
render_export_panel("extinction", data={"year": current_year, "alive": len(alive_kws), "fading": len(fading_kws), "extinct": len(extinct_kws)})
