"""
Buy Link Service - Database operations for buy links
"""
from typing import List, Optional
from datetime import datetime
from bson import ObjectId
from app.core.database import get_database
from app.models.buy_link import BuyLink, BuyLinkCreate, BuyLinkInDB


class BuyLinkService:
    """Service for managing buy links in the database"""
    
    @staticmethod
    async def create(buy_link_data: BuyLinkCreate) -> BuyLinkInDB:
        """Create or update a buy link (upsert based on product_id + platform)"""
        db = await get_database()
        buy_link_dict = buy_link_data.model_dump()
        buy_link_dict["scraped_at"] = datetime.utcnow()
        buy_link_dict["last_verified"] = datetime.utcnow()
        
        # Upsert: update if exists, insert if not
        result = await db.buy_links.update_one(
            {
                "product_id": buy_link_dict["product_id"],
                "platform": buy_link_dict["platform"]
            },
            {"$set": buy_link_dict},
            upsert=True
        )
        
        # Get the created/updated document
        buy_link = await db.buy_links.find_one({
            "product_id": buy_link_dict["product_id"],
            "platform": buy_link_dict["platform"]
        })
        
        return BuyLinkInDB(**buy_link)
    
    @staticmethod
    async def get_by_product_id(product_id: str) -> List[BuyLink]:
        """Get all buy links for a product"""
        db = await get_database()
        cursor = db.buy_links.find({"product_id": product_id}).sort("price", 1)
        buy_links = await cursor.to_list(length=100)
        
        return [BuyLink(**link) for link in buy_links]
    
    @staticmethod
    async def get_by_id(buy_link_id: str) -> Optional[BuyLink]:
        """Get a buy link by ID"""
        db = await get_database()
        buy_link = await db.buy_links.find_one({"_id": ObjectId(buy_link_id)})
        
        if not buy_link:
            return None
        
        return BuyLink(**buy_link)
    
    @staticmethod
    async def get_by_platform(platform: str, limit: int = 50) -> List[BuyLink]:
        """Get buy links by platform"""
        db = await get_database()
        cursor = db.buy_links.find({"platform": platform}).limit(limit)
        buy_links = await cursor.to_list(length=limit)
        
        return [BuyLink(**link) for link in buy_links]

