# -*- coding: utf-8 -*-
"""AEB Page: 化石挖掘报告 / Fossil Excavation Report"""
import streamlit as st
import plotly.graph_objects as go
from utils.i18n import init_lang, t
from utils.data_engine import get_engine
from utils.aeb_model import render_ai_panel, ai_analyze
from utils.export_utils import render_export_panel
from utils.chart_theme import apply_theme

init_lang()
st.set_page_config(page_title=f"AEB - {t('fossil_report')}", layout="wide")
st.title(f"🦴 {t('fossil_report')}")

engine = get_engine()
if not engine.is_computed or engine.keywords_df.empty:
    st.info(t("no_data")); st.stop()

kw_list = engine.keywords_df["keyword"].tolist()
fossil_kw = st.selectbox("Select Fossil Keyword / 选择化石关键词", kw_list, key="fr_kw")
if not fossil_kw: st.stop()

st.markdown(f"### 🦴 Excavation Report for: **{fossil_kw}**")
row = engine.keywords_df[engine.keywords_df["keyword"] == fossil_kw].iloc[0]
neighbors = engine.get_keyword_neighbors(fossil_kw)
fitness = engine.get_fitness_data(fossil_kw)

c1, c2, c3, c4 = st.columns(4)
c1.metric("TF-IDF", f"{row['tfidf_mean']:.4f}")
c2.metric("Centrality", f"{row['centrality']:.4f}")
c3.metric("Carbon Sink", int(row.get("carbon_sink", 0)))
c4.metric("Eco Role", row["eco_role"])

if fitness:
    years = [f["year"] for f in fitness]
    counts = [f["count"] for f in fitness]
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=years, y=counts, mode="lines+markers",
        fill="tozeroy", line=dict(color="#00ffaa", width=2.5, shape="spline"),
        fillcolor="rgba(0,255,136,0.08)", marker=dict(size=7, color="#00ffaa")))
    if counts:
        peak_idx = counts.index(max(counts))
        fig.add_annotation(x=years[peak_idx], y=counts[peak_idx], text="⬆ Peak / 巅峰",
            showarrow=True, arrowhead=2, arrowcolor="#ff4466", font=dict(color="#ff4466"))
    apply_theme(fig, height=380, title_text=f"Fitness Timeline: {fossil_kw}")
    st.plotly_chart(fig, use_container_width=True)

col_a, col_b = st.columns(2)
with col_a:
    st.subheader("🦴 Coexisting Species / 共存物种")
    if neighbors:
        for n, w in neighbors[:15]:
            n_row = engine.keywords_df[engine.keywords_df["keyword"] == n]
            role = n_row.iloc[0]["eco_role"] if not n_row.empty else "?"
            st.text(f"  🦴 {n} (co: {w}, role: {role})")

with col_b:
    st.subheader("⚡ Replacement Chain / 取代链")
    replacements = []
    for n, w in neighbors:
        n_row = engine.keywords_df[engine.keywords_df["keyword"] == n]
        if not n_row.empty and n_row.iloc[0]["score"] > row["score"]:
            replacements.append((n, float(n_row.iloc[0]["score"])))
    replacements.sort(key=lambda x: -x[1])
    if replacements:
        chain = [fossil_kw] + [r[0] for r in replacements[:5]]
        st.markdown(" → ".join(f"**{c}**" for c in chain))
    else:
        st.text(f"{fossil_kw} (no clear replacement)")
    st.subheader("📄 Papers")
    matching = engine.papers_df[engine.papers_df["text"].str.contains(fossil_kw, case=False, na=False)]
    st.metric("Papers containing this keyword", len(matching))

st.markdown("---")
if st.button(t("run_ai"), key="fr_ai_btn", type="primary"):
    chain_str = " → ".join([fossil_kw] + [r[0] for r in replacements[:5]]) if replacements else fossil_kw
    prompt = f"""化石挖掘报告: {fossil_kw}
TF-IDF: {row['tfidf_mean']:.4f}, Centrality: {row['centrality']:.4f}
共存: {', '.join([n for n, w in neighbors[:10]])}
取代链: {chain_str}, 论文数: {len(matching)}
请用中英双语: 1)巅峰年代 2)被什么取代 3)衰落原因 4)复兴可能性"""
    st.session_state["ai_result_fr"] = ai_analyze(prompt)
render_ai_panel("fr")
render_export_panel("fossil_report", data={"keyword": fossil_kw, "neighbors": neighbors[:20]}, df=matching if not matching.empty else engine.keywords_df)
