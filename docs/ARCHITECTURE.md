# Architecture / 架构

AEB is a Streamlit multi-page application.

AEB 是一个 Streamlit 多页面应用。

```text
app.py
  ├── sidebar upload and model configuration
  ├── parse_multiple_files()
  ├── AEBDataEngine.ingest()
  ├── AEBDataEngine.compute_all()
  └── 13 Streamlit pages under pages/
```

Core modules:

- `utils/file_parser.py` — multi-format text extraction;
- `utils/data_engine.py` — TF-IDF, co-occurrence, NetworkX graph, PageRank, centrality, Louvain, ecological metrics;
- `utils/threejs_components.py` — 3D visualizations through Streamlit components and Three.js;
- `utils/chart_theme.py` — Plotly theme and palettes;
- `utils/aeb_model.py` — optional GGUF / Ollama / OpenAI-compatible AI backends;
- `utils/export_utils.py` — JSON, CSV, TXT, ZIP exports;
- `utils/i18n.py` — Chinese/English UI strings.
