"""
Application Configuration
"""
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import field_validator
from typing import List, Union
import json


class Settings(BaseSettings):
    """Application settings loaded from environment variables"""
    
    model_config = SettingsConfigDict(
        env_file=".env",
        case_sensitive=True,
        env_parse_none_str="None",
        extra="ignore"  # Ignore extra fields in .env file (like old Reddit/Twitter configs)
    )
    
    # Application
    APP_NAME: str = "TrendFind"
    DEBUG: bool = False
    
    # MongoDB
    MONGODB_URL: str = "mongodb://localhost:27017"
    DATABASE_NAME: str = "trendfind"
    
    # CORS - can be comma-separated string or JSON array
    CORS_ORIGINS: Union[List[str], str] = ["http://localhost:3000", "https://trendfind-seven.vercel.app/"]
    
    @field_validator('CORS_ORIGINS', mode='before')
    @classmethod
    def parse_cors_origins(cls, v):
        if isinstance(v, str):
            # Try to parse as JSON first
            try:
                return json.loads(v)
            except json.JSONDecodeError:
                # If not JSON, split by comma
                return [origin.strip() for origin in v.split(',') if origin.strip()]
        return v
    
    # Firecrawl API
    FIRECRAWL_API_KEY: str = ""
    FIRECRAWL_API_URL: str = "https://api.firecrawl.dev/v1"
    
    # Scraping
    SCRAPE_INTERVAL_MINUTES: int = 60
    MAX_TRENDS_PER_SOURCE: int = 50
    
    # NLP
    SPACY_MODEL: str = "en_core_web_sm"
    PRODUCT_NAME_SIMILARITY_THRESHOLD: float = 0.85
    
    # Google Trends (no API key required - completely free)
    # Uses pytrends library
    
    # YouTube Data API (optional - free tier available)
    YOUTUBE_API_KEY: str = ""
    
    # Instagram (mock data - API access is restricted)
    # For production, consider using Instagram Basic Display API


settings = Settings()

