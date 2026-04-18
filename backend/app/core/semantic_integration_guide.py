"""
Integration guide for the Semantic Processing Pipeline

This module shows how to integrate the pipeline into the FastAPI server.
"""

# ============================================================================
# USAGE EXAMPLE IN FASTAPI ENDPOINT
# ============================================================================

"""
from fastapi import FastAPI, HTTPException
from app.core.semantic_pipeline import (
    initialize_embedding_model,
    semantic_pipeline
)
from app.dataset_loader import load_dataset

# Initialize at startup
app = FastAPI()

@app.on_event("startup")
async def startup():
    # Initialize embedding model ONCE
    initialize_embedding_model("all-MiniLM-L6-v2")
    
    # Load dataset with precomputed embeddings
    global dataset
    dataset = load_dataset()  # Should have embeddings already

# Use in endpoint
@app.post("/analyze_claim")
async def analyze_claim(request: dict):
    user_claim = request.get("text")
    
    if not user_claim:
        raise HTTPException(status_code=400, detail="Claim text required")
    
    # Step 1-4: Semantic processing pipeline
    nli_pairs, metadata = semantic_pipeline(
        user_claim=user_claim,
        dataset=dataset,
        k=5,
        similarity_threshold=0.4
    )
    
    if "error" in metadata:
        raise HTTPException(status_code=400, detail=metadata["error"])
    
    # Step 5: Pass to NLI model (already implemented elsewhere)
    nli_results = nli_model.predict(nli_pairs)  # Your NLI implementation
    
    # Step 6: Post-NLI logic (already implemented elsewhere)
    final_verdict = post_nli_logic(nli_results, metadata)
    
    return {
        "original_claim": user_claim,
        "normalized_claim": metadata["normalized_claim"],
        "verdict": final_verdict,
        "semantic_matches": len(nli_pairs),
        "top_similarity": metadata["top_similarity"]
    }
"""

# ============================================================================
# DATASET STRUCTURE REQUIRED
# ============================================================================

"""
Your dataset must have this structure after loading:

[
    {
        "text": "Bridge collapsed in Pune yesterday",
        "label": 0,  # or "false" / "False"
        "embedding": np.ndarray of shape (384,)
    },
    {
        "text": "Dam burst in Maharashtra reported",
        "label": 1,  # or "true" / "True"
        "embedding": np.ndarray of shape (384,)
    },
    ...
]

The 'embedding' field MUST be precomputed and already in the dataset.
This pipeline will NOT recompute it.
"""

# ============================================================================
# PERFORMANCE CHARACTERISTICS
# ============================================================================

"""
Pipeline Timing (per claim):

1. Text Normalization:     ~1-2 ms
2. Embedding generation:   ~50-100 ms (SentenceTransformer)
3. Similarity Search:      ~10-20 ms (for 26K dataset)
4. Filtering:              ~1-2 ms
5. NLI Preparation:        ~1-2 ms

Total: ~65-125 ms per claim (well under 3s target)

Memory:
- Embedding model: ~110 MB (loaded once)
- Per-claim overhead: minimal
- No dataset recomputation
"""

# ============================================================================
# CONFIGURATION PARAMETERS
# ============================================================================

"""
Tunable parameters:

1. similarity_threshold (0.4 default):
   - Lower: More matches but noisier
   - Higher: Fewer matches but higher quality
   - Recommended: 0.4-0.5

2. k (5 default):
   - Number of top results to return
   - Higher: More context but slower NLI
   - Recommended: 3-5

3. Embedding Model:
   - "all-MiniLM-L6-v2": Fast (~110MB), 384-dim, balanced
   - "all-mpnet-base-v2": Better quality (~420MB), 768-dim, slower
   - Default recommendation: all-MiniLM-L6-v2
"""

# ============================================================================
# ERROR HANDLING
# ============================================================================

"""
Pipeline can fail on:

1. Empty input: Returns empty NLI pairs + error metadata
2. Invalid UTF-8: normalize_text handles gracefully
3. Model not initialized: Auto-initializes on first use
4. Dataset empty: Returns empty results gracefully
5. Embedding generation: Catches and returns error in metadata

All errors are non-blocking. Pipeline always returns metadata with error field.
"""

# ============================================================================
# TESTING THE PIPELINE
# ============================================================================

"""
import numpy as np
from app.core.semantic_pipeline import (
    normalize_text,
    get_embedding,
    cosine_similarity,
    semantic_pipeline,
    initialize_embedding_model
)

# Initialize
initialize_embedding_model()

# Test normalization
claim = "  Bridge COLLAPSED in Pune!!!  "
normalized = normalize_text(claim)
print(f"Normalized: {normalized}")
# Output: "bridge collapsed in pune"

# Test embedding
emb1 = get_embedding("bridge collapsed")
print(f"Embedding shape: {emb1.shape}")
# Output: Embedding shape: (384,)

# Test similarity
emb2 = get_embedding("bridge fell down")
sim = cosine_similarity(emb1, emb2)
print(f"Similarity: {sim:.3f}")
# Output: Similarity: 0.8+ (high, semantically similar)

# Test full pipeline
dataset = [
    {
        "text": "bridge collapsed in pune",
        "label": 0,
        "embedding": get_embedding("bridge collapsed in pune")
    },
    {
        "text": "dam burst in maharashtra",
        "label": 1,
        "embedding": get_embedding("dam burst in maharashtra")
    }
]

nli_pairs, metadata = semantic_pipeline(
    user_claim="bridge fell in pune",
    dataset=dataset,
    k=5,
    similarity_threshold=0.4
)

print(f"NLI pairs generated: {len(nli_pairs)}")
print(f"Top similarity: {metadata['top_similarity']:.3f}")
"""
