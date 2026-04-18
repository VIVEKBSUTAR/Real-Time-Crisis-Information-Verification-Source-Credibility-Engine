from fastapi import FastAPI, Depends, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
import uuid
import time
from datetime import datetime
from typing import List

from app.core.config import settings
from app.core.database import engine, Base, get_db
from app.models.models import Claim, ClusterDB, Evidence, Source
from app.api.schemas.claim import ClaimInput, ClaimOutput, EvidenceOutput
from app.services.verification_service import VerificationService

# Initialize database
Base.metadata.create_all(bind=engine)

# Create FastAPI app
app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="Production-grade real-time crisis misinformation verification system"
)

# CORS middleware for frontend integration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "app": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "database": "connected"
    }

@app.post("/analyze_claim", response_model=ClaimOutput)
async def analyze_claim(
    request: ClaimInput,
    db: Session = Depends(get_db)
):
    """
    Main endpoint for claim analysis using dataset verification.
    
    Process:
    1. Input validation
    2. Dataset search (similarity matching)
    3. Verdict aggregation
    4. Confidence calculation
    5. Explanation generation
    6. Source matching
    """
    
    start_time = time.time()
    claim_id = f"CLAIM-{uuid.uuid4().hex[:8].upper()}"
    
    try:
        # Initialize verification service
        verification_svc = VerificationService(db)
        
        # Analyze claim using dataset
        verification_result = verification_svc.analyze_claim(request.text)
        
        # Store claim in database
        db_claim = Claim(
            id=claim_id,
            text=request.text,
            label=verification_result['label'],
            confidence=verification_result['confidence'],
            explanation=verification_result['explanation'],
            source_name=request.source_name or "Direct Input",
            source_platform=request.source_platform or "API"
        )
        db.add(db_claim)
        db.commit()
        
        # Format sources for response
        supporting_sources = []
        if verification_result.get('supporting_sources'):
            for src in verification_result['supporting_sources']:
                supporting_sources.append(
                    EvidenceOutput(
                        source_name=src.get('name', 'Dataset Match'),
                        relation="support",
                        confidence=src.get('similarity', 0.8),
                        text=src.get('quote', '')
                    )
                )
        
        # Build response
        processing_time = time.time() - start_time
        
        return ClaimOutput(
            claim_id=claim_id,
            text=request.text,
            verdict=verification_result['label'],
            confidence=verification_result['confidence'],
            signal_strength=verification_result['confidence'],
            explanation=verification_result['explanation'],
            supporting_sources=supporting_sources if supporting_sources else [
                EvidenceOutput(
                    source_name="Dataset",
                    relation="neutral",
                    confidence=0.5,
                    text="Analysis complete. Review results above."
                )
            ],
            missing_sources=verification_result.get('missing_sources', []),
            has_exif_warning=False,
            processing_time=processing_time,
            sources_checked=verification_result.get('sources_checked', 0)
        )
    
    except Exception as e:
        print(f"Error analyzing claim: {e}")
        raise HTTPException(status_code=500, detail=f"Analysis error: {str(e)}")

@app.get("/claims/{claim_id}")
async def get_claim(claim_id: str, db: Session = Depends(get_db)):
    """Retrieve a claim analysis by ID"""
    try:
        db_claim = db.query(Claim).filter(Claim.id == claim_id).first()
        if not db_claim:
            raise HTTPException(status_code=404, detail="Claim not found")
        
        return {
            "id": db_claim.id,
            "text": db_claim.text,
            "label": db_claim.label,
            "confidence": db_claim.confidence,
            "explanation": db_claim.explanation,
            "created_at": db_claim.created_at
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/sources")
async def list_sources(db: Session = Depends(get_db)):
    """List all data sources and their credibility scores"""
    try:
        sources = db.query(Source).all()
        return [
            {
                "id": s.id,
                "name": s.name,
                "trust_score": s.trust_score,
                "verified_count": s.verified_count,
                "error_count": s.error_count
            }
            for s in sources
        ]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/statistics")
async def get_statistics(db: Session = Depends(get_db)):
    """Get system statistics"""
    try:
        total_claims = db.query(Claim).count()
        true_claims = db.query(Claim).filter(Claim.label == 'TRUE').count()
        false_claims = db.query(Claim).filter(Claim.label == 'FALSE').count()
        unverified_claims = db.query(Claim).filter(Claim.label == 'UNVERIFIED').count()
        
        return {
            "total_claims_analyzed": total_claims,
            "verdicts": {
                "TRUE": true_claims,
                "FALSE": false_claims,
                "UNVERIFIED": unverified_claims
            },
            "accuracy": {
                "true_percentage": (true_claims / total_claims * 100) if total_claims > 0 else 0,
                "false_percentage": (false_claims / total_claims * 100) if total_claims > 0 else 0
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/info")
async def system_info():
    """Return system configuration and status"""
    return {
        "system_name": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "description": "Real-Time Crisis Information Verification",
        "verification_method": "Dataset Similarity Matching",
        "endpoints": {
            "health": "/health",
            "analyze": "/analyze_claim",
            "get_claim": "/claims/{claim_id}",
            "sources": "/sources",
            "stats": "/statistics",
            "info": "/info",
            "docs": "/docs"
        }
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)
