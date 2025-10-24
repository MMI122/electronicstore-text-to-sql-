import React from 'react'
import { Link, useLocation } from 'react-router-dom'
import { useQuery } from '@tanstack/react-query'
import { 
  HomeIcon, 
  CogIcon, 
  ChartBarIcon, 
  ShoppingCartIcon,
  UserIcon,
  ArrowRightOnRectangleIcon,
  ShieldCheckIcon,
  LockClosedIcon
} from '@heroicons/react/24/outline'
import axios from 'axios'

const API_BASE_URL = 'http://localhost:5000/api'

const Navbar = ({ customer, onLogout, onShowCart, onShowAdminAuth, isAdminAuthenticated, onAdminLogout }) => {
  const location = useLocation()

  // Fetch cart count
  const { data: cartData } = useQuery({
    queryKey: ['cart', customer?.customer_id],
    queryFn: async () => {
      console.log('Fetching cart for customer:', customer.customer_id)
      const response = await axios.get(`${API_BASE_URL}/cart/${customer.customer_id}`)
      console.log('Cart data:', response.data)
      return response.data
    },
    enabled: !!customer?.customer_id
  })

  const navigation = [
    { name: 'Home', href: '/', icon: HomeIcon },
  ]

  const adminNavigation = [
    { name: 'Admin Panel', href: '/admin', icon: CogIcon },
  ]

  const cartItemCount = cartData?.summary?.item_count || 0

  return (
    <nav className="bg-white shadow-lg border-b border-gray-200">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex justify-between h-16">
          <div className="flex items-center">
            <div className="flex-shrink-0 flex items-center">
              <ChartBarIcon className="h-8 w-8 text-blue-600" />
              <h1 className="ml-2 text-xl font-bold text-gray-900">
                Gadgets Store
              </h1>
            </div>
          </div>
          
          <div className="flex items-center space-x-4">
            {/* Regular Navigation */}
            {navigation.map((item) => {
              const isActive = location.pathname === item.href
              return (
                <Link
                  key={item.name}
                  to={item.href}
                  className={`inline-flex items-center px-3 py-2 border border-transparent text-sm leading-4 font-medium rounded-md transition-colors duration-200 ${
                    isActive
                      ? 'text-blue-700 bg-blue-100'
                      : 'text-gray-500 hover:text-gray-700 hover:bg-gray-100'
                  }`}
                >
                  <item.icon className="h-4 w-4 mr-1.5" />
                  {item.name}
                </Link>
              )
            })}

            {/* Admin Navigation */}
            {isAdminAuthenticated && adminNavigation.map((item) => {
              const isActive = location.pathname === item.href
              return (
                <Link
                  key={item.name}
                  to={item.href}
                  className={`inline-flex items-center px-3 py-2 border border-transparent text-sm leading-4 font-medium rounded-md transition-colors duration-200 ${
                    isActive
                      ? 'text-red-700 bg-red-100'
                      : 'text-red-600 hover:text-red-700 hover:bg-red-50'
                  }`}
                >
                  <item.icon className="h-4 w-4 mr-1.5" />
                  {item.name}
                </Link>
              )
            })}

            {/* Admin Login Button */}
            {!isAdminAuthenticated && (
              <button
                onClick={onShowAdminAuth}
                className="inline-flex items-center px-3 py-2 border border-red-300 text-sm leading-4 font-medium rounded-md text-red-600 hover:text-red-700 hover:bg-red-50 transition-colors duration-200"
              >
                <LockClosedIcon className="h-4 w-4 mr-1.5" />
                Admin Login
              </button>
            )}

            {/* Admin Logout Button */}
            {isAdminAuthenticated && (
              <button
                onClick={onAdminLogout}
                className="inline-flex items-center px-3 py-2 border border-transparent text-sm leading-4 font-medium rounded-md text-red-600 hover:text-red-700 hover:bg-red-50 transition-colors duration-200"
              >
                <ShieldCheckIcon className="h-4 w-4 mr-1.5" />
                Admin Logout
              </button>
            )}

            {/* Shopping Cart */}
            {customer && (
              <button
                onClick={onShowCart}
                className="relative inline-flex items-center px-3 py-2 border border-transparent text-sm leading-4 font-medium rounded-md text-gray-500 hover:text-gray-700 hover:bg-gray-100 transition-colors duration-200"
              >
                <ShoppingCartIcon className="h-4 w-4 mr-1.5" />
                Cart
                {cartItemCount > 0 && (
                  <span className="absolute -top-1 -right-1 bg-red-500 text-white text-xs rounded-full h-5 w-5 flex items-center justify-center">
                    {cartItemCount}
                  </span>
                )}
              </button>
            )}

            {/* Customer Info and Logout */}
            {customer && (
              <div className="flex items-center space-x-3 pl-4 border-l border-gray-200">
                <div className="flex items-center space-x-2">
                  <UserIcon className="h-4 w-4 text-gray-500" />
                  <span className="text-sm text-gray-700">
                    {customer.first_name} {customer.last_name}
                  </span>
                </div>
                <button
                  onClick={onLogout}
                  className="inline-flex items-center px-3 py-2 border border-transparent text-sm leading-4 font-medium rounded-md text-red-600 hover:text-red-700 hover:bg-red-50 transition-colors duration-200"
                >
                  <ArrowRightOnRectangleIcon className="h-4 w-4 mr-1.5" />
                  Logout
                </button>
              </div>
            )}
          </div>
        </div>
      </div>
    </nav>
  )
}

export default Navbar