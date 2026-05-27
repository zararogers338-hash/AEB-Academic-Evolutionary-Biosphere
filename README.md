# 🌍 AEB Academic Evolutionary Biosphere

**AEB Academic Evolutionary Biosphere** is an open-source Streamlit workbench that analyzes academic documents as an evolving biological ecosystem. It turns papers, notes, reports, and research text into keyword species, ecological roles, concept communities, evolutionary trees, fossil layers, extinction simulations, migration paths, niche hierarchies, and AI-assisted bilingual interpretations.

**AEB 学术演化生物圈** 是一个开源的 Streamlit 工作台，它把学术文档看作一个会演化、竞争、迁徙、衰退和形成生态位的“知识生物圈”。它可以把论文、笔记、报告和研究文本转化为关键词物种、生态角色、概念群落、进化树、化石层、灭绝模拟、迁徙路径、生态位层级，并通过 AI 生成中英双语解释。

![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)
![Python](https://img.shields.io/badge/Python-3.9%2B-blue.svg)
![UI](https://img.shields.io/badge/UI-Streamlit-red.svg)
![Visualization](https://img.shields.io/badge/Visualization-Plotly%20%7C%20Three.js-purple.svg)
![Status](https://img.shields.io/badge/Status-Open%20Source%20Preview-brightgreen.svg)

---

## What It Is / 它是什么

AEB is not a biology simulation system in the laboratory sense. It is an **academic ecology analysis platform**. It borrows language from evolutionary biology, ecology, paleontology, and complex systems to observe how ideas appear, grow, compete, cluster, migrate, dominate, or fade inside academic corpora.

AEB 不是现实意义上的生物学实验仿真器。它真正做的是一个 **学术生态分析平台**：借用演化生物学、生态学、古生物学和复杂系统的语言，观察思想如何在学术语料中出现、成长、竞争、聚集、迁徙、占据主导地位，或者逐渐衰退。

In plain language:

简单来说：

```text
Academic papers / 学术文献
        ↓
Text extraction / 文本提取
        ↓
TF-IDF keyword species / TF-IDF 关键词物种
        ↓
Co-occurrence network / 共现网络
        ↓
Ecological roles, communities, diversity, niches / 生态角色、群落、多样性、生态位
        ↓
3D + 2D visualizations and AI explanation / 3D + 2D 可视化与 AI 解释
```

---

## Core Metaphor / 核心隐喻

AEB treats an academic field as a biosphere:

AEB 把一个学术领域看成一个生物圈：

| Biology metaphor | Academic meaning | 中文解释 |
|---|---|---|
| Species | Keywords, concepts, methods, theories | 物种 = 关键词、概念、方法、理论 |
| Top predator | A highly dominant concept | 顶级捕食者 = 高度主导概念 |
| Dominant species | A strong mainstream concept | 优势物种 = 主流强势概念 |
| Symbiotic species | Supporting or coexisting concepts | 共生物种 = 支撑性或共现概念 |
| Fossil layer | Older knowledge strata by time | 化石层 = 按时间沉积的知识地层 |
| Extinction | Concept decline or replacement | 灭绝 = 概念衰退或被替代 |
| Migration | Cross-topic or cross-field spread | 迁徙 = 跨主题、跨领域传播 |
| Niche | Conceptual position in the research ecosystem | 生态位 = 概念在研究生态中的位置 |
| Carbon sink | Knowledge contribution and co-occurrence weight | 碳汇 = 知识贡献度与共现权重 |

---

## Main Features / 主要功能

AEB includes **13 functional pages**:

AEB 包含 **13 个功能页面**：

1. **Evolution Tree / 进化树** — 3D keyword evolution visualization.
2. **Neuron Graph / 神经元图** — force-directed keyword network.
3. **Geological Fossil Layers / 地质化石层** — knowledge strata by publication time.
4. **Extinction Event Simulation / 灭绝事件模拟** — observe keyword survival and decline.
5. **Fitness Curve / 适应度曲线** — track keyword lifecycle over time.
6. **Migration Path / 迁徙路径** — visualize concept movement across neighboring topics.
7. **Species Origin Trace / 物种起源追溯** — trace concept ancestry backward.
8. **Carbon Sink Calculation / 碳汇计算** — visualize knowledge contribution.
9. **Niche Cluster / 生态位聚类** — community detection and concept clustering.
10. **Sedimentation Monitor / 沉积速率监控** — detect publication accumulation speed.
11. **Fossil Mining Report / 化石挖掘报告** — analyze older or declining concepts.
12. **Niche Hierarchy / 生态位层级** — organize concepts from basic theories to applications.
13. **Species Collection / 物种库收藏夹** — bookmark and compare selected keywords.

---

## AI Backends / AI 后端

AEB can run without AI, but it also supports AI-assisted interpretation through optional backends:

AEB 不依赖 AI 也能运行；如果需要自然语言解释，可以选择以下 AI 后端：

| Backend | Use case | 中文说明 |
|---|---|---|
| GGUF / llama-cpp-python | Local model inference | 本地 GGUF 模型推理 |
| Ollama | Local model service | 本地 Ollama 模型服务 |
| OpenAI-compatible API | OpenAI, DeepSeek, Zhipu, local compatible servers | OpenAI、DeepSeek、智谱或本地兼容 API |

The default installation focuses on the core visualization system. Optional AI dependencies are listed in `requirements-ai.txt`.

默认安装优先保证核心可视化系统可运行。可选 AI 依赖写在 `requirements-ai.txt`。

---

## Installation / 安装

Recommended Python version: **Python 3.9–3.11**.

推荐 Python 版本：**Python 3.9–3.11**。

```bash
git clone https://github.com/zararogers338-hash/AEB-Academic-Evolutionary-Biosphere.git
cd AEB-Academic-Evolutionary-Biosphere
python -m venv .venv
```

Windows:

```bat
.venv\Scripts\activate
pip install -r requirements.txt
streamlit run app.py
```

Linux / macOS:

```bash
source .venv/bin/activate
pip install -r requirements.txt
streamlit run app.py
```

Optional AI backend dependencies:

可选 AI 后端依赖：

```bash
pip install -r requirements-ai.txt
```

Windows users can also run:

Windows 用户也可以运行：

```bat
run.bat
```

---

## Input Formats / 输入格式

Supported document formats include:

支持的文档格式包括：

```text
txt, pdf, md, markdown, doc, docx, json, jsonl,
csv, tsv, xlsx, xls, html, htm, xml, yaml, yml
```

---

## Output / 输出

AEB can export analysis data and AI reports as:

AEB 可以导出分析数据和 AI 报告：

```text
JSON, CSV, TXT, ZIP
```

---

## Project Structure / 项目结构

```text
.
├── app.py                  # Streamlit main entry
├── pages/                  # 13 functional pages
├── utils/                  # engine, parsers, visualization, AI backend, export tools
├── docs/                   # architecture, methodology, manuals, safety notes
├── examples/               # sample academic texts
├── config.yaml             # default runtime configuration
├── config.example.yaml     # example configuration
├── requirements.txt        # core dependencies
├── requirements-ai.txt     # optional AI backend dependencies
├── selfcheck.py            # repository structure check
└── smoke_test.py           # minimal computation test
```

---

## Minimum Working Standard / 最低可用标准

AEB should be considered minimally functional when it can:

AEB 的最低可用标准是：

- install core dependencies;
- launch the Streamlit UI;
- parse sample documents;
- extract keyword species;
- compute basic ecological metrics;
- render at least one visualization page;
- export structured results;
- avoid meaningless garbled output.

也就是说，它至少应当能安装依赖、启动 Streamlit、解析样例文档、提取关键词物种、计算生态指标、渲染可视化页面、导出结构化结果，并且输出不是乱码。

---

## Important Notice / 重要说明

AEB is **not** a biological proof engine, not a formal scientometric authority, and not a replacement for domain expertise.

AEB **不是** 生物学证明机器，**不是** 正式文献计量评价权威，也 **不能替代** 领域专家判断。

Its ecological metaphors are designed to help users observe academic structures and generate questions. They should not be treated as final judgments about a field, paper, author, institution, or theory.

它的生态学隐喻是为了帮助用户观察学术结构、产生问题，而不是对一个领域、论文、作者、机构或理论做最终裁决。

---

## Documentation / 文档

- `INSTALL.md` — installation guide / 安装指南
- `docs/ARCHITECTURE.md` — system architecture / 系统架构
- `docs/METHODOLOGY.md` — methodology and formulas / 方法论与公式
- `docs/PAGES.md` — functional pages / 功能页面说明
- `docs/AI_BACKENDS.md` — AI backend configuration / AI 后端配置
- `docs/DATA_FORMATS.md` — input and output formats / 数据格式
- `docs/SAFETY.md` — safety and interpretation boundaries / 安全与解释边界
- `docs/ROADMAP.md` — future plan / 路线图
- `docs/manuals/` — original technical manual / 原始技术手册

---

## License / 许可证

MIT License. See `LICENSE`.
