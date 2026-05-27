# Methodology / 方法论

AEB uses ecological metaphors to analyze academic corpora.

AEB 使用生态学隐喻分析学术语料。

## Pipeline / 流程

1. Parse uploaded files into text.
2. Extract keywords using TF-IDF.
3. Build keyword co-occurrence matrix.
4. Construct NetworkX graph.
5. Compute centrality and PageRank.
6. Detect communities using Louvain or greedy modularity fallback.
7. Compute diversity and concentration indicators.
8. Classify keywords into ecological roles.
9. Render 2D and 3D visualizations.
10. Optionally ask an AI backend to interpret the structure.

## Important formulas / 重要指标

- **TF-IDF**: identifies keyword species.
- **Co-occurrence weight**: indicates concept proximity.
- **Betweenness centrality**: identifies bridge concepts.
- **PageRank**: identifies structurally influential concepts.
- **Shannon diversity**: estimates keyword ecosystem diversity.
- **Monopoly ratio**: estimates top keyword concentration.
- **Carbon sink**: sum of co-occurrence weights for a keyword.

## Limits / 限制

These metrics are observation tools. They do not prove that a concept is scientifically correct, important, or valuable in every context.

这些指标是观测工具，不证明某个概念在所有语境下都是正确、重要或有价值的。
