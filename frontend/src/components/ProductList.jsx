import React, { useState } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { 
  MagnifyingGlassIcon, 
  FunnelIcon,
  StarIcon,
  ShoppingCartIcon,
  ExclamationTriangleIcon,
  CheckCircleIcon
} from '@heroicons/react/24/outline'
import { StarIcon as StarIconSolid } from '@heroicons/react/24/solid'
import axios from 'axios'

const API_BASE_URL = 'http://localhost:5000/api'

const ProductList = ({ customer, onShowCart }) => {
  const [filters, setFilters] = useState({
    search: '',
    category: '',
    brand: '',
    minPrice: '',
    maxPrice: '',
    sortBy: 'product_name',
    sortOrder: 'ASC'
  })
  const [page, setPage] = useState(1)
  const [showFilters, setShowFilters] = useState(false)
  const [loadingProducts, setLoadingProducts] = useState(new Set())

  const queryClient = useQueryClient()

  // Add to cart mutation
  const addToCartMutation = useMutation({
    mutationFn: async ({ productId, quantity = 1 }) => {
      console.log('Adding to cart:', { customer_id: customer.customer_id, product_id: productId, quantity })
      setLoadingProducts(prev => new Set([...prev, productId]))
      const response = await axios.post(`${API_BASE_URL}/cart/add`, {
        customer_id: customer.customer_id,
        product_id: productId,
        quantity: quantity
      })
      console.log('Cart add response:', response.data)
      return response.data
    },
    onSuccess: (data, variables) => {
      console.log('Add to cart success:', data)
      setLoadingProducts(prev => {
        const newSet = new Set(prev)
        newSet.delete(variables.productId)
        return newSet
      })
      queryClient.invalidateQueries(['cart', customer?.customer_id])
      alert('Item added to cart!')
    },
    onError: (error, variables) => {
      console.error('Add to cart error:', error)
      setLoadingProducts(prev => {
        const newSet = new Set(prev)
        newSet.delete(variables.productId)
        return newSet
      })
      alert(error.response?.data?.error || 'Failed to add item to cart')
    }
  })

  // Fetch products
  const { data: productsData, isLoading, error } = useQuery({
    queryKey: ['products', filters, page],
    queryFn: async () => {
      // Build params and map camelCase frontend keys to snake_case expected by backend
      const paramsObj = { page: page.toString(), limit: '12' }
      Object.entries(filters).forEach(([k, v]) => {
        if (v === '' || v === null || typeof v === 'undefined') return
        let key = k
        // Map frontend keys to backend expected query param names
        if (k === 'minPrice') key = 'min_price'
        else if (k === 'maxPrice') key = 'max_price'
        else if (k === 'sortBy') key = 'sort_by'
        else if (k === 'sortOrder') key = 'sort_order'

        paramsObj[key] = String(v)
      })

      const params = new URLSearchParams(paramsObj)
      const response = await axios.get(`${API_BASE_URL}/products?${params}`)
      return response.data
    }
  })

  // Fetch categories for filter
  const { data: categoriesData } = useQuery({
    queryKey: ['categories'],
    queryFn: async () => {
      const response = await axios.get(`${API_BASE_URL}/products/categories`)
      return response.data
    }
  })

  // Fetch brands for filter
  const { data: brandsData } = useQuery({
    queryKey: ['brands'],
    queryFn: async () => {
      const response = await axios.get(`${API_BASE_URL}/products/brands`)
      return response.data
    }
  })

  const handleFilterChange = (key, value) => {
    setFilters(prev => ({ ...prev, [key]: value }))
    setPage(1) // Reset to first page
  }

  const handleSearch = (e) => {
    e.preventDefault()
    // Search is triggered by the query key change
  }

  const renderStars = (rating) => {
    const stars = []
    const fullStars = Math.floor(rating)
    const hasHalfStar = rating % 1 >= 0.5

    for (let i = 0; i < 5; i++) {
      if (i < fullStars) {
        stars.push(
          <StarIconSolid key={i} className="h-4 w-4 text-yellow-400" />
        )
      } else if (i === fullStars && hasHalfStar) {
        stars.push(
          <div key={i} className="relative">
            <StarIcon className="h-4 w-4 text-gray-300" />
            <div className="absolute inset-0 overflow-hidden w-1/2">
              <StarIconSolid className="h-4 w-4 text-yellow-400" />
            </div>
          </div>
        )
      } else {
        stars.push(
          <StarIcon key={i} className="h-4 w-4 text-gray-300" />
        )
      }
    }
    return stars
  }

  if (error) {
    return (
      <div className="text-center py-12">
        <ExclamationTriangleIcon className="h-12 w-12 text-red-500 mx-auto mb-4" />
        <p className="text-red-600">Error loading products: {error.message}</p>
      </div>
    )
  }

  return (
    <div className="space-y-6">
      {/* Search and Filter Bar */}
      <div className="bg-white p-6 rounded-lg shadow-sm border border-gray-200">
        <form onSubmit={handleSearch} className="space-y-4">
          <div className="flex flex-col sm:flex-row gap-4">
            <div className="flex-1">
              <div className="relative">
                <MagnifyingGlassIcon className="h-5 w-5 absolute left-3 top-3 text-gray-400" />
                <input
                  type="text"
                  placeholder="Search products..."
                  value={filters.search}
                  onChange={(e) => handleFilterChange('search', e.target.value)}
                  className="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                />
              </div>
            </div>
            <button
              type="button"
              onClick={() => setShowFilters(!showFilters)}
              className="inline-flex items-center px-4 py-2 border border-gray-300 rounded-md text-sm font-medium text-gray-700 bg-white hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-blue-500"
            >
              <FunnelIcon className="h-4 w-4 mr-2" />
              Filters
            </button>
          </div>

          {showFilters && (
            <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4 pt-4 border-t border-gray-200">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Category
                </label>
                <select
                  value={filters.category}
                  onChange={(e) => handleFilterChange('category', e.target.value)}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500"
                >
                  <option value="">All Categories</option>
                  {categoriesData?.categories?.map((category) => (
                    <option key={category.category_id} value={category.category_name}>
                      {category.category_name}
                    </option>
                  ))}
                </select>
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Brand
                </label>
                <select
                  value={filters.brand}
                  onChange={(e) => handleFilterChange('brand', e.target.value)}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500"
                >
                  <option value="">All Brands</option>
                  {brandsData?.brands?.map((brand) => (
                    <option key={brand.brand} value={brand.brand}>
                      {brand.brand}
                    </option>
                  ))}
                </select>
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Min Price
                </label>
                <input
                  type="number"
                  placeholder="0"
                  value={filters.minPrice}
                  onChange={(e) => handleFilterChange('minPrice', e.target.value)}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500"
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Max Price
                </label>
                <input
                  type="number"
                  placeholder="10000"
                  value={filters.maxPrice}
                  onChange={(e) => handleFilterChange('maxPrice', e.target.value)}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500"
                />
              </div>
            </div>
          )}
        </form>
      </div>

      {/* Products Grid */}
      {isLoading ? (
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6">
          {Array.from({ length: 8 }).map((_, index) => (
            <div key={index} className="bg-white rounded-lg shadow-sm border border-gray-200 p-4 animate-pulse">
              <div className="bg-gray-300 h-48 rounded-md mb-4"></div>
              <div className="space-y-2">
                <div className="bg-gray-300 h-4 rounded"></div>
                <div className="bg-gray-300 h-4 rounded w-3/4"></div>
                <div className="bg-gray-300 h-6 rounded w-1/2"></div>
              </div>
            </div>
          ))}
        </div>
      ) : (
        <>
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6">
            {productsData?.products?.map((product) => (
              <div key={product.product_id} className="bg-white rounded-lg shadow-sm border border-gray-200 hover:shadow-lg transition-shadow duration-200">
                <div className="p-4">
                  {/* Product Image Placeholder */}
                  <div className="bg-gray-100 h-48 rounded-md mb-4 flex items-center justify-center">
                    <ShoppingCartIcon className="h-12 w-12 text-gray-400" />
                  </div>

                  {/* Product Info */}
                  <div className="space-y-2">
                    <h3 className="font-semibold text-gray-900 line-clamp-2">
                      {product.product_name}
                    </h3>
                    <p className="text-sm text-gray-600">{product.brand}</p>
                    <p className="text-xs text-blue-600 bg-blue-50 px-2 py-1 rounded inline-block">
                      {product.category_name}
                    </p>

                    {/* Rating */}
                    {product.avg_rating > 0 && (
                      <div className="flex items-center space-x-1">
                        <div className="flex">
                          {renderStars(product.avg_rating)}
                        </div>
                        <span className="text-sm text-gray-600">
                          ({product.review_count})
                        </span>
                      </div>
                    )}

                    {/* Price and Stock */}
                    <div className="flex items-center justify-between">
                      <span className="text-xl font-bold text-gray-900">
                        ${product.price}
                      </span>
                      <span className={`text-sm px-2 py-1 rounded-full ${
                        product.stock_quantity > 10
                          ? 'bg-green-100 text-green-800'
                          : product.stock_quantity > 0
                          ? 'bg-yellow-100 text-yellow-800'
                          : 'bg-red-100 text-red-800'
                      }`}>
                        {product.stock_quantity > 0
                          ? `${product.stock_quantity} in stock`
                          : 'Out of stock'
                        }
                      </span>
                    </div>

                    {/* Warranty */}
                    {product.warranty_period && (
                      <p className="text-xs text-gray-500">
                        {product.warranty_period} months warranty
                      </p>
                    )}

                    {/* Add to Cart Button */}
                    {customer && (
                      <button
                        onClick={() => addToCartMutation.mutate({ productId: product.product_id })}
                        disabled={product.stock_quantity === 0 || loadingProducts.has(product.product_id)}
                        className={`w-full mt-3 px-4 py-2 rounded-lg flex items-center justify-center space-x-2 transition-colors ${
                          product.stock_quantity === 0
                            ? 'bg-gray-300 text-gray-500 cursor-not-allowed'
                            : 'bg-blue-600 text-white hover:bg-blue-700'
                        } disabled:opacity-50`}
                      >
                        <ShoppingCartIcon className="h-4 w-4" />
                        <span>
                          {loadingProducts.has(product.product_id)
                            ? 'Adding...' 
                            : product.stock_quantity === 0 
                            ? 'Out of Stock' 
                            : 'Add to Cart'
                          }
                        </span>
                      </button>
                    )}
                  </div>
                </div>
              </div>
            ))}
          </div>

          {/* Pagination */}
          {productsData?.pagination && (
            <div className="flex items-center justify-between border-t border-gray-200 bg-white px-4 py-3 sm:px-6 rounded-lg">
              <div className="flex flex-1 justify-between sm:hidden">
                <button
                  onClick={() => setPage(Math.max(1, page - 1))}
                  disabled={page === 1}
                  className="relative inline-flex items-center rounded-md border border-gray-300 bg-white px-4 py-2 text-sm font-medium text-gray-700 hover:bg-gray-50 disabled:opacity-50"
                >
                  Previous
                </button>
                <button
                  onClick={() => setPage(Math.min(productsData.pagination.pages, page + 1))}
                  disabled={page === productsData.pagination.pages}
                  className="relative ml-3 inline-flex items-center rounded-md border border-gray-300 bg-white px-4 py-2 text-sm font-medium text-gray-700 hover:bg-gray-50 disabled:opacity-50"
                >
                  Next
                </button>
              </div>
              <div className="hidden sm:flex sm:flex-1 sm:items-center sm:justify-between">
                <div>
                  <p className="text-sm text-gray-700">
                    Showing{' '}
                    <span className="font-medium">
                      {((page - 1) * 12) + 1}
                    </span>{' '}
                    to{' '}
                    <span className="font-medium">
                      {Math.min(page * 12, productsData.pagination.total)}
                    </span>{' '}
                    of{' '}
                    <span className="font-medium">
                      {productsData.pagination.total}
                    </span>{' '}
                    results
                  </p>
                </div>
                <div>
                  <nav className="isolate inline-flex -space-x-px rounded-md shadow-sm">
                    <button
                      onClick={() => setPage(Math.max(1, page - 1))}
                      disabled={page === 1}
                      className="relative inline-flex items-center rounded-l-md px-2 py-2 text-gray-400 ring-1 ring-inset ring-gray-300 hover:bg-gray-50 focus:z-20 focus:outline-offset-0 disabled:opacity-50"
                    >
                      Previous
                    </button>
                    {Array.from({ length: Math.min(5, productsData.pagination.pages) }, (_, i) => {
                      const pageNum = i + 1
                      return (
                        <button
                          key={pageNum}
                          onClick={() => setPage(pageNum)}
                          className={`relative inline-flex items-center px-4 py-2 text-sm font-semibold ${
                            page === pageNum
                              ? 'z-10 bg-blue-600 text-white focus:z-20 focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-blue-600'
                              : 'text-gray-900 ring-1 ring-inset ring-gray-300 hover:bg-gray-50 focus:z-20 focus:outline-offset-0'
                          }`}
                        >
                          {pageNum}
                        </button>
                      )
                    })}
                    <button
                      onClick={() => setPage(Math.min(productsData.pagination.pages, page + 1))}
                      disabled={page === productsData.pagination.pages}
                      className="relative inline-flex items-center rounded-r-md px-2 py-2 text-gray-400 ring-1 ring-inset ring-gray-300 hover:bg-gray-50 focus:z-20 focus:outline-offset-0 disabled:opacity-50"
                    >
                      Next
                    </button>
                  </nav>
                </div>
              </div>
            </div>
          )}
        </>
      )}
    </div>
  )
}

export default ProductList