import { Link } from 'react-router-dom'

function Navbar() {
  return (
    <nav className="fixed top-0 left-0 right-0 z-50 transition-all duration-300">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 mt-4">
        <div className="glass rounded-2xl px-6 py-3 flex justify-between items-center shadow-[0_8px_32px_0_rgba(0,0,0,0.36)] border border-white/10">
          <div className="flex items-center">
            <Link to="/" className="flex items-center space-x-2">
              <span className="text-2xl font-display font-black text-gradient tracking-tight">TrendFind</span>
            </Link>
          </div>
          <div className="flex items-center space-x-6">
            <Link
              to="/"
              className="text-gray-300 hover:text-white text-sm font-medium transition-colors"
            >
              Home
            </Link>
            <Link
              to="/products"
              className="text-gray-300 hover:text-white text-sm font-medium transition-colors"
            >
              Explore Products
            </Link>
          </div>
        </div>
      </div>
    </nav>
  )
}

export default Navbar

