"""
YouTube Scraper Service - Trending product videos from YouTube India
Uses YouTube Data API v3 (free tier: 10,000 units/day)
"""
import re
import asyncio
import logging
from typing import List, Dict, Any, Optional
from datetime import datetime

from app.core.config import settings

logger = logging.getLogger(__name__)


class YouTubeScraper:
    """Service for extracting trending product data from YouTube India"""

    @classmethod
    async def search_trending_products(cls) -> List[Dict[str, Any]]:
        """
        Search YouTube for trending product videos in India.
        Uses configured search queries from settings.
        Returns list of trend dicts ready for the pipeline.
        """
        api_key = settings.YOUTUBE_API_KEY
        if not api_key:
            logger.warning("YouTube API key not configured, skipping YouTube scraper")
            return []

        all_results = []

        for query in settings.YOUTUBE_SEARCH_QUERIES:
            try:
                results = await cls._search_videos(api_key, query)
                all_results.extend(results)
                # Small delay between queries to be kind to the API
                await asyncio.sleep(0.5)
            except Exception as e:
                logger.error(f"YouTube search failed for query '{query}': {e}")
                continue

        # Deduplicate by video ID
        seen_ids = set()
        unique_results = []
        for result in all_results:
            vid_id = result.get("metadata", {}).get("video_id")
            if vid_id and vid_id not in seen_ids:
                seen_ids.add(vid_id)
                unique_results.append(result)

        logger.info(f"YouTube: Found {len(unique_results)} unique trending product videos")
        return unique_results

    @classmethod
    async def _search_videos(cls, api_key: str, query: str, max_results: int = 10) -> List[Dict[str, Any]]:
        """
        Search YouTube for videos matching a query, filtered to India region.
        Uses the YouTube Data API v3 search endpoint.
        """
        import httpx

        trends = []

        try:
            search_url = "https://www.googleapis.com/youtube/v3/search"
            search_params = {
                "part": "snippet",
                "q": query,
                "type": "video",
                "regionCode": "IN",
                "relevanceLanguage": "en",
                "order": "viewCount",
                "maxResults": max_results,
                "publishedAfter": cls._get_recent_date(),
                "key": api_key,
            }

            async with httpx.AsyncClient(timeout=15.0) as client:
                response = await client.get(search_url, params=search_params)
                response.raise_for_status()
                data = response.json()

            items = data.get("items", [])
            if not items:
                return trends

            # Get video IDs for statistics lookup
            video_ids = [item["id"]["videoId"] for item in items if "videoId" in item.get("id", {})]

            # Fetch view counts for these videos
            view_counts = await cls._get_video_stats(api_key, video_ids)

            for item in items:
                snippet = item.get("snippet", {})
                video_id = item.get("id", {}).get("videoId")
                if not video_id:
                    continue

                title = snippet.get("title", "")
                description = snippet.get("description", "")
                thumbnail = snippet.get("thumbnails", {}).get("high", {}).get("url") or \
                            snippet.get("thumbnails", {}).get("medium", {}).get("url") or \
                            snippet.get("thumbnails", {}).get("default", {}).get("url")
                published_at = snippet.get("publishedAt", "")
                channel_title = snippet.get("channelTitle", "")
                views = view_counts.get(video_id, 0)

                # Extract potential product names from the video title
                product_names = cls._extract_products_from_title(title)

                trend = {
                    "title": title,
                    "description": description[:500] if description else "",
                    "source": "youtube",
                    "source_url": f"https://www.youtube.com/watch?v={video_id}",
                    "upvotes": views,  # Use view count as the "upvote" signal
                    "comments": 0,
                    "thumbnail": thumbnail,
                    "metadata": {
                        "platform": "youtube",
                        "video_id": video_id,
                        "channel": channel_title,
                        "published_at": published_at,
                        "view_count": views,
                        "search_query": query,
                        "extracted_products": product_names,
                        "thumbnail": thumbnail,
                    }
                }
                trends.append(trend)

        except Exception as e:
            logger.error(f"YouTube API search failed for '{query}': {e}")

        return trends

    @classmethod
    async def _get_video_stats(cls, api_key: str, video_ids: List[str]) -> Dict[str, int]:
        """Fetch view counts for a list of video IDs"""
        import httpx

        view_counts = {}
        if not video_ids:
            return view_counts

        try:
            stats_url = "https://www.googleapis.com/youtube/v3/videos"
            stats_params = {
                "part": "statistics",
                "id": ",".join(video_ids),
                "key": api_key,
            }

            async with httpx.AsyncClient(timeout=15.0) as client:
                response = await client.get(stats_url, params=stats_params)
                response.raise_for_status()
                data = response.json()

            for item in data.get("items", []):
                vid_id = item.get("id")
                stats = item.get("statistics", {})
                views = int(stats.get("viewCount", 0))
                view_counts[vid_id] = views

        except Exception as e:
            logger.error(f"YouTube video stats fetch failed: {e}")

        return view_counts

    @staticmethod
    def _get_recent_date() -> str:
        """Get ISO date string for 7 days ago (only recent videos)"""
        from datetime import timedelta
        week_ago = datetime.utcnow() - timedelta(days=7)
        return week_ago.strftime("%Y-%m-%dT00:00:00Z")

    @staticmethod
    def _extract_products_from_title(title: str) -> List[str]:
        """
        Extract potential product names from a YouTube video title.
        Uses regex patterns to find product mentions.
        """
        products = []

        # Clean title
        title_clean = re.sub(r'[|🔥🎮📱💻🎧⚡️✅❌]', ' ', title)
        title_clean = re.sub(r'\s+', ' ', title_clean).strip()

        # Pattern: "Best <Product> India" or "Top <N> <Products>"
        patterns = [
            r'(?:best|top)\s+(\d+\s+)?(.+?)(?:\s+in\s+india|\s+under|\s+for|\s+20\d{2})',
            r'(.+?)\s+(?:review|unboxing|hands.?on|first.?look)',
            r'(?:new|latest)\s+(.+?)(?:\s+launch|\s+in\s+india|\s+20\d{2})',
        ]

        for pattern in patterns:
            matches = re.findall(pattern, title_clean, re.IGNORECASE)
            for match in matches:
                if isinstance(match, tuple):
                    # Take the last non-empty group
                    product = next((m.strip() for m in reversed(match) if m.strip()), "")
                else:
                    product = match.strip()

                if product and len(product) > 2 and len(product) < 80:
                    products.append(product)

        return products
