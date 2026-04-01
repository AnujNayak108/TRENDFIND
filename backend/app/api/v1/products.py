"""
Products API Routes
"""
from typing import Optional, List, Dict, Any
from fastapi import APIRouter, Query, HTTPException
from fastapi.responses import JSONResponse
from app.services.product_service import ProductService
from app.models.product import Product, ProductWithBuyLinks
from bson import ObjectId

router = APIRouter()


def serialize_product(product: Product) -> Dict[str, Any]:
    """Serialize product ensuring id is always a string"""
    data = product.model_dump(mode='json', by_alias=False)
    
    # Robustly get ID either from model attribute or dict dump
    product_id = getattr(product, "id", None) or getattr(product, "_id", None)
    if product_id is None:
        d_alias = product.model_dump(mode='json', by_alias=True)
        product_id = d_alias.get('_id') or d_alias.get('id')
        
    if product_id is not None:
        data['id'] = str(product_id)
        
    if '_id' in data:
        del data['_id']
        
    return data


@router.get("/products")
async def get_products(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    category: Optional[str] = Query(None, description="Filter by category"),
    min_trend_score: Optional[float] = Query(None, ge=0, le=100, description="Minimum trend score")
):
    """
    Get all products with optional filtering
    Returns products sorted by trend score (descending)
    """
    try:
        products = await ProductService.get_all(
            skip=skip,
            limit=limit,
            category=category,
            min_trend_score=min_trend_score
        )
        # Serialize products ensuring id is always a string
        serialized_products = [serialize_product(p) for p in products]
        print(f"Returning {len(serialized_products)} products")
        if serialized_products:
            print(f"Sample product id type: {type(serialized_products[0].get('id'))}")
        return serialized_products
    except ConnectionError as e:
        # Return empty list if database is not connected
        return []
    except Exception as e:
        print(f"Error in get_products: {e}")
        import traceback
        traceback.print_exc()
        return []


@router.get("/products/{product_id}")
async def get_product(product_id: str):
    """
    Get a specific product by ID with associated buy links
    """
    try:
        product = await ProductService.get_product_with_buy_links(product_id)
        if not product:
            raise HTTPException(status_code=404, detail="Product not found")
        
        # Serialize product ensuring id is always a string
        product_dict = product.model_dump(mode='json')
        if 'id' in product_dict:
            product_dict['id'] = str(product_dict['id'])
        
        # Ensure buy_links are properly serialized
        if 'buy_links' in product_dict:
            for link in product_dict['buy_links']:
                if 'id' in link:
                    link['id'] = str(link['id'])
                if 'product_id' in link:
                    link['product_id'] = str(link['product_id'])
        
        return product_dict
    except HTTPException:
        raise
    except Exception as e:
        print(f"Error in get_product: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

