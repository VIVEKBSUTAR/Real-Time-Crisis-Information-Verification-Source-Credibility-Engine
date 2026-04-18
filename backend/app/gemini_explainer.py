"""
Gemini-based explanation generator - fallback to deterministic if API fails.
"""

import google.generativeai as genai
import os
from typing import Dict, Any

# Get API key from environment or use provided key
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY", "AIzaSyBoW2OWLJUIe7FgYhPjkhoAYWfwikUyKVc")
try:
    genai.configure(api_key=GEMINI_API_KEY)
    MODEL = "gemini-pro"  # Use the available model
    GEMINI_AVAILABLE = True
except:
    GEMINI_AVAILABLE = False
    print("⚠️  Gemini not available, using fallback explanations")


def convert_credibility_to_verdict(credibility_score):
    """Convert credibility score to verdict and confidence."""
    credibility_score = float(credibility_score) if credibility_score is not None else 0.5
    
    if credibility_score >= 0.7:
        return "TRUE", credibility_score
    elif credibility_score <= 0.3:
        return "FALSE", 1.0 - credibility_score
    else:
        return "UNVERIFIED", 0.5


def format_evidence_for_prompt(similar_claims, limit=3):
    """Format evidence for prompt."""
    if not similar_claims:
        return "No evidence"
    
    formatted = []
    for i, claim in enumerate(similar_claims[:limit], 1):
        text = str(claim.get("text", ""))[:100]
        label = "✓ TRUE" if claim.get("label") else "✗ FALSE"
        formatted.append(f"{i}. [{label}] {text}")
    
    return "\n".join(formatted)


def generate_explanation(analysis_data):
    """Generate explanation with Gemini or fallback."""
    claim = analysis_data.get("claim", "")
    verdict = analysis_data.get("verdict", "UNVERIFIED")
    confidence = float(analysis_data.get("confidence", 0.5))
    similar_claims = analysis_data.get("similar_claims", [])
    
    confidence_pct = int(confidence * 100)
    
    if not GEMINI_AVAILABLE or not similar_claims:
        return f"Claim classified as {verdict} with {confidence_pct}% confidence based on dataset analysis."
    
    evidence_text = format_evidence_for_prompt(similar_claims)
    prompt = f"""As a crisis analyst, explain briefly why this claim is {verdict}:

Claim: {claim}
Confidence: {confidence_pct}%

Evidence:
{evidence_text}

Keep to 2 sentences. Reference evidence. No external facts."""
    
    try:
        model = genai.GenerativeModel(MODEL)
        response = model.generate_content(prompt)
        return response.text.strip()
    except:
        return f"Claim classified as {verdict} with {confidence_pct}% confidence."


def generate_evidence_summary(analysis_data):
    """Generate summary with Gemini or fallback."""
    similar_claims = analysis_data.get("similar_claims", [])
    
    if not similar_claims:
        return "No evidence available for analysis."
    
    supporting = len([c for c in similar_claims if c.get("label")])
    contradicting = len([c for c in similar_claims if not c.get("label")])
    
    if not GEMINI_AVAILABLE:
        return f"{supporting} sources support this claim, {contradicting} contradict it."
    
    evidence_text = format_evidence_for_prompt(similar_claims)
    prompt = f"""Summarize this evidence in 1-2 sentences:

Evidence:
{evidence_text}

Be concise. Identify consensus or conflict."""
    
    try:
        model = genai.GenerativeModel(MODEL)
        response = model.generate_content(prompt)
        return response.text.strip()
    except:
        return f"{supporting} supporting vs {contradicting} contradicting sources."


def enrich_analysis_response(backend_data):
    """Enrich backend response with explanations."""
    credibility = float(backend_data.get("credibility", 0.5))
    verdict, confidence = convert_credibility_to_verdict(credibility)
    
    enriched = {
        "claim": backend_data.get("claim", ""),
        "verdict": verdict,
        "confidence": float(confidence),
        "similar_claims": backend_data.get("similar_claims", []),
    }
    
    explanation = generate_explanation(enriched)
    evidence_summary = generate_evidence_summary(enriched)
    
    sources = []
    for c in enriched["similar_claims"][:5]:
        sources.append({
            "text": str(c.get("text", ""))[:120],
            "label": "TRUE" if c.get("label") else "FALSE",
            "similarity": round(float(c.get("similarity", 0)), 2),
        })
    
    return {
        "claim": enriched["claim"],
        "verdict": verdict,
        "confidence": round(float(confidence), 2),
        "explanation": explanation,
        "evidence_summary": evidence_summary,
        "sources": sources,
    }
