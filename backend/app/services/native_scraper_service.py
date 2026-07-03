"""
Native Scraper Service - Content extraction using native HTTP requests.
Enhanced with retry logic, better User-Agent rotation, and upvote filtering.
"""
import httpx
import random
import asyncio
from bs4 import BeautifulSoup
from typing import Dict, Optional, Any, List
import logging

logger = logging.getLogger(__name__)


# Realistic User-Agent strings for rotation
USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:126.0) Gecko/20100101 Firefox/126.0",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:126.0) Gecko/20100101 Firefox/126.0",
]

# Reddit-specific User-Agent (required for JSON endpoints)
REDDIT_USER_AGENTS = [
    "TrendFind/2.0 (India Product Trend Tracker; +https://github.com/trendfind)",
    "TrendFind Bot 2.0 (by /u/TrendFinderBot)",
]


class NativeScraperService:
    """Service for extracting structured data using native httpx requests"""

    @staticmethod
    async def extract_trending_topics(
        url: str, 
        platform: str,
        min_upvotes: int = 5,
        max_retries: int = 2,
    ) -> List[Dict[str, Any]]:
        """
        Use native HTTP requests to extract trending topics from a given URL.
        Supports Reddit .json endpoints with upvote filtering.
        """
        trends = []
        
        for attempt in range(max_retries + 1):
            try:
                async with httpx.AsyncClient(
                    timeout=20.0,
                    follow_redirects=True,
                ) as client:
                    if platform == "reddit":
                        trends = await NativeScraperService._scrape_reddit(
                            client, url, min_upvotes
                        )
                    else:
                        trends = await NativeScraperService._scrape_generic(
                            client, url
                        )
                    
                    # If we got results, break the retry loop
                    if trends:
                        break
                        
            except httpx.HTTPStatusError as e:
                if e.response.status_code == 429:
                    # Rate limited — wait and retry
                    wait_time = (2 ** attempt) + random.uniform(0.5, 2.0)
                    logger.warning(f"Rate limited on {url}, waiting {wait_time:.1f}s (attempt {attempt + 1})")
                    await asyncio.sleep(wait_time)
                else:
                    logger.error(f"HTTP error {e.response.status_code} for {url}: {e}")
                    break
            except Exception as e:
                logger.error(f"Scraping failed for {url} (attempt {attempt + 1}): {e}")
                if attempt < max_retries:
                    await asyncio.sleep(1.0)
                    
        return trends
    
    @staticmethod
    async def _scrape_reddit(
        client: httpx.AsyncClient,
        url: str,
        min_upvotes: int,
    ) -> List[Dict[str, Any]]:
        """Scrape Reddit subreddit using .json endpoint"""
        trends = []
        
        # Build JSON URL
        json_url = url
        if not json_url.endswith('.json'):
            if "/?/" in json_url:
                json_url = json_url.replace("/?", ".json?")
            elif json_url.endswith("/"):
                json_url = json_url[:-1] + ".json"
            else:
                json_url += ".json"
        
        # Add sort by top/hot if not already specified
        if "sort=" not in json_url and "/top" not in json_url and "/hot" not in json_url:
            separator = "&" if "?" in json_url else "?"
            json_url += f"{separator}sort=hot&limit=25"
        
        headers = {
            "User-Agent": random.choice(REDDIT_USER_AGENTS),
            "Accept": "application/json",
        }
        
        response = await client.get(json_url, headers=headers)
        response.raise_for_status()
        
        data = response.json()
        posts = data.get("data", {}).get("children", [])
        
        for post in posts:
            p_data = post.get("data", {})
            if not p_data:
                continue
            
            upvotes = int(p_data.get("ups", 0) or 0)
            
            # Filter by minimum upvotes
            if upvotes < min_upvotes:
                continue
            
            # Skip stickied/pinned posts (usually mod announcements)
            if p_data.get("stickied", False):
                continue
            
            thumbnail = p_data.get("thumbnail")
            if thumbnail and not str(thumbnail).startswith("http"):
                thumbnail = None
            
            # Try to get a better image from preview
            if not thumbnail:
                preview = p_data.get("preview", {})
                images = preview.get("images", [])
                if images:
                    source = images[0].get("source", {})
                    thumbnail = source.get("url", "").replace("&amp;", "&")
            
            trend = {
                "title": p_data.get("title", ""),
                "description": (p_data.get("selftext", "") or "")[:500],
                "upvotes": upvotes,
                "comments": int(p_data.get("num_comments", 0) or 0),
                "thumbnail": thumbnail,
                "url": f"https://www.reddit.com{p_data.get('permalink')}" if p_data.get("permalink") else p_data.get("url"),
                "subreddit": p_data.get("subreddit", ""),
            }
            
            if not trend["description"] and trend["url"]:
                trend["description"] = f"Reddit post from r/{trend['subreddit']}"
            
            trends.append(trend)
        
        logger.info(f"Reddit scraper: {len(trends)} posts from {url} (filtered by ≥{min_upvotes} upvotes)")
        return trends

    @staticmethod
    async def _scrape_generic(
        client: httpx.AsyncClient,
        url: str,
    ) -> List[Dict[str, Any]]:
        """Scrape a generic web page for Open Graph metadata"""
        trends = []
        
        headers = {"User-Agent": random.choice(USER_AGENTS)}
        response = await client.get(url, headers=headers)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.text, 'html.parser')
        title = soup.find('title')
        title_text = title.get_text(strip=True) if title else url
        
        desc_meta = (
            soup.find('meta', attrs={'name': 'description'}) or 
            soup.find('meta', attrs={'property': 'og:description'})
        )
        description = desc_meta['content'] if desc_meta and desc_meta.get('content') else ""
        
        og_image = soup.find('meta', attrs={'property': 'og:image'})
        image = og_image['content'] if og_image and og_image.get('content') else None
        
        trends.append({
            "title": title_text,
            "description": description,
            "upvotes": 0,
            "comments": 0,
            "url": url,
            "thumbnail": image,
        })
        
        return trends

    @staticmethod
    async def scrape_product_details(url: str) -> Optional[Dict[str, Any]]:
        """
        Scrape a product details page using native HTTP.
        Returns normalized structured data with Open Graph metadata.
        """
        normalized = {
            "product_name": None,
            "category": None,
            "short_description": None,
            "price": None,
            "image_url": None,
            "buy_links": [url],
            "raw_response": {"mock": False, "url": url, "source": "native_scraper"}
        }
        
        try:
            async with httpx.AsyncClient(timeout=15.0, follow_redirects=True) as client:
                headers = {"User-Agent": random.choice(USER_AGENTS)}
                response = await client.get(url, headers=headers)
                if response.status_code == 200:
                    soup = BeautifulSoup(response.text, 'html.parser')
                    
                    og_title = soup.find('meta', property='og:title')
                    og_desc = soup.find('meta', property='og:description')
                    og_image = soup.find('meta', property='og:image')
                    title = soup.find('title')
                    
                    if og_title and og_title.get('content'):
                        normalized["product_name"] = og_title.get('content')
                    elif title:
                        normalized["product_name"] = title.get_text(strip=True)
                        
                    if og_desc and og_desc.get('content'):
                        normalized["short_description"] = og_desc.get('content')
                        
                    if og_image and og_image.get('content'):
                        normalized["image_url"] = og_image.get('content')
        except Exception as e:
            logger.warning(f"Product details scrape failed for {url}: {e}")
            
        return normalized
