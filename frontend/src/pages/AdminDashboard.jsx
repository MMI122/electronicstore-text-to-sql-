import React, { useState } from 'react'
import { useQuery } from '@tanstack/react-query'
import BankingDashboard from '../components/BankingDashboard'
import ProductList from '../components/ProductList'
import {
  ChartBarIcon,
  CurrencyDollarIcon,
  ShoppingBagIcon,
  UsersIcon,
  BuildingStorefrontIcon,
  CreditCardIcon,
  CogIcon
} from '@heroicons/react/24/outline'
import { Line, Bar, Doughnut } from 'react-chartjs-2'
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  BarElement,
  Title,
  Tooltip,
  Legend,
  ArcElement,
} from 'chart.js'
import axios from 'axios'

ChartJS.register(
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  BarElement,
  Title,
  Tooltip,
  Legend,
  ArcElement
)

const API_BASE_URL = 'http://localhost:5000/api'

const AdminDashboard = () => {
  const [activeTab, setActiveTab] = useState('analytics')

  // Get auth headers
  const getAuthHeaders = () => {
    const sessionId = localStorage.getItem('session_id')
    return sessionId ? { Authorization: `Bearer ${sessionId}` } : {}
  }

  // Fetch analytics data
  const { data: analyticsData, isLoading: analyticsLoading } = useQuery({
    queryKey: ['analytics'],
    queryFn: async () => {
      const [productsRes, ordersRes] = await Promise.all([
        axios.get(`${API_BASE_URL}/products/analytics`, { headers: getAuthHeaders() }),
        axios.get(`${API_BASE_URL}/orders/analytics?days=30`, { headers: getAuthHeaders() })
      ])
      return {
        products: productsRes.data,
        orders: ordersRes.data
      }
    }
  })

  const tabs = [
    { id: 'analytics', name: 'Analytics', icon: ChartBarIcon },
    { id: 'products', name: 'Product Management', icon: CogIcon },
    { id: 'banking', name: 'Banking', icon: CreditCardIcon },
  ]

  const renderSalesChart = () => {
    if (!analyticsData?.orders?.sales_trend) return null

    const chartData = {
      labels: analyticsData.orders.sales_trend.slice(0, 7).reverse().map(item => 
        new Date(item.order_date).toLocaleDateString()
      ),
      datasets: [
        {
          label: 'Revenue',
          data: analyticsData.orders.sales_trend.slice(0, 7).reverse().map(item => item.revenue),
          borderColor: 'rgb(59, 130, 246)',
          backgroundColor: 'rgba(59, 130, 246, 0.1)',
          tension: 0.4,
        },
        {
          label: 'Orders',
          data: analyticsData.orders.sales_trend.slice(0, 7).reverse().map(item => item.order_count),
          borderColor: 'rgb(16, 185, 129)',
          backgroundColor: 'rgba(16, 185, 129, 0.1)',
          tension: 0.4,
          yAxisID: 'y1',
        }
      ],
    }

    const options = {
      responsive: true,
      interaction: {
        mode: 'index',
        intersect: false,
      },
      scales: {
        x: {
          display: true,
          title: {
            display: true,
            text: 'Date'
          }
        },
        y: {
          type: 'linear',
          display: true,
          position: 'left',
          title: {
            display: true,
            text: 'Revenue ($)'
          }
        },
        y1: {
          type: 'linear',
          display: true,
          position: 'right',
          title: {
            display: true,
            text: 'Orders Count'
          },
          grid: {
            drawOnChartArea: false,
          },
        },
      },
      plugins: {
        legend: {
          position: 'top',
        },
        title: {
          display: true,
          text: 'Sales Trend (Last 7 Days)',
        },
      },
    }

    return <Line data={chartData} options={options} />
  }

  const renderCategoryChart = () => {
    if (!analyticsData?.products?.category_performance) return null

    const chartData = {
      labels: analyticsData.products.category_performance.slice(0, 8).map(item => item.category_name),
      datasets: [
        {
          label: 'Revenue',
          data: analyticsData.products.category_performance.slice(0, 8).map(item => item.revenue || 0),
          backgroundColor: [
            'rgba(255, 99, 132, 0.8)',
            'rgba(54, 162, 235, 0.8)',
            'rgba(255, 205, 86, 0.8)',
            'rgba(75, 192, 192, 0.8)',
            'rgba(153, 102, 255, 0.8)',
            'rgba(255, 159, 64, 0.8)',
            'rgba(199, 199, 199, 0.8)',
            'rgba(83, 102, 255, 0.8)',
          ],
        },
      ],
    }

    const options = {
      responsive: true,
      plugins: {
        legend: {
          position: 'right',
        },
        title: {
          display: true,
          text: 'Revenue by Category',
        },
      },
    }

    return <Doughnut data={chartData} options={options} />
  }

  const renderPaymentMethodChart = () => {
    if (!analyticsData?.orders?.payment_methods) return null

    const chartData = {
      labels: analyticsData.orders.payment_methods.map(item => item.payment_method),
      datasets: [
        {
          label: 'Transaction Count',
          data: analyticsData.orders.payment_methods.map(item => item.transaction_count),
          backgroundColor: [
            'rgba(59, 130, 246, 0.8)',
            'rgba(16, 185, 129, 0.8)',
            'rgba(245, 158, 11, 0.8)',
            'rgba(239, 68, 68, 0.8)',
            'rgba(139, 92, 246, 0.8)',
          ],
        },
      ],
    }

    const options = {
      responsive: true,
      plugins: {
        legend: {
          position: 'top',
        },
        title: {
          display: true,
          text: 'Payment Methods Usage',
        },
      },
      scales: {
        y: {
          beginAtZero: true,
          title: {
            display: true,
            text: 'Number of Transactions'
          }
        }
      },
    }

    return <Bar data={chartData} options={options} />
  }

  if (analyticsLoading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
        <span className="ml-2 text-gray-600">Loading analytics...</span>
      </div>
    )
  }

  return (
    <div className="space-y-8">
      {/* Header */}
      <div className="text-center">
        <h1 className="text-4xl font-bold text-gray-900 mb-2">
          Admin Dashboard
        </h1>
        <p className="text-lg text-gray-600">
          Comprehensive analytics and management tools
        </p>
      </div>

      {/* Key Metrics Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        <div className="bg-white rounded-lg shadow-md p-6 border border-gray-200">
          <div className="flex items-center">
            <div className="p-3 rounded-lg bg-blue-500 text-white">
              <CurrencyDollarIcon className="h-6 w-6" />
            </div>
            <div className="ml-4">
              <p className="text-sm font-medium text-gray-500 uppercase tracking-wide">
                Total Revenue (30d)
              </p>
              <p className="text-2xl font-bold text-gray-900">
                ${analyticsData?.orders?.sales_trend?.reduce((sum, day) => sum + (day.revenue || 0), 0).toLocaleString() || '0'}
              </p>
            </div>
          </div>
        </div>

        <div className="bg-white rounded-lg shadow-md p-6 border border-gray-200">
          <div className="flex items-center">
            <div className="p-3 rounded-lg bg-green-500 text-white">
              <ShoppingBagIcon className="h-6 w-6" />
            </div>
            <div className="ml-4">
              <p className="text-sm font-medium text-gray-500 uppercase tracking-wide">
                Total Orders (30d)
              </p>
              <p className="text-2xl font-bold text-gray-900">
                {analyticsData?.orders?.sales_trend?.reduce((sum, day) => sum + (day.order_count || 0), 0).toLocaleString() || '0'}
              </p>
            </div>
          </div>
        </div>

        <div className="bg-white rounded-lg shadow-md p-6 border border-gray-200">
          <div className="flex items-center">
            <div className="p-3 rounded-lg bg-purple-500 text-white">
              <UsersIcon className="h-6 w-6" />
            </div>
            <div className="ml-4">
              <p className="text-sm font-medium text-gray-500 uppercase tracking-wide">
                Top Customers
              </p>
              <p className="text-2xl font-bold text-gray-900">
                {analyticsData?.orders?.top_customers?.length || '0'}
              </p>
            </div>
          </div>
        </div>

        <div className="bg-white rounded-lg shadow-md p-6 border border-gray-200">
          <div className="flex items-center">
            <div className="p-3 rounded-lg bg-yellow-500 text-white">
              <BuildingStorefrontIcon className="h-6 w-6" />
            </div>
            <div className="ml-4">
              <p className="text-sm font-medium text-gray-500 uppercase tracking-wide">
                Avg Order Value
              </p>
              <p className="text-2xl font-bold text-gray-900">
                ${((analyticsData?.orders?.sales_trend?.reduce((sum, day) => sum + (day.revenue || 0), 0) || 0) / 
                   (analyticsData?.orders?.sales_trend?.reduce((sum, day) => sum + (day.order_count || 0), 0) || 1)).toFixed(2)}
              </p>
            </div>
          </div>
        </div>
      </div>

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
      {activeTab === 'analytics' && (
        <div className="space-y-8">
          {/* Charts */}
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
            <div className="bg-white p-6 rounded-lg shadow-md border border-gray-200">
              {renderSalesChart()}
            </div>
            <div className="bg-white p-6 rounded-lg shadow-md border border-gray-200">
              {renderCategoryChart()}
            </div>
          </div>

          <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
            <div className="bg-white p-6 rounded-lg shadow-md border border-gray-200">
              {renderPaymentMethodChart()}
            </div>
            <div className="bg-white p-6 rounded-lg shadow-md border border-gray-200">
              <h3 className="text-lg font-semibold mb-4">Top Selling Products</h3>
              <div className="space-y-3">
                {analyticsData?.products?.top_selling_products?.slice(0, 5).map((product, index) => (
                  <div key={index} className="flex items-center justify-between p-3 bg-gray-50 rounded-md">
                    <div>
                      <p className="font-medium text-gray-900">{product.product_name}</p>
                      <p className="text-sm text-gray-600">{product.brand}</p>
                    </div>
                    <div className="text-right">
                      <p className="font-semibold text-gray-900">{product.total_sold} sold</p>
                      <p className="text-sm text-green-600">${product.revenue?.toLocaleString()}</p>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          </div>

          {/* Top Customers Table */}
          <div className="bg-white rounded-lg shadow-md border border-gray-200">
            <div className="p-6 border-b border-gray-200">
              <h3 className="text-lg font-semibold text-gray-900">Top Customers</h3>
            </div>
            <div className="overflow-x-auto">
              <table className="min-w-full divide-y divide-gray-200">
                <thead className="bg-gray-50">
                  <tr>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Customer
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Email
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Orders
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Total Spent
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Avg Order Value
                    </th>
                  </tr>
                </thead>
                <tbody className="bg-white divide-y divide-gray-200">
                  {analyticsData?.orders?.top_customers?.slice(0, 10).map((customer, index) => (
                    <tr key={index} className="hover:bg-gray-50">
                      <td className="px-6 py-4 whitespace-nowrap">
                        <div className="font-medium text-gray-900">{customer.customer_name}</div>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                        {customer.email}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                        {customer.order_count}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                        ${parseFloat(customer.total_spent || 0).toLocaleString()}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                        ${parseFloat(customer.avg_order_value || 0).toFixed(2)}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        </div>
      )}

      {activeTab === 'products' && <ProductList />}

      {activeTab === 'banking' && <BankingDashboard />}
    </div>
  )
}

export default AdminDashboard