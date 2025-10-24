import React, { useState } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { 
  EyeIcon, 
  PencilIcon, 
  CheckCircleIcon, 
  ClockIcon, 
  TruckIcon,
  ExclamationTriangleIcon,
  XMarkIcon 
} from '@heroicons/react/24/outline'

const OrderManagement = () => {
  const [selectedStatus, setSelectedStatus] = useState('')
  const [searchTerm, setSearchTerm] = useState('')
  const [currentPage, setCurrentPage] = useState(1)
  const [selectedOrder, setSelectedOrder] = useState(null)
  const [showStatusModal, setShowStatusModal] = useState(false)
  const [showDetailsModal, setShowDetailsModal] = useState(false)
  const queryClient = useQueryClient()

  // Fetch orders
  const { data: ordersData, isLoading } = useQuery({
    queryKey: ['adminOrders', currentPage, selectedStatus, searchTerm],
    queryFn: async () => {
      const params = new URLSearchParams({
        page: currentPage.toString(),
        limit: '10'
      })
      
      if (selectedStatus) params.append('status', selectedStatus)
      if (searchTerm) params.append('search', searchTerm)
      
      const response = await fetch(`http://localhost:5000/api/orders/admin?${params}`)
      if (!response.ok) throw new Error('Failed to fetch orders')
      return response.json()
    }
  })

  // Update order status mutation
  const updateStatusMutation = useMutation({
    mutationFn: async ({ orderId, status }) => {
      const response = await fetch(`http://localhost:5000/api/orders/admin/${orderId}/status`, {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ status })
      })
      if (!response.ok) throw new Error('Failed to update order status')
      return response.json()
    },
    onSuccess: () => {
      queryClient.invalidateQueries(['adminOrders'])
      queryClient.invalidateQueries(['orderAnalytics'])
      queryClient.invalidateQueries(['productAnalytics'])
      setShowStatusModal(false)
      setSelectedOrder(null)
    }
  })

  // Fetch order details
  const { data: orderDetails } = useQuery({
    queryKey: ['orderDetails', selectedOrder?.order_id],
    queryFn: async () => {
      const response = await fetch(`http://localhost:5000/api/orders/admin/${selectedOrder.order_id}`)
      if (!response.ok) throw new Error('Failed to fetch order details')
      return response.json()
    },
    enabled: !!selectedOrder && showDetailsModal
  })

  const getStatusBadge = (status) => {
    const statusConfig = {
      'PENDING': { color: 'bg-yellow-100 text-yellow-800', icon: ClockIcon },
      'PROCESSING': { color: 'bg-blue-100 text-blue-800', icon: ClockIcon },
      'SHIPPED': { color: 'bg-purple-100 text-purple-800', icon: TruckIcon },
      'DELIVERED': { color: 'bg-green-100 text-green-800', icon: CheckCircleIcon },
      'CANCELLED': { color: 'bg-red-100 text-red-800', icon: ExclamationTriangleIcon }
    }

    const config = statusConfig[status] || statusConfig['PENDING']
    const Icon = config.icon

    return (
      <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${config.color}`}>
        <Icon className="w-3 h-3 mr-1" />
        {status}
      </span>
    )
  }

  const handleStatusUpdate = (status) => {
    updateStatusMutation.mutate({ 
      orderId: selectedOrder.order_id, 
      status 
    })
  }

  const orders = ordersData?.orders || []
  const pagination = ordersData?.pagination

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex justify-between items-center">
        <h2 className="text-2xl font-bold text-gray-900">Order Management</h2>
      </div>

      {/* Filters */}
      <div className="bg-white p-6 rounded-lg shadow-md">
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Search</label>
            <input
              type="text"
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              placeholder="Search by order number, customer name, or email..."
              className="w-full p-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Status</label>
            <select
              value={selectedStatus}
              onChange={(e) => setSelectedStatus(e.target.value)}
              className="w-full p-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            >
              <option value="">All Statuses</option>
              <option value="PENDING">Pending</option>
              <option value="PROCESSING">Processing</option>
              <option value="SHIPPED">Shipped</option>
              <option value="DELIVERED">Delivered</option>
              <option value="CANCELLED">Cancelled</option>
            </select>
          </div>

          <div className="flex items-end">
            <button
              onClick={() => {
                setSearchTerm('')
                setSelectedStatus('')
                setCurrentPage(1)
              }}
              className="px-4 py-2 bg-gray-500 text-white rounded-lg hover:bg-gray-600"
            >
              Clear Filters
            </button>
          </div>
        </div>
      </div>

      {/* Orders Table */}
      <div className="bg-white rounded-lg shadow-md overflow-hidden">
        {isLoading ? (
          <div className="p-8 text-center">Loading orders...</div>
        ) : orders.length === 0 ? (
          <div className="p-8 text-center text-gray-500">No orders found</div>
        ) : (
          <>
            <div className="overflow-x-auto">
              <table className="min-w-full divide-y divide-gray-200">
                <thead className="bg-gray-50">
                  <tr>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Order</th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Customer</th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Date</th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Status</th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Total</th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Items</th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Actions</th>
                  </tr>
                </thead>
                <tbody className="bg-white divide-y divide-gray-200">
                  {orders.map((order) => (
                    <tr key={order.order_id} className="hover:bg-gray-50">
                      <td className="px-6 py-4 whitespace-nowrap">
                        <div>
                          <div className="text-sm font-medium text-gray-900">{order.order_number}</div>
                          <div className="text-sm text-gray-500">{order.payment_method}</div>
                        </div>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap">
                        <div>
                          <div className="text-sm font-medium text-gray-900">{order.customer_name}</div>
                          <div className="text-sm text-gray-500">{order.customer_email}</div>
                        </div>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                        {new Date(order.order_date).toLocaleDateString()}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap">
                        {getStatusBadge(order.order_status)}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">
                        ${parseFloat(order.total_amount).toFixed(2)}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                        {order.item_count} items
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm font-medium space-x-2">
                        <button
                          onClick={() => {
                            setSelectedOrder(order)
                            setShowDetailsModal(true)
                          }}
                          className="text-blue-600 hover:text-blue-900"
                          title="View Details"
                        >
                          <EyeIcon className="h-5 w-5" />
                        </button>
                        <button
                          onClick={() => {
                            setSelectedOrder(order)
                            setShowStatusModal(true)
                          }}
                          className="text-green-600 hover:text-green-900"
                          title="Update Status"
                        >
                          <PencilIcon className="h-5 w-5" />
                        </button>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>

            {/* Pagination */}
            {pagination && pagination.pages > 1 && (
              <div className="bg-white px-4 py-3 border-t border-gray-200 sm:px-6">
                <div className="flex items-center justify-between">
                  <div className="text-sm text-gray-700">
                    Showing {((pagination.page - 1) * pagination.limit) + 1} to{' '}
                    {Math.min(pagination.page * pagination.limit, pagination.total)} of{' '}
                    {pagination.total} results
                  </div>
                  <div className="flex space-x-2">
                    <button
                      onClick={() => setCurrentPage(currentPage - 1)}
                      disabled={currentPage === 1}
                      className="px-3 py-1 text-sm bg-gray-300 text-gray-700 rounded disabled:opacity-50"
                    >
                      Previous
                    </button>
                    <span className="px-3 py-1 text-sm bg-blue-600 text-white rounded">
                      {currentPage}
                    </span>
                    <button
                      onClick={() => setCurrentPage(currentPage + 1)}
                      disabled={currentPage === pagination.pages}
                      className="px-3 py-1 text-sm bg-gray-300 text-gray-700 rounded disabled:opacity-50"
                    >
                      Next
                    </button>
                  </div>
                </div>
              </div>
            )}
          </>
        )}
      </div>

      {/* Status Update Modal */}
      {showStatusModal && selectedOrder && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white rounded-lg p-6 w-full max-w-md">
            <div className="flex justify-between items-center mb-4">
              <h3 className="text-lg font-semibold">Update Order Status</h3>
              <button 
                onClick={() => setShowStatusModal(false)}
                className="text-gray-400 hover:text-gray-600"
              >
                <XMarkIcon className="h-6 w-6" />
              </button>
            </div>

            <div className="space-y-4">
              <div>
                <p className="text-sm text-gray-600 mb-2">
                  Order: {selectedOrder.order_number}
                </p>
                <p className="text-sm text-gray-600 mb-4">
                  Current Status: {getStatusBadge(selectedOrder.order_status)}
                </p>
              </div>

              <div className="grid grid-cols-2 gap-2">
                {['PROCESSING', 'SHIPPED', 'DELIVERED', 'CANCELLED'].map((status) => (
                  <button
                    key={status}
                    onClick={() => handleStatusUpdate(status)}
                    disabled={updateStatusMutation.isLoading}
                    className={`p-3 rounded-lg border-2 transition-colors ${
                      selectedOrder.order_status === status
                        ? 'border-blue-500 bg-blue-50'
                        : 'border-gray-200 hover:border-blue-300'
                    }`}
                  >
                    {getStatusBadge(status)}
                  </button>
                ))}
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Order Details Modal */}
      {showDetailsModal && selectedOrder && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white rounded-lg p-6 w-full max-w-4xl max-h-[90vh] overflow-y-auto">
            <div className="flex justify-between items-center mb-4">
              <h3 className="text-lg font-semibold">Order Details</h3>
              <button 
                onClick={() => setShowDetailsModal(false)}
                className="text-gray-400 hover:text-gray-600"
              >
                <XMarkIcon className="h-6 w-6" />
              </button>
            </div>

            {orderDetails && (
              <div className="space-y-6">
                {/* Order Info */}
                <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                  <div>
                    <h4 className="font-medium text-gray-900 mb-2">Order Information</h4>
                    <div className="space-y-1 text-sm">
                      <p><span className="font-medium">Order Number:</span> {orderDetails.order.order_number}</p>
                      <p><span className="font-medium">Date:</span> {new Date(orderDetails.order.order_date).toLocaleString()}</p>
                      <p><span className="font-medium">Status:</span> {getStatusBadge(orderDetails.order.order_status)}</p>
                      <p><span className="font-medium">Payment Method:</span> {orderDetails.order.payment_method}</p>
                    </div>
                  </div>

                  <div>
                    <h4 className="font-medium text-gray-900 mb-2">Customer Information</h4>
                    <div className="space-y-1 text-sm">
                      <p><span className="font-medium">Name:</span> {orderDetails.order.customer_name}</p>
                      <p><span className="font-medium">Email:</span> {orderDetails.order.customer_email}</p>
                      <p><span className="font-medium">Phone:</span> {orderDetails.order.customer_phone || 'N/A'}</p>
                    </div>
                  </div>
                </div>

                {/* Addresses */}
                <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                  <div>
                    <h4 className="font-medium text-gray-900 mb-2">Shipping Address</h4>
                    <p className="text-sm text-gray-600">{orderDetails.order.shipping_address}</p>
                  </div>
                  <div>
                    <h4 className="font-medium text-gray-900 mb-2">Billing Address</h4>
                    <p className="text-sm text-gray-600">{orderDetails.order.billing_address}</p>
                  </div>
                </div>

                {/* Order Items */}
                <div>
                  <h4 className="font-medium text-gray-900 mb-2">Order Items</h4>
                  <div className="border rounded-lg overflow-hidden">
                    <table className="min-w-full divide-y divide-gray-200">
                      <thead className="bg-gray-50">
                        <tr>
                          <th className="px-4 py-2 text-left text-xs font-medium text-gray-500 uppercase">Product</th>
                          <th className="px-4 py-2 text-left text-xs font-medium text-gray-500 uppercase">Quantity</th>
                          <th className="px-4 py-2 text-left text-xs font-medium text-gray-500 uppercase">Unit Price</th>
                          <th className="px-4 py-2 text-left text-xs font-medium text-gray-500 uppercase">Total</th>
                        </tr>
                      </thead>
                      <tbody className="divide-y divide-gray-200">
                        {orderDetails.items.map((item) => (
                          <tr key={item.order_item_id}>
                            <td className="px-4 py-2">
                              <div>
                                <div className="font-medium text-gray-900">{item.product_name}</div>
                                <div className="text-sm text-gray-500">{item.brand} - {item.model}</div>
                              </div>
                            </td>
                            <td className="px-4 py-2 text-sm text-gray-900">{item.quantity}</td>
                            <td className="px-4 py-2 text-sm text-gray-900">${parseFloat(item.unit_price).toFixed(2)}</td>
                            <td className="px-4 py-2 text-sm text-gray-900">${parseFloat(item.total_price).toFixed(2)}</td>
                          </tr>
                        ))}
                      </tbody>
                    </table>
                  </div>
                </div>

                {/* Order Summary */}
                <div className="border-t pt-4">
                  <div className="flex justify-end">
                    <div className="w-64 space-y-2 text-sm">
                      <div className="flex justify-between">
                        <span>Subtotal:</span>
                        <span>${parseFloat(orderDetails.order.subtotal).toFixed(2)}</span>
                      </div>
                      <div className="flex justify-between">
                        <span>Tax:</span>
                        <span>${parseFloat(orderDetails.order.tax_amount).toFixed(2)}</span>
                      </div>
                      <div className="flex justify-between font-medium text-lg border-t pt-2">
                        <span>Total:</span>
                        <span>${parseFloat(orderDetails.order.total_amount).toFixed(2)}</span>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            )}
          </div>
        </div>
      )}
    </div>
  )
}

export default OrderManagement