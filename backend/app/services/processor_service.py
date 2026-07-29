"""
Processor Service - Process trends and extract products with enhanced scoring.
Uses multi-source mention counting, recency decay, engagement weighting,
and cross-platform validation for trend scoring.
"""
import logging
from typing import List, Dict
import asyncio
from datetime import datetime, timedelta

from app.services.trend_service import TrendService
from app.services.product_service import ProductService
from app.services.nlp_service import NLPService
from app.services.native_scraper_service import NativeScraperService
from app.models.product import ProductCreate, TrendSource
from app.models.buy_link import BuyLinkCreate

logger = logging.getLogger(__name__)


class ProcessorService:
    """Service for processing trends and extracting products with India-focused scoring"""

    @staticmethod
    async def process_trends() -> Dict[str, int]:
        """
        Process all unprocessed trends to extract products.
        Returns statistics about processing.
        """
        stats = {
            "trends_processed": 0,
            "products_detected": 0,
            "products_created": 0,
            "products_merged": 0
        }

        # Get unprocessed trends
        unprocessed_trends = await TrendService.get_unprocessed()

        semaphore = asyncio.Semaphore(10)

        async def process_single_trend(trend):
            async with semaphore:
                try:
                    # Extract product names from trend content
                    text = f"{trend.title} {trend.content or ''}"
                    product_names = NLPService.extract_product_names(text)

                    if not product_names:
                        # Mark as processed even if no products found
                        await TrendService.mark_as_processed(str(trend.id))
                        stats["trends_processed"] += 1
                        return

                    stats["products_detected"] += len(product_names)

                    # Process each potential product
                    for product_name in product_names:
                        await ProcessorService._process_product(
                            product_name,
                            trend,
                            stats
                        )

                    # Mark trend as processed
                    await TrendService.mark_as_processed(str(trend.id))
                    stats["trends_processed"] += 1

                except Exception as e:
                    logger.error(f"Error processing trend {trend.id}: {e}")

        # Run all trend processing tasks concurrently
        tasks = [process_single_trend(trend) for trend in unprocessed_trends]
        if tasks:
            await asyncio.gather(*tasks)

        return stats

    @staticmethod
    def _calculate_trend_score(
        mention_count: int,
        avg_upvotes: float,
        created_at: datetime,
        sources: List[TrendSource],
        google_trends_volume: float = 0.0,
    ) -> float:
        """
        Calculate trend score using the formula:
        score = (mention_count × 15) + (avg_upvotes × 0.1) + (recency_boost) 
                + (google_trends_volume × 0.5) + (cross_platform_bonus × 20)

        - recency_boost: +30 if last 6h, +20 if last 24h, +10 if last 48h
        - cross_platform_bonus: number of distinct platforms - 1 (if mentioned on 2+ platforms)
        """
        now = datetime.utcnow()

        # Mention count contribution
        mention_score = mention_count * 15

        # Engagement score (upvotes / views)
        engagement_score = avg_upvotes * 0.1

        # Recency boost based on most recent mention
        hours_since = (now - created_at).total_seconds() / 3600 if created_at else 999
        if hours_since <= 6:
            recency_boost = 30
        elif hours_since <= 24:
            recency_boost = 20
        elif hours_since <= 48:
            recency_boost = 10
        else:
            recency_boost = 0

        # Cross-platform bonus
        unique_platforms = set(s.source for s in sources)
        cross_platform_count = len(unique_platforms)
        cross_platform_bonus = max(0, cross_platform_count - 1) * 20

        # Google Trends volume contribution
        trends_score = google_trends_volume * 0.5

        total = mention_score + engagement_score + recency_boost + trends_score + cross_platform_bonus

        # Cap at 100
        return min(100.0, max(0.0, total))

    @staticmethod
    async def _process_product(product_name: str, trend, stats: Dict[str, int]):
        """Process a single product from a trend"""
        # Normalize product name
        normalized_name = NLPService.normalize_product_name(product_name)

        if not normalized_name or len(normalized_name) < 2:
            return

        # Check for existing product (deduplication with fuzzy matching)
        existing_product = await ProductService.get_by_normalized_name(normalized_name)

        # If exact match not found, try fuzzy matching against recent products
        if not existing_product:
            existing_product = await ProcessorService._fuzzy_find_product(normalized_name)

        # Extract category
        text = f"{trend.title} {trend.content or ''}"
        category = NLPService.extract_category(text, product_name)

        # Create trend source
        trend_source = TrendSource(
            trend_id=str(trend.id),
            source=trend.source,
            mentioned_at=trend.created_at
        )

        if existing_product:
            # Merge with existing product
            await ProductService.add_trend_source(str(existing_product.id), trend_source)

            # Calculate new trend score
            all_sources = list(existing_product.trend_sources) + [trend_source]
            avg_upvotes = trend.upvotes or 0
            new_score = ProcessorService._calculate_trend_score(
                mention_count=len(all_sources),
                avg_upvotes=avg_upvotes,
                created_at=trend.created_at,
                sources=all_sources,
            )
            await ProductService.update_trend_score(str(existing_product.id), new_score)

            # Update category if we didn't have one
            if not existing_product.category and category:
                await ProductService.update(str(existing_product.id), {"category": category})

            stats["products_merged"] += 1

            # Try to get more info from NativeScraper if we don't have it
            if not existing_product.short_description and trend.source_url:
                try:
                    scraper_data = await NativeScraperService.scrape_product_details(trend.source_url)
                    if scraper_data and scraper_data.get("product_name"):
                        update_data = {}
                        if scraper_data.get("short_description"):
                            update_data["short_description"] = scraper_data["short_description"]
                        if scraper_data.get("image_url"):
                            update_data["image_url"] = scraper_data["image_url"]
                        if update_data:
                            await ProductService.update(str(existing_product.id), update_data)
                except Exception as e:
                    logger.warning(f"Product enrichment failed: {e}")

        else:
            # Get image from trend metadata
            image_url = None
            if trend.metadata:
                image_url = trend.metadata.get("thumbnail")

            # Create new product
            initial_sources = [trend_source]
            initial_score = ProcessorService._calculate_trend_score(
                mention_count=1,
                avg_upvotes=trend.upvotes or 0,
                created_at=trend.created_at,
                sources=initial_sources,
            )

            product_data = ProductCreate(
                product_name=product_name,
                normalized_name=normalized_name,
                category=category,
                image_url=image_url,
                trend_sources=initial_sources,
                trend_score=initial_score,
                tags=[]
            )

            # Try to enrich with NativeScraper data
            if trend.source_url:
                try:
                    scraper_data = await NativeScraperService.scrape_product_details(trend.source_url)
                    if scraper_data:
                        if scraper_data.get("short_description"):
                            product_data.short_description = scraper_data["short_description"]
                        if scraper_data.get("category") and not product_data.category:
                            product_data.category = scraper_data["category"]
                        if scraper_data.get("image_url") and not product_data.image_url:
                            product_data.image_url = scraper_data["image_url"]
                except Exception as e:
                    logger.warning(f"Product enrichment failed: {e}")

            await ProductService.create(product_data)
            stats["products_created"] += 1

            # Create buy links for multiple Indian platforms
            await ProcessorService._create_indian_buy_links(
                product_data.product_name,
                product_data.normalized_name,
                product_data.category
            )

    @staticmethod
    async def _fuzzy_find_product(normalized_name: str):
        """
        Try to find an existing product using fuzzy matching.
        Checks against recent products in the database.
        """
        try:
            from app.core.database import get_database
            db = await get_database()

            # Get recent products (last 100)
            cursor = db.products.find().sort("last_updated_at", -1).limit(100)
            recent_products = await cursor.to_list(length=100)

            for product_doc in recent_products:
                existing_normalized = product_doc.get("normalized_name", "")
                if NLPService.is_duplicate(normalized_name, existing_normalized):
                    from app.models.product import ProductInDB
                    return ProductInDB(**product_doc)

        except Exception as e:
            logger.warning(f"Fuzzy product search failed: {e}")

        return None

    @staticmethod
    async def _create_indian_buy_links(product_name: str, normalized_name: str, category: str = None):
        """Create buy links for multiple Indian e-commerce platforms based on product category"""
        from app.services.buy_link_service import BuyLinkService

        # Get the product we just created
        product = await ProductService.get_by_normalized_name(normalized_name)
        if not product:
            return

        product_id = str(product.id)
        search_term = product_name.replace(' ', '+')

        # Determine which platforms to generate links for based on category
        category_lower = (category or "").lower()

        # Default platforms for all categories
        platforms = [
            {
                "platform": "amazon",
                "url": f"https://www.amazon.in/s?k={search_term}",
                "title": f"Search {product_name} on Amazon India",
            },
            {
                "platform": "flipkart",
                "url": f"https://www.flipkart.com/search?q={search_term}",
                "title": f"Search {product_name} on Flipkart",
            },
        ]

        # Add category-specific platforms
        if "electronics" in category_lower or "audio" in category_lower or "gaming" in category_lower or "computer" in category_lower:
            platforms.append({
                "platform": "croma",
                "url": f"https://www.croma.com/searchB?q={search_term}",
                "title": f"Search {product_name} on Croma",
            })
        elif "fashion" in category_lower or "clothing" in category_lower or "footwear" in category_lower:
            platforms.append({
                "platform": "myntra",
                "url": f"https://www.myntra.com/{search_term.replace('+', '-').lower()}",
                "title": f"Search {product_name} on Myntra",
            })
        elif "beauty" in category_lower or "skincare" in category_lower or "haircare" in category_lower or "makeup" in category_lower or "grooming" in category_lower:
            platforms.append({
                "platform": "nykaa",
                "url": f"https://www.nykaa.com/search/result/?q={search_term}",
                "title": f"Search {product_name} on Nykaa",
            })

        for platform_info in platforms:
            try:
                buy_link = BuyLinkCreate(
                    product_id=product_id,
                    platform=platform_info["platform"],
                    url=platform_info["url"],
                    title=platform_info["title"],
                    price=None,
                    currency="INR",
                    availability="check_site",
                    metadata={"source": "search_link", "country": "IN"}
                )
                await BuyLinkService.create(buy_link)
            except Exception as e:
                logger.warning(f"Failed to create {platform_info['platform']} buy link: {e}")
