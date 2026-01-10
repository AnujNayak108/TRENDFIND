"""
Buy Link Model - E-commerce buying options
"""
from typing import Optional, Dict, Any
from datetime import datetime
from pydantic import BaseModel, Field, ConfigDict
from bson import ObjectId
from app.models.base import PyObjectId


class BuyLinkBase(BaseModel):
    """Base buy link model"""
    product_id: str = Field(..., description="Associated product ID")
    platform: str = Field(..., description="E-commerce platform (amazon, ebay, etc.)")
    url: str = Field(..., description="Product URL on the platform")
    title: Optional[str] = Field(None, description="Product title on the platform")
    price: Optional[float] = Field(None, description="Product price")
    currency: str = Field(default="USD", description="Currency code")
    availability: Optional[str] = Field(None, description="Availability status")
    rating: Optional[float] = Field(None, description="Product rating")
    review_count: Optional[int] = Field(None, description="Number of reviews")
    metadata: Optional[Dict[str, Any]] = Field(default_factory=dict, description="Additional platform-specific metadata")


class BuyLinkCreate(BuyLinkBase):
    """Buy link creation model"""
    pass


class BuyLinkInDB(BuyLinkBase):
    """Buy link model stored in database"""
    model_config = ConfigDict(
        populate_by_name=True,
        arbitrary_types_allowed=True,
        json_encoders={ObjectId: str}
    )
    id: PyObjectId = Field(default_factory=PyObjectId, alias="_id")
    scraped_at: datetime = Field(default_factory=datetime.utcnow)
    last_verified: datetime = Field(default_factory=datetime.utcnow)


class BuyLink(BuyLinkInDB):
    """Buy link model for API responses"""
    pass

