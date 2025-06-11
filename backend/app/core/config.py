from pydantic_settings import BaseSettings
from typing import Optional

class Settings(BaseSettings):
    # Database configuration
    DATABASE_URL: str = "postgresql://openmnd_user:openmnd_password@localhost:5432/openmnd_research"
    ELASTICSEARCH_URL: str = "http://localhost:9200"
    REDIS_URL: str = "redis://localhost:6379"
    SECRET_KEY: str = "your-secret-key-change-in-production"
    PUBMED_API_KEY: Optional[str] = None
    
    # OpenMND specific settings
    PROJECT_NAME: str = "OpenMND"
    PROJECT_DESCRIPTION: str = "Open Motor Neuron Disease Research Intelligence Platform"
    VERSION: str = "1.0.0"
    
    class Config:
        env_file = ".env"

settings = Settings()
