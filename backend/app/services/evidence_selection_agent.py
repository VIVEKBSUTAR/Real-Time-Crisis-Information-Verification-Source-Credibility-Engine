"""
Evidence Selection Agent.

This module filters and ranks NLI-processed evidence so downstream decisioning
and explanation consume only the most informative items.
"""

from __future__ import annotations

from typing import Any, Dict, List

import numpy as np


W1_SIMILARITY = 0.6
W2_RELATION = 0.4
MIN_SIMILARITY = 0.5

RELATION_WEIGHTS = {
    "supports": 1.0,
    "contradicts": 1.0,
    "neutral": 0.2,
}


def _normalize_relation(relation: Any) -> str:
    """Normalize relation labels to supports/contradicts/neutral."""
    raw = str(relation or "").strip().lower()
    if raw in {"supports", "support", "entailment", "entailed"}:
        return "supports"
    if raw in {"contradicts", "contradict", "contradiction"}:
        return "contradicts"
    return "neutral"


def compute_evidence_score(similarity: float, relation: str) -> float:
    """
    Compute deterministic evidence score.

    score = (0.6 * similarity) + (0.4 * relation_weight)
    """
    sim = float(np.clip(similarity, 0.0, 1.0))
    rel = _normalize_relation(relation)
    relation_weight = RELATION_WEIGHTS.get(rel, RELATION_WEIGHTS["neutral"])
    return float((W1_SIMILARITY * sim) + (W2_RELATION * relation_weight))


def _rank_candidates(candidates: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Sort by:
      1) score desc
      2) similarity desc
      3) text asc (deterministic tie-breaker)
    """
    return sorted(
        candidates,
        key=lambda item: (
            -float(item["score"]),
            -float(item["similarity"]),
            str(item["text"]),
        ),
    )


def select_best_evidence(nli_results: List[Dict], top_n: int = 3) -> List[Dict]:
    """
    Select best evidence items for decisioning/explanations.

    Input item shape:
    {
        "text": str,
        "similarity": float,
        "label": "TRUE|FALSE",   # optional for selection
        "relation": "supports|contradicts|neutral"
    }

    Output item shape:
    {
        "text": str,
        "similarity": float,
        "relation": str,
        "score": float
    }
    """
    if not nli_results:
        return []

    limit = max(1, int(top_n or 1))

    # Step 0: remove weak signals before scoring.
    filtered_inputs = [
        item for item in nli_results
        if float(item.get("similarity", 0.0) or 0.0) >= MIN_SIMILARITY
    ]
    if not filtered_inputs:
        return []

    scored: List[Dict[str, Any]] = []
    for item in filtered_inputs:
        text = str(item.get("text", "") or "")
        similarity = float(item.get("similarity", 0.0) or 0.0)
        relation = _normalize_relation(item.get("relation"))
        score = compute_evidence_score(similarity, relation)
        scored.append(
            {
                "text": text,
                "similarity": similarity,
                "relation": relation,
                "score": score,
            }
        )

    ranked = _rank_candidates(scored)

    supports = [item for item in ranked if item["relation"] == "supports"]
    contradicts = [item for item in ranked if item["relation"] == "contradicts"]
    neutrals = [item for item in ranked if item["relation"] == "neutral"]

    # Case 1: only neutral evidence -> top 2 highest similarity.
    if neutrals and not supports and not contradicts:
        neutral_sorted = sorted(
            neutrals,
            key=lambda item: (-float(item["similarity"]), str(item["text"])),
        )
        return neutral_sorted[: min(2, len(neutral_sorted))]

    # Case 2: all evidence has same relation -> top-N by score.
    relations_present = {item["relation"] for item in ranked}
    if len(relations_present) == 1:
        return ranked[: min(limit, len(ranked))]

    # Step 4: ensure diversity when both relations exist.
    selected: List[Dict[str, Any]] = []
    selected_ids = set()

    if supports and contradicts and limit >= 2:
        must_include = {id(supports[0]), id(contradicts[0])}
        for item in ranked:
            if id(item) in must_include and id(item) not in selected_ids:
                selected.append(item)
                selected_ids.add(id(item))
                if len(selected) >= limit:
                    return selected

    # Fill remainder by rank.
    for item in ranked:
        if id(item) in selected_ids:
            continue
        selected.append(item)
        selected_ids.add(id(item))
        if len(selected) >= limit:
            break

    return selected

