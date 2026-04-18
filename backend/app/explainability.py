"""
Explainability layer for deterministic claim verification.

Gemini is only used to explain deterministic outputs.
It never performs classification, similarity, embeddings, or verdict selection.
"""

from __future__ import annotations

import os
from typing import Any, Dict, List

try:
    import google.generativeai as genai
except Exception:  # pragma: no cover
    genai = None

try:
    from dotenv import load_dotenv
except Exception:  # pragma: no cover
    load_dotenv = None

if load_dotenv is not None:
    load_dotenv()


_MODEL_CANDIDATES = [
    "gemini-1.5-flash",
    "gemini-1.5-flash-latest",
    "gemini-1.5-pro-latest",
]
_MAX_EVIDENCE = 3
_MAX_EVIDENCE_CHARS = 200


def _normalize_verdict(verdict: str) -> str:
    verdict = (verdict or "").strip().upper()
    if verdict in {"TRUE", "FALSE", "UNVERIFIED"}:
        return verdict
    return "UNVERIFIED"


def _fallback_text(verdict: str, confidence: float) -> str:
    pct = int(max(0.0, min(1.0, confidence)) * 100)
    return f"Claim classified as {verdict} with {pct}% confidence based on available evidence."


def _relation_for_evidence(label: str) -> str:
    return "supports" if str(label).upper() == "TRUE" else "contradicts"


def _select_top_evidence(evidence: List[Dict[str, Any]], limit: int = _MAX_EVIDENCE) -> List[Dict[str, Any]]:
    ranked = []
    for item in evidence or []:
        similarity = float(item.get("similarity", 0.0) or 0.0)
        relation = str(item.get("relation", "")).lower()
        relation_weight = 1.0 if relation in {"supports", "contradicts"} else 0.0
        ranked.append((similarity, relation_weight, item))
    ranked.sort(key=lambda x: (x[0], x[1]), reverse=True)
    return [row[2] for row in ranked[:limit]]


def _format_evidence_lines(evidence: List[Dict[str, Any]]) -> str:
    lines = []
    for idx, item in enumerate(evidence, start=1):
        text = str(item.get("text", "")).strip().replace("\n", " ")[:_MAX_EVIDENCE_CHARS]
        similarity = float(item.get("similarity", 0.0) or 0.0)
        label = str(item.get("label", "UNVERIFIED")).upper()
        relation = str(item.get("relation", "contradicts")).lower()
        lines.append(
            f"{idx}. [{relation}] [{label}] sim={similarity:.2f} :: {text}"
        )
    return "\n".join(lines) if lines else "No strong evidence retrieved."


def _fallback_explanation_with_evidence(verdict: str, confidence: float, evidence: List[Dict[str, Any]]) -> str:
    base = _fallback_text(verdict, confidence)
    if not evidence:
        return base
    top = _select_top_evidence(evidence, limit=1)[0]
    snippet = str(top.get("text", "")).strip().replace("\n", " ")[:120]
    relation = str(top.get("relation", "contradicts"))
    return f"{base} Retrieved dataset evidence ({relation}): {snippet}"


def _fallback_summary_with_evidence(verdict: str, confidence: float, evidence: List[Dict[str, Any]]) -> str:
    if not evidence:
        return _fallback_text(verdict, confidence)
    top = _select_top_evidence(evidence, limit=min(3, len(evidence)))
    supports = sum(1 for e in top if str(e.get("relation", "")).lower() == "supports")
    contradicts = sum(1 for e in top if str(e.get("relation", "")).lower() == "contradicts")
    return f"Top dataset evidence: {supports} supporting, {contradicts} contradicting. Verdict remains {verdict}."


def _gemini_model():
    api_key = os.getenv("GEMINI_API_KEY", "").strip()
    if not api_key or genai is None:
        return None
    genai.configure(api_key=api_key)
    for model_name in _MODEL_CANDIDATES:
        try:
            return genai.GenerativeModel(model_name)
        except Exception:
            continue
    return None


def generate_explanation(data: Dict[str, Any]) -> str:
    """
    Generate concise analyst-style explanation from deterministic result.
    """
    verdict = _normalize_verdict(str(data.get("verdict", "UNVERIFIED")))
    confidence = float(data.get("confidence", 0.0) or 0.0)
    claim = str(data.get("claim", "")).strip()
    top_evidence = _select_top_evidence(data.get("evidence", []))

    model = _gemini_model()
    if model is None:
        return _fallback_explanation_with_evidence(verdict, confidence, top_evidence)

    prompt = (
        "You are a crisis intelligence analyst.\n\n"
        f"Claim: {claim}\n"
        f"Verdict: {verdict}\n"
        f"Confidence: {int(confidence * 100)}%\n\n"
        "Evidence:\n"
        f"{_format_evidence_lines(top_evidence)}\n\n"
        "Instructions:\n"
        "- Explain WHY the verdict was reached\n"
        "- Refer to retrieved claims explicitly\n"
        "- State uncertainty if evidence is mixed/weak\n"
        "- Do NOT add external facts\n"
        "- Keep concise and analytical (3-5 lines)"
    )

    try:
        resp = model.generate_content(
            prompt,
            generation_config={"temperature": 0.2, "max_output_tokens": 170},
            request_options={"timeout": 2.5},
        )
        text = (getattr(resp, "text", "") or "").strip()
        return text if text else _fallback_explanation_with_evidence(verdict, confidence, top_evidence)
    except Exception as exc:
        print(f"   ⚠️  Gemini explanation fallback: {exc}")
        return _fallback_explanation_with_evidence(verdict, confidence, top_evidence)


def generate_evidence_summary(data: Dict[str, Any]) -> str:
    """
    Summarize top evidence into a short intelligence insight.
    """
    verdict = _normalize_verdict(str(data.get("verdict", "UNVERIFIED")))
    confidence = float(data.get("confidence", 0.0) or 0.0)
    claim = str(data.get("claim", "")).strip()
    top_evidence = _select_top_evidence(data.get("evidence", []))

    model = _gemini_model()
    if model is None:
        return _fallback_summary_with_evidence(verdict, confidence, top_evidence)

    prompt = (
        "Summarize the evidence for the following claim:\n\n"
        f"{claim}\n\n"
        "Evidence:\n"
        f"{_format_evidence_lines(top_evidence)}\n\n"
        "Instructions:\n"
        "- Distinguish supporting and contradicting evidence\n"
        "- Identify dominant pattern\n"
        "- Mention weak/no strong support when applicable\n"
        "- Keep under 3 lines\n"
        "- Do NOT add external information"
    )

    try:
        resp = model.generate_content(
            prompt,
            generation_config={"temperature": 0.2, "max_output_tokens": 120},
            request_options={"timeout": 2.5},
        )
        text = (getattr(resp, "text", "") or "").strip()
        return text if text else _fallback_summary_with_evidence(verdict, confidence, top_evidence)
    except Exception as exc:
        print(f"   ⚠️  Gemini summary fallback: {exc}")
        return _fallback_summary_with_evidence(verdict, confidence, top_evidence)


def build_explainability_input(
    claim: str,
    verdict: str,
    confidence: float,
    sources: List[Dict[str, Any]],
) -> Dict[str, Any]:
    evidence: List[Dict[str, Any]] = []
    for src in sources or []:
        label = str(src.get("label", "FALSE")).upper()
        evidence.append(
            {
                "text": str(src.get("text", "")),
                "similarity": float(src.get("similarity", 0.0) or 0.0),
                "label": label if label in {"TRUE", "FALSE"} else "FALSE",
                "relation": _relation_for_evidence(label),
            }
        )
    return {
        "claim": claim,
        "verdict": _normalize_verdict(verdict),
        "confidence": float(confidence or 0.0),
        "evidence": evidence,
    }
