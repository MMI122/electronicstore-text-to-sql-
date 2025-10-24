import React, { useState } from 'react'
import { useQuery, useMutation } from '@tanstack/react-query'
import { 
  PaperAirplaneIcon, 
  SparklesIcon,
  DocumentTextIcon,
  ExclamationTriangleIcon,
  ClipboardDocumentIcon,
  LightBulbIcon
} from '@heroicons/react/24/outline'
import axios from 'axios'

const API_BASE_URL = 'http://localhost:5000/api'

const NaturalQuery = () => {
  const [query, setQuery] = useState('')
  const [queryHistory, setQueryHistory] = useState([])
  const [showSuggestions, setShowSuggestions] = useState(true)

  // Fetch query suggestions
  const { data: suggestionsData } = useQuery({
    queryKey: ['querySuggestions'],
    queryFn: async () => {
      const response = await axios.get(`${API_BASE_URL}/ai/suggestions`)
      return response.data
    }
  })

  // Execute natural language query
  const queryMutation = useMutation({
    mutationFn: async (naturalQuery) => {
      const response = await axios.post(`${API_BASE_URL}/ai/query`, {
        query: naturalQuery
      })
      return response.data
    },
    onSuccess: (data) => {
      setQueryHistory(prev => [{
        id: Date.now(),
        query: data.natural_query,
        sql: data.sql_query,
        results: data.results,
        rowCount: data.row_count,
        timestamp: new Date().toLocaleString()
      }, ...prev.slice(0, 9)]) // Keep only last 10 queries
      setQuery('')
      setShowSuggestions(false)
    }
  })

  const handleSubmit = (e) => {
    e.preventDefault()
    if (query.trim()) {
      queryMutation.mutate(query.trim())
    }
  }

  const handleSuggestionClick = (suggestion) => {
    setQuery(suggestion)
    setShowSuggestions(false)
  }

  const copyToClipboard = (text) => {
    navigator.clipboard.writeText(text)
    // You could add a toast notification here
  }

  const renderTable = (results) => {
    if (!results || results.length === 0) {
      return <p className="text-gray-500 text-center py-4">No results found</p>
    }

    const columns = Object.keys(results[0])

    return (
      <div className="overflow-x-auto">
        <table className="min-w-full divide-y divide-gray-200">
          <thead className="bg-gray-50">
            <tr>
              {columns.map((column) => (
                <th
                  key={column}
                  className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider"
                >
                  {column.replace(/_/g, ' ')}
                </th>
              ))}
            </tr>
          </thead>
          <tbody className="bg-white divide-y divide-gray-200">
            {results.map((row, index) => (
              <tr key={index} className="hover:bg-gray-50">
                {columns.map((column) => (
                  <td
                    key={column}
                    className="px-6 py-4 whitespace-nowrap text-sm text-gray-900"
                  >
                    {row[column] !== null && row[column] !== undefined 
                      ? String(row[column]) 
                      : '-'
                    }
                  </td>
                ))}
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    )
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="text-center">
        <SparklesIcon className="h-12 w-12 text-blue-600 mx-auto mb-4" />
        <h2 className="text-2xl font-bold text-gray-900 mb-2">
          AI-Powered Database Queries
        </h2>
        <p className="text-gray-600 max-w-2xl mx-auto">
          Ask questions about your store data in plain English. Our AI will convert them to SQL and show you the results.
        </p>
      </div>

      {/* Query Input */}
      <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
        <form onSubmit={handleSubmit} className="space-y-4">
          <div className="relative">
            <textarea
              value={query}
              onChange={(e) => setQuery(e.target.value)}
              placeholder="Ask me anything about your store... e.g., 'Show me the top 10 customers by spending' or 'What are the low stock products?'"
              rows={3}
              className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent resize-none"
              disabled={queryMutation.isPending}
            />
            <button
              type="submit"
              disabled={!query.trim() || queryMutation.isPending}
              className="absolute bottom-3 right-3 inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md text-white bg-blue-600 hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 disabled:opacity-50 disabled:cursor-not-allowed"
            >
              {queryMutation.isPending ? (
                <>
                  <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white mr-2"></div>
                  Processing...
                </>
              ) : (
                <>
                  <PaperAirplaneIcon className="h-4 w-4 mr-2" />
                  Ask AI
                </>
              )}
            </button>
          </div>
        </form>

        {/* Error Display */}
        {queryMutation.isError && (
          <div className="mt-4 p-4 bg-red-50 border border-red-200 rounded-md">
            <div className="flex">
              <ExclamationTriangleIcon className="h-5 w-5 text-red-400" />
              <div className="ml-3">
                <h3 className="text-sm font-medium text-red-800">Query Error</h3>
                <p className="mt-1 text-sm text-red-700">
                  {queryMutation.error?.response?.data?.error || queryMutation.error?.message}
                </p>
              </div>
            </div>
          </div>
        )}
      </div>

      {/* Query Suggestions */}
      {showSuggestions && suggestionsData?.suggestions && (
        <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
          <div className="flex items-center mb-4">
            <LightBulbIcon className="h-5 w-5 text-yellow-500 mr-2" />
            <h3 className="text-lg font-medium text-gray-900">Try these examples:</h3>
          </div>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-3">
            {suggestionsData.suggestions.slice(0, 9).map((suggestion, index) => (
              <button
                key={index}
                onClick={() => handleSuggestionClick(suggestion)}
                className="text-left p-3 border border-gray-200 rounded-lg hover:bg-blue-50 hover:border-blue-300 transition-colors duration-200 text-sm"
              >
                {suggestion}
              </button>
            ))}
          </div>
        </div>
      )}

      {/* Query Results */}
      {queryHistory.length > 0 && (
        <div className="space-y-6">
          <h3 className="text-xl font-semibold text-gray-900">Recent Queries</h3>
          {queryHistory.map((item) => (
            <div key={item.id} className="bg-white rounded-lg shadow-sm border border-gray-200">
              {/* Query Header */}
              <div className="p-4 border-b border-gray-200">
                <div className="flex items-start justify-between">
                  <div className="flex-1">
                    <h4 className="font-medium text-gray-900 mb-1">
                      "{item.query}"
                    </h4>
                    <p className="text-sm text-gray-500">
                      {item.timestamp} • {item.rowCount} results
                    </p>
                  </div>
                  <button
                    onClick={() => copyToClipboard(item.sql)}
                    className="ml-4 p-2 text-gray-400 hover:text-gray-600 rounded-md hover:bg-gray-100"
                    title="Copy SQL query"
                  >
                    <ClipboardDocumentIcon className="h-4 w-4" />
                  </button>
                </div>
              </div>

              {/* SQL Query */}
              <div className="p-4 bg-gray-50 border-b border-gray-200">
                <div className="flex items-center mb-2">
                  <DocumentTextIcon className="h-4 w-4 text-gray-500 mr-2" />
                  <span className="text-sm font-medium text-gray-700">Generated SQL:</span>
                </div>
                <pre className="text-sm text-gray-800 bg-white p-3 rounded border overflow-x-auto">
                  {item.sql}
                </pre>
              </div>

              {/* Results */}
              <div className="p-4">
                <div className="mb-3">
                  <span className="text-sm font-medium text-gray-700">Results:</span>
                </div>
                {renderTable(item.results)}
              </div>
            </div>
          ))}
        </div>
      )}

      {/* Help Text */}
      <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
        <div className="flex items-start">
          <SparklesIcon className="h-5 w-5 text-blue-600 mt-0.5 mr-3 flex-shrink-0" />
          <div className="text-sm text-blue-800">
            <h4 className="font-medium mb-1">How it works:</h4>
            <ul className="space-y-1 text-blue-700">
              <li>• Ask questions in plain English about your store data</li>
              <li>• The AI converts your question to SQL automatically</li>
              <li>• Results are displayed in an easy-to-read table format</li>
              <li>• You can see the generated SQL query for learning</li>
              <li>• Try complex queries with joins, aggregations, and filters</li>
            </ul>
          </div>
        </div>
      </div>
    </div>
  )
}

export default NaturalQuery