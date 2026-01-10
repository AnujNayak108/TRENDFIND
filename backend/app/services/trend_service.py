"""
Trend Service - Database operations for trends
"""
from typing import List, Optional
from datetime import datetime
from bson import ObjectId
from app.core.database import get_database
from app.models.trend import Trend, TrendCreate, TrendInDB


class TrendService:
    """Service for managing trends in the database"""
    
    @staticmethod
    async def create(trend_data: TrendCreate) -> TrendInDB:
        """Create a new trend"""
        db = await get_database()
        trend_dict = trend_data.model_dump()
        trend_dict["scraped_at"] = datetime.utcnow()
        result = await db.trends.insert_one(trend_dict)
        
        created_trend = await db.trends.find_one({"_id": result.inserted_id})
        return TrendInDB(**created_trend)
    
    @staticmethod
    async def get_all(
        skip: int = 0,
        limit: int = 50,
        source: Optional[str] = None,
        processed: Optional[bool] = None
    ) -> List[Trend]:
        """Get all trends with optional filtering"""
        db = await get_database()
        query = {}
        
        if source:
            query["source"] = source
        if processed is not None:
            query["processed"] = processed
        
        cursor = db.trends.find(query).sort("created_at", -1).skip(skip).limit(limit)
        trends = await cursor.to_list(length=limit)
        
        return [Trend(**trend) for trend in trends]
    
    @staticmethod
    async def get_by_id(trend_id: str) -> Optional[Trend]:
        """Get a trend by ID"""
        db = await get_database()
        trend = await db.trends.find_one({"_id": ObjectId(trend_id)})
        
        if not trend:
            return None
        
        return Trend(**trend)
    
    @staticmethod
    async def mark_as_processed(trend_id: str) -> bool:
        """Mark a trend as processed"""
        db = await get_database()
        result = await db.trends.update_one(
            {"_id": ObjectId(trend_id)},
            {"$set": {"processed": True}}
        )
        
        return result.modified_count > 0
    
    @staticmethod
    async def get_unprocessed() -> List[Trend]:
        """Get all unprocessed trends"""
        return await TrendService.get_all(processed=False, limit=100)

