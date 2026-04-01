"""
Scraper Service - Scrape trending topics across the internet using Firecrawl LLM extraction.
"""
from typing import List, Dict, Any
from datetime import datetime
from app.core.config import settings
from app.models.trend import TrendCreate
from app.services.trend_service import TrendService
from app.services.native_scraper_service import NativeScraperService


class ScraperService:
    """Service for orchestrating multi-platform trend scraping via Firecrawl"""
    
    # Target URLs mapping to platforms
    TARGET_SOURCES = [
        {"platform": "reddit", "url": "https://www.reddit.com/r/BuyItForLifeIndia/"},
        {"platform": "instagram", "url": "https://www.instagram.com/popular/trending-products-india/"}
    ]

    @staticmethod
    async def scrape_platform(source: Dict[str, str]) -> List[TrendCreate]:
        """
        Scrape a specific platform via Firecrawl LLM extraction and map to DB models.
        """
        platform = source["platform"]
        url = source["url"]
        trends = []
        
        try:
            # Send native scraper to extract arrays of trends
            extracted_data = await NativeScraperService.extract_trending_topics(url, platform)
            
            for idx, item in enumerate(extracted_data):
                # Ensure we have the minimum requirements
                if not item.get("title"):
                    continue
                    
                trend = TrendCreate(
                    source=platform,
                    source_url=str(item.get("url") or url),
                    title=str(item.get("title")),
                    content=str(item.get("description", ""))[:1000],  # cap length
                    subreddit=None,
                    upvotes=int(item.get("upvotes", 0) or 0),
                    comments=int(item.get("comments", 0) or 0),
                    created_at=datetime.utcnow(),
                    processed=False,
                    metadata={
                        "platform": platform,
                        "extraction_method": "native_scraper",
                        "index": idx,
                        "thumbnail": item.get("thumbnail")
                    }
                )
                trends.append(trend)
                
        except Exception as e:
            print(f"Failed to scrape {platform} at {url}: {e}")
            
        return trends

    @staticmethod
    async def run_scrape() -> Dict[str, int]:
        """
        Orchestrate scraping across all configured sources using native scrapers.
        Returns count of trends scraped per source.
        """
        results = {"total": 0}
        
        try:
            for source in ScraperService.TARGET_SOURCES:
                platform = source["platform"]
                if platform not in results:
                    results[platform] = 0
                    
                print(f"Dispatching Native extraction to {platform}...")
                platform_trends = await ScraperService.scrape_platform(source)
                
                for trend in platform_trends:
                    # Save to DB
                    await TrendService.create(trend)
                    results[platform] += 1
                    results["total"] += 1
                    
        except Exception as e:
            # Log error but continue
            print(f"Error during overall scraping operation: {e}")
            
        return results
