# Sentinel Protocol Backend

Real-time crisis misinformation verification engine using layered intelligence.

## Architecture

```
User Input
    ↓
Claim Extraction & Normalization
    ↓
Embedding + Clustering (Signal Detection)
    ↓
Trusted Source Retrieval
    ↓
Evidence Evaluation (NLI)
    ↓
Multi-Source Aggregation
    ↓
Decision Engine (TRUE/FALSE/UNCERTAIN + confidence)
    ↓
Explanation Generator
    ↓
Temporal Tracking
    ↓
(Async) Bayesian Credibility Updates
```

## Components

- **Embedding Service**: sentence-transformers for multilingual embeddings
- **Clustering**: Signal detection via vector similarity
- **Evidence Eval**: NLI model for claim-source relationships
- **Decision Engine**: Weighted aggregation with Bayesian credibility
- **API**: FastAPI with async processing

## Quick Start

```bash
# Install dependencies
pip install -r requirements.txt

# Run server
./run.sh

# Or directly with uvicorn
uvicorn app.main:app --reload
```

API available at: http://localhost:8000
Docs at: http://localhost:8000/docs

## API Endpoints

### POST /analyze_claim
Analyze a claim and return verdict + evidence.

**Request:**
```json
{
  "text": "Bridge collapsed in Pune",
  "source_name": "Twitter",
  "source_platform": "twitter"
}
```

**Response:**
```json
{
  "claim_id": "CLAIM-abc123",
  "verdict": "UNVERIFIED",
  "confidence": 0.52,
  "explanation": "...",
  "supporting_sources": [],
  "missing_sources": [],
  "processing_time": 0.847
}
```

### GET /health
System health check.

### GET /sources
List all trusted sources and credibility scores.

### GET /info
System configuration info.

## Database Schema

- **claims**: Submitted claims + verdicts
- **clusters**: Groups of similar claims
- **sources**: Trusted sources + trust scores  
- **evidence**: Source evidence for claims
- **temporal_events**: Claim evolution over time
- **credibility_updates**: Bayesian updates history

## Configuration

Edit `.env` for:
- Database connection
- Model selection
- Threshold tuning
- Trusted sources list

## Development

```bash
# Run tests
pytest tests/

# Code formatting
black app/
isort app/

# Linting
flake8 app/
```

## Production Deployment

```bash
# Build Docker image
docker build -t sentinel-backend .

# Run with PostgreSQL + Redis
docker-compose up
```

## Architecture Decisions

1. **FastAPI**: Async-first, automatic OpenAPI docs
2. **SQLAlchemy**: ORM with PostgreSQL support
3. **sentence-transformers**: Multilingual, lightweight
4. **Qdrant**: Vector DB alternative to Pinecone
5. **Pydantic**: Strict validation + serialization

## Next Steps

- [ ] Integrate real trusted source RSS feeds
- [ ] Implement NLI evidence evaluation
- [ ] Add Qdrant vector DB for clustering
- [ ] Implement Bayesian credibility updates
- [ ] Add WebSocket for real-time alerts
- [ ] Deploy to production
