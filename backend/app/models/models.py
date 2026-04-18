from sqlalchemy import Column, String, Float, Integer, DateTime, Text, Boolean, ForeignKey, JSON
from sqlalchemy.orm import relationship
from datetime import datetime
from app.core.database import Base

class Claim(Base):
    """Represents a single claim to be verified"""
    __tablename__ = "claims"
    
    id = Column(String, primary_key=True)
    text = Column(Text, nullable=False)
    normalized_text = Column(Text)
    source_name = Column(String)
    source_platform = Column(String)
    timestamp = Column(DateTime, default=datetime.utcnow)
    
    # Clustering
    cluster_id = Column(String, ForeignKey("clusters.id"))
    
    # Analysis Results
    verdict = Column(String, default="PENDING")  # TRUE, FALSE, UNCERTAIN, PENDING
    confidence = Column(Float, default=0.0)
    signal_strength = Column(Float, default=0.0)
    explanation = Column(Text)
    
    # Metadata
    has_exif_warning = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    cluster = relationship("Cluster", back_populates="claims")
    evidence = relationship("Evidence", back_populates="claim")
    temporal_events = relationship("TemporalEvent", back_populates="claim")
    
class Cluster(Base):
    """Groups similar claims together"""
    __tablename__ = "clusters"
    
    id = Column(String, primary_key=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Signal Metrics
    source_count = Column(Integer, default=0)
    source_diversity = Column(Float, default=0.0)
    time_density = Column(Float, default=0.0)
    signal_score = Column(Float, default=0.0)
    
    # Metadata
    sources_json = Column(JSON, default=[])  # List of source names/platforms
    
    # Relationships
    claims = relationship("Claim", back_populates="cluster")

class Source(Base):
    """Trusted sources for evidence gathering"""
    __tablename__ = "sources"
    
    id = Column(String, primary_key=True)
    name = Column(String, unique=True)
    url = Column(String)
    type = Column(String)  # news_agency, official, research, etc.
    
    # Credibility Tracking
    trust_score = Column(Float, default=0.5)  # 0-1 scale
    total_decisions = Column(Integer, default=0)
    correct_decisions = Column(Integer, default=0)
    
    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow)
    last_updated = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    evidence = relationship("Evidence", back_populates="source")
    credibility_history = relationship("CredibilityUpdate", back_populates="source")

class Evidence(Base):
    """Evidence from trusted sources for a claim"""
    __tablename__ = "evidence"
    
    id = Column(String, primary_key=True)
    claim_id = Column(String, ForeignKey("claims.id"))
    source_id = Column(String, ForeignKey("sources.id"))
    
    # Evidence Details
    source_text = Column(Text)
    relation = Column(String)  # support, contradict, neutral
    confidence = Column(Float)  # 0-1 score
    
    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    claim = relationship("Claim", back_populates="evidence")
    source = relationship("Source", back_populates="evidence")

class TemporalEvent(Base):
    """Tracks evolution of a claim over time"""
    __tablename__ = "temporal_events"
    
    id = Column(String, primary_key=True)
    claim_id = Column(String, ForeignKey("claims.id"))
    
    event_type = Column(String)  # signal, confirmation, update, ground_truth
    timestamp = Column(DateTime, default=datetime.utcnow)
    
    # Event Details
    metadata_json = Column(JSON)  # Flexible event-specific data
    
    # Relationships
    claim = relationship("Claim", back_populates="temporal_events")

class CredibilityUpdate(Base):
    """Bayesian credibility updates for sources"""
    __tablename__ = "credibility_updates"
    
    id = Column(String, primary_key=True)
    source_id = Column(String, ForeignKey("sources.id"))
    
    # Update Details
    previous_score = Column(Float)
    new_score = Column(Float)
    accuracy = Column(Boolean)  # True if source was correct
    
    # Metadata
    claim_id = Column(String)  # Reference to what was verified
    timestamp = Column(DateTime, default=datetime.utcnow)
    reason = Column(Text)  # Why score was updated
    
    # Relationships
    source = relationship("Source", back_populates="credibility_history")
