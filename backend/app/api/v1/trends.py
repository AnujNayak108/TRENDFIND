"""
Trends API Routes
"""
from typing import Optional
from fastapi import APIRouter, Query, HTTPException
from app.services.trend_service import TrendService
from app.models.trend import Trend

router = APIRouter()


@router.get("/trends", response_model=list[Trend])
async def get_trends(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    source: Optional[str] = Query(None, description="Filter by source platform"),
    processed: Optional[bool] = Query(None, description="Filter by processed status")
):
    """
    Get all trends with optional filtering
    """
    trends = await TrendService.get_all(
        skip=skip,
        limit=limit,
        source=source,
        processed=processed
    )
    return trends


@router.get("/trends/{trend_id}", response_model=Trend)
async def get_trend(trend_id: str):
    """
    Get a specific trend by ID
    """
    trend = await TrendService.get_by_id(trend_id)
    if not trend:
        raise HTTPException(status_code=404, detail="Trend not found")
    return trend

