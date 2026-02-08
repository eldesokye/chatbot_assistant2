import os
from typing import Optional
from pydantic_settings import BaseSettings
from dotenv import load_dotenv

load_dotenv()

class Settings(BaseSettings):
    """Application settings"""
    
    # Backend Configuration
    BACKEND_API_URL: str = os.getenv("BACKEND_API_URL", "http://localhost:8000")
    
    # LLM Configuration
    OPENAI_API_KEY: Optional[str] = os.getenv("OPENAI_API_KEY")
    OPENROUTER_API_KEY: Optional[str] = os.getenv("OPENROUTER_API_KEY")
    OPENROUTER_BASE_URL: str = os.getenv("OPENROUTER_BASE_URL", "https://openrouter.ai/api/v1")
    
    # Chatbot Configuration
    CHATBOT_NAME: str = os.getenv("CHATBOT_NAME", "RetailAnalyst")
    CHATBOT_TEMPERATURE: float = float(os.getenv("CHATBOT_TEMPERATURE", 0.1))
    MAX_RETRIES: int = int(os.getenv("MAX_RETRIES", 3))
    REQUEST_TIMEOUT: int = int(os.getenv("REQUEST_TIMEOUT", 30))
    
    # Model Selection
    MODEL_NAME: str = "gpt-3.5-turbo"
    
    # Feature Flags
    ENABLE_VISUALIZATIONS: bool = True
    ENABLE_VOICE_INPUT: bool = False
    ENABLE_HISTORY_EXPORT: bool = True
    
    # API Endpoints
    API_ENDPOINTS: dict = {
        "health": "/health",
        "visitors_current": "/api/visitors/current",
        "visitors_sections": "/api/visitors/sections",
        "cashier_current": "/api/cashier/current",
        "cashier_history": "/api/cashier/history",
        "cashier_wait_time": "/api/cashier/wait-time",
        "heatmap": "/api/heatmap/",
        "predictions": "/api/predictions/",
        "daily_analytics": "/api/visitors/analytics/daily"
    }
    
    class Config:
        env_file = ".env"

settings = Settings()