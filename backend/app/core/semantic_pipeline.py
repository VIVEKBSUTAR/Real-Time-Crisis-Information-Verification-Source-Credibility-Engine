"""
Semantic Processing Pipeline for Claim Verification

This module implements the core semantic processing steps:
1. Text Normalization
2. User Embedding
3. Similarity Search
4. NLI Input Preparation

Note: Dataset embeddings are precomputed. This module only processes user inputs.
"""

import re
import numpy as np
from typing import List, Dict, Tuple
from sentence_transformers import SentenceTransformer


# Global embedding model (loaded once at startup)
_embedding_model = None


def initialize_embedding_model(model_name: str = "all-MiniLM-L6-v2") -> None:
    """
    Initialize the global embedding model.
    Call this once at application startup.
    
    Args:
        model_name: HuggingFace model identifier
    """
    global _embedding_model
    if _embedding_model is None:
        _embedding_model = SentenceTransformer(model_name)
        print(f"✅ Embedding model initialized: {model_name}")


def get_embedding_model() -> SentenceTransformer:
    """
    Get the global embedding model.
    Ensures model is initialized.
    """
    global _embedding_model
    if _embedding_model is None:
        initialize_embedding_model()
    return _embedding_model


# ============================================================================
# STEP 1: TEXT NORMALIZATION
# ============================================================================

def normalize_text(text: str) -> str:
    """
    Normalize input text for consistent processing.
    
    Steps:
    1. Convert to lowercase
    2. Strip leading/trailing whitespace
    3. Remove extra whitespace (multiple spaces → single space)
    4. Remove special characters (keep basic punctuation)
    5. Remove URLs and email addresses
    
    Args:
        text: Raw input text
        
    Returns:
        Normalized text string
        
    Example:
        "  Bridge COLLAPSED in Pune!!!  " → "bridge collapsed in pune"
    """
    if not isinstance(text, str):
        text = str(text)
    
    # Convert to lowercase
    text = text.lower()
    
    # Strip leading/trailing whitespace
    text = text.strip()
    
    # Remove URLs
    text = re.sub(r'http\S+|www\S+|https\S+', '', text, flags=re.MULTILINE)
    
    # Remove email addresses
    text = re.sub(r'\S+@\S+', '', text)
    
    # Remove special characters (keep alphanumeric, spaces, and basic punctuation)
    # Keep: letters, digits, spaces, periods, commas, question marks, exclamation
    text = re.sub(r'[^a-z0-9\s.,?!]', '', text)
    
    # Remove extra whitespace
    text = re.sub(r'\s+', ' ', text)
    
    # Strip again after processing
    text = text.strip()
    
    return text


# ============================================================================
# STEP 2: USER EMBEDDING
# ============================================================================

def get_embedding(text: str) -> np.ndarray:
    """
    Generate embedding for input text using preloaded model.
    
    Args:
        text: Normalized or raw text (will be used as-is)
        
    Returns:
        numpy array of shape (384,) for all-MiniLM-L6-v2
        
    Raises:
        ValueError: If text is empty after normalization
    """
    if not text or not text.strip():
        raise ValueError("Cannot embed empty text")
    
    model = get_embedding_model()
    
    # Generate embedding (returns list of arrays, we take first)
    embeddings = model.encode([text], convert_to_tensor=False)
    
    # Return as numpy array
    return np.array(embeddings[0], dtype=np.float32)


# ============================================================================
# STEP 3: COSINE SIMILARITY
# ============================================================================

def cosine_similarity(vec1: np.ndarray, vec2: np.ndarray) -> float:
    """
    Compute cosine similarity between two vectors.
    
    Formula: cos(θ) = (A · B) / (||A|| × ||B||)
    
    Args:
        vec1: First vector (numpy array)
        vec2: Second vector (numpy array)
        
    Returns:
        Similarity score in range [0, 1]
        Returns 0.0 if either vector is zero (no similarity)
    """
    # Compute dot product
    dot_product = np.dot(vec1, vec2)
    
    # Compute norms
    norm_vec1 = np.linalg.norm(vec1)
    norm_vec2 = np.linalg.norm(vec2)
    
    # Handle zero division
    if norm_vec1 == 0.0 or norm_vec2 == 0.0:
        return 0.0
    
    # Compute cosine similarity
    similarity = dot_product / (norm_vec1 * norm_vec2)
    
    # Clamp to [0, 1] range (due to floating point errors)
    similarity = float(np.clip(similarity, 0.0, 1.0))
    
    return similarity


# ============================================================================
# STEP 4: TOP-K SIMILARITY SEARCH
# ============================================================================

def get_top_k_similar(
    user_embedding: np.ndarray,
    dataset: List[Dict],
    k: int = 5,
    similarity_threshold: float = 0.4
) -> List[Dict]:
    """
    Find top-K most similar claims from dataset.
    
    Args:
        user_embedding: Embedding vector of user claim
        dataset: List of dataset items with structure:
                {
                    "text": str,
                    "label": str or int,
                    "embedding": np.ndarray
                }
        k: Number of top results to return (will be capped at 10)
        similarity_threshold: Minimum similarity score to include (0.0-1.0)
        
    Returns:
        List of dictionaries with structure:
        [
            {
                "text": str,
                "label": str or int,
                "similarity": float
            },
            ...
        ]
        
    Notes:
        - K is capped at 10 for efficiency
        - Results filtered by similarity_threshold
        - Results sorted in descending similarity order
    """
    # Cap K value
    k = min(k, 10)
    
    if not dataset:
        return []
    
    # Compute similarity scores
    similarities = []
    for item in dataset:
        if "embedding" not in item or item["embedding"] is None:
            continue
        
        similarity = cosine_similarity(
            user_embedding,
            np.array(item["embedding"], dtype=np.float32)
        )
        
        # Apply threshold filter
        if similarity >= similarity_threshold:
                similarities.append({
                    "text": item["text"],
                    "label": item["label"],
                    "similarity": similarity,
                    "source": item.get("source", "dataset"),
                })
    
    # Sort by similarity (descending)
    similarities.sort(key=lambda x: x["similarity"], reverse=True)
    
    # Return top-K
    return similarities[:k]


# ============================================================================
# STEP 5: FILTER LOW-QUALITY MATCHES
# ============================================================================

def filter_similar_results(
    similar_results: List[Dict],
    min_threshold: float = 0.4
) -> List[Dict]:
    """
    Filter out low-quality matches based on similarity threshold.
    
    Args:
        similar_results: List of similarity results
        min_threshold: Minimum similarity score to keep (0.0-1.0)
        
    Returns:
        Filtered list of results (may be shorter than input)
        
    Notes:
        - Prevents noisy/irrelevant matches from entering NLI
        - Maintains original sorting
    """
    filtered = [
        result for result in similar_results
        if result["similarity"] >= min_threshold
    ]
    return filtered


# ============================================================================
# STEP 6: NLI INPUT PREPARATION
# ============================================================================

def prepare_nli_pairs(
    user_text: str,
    similar_results: List[Dict]
) -> List[Dict]:
    """
    Prepare premise-hypothesis pairs for NLI model.
    
    Each pair represents: "Does this dataset claim support the user's claim?"
    
    Args:
        user_text: User's input claim (will be used as hypothesis)
        similar_results: List of similar dataset items with structure:
                        {
                            "text": str,
                            "label": str or int,
                            "similarity": float
                        }
        
    Returns:
        List of NLI input pairs:
        [
            {
                "premise": str,           # Dataset claim
                "hypothesis": str,        # User claim
                "similarity": float,      # Semantic similarity score
                "label": str or int       # Dataset label
            },
            ...
        ]
    """
    nli_pairs = []
    
    for result in similar_results:
        nli_pair = {
            "premise": result["text"],
            "hypothesis": user_text,
            "similarity": result["similarity"],
            "label": result["label"],
            "source": result.get("source", "dataset"),
        }
        nli_pairs.append(nli_pair)
    
    return nli_pairs


# ============================================================================
# MAIN PIPELINE FUNCTION
# ============================================================================

def semantic_pipeline(
    user_claim: str,
    dataset: List[Dict],
    k: int = 5,
    similarity_threshold: float = 0.4
) -> Tuple[List[Dict], Dict]:
    """
    Complete semantic processing pipeline.
    
    Steps:
    1. Normalize user claim
    2. Generate embedding
    3. Search for top-K similar claims
    4. Filter by similarity threshold
    5. Prepare NLI input pairs
    
    Args:
        user_claim: Raw user input claim
        dataset: Preloaded dataset with embeddings
        k: Number of top results (capped at 10)
        similarity_threshold: Minimum similarity score (0.0-1.0)
        
    Returns:
        Tuple of:
        - nli_pairs: List of premise-hypothesis pairs for NLI
        - metadata: Dict with pipeline statistics
        
    Metadata includes:
        {
            "original_claim": str,
            "normalized_claim": str,
            "num_dataset": int,
            "num_similar_found": int,
            "num_passed_threshold": int,
            "num_nli_pairs": int,
            "top_similarity": float or None
        }
    """
    # Step 1: Normalize user claim
    normalized_claim = normalize_text(user_claim)
    
    if not normalized_claim:
        return [], {
            "original_claim": user_claim,
            "normalized_claim": normalized_claim,
            "num_dataset": len(dataset),
            "num_similar_found": 0,
            "num_passed_threshold": 0,
            "num_nli_pairs": 0,
            "top_similarity": None,
            "error": "Claim normalized to empty string"
        }
    
    # Step 2: Generate embedding
    try:
        user_embedding = get_embedding(normalized_claim)
    except Exception as e:
        return [], {
            "original_claim": user_claim,
            "normalized_claim": normalized_claim,
            "num_dataset": len(dataset),
            "num_similar_found": 0,
            "num_passed_threshold": 0,
            "num_nli_pairs": 0,
            "top_similarity": None,
            "error": f"Embedding generation failed: {str(e)}"
        }
    
    # Step 3: Get top-K similar claims
    similar_results = get_top_k_similar(
        user_embedding,
        dataset,
        k=k,
        similarity_threshold=similarity_threshold
    )
    
    num_similar_found = len(similar_results)
    
    # Step 4: Filter by threshold (already done in get_top_k_similar)
    num_passed_threshold = len(similar_results)
    
    # Step 5: Prepare NLI pairs
    nli_pairs = prepare_nli_pairs(user_claim, similar_results)
    
    # Collect metadata
    metadata = {
        "original_claim": user_claim,
        "normalized_claim": normalized_claim,
        "num_dataset": len(dataset),
        "num_similar_found": num_similar_found,
        "num_passed_threshold": num_passed_threshold,
        "num_nli_pairs": len(nli_pairs),
        "top_similarity": similar_results[0]["similarity"] if similar_results else None
    }
    
    return nli_pairs, metadata
