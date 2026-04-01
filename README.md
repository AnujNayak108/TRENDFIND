# TrendFind

**Automatically detect India-specific trending products from social networks, identify what they are, and find where to buy them.**

TrendFind scrapes live trending topics from Indian subreddits (`r/IndiaTech`, `r/IndianBeautyDeals`), Google Trends (India), and other platforms. It uses spaCy NLP to identify product mentions, extracts real Open Graph thumbnails, and automatically generates reliable buy links for Amazon India.

## 🏗️ Architecture

- **Backend**: FastAPI (Python) with async/await patterns
- **Database**: MongoDB (NoSQL) with optimized indexes
- **Frontend**: React + Vite + Tailwind CSS
- **NLP**: spaCy for product name extraction
- **Scraping**: Playwright + Firecrawl API for content extraction

## 📁 Project Structure

```
trendfind/
├── backend/
│   ├── app/
│   │   ├── api/           # API routes
│   │   │   └── v1/
│   │   ├── core/          # Configuration and database
│   │   ├── models/        # Pydantic models
│   │   └── services/      # Business logic
│   ├── requirements.txt
│   └── .env.example
├── frontend/
│   ├── src/
│   │   ├── components/    # React components
│   │   ├── pages/         # Page components
│   │   └── services/      # API client
│   ├── package.json
│   └── vite.config.js
├── docs/
│   └── mongodb_schema.md  # Database schema documentation
└── README.md
```

## 🚀 Quick Start

### Prerequisites

- Python 3.9+
- Node.js 18+
- MongoDB (local or remote)
- (Optional) Firecrawl API key
- (Optional) YouTube Data API key (free tier available)
- Google Trends (no API key required - completely free)

### Backend Setup

1. **Navigate to backend directory:**
   ```bash
   cd backend
   ```

2. **Create virtual environment:**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv/Scripts/activate
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Download spaCy model:**
   ```bash
   python -m spacy download en_core_web_sm
   ```

5. **Configure environment:**
   ```bash
   cp .env.example .env
   # Edit .env with your configuration
   ```

   Minimum required configuration:
   ```env
   MONGODB_URL=mongodb://localhost:27017
   DATABASE_NAME=trendfind
   ```

6. **Start MongoDB:**
   ```bash
   # If using local MongoDB
   mongod
   ```

7. **Run the backend:**
   ```bash
   uvicorn app.main:app --reload --port 8000
   ```

   The API will be available at `http://localhost:8000`
   API documentation: `http://localhost:8000/docs`

### Frontend Setup

1. **Navigate to frontend directory:**
   ```bash
   cd frontend
   ```

2. **Install dependencies:**
   ```bash
   npm install
   ```

3. **Start development server:**
   ```bash
   npm run dev
   ```

   The frontend will be available at `http://localhost:3000`

## 📊 Database Schema

See [docs/mongodb_schema.md](docs/mongodb_schema.md) for detailed schema documentation.

### Collections

1. **trends**: Raw trending topics from social media
2. **products**: Detected and processed products
3. **buy_links**: E-commerce buying options

All collections include:
- Automatic timestamps
- Optimized indexes
- Deduplication logic

## 🔌 API Endpoints

### Trends
- `GET /api/v1/trends` - Get all trends (with filters)
- `GET /api/v1/trends/{id}` - Get a specific trend

### Products
- `GET /api/v1/products` - Get all products (with filters)
- `GET /api/v1/products/{id}` - Get product with buy links

### Scraping
- `POST /api/v1/scrape/run` - Trigger scraping and processing

## 🔄 How It Works

1. **Scraping**: Natively collects live trending topics from Google Trends (IN) and Indian subreddits using automated JSON fallback bypassing failing APIs.
2. **NLP Processing**: Extracts accurate product names using spaCy NER and deduplicates utilizing fuzzy matching.
3. **Enrichment**: Extracts real Open Graph metadata (`og:image`, `og:description`) from raw HTML to populate rich thumbnails.
4. **E-commerce**: Automatically generates `amazon.in` affiliate/search links formatted with INR currency.

## 🛠️ Development

### Backend Development

- **Code Style**: Follow PEP 8
- **Type Hints**: Use type hints for all functions
- **Async**: Use async/await for I/O operations
- **Error Handling**: Gracefully handle scraper failures

### Frontend Development

- **Components**: Modular, reusable components
- **State Management**: React hooks
- **Styling**: Tailwind CSS utility classes
- **API**: Centralized API service in `src/services/api.js`

## 🧪 Testing

### Manual Testing

1. Start backend and frontend
2. Navigate to `http://localhost:3000`
3. Click "Start Scraping" to trigger data collection
4. View products at `/products`
5. Click on a product to see details and buy links

### Graceful Degradation & Free APIs

The application has been engineered to avoid hard dependency lock-in:
- **Reddit**: Bypasses required API keys using native `.json` scraping on subreddits.
- **Open Graph**: Extracts images and descriptions using `httpx` and `BeautifulSoup` when third-party APIs like Firecrawl limit access.
- **Google Trends**: Uses Python native scraping specific to the `IN` region.
- **Amazon Links**: Dynamically generates real India-specific `amazon.in` query strings rather than fixed dummy links.

## 🔧 Configuration

### Environment Variables

```env
# MongoDB
MONGODB_URL=mongodb://localhost:27017
DATABASE_NAME=trendfind

# CORS
CORS_ORIGINS=http://localhost:3000,http://localhost:5173

# Firecrawl (optional)
FIRECRAWL_API_KEY=your_key_here

# Google Trends (no API key required - completely free)
# Uses pytrends library

# YouTube Data API (optional - free tier available)
# Get your API key from: https://console.cloud.google.com/apis/credentials
YOUTUBE_API_KEY=

# Instagram (mock data - API access is restricted)
# For production, consider using Instagram Basic Display API

# NLP
SPACY_MODEL=en_core_web_sm
PRODUCT_NAME_SIMILARITY_THRESHOLD=0.85
```

## 📝 Features

### Current (MVP)
- ✅ Scrape live trends from India-specific subreddits natively (no API key required)
- ✅ Scrape trends from Google Trends India (free)
- ✅ Extract product names and descriptions using NLP
- ✅ Real thumbnail extraction via Open Graph HTML meta tags
- ✅ Store dynamically extracted products in MongoDB
- ✅ Display products in a React UI
- ✅ Product detail pages with dynamically generated `amazon.in` searching links in INR
- ✅ Deduplication using fuzzy matching

### Future Enhancements
- Real Instagram API integration (Instagram Basic Display API)
- Real e-commerce scraping (Amazon, eBay, etc.)
- Image recognition for products
- User accounts and favorites
- Email alerts for new products
- Price tracking and alerts

## 🐛 Troubleshooting

### MongoDB Connection Issues
- Ensure MongoDB is running: `mongod`
- Check `MONGODB_URL` in `.env`
- Verify network connectivity

### spaCy Model Not Found
```bash
python -m spacy download en_core_web_sm
```

### CORS Errors
- Verify `CORS_ORIGINS` includes your frontend URL
- Check backend is running on port 8000

### Port Already in Use
- Backend: Change port in uvicorn command
- Frontend: Update `vite.config.js` port

## 📄 License

MIT License - feel free to use this project for learning and development.

## 🤝 Contributing

This is an MVP project. Contributions welcome for:
- Real API integrations
- Enhanced NLP models
- E-commerce scraping
- UI/UX improvements

---

**Built with ❤️ for discovering trending products**

