import asyncio
import sys
import os
import json

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.services.scraper_service import ScraperService
from app.services.processor_service import ProcessorService
from app.core.database import connect_to_mongo, close_mongo_connection

async def test_scraping():
    print("Testing scraper service directly...")
    
    # Run the scrape
    scrape_results = await ScraperService.run_scrape()
    print("Scrape results:")
    print(scrape_results)
    
    print("\nProcessing trends...")
    process_results = await ProcessorService.process_trends()
    print("Process results:")
    print(process_results)

if __name__ == "__main__":
    async def main():
        await connect_to_mongo()
        await test_scraping()
        await close_mongo_connection()

    asyncio.run(main())
