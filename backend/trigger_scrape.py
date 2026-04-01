import asyncio
import sys
import os

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from app.services.scraper_service import ScraperService
from app.services.processor_service import ProcessorService
from app.core.database import connect_to_mongo, close_mongo_connection

async def manual_scrape():
    try:
        await connect_to_mongo()
        
        print("Starting manual scrape...")
        scrape_results = await ScraperService.run_scrape()
        print(f"Scrape results: {scrape_results}")
        
        print("Starting manual process...")
        process_results = await ProcessorService.process_trends()
        print(f"Process results: {process_results}")
        
    except Exception as e:
        print(f"Error during scrape/process: {e}")
    finally:
        await close_mongo_connection()

if __name__ == "__main__":
    asyncio.run(manual_scrape())
