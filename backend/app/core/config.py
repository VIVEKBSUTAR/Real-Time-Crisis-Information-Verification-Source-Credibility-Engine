from pydantic import BaseSettings
from typing import Optional

class Settings(BaseSettings):
    """Application settings from environment variables"""
    
    # App
    APP_NAME: str = "Sentinel Protocol"
    APP_VERSION: str = "0.1.0"
    DEBUG: bool = True
    
    # Database
    DATABASE_URL: str = "sqlite:///./sentinel.db"
    
    # Vector DB (Qdrant)
    QDRANT_HOST: str = "localhost"
    QDRANT_PORT: int = 6333
    QDRANT_COLLECTION_NAME: str = "sentinel_claims"
    
    # ML Models
    EMBEDDING_MODEL: str = "sentence-transformers/multilingual-MiniLM-L6-v2"
    NLI_MODEL: str = "facebook/bart-large-mnli"
    
    # Thresholds
    CLUSTERING_THRESHOLD: float = 0.85
    SIGNAL_THRESHOLD: float = 0.6
    CONFIDENCE_THRESHOLD: float = 0.7
    
    # Trusted Sources
    TRUSTED_SOURCES: list = [
        "Reuters",
        "AP News", 
        "BBC",
        "Press Information Bureau",
        "News18",
        "The Hindu",
        "NDTV",
        "India Today"
    ]
    
    # Processing
    EMBEDDING_BATCH_SIZE: int = 32
    MAX_PROCESSING_TIME: int = 30  # seconds
    
    class Config:
        env_file = ".env"
        case_sensitive = True

settings = Settings()
