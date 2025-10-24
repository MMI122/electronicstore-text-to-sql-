import React, { useState } from 'react'
import { useQuery } from '@tanstack/react-query'
import ProductList from '../components/ProductList'
import NaturalQuery from '../components/NaturalQuery'
import MetricsCards from '../components/MetricsCards'
import { 
  ShoppingBagIcon, 
  ChartBarIcon, 
  CurrencyDollarIcon,
  UsersIcon,
  SparklesIcon
} from '@heroicons/react/24/outline'
import axios from 'axios'

const API_BASE_URL = 'http://localhost:5000/api'

const Home = ({ customer, onShowCart }) => {
  const [activeTab, setActiveTab] = useState('products')

  // Fetch dashboard stats
  const { data: dashboardStats, isLoading: statsLoading } = useQuery({
    queryKey: ['dashboardStats'],
    queryFn: async () => {
      const [productsRes, ordersRes] = await Promise.all([
        axios.get(`${API_BASE_URL}/products/analytics`),
        axios.get(`${API_BASE_URL}/orders/analytics?days=30`)
      ])
      return {
        products: productsRes.data,
        orders: ordersRes.data
      }
    }
  })

  const tabs = [
    { id: 'products', name: 'Products', icon: ShoppingBagIcon },
    { id: 'ai-query', name: 'AI Query', icon: SparklesIcon },
  ]

  const statsCards = [
    {
      title: 'Total Products',
      value: dashboardStats?.products?.inventory_statistics?.total_products || 0,
      icon: ShoppingBagIcon,
      color: 'bg-blue-500',
      subtitle: 'Available in store'
    },
    {
      title: 'Low Stock Items',
      value: dashboardStats?.products?.inventory_statistics?.low_stock_count || 0,
      icon: ChartBarIcon,
      color: 'bg-yellow-500',
      subtitle: 'Need restocking'
    },
    {
      title: 'Total Revenue (30d)',
      value: dashboardStats?.orders?.sales_trend?.reduce((sum, day) => sum + (day.revenue || 0), 0) || 0,
      icon: CurrencyDollarIcon,
      color: 'bg-green-500',
      subtitle: 'Last 30 days'
    },
    {
      title: 'Active Customers',
      value: dashboardStats?.orders?.top_customers?.length || 0,
      icon: UsersIcon,
      color: 'bg-purple-500',
      subtitle: 'With recent orders'
    },
  ]

  return (
    <div className="space-y-8">
      {/* Header */}
      <div className="text-center">
        <h1 className="text-4xl font-bold text-gray-900 mb-2">
          Electronics Store Dashboard
        </h1>
        <p className="text-lg text-gray-600">
          Manage your gadgets store with AI-powered insights
        </p>
      </div>

      {/* Stats Cards - Horizontal Scrollable */}
      <MetricsCards statsCards={statsCards} isLoading={statsLoading} />

      {/* Tab Navigation */}
      <div className="border-b border-gray-200">
        <nav className="-mb-px flex space-x-8">
          {tabs.map((tab) => (
            <button
              key={tab.id}
              onClick={() => setActiveTab(tab.id)}
              className={`py-2 px-1 border-b-2 font-medium text-sm flex items-center space-x-2 transition-colors duration-200 ${
                activeTab === tab.id
                  ? 'border-blue-500 text-blue-600'
                  : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
              }`}
            >
              <tab.icon className="h-5 w-5" />
              <span>{tab.name}</span>
            </button>
          ))}
        </nav>
      </div>

      {/* Tab Content */}
      <div className="mt-8">
        {activeTab === 'products' && (
          <ProductList customer={customer} onShowCart={onShowCart} />
        )}
        {activeTab === 'ai-query' && <NaturalQuery />}
      </div>
    </div>
  )
}

export default Home