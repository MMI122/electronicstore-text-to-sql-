import React, { useState } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { 
  PlusIcon, 
  PencilIcon, 
  TrashIcon,
  MagnifyingGlassIcon,
  ExclamationTriangleIcon,
  CheckCircleIcon
} from '@heroicons/react/24/outline'
import axios from 'axios'

const API_BASE_URL = 'http://localhost:5000/api'

const ProductManagement = () => {
  const [showModal, setShowModal] = useState(false)
  const [editingProduct, setEditingProduct] = useState(null)
  const [filters, setFilters] = useState({
    search: '',
    category: '',
    brand: ''
  })
  const [page, setPage] = useState(1)

  const queryClient = useQueryClient()

  // Fetch products
  const { data: productsData, isLoading } = useQuery({
    queryKey: ['adminProducts', filters, page],
    queryFn: async () => {
      const params = new URLSearchParams({
        page: page.toString(),
        limit: '10',
        ...Object.fromEntries(Object.entries(filters).filter(([_, v]) => v !== ''))
      })
      const response = await axios.get(`${API_BASE_URL}/products?${params}`)
      return response.data
    }
  })

  // Fetch categories and suppliers for form
  const { data: categoriesData } = useQuery({
    queryKey: ['categories'],
    queryFn: async () => {
      const response = await axios.get(`${API_BASE_URL}/products/categories`)
      return response.data
    }
  })

  const { data: suppliersData } = useQuery({
    queryKey: ['suppliers'],
    queryFn: async () => {
      const response = await axios.get(`${API_BASE_URL}/products/suppliers`)
      return response.data
    }
  })

  // Mutations
  const createProductMutation = useMutation({
    mutationFn: async (productData) => {
      const response = await axios.post(`${API_BASE_URL}/products/admin`, productData)
      return response.data
    },
    onSuccess: () => {
      queryClient.invalidateQueries(['adminProducts'])
      setShowModal(false)
      setEditingProduct(null)
    }
  })

  const updateProductMutation = useMutation({
    mutationFn: async ({ id, data }) => {
      const response = await axios.put(`${API_BASE_URL}/products/admin/${id}`, data)
      return response.data
    },
    onSuccess: () => {
      queryClient.invalidateQueries(['adminProducts'])
      setShowModal(false)
      setEditingProduct(null)
    }
  })

  const deleteProductMutation = useMutation({
    mutationFn: async (productId) => {
      const response = await axios.delete(`${API_BASE_URL}/products/admin/${productId}`)
      return response.data
    },
    onSuccess: () => {
      queryClient.invalidateQueries(['adminProducts'])
    }
  })

  const updateStockMutation = useMutation({
    mutationFn: async ({ productId, quantityChange, reason }) => {
      const response = await axios.put(`${API_BASE_URL}/products/admin/stock/${productId}`, {
        quantity_change: quantityChange,
        transaction_type: 'ADJUSTMENT',
        reason: reason
      })
      return response.data
    },
    onSuccess: () => {
      queryClient.invalidateQueries(['adminProducts'])
    }
  })

  const handleSubmit = (formData) => {
    if (editingProduct) {
      updateProductMutation.mutate({ id: editingProduct.product_id, data: formData })
    } else {
      createProductMutation.mutate(formData)
    }
  }

  const handleDelete = (productId) => {
    if (window.confirm('Are you sure you want to delete this product?')) {
      deleteProductMutation.mutate(productId)
    }
  }

  const handleStockUpdate = (productId, currentStock) => {
    const change = prompt('Enter stock change (positive to add, negative to remove):')
    if (change !== null && !isNaN(change)) {
      const quantityChange = parseInt(change)
      const reason = prompt('Enter reason for stock adjustment:') || 'Manual adjustment'
      updateStockMutation.mutate({ productId, quantityChange, reason })
    }
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex justify-between items-center">
        <h2 className="text-2xl font-bold text-gray-900">Product Management</h2>
        <button
          onClick={() => {
            setEditingProduct(null)
            setShowModal(true)
          }}
          className="bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700 flex items-center space-x-2"
        >
          <PlusIcon className="h-5 w-5" />
          <span>Add Product</span>
        </button>
      </div>

      {/* Filters */}
      <div className="bg-white p-6 rounded-lg shadow-md">
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">Search</label>
            <div className="relative">
              <MagnifyingGlassIcon className="h-5 w-5 absolute left-3 top-3 text-gray-400" />
              <input
                type="text"
                value={filters.search}
                onChange={(e) => setFilters(prev => ({ ...prev, search: e.target.value }))}
                placeholder="Search products..."
                className="pl-10 w-full p-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              />
            </div>
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">Category</label>
            <select
              value={filters.category}
              onChange={(e) => setFilters(prev => ({ ...prev, category: e.target.value }))}
              className="w-full p-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            >
              <option value="">All Categories</option>
              {categoriesData?.categories?.map(category => (
                <option key={category.category_id} value={category.category_name}>
                  {category.category_name}
                </option>
              ))}
            </select>
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">Brand</label>
            <input
              type="text"
              value={filters.brand}
              onChange={(e) => setFilters(prev => ({ ...prev, brand: e.target.value }))}
              placeholder="Filter by brand..."
              className="w-full p-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            />
          </div>
        </div>
      </div>

      {/* Products Table */}
      <div className="bg-white rounded-lg shadow-md overflow-hidden">
        <div className="overflow-x-auto">
          <table className="min-w-full divide-y divide-gray-200">
            <thead className="bg-gray-50">
              <tr>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Product
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Category
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Price
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Stock
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Status
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Actions
                </th>
              </tr>
            </thead>
            <tbody className="bg-white divide-y divide-gray-200">
              {isLoading ? (
                <tr>
                  <td colSpan="6" className="px-6 py-4 text-center text-gray-500">
                    Loading products...
                  </td>
                </tr>
              ) : (
                productsData?.products?.map((product) => (
                  <tr key={product.product_id} className="hover:bg-gray-50">
                    <td className="px-6 py-4">
                      <div>
                        <div className="text-sm font-medium text-gray-900">
                          {product.product_name}
                        </div>
                        <div className="text-sm text-gray-500">
                          {product.brand} - {product.model}
                        </div>
                      </div>
                    </td>
                    <td className="px-6 py-4 text-sm text-gray-900">
                      {product.category_name}
                    </td>
                    <td className="px-6 py-4 text-sm text-gray-900">
                      ${product.price}
                    </td>
                    <td className="px-6 py-4">
                      <div className="flex items-center space-x-2">
                        <span className={`text-sm ${product.stock_quantity <= 10 ? 'text-red-600' : 'text-gray-900'}`}>
                          {product.stock_quantity}
                        </span>
                        <button
                          onClick={() => handleStockUpdate(product.product_id, product.stock_quantity)}
                          className="text-blue-600 hover:text-blue-800 text-xs"
                        >
                          Adjust
                        </button>
                      </div>
                    </td>
                    <td className="px-6 py-4">
                      <span className={`px-2 py-1 text-xs rounded-full ${
                        product.stock_quantity > 10 
                          ? 'bg-green-100 text-green-800'
                          : product.stock_quantity > 0
                          ? 'bg-yellow-100 text-yellow-800'
                          : 'bg-red-100 text-red-800'
                      }`}>
                        {product.stock_quantity > 10 ? 'In Stock' : product.stock_quantity > 0 ? 'Low Stock' : 'Out of Stock'}
                      </span>
                    </td>
                    <td className="px-6 py-4">
                      <div className="flex space-x-2">
                        <button
                          onClick={() => {
                            setEditingProduct(product)
                            setShowModal(true)
                          }}
                          className="text-blue-600 hover:text-blue-800"
                        >
                          <PencilIcon className="h-4 w-4" />
                        </button>
                        <button
                          onClick={() => handleDelete(product.product_id)}
                          className="text-red-600 hover:text-red-800"
                        >
                          <TrashIcon className="h-4 w-4" />
                        </button>
                      </div>
                    </td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>
      </div>

      {/* Pagination */}
      {productsData?.pagination && (
        <div className="flex justify-between items-center">
          <div className="text-sm text-gray-700">
            Showing {((productsData.pagination.page - 1) * productsData.pagination.limit) + 1} to{' '}
            {Math.min(productsData.pagination.page * productsData.pagination.limit, productsData.pagination.total)} of{' '}
            {productsData.pagination.total} results
          </div>
          <div className="flex space-x-2">
            <button
              onClick={() => setPage(p => Math.max(1, p - 1))}
              disabled={page === 1}
              className="px-3 py-1 border border-gray-300 rounded disabled:opacity-50"
            >
              Previous
            </button>
            <button
              onClick={() => setPage(p => p + 1)}
              disabled={page >= productsData.pagination.pages}
              className="px-3 py-1 border border-gray-300 rounded disabled:opacity-50"
            >
              Next
            </button>
          </div>
        </div>
      )}

      {/* Product Form Modal */}
      {showModal && (
        <ProductFormModal
          product={editingProduct}
          categories={categoriesData?.categories || []}
          suppliers={suppliersData?.suppliers || []}
          onSubmit={handleSubmit}
          onClose={() => {
            setShowModal(false)
            setEditingProduct(null)
          }}
          isLoading={createProductMutation.isLoading || updateProductMutation.isLoading}
        />
      )}
    </div>
  )
}

// Product Form Modal Component
const ProductFormModal = ({ product, categories, suppliers, onSubmit, onClose, isLoading }) => {
  const [formData, setFormData] = useState({
    product_name: product?.product_name || '',
    category_id: product?.category_id || '',
    supplier_id: product?.supplier_id || '',
    brand: product?.brand || '',
    model: product?.model || '',
    description: product?.description || '',
    price: product?.price || '',
    cost_price: product?.cost_price || '',
    stock_quantity: product?.stock_quantity || '',
    weight: product?.weight || '',
    warranty_period: product?.warranty_period || 12,
    featured: product?.featured || false
  })

  const handleSubmit = (e) => {
    e.preventDefault()
    onSubmit(formData)
  }

  const handleChange = (e) => {
    const { name, value, type, checked } = e.target
    setFormData(prev => ({
      ...prev,
      [name]: type === 'checkbox' ? checked : value
    }))
  }

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
      <div className="bg-white rounded-lg p-6 w-full max-w-2xl max-h-[90vh] overflow-y-auto">
        <div className="flex justify-between items-center mb-4">
          <h3 className="text-lg font-semibold">
            {product ? 'Edit Product' : 'Add New Product'}
          </h3>
          <button onClick={onClose} className="text-gray-400 hover:text-gray-600">
            ×
          </button>
        </div>

        <form onSubmit={handleSubmit} className="space-y-4">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Product Name *
              </label>
              <input
                type="text"
                name="product_name"
                value={formData.product_name}
                onChange={handleChange}
                required
                className="w-full p-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Category *
              </label>
              <select
                name="category_id"
                value={formData.category_id}
                onChange={handleChange}
                required
                className="w-full p-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              >
                <option value="">Select Category</option>
                {categories.map(category => (
                  <option key={category.category_id} value={category.category_id}>
                    {category.category_name}
                  </option>
                ))}
              </select>
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Supplier *
              </label>
              <select
                name="supplier_id"
                value={formData.supplier_id}
                onChange={handleChange}
                required
                className="w-full p-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              >
                <option value="">Select Supplier</option>
                {suppliers.map(supplier => (
                  <option key={supplier.supplier_id} value={supplier.supplier_id}>
                    {supplier.company_name}
                  </option>
                ))}
              </select>
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Brand
              </label>
              <input
                type="text"
                name="brand"
                value={formData.brand}
                onChange={handleChange}
                className="w-full p-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Model
              </label>
              <input
                type="text"
                name="model"
                value={formData.model}
                onChange={handleChange}
                className="w-full p-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Price *
              </label>
              <input
                type="number"
                step="0.01"
                name="price"
                value={formData.price}
                onChange={handleChange}
                required
                className="w-full p-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Cost Price
              </label>
              <input
                type="number"
                step="0.01"
                name="cost_price"
                value={formData.cost_price}
                onChange={handleChange}
                className="w-full p-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Stock Quantity *
              </label>
              <input
                type="number"
                name="stock_quantity"
                value={formData.stock_quantity}
                onChange={handleChange}
                required
                className="w-full p-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Weight (kg)
              </label>
              <input
                type="number"
                step="0.01"
                name="weight"
                value={formData.weight}
                onChange={handleChange}
                className="w-full p-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Warranty (months)
              </label>
              <input
                type="number"
                name="warranty_period"
                value={formData.warranty_period}
                onChange={handleChange}
                className="w-full p-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              />
            </div>
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Description
            </label>
            <textarea
              name="description"
              value={formData.description}
              onChange={handleChange}
              rows={3}
              className="w-full p-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            />
          </div>

          <div className="flex items-center">
            <input
              type="checkbox"
              name="featured"
              checked={formData.featured}
              onChange={handleChange}
              className="mr-2"
            />
            <label className="text-sm font-medium text-gray-700">
              Featured Product
            </label>
          </div>

          <div className="flex justify-end space-x-3 pt-4">
            <button
              type="button"
              onClick={onClose}
              className="px-4 py-2 text-gray-700 border border-gray-300 rounded-lg hover:bg-gray-50"
            >
              Cancel
            </button>
            <button
              type="submit"
              disabled={isLoading}
              className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50"
            >
              {isLoading ? 'Saving...' : product ? 'Update Product' : 'Create Product'}
            </button>
          </div>
        </form>
      </div>
    </div>
  )
}

export default ProductManagement