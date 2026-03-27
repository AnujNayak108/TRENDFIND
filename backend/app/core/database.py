"""
MongoDB Database Connection and Configuration
"""
import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
from typing import Optional
from app.core.config import settings


class Database:
    """MongoDB database connection manager"""
    client: Optional[AsyncIOMotorClient] = None


database = Database()


async def connect_to_mongo():
    """Connect to MongoDB"""
    try:
        print("Connecting to MongoDB...")
        # For MongoDB Atlas (mongodb+srv://), SSL is handled automatically
        # Use shorter timeout to fail faster if network is unavailable
        database.client = AsyncIOMotorClient(
            settings.MONGODB_URL,
            serverSelectionTimeoutMS=10000,  # 10 second timeout
            connectTimeoutMS=10000,
            socketTimeoutMS=10000,
            retryWrites=False  # Disable retries to fail faster
        )
        
        # Test connection with timeout handling
        print("  Testing connection...")
        try:
            await asyncio.wait_for(
                database.client.admin.command('ping'),
                timeout=5.0  # 5 second timeout for the ping command
            )
        except asyncio.TimeoutError:
            print("  [WARNING] MongoDB connection test timed out")
            print("  Server will continue in degraded mode")
            return  # Don't raise - continue with degraded mode
        
        # Get connection info
        is_atlas = "mongodb+srv://" in settings.MONGODB_URL
        connection_type = "MongoDB Atlas" if is_atlas else "MongoDB"
        
        print(f"[SUCCESS] Connected to {connection_type}!")
        print(f"  Database: {settings.DATABASE_NAME}")
        
        # Create indexes on startup
        await create_indexes()
        print("  Indexes created successfully")
        
    except asyncio.TimeoutError:
        print("[WARNING] MongoDB connection timed out - starting in degraded mode")
        print("  The server will work but without database features")
        # Don't raise - allow server to continue
    except Exception as e:
        error_msg = str(e)
        print(f"[ERROR] MongoDB connection failed!")
        print(f"  Error: {error_msg}")
        
        if "SSL" in error_msg or "TLS" in error_msg or "timeout" in error_msg.lower():
            print("\n  Troubleshooting steps:")
            print("  1. Go to MongoDB Atlas Dashboard")
            print("  2. Navigate to 'Network Access'")
            print("  3. Click 'Add IP Address'")
            print("  4. Add your current IP or '0.0.0.0/0' (for development)")
            print("  5. Wait 1-2 minutes for changes to take effect")
        elif "authentication" in error_msg.lower() or "auth" in error_msg.lower():
            print("\n  Troubleshooting steps:")
            print("  1. Check your MongoDB connection string")
            print("  2. Verify username and password are correct")
            print("  3. Make sure database user has proper permissions")
        else:
            print("\n  Troubleshooting steps:")
            print("  1. Verify your MongoDB connection string is correct")
            print("  2. Check your internet connection")
            print("  3. Ensure MongoDB Atlas cluster is running")
        
        # Don't raise - allow server to continue in degraded mode
        print("  Continuing with degraded mode...")


async def close_mongo_connection():
    """Close MongoDB connection"""
    if database.client:
        print("Closing MongoDB connection...")
        database.client.close()
        print("[SUCCESS] MongoDB connection closed")


async def get_database():
    """Get database instance"""
    if database.client is None:
        raise ConnectionError("MongoDB client is not connected. Please check your MongoDB connection.")
    return database.client[settings.DATABASE_NAME]


async def create_indexes():
    """Create database indexes for optimal query performance"""
    db = await get_database()
    
    # Trends collection indexes
    trends_collection = db.trends
    await trends_collection.create_index([("source", 1), ("created_at", -1)])
    await trends_collection.create_index([("processed", 1)])
    await trends_collection.create_index([("scraped_at", -1)])
    
    # Products collection indexes
    products_collection = db.products
    await products_collection.create_index([("normalized_name", 1)])
    await products_collection.create_index([("trend_score", -1)])
    await products_collection.create_index([("category", 1)])
    await products_collection.create_index([("first_detected_at", -1)])
    
    # Buy links collection indexes
    buy_links_collection = db.buy_links
    await buy_links_collection.create_index([("product_id", 1), ("platform", 1)], unique=True)
    await buy_links_collection.create_index([("product_id", 1)])
    await buy_links_collection.create_index([("platform", 1)])
    await buy_links_collection.create_index([("price", 1)])



