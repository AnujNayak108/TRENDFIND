"""
Product Model - Detected and processed products
"""
from __future__ import annotations
from typing import Optional, List, Dict, Any, Union
from datetime import datetime
from pydantic import BaseModel, Field, ConfigDict
from bson import ObjectId
from app.models.base import PyObjectId


class PriceInfo(BaseModel):
    """Price information model"""
    min: Optional[float] = None
    max: Optional[float] = None
    currency: str = Field(default="INR", description="Currency code")


class TrendSource(BaseModel):
    """Source information for a product"""
    trend_id: str = Field(..., description="ID of the trend that mentioned this product")
    source: str = Field(..., description="Source platform")
    mentioned_at: datetime = Field(..., description="When this product was mentioned")


class ProductBase(BaseModel):
    """Base product model"""
    product_name: str = Field(..., description="Name of the product")
    normalized_name: str = Field(..., description="Normalized name for deduplication")
    category: Optional[str] = Field(None, description="Product category")
    short_description: Optional[str] = Field(None, description="Short description of the product")
    image_url: Optional[str] = Field(None, description="Product image URL")
    price: Optional[PriceInfo] = Field(None, description="Price range if available")
    trend_sources: List[TrendSource] = Field(default_factory=list, description="Sources where this product was mentioned")
    trend_score: float = Field(default=0.0, description="Trending score (0-100)")
    tags: List[str] = Field(default_factory=list, description="Product tags")
    firecrawl_data: Optional[Dict[str, Any]] = Field(None, description="Raw Firecrawl response data")


class ProductCreate(ProductBase):
    """Product creation model"""
    pass


class ProductInDB(ProductBase):
    """Product model stored in database"""
    model_config = ConfigDict(
        populate_by_name=True,
        arbitrary_types_allowed=True,
        json_encoders={ObjectId: str}
    )
    id: PyObjectId = Field(default_factory=PyObjectId, alias="_id")
    first_detected_at: datetime = Field(default_factory=datetime.utcnow)
    last_updated_at: datetime = Field(default_factory=datetime.utcnow)


class Product(ProductInDB):
    """Product model for API responses"""
    model_config = ConfigDict(
        populate_by_name=True,  # Allows both _id and id
        arbitrary_types_allowed=True,
        json_encoders={ObjectId: str}
    )


class ProductWithBuyLinks(Product):
    """Product model with associated buy links"""
    model_config = ConfigDict(
        populate_by_name=True,
        arbitrary_types_allowed=True,
        json_encoders={ObjectId: str}
    )
    # Use Any to allow dicts - will be validated/serialized properly
    buy_links: List[Dict[str, Any]] = Field(default_factory=list, description="Buying options for this product")

