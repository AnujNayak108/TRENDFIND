"""
Scheduler Service - Background task scheduling for automatic scraping
"""
import asyncio
import logging
from datetime import datetime
from typing import Optional
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.interval import IntervalTrigger
from app.core.config import settings
from app.services.scraper_service import ScraperService
from app.services.processor_service import ProcessorService

logger = logging.getLogger(__name__)


class SchedulerService:
    """Service for managing background scraping tasks"""
    
    _scheduler: Optional[AsyncIOScheduler] = None
    _last_scrape_time: Optional[datetime] = None
    _last_scrape_status: Optional[dict] = None
    _is_running: bool = False
    
    @classmethod
    async def start(cls):
        """Start the background scheduler and run initial scrape"""
        if cls._scheduler and cls._scheduler.running:
            logger.warning("Scheduler is already running")
            return
        
        cls._scheduler = AsyncIOScheduler()
        
        # Schedule scraping task at configured interval
        trigger = IntervalTrigger(minutes=settings.SCRAPE_INTERVAL_MINUTES)
        cls._scheduler.add_job(
            cls._run_scraping_task,
            trigger=trigger,
            id='scrape_and_process',
            name='Scrape trends and process products',
            replace_existing=True,
            max_instances=1  # Prevent overlapping runs
        )
        
        cls._scheduler.start()
        cls._is_running = True
        logger.info(f"Scheduler started. Scraping every {settings.SCRAPE_INTERVAL_MINUTES} minutes")
        
        # Run initial scrape immediately
        await cls._run_scraping_task()
    
    @classmethod
    def stop(cls):
        """Stop the background scheduler"""
        if cls._scheduler:
            cls._scheduler.shutdown()
            cls._is_running = False
            logger.info("Scheduler stopped")
    
    @classmethod
    async def _run_scraping_task(cls):
        """Background task that runs scraping and processing"""
        try:
            logger.info("Starting scheduled scraping task...")
            start_time = datetime.utcnow()
            
            # Step 1: Scrape trends from sources
            scrape_results = await ScraperService.run_scrape()
            logger.info(f"Scraping completed: {scrape_results}")
            
            # Step 2: Process trends to extract products
            process_results = await ProcessorService.process_trends()
            logger.info(f"Processing completed: {process_results}")
            
            end_time = datetime.utcnow()
            duration = (end_time - start_time).total_seconds()
            
            cls._last_scrape_time = end_time
            cls._last_scrape_status = {
                "success": True,
                "scraping": scrape_results,
                "processing": process_results,
                "duration_seconds": duration,
                "timestamp": end_time.isoformat()
            }
            
            logger.info(f"Scraping task completed in {duration:.2f} seconds")
            
        except Exception as e:
            logger.error(f"Error in scraping task: {e}", exc_info=True)
            cls._last_scrape_time = datetime.utcnow()
            cls._last_scrape_status = {
                "success": False,
                "error": str(e),
                "timestamp": cls._last_scrape_time.isoformat()
            }
    
    @classmethod
    def get_status(cls) -> dict:
        """Get current scheduler status"""
        next_run = None
        if cls._scheduler and cls._scheduler.running:
            job = cls._scheduler.get_job('scrape_and_process')
            if job:
                next_run = job.next_run_time.isoformat() if job.next_run_time else None
        
        return {
            "is_running": cls._is_running,
            "interval_minutes": settings.SCRAPE_INTERVAL_MINUTES,
            "last_scrape_time": cls._last_scrape_time.isoformat() if cls._last_scrape_time else None,
            "last_scrape_status": cls._last_scrape_status,
            "next_scrape_time": next_run
        }
    
    @classmethod
    async def trigger_manual_scrape(cls):
        """Manually trigger a scraping task (for admin/testing)"""
        await cls._run_scraping_task()
        return cls._last_scrape_status
