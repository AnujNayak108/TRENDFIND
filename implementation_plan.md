# TrendFind Rebuild — Real Indian Trending Products Discovery

## Problem Statement

The current TrendFind app has **critical issues** that prevent it from delivering real value:

1. **Broken/useless data sources**: Scrapes `r/BuyItForLifeIndia` (tiny/dead subreddit) and a non-existent Instagram URL. The Firecrawl API returns 403 Forbidden. No Google Trends integration despite `pytrends` being in requirements.
2. **No actual product signal filtering**: The NLP pipeline (`spaCy en_core_web_sm`) treats every noun chunk ≥2 words as a "product" — producing messy results like "everyone thing", "best coffee", etc. There's no classification of whether something is actually a purchasable product.
3. **No Indian e-commerce context**: Buy links are just `amazon.in/s?k={name}` search URLs with no verification that the product actually exists on the platform or is currently trending in India.
4. **No trending signal**: "Trending" is just order-of-appearance from Reddit posts. There's no velocity, volume, or recency scoring.

## Proposed Architecture — "What Will Actually Work"

### Core Insight
Instead of trying to **infer** products from social media text (which is inherently noisy), we should **combine multiple real signals** from sources that are explicitly about products trending in India:

```
┌─────────────────────────────────────────────────────────────────────┐
│                        DATA COLLECTION LAYER                        │
│                                                                     │
│  ┌──────────────┐  ┌───────────────────┐  ┌─────────────────────┐  │
│  │ Google Trends │  │  Indian Reddit    │  │  YouTube India      │  │
│  │  (India, IN)  │  │  Subreddits       │  │  (Product Reviews)  │  │
│  │              │  │  (deals/tech/     │  │                     │  │
│  │  • Daily     │  │   beauty)         │  │  • Search trending  │  │
│  │    trending  │  │                   │  │    product keywords │  │
│  │    searches  │  │  • .json endpoint │  │  • YouTube Data API │  │
│  │  • Related   │  │  • Top posts/week │  │    (free tier)      │  │
│  │    queries   │  │  • Upvote signal  │  │  • View count signal│  │
│  └──────┬───────┘  └────────┬──────────┘  └──────────┬──────────┘  │
│         │                   │                        │              │
└─────────┼───────────────────┼────────────────────────┼──────────────┘
          │                   │                        │
          ▼                   ▼                        ▼
┌─────────────────────────────────────────────────────────────────────┐
│                     INTELLIGENCE LAYER (NEW)                        │
│                                                                     │
│  ┌────────────────────────────────────────────────────────────────┐ │
│  │  1. Product Extraction (Enhanced NLP)                         │ │
│  │     • Keyword-list + spaCy NER combined approach              │ │
│  │     • India-specific product category whitelist               │ │
│  │     • Filter OUT non-products (people, places, events)        │ │
│  └────────────────────────────────────────────────────────────────┘ │
│  ┌────────────────────────────────────────────────────────────────┐ │
│  │  2. Trend Scoring Engine                                      │ │
│  │     • Multi-source mention count (cross-platform validation)  │ │
│  │     • Recency decay (newer = higher score)                    │ │
│  │     • Engagement weighting (upvotes, views, comments)         │ │
│  │     • Google Trends volume normalization                      │ │
│  └────────────────────────────────────────────────────────────────┘ │
│  ┌────────────────────────────────────────────────────────────────┐ │
│  │  3. India Context Enrichment                                  │ │
│  │     • Amazon.in search link generation                        │ │
│  │     • Flipkart search link generation                         │ │
│  │     • Price range estimation from search term                 │ │
│  │     • Category auto-assignment (India-relevant taxonomy)      │ │
│  └────────────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────────────┘
          │
          ▼
┌─────────────────────────────────────────────────────────────────────┐
│                         STORAGE LAYER                               │
│                                                                     │
│  MongoDB Atlas (existing)                                           │
│  ┌─────────────┐  ┌─────────────┐  ┌──────────────┐               │
│  │   trends     │  │  products   │  │  buy_links   │               │
│  │  (raw data)  │  │ (enriched)  │  │ (multi-store)│               │
│  └─────────────┘  └─────────────┘  └──────────────┘               │
└─────────────────────────────────────────────────────────────────────┘
          │
          ▼
┌─────────────────────────────────────────────────────────────────────┐
│                        PRESENTATION LAYER                           │
│                                                                     │
│  React + Vite Frontend (redesigned)                                 │
│  ┌──────────┐  ┌──────────────┐  ┌───────────────┐                │
│  │ Home     │  │ Product Grid │  │ Product Detail│                │
│  │ (Hero +  │  │ (Filters,   │  │ (Buy links,  │                │
│  │  Top 5)  │  │  Categories) │  │  Sources)    │                │
│  └──────────┘  └──────────────┘  └───────────────┘                │
└─────────────────────────────────────────────────────────────────────┘
```

---

## User Review Required

> [!IMPORTANT]
> **API Keys**: Your YouTube Data API key (`AIzaSyB...`) is already in `.env`. Google Trends via `pytrends` requires no key. Reddit `.json` endpoints require no key (just rate limiting). No additional paid APIs are needed for this plan.

> [!WARNING]
> **Exposed Secrets**: Your `.env` file contains your MongoDB Atlas password and API keys. These are currently committed to git history. After we fix the app, you should rotate these credentials.

> [!IMPORTANT]
> **Data Freshness vs. Cost**: This plan uses entirely **free** data sources. The trade-off is that data will update every 60 minutes via the scheduler (configurable). For real-time data, you'd need paid APIs like SerpApi. Is the 60-minute refresh acceptable?

---

## Open Questions

> [!IMPORTANT]
> **1. Product Categories**: Which product categories matter most to you for the Indian audience? The plan currently covers:
> - Electronics (phones, laptops, earbuds, smartwatches)
> - Fashion (clothing, shoes, accessories)
> - Home & Kitchen (appliances, gadgets)
> - Beauty & Personal Care
> - Gaming (consoles, peripherals)
> - Books & Media
> 
> Should I add/remove any?

> [!IMPORTANT]  
> **2. Frontend Redesign**: The current frontend is functional but basic. Should I:
> - **Option A**: Keep the existing React + Tailwind frontend and just fix the data pipeline (faster)
> - **Option B**: Also redesign the frontend for a premium look (takes longer but better result)

> [!IMPORTANT]
> **3. Deployment**: You have Render and Vercel configs. Should the solution work with the existing deployment setup, or are you only testing locally for now?

---

## Proposed Changes

### Component 1: Data Sources (Complete Rewrite)

Replace the broken scraper sources with **3 reliable, free data pipelines** for India.

#### [MODIFY] [scraper_service.py](file:///c:/Users/BIT/Desktop/timepass/backend/app/services/scraper_service.py)
- **Remove** dead Instagram URL and broken `r/BuyItForLifeIndia`
- **Add** curated list of active Indian subreddits:
  - `r/IndianGaming` (1M+ members, very active product discussions)
  - `r/india` (2M+ members, weekly product/deal threads)  
  - `r/dealsforindia` (dedicated deals community)
  - `r/mobilerepair` / `r/GadgetDeals` (tech-focused)
- **Add** Google Trends India scraper using `pytrends` library (already in requirements)
  - Daily trending searches filtered to India (`geo='IN'`)
  - Related queries for product-related trending terms
- **Add** YouTube India trending product videos using existing YouTube Data API key
  - Search for "best [product] India 2026", "trending products India"
  - Extract product names from video titles

#### [NEW] [google_trends_scraper.py](file:///c:/Users/BIT/Desktop/timepass/backend/app/services/google_trends_scraper.py)
New dedicated service for Google Trends India data:
- `get_trending_searches(geo='IN')` — daily trending searches
- `get_related_queries(keyword, geo='IN')` — related product queries
- `get_interest_over_time(keywords, geo='IN')` — trend velocity for scoring
- Built-in rate limiting and error handling for pytrends
- Product-keyword filtering (only keep trends that match product categories)

#### [NEW] [youtube_scraper.py](file:///c:/Users/BIT/Desktop/timepass/backend/app/services/youtube_scraper.py)
New service for YouTube India product trends:
- Search YouTube for product review/unboxing videos trending in India
- Extract product names from video titles using regex + NLP
- Use view count and publish date as trending signals
- Uses existing `YOUTUBE_API_KEY` from `.env`

#### [MODIFY] [native_scraper_service.py](file:///c:/Users/BIT/Desktop/timepass/backend/app/services/native_scraper_service.py)
- Improve Reddit JSON scraping with better User-Agent rotation
- Add retry logic with exponential backoff
- Add response validation to filter low-quality posts
- Filter posts by minimum upvote threshold (e.g., ≥10 upvotes)

---

### Component 2: Intelligence Layer (Major Enhancement)

#### [MODIFY] [nlp_service.py](file:///c:/Users/BIT/Desktop/timepass/backend/app/services/nlp_service.py)
**This is the most critical fix.** Current NLP extracts garbage. New approach:

1. **India-specific product keyword whitelist**: A curated dictionary of ~200 product keywords commonly sold in India (e.g., "earbuds", "kurta", "mixer grinder", "inverter AC", "pressure cooker")
2. **Brand name database**: ~100 popular Indian/global brands (boAt, Noise, Realme, OnePlus, Crompton, Prestige, etc.)
3. **Negative filter list**: Words that should never be products ("Modi", "India", "price", "review", "best", "vs", etc.)
4. **Hybrid extraction**: 
   - First pass: spaCy NER for ORG/PRODUCT entities
   - Second pass: Keyword match against whitelist
   - Third pass: Brand + category pattern matching ("boAt Airdopes" → product)
   - Scoring: Weight by match confidence
5. **India-specific category taxonomy** with subcategories relevant to Indian e-commerce

#### [MODIFY] [processor_service.py](file:///c:/Users/BIT/Desktop/timepass/backend/app/services/processor_service.py)
- **New trend scoring algorithm**:
  ```
  score = (mention_count × 15) + (avg_upvotes × 0.1) + (recency_boost) + (google_trends_volume × 0.5) + (cross_platform_bonus × 20)
  ```
  - `recency_boost`: +30 if detected in last 6 hours, +20 if last 24h, +10 if last 48h
  - `cross_platform_bonus`: If mentioned on 2+ platforms (Reddit + Google Trends), big boost
- **Better deduplication**: Use fuzzy matching + brand normalization ("boAt Airdopes 141" ≈ "Boat Airdopes")
- **Image enrichment**: Try to fetch product image from Google search or Open Graph

---

### Component 3: Buy Links (India E-commerce)

#### [MODIFY] [buy_link_service.py](file:///c:/Users/BIT/Desktop/timepass/backend/app/services/buy_link_service.py)
- Generate buy links for **multiple Indian platforms**:
  - `amazon.in/s?k={product_name}` (Amazon India)
  - `flipkart.com/search?q={product_name}` (Flipkart)
  - `croma.com/searchB?q={product_name}` (Croma — electronics)
  - `myntra.com/{product_name}` (Myntra — fashion)
- Auto-select relevant platforms based on product category:
  - Electronics → Amazon, Flipkart, Croma
  - Fashion → Myntra, Amazon, Flipkart
  - Home & Kitchen → Amazon, Flipkart
  - Beauty → Nykaa (nykaa.com), Amazon, Flipkart

---

### Component 4: Configuration & Environment

#### [MODIFY] [config.py](file:///c:/Users/BIT/Desktop/timepass/backend/app/core/config.py)
- Add configuration for new scrapers:
  - `GOOGLE_TRENDS_GEO` = `"IN"` (India)
  - `REDDIT_SUBREDDITS` = list of target subreddits
  - `REDDIT_MIN_UPVOTES` = `10` (filter threshold)
  - `YOUTUBE_SEARCH_QUERIES` = product-related search templates
  - `SCRAPE_INTERVAL_MINUTES` = `30` (more frequent)

#### [MODIFY] [.env](file:///c:/Users/BIT/Desktop/timepass/backend/.env)
- Remove the stray ` ``` ` at the end of the file (line 22 — this is a syntax error!)
- Clean up unused Reddit/Twitter API key placeholders

---

### Component 5: Database Cleanup

#### [NEW] [cleanup_db.py](file:///c:/Users/BIT/Desktop/timepass/backend/cleanup_db.py)
- Script to wipe the existing messy seeded data
- Clear all 3 collections (trends, products, buy_links) 
- Rerun indexes

---

### Component 6: Frontend Fixes (Minimal — data-focused)

#### [MODIFY] [api.js](file:///c:/Users/BIT/Desktop/timepass/frontend/src/services/api.js)
- Increase timeout from 10s to 30s (scraping takes time)

#### [MODIFY] [ProductList.jsx](file:///c:/Users/BIT/Desktop/timepass/frontend/src/pages/ProductList.jsx)
- Show "Source" badges (Google Trends, Reddit, YouTube)
- Show trend score visually
- Add "Last Updated" timestamp
- Handle empty state better (show "Scraping in progress..." instead of empty grid)

#### [MODIFY] [ProductDetail.jsx](file:///c:/Users/BIT/Desktop/timepass/frontend/src/pages/ProductDetail.jsx)
- Show buy links for multiple Indian platforms (Amazon, Flipkart, etc.)
- Show which platforms detected this trend
- Show trending velocity indicator

---

## Verification Plan

### Automated Tests

```bash
# 1. Test Google Trends scraper independently
cd backend
python -c "from app.services.google_trends_scraper import GoogleTrendsScraper; import asyncio; asyncio.run(GoogleTrendsScraper.get_trending_searches())"

# 2. Test Reddit scraper with Indian subreddits
python -c "from app.services.native_scraper_service import NativeScraperService; import asyncio; print(asyncio.run(NativeScraperService.extract_trending_topics('https://www.reddit.com/r/IndianGaming/top/?t=week', 'reddit')))"

# 3. Test NLP product extraction with Indian text
python -c "from app.services.nlp_service import NLPService; print(NLPService.extract_product_names('Just bought boAt Airdopes 141 from Amazon India sale, amazing bass for 999 rupees'))"

# 4. Run the full scrape pipeline
python trigger_scrape.py

# 5. Verify products endpoint returns clean data
curl http://localhost:8000/api/v1/products
```

### Manual Verification
1. Start backend (`uvicorn app.main:app --reload --port 8000`)
2. Start frontend (`npm run dev`)
3. Wait for initial scrape to complete (~60 seconds)
4. Verify products page shows real Indian trending products
5. Verify product detail pages have working Amazon.in + Flipkart links
6. Verify no messy/garbage product names appear
7. Verify trend scores reflect actual popularity
