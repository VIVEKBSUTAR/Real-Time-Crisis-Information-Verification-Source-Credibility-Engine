"""
Advanced Semantic Verification Pipeline - Full Workflow
Input → Normalization → Embedding + Clustering → Cluster Signals → 
Trust Score Verification → NLI Reasoning → Decision + Confidence → 
Alert + System → Explanation → Learning(Bayesian Update)

This implements the complete end-to-end workflow with clustering,
trust scoring, alert system, and Bayesian learning.
"""

import numpy as np
from typing import List, Dict, Tuple, Optional
from scipy.cluster.hierarchy import dendrogram, linkage, fcluster
from scipy.spatial.distance import pdist, squareform
import json
from datetime import datetime

# ============================================================================
# STEP 1 & 2: INPUT + NORMALIZATION (Already have these)
# ============================================================================

def normalize_text(text: str) -> str:
    """Normalize text for processing"""
    import re
    if not isinstance(text, str):
        text = str(text)
    
    text = text.lower().strip()
    text = re.sub(r'http\S+|www\S+|@\S+', '', text)
    text = re.sub(r'[^a-z0-9\s\.\,\!\?]', '', text)
    text = re.sub(r'\s+', ' ', text).strip()
    return text


# ============================================================================
# STEP 3: EMBEDDING + CLUSTERING
# ============================================================================

class EmbeddingClusterer:
    """Cluster embeddings to find groups of similar claims"""
    
    def __init__(self, distance_threshold=0.5, min_cluster_size=2):
        """
        Args:
            distance_threshold: Distance threshold for clustering (0-2 range)
            min_cluster_size: Minimum size of a cluster
        """
        self.distance_threshold = distance_threshold
        self.min_cluster_size = min_cluster_size
    
    def cluster_embeddings(self, embeddings: np.ndarray, claim_ids: List) -> Dict:
        """
        Perform hierarchical clustering on embeddings
        
        Args:
            embeddings: N x D array of embeddings
            claim_ids: List of claim identifiers
            
        Returns:
            Dict with clusters and cluster info
        """
        if len(embeddings) < 2:
            return {
                "clusters": {0: list(range(len(embeddings)))},
                "cluster_count": 1,
                "cluster_info": {
                    0: {
                        "size": len(embeddings),
                        "center": embeddings[0] if len(embeddings) > 0 else None,
                        "members": claim_ids
                    }
                }
            }
        
        # Compute pairwise distances
        distances = pdist(embeddings, metric='cosine')
        condensed_matrix = linkage(distances, method='average')
        
        # Perform clustering
        cluster_labels = fcluster(
            condensed_matrix, 
            self.distance_threshold, 
            criterion='distance'
        )
        
        # Group by cluster
        clusters = {}
        for idx, label in enumerate(cluster_labels):
            if label not in clusters:
                clusters[label] = []
            clusters[label].append(idx)
        
        # Filter by minimum cluster size
        filtered_clusters = {
            k: v for k, v in clusters.items() 
            if len(v) >= self.min_cluster_size
        }
        
        # Add singleton items if any
        singleton_cluster_id = max(filtered_clusters.keys()) + 1 if filtered_clusters else 0
        for idx, label in enumerate(cluster_labels):
            if label not in filtered_clusters and idx not in sum(filtered_clusters.values(), []):
                if singleton_cluster_id not in filtered_clusters:
                    filtered_clusters[singleton_cluster_id] = []
                filtered_clusters[singleton_cluster_id].append(idx)
        
        # Create cluster info
        cluster_info = {}
        for cluster_id, member_indices in filtered_clusters.items():
            member_embeddings = embeddings[member_indices]
            center = np.mean(member_embeddings, axis=0)
            
            cluster_info[cluster_id] = {
                "size": len(member_indices),
                "center": center,
                "members": [claim_ids[i] for i in member_indices],
                "density": self._calculate_density(member_embeddings),
                "spread": self._calculate_spread(member_embeddings)
            }
        
        return {
            "clusters": filtered_clusters,
            "cluster_count": len(filtered_clusters),
            "cluster_info": cluster_info
        }
    
    def _calculate_density(self, embeddings: np.ndarray) -> float:
        """Calculate cluster density (inverse of average distance)"""
        if len(embeddings) < 2:
            return 1.0
        distances = pdist(embeddings, metric='cosine')
        return 1.0 / (np.mean(distances) + 0.1)
    
    def _calculate_spread(self, embeddings: np.ndarray) -> float:
        """Calculate cluster spread (variance)"""
        if len(embeddings) < 2:
            return 0.0
        return float(np.var(np.linalg.norm(embeddings, axis=1)))


# ============================================================================
# STEP 4: CLUSTER SIGNALS EXTRACTION
# ============================================================================

class ClusterSignalExtractor:
    """Extract signals/features from clusters"""
    
    def extract_signals(self, cluster_info: Dict, dataset_labels: List) -> Dict:
        """
        Extract features from clusters
        
        Returns signals like:
        - cluster_size (more members = stronger signal)
        - label_consensus (all same label?)
        - density (tightly grouped?)
        - evidence_weight (how much evidence in cluster)
        """
        signals = {}
        
        for cluster_id, info in cluster_info.items():
            cluster_size = info["size"]
            member_labels = dataset_labels  # Would be indexed by member IDs
            
            # Signal 1: Size signal (more evidence = stronger)
            size_signal = min(1.0, cluster_size / 10)  # Saturate at 10 items
            
            # Signal 2: Consensus signal (0-1 based on label agreement)
            # Assume we have labels for comparison
            consensus_signal = 0.5  # Would calculate from actual labels
            
            # Signal 3: Density signal (tight = stronger)
            density_signal = min(1.0, info["density"] / 2)  # Saturate at density=2
            
            # Signal 4: Spread signal (low spread = more coherent)
            spread_signal = max(0.0, 1.0 - info["spread"])
            
            signals[cluster_id] = {
                "size_signal": size_signal,
                "consensus_signal": consensus_signal,
                "density_signal": density_signal,
                "spread_signal": spread_signal,
                "combined_signal": np.mean([
                    size_signal, 
                    consensus_signal, 
                    density_signal, 
                    spread_signal
                ])
            }
        
        return signals


# ============================================================================
# STEP 5: TRUST SCORE VERIFICATION
# ============================================================================

class TrustScoreCalculator:
    """Calculate trust scores based on multiple factors"""
    
    def __init__(self):
        self.source_credibility = {}
        self.claim_age_weights = {}
    
    def calculate_trust_score(
        self,
        cluster_info: Dict,
        cluster_signals: Dict,
        dataset_items: List[Dict]
    ) -> Dict:
        """
        Calculate trust scores combining:
        - Source credibility
        - Corroboration count
        - Cluster consensus
        - Dataset label agreement
        """
        trust_scores = {}
        
        for cluster_id, info in cluster_info.items():
            members = info["members"]
            
            # Factor 1: Corroboration (how many items say same thing)
            corroboration_score = min(1.0, len(members) / 5)
            
            # Factor 2: Dataset label agreement
            label_agreement = self._calculate_label_agreement(members, dataset_items)
            
            # Factor 3: Cluster signal strength
            signal_strength = cluster_signals[cluster_id]["combined_signal"]
            
            # Factor 4: Source diversity
            source_diversity = self._calculate_source_diversity(members, dataset_items)
            
            # Weighted combination
            trust_score = (
                0.3 * corroboration_score +
                0.3 * label_agreement +
                0.2 * signal_strength +
                0.2 * source_diversity
            )
            
            trust_scores[cluster_id] = {
                "score": trust_score,
                "corroboration": corroboration_score,
                "label_agreement": label_agreement,
                "signal_strength": signal_strength,
                "source_diversity": source_diversity
            }
        
        return trust_scores
    
    def _calculate_label_agreement(self, members: List, dataset_items: List[Dict]) -> float:
        """Check if all members have same label"""
        if not members or not dataset_items:
            return 0.5
        
        labels = [dataset_items[m]["label"] for m in members if m < len(dataset_items)]
        if not labels:
            return 0.5
        
        agreement = 1.0 - (np.std(labels) if len(labels) > 1 else 0)
        return float(max(0.0, min(1.0, agreement)))
    
    def _calculate_source_diversity(self, members: List, dataset_items: List[Dict]) -> float:
        """Check diversity of sources"""
        if not members or not dataset_items:
            return 0.5
        
        sources = set()
        for m in members:
            if m < len(dataset_items) and "source" in dataset_items[m]:
                sources.add(dataset_items[m]["source"])
        
        # More sources = higher diversity
        diversity = min(1.0, len(sources) / 3)
        return float(diversity)


# ============================================================================
# STEP 6: NLI REASONING (already have this)
# ============================================================================

def calculate_nli_scores(cluster_info: Dict, user_claim: str) -> Dict:
    """Calculate NLI scores for clusters"""
    nli_scores = {}
    
    for cluster_id, info in cluster_info.items():
        # Mock NLI: word overlap heuristic
        user_words = set(user_claim.lower().split())
        center_vector = info["center"]  # Would use actual NLI model here
        
        # Heuristic: assume cluster center represents the group
        entailment_score = 0.5  # Would use actual NLI model
        contradiction_score = 0.3
        neutral_score = 0.2
        
        nli_scores[cluster_id] = {
            "entailment": entailment_score,
            "contradiction": contradiction_score,
            "neutral": neutral_score
        }
    
    return nli_scores


# ============================================================================
# STEP 7: DECISION + CONFIDENCE
# ============================================================================

class VerdictGenerator:
    """Generate final verdict and confidence"""
    
    def generate_verdict(
        self,
        trust_scores: Dict,
        nli_scores: Dict,
        cluster_info: Dict
    ) -> Dict:
        """Combine all signals into verdict"""
        
        if not trust_scores:
            return {
                "verdict": "UNCERTAIN",
                "confidence": 0.0,
                "reasoning": "No clusters found"
            }
        
        # Aggregate across clusters
        total_entailment = 0
        total_contradiction = 0
        total_weight = 0
        
        for cluster_id, trust_score in trust_scores.items():
            weight = trust_score["score"]
            nli = nli_scores.get(cluster_id, {})
            
            total_entailment += weight * nli.get("entailment", 0.33)
            total_contradiction += weight * nli.get("contradiction", 0.33)
            total_weight += weight
        
        if total_weight == 0:
            return {"verdict": "UNCERTAIN", "confidence": 0.0}
        
        # Normalize
        norm_entailment = total_entailment / total_weight
        norm_contradiction = total_contradiction / total_weight
        
        # Determine verdict
        if norm_entailment > 0.6:
            verdict = "VERIFIED"
            confidence = norm_entailment
        elif norm_contradiction > 0.6:
            verdict = "FALSE"
            confidence = norm_contradiction
        else:
            verdict = "UNCERTAIN"
            confidence = max(norm_entailment, norm_contradiction)
        
        return {
            "verdict": verdict,
            "confidence": min(0.95, confidence),
            "entailment": norm_entailment,
            "contradiction": norm_contradiction
        }


# ============================================================================
# STEP 8: ALERT + SYSTEM
# ============================================================================

class AlertSystem:
    """Generate and route alerts for high-risk claims"""
    
    def generate_alerts(self, verdict: Dict, claim: str) -> List[Dict]:
        """Generate alerts based on verdict"""
        alerts = []
        
        if verdict["verdict"] == "FALSE" and verdict["confidence"] > 0.8:
            alerts.append({
                "alert_type": "HIGH_CONFIDENCE_FALSE",
                "severity": "HIGH",
                "message": f"High-confidence FALSE claim detected: {claim[:100]}...",
                "confidence": verdict["confidence"],
                "timestamp": datetime.now().isoformat(),
                "action": "NOTIFY_ADMINS"
            })
        
        if verdict["verdict"] == "UNCERTAIN" and verdict["confidence"] > 0.7:
            alerts.append({
                "alert_type": "UNCLEAR_CLAIM",
                "severity": "MEDIUM",
                "message": f"Ambiguous claim detected: {claim[:100]}...",
                "confidence": verdict["confidence"],
                "timestamp": datetime.now().isoformat(),
                "action": "FLAG_FOR_REVIEW"
            })
        
        return alerts
    
    def route_alerts(self, alerts: List[Dict]) -> Dict:
        """Route alerts to appropriate systems"""
        routed = {
            "admin_notifications": [],
            "flagged_for_review": [],
            "trending_analysis": [],
            "logged": []
        }
        
        for alert in alerts:
            if alert["action"] == "NOTIFY_ADMINS":
                routed["admin_notifications"].append(alert)
            elif alert["action"] == "FLAG_FOR_REVIEW":
                routed["flagged_for_review"].append(alert)
            
            routed["logged"].append(alert)
        
        return routed


# ============================================================================
# STEP 9: EXPLANATION GENERATION
# ============================================================================

class ExplanationGenerator:
    """Generate human-readable explanations"""
    
    def generate_explanation(
        self,
        verdict: Dict,
        cluster_info: Dict,
        trust_scores: Dict,
        original_claim: str
    ) -> str:
        """Generate detailed explanation"""
        
        explanation = f"""
VERDICT: {verdict['verdict']} (Confidence: {verdict['confidence']:.1%})

ANALYSIS:
- Found {len(cluster_info)} clusters of similar claims
- Aggregate evidence strength: {verdict.get('entailment', 0):.1%}
- Contradiction evidence: {verdict.get('contradiction', 0):.1%}

SUPPORTING EVIDENCE:
"""
        
        for cluster_id, trust_score in list(trust_scores.items())[:3]:
            info = cluster_info.get(cluster_id, {})
            explanation += f"\n  Cluster {cluster_id}:"
            explanation += f"\n    - Size: {info.get('size', 0)} corroborating claims"
            explanation += f"\n    - Trust Score: {trust_score['score']:.2f}"
            explanation += f"\n    - Label Agreement: {trust_score['label_agreement']:.1%}"
        
        return explanation


# ============================================================================
# STEP 10: BAYESIAN LEARNING
# ============================================================================

class BayesianLearner:
    """Learn from feedback using Bayesian updates"""
    
    def __init__(self):
        self.prior_true = 0.5
        self.prior_false = 0.5
        self.likelihood_evidence = {}
    
    def update_from_feedback(
        self,
        predicted_verdict: str,
        true_verdict: str,
        evidence_strength: float
    ):
        """Update priors based on actual outcome"""
        
        # Bayesian update: P(H|E) = P(E|H) * P(H) / P(E)
        
        if predicted_verdict == true_verdict:
            # Correct prediction
            likelihood = 0.8 + (0.2 * evidence_strength)
        else:
            # Incorrect prediction
            likelihood = 0.2 + (0.2 * evidence_strength)
        
        # Update priors
        if true_verdict == "VERIFIED":
            self.prior_true = (likelihood * self.prior_true) / (
                likelihood * self.prior_true + (1 - likelihood) * self.prior_false
            )
            self.prior_false = 1 - self.prior_true
        else:
            self.prior_false = (likelihood * self.prior_false) / (
                likelihood * self.prior_false + (1 - likelihood) * self.prior_true
            )
            self.prior_true = 1 - self.prior_false
    
    def get_current_priors(self) -> Dict:
        """Get current belief state"""
        return {
            "prior_verified": self.prior_true,
            "prior_false": self.prior_false,
            "learning_sample_size": len(self.likelihood_evidence)
        }


# ============================================================================
# MAIN PIPELINE ORCHESTRATOR
# ============================================================================

class AdvancedVerificationPipeline:
    """Complete end-to-end pipeline"""
    
    def __init__(self):
        self.clusterer = EmbeddingClusterer(distance_threshold=0.6)
        self.signal_extractor = ClusterSignalExtractor()
        self.trust_calculator = TrustScoreCalculator()
        self.verdict_generator = VerdictGenerator()
        self.alert_system = AlertSystem()
        self.explanation_gen = ExplanationGenerator()
        self.bayesian_learner = BayesianLearner()
    
    def process_claim(
        self,
        user_claim: str,
        user_embedding: np.ndarray,
        dataset_embeddings: List[np.ndarray],
        dataset_items: List[Dict]
    ) -> Dict:
        """
        Full pipeline: Input → Normalization → Clustering → Trust → 
        NLI → Decision → Alerts → Explanation → Learning
        """
        
        # Step 1-2: Normalize
        normalized_claim = normalize_text(user_claim)
        
        # Step 3: Cluster embeddings
        claim_ids = list(range(len(dataset_embeddings)))
        embedding_matrix = np.array(dataset_embeddings)
        cluster_result = self.clusterer.cluster_embeddings(embedding_matrix, claim_ids)
        cluster_info = cluster_result["cluster_info"]
        
        # Step 4: Extract cluster signals
        cluster_signals = self.signal_extractor.extract_signals(
            cluster_info,
            [item.get("label", 0.5) for item in dataset_items]
        )
        
        # Step 5: Calculate trust scores
        trust_scores = self.trust_calculator.calculate_trust_score(
            cluster_info,
            cluster_signals,
            dataset_items
        )
        
        # Step 6: NLI reasoning
        nli_scores = calculate_nli_scores(cluster_info, user_claim)
        
        # Step 7: Generate verdict
        verdict = self.verdict_generator.generate_verdict(
            trust_scores,
            nli_scores,
            cluster_info
        )
        
        # Step 8: Generate and route alerts
        alerts = self.alert_system.generate_alerts(verdict, user_claim)
        routed_alerts = self.alert_system.route_alerts(alerts)
        
        # Step 9: Generate explanation
        explanation = self.explanation_gen.generate_explanation(
            verdict,
            cluster_info,
            trust_scores,
            user_claim
        )
        
        # Step 10: Bayesian learning readiness (returns priors)
        current_priors = self.bayesian_learner.get_current_priors()
        
        return {
            "input_claim": user_claim,
            "normalized_claim": normalized_claim,
            "clustering": {
                "cluster_count": cluster_result["cluster_count"],
                "clusters": cluster_result["clusters"],
                "cluster_info": cluster_info
            },
            "signals": cluster_signals,
            "trust_scores": trust_scores,
            "nli_scores": nli_scores,
            "verdict": verdict,
            "alerts": routed_alerts,
            "explanation": explanation,
            "bayesian_state": current_priors,
            "pipeline_status": "complete"
        }

