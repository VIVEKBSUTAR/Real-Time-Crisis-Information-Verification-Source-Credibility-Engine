from datetime import datetime
from app.api.schemas.claim import NormalizedClaim

class NormalizationService:
    """Normalizes raw claims into structured format"""
    
    @staticmethod
    def normalize_claim(raw_claim: str) -> NormalizedClaim:
        """
        Convert raw claim text to normalized structure.
        In production, this would use LLM-based NER.
        For now, using simple heuristics.
        """
        
        # Simple entity extraction (mock)
        # In production: use spaCy + LLM
        
        claim_lower = raw_claim.lower()
        
        # Time detection
        time_ref = "recent"
        if "now" in claim_lower or "today" in claim_lower:
            time_ref = "immediate"
        elif "yesterday" in claim_lower:
            time_ref = "24h"
        elif "week" in claim_lower:
            time_ref = "7d"
        
        # Location extraction (mock)
        locations = ["pune", "mumbai", "delhi", "bangalore", "chennai", "hyderabad"]
        location = "unknown"
        for loc in locations:
            if loc in claim_lower:
                location = loc.title()
                break
        
        # Event extraction (mock)
        events = ["collapse", "fall", "accident", "outbreak", "fire", "flood"]
        event = "incident"
        for evt in events:
            if evt in claim_lower:
                event = evt.title()
                break
        
        return NormalizedClaim(
            event=event,
            location=location,
            time_reference=time_ref,
            entities={"raw_claim": raw_claim}
        )
