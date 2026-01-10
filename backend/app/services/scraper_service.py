"""
Scraper Service - Scrape trending topics from Google Trends, YouTube, and Instagram
"""
import json
import httpx
from typing import List, Dict, Optional
from datetime import datetime, timedelta
from app.core.config import settings
from app.models.trend import TrendCreate
from app.services.trend_service import TrendService

try:
    from pytrends.request import TrendReq
except ImportError:
    TrendReq = None

try:
    from googleapiclient.discovery import build
except ImportError:
    build = None


class ScraperService:
    """Service for scraping trending topics from various platforms"""
    
    @staticmethod
    async def scrape_google_trends(keywords: List[str] = None) -> List[TrendCreate]:
        """
        Scrape trending topics from Google Trends
        No API key required - completely free
        """
        if keywords is None:
            keywords = ["gadgets", "technology", "products", "electronics", "fashion"]
        
        trends = []
        
        if TrendReq is None:
            # Fallback to mock data if pytrends is not installed
            return ScraperService._get_mock_google_trends(keywords)
        
        try:
            pytrends = TrendReq(hl='en-US', tz=360)
            
            # Get trending searches
            trending_searches = pytrends.trending_searches(pn='united_states')
            
            for idx, trend_title in enumerate(trending_searches.head(10).values.flatten()):
                trend = {
                    "source": "google_trends",
                    "source_url": f"https://trends.google.com/trending/explore?q={trend_title.replace(' ', '+')}",
                    "title": str(trend_title),
                    "content": f"Trending on Google Trends: {trend_title}",
                    "subreddit": None,
                    "upvotes": 0,
                    "comments": 0,
                    "created_at": datetime.utcnow(),
                    "processed": False,
                    "metadata": {"trend_index": idx, "platform": "google_trends"}
                }
                trends.append(TrendCreate(**trend))
        except Exception as e:
            # Silently fallback to mock data on error (Google Trends can be rate-limited)
            # Uncomment for debugging: print(f"Google Trends API error, using mock data: {e}")
            return ScraperService._get_mock_google_trends(keywords)
        
        return trends
    
    @staticmethod
    def _get_mock_google_trends(keywords: List[str]) -> List[TrendCreate]:
        """Generate mock Google Trends data for development"""
        mock_trends = [
            {
                "source": "google_trends",
                "source_url": "https://trends.google.com/trending/explore?q=AirPods+Pro",
                "title": "AirPods Pro 2",
                "content": "Trending on Google Trends: AirPods Pro 2 - Latest wireless earbuds with noise cancellation",
                "subreddit": None,
                "upvotes": 0,
                "comments": 0,
                "created_at": datetime.utcnow(),
                "processed": False,
                "metadata": {"platform": "google_trends"}
            },
            {
                "source": "google_trends",
                "source_url": "https://trends.google.com/trending/explore?q=Stanley+Tumbler",
                "title": "Stanley Tumbler",
                "content": "Trending on Google Trends: Stanley Tumbler - Popular water bottle trending everywhere",
                "subreddit": None,
                "upvotes": 0,
                "comments": 0,
                "created_at": datetime.utcnow(),
                "processed": False,
                "metadata": {"platform": "google_trends"}
            },
            {
                "source": "google_trends",
                "source_url": "https://trends.google.com/trending/explore?q=Dyson+Airwrap",
                "title": "Dyson Airwrap",
                "content": "Trending on Google Trends: Dyson Airwrap - Revolutionary hair styling tool",
                "subreddit": None,
                "upvotes": 0,
                "comments": 0,
                "created_at": datetime.utcnow(),
                "processed": False,
                "metadata": {"platform": "google_trends"}
            }
        ]
        
        return [TrendCreate(**trend) for trend in mock_trends]
    
    @staticmethod
    async def scrape_youtube() -> List[TrendCreate]:
        """
        Scrape trending videos from YouTube
        Uses YouTube Data API v3 (free tier available)
        """
        # Check if API key is valid (not empty or placeholder)
        if not settings.YOUTUBE_API_KEY or settings.YOUTUBE_API_KEY in ["your_youtube_api_key", ""]:
            return ScraperService._get_mock_youtube_trends()
        
        if build is None:
            return ScraperService._get_mock_youtube_trends()
        
        trends = []
        
        try:
            youtube = build('youtube', 'v3', developerKey=settings.YOUTUBE_API_KEY)
            
            # Get trending videos in US
            request = youtube.videos().list(
                part='snippet,statistics',
                chart='mostPopular',
                regionCode='US',
                maxResults=10
            )
            response = request.execute()
            
            for item in response.get('items', []):
                snippet = item['snippet']
                stats = item.get('statistics', {})
                
                trend = {
                    "source": "youtube",
                    "source_url": f"https://www.youtube.com/watch?v={item['id']}",
                    "title": snippet['title'],
                    "content": snippet.get('description', '')[:500],  # Limit description length
                    "subreddit": None,
                    "upvotes": int(stats.get('likeCount', 0)),
                    "comments": int(stats.get('commentCount', 0)),
                    "created_at": datetime.fromisoformat(snippet['publishedAt'].replace('Z', '+00:00')),
                    "processed": False,
                    "metadata": {
                        "video_id": item['id'],
                        "channel": snippet['channelTitle'],
                        "views": stats.get('viewCount', 0),
                        "platform": "youtube"
                    }
                }
                trends.append(TrendCreate(**trend))
        except Exception as e:
            # Silently fallback to mock data on error (API key invalid or rate limited)
            # Uncomment for debugging: print(f"YouTube API error, using mock data: {e}")
            return ScraperService._get_mock_youtube_trends()
        
        return trends
    
    @staticmethod
    def _get_mock_youtube_trends() -> List[TrendCreate]:
        """Generate mock YouTube trends for development"""
        mock_trends = [
            {
                "source": "youtube",
                "source_url": "https://www.youtube.com/watch?v=mock1",
                "title": "iPhone 15 Pro Max Review - Best Camera Phone?",
                "content": "Full review of the iPhone 15 Pro Max camera system and features. Is it worth the upgrade?",
                "subreddit": None,
                "upvotes": 12500,
                "comments": 890,
                "created_at": datetime.utcnow(),
                "processed": False,
                "metadata": {"video_id": "mock1", "platform": "youtube"}
            },
            {
                "source": "youtube",
                "source_url": "https://www.youtube.com/watch?v=mock2",
                "title": "Top 10 Trending Products You Need in 2024",
                "content": "Discover the hottest products trending right now including Stanley tumblers, AirPods Pro, and more!",
                "subreddit": None,
                "upvotes": 8900,
                "comments": 567,
                "created_at": datetime.utcnow(),
                "processed": False,
                "metadata": {"video_id": "mock2", "platform": "youtube"}
            },
            {
                "source": "youtube",
                "source_url": "https://www.youtube.com/watch?v=mock3",
                "title": "Dyson Airwrap Tutorial - How to Style Your Hair",
                "content": "Learn how to use the Dyson Airwrap to achieve salon-quality hair styling at home.",
                "subreddit": None,
                "upvotes": 15200,
                "comments": 1234,
                "created_at": datetime.utcnow(),
                "processed": False,
                "metadata": {"video_id": "mock3", "platform": "youtube"}
            }
        ]
        
        return [TrendCreate(**trend) for trend in mock_trends]
    
    @staticmethod
    async def scrape_instagram() -> List[TrendCreate]:
        """
        Scrape trending posts from Instagram
        Note: Instagram's official API is restricted. This uses mock data.
        For production, consider using Instagram Basic Display API or web scraping.
        """
        # Instagram scraping requires authentication and has strict rate limits
        # Using mock data for now - can be extended with instagrapi or similar libraries
        return ScraperService._get_mock_instagram_trends()
    
    @staticmethod
    def _get_mock_instagram_trends() -> List[TrendCreate]:
        """Generate mock Instagram trends for development"""
        mock_trends = [
            {
                "source": "instagram",
                "source_url": "https://www.instagram.com/p/mock1",
                "title": "New AirPods Pro 2 Unboxing",
                "content": "Just got the new AirPods Pro 2! The noise cancellation is incredible 🔥 #AirPodsPro #Apple",
                "subreddit": None,
                "upvotes": 45200,
                "comments": 1234,
                "created_at": datetime.utcnow(),
                "processed": False,
                "metadata": {"post_id": "mock1", "platform": "instagram"}
            },
            {
                "source": "instagram",
                "source_url": "https://www.instagram.com/p/mock2",
                "title": "Stanley Tumbler Collection",
                "content": "My Stanley tumbler collection is growing! These are the best water bottles 💧 #StanleyTumbler #Hydration",
                "subreddit": None,
                "upvotes": 32100,
                "comments": 890,
                "created_at": datetime.utcnow(),
                "processed": False,
                "metadata": {"post_id": "mock2", "platform": "instagram"}
            },
            {
                "source": "instagram",
                "source_url": "https://www.instagram.com/p/mock3",
                "title": "Dyson Airwrap Hair Transformation",
                "content": "Before and after using the Dyson Airwrap! My hair has never looked better ✨ #DysonAirwrap #HairGoals",
                "subreddit": None,
                "upvotes": 67800,
                "comments": 2345,
                "created_at": datetime.utcnow(),
                "processed": False,
                "metadata": {"post_id": "mock3", "platform": "instagram"}
            }
        ]
        
        return [TrendCreate(**trend) for trend in mock_trends]
    
    @staticmethod
    async def run_scrape() -> Dict[str, int]:
        """
        Run scraping for all configured sources
        Returns count of trends scraped per source
        """
        results = {
            "google_trends": 0,
            "youtube": 0,
            "instagram": 0,
            "total": 0
        }
        
        try:
            # Scrape Google Trends
            google_trends = await ScraperService.scrape_google_trends()
            for trend in google_trends:
                await TrendService.create(trend)
                results["google_trends"] += 1
                results["total"] += 1
            
            # Scrape YouTube
            youtube_trends = await ScraperService.scrape_youtube()
            for trend in youtube_trends:
                await TrendService.create(trend)
                results["youtube"] += 1
                results["total"] += 1
            
            # Scrape Instagram
            instagram_trends = await ScraperService.scrape_instagram()
            for trend in instagram_trends:
                await TrendService.create(trend)
                results["instagram"] += 1
                results["total"] += 1
            
        except Exception as e:
            # Log error but continue processing
            print(f"Error during scraping: {e}")
        
        return results

