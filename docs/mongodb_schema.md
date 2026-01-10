# MongoDB Schema Design

## Collections

### 1. `trends` Collection
Stores raw trending topics from social media platforms.

```json
{
  "_id": ObjectId("..."),
  "source": "reddit",
  "source_url": "https://reddit.com/r/gadgets/...",
  "title": "New wireless earbuds taking over TikTok",
  "content": "Full post/comment content...",
  "subreddit": "gadgets",
  "upvotes": 1523,
  "comments": 87,
  "created_at": ISODate("2024-01-15T10:30:00Z"),
  "scraped_at": ISODate("2024-01-15T11:00:00Z"),
  "processed": false,
  "metadata": {
    "platform": "reddit",
    "post_id": "abc123"
  }
}
```

**Indexes:**
- `source` + `created_at` (compound, for querying by platform and date)
- `processed` (for finding unprocessed trends)
- `scraped_at` (for freshness queries)

---

### 2. `products` Collection
Stores detected and processed products with extracted information.

```json
{
  "_id": ObjectId("..."),
  "product_name": "AirPods Pro 2",
  "normalized_name": "airpods pro 2",
  "category": "Electronics > Audio > Headphones",
  "short_description": "Latest wireless earbuds with noise cancellation",
  "price": {
    "min": 249.99,
    "max": 299.99,
    "currency": "USD"
  },
  "trend_sources": [
    {
      "trend_id": ObjectId("..."),
      "source": "reddit",
      "mentioned_at": ISODate("2024-01-15T10:30:00Z")
    }
  ],
  "first_detected_at": ISODate("2024-01-15T11:00:00Z"),
  "last_updated_at": ISODate("2024-01-15T11:00:00Z"),
  "trend_score": 85.5,
  "tags": ["wireless", "audio", "apple"],
  "firecrawl_data": {
    "raw_response": {...},
    "extracted_at": ISODate("2024-01-15T11:05:00Z")
  }
}
```

**Indexes:**
- `normalized_name` (for fuzzy matching and deduplication)
- `trend_score` (descending, for trending products)
- `category` (for filtering by category)
- `first_detected_at` (for sorting by discovery date)

---

### 3. `buy_links` Collection
Stores buying options from various e-commerce platforms.

```json
{
  "_id": ObjectId("..."),
  "product_id": ObjectId("..."),
  "platform": "amazon",
  "url": "https://amazon.com/dp/...",
  "title": "Apple AirPods Pro (2nd Generation) - Official",
  "price": 249.99,
  "currency": "USD",
  "availability": "in_stock",
  "rating": 4.5,
  "review_count": 12543,
  "scraped_at": ISODate("2024-01-15T11:10:00Z"),
  "last_verified": ISODate("2024-01-15T11:10:00Z"),
  "metadata": {
    "asin": "B0BDHB9Y8H",
    "seller": "Amazon"
  }
}
```

**Indexes:**
- `product_id` + `platform` (compound, unique, for one link per platform per product)
- `product_id` (for fetching all buy links for a product)
- `platform` (for filtering by e-commerce site)
- `price` (for price comparison queries)

---

## Deduplication Strategy

1. **Product Name Normalization:**
   - Convert to lowercase
   - Remove special characters
   - Remove common words (the, a, an)
   - Apply stemming (optional)

2. **Fuzzy Matching:**
   - Use Levenshtein distance or similar string similarity
   - Threshold: 0.85 similarity for duplicates
   - Manual review flag for edge cases

3. **Merge Logic:**
   - When duplicate detected, merge trend_sources arrays
   - Update trend_score based on combined sources
   - Keep earliest first_detected_at
   - Update last_updated_at

---

## Data Flow

1. Scraper → `trends` (raw data)
2. NLP Processor → `products` (extracted products)
3. E-commerce Scraper → `buy_links` (buying options)
4. Frontend queries → Aggregated view of products with buy_links

