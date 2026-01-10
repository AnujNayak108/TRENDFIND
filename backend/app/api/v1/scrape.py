"""
Scraping API Routes
"""
from fastapi import APIRouter, HTTPException
from app.services.scraper_service import ScraperService
from app.services.processor_service import ProcessorService
from app.services.scheduler_service import SchedulerService
from pydantic import BaseModel
from typing import Dict


class ScrapeResponse(BaseModel):
    """Response model for scrape operations"""
    success: bool
    message: str
    data: Dict


router = APIRouter()


@router.get("/scrape/status")
async def get_scrape_status():
    """
    Get the status of the automatic scraping scheduler
    Returns information about last scrape time, next scrape time, and scheduler status
    """
    status = SchedulerService.get_status()
    return status


@router.post("/scrape/run", response_model=ScrapeResponse)
async def run_scrape():
    """
    Manually trigger scraping of trending topics (for admin/testing)
    Note: Automatic scraping runs in the background at configured intervals
    """
    try:
        # Trigger manual scrape through scheduler service
        result = await SchedulerService.trigger_manual_scrape()
        
        if result and result.get("success"):
            return ScrapeResponse(
                success=True,
                message="Manual scraping triggered successfully",
                data=result
            )
        else:
            return ScrapeResponse(
                success=False,
                message="Scraping completed with errors",
                data=result or {}
            )
    
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error during scraping: {str(e)}"
        )

