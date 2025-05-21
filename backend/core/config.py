import os
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    """Application settings"""
    
    # API settings
    API_V1_STR: str = "/api"
    PROJECT_NAME: str = "Rock Fragment Analysis"
    
    # Model settings
    MODEL_CONFIG_PATH: str = os.getenv("MODEL_CONFIG_PATH", "/app/model/mask_rcnn_R_50_FPN_3x.yaml")
    MODEL_WEIGHTS_PATH: str = os.getenv("MODEL_WEIGHTS_PATH", "/app/model/model_final.pth")
    SCORE_THRESHOLD: float = 0.5
    
    # Celery settings
    CELERY_BROKER_URL: str = os.getenv("CELERY_BROKER_URL", "redis://redis:6379/0")
    CELERY_RESULT_BACKEND: str = os.getenv("CELERY_RESULT_BACKEND", "redis://redis:6379/0")
    
    # CDF settings
    PIXEL_SIZE_MM: float = 3.0  # Size of one pixel in mm
    
    class Config:
        case_sensitive = True

# Create settings instance
settings = Settings()
