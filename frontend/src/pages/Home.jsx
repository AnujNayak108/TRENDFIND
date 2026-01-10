import { useState, useEffect } from 'react'
import { scrapeAPI } from '../services/api'
import { useNavigate } from 'react-router-dom'

function Home() {
  const [status, setStatus] = useState(null)
  const [loading, setLoading] = useState(true)
  const navigate = useNavigate()

  useEffect(() => {
    // Fetch status on mount
    fetchStatus()
    
    // Poll status every 30 seconds
    const interval = setInterval(fetchStatus, 30000)
    
    return () => clearInterval(interval)
  }, [])

  const fetchStatus = async () => {
    try {
      const data = await scrapeAPI.getStatus()
      setStatus(data)
    } catch (error) {
      console.error('Error fetching scrape status:', error)
    } finally {
      setLoading(false)
    }
  }

  const formatTime = (isoString) => {
    if (!isoString) return 'Never'
    const date = new Date(isoString)
    const now = new Date()
    const diffMs = now - date
    const diffMins = Math.floor(diffMs / 60000)
    
    if (diffMins < 1) return 'Just now'
    if (diffMins < 60) return `${diffMins} minute${diffMins > 1 ? 's' : ''} ago`
    const diffHours = Math.floor(diffMins / 60)
    if (diffHours < 24) return `${diffHours} hour${diffHours > 1 ? 's' : ''} ago`
    const diffDays = Math.floor(diffHours / 24)
    return `${diffDays} day${diffDays > 1 ? 's' : ''} ago`
  }

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
      <div className="text-center">
        <h1 className="text-4xl font-bold text-gray-900 mb-4">
          Discover Trending Products
        </h1>
        <p className="text-xl text-gray-600 mb-8 max-w-2xl mx-auto">
          TrendFind automatically detects trending products from social media,
          identifies what they are, and shows you where to buy them.
        </p>

        {/* Automatic Scraping Status */}
        {loading ? (
          <div className="max-w-md mx-auto mb-12 p-6 bg-gray-50 rounded-lg">
            <p className="text-gray-600">Loading status...</p>
          </div>
        ) : status && (
          <div className="max-w-2xl mx-auto mb-12">
            <div className="bg-green-50 border-2 border-green-200 rounded-lg p-6 mb-6">
              <div className="flex items-center justify-center mb-4">
                <div className="bg-green-500 rounded-full p-2 mr-3">
                  <svg className="w-6 h-6 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                  </svg>
                </div>
                <h2 className="text-2xl font-semibold text-green-800">Automatic Scraping Active</h2>
              </div>
              <p className="text-green-700 mb-4">
                We're continuously monitoring social media for trending products every {status.interval_minutes} minutes.
              </p>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4 text-left">
                <div className="bg-white rounded p-4">
                  <p className="text-sm text-gray-600 mb-1">Last Scrape</p>
                  <p className="text-lg font-semibold text-gray-900">
                    {formatTime(status.last_scrape_time)}
                  </p>
                  {status.last_scrape_status?.success && status.last_scrape_status?.scraping && (
                    <p className="text-xs text-gray-500 mt-1">
                      {status.last_scrape_status.scraping.total} trends found
                    </p>
                  )}
                </div>
                {status.next_scrape_time && (
                  <div className="bg-white rounded p-4">
                    <p className="text-sm text-gray-600 mb-1">Next Scrape</p>
                    <p className="text-lg font-semibold text-gray-900">
                      {formatTime(status.next_scrape_time)}
                    </p>
                  </div>
                )}
              </div>
            </div>
          </div>
        )}

        <div className="flex justify-center space-x-4 mb-12">
          <button
            onClick={() => navigate('/products')}
            className="bg-primary-600 text-white px-8 py-3 rounded-lg font-semibold hover:bg-primary-700 transition-colors shadow-lg"
          >
            View Trending Products
          </button>
        </div>

        <div className="mt-16 grid grid-cols-1 md:grid-cols-3 gap-8">
          <div className="bg-white p-6 rounded-lg shadow-md">
            <div className="text-primary-600 text-3xl mb-4">🔍</div>
            <h3 className="text-xl font-semibold mb-2">Auto-Detect</h3>
            <p className="text-gray-600">
              Automatically detects trending products from Google Trends, YouTube, and Instagram.
            </p>
          </div>
          <div className="bg-white p-6 rounded-lg shadow-md">
            <div className="text-primary-600 text-3xl mb-4">🤖</div>
            <h3 className="text-xl font-semibold mb-2">AI-Powered</h3>
            <p className="text-gray-600">
              Uses NLP to identify product names and extract key information.
            </p>
          </div>
          <div className="bg-white p-6 rounded-lg shadow-md">
            <div className="text-primary-600 text-3xl mb-4">🛒</div>
            <h3 className="text-xl font-semibold mb-2">Buy Links</h3>
            <p className="text-gray-600">
              Find buying options from multiple e-commerce platforms.
            </p>
          </div>
        </div>
      </div>
    </div>
  )
}

export default Home

