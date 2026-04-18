from pydantic import BaseModel
from datetime import datetime
from typing import Optional, List

class ClaimInput(BaseModel):
    """Input schema for claim submission"""
    text: str
    source_name: Optional[str] = None
    source_platform: Optional[str] = None
    url: Optional[str] = None

class EvidenceOutput(BaseModel):
    """Output schema for evidence"""
    source_name: str
    relation: str  # support, contradict, neutral
    confidence: float
    text: str

class ClaimOutput(BaseModel):
    """Output schema for claim analysis"""
    claim_id: str
    text: str
    verdict: str  # TRUE, FALSE, UNCERTAIN
    confidence: float
    signal_strength: float
    explanation: str
    supporting_sources: List[EvidenceOutput]
    missing_sources: List[str]
    has_exif_warning: bool
    processing_time: float

class NormalizedClaim(BaseModel):
    """Normalized claim structure"""
    event: str
    location: str
    time_reference: str
    entities: dict
