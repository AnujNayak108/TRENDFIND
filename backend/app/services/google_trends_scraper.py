"""
Google Trends Scraper Service - Real trending search data from Google Trends India
Uses the pytrends library (free, no API key required)
"""
import asyncio
import logging
import random
import time
from typing import List, Dict, Any, Optional
from datetime import datetime

from pytrends.request import TrendReq

from app.core.config import settings

logger = logging.getLogger(__name__)

# Product-related keywords to filter Google Trends results
PRODUCT_FILTER_KEYWORDS = [
    "buy", "price", "review", "best", "sale", "deal", "offer", "discount",
    "amazon", "flipkart", "online", "order", "launch", "new", "compare",
    "vs", "under", "budget", "premium", "specs", "features", "unboxing",
    # Hindi transliterations commonly searched
    "kharido", "sasta", "mehnga",
    # Product categories
    "phone", "laptop", "earbuds", "headphone", "watch", "tablet", "camera",
    "tv", "ac", "fridge", "washing machine", "mixer", "grinder", "cooker",
    "shoes", "sneakers", "kurta", "saree", "dress", "shirt", "jeans",
    "cream", "serum", "shampoo", "perfume", "trimmer", "dryer",
    "gaming", "console", "keyboard", "mouse", "monitor",
    "inverter", "ups", "router", "speaker", "soundbar",
]


class GoogleTrendsScraper:
    """Service for extracting trending product data from Google Trends India"""

    @classmethod
    async def get_trending_searches(cls, geo: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Get daily trending searches in India.
        Returns list of dicts with 'title' and 'metadata' keys.
        """
        geo = geo or settings.GOOGLE_TRENDS_GEO
        trends = []

        try:
            import httpx
            import xml.etree.ElementTree as ET
            
            url = f"https://trends.google.com/trends/trendingsearches/daily/rss?geo={geo}"
            async with httpx.AsyncClient(timeout=15.0) as client:
                response = await client.get(url)
                response.raise_for_status()
                
            root = ET.fromstring(response.text)
            
            for idx, item in enumerate(root.findall(".//item")):
                title_elem = item.find("title")
                if title_elem is None or not title_elem.text:
                    continue
                    
                search_term = title_elem.text.strip()
                is_product_related = cls._is_product_related(search_term)
                
                # Try to get traffic volume
                traffic = 0
                ht_approx = item.find("{https://trends.google.com/trends/trendingsearches/daily}approx_traffic")
                if ht_approx is not None and ht_approx.text:
                    traffic_text = ht_approx.text.replace("+", "").replace(",", "")
                    if traffic_text.isdigit():
                        traffic = int(traffic_text)
                
                trends.append({
                    "title": search_term,
                    "description": f"Trending search on Google India: {search_term}",
                    "source": "google_trends",
                    "source_url": f"https://trends.google.com/trends/explore?q={search_term.replace(' ', '+')}&geo={geo}",
                    "upvotes": traffic,
                    "comments": 0,
                    "is_product_related": is_product_related,
                    "metadata": {
                        "platform": "google_trends",
                        "type": "daily_trending",
                        "geo": geo,
                        "rank": idx,
                    }
                })

            logger.info(f"Google Trends: Found {len(trends)} trending searches for India via RSS")

        except Exception as e:
            logger.error(f"Google Trends daily trending failed: {e}")

        return trends

    @staticmethod
    def _is_product_related(text: str) -> bool:
        """Check if a text/search term is likely product-related"""
        text_lower = text.lower()
        return any(keyword in text_lower for keyword in PRODUCT_FILTER_KEYWORDS)

