import React, { useState } from 'react'
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom'
import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import Navbar from './components/Navbar'
import Home from './pages/Home'
import AdminPanel from './pages/AdminPanel'
import CustomerAuth from './components/CustomerAuth'
import ShoppingCart from './components/ShoppingCart'
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

  // Load customer from localStorage on app start
  React.useEffect(() => {
    const savedCustomer = localStorage.getItem('customer')
    if (savedCustomer) {
      setCustomer(JSON.parse(savedCustomer))
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
              <Route path="/admin" element={<AdminPanel />} />
            </Routes>
          </main>

          {/* Shopping Cart Modal */}
          {showCart && (
            <ShoppingCart
              customerId={customer?.customer_id}
              onClose={() => setShowCart(false)}
            />
          )}
        </div>
      </Router>
    </QueryClientProvider>
  )
}

export default App