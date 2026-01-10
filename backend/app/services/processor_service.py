"""
Processor Service - Process trends and extract products
"""
from typing import List, Dict
from datetime import datetime
from app.services.trend_service import TrendService
from app.services.product_service import ProductService
from app.services.nlp_service import NLPService
from app.services.firecrawl_service import FirecrawlService
from app.models.product import ProductCreate, TrendSource
from app.models.buy_link import BuyLinkCreate


class ProcessorService:
    """Service for processing trends and extracting products"""
    
    @staticmethod
    async def process_trends() -> Dict[str, int]:
        """
        Process all unprocessed trends to extract products
        Returns statistics about processing
        """
        stats = {
            "trends_processed": 0,
            "products_detected": 0,
            "products_created": 0,
            "products_merged": 0
        }
        
        # Get unprocessed trends
        unprocessed_trends = await TrendService.get_unprocessed()
        
        for trend in unprocessed_trends:
            try:
                # Extract product names from trend content
                text = f"{trend.title} {trend.content or ''}"
                product_names = NLPService.extract_product_names(text)
                
                if not product_names:
                    # Mark as processed even if no products found
                    await TrendService.mark_as_processed(str(trend.id))
                    stats["trends_processed"] += 1
                    continue
                
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
                print(f"Error processing trend {trend.id}: {e}")
                # Continue with next trend
                continue
        
        return stats
    
    @staticmethod
    async def _process_product(product_name: str, trend, stats: Dict[str, int]):
        """Process a single product from a trend"""
        # Normalize product name
        normalized_name = NLPService.normalize_product_name(product_name)
        
        # Check for existing product (deduplication)
        existing_product = await ProductService.get_by_normalized_name(normalized_name)
        
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
            
            # Update trend score (simple: count of sources * 10)
            updated_score = len(existing_product.trend_sources) * 10 + 10
            await ProductService.update_trend_score(str(existing_product.id), updated_score)
            
            stats["products_merged"] += 1
            
            # Try to get more info from Firecrawl if we don't have it
            if not existing_product.short_description and trend.source_url:
                firecrawl_data = await FirecrawlService.scrape_url(trend.source_url)
                if firecrawl_data and firecrawl_data.get("product_name"):
                    # Update product with Firecrawl data
                    update_data = {}
                    if firecrawl_data.get("short_description"):
                        update_data["short_description"] = firecrawl_data["short_description"]
                    if firecrawl_data.get("category"):
                        update_data["category"] = firecrawl_data["category"]
                    if firecrawl_data.get("price"):
                        update_data["price"] = firecrawl_data["price"]
                    if firecrawl_data.get("raw_response"):
                        update_data["firecrawl_data"] = {
                            "raw_response": firecrawl_data["raw_response"],
                            "extracted_at": datetime.utcnow()
                        }
                    
                    if update_data:
                        await ProductService.update(str(existing_product.id), update_data)
        else:
            # Create new product
            product_data = ProductCreate(
                product_name=product_name,
                normalized_name=normalized_name,
                category=category,
                trend_sources=[trend_source],
                trend_score=10.0,
                tags=[]  # TODO: Extract tags from text
            )
            
            # Try to enrich with Firecrawl data
            if trend.source_url:
                firecrawl_data = await FirecrawlService.scrape_url(trend.source_url)
                if firecrawl_data:
                    if firecrawl_data.get("short_description"):
                        product_data.short_description = firecrawl_data["short_description"]
                    if firecrawl_data.get("category") and not product_data.category:
                        product_data.category = firecrawl_data["category"]
                    if firecrawl_data.get("price"):
                        product_data.price = firecrawl_data["price"]
                    if firecrawl_data.get("raw_response"):
                        product_data.firecrawl_data = {
                            "raw_response": firecrawl_data["raw_response"],
                            "extracted_at": datetime.utcnow()
                        }
            
            await ProductService.create(product_data)
            stats["products_created"] += 1
            
            # Create mock buy links (in production, would scrape e-commerce sites)
            await ProcessorService._create_mock_buy_links(product_data.product_name, product_data.normalized_name)
    
    @staticmethod
    async def _create_mock_buy_links(product_name: str, normalized_name: str):
        """Create mock buy links for a product (placeholder for real e-commerce scraping)"""
        from app.services.buy_link_service import BuyLinkService
        
        # Get the product we just created
        product = await ProductService.get_by_normalized_name(normalized_name)
        if not product:
            return
        
        # Mock Amazon link
        amazon_link = BuyLinkCreate(
            product_id=str(product.id),
            platform="amazon",
            url=f"https://amazon.com/s?k={product_name.replace(' ', '+')}",
            title=f"{product_name} - Buy on Amazon",
            price=249.99,  # Mock price
            currency="USD",
            availability="in_stock",
            rating=4.5,
            review_count=1234,
            metadata={"mock": True}
        )
        
        await BuyLinkService.create(amazon_link)

