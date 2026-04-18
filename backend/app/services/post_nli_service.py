"""
Post-NLI Logic Service

Aggregates NLI results with semantic similarity and dataset labels
to produce final verdict and confidence scores.

Pipeline:
  NLI Results + Semantic Similarity + Dataset Labels
  → Aggregation Logic
  → Final Verdict (VERIFIED/FALSE/UNCERTAIN)
  → Confidence Score (0.0-1.0)
"""

from typing import List, Dict, Tuple
from collections import Counter
import numpy as np


class PostNLIService:
    """Aggregates NLI and semantic results into final verdict"""
    
    def __init__(self):
        """Initialize post-NLI service with decision thresholds"""
        self.entailment_threshold = 0.5    # For VERIFIED
        self.contradiction_threshold = 0.5 # For FALSE
        self.neutral_threshold = 0.3       # For uncertain matches
    
    def aggregate_results(
        self,
        nli_results: List[Dict],
        use_dataset_labels: bool = True
    ) -> Tuple[str, float]:
        """
        Aggregate multiple NLI results into final verdict.
        
        Args:
            nli_results: List of dicts with:
                {
                    "nli_scores": {...},
                    "similarity": float,
                    "label": str or int (dataset label)
                }
            use_dataset_labels: If True, weight by dataset labels
            
        Returns:
            (verdict: str, confidence: float)
            verdict: "VERIFIED", "FALSE", or "UNCERTAIN"
            confidence: 0.0-1.0
        """
        if not nli_results:
            return "UNCERTAIN", 0.3
        
        # Extract entailment scores weighted by similarity
        entailment_scores = []
        contradiction_scores = []
        neutral_scores = []
        
        for result in nli_results:
            nli_scores = result.get("nli_scores", {})
            similarity = result.get("similarity", 0.5)
            label = result.get("label", 0)
            
            # Weight by semantic similarity
            weight = similarity
            
            # If using dataset labels, adjust weight
            if use_dataset_labels:
                label_int = int(label) if label not in [0, 1] else label
                if label_int == 1:
                    weight *= 1.2  # Boost if dataset says TRUE
                else:
                    weight *= 0.9  # Reduce if dataset says FALSE
            
            # Collect weighted scores
            entailment_scores.append(nli_scores.get("entailment", 0.0) * weight)
            contradiction_scores.append(nli_scores.get("contradiction", 0.0) * weight)
            neutral_scores.append(nli_scores.get("neutral", 0.0) * weight)
        
        # Aggregate by averaging
        avg_entailment = np.mean(entailment_scores) if entailment_scores else 0.0
        avg_contradiction = np.mean(contradiction_scores) if contradiction_scores else 0.0
        avg_neutral = np.mean(neutral_scores) if neutral_scores else 0.0
        
        # Normalize to sum to 1
        total = avg_entailment + avg_contradiction + avg_neutral
        if total > 0:
            avg_entailment /= total
            avg_contradiction /= total
            avg_neutral /= total
        
        # Decision logic
        verdict, confidence = self._decide_verdict(
            avg_entailment,
            avg_contradiction,
            avg_neutral
        )
        
        return verdict, confidence
    
    def _decide_verdict(
        self,
        entailment_score: float,
        contradiction_score: float,
        neutral_score: float
    ) -> Tuple[str, float]:
        """
        Decide verdict based on normalized NLI scores.
        
        Args:
            entailment_score: Score for entailment (0.0-1.0)
            contradiction_score: Score for contradiction (0.0-1.0)
            neutral_score: Score for neutral (0.0-1.0)
            
        Returns:
            (verdict, confidence) tuple
        """
        # Find max score
        max_score = max(entailment_score, contradiction_score, neutral_score)
        
        # Decision thresholds
        if entailment_score > contradiction_score and entailment_score >= self.entailment_threshold:
            return "VERIFIED", entailment_score
        
        elif contradiction_score > entailment_score and contradiction_score >= self.contradiction_threshold:
            return "FALSE", contradiction_score
        
        else:
            # Neutral or uncertain
            return "UNCERTAIN", max_score
    
    def aggregate_with_dataset_voting(
        self,
        nli_results: List[Dict]
    ) -> Tuple[str, float]:
        """
        Aggregate using both NLI scores and dataset label voting.
        
        Args:
            nli_results: List of NLI result dicts
            
        Returns:
            (verdict, confidence) tuple
        """
        if not nli_results:
            return "UNCERTAIN", 0.3
        
        # Extract labels from dataset
        labels = []
        nli_entailments = []
        similarities = []
        
        for result in nli_results:
            labels.append(result.get("label", 0))
            nli_entailments.append(result.get("nli_scores", {}).get("entailment", 0.5))
            similarities.append(result.get("similarity", 0.5))
        
        # Convert labels to boolean (1 = TRUE/VERIFIED, 0 = FALSE)
        label_votes = [int(label) for label in labels]
        
        # Count votes
        true_votes = sum(label_votes)
        false_votes = len(label_votes) - true_votes
        
        # Weighted by NLI entailment and similarity
        true_weight = sum(
            nli_entailments[i] * similarities[i]
            for i in range(len(labels))
            if label_votes[i] == 1
        )
        
        false_weight = sum(
            (1 - nli_entailments[i]) * similarities[i]
            for i in range(len(labels))
            if label_votes[i] == 0
        )
        
        # Determine verdict
        if true_weight > false_weight and true_votes > len(label_votes) * 0.3:
            confidence = min(0.95, true_weight / (len(label_votes) * 0.8))
            return "VERIFIED", confidence
        
        elif false_weight > true_weight and false_votes > len(label_votes) * 0.3:
            confidence = min(0.95, false_weight / (len(label_votes) * 0.8))
            return "FALSE", confidence
        
        else:
            confidence = 0.5
            return "UNCERTAIN", confidence
    
    def format_explanation(
        self,
        user_claim: str,
        nli_results: List[Dict],
        verdict: str,
        confidence: float
    ) -> str:
        """
        Generate human-readable explanation.
        
        Args:
            user_claim: User's input claim
            nli_results: NLI result dicts
            verdict: Final verdict
            confidence: Confidence score
            
        Returns:
            Explanation string
        """
        if not nli_results:
            return "No similar claims found in dataset for comparison."
        
        top_match = nli_results[0] if nli_results else {}
        num_matches = len(nli_results)
        top_similarity = top_match.get("similarity", 0.0)
        top_premise = top_match.get("premise", "Unknown")[:100]
        
        if verdict == "VERIFIED":
            return (
                f"Analysis found {num_matches} similar claim(s) in the dataset. "
                f"Based on NLI evaluation, the claim appears to be VERIFIED. "
                f"Best match: '{top_premise}...' ({int(top_similarity*100)}% similar). "
                f"Confidence: {int(confidence*100)}%"
            )
        
        elif verdict == "FALSE":
            return (
                f"Analysis found {num_matches} similar claim(s) that contradict the input. "
                f"Based on NLI evaluation, the claim appears to be FALSE/MISINFORMATION. "
                f"Contradicting claim: '{top_premise}...' ({int(top_similarity*100)}% similar). "
                f"Confidence: {int(confidence*100)}%"
            )
        
        else:  # UNCERTAIN
            return (
                f"Analysis found {num_matches} partially matching claim(s) with mixed results. "
                f"Based on NLI evaluation, the verdict is UNCERTAIN. "
                f"Requires manual verification. Confidence: {int(confidence*100)}%"
            )


# Singleton instance
post_nli_service = PostNLIService()
