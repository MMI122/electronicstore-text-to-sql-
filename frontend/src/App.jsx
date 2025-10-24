import React, { useState } from 'react'
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom'
import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import Navbar from './components/Navbar'
import Home from './pages/Home'
import AdminPanel from './pages/AdminPanel'
import CustomerAuth from './components/CustomerAuth'
import ShoppingCart from './components/ShoppingCart'
import AdminAuth from './components/AdminAuth'
import './App.css'

// Create a client
const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      refetchOnWindowFocus: false,
      retry: 1,
      staleTime: 5 * 60 * 1000, // 5 minutes
    },
  },
})

function App() {
  const [customer, setCustomer] = useState(null)
  const [showCart, setShowCart] = useState(false)
  const [showAdminAuth, setShowAdminAuth] = useState(false)
  const [isAdminAuthenticated, setIsAdminAuthenticated] = useState(false)

  const handleCustomerLogin = (customerData) => {
    console.log('Customer logged in:', customerData)
    setCustomer(customerData)
    localStorage.setItem('customer', JSON.stringify(customerData))
  }

  const handleCustomerLogout = () => {
    setCustomer(null)
    localStorage.removeItem('customer')
    setShowCart(false)
  }

  const handleAdminLogin = () => {
    setIsAdminAuthenticated(true)
    setShowAdminAuth(false)
  }

  const handleAdminLogout = () => {
    setIsAdminAuthenticated(false)
    localStorage.removeItem('admin_authenticated')
    localStorage.removeItem('admin_login_time')
  }

  const handleShowAdminAuth = () => {
    setShowAdminAuth(true)
  }

  const handleCancelAdminAuth = () => {
    setShowAdminAuth(false)
  }

  // Load customer and admin session from localStorage on app start
  React.useEffect(() => {
    const savedCustomer = localStorage.getItem('customer')
    if (savedCustomer) {
      setCustomer(JSON.parse(savedCustomer))
    }

    // Check admin authentication
    const adminAuth = localStorage.getItem('admin_authenticated')
    const adminLoginTime = localStorage.getItem('admin_login_time')
    
    if (adminAuth === 'true' && adminLoginTime) {
      const sessionAge = Date.now() - parseInt(adminLoginTime)
      const sessionTimeout = 30 * 60 * 1000 // 30 minutes
      
      if (sessionAge < sessionTimeout) {
        setIsAdminAuthenticated(true)
      } else {
        // Session expired
        localStorage.removeItem('admin_authenticated')
        localStorage.removeItem('admin_login_time')
      }
    }
  }, [])

  // Show login screen if no customer is logged in
  if (!customer) {
    return (
      <QueryClientProvider client={queryClient}>
        <CustomerAuth onCustomerLogin={handleCustomerLogin} />
      </QueryClientProvider>
    )
  }

  return (
    <QueryClientProvider client={queryClient}>
      <Router>
        <div className="min-h-screen bg-gray-50">
          <Navbar 
            customer={customer} 
            onLogout={handleCustomerLogout}
            onShowCart={() => setShowCart(true)}
            onShowAdminAuth={handleShowAdminAuth}
            isAdminAuthenticated={isAdminAuthenticated}
            onAdminLogout={handleAdminLogout}
          />
          <main className="container mx-auto px-4 py-8">
            <Routes>
              <Route 
                path="/" 
                element={
                  <Home 
                    customer={customer} 
                    onShowCart={() => setShowCart(true)} 
                  />
                } 
              />
              <Route 
                path="/admin" 
                element={
                  isAdminAuthenticated ? (
                    <AdminPanel onAdminLogout={handleAdminLogout} />
                  ) : (
                    <div className="text-center py-12">
                      <h2 className="text-2xl font-bold text-gray-900 mb-4">Access Denied</h2>
                      <p className="text-gray-600 mb-6">You need to authenticate to access the admin panel.</p>
                      <button
                        onClick={handleShowAdminAuth}
                        className="bg-red-600 text-white px-6 py-2 rounded-lg hover:bg-red-700 transition-colors"
                      >
                        Admin Login
                      </button>
                    </div>
                  )
                } 
              />
            </Routes>
          </main>

          {/* Shopping Cart Modal */}
          {showCart && (
            <ShoppingCart
              customerId={customer?.customer_id}
              onClose={() => setShowCart(false)}
            />
          )}

          {/* Admin Authentication Modal */}
          {showAdminAuth && (
            <AdminAuth
              onAdminLogin={handleAdminLogin}
              onCancel={handleCancelAdminAuth}
            />
          )}
        </div>
      </Router>
    </QueryClientProvider>
  )
}

export default App