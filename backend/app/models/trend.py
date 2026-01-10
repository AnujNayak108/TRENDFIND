"""
Trend Model - Raw trending topics from social media
"""
from typing import Optional, Dict, Any
from datetime import datetime
from pydantic import BaseModel, Field, ConfigDict
from bson import ObjectId
from app.models.base import PyObjectId


class TrendBase(BaseModel):
    """Base trend model"""
    source: str = Field(..., description="Source platform (google_trends, youtube, instagram, etc.)")
    source_url: str = Field(..., description="URL of the original post/video/trend")
    title: str = Field(..., description="Title of the trend")
    content: Optional[str] = Field(None, description="Full content of the post/video/trend")
    subreddit: Optional[str] = Field(None, description="Subreddit name (legacy field, kept for compatibility)")
    upvotes: Optional[int] = Field(0, description="Number of upvotes/likes")
    comments: Optional[int] = Field(0, description="Number of comments")
    created_at: datetime = Field(..., description="When the trend was created on source platform")
    processed: bool = Field(False, description="Whether this trend has been processed for products")
    metadata: Optional[Dict[str, Any]] = Field(default_factory=dict, description="Additional metadata")


class TrendCreate(TrendBase):
    """Trend creation model"""
    pass


class TrendInDB(TrendBase):
    """Trend model stored in database"""
    model_config = ConfigDict(
        populate_by_name=True,
        arbitrary_types_allowed=True,
        json_encoders={ObjectId: str}
    )
    id: PyObjectId = Field(default_factory=PyObjectId, alias="_id")
    scraped_at: datetime = Field(default_factory=datetime.utcnow, description="When this trend was scraped")


class Trend(TrendInDB):
    """Trend model for API responses"""
    pass

