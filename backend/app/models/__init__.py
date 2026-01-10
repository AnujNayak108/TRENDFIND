"""
Database Models
"""
from app.models.trend import Trend, TrendCreate, TrendInDB
from app.models.product import Product, ProductCreate, ProductInDB, ProductWithBuyLinks
from app.models.buy_link import BuyLink, BuyLinkCreate, BuyLinkInDB

__all__ = [
    "Trend",
    "TrendCreate",
    "TrendInDB",
    "Product",
    "ProductCreate",
    "ProductInDB",
    "ProductWithBuyLinks",
    "BuyLink",
    "BuyLinkCreate",
    "BuyLinkInDB",
]

