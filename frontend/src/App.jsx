import { BrowserRouter as Router, Routes, Route } from 'react-router-dom'
import Navbar from './components/Navbar'
import ProductList from './pages/ProductList'
import ProductDetail from './pages/ProductDetail'
import Home from './pages/Home'

function App() {
  return (
    <Router>
      <div className="min-h-screen bg-background text-gray-100 font-sans relative overflow-x-hidden">
        {/* Background Gradients */}
        <div className="fixed top-[-10%] left-[-10%] w-[40%] h-[40%] bg-primary-900/40 rounded-full blur-[120px] mix-blend-screen pointer-events-none" />
        <div className="fixed bottom-[-10%] right-[-10%] w-[40%] h-[40%] bg-accent-purple/20 rounded-full blur-[120px] mix-blend-screen pointer-events-none" />
        
        <Navbar />
        <div className="relative z-10 pt-20">
          <Routes>
            <Route path="/" element={<Home />} />
            <Route path="/products" element={<ProductList />} />
            <Route path="/products/:id" element={<ProductDetail />} />
          </Routes>
        </div>
      </div>
    </Router>
  )
}

export default App

