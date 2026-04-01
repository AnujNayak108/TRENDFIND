"""
Native Scraper Service - Content extraction using native HTTP requests instead of third party APIs
"""
import httpx
from bs4 import BeautifulSoup
from typing import Dict, Optional, Any


class NativeScraperService:
    """Service for extracting structured data using native httpx requests"""

    @staticmethod
    async def extract_trending_topics(url: str, platform: str) -> list[Dict[str, Any]]:
        """
        Use native HTTP requests to extract a list of trending topics or top posts from a given URL.
        """
        trends = []
        try:
            async with httpx.AsyncClient(timeout=15.0) as client:
                if platform == "reddit":
                    json_url = url
                    if not json_url.endswith('.json'):
                        if "/?" in json_url:
                            json_url = json_url.replace("/?", ".json?")
                        elif json_url.endswith("/"):
                            json_url = json_url[:-1] + ".json"
                        else:
                            json_url += ".json"
                    
                    # Reddit expects a specific User-Agent format, otherwise it may return 429 Too Many Requests
                    headers = {"User-Agent": "TrendFind Bot 1.0 (by /u/TrendFinderBot)"}
                    response = await client.get(json_url, headers=headers)
                    response.raise_for_status()
                    
                    data = response.json()
                    posts = data.get("data", {}).get("children", [])
                    
                    for post in posts:
                        p_data = post.get("data", {})
                        if not p_data: 
                            continue
                        
                        trend = {
                            "title": p_data.get("title", ""),
                            "description": p_data.get("selftext", ""),
                            "upvotes": p_data.get("ups", 0),
                            "comments": p_data.get("num_comments", 0),
                            "thumbnail": p_data.get("thumbnail") if p_data.get("thumbnail") and str(p_data.get("thumbnail")).startswith("http") else None,
                            "url": f"https://www.reddit.com{p_data.get('permalink')}" if p_data.get("permalink") else p_data.get("url")
                        }
                        if not trend["description"] and trend["url"]:
                            trend["description"] = f"Link: {trend['url']}"
                        
                        trends.append(trend)
                        
                else:
                    response = await client.get(url, headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"})
                    response.raise_for_status()
                    soup = BeautifulSoup(response.text, 'html.parser')
                    title = soup.find('title').get_text(strip=True) if soup.find('title') else url
                    desc_meta = soup.find('meta', attrs={'name': 'description'}) or soup.find('meta', attrs={'property': 'og:description'})
                    description = desc_meta['content'] if desc_meta else ""
                    trends.append({
                        "title": title,
                        "description": description,
                        "upvotes": 0,
                        "comments": 0,
                        "url": url
                    })
        except Exception as e:
            print(f"Native extraction failed for {url}: {e}")
            
        return trends

    @staticmethod
    async def scrape_product_details(url: str) -> Optional[Dict[str, Any]]:
        """
        Scrape a product details page using native HTTP
        Returns normalized structured data
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
            async with httpx.AsyncClient(timeout=15.0) as client:
                response = await client.get(url, headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"})
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
            print(f"Native product details scrape failed for {url}: {e}")
            
        return normalized
