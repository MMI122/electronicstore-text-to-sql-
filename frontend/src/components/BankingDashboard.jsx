import React, { useState } from 'react'
import { useQuery } from '@tanstack/react-query'
import {
  CreditCardIcon,
  BanknotesIcon,
  ArrowTrendingUpIcon,
  ArrowTrendingDownIcon,
  MagnifyingGlassIcon
} from '@heroicons/react/24/outline'
import axios from 'axios'

const API_BASE_URL = 'http://localhost:5000/api'

const BankingDashboard = () => {
  const [selectedCustomer, setSelectedCustomer] = useState('')
  const [selectedAccount, setSelectedAccount] = useState('')

  // Fetch customers for dropdown
  const { data: customersData } = useQuery({
    queryKey: ['customers'],
    queryFn: async () => {
      // This would need to be implemented in the backend
      const response = await axios.get(`${API_BASE_URL}/orders/analytics?days=365`)
      return response.data.top_customers || []
    }
  })

  // Fetch accounts for selected customer
  const { data: accountsData } = useQuery({
    queryKey: ['accounts', selectedCustomer],
    queryFn: async () => {
      if (!selectedCustomer) return { accounts: [] }
      const response = await axios.get(`${API_BASE_URL}/orders/banking/accounts/${selectedCustomer}`)
      return response.data
    },
    enabled: !!selectedCustomer
  })

  // Fetch transactions for selected account
  const { data: transactionsData } = useQuery({
    queryKey: ['transactions', selectedAccount],
    queryFn: async () => {
      if (!selectedAccount) return { transactions: [], pagination: {} }
      const response = await axios.get(`${API_BASE_URL}/orders/banking/transactions/${selectedAccount}`)
      return response.data
    },
    enabled: !!selectedAccount
  })

  const getTransactionIcon = (type) => {
    const isCredit = ['CREDIT', 'DEPOSIT'].includes(type)
    return isCredit ? (
      <ArrowTrendingUpIcon className="h-5 w-5 text-green-500" />
    ) : (
      <ArrowTrendingDownIcon className="h-5 w-5 text-red-500" />
    )
  }

  const getTransactionColor = (type) => {
    const isCredit = ['CREDIT', 'DEPOSIT'].includes(type)
    return isCredit ? 'text-green-600' : 'text-red-600'
  }

  const formatCurrency = (amount) => {
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: 'USD'
    }).format(amount)
  }

  const getAccountTypeColor = (type) => {
    const colors = {
      'CHECKING': 'bg-blue-100 text-blue-800',
      'SAVINGS': 'bg-green-100 text-green-800',
      'CREDIT': 'bg-purple-100 text-purple-800'
    }
    return colors[type] || 'bg-gray-100 text-gray-800'
  }

  return (
    <div className="space-y-8">
      {/* Header */}
      <div className="text-center">
        <CreditCardIcon className="h-12 w-12 text-blue-600 mx-auto mb-4" />
        <h2 className="text-2xl font-bold text-gray-900 mb-2">
          Banking Dashboard
        </h2>
        <p className="text-gray-600">
          Manage customer accounts and view transaction history
        </p>
      </div>

      {/* Customer and Account Selection */}
      <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Select Customer
            </label>
            <select
              value={selectedCustomer}
              onChange={(e) => {
                setSelectedCustomer(e.target.value)
                setSelectedAccount('')
              }}
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            >
              <option value="">Choose a customer...</option>
              {customersData?.map((customer) => (
                <option key={customer.customer_id} value={customer.customer_id}>
                  {customer.customer_name} - {customer.email}
                </option>
              ))}
            </select>
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Select Account
            </label>
            <select
              value={selectedAccount}
              onChange={(e) => setSelectedAccount(e.target.value)}
              disabled={!selectedCustomer}
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-transparent disabled:bg-gray-50 disabled:cursor-not-allowed"
            >
              <option value="">Choose an account...</option>
              {accountsData?.accounts?.map((account) => (
                <option key={account.account_id} value={account.account_id}>
                  {account.account_number} ({account.account_type})
                </option>
              ))}
            </select>
          </div>
        </div>
      </div>

      {/* Account Information */}
      {selectedCustomer && accountsData?.accounts && accountsData.accounts.length > 0 && (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {accountsData.accounts.map((account) => (
            <div
              key={account.account_id}
              className={`bg-white rounded-lg shadow-md border-2 p-6 cursor-pointer transition-all duration-200 ${
                selectedAccount == account.account_id
                  ? 'border-blue-500 shadow-lg'
                  : 'border-gray-200 hover:border-gray-300'
              }`}
              onClick={() => setSelectedAccount(account.account_id.toString())}
            >
              <div className="flex items-center justify-between mb-4">
                <div className="flex items-center">
                  <CreditCardIcon className="h-6 w-6 text-gray-600 mr-2" />
                  <span className="font-medium text-gray-900">
                    {account.account_number}
                  </span>
                </div>
                <span className={`px-2 py-1 rounded-full text-xs font-medium ${getAccountTypeColor(account.account_type)}`}>
                  {account.account_type}
                </span>
              </div>

              <div className="space-y-2">
                <div className="flex justify-between">
                  <span className="text-sm text-gray-600">Balance:</span>
                  <span className={`text-sm font-semibold ${account.balance >= 0 ? 'text-green-600' : 'text-red-600'}`}>
                    {formatCurrency(account.balance)}
                  </span>
                </div>

                {account.credit_limit && (
                  <div className="flex justify-between">
                    <span className="text-sm text-gray-600">Credit Limit:</span>
                    <span className="text-sm text-gray-900">
                      {formatCurrency(account.credit_limit)}
                    </span>
                  </div>
                )}

                {account.interest_rate && (
                  <div className="flex justify-between">
                    <span className="text-sm text-gray-600">Interest Rate:</span>
                    <span className="text-sm text-gray-900">
                      {(account.interest_rate * 100).toFixed(2)}% APR
                    </span>
                  </div>
                )}

                <div className="flex justify-between">
                  <span className="text-sm text-gray-600">Status:</span>
                  <span className={`text-sm font-medium ${
                    account.account_status === 'ACTIVE' ? 'text-green-600' : 'text-red-600'
                  }`}>
                    {account.account_status}
                  </span>
                </div>
              </div>

              <div className="mt-4 pt-3 border-t border-gray-200">
                <p className="text-xs text-gray-500">
                  Customer: {account.customer_name}
                </p>
                <p className="text-xs text-gray-500">
                  Opened: {new Date(account.opened_date).toLocaleDateString()}
                </p>
              </div>
            </div>
          ))}
        </div>
      )}

      {/* Transaction History */}
      {selectedAccount && transactionsData?.transactions && (
        <div className="bg-white rounded-lg shadow-sm border border-gray-200">
          <div className="p-6 border-b border-gray-200">
            <div className="flex items-center justify-between">
              <h3 className="text-lg font-semibold text-gray-900">
                Transaction History
              </h3>
              <div className="flex items-center text-sm text-gray-500">
                <BanknotesIcon className="h-4 w-4 mr-1" />
                {transactionsData.transactions.length} transactions
              </div>
            </div>
          </div>

          {transactionsData.transactions.length > 0 ? (
            <div className="overflow-x-auto">
              <table className="min-w-full divide-y divide-gray-200">
                <thead className="bg-gray-50">
                  <tr>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Date
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Type
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Description
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Amount
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Balance
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Status
                    </th>
                  </tr>
                </thead>
                <tbody className="bg-white divide-y divide-gray-200">
                  {transactionsData.transactions.map((transaction, index) => (
                    <tr key={transaction.transaction_id} className="hover:bg-gray-50">
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                        {new Date(transaction.transaction_date).toLocaleString()}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap">
                        <div className="flex items-center">
                          {getTransactionIcon(transaction.transaction_type)}
                          <span className="ml-2 text-sm text-gray-900">
                            {transaction.transaction_type}
                          </span>
                        </div>
                      </td>
                      <td className="px-6 py-4 text-sm text-gray-900 max-w-xs truncate">
                        {transaction.description}
                        {transaction.order_number && (
                          <div className="text-xs text-blue-600">
                            Order: {transaction.order_number}
                          </div>
                        )}
                      </td>
                      <td className={`px-6 py-4 whitespace-nowrap text-sm font-medium ${getTransactionColor(transaction.transaction_type)}`}>
                        {['CREDIT', 'DEPOSIT'].includes(transaction.transaction_type) ? '+' : '-'}
                        {formatCurrency(Math.abs(transaction.amount))}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                        {formatCurrency(transaction.balance_after)}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap">
                        <span className={`inline-flex px-2 py-1 text-xs font-medium rounded-full ${
                          transaction.status === 'COMPLETED' 
                            ? 'bg-green-100 text-green-800'
                            : transaction.status === 'PENDING'
                            ? 'bg-yellow-100 text-yellow-800'
                            : transaction.status === 'FAILED'
                            ? 'bg-red-100 text-red-800'
                            : 'bg-gray-100 text-gray-800'
                        }`}>
                          {transaction.status}
                        </span>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          ) : (
            <div className="p-8 text-center">
              <MagnifyingGlassIcon className="h-12 w-12 text-gray-400 mx-auto mb-4" />
              <p className="text-gray-500">No transactions found for this account</p>
            </div>
          )}

          {/* Pagination for transactions */}
          {transactionsData?.pagination && transactionsData.pagination.pages > 1 && (
            <div className="p-6 border-t border-gray-200">
              <div className="flex items-center justify-between">
                <p className="text-sm text-gray-700">
                  Showing page {transactionsData.pagination.page} of {transactionsData.pagination.pages}
                </p>
                <div className="flex space-x-2">
                  <button
                    disabled={transactionsData.pagination.page === 1}
                    className="px-3 py-1 text-sm border border-gray-300 rounded-md hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed"
                  >
                    Previous
                  </button>
                  <button
                    disabled={transactionsData.pagination.page === transactionsData.pagination.pages}
                    className="px-3 py-1 text-sm border border-gray-300 rounded-md hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed"
                  >
                    Next
                  </button>
                </div>
              </div>
            </div>
          )}
        </div>
      )}

      {/* Empty State */}
      {!selectedCustomer && (
        <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-12 text-center">
          <CreditCardIcon className="h-16 w-16 text-gray-300 mx-auto mb-4" />
          <h3 className="text-lg font-medium text-gray-900 mb-2">
            Select a Customer
          </h3>
          <p className="text-gray-600 max-w-md mx-auto">
            Choose a customer from the dropdown above to view their banking accounts and transaction history.
          </p>
        </div>
      )}

      {selectedCustomer && (!accountsData?.accounts || accountsData.accounts.length === 0) && (
        <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-12 text-center">
          <BanknotesIcon className="h-16 w-16 text-gray-300 mx-auto mb-4" />
          <h3 className="text-lg font-medium text-gray-900 mb-2">
            No Banking Accounts
          </h3>
          <p className="text-gray-600 max-w-md mx-auto">
            This customer doesn't have any banking accounts set up yet.
          </p>
        </div>
      )}
    </div>
  )
}

export default BankingDashboard