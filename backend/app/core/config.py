"""
Application configuration using Pydantic
Compatible with both Pydantic v1 and v2
"""
import os
try:
    from pydantic import BaseSettings
except ImportError:
    from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings from environment variables"""
    
    # App
    APP_NAME: str = "Sentinel Protocol"
    APP_VERSION: str = "0.1.0"
    DEBUG: bool = False
    
    # Database
    DATABASE_URL: str = "sqlite:///./app.db"
    
    # ML Models (optional)
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
        "Associated Press",
        "NPR",
        "The Guardian",
        "NYTimes",
        "Washington Post"
    ]
    
    class Config:
        env_file = ".env"
        case_sensitive = True
        extra = "allow"


# Create settings instance - ignore any external DEBUG env var
os.environ.pop('DEBUG', None)
settings = Settings()
