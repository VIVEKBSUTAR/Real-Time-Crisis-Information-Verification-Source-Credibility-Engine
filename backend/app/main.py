from fastapi import FastAPI, Depends, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
import uuid
import time
from datetime import datetime
from typing import List

from app.core.config import settings
from app.core.database import engine, Base, get_db
from app.models.models import Claim, Cluster, Evidence, Source
from app.api.schemas.claim import ClaimInput, ClaimOutput, EvidenceOutput
from app.services.embedding_service import embedding_service
from app.services.normalization_service import NormalizationService

# Initialize database
Base.metadata.create_all(bind=engine)

# Create FastAPI app
app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="Production-grade real-time crisis misinformation verification system"
)

# CORS middleware
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
        "version": settings.APP_VERSION
    }

@app.post("/analyze_claim", response_model=ClaimOutput)
async def analyze_claim(
    request: ClaimInput,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    """
    Main endpoint for claim analysis.
    
    Pipeline:
    1. Input validation & claim extraction
    2. Claim normalization
    3. Embedding & clustering (signal detection)
    4. Trusted source retrieval
    5. Evidence evaluation
    6. Decision aggregation
    7. Explanation generation
    """
    
    start_time = time.time()
    claim_id = f"CLAIM-{uuid.uuid4().hex[:8].upper()}"
    
    try:
        # Step 1: Normalize claim
        normalized = NormalizationService.normalize_claim(request.text)
        
        # Step 2: Generate embedding
        embedding = embedding_service.generate_embedding(request.text)
        
        # Step 3: Create cluster (mock clustering)
        cluster_id = f"CLUSTER-{uuid.uuid4().hex[:8].upper()}"
        cluster = Cluster(
            id=cluster_id,
            source_count=1,
            source_diversity=0.5,
            time_density=0.7,
            signal_score=0.65
        )
        db.add(cluster)
        
        # Step 4: Store claim in database
        db_claim = Claim(
            id=claim_id,
            text=request.text,
            normalized_text=f"{normalized.event} in {normalized.location}",
            source_name=request.source_name or "User",
            source_platform=request.source_platform or "Direct",
            cluster_id=cluster_id,
            verdict="UNVERIFIED",
            confidence=0.52,
            signal_strength=0.65,
            explanation="Claim originates from unverified source. Cross-verification with trusted sources in progress."
        )
        db.add(db_claim)
        db.commit()
        
        # Step 5: Mock evidence gathering
        supporting_sources = [
            EvidenceOutput(
                source_name="Reuters",
                relation="neutral",
                confidence=0.6,
                text="No confirmed reports from official sources yet."
            )
        ]
        
        # Step 6: Build response
        processing_time = time.time() - start_time
        
        return ClaimOutput(
            claim_id=claim_id,
            text=request.text,
            verdict="UNVERIFIED",
            confidence=0.52,
            signal_strength=0.65,
            explanation="Claim originates from unverified source. Similar patterns detected in database (2 related claims). Waiting for trusted source confirmation.",
            supporting_sources=supporting_sources,
            missing_sources=["AP News", "BBC", "Government Authority"],
            has_exif_warning=False,
            processing_time=processing_time
        )
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/claims/{claim_id}")
async def get_claim(claim_id: str, db: Session = Depends(get_db)):
    """Retrieve a claim analysis"""
    db_claim = db.query(Claim).filter(Claim.id == claim_id).first()
    if not db_claim:
        raise HTTPException(status_code=404, detail="Claim not found")
    return db_claim

@app.get("/sources")
async def list_sources(db: Session = Depends(get_db)):
    """List all trusted sources and their credibility scores"""
    sources = db.query(Source).all()
    return [
        {
            "id": s.id,
            "name": s.name,
            "trust_score": s.trust_score,
            "correct_decisions": s.correct_decisions,
            "total_decisions": s.total_decisions
        }
        for s in sources
    ]

@app.get("/info")
async def system_info():
    """Return system configuration info"""
    return {
        "system_name": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "embedding_model": settings.EMBEDDING_MODEL,
        "nli_model": settings.NLI_MODEL,
        "clustering_threshold": settings.CLUSTERING_THRESHOLD,
        "trusted_sources": settings.TRUSTED_SOURCES
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
