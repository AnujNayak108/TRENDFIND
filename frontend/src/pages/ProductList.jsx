import { useState, useEffect } from 'react'
import { Link } from 'react-router-dom'
import { productsAPI, scrapeAPI } from '../services/api'

function ProductList() {
  const [products, setProducts] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')
  const [category, setCategory] = useState('')
  const [lastUpdated, setLastUpdated] = useState(null)

  useEffect(() => {
    loadProducts()
    loadScrapeStatus()
  }, [category])

  const loadProducts = async () => {
    setLoading(true)
    setError('')
    try {
      const params = category ? { category } : {}
      const data = await productsAPI.getAll(params)
      
      // Filter out products with invalid IDs
      const validProducts = (data || []).filter(product => {
        const hasValidId = product.id && product.id !== 'undefined' && product.id !== 'null'
        return hasValidId
      })
      
      setProducts(validProducts)
    } catch (err) {
      console.error('Error loading products:', err)
      setError(err.response?.data?.detail || err.message)
    } finally {
      setLoading(false)
    }
  }

  const loadScrapeStatus = async () => {
    try {
      const status = await scrapeAPI.getStatus()
      if (status?.last_scrape_time) {
        setLastUpdated(new Date(status.last_scrape_time))
      }
    } catch (err) {
      // Non-critical, ignore
    }
  }

  const formatPrice = (price) => {
    if (!price) return 'Price not available'
    const symbol = price.currency === 'INR' ? '₹' : '$'
    if (price.min === price.max) {
      return `${symbol}${price.min.toFixed(0)}`
    }
    return `${symbol}${price.min.toFixed(0)} - ${symbol}${price.max.toFixed(0)}`
  }

  const getTrendScoreColor = (score) => {
    if (score >= 70) return 'bg-green-500/10 text-green-400 border-green-500/20'
    if (score >= 40) return 'bg-yellow-500/10 text-yellow-400 border-yellow-500/20'
    return 'bg-gray-500/10 text-gray-400 border-gray-500/20'
  }

  const getSourceBadge = (source) => {
    const badges = {
      reddit: { label: 'Reddit', color: 'bg-orange-500/20 text-orange-400 border-orange-500/30' },
      google_trends: { label: 'Google Trends', color: 'bg-blue-500/20 text-blue-400 border-blue-500/30' },
      youtube: { label: 'YouTube', color: 'bg-red-500/20 text-red-400 border-red-500/30' },
    }
    return badges[source] || { label: source, color: 'bg-gray-500/20 text-gray-400 border-gray-500/30' }
  }

  const getUniqueSources = (trendSources) => {
    if (!trendSources || trendSources.length === 0) return []
    const unique = [...new Set(trendSources.map(s => s.source))]
    return unique
  }

  const formatTimeAgo = (date) => {
    if (!date) return ''
    const now = new Date()
    const diffMs = now - date
    const diffMins = Math.floor(diffMs / 60000)
    const diffHours = Math.floor(diffMs / 3600000)
    const diffDays = Math.floor(diffMs / 86400000)

    if (diffMins < 1) return 'just now'
    if (diffMins < 60) return `${diffMins}m ago`
    if (diffHours < 24) return `${diffHours}h ago`
    return `${diffDays}d ago`
  }

  if (loading) {
    return (
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
        <div className="text-center mt-20">
          <div className="inline-block animate-spin rounded-full h-12 w-12 border-b-2 border-primary-500"></div>
          <p className="mt-6 text-gray-400 font-medium">Gathering Intelligence...</p>
        </div>
      </div>
    )
  }

  if (error) {
    return (
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
        <div className="bg-red-500/10 border border-red-500/20 text-red-400 px-6 py-4 rounded-xl max-w-2xl mx-auto mt-12 backdrop-blur-md">
          <strong>System Error: </strong>{error}
        </div>
      </div>
    )
  }

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12 relative animate-fade-in">
      <div className="mb-12">
        <div className="flex flex-col sm:flex-row sm:items-end sm:justify-between mb-6">
          <h1 className="text-4xl md:text-5xl font-display font-black text-white mb-2 sm:mb-0">Trending <span className="text-gradient">Products</span></h1>
          {lastUpdated && (
            <span className="text-sm text-gray-500 font-mono flex items-center gap-1.5">
              <span className="w-2 h-2 rounded-full bg-green-500 animate-pulse inline-block"></span>
              Updated {formatTimeAgo(lastUpdated)}
            </span>
          )}
        </div>
        
        <div className="flex flex-col sm:flex-row sm:items-center space-y-4 sm:space-y-0 sm:space-x-4">
          <div className="relative flex-1 max-w-lg">
            <input
              id="category"
              type="text"
              value={category}
              onChange={(e) => setCategory(e.target.value)}
              placeholder="Filter by category (e.g. Electronics, Beauty)"
              className="w-full bg-surface/50 border border-white/10 rounded-xl px-5 py-3 focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-transparent text-white placeholder-gray-500 transition-all font-medium"
            />
            {category && (
              <button
                onClick={() => setCategory('')}
                className="absolute right-4 top-1/2 -translate-y-1/2 text-gray-400 hover:text-white"
              >
                ✕
              </button>
            )}
          </div>
        </div>
      </div>

      {products.length === 0 ? (
        <div className="text-center py-20 glass-card">
          <div className="text-6xl mb-6">📡</div>
          <p className="text-white text-xl font-display font-semibold mb-3">
            {category ? 'No products found for this category.' : 'Scraping in progress...'}
          </p>
          <p className="text-gray-400 max-w-md mx-auto">
            {category
              ? 'Try clearing the filter or using a broader category name.'
              : 'Our bots are scanning Google Trends, Reddit, and YouTube for trending Indian products. This usually takes 1-2 minutes. Refresh the page shortly!'}
          </p>
          {!category && (
            <button
              onClick={loadProducts}
              className="mt-6 px-6 py-2 bg-primary-600 text-white rounded-xl font-bold hover:bg-primary-500 transition-all"
            >
              Refresh
            </button>
          )}
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8">
          {products.map((product) => {
            if (!product.id || product.id === 'undefined' || product.id === 'null') {
              return null
            }
            const uniqueSources = getUniqueSources(product.trend_sources)
            return (
              <Link
                key={product.id}
                to={`/products/${product.id}`}
                className="glass-card group flex flex-col h-full hover:-translate-y-2"
              >
                {/* Product Image Area */}
                <div className="relative h-64 w-full bg-surface/80 overflow-hidden rounded-t-2xl">
                  {product.image_url ? (
                    <img 
                      src={product.image_url} 
                      alt={product.product_name}
                      className="w-full h-full object-cover transition-transform duration-700 group-hover:scale-110"
                    />
                  ) : (
                    <div className="w-full h-full flex items-center justify-center text-gray-600 bg-surface/50">
                      No Image Available
                    </div>
                  )}
                  <div className="absolute inset-0 bg-gradient-to-t from-background via-transparent to-transparent opacity-60"></div>
                  
                  {/* Floating Badges */}
                  <div className="absolute top-4 right-4">
                    <span className={`px-3 py-1.5 rounded-full text-xs font-bold border ${getTrendScoreColor(product.trend_score)} shadow-xl backdrop-blur-md`}>
                      Score: {product.trend_score.toFixed(1)}
                    </span>
                  </div>

                  {/* Source badges at bottom-left of image */}
                  {uniqueSources.length > 0 && (
                    <div className="absolute bottom-3 left-3 flex flex-wrap gap-1.5">
                      {uniqueSources.map((source) => {
                        const badge = getSourceBadge(source)
                        return (
                          <span
                            key={source}
                            className={`px-2 py-0.5 rounded text-[10px] font-bold border backdrop-blur-md ${badge.color}`}
                          >
                            {badge.label}
                          </span>
                        )
                      })}
                    </div>
                  )}
                </div>

                {/* Content Area */}
                <div className="p-6 flex-1 flex flex-col">
                  {product.category && (
                    <p className="text-xs font-bold uppercase tracking-wider text-primary-400 mb-2">{product.category}</p>
                  )}
                  
                  <h2 className="text-2xl font-display font-bold text-white mb-3 line-clamp-2 leading-tight group-hover:text-primary-400 transition-colors">
                    {product.product_name}
                  </h2>

                  {product.short_description ? (
                    <p className="text-gray-400 mb-5 line-clamp-2 text-sm leading-relaxed flex-1">
                      {product.short_description}
                    </p>
                  ) : (
                    <div className="flex-1"></div>
                  )}

                  <div className="mt-auto pt-4 border-t border-white/5 flex items-center justify-between">
                    <div>
                      {product.price ? (
                        <p className="text-xl font-display font-bold text-white">
                          {formatPrice(product.price)}
                        </p>
                      ) : (
                        <p className="text-sm text-gray-500">Price unavailable</p>
                      )}
                    </div>
                    <div className="flex items-center text-sm font-semibold text-primary-500 group-hover:text-primary-400 transition-colors">
                      <span className="mr-2">{product.trend_sources?.length || 0} Sources</span>
                      <span className="group-hover:translate-x-1 transition-transform">→</span>
                    </div>
                  </div>
                </div>
              </Link>
            )
          })}
        </div>
      )}
    </div>
  )
}

export default ProductList
