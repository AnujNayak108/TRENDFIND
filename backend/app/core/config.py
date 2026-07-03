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
        extra="ignore"  # Ignore extra fields in .env file
    )
    
    # Application
    APP_NAME: str = "TrendFind"
    DEBUG: bool = False
    
    # MongoDB
    MONGODB_URL: str = "mongodb://localhost:27017"
    DATABASE_NAME: str = "trendfind"
    
    # CORS - can be comma-separated string or JSON array
    CORS_ORIGINS: Union[List[str], str] = ["http://localhost:3000", "http://localhost:5173", "https://trendfind-seven.vercel.app/"]
    
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
    
    # Firecrawl API (optional enrichment)
    FIRECRAWL_API_KEY: str = ""
    FIRECRAWL_API_URL: str = "https://api.firecrawl.dev/v1"
    
    # Scraping intervals
    SCRAPE_INTERVAL_MINUTES: int = 30
    MAX_TRENDS_PER_SOURCE: int = 50
    
    # NLP
    SPACY_MODEL: str = "en_core_web_sm"
    PRODUCT_NAME_SIMILARITY_THRESHOLD: float = 0.85
    
    # Google Trends (free - no API key required)
    GOOGLE_TRENDS_GEO: str = "IN"
    
    # YouTube Data API (free tier - 10,000 units/day)
    YOUTUBE_API_KEY: str = ""
    YOUTUBE_SEARCH_QUERIES: List[str] = [
        "trending products India 2026",
        "best gadgets India",
        "Amazon India sale best deals",
        "Flipkart trending products",
        "best earbuds India",
        "best smartphones India under",
    ]
    
    # Reddit (free - .json endpoints, no API key)
    REDDIT_SUBREDDITS: List[str] = [
        "IndianGaming",
        "india",
        "dealsforindia",
        "indianbeautydeals",
        "HeadphoneIndia",
        "IndianFashionAddicts",
    ]
    REDDIT_MIN_UPVOTES: int = 5
    
    @field_validator('YOUTUBE_SEARCH_QUERIES', mode='before')
    @classmethod
    def parse_youtube_queries(cls, v):
        if isinstance(v, str):
            try:
                return json.loads(v)
            except json.JSONDecodeError:
                return [q.strip() for q in v.split(',') if q.strip()]
        return v
    
    @field_validator('REDDIT_SUBREDDITS', mode='before')
    @classmethod
    def parse_subreddits(cls, v):
        if isinstance(v, str):
            try:
                return json.loads(v)
            except json.JSONDecodeError:
                return [s.strip() for s in v.split(',') if s.strip()]
        return v


settings = Settings()


