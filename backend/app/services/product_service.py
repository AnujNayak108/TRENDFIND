"""
Product Service - Database operations for products
"""
from typing import List, Optional
from datetime import datetime
from bson import ObjectId
from app.core.database import get_database
from app.models.product import Product, ProductCreate, ProductInDB, TrendSource
from app.services.buy_link_service import BuyLinkService


class ProductService:
    """Service for managing products in the database"""
    
    @staticmethod
    async def create(product_data: ProductCreate) -> ProductInDB:
        """Create a new product"""
        db = await get_database()
        product_dict = product_data.model_dump()
        product_dict["first_detected_at"] = datetime.utcnow()
        product_dict["last_updated_at"] = datetime.utcnow()
        
        result = await db.products.insert_one(product_dict)
        created_product = await db.products.find_one({"_id": result.inserted_id})
        
        return ProductInDB(**created_product)
    
    @staticmethod
    async def get_all(
        skip: int = 0,
        limit: int = 50,
        category: Optional[str] = None,
        min_trend_score: Optional[float] = None
    ) -> List[Product]:
        """Get all products with optional filtering"""
        try:
            db = await get_database()
            query = {}
            
            if category:
                query["category"] = category
            if min_trend_score is not None:
                query["trend_score"] = {"$gte": min_trend_score}
            
            cursor = db.products.find(query).sort("trend_score", -1).skip(skip).limit(limit)
            products = await cursor.to_list(length=limit)
            
            # Convert MongoDB documents to Product models
            result = []
            for product in products:
                try:
                    # Convert _id to id for Pydantic model
                    # Pydantic will use the alias to map _id -> id
                    product_doc = dict(product)
                    
                    # Create Product instance - Pydantic will handle _id -> id mapping via alias
                    product_model = Product(**product_doc)
                    result.append(product_model)
                except Exception as e:
                    # Skip products that can't be parsed
                    print(f"Warning: Skipping product due to parsing error: {e}")
                    print(f"  Product keys: {list(product.keys())}")
                    if "_id" in product:
                        print(f"  _id type: {type(product['_id'])}")
                    import traceback
                    traceback.print_exc()
                    continue
            
            print(f"Successfully loaded {len(result)} products from database")
            return result
        except Exception as e:
            # If database connection fails, return empty list
            print(f"Error fetching products: {e}")
            return []
    
    @staticmethod
    async def get_by_id(product_id: str) -> Optional[Product]:
        """Get a product by ID"""
        db = await get_database()
        # Validate ObjectId to prevent exceptions for invalid IDs (e.g., 'undefined')
        if not ObjectId.is_valid(product_id):
            return None
        product = await db.products.find_one({"_id": ObjectId(product_id)})
        
        if not product:
            return None
        
        return Product(**product)
    
    @staticmethod
    async def get_by_normalized_name(normalized_name: str) -> Optional[ProductInDB]:
        """Get a product by normalized name (for deduplication)"""
        db = await get_database()
        product = await db.products.find_one({"normalized_name": normalized_name})
        
        if not product:
            return None
        
        return ProductInDB(**product)
    
    @staticmethod
    async def update(product_id: str, update_data: dict) -> bool:
        """Update a product"""
        db = await get_database()
        update_data["last_updated_at"] = datetime.utcnow()

        # Validate ObjectId
        if not ObjectId.is_valid(product_id):
            return False
        
        result = await db.products.update_one(
            {"_id": ObjectId(product_id)},
            {"$set": update_data}
        )
        
        return result.modified_count > 0
    
    @staticmethod
    async def add_trend_source(product_id: str, trend_source: TrendSource) -> bool:
        """Add a trend source to a product"""
        db = await get_database()

        # Validate ObjectId
        if not ObjectId.is_valid(product_id):
            return False
        
        result = await db.products.update_one(
            {"_id": ObjectId(product_id)},
            {
                "$addToSet": {"trend_sources": trend_source.model_dump()},
                "$set": {"last_updated_at": datetime.utcnow()}
            }
        )
        
        return result.modified_count > 0
    
    @staticmethod
    async def update_trend_score(product_id: str, new_score: float) -> bool:
        """Update trend score for a product"""
        return await ProductService.update(product_id, {"trend_score": new_score})
    
    @staticmethod
    async def get_product_with_buy_links(product_id: str):
        """Get a product with its associated buy links"""
        from app.models.product import ProductWithBuyLinks
        from app.models.buy_link import BuyLink
        
        product = await ProductService.get_by_id(product_id)
        if not product:
            return None
        
        try:
            buy_links = await BuyLinkService.get_by_product_id(product_id)
        except Exception as e:
            print(f"Error fetching buy links: {e}")
            buy_links = []
        
        # Convert product to dict for serialization
        product_dict = product.model_dump(mode='json')
        # Ensure id is a string
        if 'id' in product_dict:
            product_dict['id'] = str(product_dict['id'])
        
        # Serialize buy links properly as dicts
        buy_links_serialized = []
        for link in buy_links:
            try:
                # Convert BuyLink to dict and ensure all fields are properly serialized
                link_dict = link.model_dump(mode='json', exclude_none=True)
                # Ensure id is a string (handle both _id and id)
                if '_id' in link_dict:
                    link_dict['id'] = str(link_dict['_id'])
                    del link_dict['_id']
                if 'id' in link_dict and link_dict['id']:
                    link_dict['id'] = str(link_dict['id'])
                # Ensure product_id is a string
                if 'product_id' in link_dict:
                    link_dict['product_id'] = str(link_dict['product_id'])
                # Remove any None values to avoid validation issues
                link_dict = {k: v for k, v in link_dict.items() if v is not None}
                buy_links_serialized.append(link_dict)
            except Exception as e:
                print(f"Warning: Error serializing buy link: {e}")
                import traceback
                traceback.print_exc()
                continue
        
        # Create ProductWithBuyLinks - pass buy_links as list of dicts
        product_dict["buy_links"] = buy_links_serialized
        
        return ProductWithBuyLinks(**product_dict)

