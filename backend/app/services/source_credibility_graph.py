"""
Dynamic Source Credibility Graph with simplified Bayesian-style trust updates.
"""

from __future__ import annotations

from dataclasses import dataclass
from itertools import combinations
from typing import Any, Dict, List

import networkx as nx


def update_trust(prior: float, is_correct: bool, alpha: float = 0.7) -> float:
    """
    Simplified Bayesian-style update.
    If correct, move trust toward 1.
    If incorrect, decay trust toward 0.
    """
    prior = float(max(0.0, min(1.0, prior)))
    alpha = float(max(0.0, min(1.0, alpha)))
    if is_correct:
        updated = prior + alpha * (1.0 - prior)
    else:
        updated = prior * (1.0 - alpha)
    return float(max(0.0, min(1.0, updated)))


def _to_bool_label(label: Any) -> bool:
    label_str = str(label).strip().upper()
    return label_str in {"1", "TRUE", "VERIFIED", "FACT", "REAL"}


def _normalize_relation(relation: Any) -> str:
    relation_str = str(relation or "").strip().lower()
    if relation_str in {"supports", "support", "entailment"}:
        return "supports"
    if relation_str in {"contradicts", "contradict", "contradiction"}:
        return "contradicts"
    return "supports"


def is_evidence_correct(label: Any, relation: Any) -> bool:
    """
    Correctness rules:
    - supports + TRUE -> correct
    - supports + FALSE -> incorrect
    - contradicts + TRUE -> incorrect
    - contradicts + FALSE -> correct
    """
    label_true = _to_bool_label(label)
    rel = _normalize_relation(relation)
    if rel == "supports":
        return label_true
    return not label_true


@dataclass
class SourceCredibilityGraph:
    alpha: float = 0.7
    max_sources_per_query: int = 10

    def __post_init__(self):
        self.graph = nx.Graph()
        self.source_evidence: Dict[str, List[Dict[str, Any]]] = {}

    def _ensure_node(self, source: str):
        if source not in self.graph:
            self.graph.add_node(
                source,
                trust=0.5,
                influence=0.0,
                low_credibility=False,
            )

    def ingest_evidence(self, evidence_items: List[Dict[str, Any]]) -> Dict[str, Any]:
        if not evidence_items:
            return self.to_json([])

        # Top-N sources per query by best similarity to keep graph light.
        source_best_similarity: Dict[str, float] = {}
        for item in evidence_items:
            source = str(item.get("source", "Unknown Source") or "Unknown Source")
            similarity = float(item.get("similarity", 0.0) or 0.0)
            source_best_similarity[source] = max(source_best_similarity.get(source, 0.0), similarity)

        ranked_sources = sorted(
            source_best_similarity.items(),
            key=lambda pair: pair[1],
            reverse=True,
        )
        selected_sources = {s for s, _ in ranked_sources[: self.max_sources_per_query]}
        filtered_items = [
            item
            for item in evidence_items
            if str(item.get("source", "Unknown Source") or "Unknown Source") in selected_sources
        ]

        # Update trust node-by-node.
        for item in filtered_items:
            source = str(item.get("source", "Unknown Source") or "Unknown Source")
            self._ensure_node(source)
            current_trust = float(self.graph.nodes[source].get("trust", 0.5))
            correct = is_evidence_correct(item.get("label"), item.get("relation"))
            new_trust = update_trust(current_trust, correct, alpha=self.alpha)
            self.graph.nodes[source]["trust"] = new_trust
            self.graph.nodes[source]["low_credibility"] = new_trust < 0.3

            self.source_evidence.setdefault(source, []).append(
                {
                    "text": str(item.get("text", "")),
                    "label": str(item.get("label", "")),
                    "relation": _normalize_relation(item.get("relation")),
                    "similarity": float(item.get("similarity", 0.0) or 0.0),
                }
            )

        # Add/refresh edges among sources in this query context.
        query_sources = sorted({
            str(item.get("source", "Unknown Source") or "Unknown Source")
            for item in filtered_items
        })
        source_to_similarities: Dict[str, List[float]] = {s: [] for s in query_sources}
        for item in filtered_items:
            source = str(item.get("source", "Unknown Source") or "Unknown Source")
            source_to_similarities[source].append(float(item.get("similarity", 0.0) or 0.0))

        for src_a, src_b in combinations(query_sources, 2):
            mean_a = sum(source_to_similarities[src_a]) / max(1, len(source_to_similarities[src_a]))
            mean_b = sum(source_to_similarities[src_b]) / max(1, len(source_to_similarities[src_b]))
            edge_weight = float(max(0.0, min(1.0, (mean_a + mean_b) / 2.0)))
            if self.graph.has_edge(src_a, src_b):
                prev = float(self.graph[src_a][src_b].get("weight", edge_weight))
                self.graph[src_a][src_b]["weight"] = (prev + edge_weight) / 2.0
            else:
                self.graph.add_edge(src_a, src_b, weight=edge_weight)

        # Optional centrality/influence.
        if self.graph.number_of_nodes() > 1:
            try:
                centrality = nx.eigenvector_centrality(self.graph, max_iter=300, tol=1e-06)
            except Exception:
                centrality = {node: 0.0 for node in self.graph.nodes}
        else:
            centrality = {node: 0.0 for node in self.graph.nodes}

        for node, score in centrality.items():
            self.graph.nodes[node]["influence"] = float(score)

        return self.to_json(query_sources)

    def to_json(self, query_sources: List[str]) -> Dict[str, Any]:
        nodes = []
        for node in query_sources:
            attrs = self.graph.nodes.get(node, {})
            nodes.append(
                {
                    "id": node,
                    "trust": float(attrs.get("trust", 0.5)),
                    "influence": float(attrs.get("influence", 0.0)),
                    "low_credibility": bool(attrs.get("low_credibility", False)),
                }
            )

        edges = []
        query_source_set = set(query_sources)
        for src, dst, attrs in self.graph.edges(data=True):
            if src in query_source_set and dst in query_source_set:
                edges.append(
                    {
                        "source": src,
                        "target": dst,
                        "weight": float(attrs.get("weight", 0.0)),
                    }
                )

        source_evidence = {
            source: self.source_evidence.get(source, [])[-5:]
            for source in query_sources
        }

        return {
            "nodes": nodes,
            "edges": edges,
            "source_evidence": source_evidence,
        }

