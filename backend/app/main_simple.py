"""
Simplified Sentinel Protocol Backend - Minimum working version
Compatible with Python 3.14
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, List
import json
import os
from datetime import datetime

# Create FastAPI app
app = FastAPI(
    title="Sentinel Protocol",
    version="0.1.0",
    description="Real-time crisis misinformation verification"
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Schemas
class ClaimInput(BaseModel):
    text: str
    source_url: Optional[str] = None

class EvidenceItem(BaseModel):
    source: str
    relation: str
    confidence: float

class ClaimOutput(BaseModel):
    claim_id: str
    original_claim: str
    verdict: str
    confidence: float
    evidence: List[EvidenceItem]
    explanation: str

# Mock dataset
MOCK_DATASET = [
    {"claim": "Bridge collapsed in Pune", "label": 0, "source": "Twitter", "date": "2024-01-15"},
    {"claim": "Heavy rainfall causes dam breach", "label": 0, "source": "Reddit", "date": "2024-01-16"},
    {"claim": "Traffic accident on highway", "label": 1, "source": "News", "date": "2024-01-17"},
]

# Health check
@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "app": "Sentinel Protocol",
        "version": "0.1.0"
    }

# Main endpoint
@app.post("/analyze_claim", response_model=ClaimOutput)
async def analyze_claim(request: ClaimInput):
    """Analyze a claim for misinformation"""
    
    import random
    import uuid
    
    # Generate claim ID
    claim_id = str(uuid.uuid4())[:8]
    
    # Simulate verification (real: similarity matching against dataset)
    verdicts = ["Verified", "Debunked", "Manipulated"]
    verdict = random.choice(verdicts)
    confidence = round(random.uniform(0.5, 0.95), 2)
    
    # Mock evidence
    evidence = [
        EvidenceItem(source="Reuters", relation="support", confidence=0.82),
        EvidenceItem(source="AP News", relation="support", confidence=0.75),
    ]
    
    # Mock explanation
    explanation = f"This claim is likely {verdict.lower()} based on {len(evidence)} trusted sources within the time window."
    
    return ClaimOutput(
        claim_id=claim_id,
        original_claim=request.text,
        verdict=verdict,
        confidence=confidence,
        evidence=evidence,
        explanation=explanation
    )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
