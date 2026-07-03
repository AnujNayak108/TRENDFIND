"""
Database Cleanup Script
Wipes existing messy seeded data and recreates indexes.
Run this before starting the new pipeline to get clean results.

Usage:
    cd backend
    python cleanup_db.py
"""
import asyncio
import sys
import os

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.core.database import connect_to_mongo, close_mongo_connection, get_database, create_indexes


async def cleanup():
    """Wipe all collections and recreate indexes"""
    try:
        await connect_to_mongo()
        db = await get_database()

        print("\n--- TrendFind Database Cleanup ---")
        print("=" * 40)

        # Count existing documents
        trends_count = await db.trends.count_documents({})
        products_count = await db.products.count_documents({})
        buy_links_count = await db.buy_links.count_documents({})

        print(f"\nCurrent data:")
        print(f"  • trends:    {trends_count} documents")
        print(f"  • products:  {products_count} documents")
        print(f"  • buy_links: {buy_links_count} documents")

        # Drop all documents from collections
        print("\nClearing collections...")
        result_trends = await db.trends.delete_many({})
        print(f"  OK trends:    deleted {result_trends.deleted_count} documents")

        result_products = await db.products.delete_many({})
        print(f"  OK products:  deleted {result_products.deleted_count} documents")

        result_buy_links = await db.buy_links.delete_many({})
        print(f"  OK buy_links: deleted {result_buy_links.deleted_count} documents")

        # Recreate indexes
        print("\nRecreating indexes...")
        await create_indexes()
        print("  OK All indexes recreated")

        print("\nSUCCESS Cleanup complete! Ready for fresh data.")
        print("   Run 'python trigger_scrape.py' to start the new pipeline.\n")

    except Exception as e:
        print(f"\nFAILED Cleanup failed: {e}")
        import traceback
        traceback.print_exc()
    finally:
        await close_mongo_connection()


if __name__ == "__main__":
    asyncio.run(cleanup())
