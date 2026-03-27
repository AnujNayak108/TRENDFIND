"""
FastAPI Application Entry Point
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.encoders import jsonable_encoder
from bson import ObjectId
from app.core.config import settings
from app.core.database import connect_to_mongo, close_mongo_connection
from app.api.v1 import trends, products, scrape
from app.services.scheduler_service import SchedulerService

# Custom JSON encoder to handle ObjectId
def custom_jsonable_encoder(obj):
    """Custom encoder that converts ObjectId to string"""
    if isinstance(obj, ObjectId):
        return str(obj)
    return jsonable_encoder(obj)

# Initialize FastAPI app
app = FastAPI(
    title="TrendFind API",
    description="API for detecting and tracking trending products from social media",
    version="1.0.0",
)


@app.on_event("startup")
async def startup_db():
    """Initialize database and start background scheduler on application startup"""
    try:
        await connect_to_mongo()
        # Start automatic scraping scheduler (runs initial scrape immediately)
        # Run in background so it doesn't block the server startup
        import asyncio
        asyncio.create_task(SchedulerService.start())
    except Exception as e:
        print(f"\n[WARNING] Server starting without MongoDB connection:")
        print(f"  {str(e)}")
        print(f"  The server will start, but database features will not work.")
        print(f"  Please fix the MongoDB connection and restart the server.\n")
        # Don't raise - allow server to start in degraded mode


@app.on_event("shutdown")
async def shutdown_db():
    """Close database and stop scheduler on application shutdown"""
    SchedulerService.stop()
    await close_mongo_connection()

# CORS middleware for frontend access
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(trends.router, prefix="/api/v1", tags=["trends"])
app.include_router(products.router, prefix="/api/v1", tags=["products"])
app.include_router(scrape.router, prefix="/api/v1", tags=["scrape"])


@app.get("/")
async def root():
    """Health check endpoint"""
    return {
        "status": "ok",
        "message": "TrendFind API is running",
        "version": "1.0.0"
    }


@app.get("/health")
async def health_check():
    """Detailed health check"""
    return {
        "status": "healthy",
        "database": "connected"  # TODO: Add actual DB health check
    }

