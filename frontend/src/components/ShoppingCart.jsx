import React, { useState } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { 
  ShoppingCartIcon,
  TrashIcon,
  PlusIcon,
  MinusIcon,
  CreditCardIcon,
  MapPinIcon
} from '@heroicons/react/24/outline'
import axios from 'axios'

const API_BASE_URL = 'http://localhost:5000/api'

const ShoppingCart = ({ customerId, onClose }) => {
  const [showCheckout, setShowCheckout] = useState(false)
  const queryClient = useQueryClient()

  // Fetch cart items
  const { data: cartData, isLoading } = useQuery({
    queryKey: ['cart', customerId],
    queryFn: async () => {
      const response = await axios.get(`${API_BASE_URL}/cart/${customerId}`)
      return response.data
    },
    enabled: !!customerId
  })

  // Update cart item quantity
  const updateQuantityMutation = useMutation({
    mutationFn: async ({ cartId, quantity }) => {
      const response = await axios.put(`${API_BASE_URL}/cart/update/${cartId}`, { quantity })
      return response.data
    },
    onSuccess: () => {
      queryClient.invalidateQueries(['cart', customerId])
    }
  })

  // Remove item from cart
  const removeItemMutation = useMutation({
    mutationFn: async (cartId) => {
      const response = await axios.delete(`${API_BASE_URL}/cart/remove/${cartId}`)
      return response.data
    },
    onSuccess: () => {
      queryClient.invalidateQueries(['cart', customerId])
    }
  })

  // Clear entire cart
  const clearCartMutation = useMutation({
    mutationFn: async () => {
      const response = await axios.delete(`${API_BASE_URL}/cart/clear/${customerId}`)
      return response.data
    },
    onSuccess: () => {
      queryClient.invalidateQueries(['cart', customerId])
    }
  })

  // Checkout mutation
  const checkoutMutation = useMutation({
    mutationFn: async (checkoutData) => {
      const response = await axios.post(`${API_BASE_URL}/cart/checkout`, checkoutData)
      return response.data
    },
    onSuccess: (data) => {
      queryClient.invalidateQueries(['cart', customerId])
      alert(`Order placed successfully! Order number: ${data.order_number}`)
      setShowCheckout(false)
      onClose?.()
    }
  })

  const handleUpdateQuantity = (cartId, currentQuantity, change) => {
    const newQuantity = currentQuantity + change
    if (newQuantity > 0) {
      updateQuantityMutation.mutate({ cartId, quantity: newQuantity })
    }
  }

  const handleRemoveItem = (cartId) => {
    if (window.confirm('Remove this item from cart?')) {
      removeItemMutation.mutate(cartId)
    }
  }

  const handleClearCart = () => {
    if (window.confirm('Clear entire cart?')) {
      clearCartMutation.mutate()
    }
  }

  if (isLoading) {
    return (
      <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
        <div className="bg-white rounded-lg p-6">
          <div className="text-center">Loading cart...</div>
        </div>
      </div>
    )
  }

  const cartItems = cartData?.cart_items || []
  const summary = cartData?.summary || {}

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
      <div className="bg-white rounded-lg w-full max-w-4xl max-h-[90vh] overflow-hidden">
        {/* Header */}
        <div className="bg-gray-50 px-6 py-4 border-b flex justify-between items-center">
          <div className="flex items-center space-x-2">
            <ShoppingCartIcon className="h-6 w-6 text-gray-700" />
            <h2 className="text-xl font-semibold text-gray-900">Shopping Cart</h2>
            <span className="bg-blue-100 text-blue-800 px-2 py-1 rounded-full text-sm">
              {summary.item_count || 0} items
            </span>
          </div>
          <div className="flex space-x-2">
            {cartItems.length > 0 && (
              <button
                onClick={handleClearCart}
                className="text-red-600 hover:text-red-800 text-sm"
              >
                Clear Cart
              </button>
            )}
            <button
              onClick={onClose}
              className="text-gray-400 hover:text-gray-600 text-2xl"
            >
              ×
            </button>
          </div>
        </div>

        <div className="flex flex-col md:flex-row">
          {/* Cart Items */}
          <div className="flex-1 p-6 max-h-96 overflow-y-auto">
            {cartItems.length === 0 ? (
              <div className="text-center py-12">
                <ShoppingCartIcon className="h-16 w-16 text-gray-400 mx-auto mb-4" />
                <h3 className="text-lg font-medium text-gray-900 mb-2">Your cart is empty</h3>
                <p className="text-gray-500">Add some products to get started!</p>
              </div>
            ) : (
              <div className="space-y-4">
                {cartItems.map((item) => (
                  <div key={item.cart_id} className="flex items-center space-x-4 p-4 border rounded-lg">
                    <div className="flex-1">
                      <h4 className="font-medium text-gray-900">{item.product_name}</h4>
                      <p className="text-sm text-gray-500">{item.brand}</p>
                      <p className="text-sm text-gray-500">{item.category_name}</p>
                      <p className="text-lg font-semibold text-blue-600">${item.price}</p>
                    </div>

                    {/* Quantity Controls */}
                    <div className="flex items-center space-x-2">
                      <button
                        onClick={() => handleUpdateQuantity(item.cart_id, item.quantity, -1)}
                        className="p-1 rounded-full bg-gray-100 hover:bg-gray-200"
                        disabled={updateQuantityMutation.isLoading}
                      >
                        <MinusIcon className="h-4 w-4" />
                      </button>
                      <span className="w-8 text-center font-medium">{item.quantity}</span>
                      <button
                        onClick={() => handleUpdateQuantity(item.cart_id, item.quantity, 1)}
                        className="p-1 rounded-full bg-gray-100 hover:bg-gray-200"
                        disabled={updateQuantityMutation.isLoading || item.quantity >= item.stock_quantity}
                      >
                        <PlusIcon className="h-4 w-4" />
                      </button>
                    </div>

                    {/* Item Total */}
                    <div className="text-right">
                      <p className="font-semibold">${item.total_price}</p>
                      <p className="text-xs text-gray-500">
                        {item.stock_quantity} in stock
                      </p>
                    </div>

                    {/* Remove Button */}
                    <button
                      onClick={() => handleRemoveItem(item.cart_id)}
                      className="text-red-600 hover:text-red-800 p-1"
                      disabled={removeItemMutation.isLoading}
                    >
                      <TrashIcon className="h-5 w-5" />
                    </button>
                  </div>
                ))}
              </div>
            )}
          </div>

          {/* Order Summary */}
          {cartItems.length > 0 && (
            <div className="w-full md:w-80 bg-gray-50 p-6 border-l">
              <h3 className="text-lg font-semibold text-gray-900 mb-4">Order Summary</h3>
              
              <div className="space-y-2 mb-4">
                <div className="flex justify-between">
                  <span>Subtotal:</span>
                  <span>${summary.subtotal}</span>
                </div>
                <div className="flex justify-between">
                  <span>Tax:</span>
                  <span>${summary.tax_amount}</span>
                </div>
                <div className="border-t pt-2">
                  <div className="flex justify-between font-semibold text-lg">
                    <span>Total:</span>
                    <span>${summary.total_amount}</span>
                  </div>
                </div>
              </div>

              <button
                onClick={() => setShowCheckout(true)}
                className="w-full bg-blue-600 text-white py-3 rounded-lg hover:bg-blue-700 flex items-center justify-center space-x-2"
              >
                <CreditCardIcon className="h-5 w-5" />
                <span>Proceed to Checkout</span>
              </button>
            </div>
          )}
        </div>

        {/* Checkout Modal */}
        {showCheckout && (
          <CheckoutModal
            customerId={customerId}
            summary={summary}
            onSubmit={(checkoutData) => checkoutMutation.mutate(checkoutData)}
            onClose={() => setShowCheckout(false)}
            isLoading={checkoutMutation.isLoading}
          />
        )}
      </div>
    </div>
  )
}

// Checkout Modal Component
const CheckoutModal = ({ customerId, summary, onSubmit, onClose, isLoading }) => {
  const [formData, setFormData] = useState({
    payment_method: 'CREDIT_CARD',
    shipping_address: '',
    billing_address: '',
    store_id: 1
  })

  const handleSubmit = (e) => {
    e.preventDefault()
    onSubmit({
      customer_id: customerId,
      ...formData
    })
  }

  const handleChange = (e) => {
    const { name, value } = e.target
    setFormData(prev => ({
      ...prev,
      [name]: value
    }))
  }

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
      <div className="bg-white rounded-lg p-6 w-full max-w-md">
        <div className="flex justify-between items-center mb-4">
          <h3 className="text-lg font-semibold">Checkout</h3>
          <button onClick={onClose} className="text-gray-400 hover:text-gray-600">
            ×
          </button>
        </div>

        <form onSubmit={handleSubmit} className="space-y-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Payment Method *
            </label>
            <select
              name="payment_method"
              value={formData.payment_method}
              onChange={handleChange}
              required
              className="w-full p-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            >
              <option value="CREDIT_CARD">Credit Card</option>
              <option value="DEBIT_CARD">Debit Card</option>
              <option value="BANK_ACCOUNT">Bank Account</option>
              <option value="PAYPAL">PayPal</option>
            </select>
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Shipping Address *
            </label>
            <textarea
              name="shipping_address"
              value={formData.shipping_address}
              onChange={handleChange}
              required
              rows={3}
              placeholder="Enter your complete shipping address..."
              className="w-full p-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Billing Address
            </label>
            <textarea
              name="billing_address"
              value={formData.billing_address}
              onChange={handleChange}
              rows={3}
              placeholder="Same as shipping address if left empty..."
              className="w-full p-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            />
          </div>

          {/* Order Summary */}
          <div className="bg-gray-50 p-4 rounded-lg">
            <h4 className="font-medium mb-2">Order Summary</h4>
            <div className="space-y-1 text-sm">
              <div className="flex justify-between">
                <span>Subtotal:</span>
                <span>${summary.subtotal}</span>
              </div>
              <div className="flex justify-between">
                <span>Tax:</span>
                <span>${summary.tax_amount}</span>
              </div>
              <div className="border-t pt-1">
                <div className="flex justify-between font-semibold">
                  <span>Total:</span>
                  <span>${summary.total_amount}</span>
                </div>
              </div>
            </div>
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
              {isLoading ? 'Processing...' : 'Place Order'}
            </button>
          </div>
        </form>
      </div>
    </div>
  )
}

export default ShoppingCart