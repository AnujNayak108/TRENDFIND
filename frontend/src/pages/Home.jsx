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
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12 relative">
      <div className="absolute top-20 left-10 w-72 h-72 bg-primary-500 rounded-full mix-blend-screen mix-blend-multiply filter blur-[128px] opacity-20 animate-blob"></div>
      <div className="absolute top-40 right-10 w-72 h-72 bg-accent-pink rounded-full mix-blend-screen mix-blend-multiply filter blur-[128px] opacity-20 animate-blob animation-delay-2000"></div>

      <div className="text-center relative z-10 animate-fade-in mt-16 mb-20">
        <h1 className="text-5xl md:text-7xl font-display font-black text-white mb-6 tracking-tight">
          Discover <span className="text-gradient">Trending</span> Products
        </h1>
        <p className="text-xl text-gray-400 mb-10 max-w-2xl mx-auto font-light leading-relaxed">
          TrendFind automatically detects trending products from social media,
          identifies what they are, and shows you exactly where to buy them.
        </p>

        <div className="flex justify-center space-x-6 mb-16">
          <button
            onClick={() => navigate('/products')}
            className="group relative px-8 py-4 bg-primary-600 text-white rounded-full font-semibold hover:bg-primary-500 transition-all duration-300 shadow-[0_0_40px_rgba(37,99,235,0.4)] hover:shadow-[0_0_60px_rgba(37,99,235,0.6)] hover:-translate-y-1"
          >
            Explore Trends Now 
            <span className="inline-block transition-transform group-hover:translate-x-1 ml-2">→</span>
          </button>
        </div>

        {/* Automatic Scraping Status Dashboard */}
        {loading ? (
          <div className="max-w-md mx-auto mb-16 glass-card p-8">
            <div className="w-8 h-8 border-t-2 border-primary-500 border-solid rounded-full animate-spin mx-auto"></div>
            <p className="text-gray-400 mt-4 font-medium">Initializing AI Scraper...</p>
          </div>
        ) : status && (
          <div className="max-w-3xl mx-auto mb-20 animate-fade-in">
            <div className="glass-card p-8 border border-green-500/20 relative overflow-hidden">
              <div className="absolute top-0 left-0 w-full h-1 bg-gradient-to-r from-green-400 to-green-600"></div>
              
              <div className="flex items-center justify-center mb-6">
                <div className="relative">
                  <div className="absolute inset-0 bg-green-500 rounded-full blur animate-pulse"></div>
                  <div className="relative bg-green-500/20 border border-green-500 rounded-full p-2 mr-4">
                    <svg className="w-5 h-5 text-green-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                    </svg>
                  </div>
                </div>
                <h2 className="text-2xl font-display font-bold text-white tracking-wide">Monitoring Active</h2>
              </div>
              
              <p className="text-green-400/80 mb-8 font-medium">
                Continuously scanning social media for trending products every <span className="text-green-300 font-bold">{status.interval_minutes} minutes</span>.
              </p>
              
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6 text-left">
                <div className="bg-surface/50 border border-white/5 rounded-xl p-5 hover:border-white/10 transition-colors">
                  <p className="text-sm font-medium text-gray-400 mb-2 uppercase tracking-wider">Last Sync</p>
                  <p className="text-xl font-display font-semibold text-white">
                    {formatTime(status.last_scrape_time)}
                  </p>
                  {status.last_scrape_status?.success && status.last_scrape_status?.scraping && (
                    <div className="mt-3 inline-flex items-center px-2.5 py-1 rounded-full text-xs font-semibold bg-green-500/10 text-green-400 border border-green-500/20">
                      {status.last_scrape_status.scraping.total} trends discovered
                    </div>
                  )}
                </div>
                {status.next_scrape_time && (
                  <div className="bg-surface/50 border border-white/5 rounded-xl p-5 hover:border-white/10 transition-colors">
                    <p className="text-sm font-medium text-gray-400 mb-2 uppercase tracking-wider">Next Scan</p>
                    <p className="text-xl font-display font-semibold text-white">
                      {formatTime(status.next_scrape_time)}
                    </p>
                    <div className="mt-3 w-full bg-surface rounded-full h-1.5 overflow-hidden">
                      <div className="bg-primary-500 h-1.5 rounded-full w-2/3 animate-pulse"></div>
                    </div>
                  </div>
                )}
              </div>
            </div>
          </div>
        )}

        <div className="grid grid-cols-1 md:grid-cols-3 gap-8 mt-24">
          <div className="glass-card p-8 group">
            <div className="w-14 h-14 rounded-2xl bg-primary-500/10 border border-primary-500/20 flex items-center justify-center mb-6 ml-auto mr-auto transition-transform group-hover:scale-110 group-hover:rotate-3 duration-300">
              <span className="text-primary-400 text-2xl">🔍</span>
            </div>
            <h3 className="text-xl font-display font-semibold text-white mb-3">Global Scanning</h3>
            <p className="text-gray-400 leading-relaxed text-sm">
              Automatically detects trending signals across TikTok, Google Trends, YouTube, and Instagram.
            </p>
          </div>
          <div className="glass-card p-8 group">
            <div className="w-14 h-14 rounded-2xl bg-accent-purple/10 border border-accent-purple/20 flex items-center justify-center mb-6 ml-auto mr-auto transition-transform group-hover:scale-110 group-hover:-rotate-3 duration-300">
              <span className="text-accent-purple text-2xl">🧠</span>
            </div>
            <h3 className="text-xl font-display font-semibold text-white mb-3">AI Intelligence</h3>
            <p className="text-gray-400 leading-relaxed text-sm">
              Uses advanced NLP models to parse conversational noise and identify actual product names.
            </p>
          </div>
          <div className="glass-card p-8 group">
            <div className="w-14 h-14 rounded-2xl bg-accent-pink/10 border border-accent-pink/20 flex items-center justify-center mb-6 ml-auto mr-auto transition-transform group-hover:scale-110 group-hover:rotate-3 duration-300">
              <span className="text-accent-pink text-2xl">🛒</span>
            </div>
            <h3 className="text-xl font-display font-semibold text-white mb-3">Instant Checkout</h3>
            <p className="text-gray-400 leading-relaxed text-sm">
              Automatically finds direct buying options and authentic retailers for the identified trends.
            </p>
          </div>
        </div>
      </div>
    </div>
  )
}

export default Home

