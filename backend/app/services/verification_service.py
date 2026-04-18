"""
Verification Service for Sentinel Protocol
Implements core verification logic using dataset
"""
from sqlalchemy.orm import Session
from sqlalchemy import func
from app.models.models import Claim, Evidence, ClusterDB
from typing import Dict, List, Optional, Tuple
import difflib


class VerificationService:
    """Professional verification service using dataset search"""

    def __init__(self, db: Session):
        self.db = db
        self.min_similarity = 0.6

    def analyze_claim(self, content: str) -> Dict:
        """
        Analyze a claim using dataset verification
        
        Returns:
            Dict with label, confidence, explanation, sources
        """
        # Normalize input
        content = content.strip().lower()
        if len(content) < 5:
            return self._create_response(
                label='UNVERIFIED',
                confidence=0.0,
                explanation='Claim too short for analysis',
                sources=[],
                sources_checked=0
            )

        # Search dataset
        matches = self._search_dataset(content)
        
        if not matches:
            return self._create_response(
                label='UNVERIFIED',
                confidence=0.3,
                explanation='No matching claims found in dataset. Unable to verify at this time.',
                sources=[],
                sources_checked=0
            )

        # Aggregate results
        label, confidence = self._aggregate_matches(matches)
        explanation = self._generate_explanation(content, matches, label, confidence)
        
        return self._create_response(
            label=label,
            confidence=confidence,
            explanation=explanation,
            sources=self._format_sources(matches),
            sources_checked=len(matches)
        )

    def _search_dataset(self, query: str, limit: int = 10) -> List[Dict]:
        """
        Search dataset for similar claims using similarity matching
        """
        try:
            # Get all claims from database (for initial phase - can be optimized with embeddings)
            all_claims = self.db.query(Claim).limit(1000).all()
            
            matches = []
            for claim in all_claims:
                similarity = self._calculate_similarity(query, claim.text.lower())
                if similarity >= self.min_similarity:
                    matches.append({
                        'text': claim.text,
                        'label': claim.label,
                        'confidence': claim.confidence,
                        'similarity': similarity,
                        'explanation': claim.explanation
                    })
            
            # Sort by similarity
            matches = sorted(matches, key=lambda x: x['similarity'], reverse=True)[:limit]
            return matches
            
        except Exception as e:
            print(f"Search error: {e}")
            return []

    def _calculate_similarity(self, text1: str, text2: str) -> float:
        """
        Calculate similarity between two texts using SequenceMatcher
        Returns value between 0 and 1
        """
        return difflib.SequenceMatcher(None, text1, text2).ratio()

    def _aggregate_matches(self, matches: List[Dict]) -> Tuple[str, float]:
        """
        Aggregate multiple matches into a single verdict
        
        Returns:
            (label: 'TRUE'/'FALSE'/'UNVERIFIED', confidence: float 0-1)
        """
        if not matches:
            return 'UNVERIFIED', 0.3

        # Count labels
        true_count = sum(1 for m in matches if m['label'] == 'TRUE')
        false_count = sum(1 for m in matches if m['label'] == 'FALSE')
        total = len(matches)

        # Weighted by similarity
        weighted_true = sum(m['similarity'] * m['confidence'] for m in matches if m['label'] == 'TRUE')
        weighted_false = sum(m['similarity'] * m['confidence'] for m in matches if m['label'] == 'FALSE')

        # Decision logic
        if weighted_true > weighted_false and true_count > total * 0.4:
            confidence = min(0.95, weighted_true / (total * 0.8))
            return 'TRUE', confidence
        elif weighted_false > weighted_true and false_count > total * 0.4:
            confidence = min(0.95, weighted_false / (total * 0.8))
            return 'FALSE', confidence
        else:
            confidence = max(0.3, (weighted_true + weighted_false) / (total * 1.6))
            return 'UNVERIFIED', confidence

    def _generate_explanation(
        self, 
        query: str, 
        matches: List[Dict], 
        label: str, 
        confidence: float
    ) -> str:
        """Generate human-readable explanation"""
        
        if not matches:
            return "No matching claims found in database for comparison."

        match_count = len(matches)
        best_match = matches[0] if matches else None
        
        if label == 'TRUE':
            return (f"Analysis found {match_count} similar claim(s) in the dataset "
                   f"predominantly marked as TRUE. Highest confidence match: "
                   f"\"{best_match['text'][:100]}...\" with "
                   f"{int(best_match['similarity'] * 100)}% similarity. "
                   f"Overall confidence: {int(confidence * 100)}%")
        
        elif label == 'FALSE':
            return (f"Analysis found {match_count} similar claim(s) marked as FALSE. "
                   f"The claim appears to be related to known misinformation. "
                   f"Best match: \"{best_match['text'][:100]}...\" "
                   f"({int(best_match['similarity'] * 100)}% similar). "
                   f"Confidence: {int(confidence * 100)}%")
        
        else:  # UNVERIFIED
            return (f"Found {match_count} partial match(es) with mixed verdicts. "
                   f"Claim is partially related to known information but "
                   f"lacks strong corroboration. Recommendation: Requires manual review. "
                   f"Confidence: {int(confidence * 100)}%")

    def _format_sources(self, matches: List[Dict]) -> List[Dict]:
        """Format matches for API response"""
        sources = []
        for match in matches[:3]:  # Return top 3
            sources.append({
                'name': 'Dataset Match',
                'quote': match['text'][:120] + ('...' if len(match['text']) > 120 else ''),
                'label': match['label'],
                'similarity': match['similarity']
            })
        return sources

    def _create_response(
        self,
        label: str,
        confidence: float,
        explanation: str,
        sources: List[Dict],
        sources_checked: int
    ) -> Dict:
        """Create standardized API response"""
        return {
            'label': label,
            'confidence': min(1.0, max(0.0, confidence)),  # Clamp 0-1
            'explanation': explanation,
            'supporting_sources': [s for s in sources if s.get('label') == 'TRUE'][:2],
            'missing_sources': ['No contradicting sources found'] if not any(s.get('label') == 'FALSE' for s in sources) else [s for s in sources if s.get('label') == 'FALSE'][:2],
            'sources_checked': sources_checked,
            'method': 'dataset_matching'
        }
