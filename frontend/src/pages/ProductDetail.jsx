import { useState, useEffect } from 'react'
import { useParams, Link } from 'react-router-dom'
import { productsAPI } from '../services/api'

function ProductDetail() {
  const { id } = useParams()
  const [product, setProduct] = useState(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')

  useEffect(() => {
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
      const data = await productsAPI.getById(id)
      setProduct(data)
    } catch (err) {
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
    if (score >= 70) return 'bg-green-100 text-green-800'
    if (score >= 40) return 'bg-yellow-100 text-yellow-800'
    return 'bg-gray-100 text-gray-800'
  }

  if (loading) {
    return (
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
        <div className="text-center">
          <div className="inline-block animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600"></div>
          <p className="mt-4 text-gray-600">Loading product details...</p>
        </div>
      </div>
    )
  }

  if (error) {
    return (
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
        <div className="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded mb-4">
          <strong>Error: </strong>{error}
        </div>
        <Link to="/products" className="text-primary-600 hover:text-primary-700">
          ← Back to Products
        </Link>
      </div>
    )
  }

  if (!product) {
    return (
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
        <p className="text-gray-600">Product not found.</p>
        <Link to="/products" className="text-primary-600 hover:text-primary-700">
          ← Back to Products
        </Link>
      </div>
    )
  }

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
      <Link
        to="/products"
        className="text-primary-600 hover:text-primary-700 mb-6 inline-block"
      >
        ← Back to Products
      </Link>

      <div className="bg-white rounded-lg shadow-lg p-8 mb-6">
        <div className="flex justify-between items-start mb-6">
          <div>
            <h1 className="text-3xl font-bold text-gray-900 mb-2">
              {product.product_name}
            </h1>
            {product.category && (
              <p className="text-lg text-gray-600">{product.category}</p>
            )}
          </div>
          <span
            className={`px-4 py-2 rounded-full text-sm font-semibold ${getTrendScoreColor(
              product.trend_score
            )}`}
          >
            Trend Score: {product.trend_score.toFixed(1)}
          </span>
        </div>

        {product.short_description && (
          <p className="text-gray-700 mb-6 text-lg">{product.short_description}</p>
        )}

        {product.price && (
          <div className="mb-6">
            <h3 className="text-xl font-semibold text-gray-900 mb-2">Price</h3>
            <p className="text-2xl font-bold text-primary-600">
              {formatPrice(product.price)}
            </p>
          </div>
        )}

        {product.tags && product.tags.length > 0 && (
          <div className="mb-6">
            <h3 className="text-lg font-semibold text-gray-900 mb-2">Tags</h3>
            <div className="flex flex-wrap gap-2">
              {product.tags.map((tag, index) => (
                <span
                  key={index}
                  className="bg-gray-100 text-gray-700 px-3 py-1 rounded-full text-sm"
                >
                  {tag}
                </span>
              ))}
            </div>
          </div>
        )}

        <div className="mb-6">
          <h3 className="text-lg font-semibold text-gray-900 mb-2">
            Mentioned In ({product.trend_sources.length} source{product.trend_sources.length !== 1 ? 's' : ''})
          </h3>
          <div className="space-y-2">
            {product.trend_sources.map((source, index) => (
              <div
                key={index}
                className="bg-gray-50 p-3 rounded border border-gray-200"
              >
                <div className="flex justify-between items-center">
                  <span className="font-medium text-gray-700 capitalize">
                    {source.source}
                  </span>
                  <span className="text-sm text-gray-500">
                    {new Date(source.mentioned_at).toLocaleDateString()}
                  </span>
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>

      {product.buy_links && product.buy_links.length > 0 ? (
        <div className="bg-white rounded-lg shadow-lg p-8">
          <h2 className="text-2xl font-bold text-gray-900 mb-6">Where to Buy</h2>
          <div className="space-y-4">
            {product.buy_links.map((link) => (
              <div
                key={link.id}
                className="border border-gray-200 rounded-lg p-6 hover:shadow-md transition-shadow"
              >
                <div className="flex justify-between items-start mb-4">
                  <div>
                    <h3 className="text-xl font-semibold text-gray-900 capitalize mb-2">
                      {link.platform}
                    </h3>
                    {link.title && (
                      <p className="text-gray-600 mb-2">{link.title}</p>
                    )}
                  </div>
                  {link.price && (
                    <div className="text-right">
                      <p className="text-2xl font-bold text-primary-600">
                        ${link.price.toFixed(2)}
                      </p>
                      <p className="text-sm text-gray-500">{link.currency}</p>
                    </div>
                  )}
                </div>

                {link.rating && (
                  <div className="mb-4">
                    <div className="flex items-center space-x-2">
                      <span className="text-yellow-500">★</span>
                      <span className="font-semibold">{link.rating}</span>
                      {link.review_count && (
                        <span className="text-gray-500">
                          ({link.review_count.toLocaleString()} reviews)
                        </span>
                      )}
                    </div>
                  </div>
                )}

                {link.availability && (
                  <div className="mb-4">
                    <span
                      className={`px-3 py-1 rounded-full text-sm font-medium ${
                        link.availability === 'in_stock'
                          ? 'bg-green-100 text-green-800'
                          : 'bg-red-100 text-red-800'
                      }`}
                    >
                      {link.availability.replace('_', ' ').toUpperCase()}
                    </span>
                  </div>
                )}

                <a
                  href={link.url}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="inline-block bg-primary-600 text-white px-6 py-2 rounded-lg font-semibold hover:bg-primary-700 transition-colors"
                >
                  Buy on {link.platform.charAt(0).toUpperCase() + link.platform.slice(1)} →
                </a>
              </div>
            ))}
          </div>
        </div>
      ) : (
        <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-6">
          <p className="text-yellow-800">
            No buying options available yet. Check back later!
          </p>
        </div>
      )}
    </div>
  )
}

export default ProductDetail

