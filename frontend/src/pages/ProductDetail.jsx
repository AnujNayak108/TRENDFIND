import { useState, useEffect } from 'react'
import { useParams, Link } from 'react-router-dom'
import { productsAPI } from '../services/api'

function ProductDetail() {
  const { id } = useParams()
  const [product, setProduct] = useState(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')

  useEffect(() => {
    console.log('ProductDetail useEffect - ID from params:', id)
    // Only load if id is valid (not undefined, null, or empty string)
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
    
    // Double check id is valid before making API call
    if (!id || id === 'undefined' || id === 'null') {
      setError('Invalid product ID')
      setLoading(false)
      return
    }
    
    try {
      console.log('Calling productsAPI.getById with ID:', id)
      const data = await productsAPI.getById(id)
      console.log('Product data received:', data)
      setProduct(data)
    } catch (err) {
      console.error('Error loading product:', err)
      console.error('Error response:', err.response)
      console.error('Error message:', err.message)
      setError(err.response?.data?.detail || err.message || 'Failed to load product')
    } finally {
      setLoading(false)
    }
  }

  const formatPrice = (price) => {
    if (!price) return 'Price not available'
    if (price.min === price.max) {
      return `$${price.min.toFixed(2)} ${price.currency}`
    }
    return `$${price.min.toFixed(2)} - $${price.max.toFixed(2)} ${price.currency}`
  }

  const getTrendScoreColor = (score) => {
    if (score >= 70) return 'bg-green-500/10 text-green-400 border-green-500/20'
    if (score >= 40) return 'bg-yellow-500/10 text-yellow-400 border-yellow-500/20'
    return 'bg-gray-500/10 text-gray-400 border-gray-500/20'
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
          
          {/* Trend Sources Mini-card */}
          <div className="glass-card p-6 border border-white/5">
            <h3 className="text-lg font-display font-semibold text-white mb-4">
              Trending Mentions ({product.trend_sources?.length || 0})
            </h3>
            <div className="space-y-3 max-h-[250px] overflow-y-auto pr-2 custom-scrollbar">
              {product.trend_sources?.map((source, index) => (
                <div
                  key={index}
                  className="bg-surface/50 p-4 rounded-xl border border-white/5 hover:border-primary-500/30 transition-colors flex items-center justify-between"
                >
                  <div className="flex items-center">
                    <div className={`w-8 h-8 rounded-full flex items-center justify-center mr-3 ${
                      source.source === 'youtube' ? 'bg-red-500/20 text-red-500' :
                      source.source === 'instagram' ? 'bg-pink-500/20 text-pink-500' :
                      'bg-primary-500/20 text-primary-500'
                    }`}>
                      {source.source === 'youtube' ? '▶' : source.source === 'instagram' ? '📷' : '🔍'}
                    </div>
                    <span className="font-medium text-gray-200 capitalize">
                      {source.source.replace('_', ' ')}
                    </span>
                  </div>
                  <span className="text-xs text-gray-500 font-mono">
                    {new Date(source.mentioned_at).toLocaleDateString()}
                  </span>
                </div>
              ))}
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

          {/* Buy Links Section */}
          <div className="mt-6 flex-1">
            <h2 className="text-2xl font-display font-bold text-white mb-6 flex items-center">
              <span className="w-8 h-8 rounded-full bg-accent-pink/20 text-accent-pink flex items-center justify-center mr-3 text-sm">🛒</span>
              Where to Buy
            </h2>
            
            {product.buy_links && product.buy_links.length > 0 ? (
              <div className="space-y-4">
                {product.buy_links.map((link) => (
                  <div
                    key={link.id}
                    className="glass-card p-5 group flex flex-col sm:flex-row sm:items-center justify-between"
                  >
                    <div className="mb-4 sm:mb-0">
                      <div className="flex items-center mb-1">
                        <h3 className="text-xl font-display font-bold text-white capitalize mr-3">
                          {link.platform}
                        </h3>
                        {link.availability && (
                          <span
                            className={`px-2 py-0.5 rounded text-[10px] font-bold uppercase tracking-wider ${
                              link.availability === 'in_stock'
                                ? 'bg-green-500/20 text-green-400 border border-green-500/20'
                                : 'bg-red-500/20 text-red-400 border border-red-500/20'
                            }`}
                          >
                            {link.availability.replace('_', ' ')}
                          </span>
                        )}
                      </div>
                      
                      {link.rating && (
                        <div className="flex items-center space-x-2 text-sm">
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
                            ${link.price.toFixed(2)}
                          </p>
                        </div>
                      )}
                      <a
                        href={link.url}
                        target="_blank"
                        rel="noopener noreferrer"
                        className="flex-1 sm:flex-none text-center bg-primary-600 text-white px-6 py-3 rounded-xl font-bold hover:bg-primary-500 transition-all shadow-[0_0_20px_rgba(37,99,235,0.2)] hover:shadow-[0_0_30px_rgba(37,99,235,0.4)]"
                      >
                        Buy Now
                      </a>
                    </div>
                  </div>
                ))}
              </div>
            ) : (
              <div className="glass-card p-8 border-yellow-500/20 bg-yellow-500/5 text-center">
                <p className="text-yellow-400/80 font-medium">
                  We're still hunting for the best buying options. Check back later!
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

