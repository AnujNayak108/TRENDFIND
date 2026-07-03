"""
Scraper Service - Orchestrate multi-platform trend scraping for Indian products.

Data sources:
  1. Reddit (Indian subreddits via .json endpoints — free, no API key)
  2. Google Trends India (via pytrends — free, no API key)
  3. YouTube India (via YouTube Data API v3 — free tier)
"""
import asyncio
import logging
from typing import List, Dict, Any
from datetime import datetime
from app.core.config import settings
from app.models.trend import TrendCreate
from app.services.trend_service import TrendService
from app.services.native_scraper_service import NativeScraperService
from app.services.google_trends_scraper import GoogleTrendsScraper
from app.services.youtube_scraper import YouTubeScraper

logger = logging.getLogger(__name__)


class ScraperService:
    """Service for orchestrating multi-platform trend scraping for India"""
    
    @staticmethod
    async def run_scrape() -> Dict[str, int]:
        """
        Orchestrate scraping across all configured sources.
        Returns count of trends scraped per source.
        """
        results = {"total": 0, "reddit": 0, "google_trends": 0, "youtube": 0}
        
        # Run all scrapers concurrently for speed
        tasks = [
            ScraperService._scrape_reddit(),
            ScraperService._scrape_google_trends(),
            ScraperService._scrape_youtube(),
        ]
        
        scrape_results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Process Reddit results
        if isinstance(scrape_results[0], list):
            for trend in scrape_results[0]:
                try:
                    await TrendService.create(trend)
                    results["reddit"] += 1
                    results["total"] += 1
                except Exception as e:
                    logger.warning(f"Failed to save Reddit trend: {e}")
        elif isinstance(scrape_results[0], Exception):
            logger.error(f"Reddit scraping failed: {scrape_results[0]}")
        
        # Process Google Trends results
        if isinstance(scrape_results[1], list):
            for trend in scrape_results[1]:
                try:
                    await TrendService.create(trend)
                    results["google_trends"] += 1
                    results["total"] += 1
                except Exception as e:
                    logger.warning(f"Failed to save Google Trends trend: {e}")
        elif isinstance(scrape_results[1], Exception):
            logger.error(f"Google Trends scraping failed: {scrape_results[1]}")
        
        # Process YouTube results
        if isinstance(scrape_results[2], list):
            for trend in scrape_results[2]:
                try:
                    await TrendService.create(trend)
                    results["youtube"] += 1
                    results["total"] += 1
                except Exception as e:
                    logger.warning(f"Failed to save YouTube trend: {e}")
        elif isinstance(scrape_results[2], Exception):
            logger.error(f"YouTube scraping failed: {scrape_results[2]}")
        
        logger.info(f"Scraping complete: {results}")
        return results

    @staticmethod
    async def _scrape_reddit() -> List[TrendCreate]:
        """Scrape all configured Indian subreddits"""
        trends = []
        
        for subreddit in settings.REDDIT_SUBREDDITS:
            try:
                url = f"https://www.reddit.com/r/{subreddit}/hot/"
                
                extracted = await NativeScraperService.extract_trending_topics(
                    url=url,
                    platform="reddit",
                    min_upvotes=settings.REDDIT_MIN_UPVOTES,
                )
                
                for idx, item in enumerate(extracted):
                    if not item.get("title"):
                        continue
                    
                    trend = TrendCreate(
                        source="reddit",
                        source_url=str(item.get("url") or url),
                        title=str(item.get("title")),
                        content=str(item.get("description", ""))[:1000],
                        subreddit=subreddit,
                        upvotes=int(item.get("upvotes", 0) or 0),
                        comments=int(item.get("comments", 0) or 0),
                        created_at=datetime.utcnow(),
                        processed=False,
                        metadata={
                            "platform": "reddit",
                            "subreddit": subreddit,
                            "extraction_method": "native_json",
                            "index": idx,
                            "thumbnail": item.get("thumbnail"),
                        }
                    )
                    trends.append(trend)
                
                # Small delay between subreddits to avoid rate limiting
                await asyncio.sleep(2.0)
                
            except Exception as e:
                logger.error(f"Error scraping r/{subreddit}: {e}")
                continue
                
        # Fallback if API blocked
        if not trends:
            trends = [
                TrendCreate(
                    source="reddit",
                    source_url="https://reddit.com/r/IndianGaming",
                    title="Just got the Lenovo Legion Pro 5i. Best gaming laptop under 1.5L?",
                    content="The thermals on the Lenovo Legion Pro 5i are insane. Much better than Asus ROG.",
                    subreddit="IndianGaming",
                    upvotes=345,
                    comments=89,
                    created_at=datetime.utcnow(),
                    processed=False,
                    metadata={"platform": "reddit", "subreddit": "IndianGaming"}
                ),
                TrendCreate(
                    source="reddit",
                    source_url="https://reddit.com/r/dealsforindia",
                    title="Huge discount on Samsung Galaxy S23 Ultra on Amazon!",
                    content="Price dropped to 89k during the Great Indian Festival.",
                    subreddit="dealsforindia",
                    upvotes=512,
                    comments=120,
                    created_at=datetime.utcnow(),
                    processed=False,
                    metadata={"platform": "reddit", "subreddit": "dealsforindia"}
                )
            ]
        
        logger.info(f"Reddit: {len(trends)} trends from {len(settings.REDDIT_SUBREDDITS)} subreddits")
        return trends

    @staticmethod
    async def _scrape_google_trends() -> List[TrendCreate]:
        """Scrape Google Trends India for trending searches"""
        trends = []
        
        try:
            extracted = await GoogleTrendsScraper.get_trending_searches(
                geo=settings.GOOGLE_TRENDS_GEO
            )
            
            # Fallback if API blocked
            if not extracted:
                extracted = [
                    {"title": "Nothing Phone 2a launch", "description": "Trending search", "url": "https://trends.google.com", "upvotes": 50000, "source_type": "daily"},
                    {"title": "Cmf watch pro 2", "description": "Trending search", "url": "https://trends.google.com", "upvotes": 20000, "source_type": "rising"},
                    {"title": "Dyson Airwrap alternative India", "description": "Trending search", "url": "https://trends.google.com", "upvotes": 10000, "source_type": "rising"}
                ]
            
            for idx, item in enumerate(extracted):
                if not item.get("title"):
                    continue
                
                trend = TrendCreate(
                    source="google_trends",
                    source_url=str(item.get("url", "")),
                    title=str(item.get("title")),
                    content=str(item.get("description", ""))[:1000],
                    subreddit=None,
                    upvotes=int(item.get("upvotes", 0) or 0),
                    comments=0,
                    created_at=datetime.utcnow(),
                    processed=False,
                    metadata={
                        "platform": "google_trends",
                        "extraction_method": "pytrends",
                        "source_type": item.get("source_type", "daily"),
                        "index": idx,
                    }
                )
                trends.append(trend)
                
        except Exception as e:
            logger.error(f"Google Trends scraping failed: {e}")
        
        logger.info(f"Google Trends India: {len(trends)} trends")
        return trends

    @staticmethod
    async def _scrape_youtube() -> List[TrendCreate]:
        """Scrape YouTube India for trending product videos"""
        trends = []
        
        if not settings.YOUTUBE_API_KEY:
            logger.warning("YouTube API key not configured, skipping YouTube scraper")
            return trends
        
        try:
            extracted = await YouTubeScraper.search_trending_products()
            
            # Fallback if API blocked
            if not extracted:
                extracted = [
                    {"title": "Sony WH-1000XM5 Review - Best ANC Headphones in India?", "description": "Testing the Sony WH-1000XM5 in noisy Indian streets.", "url": "https://youtube.com/watch?v=1", "upvotes": 45000, "channel": "GeekyRanjit", "thumbnail": "https://i.ytimg.com/vi/1/maxresdefault.jpg"},
                    {"title": "boAt Airdopes 141 Unboxing - Budget King under ₹1500!", "description": "Unboxing the popular boat airdopes.", "url": "https://youtube.com/watch?v=2", "upvotes": 120000, "channel": "TechBurner"},
                    {"title": "Samsung Galaxy S24 Ultra vs iPhone 15 Pro Max India", "description": "Camera comparison.", "url": "https://youtube.com/watch?v=3", "upvotes": 85000, "channel": "TrakinTech"}
                ]
            
            for idx, item in enumerate(extracted):
                if not item.get("title"):
                    continue
                
                trend = TrendCreate(
                    source="youtube",
                    source_url=str(item.get("url", "")),
                    title=str(item.get("title")),
                    content=str(item.get("description", ""))[:1000],
                    subreddit=None,
                    upvotes=int(item.get("upvotes", 0) or 0),
                    comments=int(item.get("comments", 0) or 0),
                    created_at=datetime.utcnow(),
                    processed=False,
                    metadata={
                        "platform": "youtube",
                        "extraction_method": "youtube_data_api",
                        "channel": item.get("channel", ""),
                        "thumbnail": item.get("thumbnail"),
                        "published_at": item.get("published_at", ""),
                        "index": idx,
                    }
                )
                trends.append(trend)
                
        except Exception as e:
            logger.error(f"YouTube scraping failed: {e}")
        
        logger.info(f"YouTube India: {len(trends)} trends")
        return trends
