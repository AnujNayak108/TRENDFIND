import { useState, useEffect } from 'react'
import { useParams, Link } from 'react-router-dom'
import { productsAPI } from '../services/api'

// Platform brand colors and icons
const PLATFORM_INFO = {
  amazon: { label: 'Amazon India', icon: '🛒', color: 'bg-yellow-500/20 border-yellow-500/30 hover:bg-yellow-500/30' },
  flipkart: { label: 'Flipkart', icon: '🔵', color: 'bg-blue-500/20 border-blue-500/30 hover:bg-blue-500/30' },
  croma: { label: 'Croma', icon: '🟢', color: 'bg-green-500/20 border-green-500/30 hover:bg-green-500/30' },
  myntra: { label: 'Myntra', icon: '👗', color: 'bg-pink-500/20 border-pink-500/30 hover:bg-pink-500/30' },
  nykaa: { label: 'Nykaa', icon: '💄', color: 'bg-fuchsia-500/20 border-fuchsia-500/30 hover:bg-fuchsia-500/30' },
}

function ProductDetail() {
  const { id } = useParams()
  const [product, setProduct] = useState(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')

  useEffect(() => {
    if (id && id !== 'undefined' && id !== 'null') {
      loadProduct()
    } else {
      setError('Invalid product ID')
      setLoading(false)
    }
  }, [id])

  const loadProduct = async () => {
    setLoading(true)
    setError('')
    
    if (!id || id === 'undefined' || id === 'null') {
      setError('Invalid product ID')
      setLoading(false)
      return
    }
    
    try {
      const data = await productsAPI.getById(id)
      setProduct(data)
    } catch (err) {
      console.error('Error loading product:', err)
      setError(err.response?.data?.detail || err.message || 'Failed to load product')
    } finally {
      setLoading(false)
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

  const getTrendVelocity = (score) => {
    if (score >= 70) return { label: '🔥 Hot', desc: 'Trending strongly across multiple platforms' }
    if (score >= 40) return { label: '📈 Rising', desc: 'Gaining traction in India' }
    if (score >= 20) return { label: '🆕 New', desc: 'Recently detected in trending data' }
    return { label: '📊 Tracking', desc: 'Being monitored for trend signals' }
  }

  const getSourceIcon = (source) => {
    const icons = {
      reddit: { icon: '💬', color: 'bg-orange-500/20 text-orange-400', label: 'Reddit' },
      google_trends: { icon: '📊', color: 'bg-blue-500/20 text-blue-400', label: 'Google Trends' },
      youtube: { icon: '▶', color: 'bg-red-500/20 text-red-500', label: 'YouTube' },
    }
    return icons[source] || { icon: '🔍', color: 'bg-primary-500/20 text-primary-500', label: source }
  }

  const getUniquePlatforms = () => {
    if (!product?.trend_sources) return []
    return [...new Set(product.trend_sources.map(s => s.source))]
  }

  if (loading) {
    return (
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
        <div className="text-center mt-20">
          <div className="inline-block animate-spin rounded-full h-12 w-12 border-b-2 border-primary-500"></div>
          <p className="mt-6 text-gray-400 font-medium">Retrieving Product Details...</p>
        </div>
      </div>
    )
  }

  if (error || !product) {
    return (
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12 animate-fade-in">
        <div className="bg-red-500/10 border border-red-500/20 text-red-400 px-6 py-4 rounded-xl max-w-2xl mx-auto mt-12 backdrop-blur-md mb-6">
          <strong>Error: </strong>{error || 'Product not found'}
        </div>
        <Link to="/products" className="text-primary-400 hover:text-primary-300 font-medium ml-4">
          ← Return to Products
        </Link>
      </div>
    )
  }

  const velocity = getTrendVelocity(product.trend_score)
  const detectedPlatforms = getUniquePlatforms()

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12 relative animate-fade-in">
      <Link
        to="/products"
        className="inline-flex items-center text-gray-400 hover:text-white mb-8 transition-colors group"
      >
        <span className="transform group-hover:-translate-x-1 transition-transform mr-2">←</span> 
        Back to Products
      </Link>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-12">
        {/* Left Column: Image Area */}
        <div className="space-y-6">
          <div className="glass-card overflow-hidden aspect-square flex items-center justify-center p-2 relative group">
            <div className="absolute inset-0 bg-gradient-to-tr from-primary-500/10 to-accent-purple/10 opacity-0 group-hover:opacity-100 transition-opacity duration-500"></div>
            {product.image_url ? (
              <img 
                src={product.image_url} 
                alt={product.product_name} 
                className="w-full h-full object-cover rounded-xl transition-transform duration-700 group-hover:scale-105"
              />
            ) : (
              <span className="text-6xl">📦</span>
            )}
          </div>

          {/* Trend Velocity Indicator */}
          <div className="glass-card p-5 border border-white/5">
            <div className="flex items-center justify-between mb-3">
              <h3 className="text-lg font-display font-semibold text-white">Trend Velocity</h3>
              <span className="text-lg">{velocity.label}</span>
            </div>
            <p className="text-sm text-gray-400 mb-4">{velocity.desc}</p>
            
            {/* Score bar */}
            <div className="w-full bg-surface/80 rounded-full h-2.5 overflow-hidden">
              <div
                className="h-full rounded-full transition-all duration-1000 bg-gradient-to-r from-primary-600 to-accent-pink"
                style={{ width: `${Math.min(100, product.trend_score)}%` }}
              ></div>
            </div>
            <div className="flex justify-between mt-1.5 text-xs text-gray-500 font-mono">
              <span>0</span>
              <span>Score: {product.trend_score.toFixed(1)}</span>
              <span>100</span>
            </div>
          </div>

          {/* Detected On Platforms */}
          {detectedPlatforms.length > 0 && (
            <div className="glass-card p-5 border border-white/5">
              <h3 className="text-lg font-display font-semibold text-white mb-3">
                Detected On
              </h3>
              <div className="flex flex-wrap gap-2">
                {detectedPlatforms.map((platform) => {
                  const info = getSourceIcon(platform)
                  return (
                    <span
                      key={platform}
                      className={`px-3 py-1.5 rounded-full text-sm font-medium border border-white/10 ${info.color} flex items-center gap-1.5`}
                    >
                      <span>{info.icon}</span>
                      {info.label}
                    </span>
                  )
                })}
              </div>
            </div>
          )}
          
          {/* Trend Sources Mini-card */}
          <div className="glass-card p-6 border border-white/5">
            <h3 className="text-lg font-display font-semibold text-white mb-4">
              Trending Mentions ({product.trend_sources?.length || 0})
            </h3>
            <div className="space-y-3 max-h-[250px] overflow-y-auto pr-2 custom-scrollbar">
              {product.trend_sources?.map((source, index) => {
                const info = getSourceIcon(source.source)
                return (
                  <div
                    key={index}
                    className="bg-surface/50 p-4 rounded-xl border border-white/5 hover:border-primary-500/30 transition-colors flex items-center justify-between"
                  >
                    <div className="flex items-center">
                      <div className={`w-8 h-8 rounded-full flex items-center justify-center mr-3 ${info.color}`}>
                        {info.icon}
                      </div>
                      <span className="font-medium text-gray-200 capitalize">
                        {info.label}
                      </span>
                    </div>
                    <span className="text-xs text-gray-500 font-mono">
                      {new Date(source.mentioned_at).toLocaleDateString()}
                    </span>
                  </div>
                )
              })}
            </div>
          </div>
        </div>

        {/* Right Column: Details & Buy Links */}
        <div className="flex flex-col">
          <div className="mb-2 flex items-center justify-between">
            {product.category && (
              <span className="text-primary-400 text-sm font-bold uppercase tracking-widest">{product.category}</span>
            )}
            <span
              className={`px-4 py-1.5 rounded-full text-xs font-bold border ${getTrendScoreColor(
                product.trend_score
              )}`}
            >
              Trend Score: {product.trend_score.toFixed(1)}
            </span>
          </div>

          <h1 className="text-4xl md:text-5xl font-display font-black text-white mb-6 leading-tight">
            {product.product_name}
          </h1>

          {product.short_description && (
            <p className="text-gray-300 text-lg leading-relaxed mb-8 border-l-2 border-primary-500 pl-4">
              {product.short_description}
            </p>
          )}

          {product.price && (
            <div className="mb-10">
              <span className="text-sm text-gray-400 font-medium uppercase tracking-wider block mb-1">Estimated Price</span>
              <p className="text-4xl font-display font-bold text-white">
                {formatPrice(product.price)}
              </p>
            </div>
          )}

          {product.tags && product.tags.length > 0 && (
            <div className="mb-10">
              <div className="flex flex-wrap gap-2">
                {product.tags.map((tag, index) => (
                  <span
                    key={index}
                    className="bg-surface/80 border border-white/10 text-gray-300 px-4 py-1.5 rounded-full text-sm hover:border-primary-500/50 hover:text-white transition-colors cursor-default"
                  >
                    #{tag}
                  </span>
                ))}
              </div>
            </div>
          )}

          {/* Buy Links Section — Multi-platform Indian e-commerce */}
          <div className="mt-6 flex-1">
            <h2 className="text-2xl font-display font-bold text-white mb-6 flex items-center">
              <span className="w-8 h-8 rounded-full bg-accent-pink/20 text-accent-pink flex items-center justify-center mr-3 text-sm">🛒</span>
              Where to Buy in India
            </h2>
            
            {product.buy_links && product.buy_links.length > 0 ? (
              <div className="space-y-4">
                {product.buy_links.map((link, idx) => {
                  const platformKey = (link.platform || '').toLowerCase()
                  const info = PLATFORM_INFO[platformKey] || { label: link.platform, icon: '🔗', color: 'bg-gray-500/20 border-gray-500/30 hover:bg-gray-500/30' }
                  
                  return (
                    <div
                      key={link.id || idx}
                      className={`glass-card p-5 group flex flex-col sm:flex-row sm:items-center justify-between border ${info.color} transition-all`}
                    >
                      <div className="mb-4 sm:mb-0">
                        <div className="flex items-center mb-1">
                          <span className="text-2xl mr-3">{info.icon}</span>
                          <h3 className="text-xl font-display font-bold text-white capitalize">
                            {info.label}
                          </h3>
                          {link.availability && (
                            <span
                              className={`ml-3 px-2 py-0.5 rounded text-[10px] font-bold uppercase tracking-wider ${
                                link.availability === 'in_stock'
                                  ? 'bg-green-500/20 text-green-400 border border-green-500/20'
                                  : 'bg-yellow-500/20 text-yellow-400 border border-yellow-500/20'
                              }`}
                            >
                              {link.availability === 'check_site' ? 'Check Site' : link.availability.replace('_', ' ')}
                            </span>
                          )}
                        </div>
                        
                        {link.title && (
                          <p className="text-sm text-gray-400 mt-1">{link.title}</p>
                        )}

                        {link.rating && (
                          <div className="flex items-center space-x-2 text-sm mt-1">
                            <span className="text-yellow-400">★</span>
                            <span className="font-bold text-white">{link.rating}</span>
                            {link.review_count && (
                              <span className="text-gray-500">
                                ({link.review_count.toLocaleString()} reviews)
                              </span>
                            )}
                          </div>
                        )}
                      </div>

                      <div className="flex items-center sm:block">
                        {link.price && (
                          <div className="mr-4 sm:mr-0 sm:mb-3 sm:text-right">
                            <p className="text-2xl font-display font-bold text-primary-400">
                              ₹{link.price.toFixed(0)}
                            </p>
                          </div>
                        )}
                        <a
                          href={link.url}
                          target="_blank"
                          rel="noopener noreferrer"
                          className="flex-1 sm:flex-none text-center bg-primary-600 text-white px-6 py-3 rounded-xl font-bold hover:bg-primary-500 transition-all shadow-[0_0_20px_rgba(37,99,235,0.2)] hover:shadow-[0_0_30px_rgba(37,99,235,0.4)]"
                        >
                          Shop Now →
                        </a>
                      </div>
                    </div>
                  )
                })}
              </div>
            ) : (
              <div className="glass-card p-8 border-yellow-500/20 bg-yellow-500/5 text-center">
                <p className="text-yellow-400/80 font-medium">
                  We're still hunting for the best buying options on Indian platforms. Check back later!
                </p>
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  )
}

export default ProductDetail
