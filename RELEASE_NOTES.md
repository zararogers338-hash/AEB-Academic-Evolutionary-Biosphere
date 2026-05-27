# AEB Academic Evolutionary Biosphere v3.0 Open Source Preview

AEB Academic Evolutionary Biosphere is an open-source Streamlit workbench that models academic documents and research fields as evolving biological ecosystems.

AEB 学术演化生物圈是一个开源 Streamlit 工作台，它把学术文档和研究领域建模为会演化的生物生态系统。

## English

This is the first open-source preview release of **AEB Academic Evolutionary Biosphere v3.0**.

AEB turns uploaded academic documents into a keyword ecosystem. It extracts keyword species, builds co-occurrence networks, computes ecological metrics, classifies concepts into roles, detects communities, and visualizes academic evolution through 13 interactive pages.

It uses evolutionary biology and ecology as analytical metaphors: papers become habitat samples, keywords become species, strong concepts become dominant species or top predators, older concepts form fossil layers, and declining ideas can be observed through extinction-style simulations.

## 中文

这是 **AEB Academic Evolutionary Biosphere / 学术演化生物圈 v3.0** 的第一个开源预览版本。

AEB 可以把上传的学术文档转化为关键词生态系统。它会提取关键词物种，构建共现网络，计算生态指标，将概念划分为不同生态角色，检测概念群落，并通过 13 个交互页面可视化学术演化过程。

它使用演化生物学和生态学作为分析隐喻：论文像栖息地样本，关键词像物种，强势概念像优势物种或顶级捕食者，较早出现的概念形成化石层，正在衰退的思想可以通过灭绝模拟来观察。

## Included in this release / 本版本包含

- Streamlit-based local web interface
- Multi-format academic document parsing
- TF-IDF keyword extraction
- Co-occurrence network construction
- NetworkX centrality and PageRank analysis
- Louvain community detection with fallback
- Shannon diversity and monopoly ratio computation
- Ecological role classification
- Evolution tree visualization
- Force-directed keyword graph
- Geological fossil layers
- Extinction event simulation
- Fitness curve tracking
- Migration path visualization
- Species origin tracing
- Carbon sink visualization
- Niche clustering and hierarchy
- Species collection system
- AI-assisted interpretation workflow
- GGUF / Ollama / OpenAI-compatible backend support
- Example input texts
- Bilingual documentation
- Installation guide
- Technical manual preservation
- Self-check and smoke-test scripts
- Open-source cleanup

## Installation / 安装

```bash
git clone https://github.com/zararogers338-hash/AEB-Academic-Evolutionary-Biosphere.git
cd AEB-Academic-Evolutionary-Biosphere
pip install -r requirements.txt
streamlit run app.py
```

Optional AI backends:

```bash
pip install -r requirements-ai.txt
```

## Important Notice / 重要说明

AEB is not a biological proof engine, not a formal scientometric authority, and not a replacement for expert scholarly judgment.

AEB 不是生物学证明机器，不是正式文献计量评价权威，也不能替代专家学术判断。

Use it as an observation window for academic ecosystems, not as an absolute truth machine.

请把它当作观察学术生态的窗口，而不是绝对真理机器。
