import React from 'react'
import { 
  ShoppingBagIcon, 
  ChartBarIcon, 
  CurrencyDollarIcon,
  UsersIcon,
  ExclamationTriangleIcon,
  ArrowUpIcon,
  ArrowDownIcon
} from '@heroicons/react/24/outline'

const MetricsCards = ({ statsCards, isLoading }) => {
  const formatValue = (value, title) => {
    if (isLoading) return '...'
    
    // Handle currency values
    if (title.includes('Revenue') || title.includes('$')) {
      if (typeof value === 'string' && value.startsWith('$')) {
        return value
      }
      return `$${parseFloat(value || 0).toLocaleString('en-US', { 
        minimumFractionDigits: 2, 
        maximumFractionDigits: 2 
      })}`
    }
    
    // Handle numeric values
    if (typeof value === 'number') {
      return value.toLocaleString()
    }
    
    return value || '0'
  }

  const getTrendIcon = (title, value) => {
    if (title.includes('Low Stock') && value > 0) {
      return <ExclamationTriangleIcon className="h-4 w-4 text-red-500" />
    }
    if (title.includes('Revenue') && value > 0) {
      return <ArrowUpIcon className="h-4 w-4 text-green-500" />
    }
    return null
  }

  return (
    <div className="w-full">
      {/* Desktop: Horizontal scrollable cards */}
      <div className="hidden md:block">
        <div className="flex space-x-4 overflow-x-auto pb-4 scrollbar-thin scrollbar-thumb-gray-300 scrollbar-track-gray-100 metrics-scroll">
          {statsCards.map((stat, index) => (
            <div 
              key={index} 
              className="flex-shrink-0 w-80 bg-white rounded-lg shadow-md p-6 border border-gray-200 hover:shadow-lg transition-shadow duration-200 metrics-card"
            >
              <div className="flex items-start justify-between">
                <div className="flex-1 min-w-0">
                  <div className="flex items-center space-x-2 mb-2">
                    <p className="text-sm font-medium text-gray-500 uppercase tracking-wide truncate">
                      {stat.title}
                    </p>
                    {getTrendIcon(stat.title, stat.value)}
                  </div>
                  <p className="text-3xl font-bold text-gray-900 break-words">
                    {formatValue(stat.value, stat.title)}
                  </p>
                  {stat.subtitle && (
                    <p className="text-sm text-gray-600 mt-1">
                      {stat.subtitle}
                    </p>
                  )}
                </div>
                <div className={`${stat.color} rounded-lg p-3 flex-shrink-0 ml-4`}>
                  <stat.icon className="h-6 w-6 text-white" />
                </div>
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Mobile: Vertical stacked cards */}
      <div className="md:hidden space-y-4">
        {statsCards.map((stat, index) => (
          <div 
            key={index} 
            className="bg-white rounded-lg shadow-md p-4 border border-gray-200"
          >
            <div className="flex items-center justify-between">
              <div className="flex-1 min-w-0">
                <div className="flex items-center space-x-2 mb-1">
                  <p className="text-sm font-medium text-gray-500 uppercase tracking-wide truncate">
                    {stat.title}
                  </p>
                  {getTrendIcon(stat.title, stat.value)}
                </div>
                <p className="text-2xl font-bold text-gray-900 break-words">
                  {formatValue(stat.value, stat.title)}
                </p>
                {stat.subtitle && (
                  <p className="text-xs text-gray-600 mt-1">
                    {stat.subtitle}
                  </p>
                )}
              </div>
              <div className={`${stat.color} rounded-lg p-2 flex-shrink-0 ml-3`}>
                <stat.icon className="h-5 w-5 text-white" />
              </div>
            </div>
          </div>
        ))}
      </div>

      {/* Scroll indicator for desktop */}
      <div className="hidden md:flex justify-center mt-2">
        <div className="flex space-x-1">
          {statsCards.map((_, index) => (
            <div 
              key={index}
              className="w-2 h-2 bg-gray-300 rounded-full"
            />
          ))}
        </div>
      </div>
    </div>
  )
}

export default MetricsCards
