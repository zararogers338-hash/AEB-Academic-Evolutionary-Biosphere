# -*- coding: utf-8 -*-
"""AEB 数据引擎 / Data Engine
TF-IDF, co-occurrence matrix, centrality, PageRank, ecology classification
"""

import re
import math
import numpy as np
import pandas as pd
import networkx as nx
from collections import Counter, defaultdict
from typing import Dict, List, Tuple, Optional
from sklearn.feature_extraction.text import TfidfVectorizer


def extract_keywords_from_texts(texts: List[str], top_n: int = 200, min_df: int = 2) -> pd.DataFrame:
    """Extract keywords using TF-IDF from a list of texts.
    Returns keywords_df with columns: keyword, tfidf_mean, doc_freq, first_year
    """
    if not texts:
        return pd.DataFrame(columns=["keyword", "tfidf_mean", "doc_freq", "first_year"])

    try:
        vectorizer = TfidfVectorizer(
            max_features=top_n * 3,
            min_df=min(min_df, len(texts)),
            max_df=0.95,
            stop_words="english",
            token_pattern=r"(?u)\b[a-zA-Z\u4e00-\u9fff]{2,}\b",
        )
        tfidf_matrix = vectorizer.fit_transform(texts)
        feature_names = vectorizer.get_feature_names_out()
        tfidf_means = np.array(tfidf_matrix.mean(axis=0)).flatten()
        doc_freqs = np.array((tfidf_matrix > 0).sum(axis=0)).flatten()

        kw_data = []
        for i, kw in enumerate(feature_names):
            kw_data.append({
                "keyword": kw,
                "tfidf_mean": round(float(tfidf_means[i]), 6),
                "doc_freq": int(doc_freqs[i]),
                "first_year": 2000,  # default, override with actual data
            })

        df = pd.DataFrame(kw_data)
        df = df.sort_values("tfidf_mean", ascending=False).head(top_n).reset_index(drop=True)
        return df
    except Exception:
        return pd.DataFrame(columns=["keyword", "tfidf_mean", "doc_freq", "first_year"])


def build_cooccurrence_matrix(texts: List[str], keywords: List[str]) -> pd.DataFrame:
    """Build keyword co-occurrence matrix from texts."""
    kw_set = set(k.lower() for k in keywords)
    co = defaultdict(int)
    for text in texts:
        words = set(re.findall(r"(?u)\b[a-zA-Z\u4e00-\u9fff]{2,}\b", text.lower()))
        present = words & kw_set
        present = sorted(present)
        for i in range(len(present)):
            for j in range(i + 1, len(present)):
                co[(present[i], present[j])] += 1
                co[(present[j], present[i])] += 1

    matrix = pd.DataFrame(0, index=keywords, columns=keywords, dtype=int)
    for (a, b), cnt in co.items():
        if a in matrix.index and b in matrix.columns:
            matrix.at[a, b] = cnt
    return matrix


def build_network(keywords_df: pd.DataFrame, cooccurrence: pd.DataFrame, min_edge_weight: int = 2) -> nx.Graph:
    """Build NetworkX graph from keywords and co-occurrence."""
    G = nx.Graph()
    for _, row in keywords_df.iterrows():
        G.add_node(row["keyword"], tfidf=row["tfidf_mean"], doc_freq=row["doc_freq"])

    kws = list(keywords_df["keyword"])
    for i in range(len(kws)):
        for j in range(i + 1, len(kws)):
            w = 0
            try:
                w = int(cooccurrence.at[kws[i], kws[j]])
            except (KeyError, ValueError):
                pass
            if w >= min_edge_weight:
                G.add_edge(kws[i], kws[j], weight=w)
    return G


def compute_centrality(G: nx.Graph) -> Dict[str, float]:
    """Compute betweenness centrality."""
    if len(G) == 0:
        return {}
    try:
        return nx.betweenness_centrality(G, weight="weight")
    except Exception:
        return {n: 0.0 for n in G.nodes()}


def compute_pagerank(G: nx.Graph) -> Dict[str, float]:
    """Compute PageRank."""
    if len(G) == 0:
        return {}
    try:
        return nx.pagerank(G, weight="weight")
    except Exception:
        return {n: 1.0 / len(G) for n in G.nodes()}


def classify_ecology(keywords_df: pd.DataFrame, centrality: Dict, config: dict) -> pd.DataFrame:
    """Classify keywords into ecological roles: top_predator, dominant, symbiotic, extinct."""
    df = keywords_df.copy()
    df["centrality"] = df["keyword"].map(lambda k: centrality.get(k, 0.0))
    df["score"] = df["tfidf_mean"] + df["centrality"]
    df = df.sort_values("score", ascending=False).reset_index(drop=True)

    top_pct = config.get("top_predator_percentile", 0.01)
    dom_pct = config.get("dominant_percentile", 0.10)
    n = len(df)

    roles = []
    for i in range(n):
        if i < max(1, int(n * top_pct)):
            roles.append("top_predator")
        elif i < max(2, int(n * dom_pct)):
            roles.append("dominant")
        else:
            roles.append("symbiotic")
    df["eco_role"] = roles
    return df


def compute_shannon_index(keywords_df: pd.DataFrame) -> float:
    """Compute Shannon diversity index from keyword frequencies."""
    freqs = keywords_df["tfidf_mean"].values
    total = freqs.sum()
    if total == 0:
        return 0.0
    proportions = freqs / total
    proportions = proportions[proportions > 0]
    return float(-np.sum(proportions * np.log2(proportions)))


def compute_monopoly_ratio(keywords_df: pd.DataFrame, top_n: int = 3) -> float:
    """Ratio of top N keywords' TF-IDF to total."""
    freqs = keywords_df["tfidf_mean"].values
    total = freqs.sum()
    if total == 0:
        return 0.0
    return float(freqs[:top_n].sum() / total)


def detect_extinction(keywords_df: pd.DataFrame, year_counts: Dict[str, Dict[int, int]], current_year: int = 2025, decay_threshold: float = 0.8, lookback: int = 5) -> List[str]:
    """Detect extinct keywords (decay > threshold over lookback years)."""
    extinct = []
    for kw in keywords_df["keyword"]:
        counts = year_counts.get(kw, {})
        if not counts:
            continue
        recent = sum(counts.get(y, 0) for y in range(current_year - lookback, current_year + 1))
        peak = max(counts.values()) if counts else 0
        if peak > 0 and recent == 0:
            extinct.append(kw)
        elif peak > 0 and (peak - recent) / peak > decay_threshold:
            extinct.append(kw)
    return extinct


def compute_niche_levels(keywords_df: pd.DataFrame, n_levels: int = 5) -> pd.DataFrame:
    """Assign niche levels 1-5 based on score quantiles."""
    df = keywords_df.copy()
    if len(df) == 0:
        df["niche_level"] = []
        return df
    df["niche_level"] = pd.qcut(df["score"].rank(method="first"), q=min(n_levels, len(df)), labels=False, duplicates="drop") + 1
    return df


def compute_carbon_sink(keywords_df: pd.DataFrame, cooccurrence: pd.DataFrame) -> pd.DataFrame:
    """Carbon sink = total co-occurrence weight (how much a keyword contributes to the ecosystem)."""
    df = keywords_df.copy()
    sinks = []
    for kw in df["keyword"]:
        if kw in cooccurrence.index:
            sinks.append(int(cooccurrence.loc[kw].sum()))
        else:
            sinks.append(0)
    df["carbon_sink"] = sinks
    return df


def build_evolution_tree(keywords_df: pd.DataFrame, cooccurrence: pd.DataFrame) -> Dict:
    """Build a tree structure for evolution visualization.
    Root = highest score keyword, branches = co-occurring keywords.
    """
    if keywords_df.empty:
        return {"name": "root", "children": []}

    df = keywords_df.sort_values("score", ascending=False).reset_index(drop=True)
    root_kw = df.iloc[0]["keyword"]

    # BFS tree from root
    visited = {root_kw}
    tree = {"name": root_kw, "score": float(df.iloc[0]["score"]), "year": int(df.iloc[0].get("first_year", 2000)), "children": []}

    queue = [(tree, root_kw)]
    max_depth = 5
    depth = 0

    while queue and depth < max_depth:
        next_queue = []
        for parent_node, parent_kw in queue:
            # Find co-occurring keywords
            if parent_kw in cooccurrence.index:
                neighbors = cooccurrence.loc[parent_kw]
                neighbors = neighbors[neighbors > 0].sort_values(ascending=False)
                for child_kw in neighbors.index[:5]:  # max 5 children
                    if child_kw not in visited and child_kw in df["keyword"].values:
                        visited.add(child_kw)
                        row = df[df["keyword"] == child_kw].iloc[0]
                        child_node = {
                            "name": child_kw,
                            "score": float(row["score"]),
                            "year": int(row.get("first_year", 2000)),
                            "children": [],
                        }
                        parent_node["children"].append(child_node)
                        next_queue.append((child_node, child_kw))
        queue = next_queue
        depth += 1

    return tree


def detect_louvain_communities(G: nx.Graph, resolution: float = 1.0) -> Dict[str, int]:
    """Detect communities using Louvain algorithm."""
    if len(G) == 0:
        return {}
    try:
        import community as community_louvain
        return community_louvain.best_partition(G, weight="weight", resolution=resolution)
    except Exception:
        # Fallback: greedy modularity
        try:
            communities = nx.community.greedy_modularity_communities(G, weight="weight")
            partition = {}
            for i, comm in enumerate(communities):
                for node in comm:
                    partition[node] = i
            return partition
        except Exception:
            return {n: 0 for n in G.nodes()}


class AEBDataEngine:
    """Central data engine managing all computed state."""

    def __init__(self):
        self.raw_texts: List[str] = []
        self.filenames: List[str] = []
        self.papers_df = pd.DataFrame()
        self.keywords_df = pd.DataFrame()
        self.cooccurrence = pd.DataFrame()
        self.graph = nx.Graph()
        self.centrality: Dict[str, float] = {}
        self.pagerank: Dict[str, float] = {}
        self.communities: Dict[str, int] = {}
        self.evolution_tree: Dict = {}
        self.shannon_index: float = 0.0
        self.monopoly_ratio: float = 0.0
        self.extinct_keywords: List[str] = []
        self.year_counts: Dict[str, Dict[int, int]] = {}
        self.is_computed = False

    def ingest(self, parse_results: list):
        """Ingest parsed file results."""
        for r in parse_results:
            if r.get("success") and r.get("text", "").strip():
                self.raw_texts.append(r["text"])
                self.filenames.append(r.get("filename", "unknown"))

        # Build papers_df
        self.papers_df = pd.DataFrame({
            "filename": self.filenames,
            "text": self.raw_texts,
            "year": [self._extract_year(t) for t in self.raw_texts],
        })

    def _extract_year(self, text: str) -> int:
        """Try to extract a year from text."""
        years = re.findall(r"\b(19[5-9]\d|20[0-2]\d)\b", text[:2000])
        if years:
            return int(max(years))
        return 2020

    def compute_all(self, config: dict, progress_callback=None):
        """Run full computation pipeline."""
        steps = 8
        step = 0

        def _progress(msg):
            nonlocal step
            step += 1
            if progress_callback:
                progress_callback(step / steps, msg)

        _progress("Extracting keywords / 提取关键词...")
        self.keywords_df = extract_keywords_from_texts(self.raw_texts)

        if self.keywords_df.empty:
            self.is_computed = True
            return

        _progress("Building co-occurrence / 构建共现矩阵...")
        kw_list = list(self.keywords_df["keyword"])
        self.cooccurrence = build_cooccurrence_matrix(self.raw_texts, kw_list)

        _progress("Building network / 构建网络...")
        self.graph = build_network(self.keywords_df, self.cooccurrence)

        _progress("Computing centrality & PageRank / 计算中心性...")
        self.centrality = compute_centrality(self.graph)
        self.pagerank = compute_pagerank(self.graph)

        _progress("Classifying ecology / 生态分类...")
        self.keywords_df["centrality"] = self.keywords_df["keyword"].map(lambda k: self.centrality.get(k, 0.0))
        self.keywords_df["pagerank"] = self.keywords_df["keyword"].map(lambda k: self.pagerank.get(k, 0.0))
        self.keywords_df["score"] = self.keywords_df["tfidf_mean"] + self.keywords_df["centrality"]
        self.keywords_df = classify_ecology(self.keywords_df, self.centrality, config.get("ecology", {}))
        self.keywords_df = compute_niche_levels(self.keywords_df, config.get("ecology", {}).get("niche_levels", 5))
        self.keywords_df = compute_carbon_sink(self.keywords_df, self.cooccurrence)

        _progress("Computing diversity / 计算多样性...")
        self.shannon_index = compute_shannon_index(self.keywords_df)
        self.monopoly_ratio = compute_monopoly_ratio(self.keywords_df)

        _progress("Detecting communities / 检测群落...")
        self.communities = detect_louvain_communities(self.graph, config.get("ecology", {}).get("louvain_resolution", 1.0))
        self.keywords_df["community"] = self.keywords_df["keyword"].map(lambda k: self.communities.get(k, -1))

        _progress("Building evolution tree / 构建进化树...")
        self.evolution_tree = build_evolution_tree(self.keywords_df, self.cooccurrence)

        self.is_computed = True

    def get_keywords_by_role(self, role: str) -> pd.DataFrame:
        return self.keywords_df[self.keywords_df["eco_role"] == role]

    def get_community_keywords(self, comm_id: int) -> pd.DataFrame:
        return self.keywords_df[self.keywords_df["community"] == comm_id]

    def get_keyword_neighbors(self, keyword: str) -> List[Tuple[str, int]]:
        """Get co-occurring keywords sorted by weight."""
        if keyword not in self.cooccurrence.index:
            return []
        row = self.cooccurrence.loc[keyword]
        neighbors = row[row > 0].sort_values(ascending=False)
        return [(k, int(v)) for k, v in neighbors.items()]

    def get_fitness_data(self, keyword: str) -> List[Dict]:
        """Get per-year frequency data for a keyword."""
        data = []
        for _, row in self.papers_df.iterrows():
            year = row["year"]
            count = row["text"].lower().count(keyword.lower())
            data.append({"year": year, "count": count})
        df = pd.DataFrame(data)
        if df.empty:
            return []
        grouped = df.groupby("year")["count"].sum().reset_index()
        return grouped.to_dict("records")

    def to_json(self) -> Dict:
        """Export engine state as JSON-serializable dict."""
        return {
            "total_papers": len(self.papers_df),
            "total_keywords": len(self.keywords_df),
            "shannon_index": self.shannon_index,
            "monopoly_ratio": self.monopoly_ratio,
            "keywords": self.keywords_df.to_dict("records") if not self.keywords_df.empty else [],
            "evolution_tree": self.evolution_tree,
            "communities": self.communities,
        }


def get_engine() -> AEBDataEngine:
    """Get or create singleton data engine."""
    import streamlit as st
    if "aeb_engine" not in st.session_state:
        st.session_state.aeb_engine = AEBDataEngine()
    return st.session_state.aeb_engine
