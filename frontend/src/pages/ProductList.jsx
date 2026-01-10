import { useState, useEffect } from 'react'
import { Link } from 'react-router-dom'
import { productsAPI } from '../services/api'

function ProductList() {
  const [products, setProducts] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')
  const [category, setCategory] = useState('')

  useEffect(() => {
    loadProducts()
  }, [category])

  const loadProducts = async () => {
    setLoading(true)
    setError('')
    try {
      const params = category ? { category } : {}
      const data = await productsAPI.getAll(params)
      console.log('Products loaded:', data) // Debug log
      console.log('Number of products:', data?.length || 0) // Debug log
      
      // Filter out products with invalid IDs and log them
      const validProducts = (data || []).filter(product => {
        const hasValidId = product.id && product.id !== 'undefined' && product.id !== 'null'
        if (!hasValidId) {
          console.warn('Product filtered out (invalid ID):', product)
        }
        return hasValidId
      })
      
      console.log('Valid products after filtering:', validProducts.length)
      setProducts(validProducts)
    } catch (err) {
      console.error('Error loading products:', err) // Debug log
      setError(err.response?.data?.detail || err.message)
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
          <p className="mt-4 text-gray-600">Loading products...</p>
        </div>
      </div>
    )
  }

  if (error) {
    return (
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
        <div className="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded">
          <strong>Error: </strong>{error}
        </div>
      </div>
    )
  }

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-gray-900 mb-4">Trending Products</h1>
        
        <div className="flex items-center space-x-4">
          <label htmlFor="category" className="text-gray-700 font-medium">
            Filter by Category:
          </label>
          <input
            id="category"
            type="text"
            value={category}
            onChange={(e) => setCategory(e.target.value)}
            placeholder="e.g., Electronics"
            className="border border-gray-300 rounded-md px-4 py-2 focus:outline-none focus:ring-2 focus:ring-primary-600"
          />
          {category && (
            <button
              onClick={() => setCategory('')}
              className="text-primary-600 hover:text-primary-700"
            >
              Clear
            </button>
          )}
        </div>
      </div>

      {products.length === 0 ? (
        <div className="text-center py-12">
          <p className="text-gray-600 text-lg mb-4">No products found.</p>
          <p className="text-gray-500">Try running a scrape from the home page.</p>
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {products.map((product) => {
            // Ensure product has a valid ID before rendering link
            if (!product.id || product.id === 'undefined' || product.id === 'null') {
              return null
            }
            return (
            <Link
              key={product.id}
              to={`/products/${product.id}`}
              className="bg-white rounded-lg shadow-md hover:shadow-xl transition-shadow p-6 block"
            >
              <div className="flex justify-between items-start mb-3">
                <h2 className="text-xl font-semibold text-gray-900 line-clamp-2">
                  {product.product_name}
                </h2>
                <span
                  className={`px-2 py-1 rounded-full text-xs font-semibold ${getTrendScoreColor(
                    product.trend_score
                  )}`}
                >
                  {product.trend_score.toFixed(1)}
                </span>
              </div>

              {product.category && (
                <p className="text-sm text-gray-500 mb-2">{product.category}</p>
              )}

              {product.short_description && (
                <p className="text-gray-600 mb-4 line-clamp-2">
                  {product.short_description}
                </p>
              )}

              {product.price && (
                <p className="text-lg font-semibold text-primary-600 mb-2">
                  {formatPrice(product.price)}
                </p>
              )}

              <div className="flex items-center justify-between text-sm text-gray-500">
                <span>{product.trend_sources.length} source(s)</span>
                <span className="text-primary-600">View Details →</span>
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

