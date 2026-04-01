import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
import sys
import os

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from app.core.config import settings

async def drop_collections():
    client = AsyncIOMotorClient(settings.MONGODB_URL)
    db = client[settings.DATABASE_NAME]
    
    print("Dropping collections...")
    await db.trends.drop()
    await db.products.drop()
    await db.buy_links.drop()
    print("Collections dropped successfully.")
    
if __name__ == "__main__":
    asyncio.run(drop_collections())
