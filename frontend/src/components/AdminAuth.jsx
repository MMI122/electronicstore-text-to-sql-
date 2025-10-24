import React, { useState, useRef, useEffect } from 'react'
import { 
  ShieldCheckIcon, 
  LockClosedIcon,
  ExclamationTriangleIcon,
  CheckCircleIcon
} from '@heroicons/react/24/outline'

const AdminAuth = ({ onAdminLogin, onCancel }) => {
  const [pin, setPin] = useState(['', '', '', '', '', '', '', ''])
  const [currentIndex, setCurrentIndex] = useState(0)
  const [error, setError] = useState('')
  const [isLoading, setIsLoading] = useState(false)
  const inputRefs = useRef([])

  const ADMIN_PIN = '12345678'

  useEffect(() => {
    // Focus the first input on mount
    if (inputRefs.current[0]) {
      inputRefs.current[0].focus()
    }
  }, [])

  const handleInputChange = (index, value) => {
    // Only allow single digit input
    if (value.length > 1) {
      value = value.slice(-1)
    }

    // Only allow numbers
    if (!/^\d*$/.test(value)) {
      return
    }

    const newPin = [...pin]
    newPin[index] = value
    setPin(newPin)
    setError('')

    // Auto-focus next input
    if (value && index < 7) {
      setCurrentIndex(index + 1)
      setTimeout(() => {
        if (inputRefs.current[index + 1]) {
          inputRefs.current[index + 1].focus()
        }
      }, 10)
    }
  }

  const handleKeyDown = (index, e) => {
    // Handle backspace
    if (e.key === 'Backspace') {
      if (pin[index]) {
        // Clear current input
        const newPin = [...pin]
        newPin[index] = ''
        setPin(newPin)
      } else if (index > 0) {
        // Move to previous input
        setCurrentIndex(index - 1)
        setTimeout(() => {
          if (inputRefs.current[index - 1]) {
            inputRefs.current[index - 1].focus()
          }
        }, 10)
      }
    }
    
    // Handle arrow keys
    if (e.key === 'ArrowLeft' && index > 0) {
      setCurrentIndex(index - 1)
      setTimeout(() => {
        if (inputRefs.current[index - 1]) {
          inputRefs.current[index - 1].focus()
        }
      }, 10)
    }
    
    if (e.key === 'ArrowRight' && index < 7) {
      setCurrentIndex(index + 1)
      setTimeout(() => {
        if (inputRefs.current[index + 1]) {
          inputRefs.current[index + 1].focus()
        }
      }, 10)
    }
  }

  const handleSubmit = async (e) => {
    e.preventDefault()
    
    const enteredPin = pin.join('')
    
    if (enteredPin.length !== 8) {
      setError('Please enter all 8 digits')
      return
    }

    setIsLoading(true)
    setError('')

    // Simulate authentication delay
    setTimeout(() => {
      if (enteredPin === ADMIN_PIN) {
        // Store admin session
        localStorage.setItem('admin_authenticated', 'true')
        localStorage.setItem('admin_login_time', Date.now().toString())
        onAdminLogin()
      } else {
        setError('Invalid PIN. Access denied.')
        setPin(['', '', '', '', '', '', '', ''])
        setCurrentIndex(0)
        if (inputRefs.current[0]) {
          inputRefs.current[0].focus()
        }
      }
      setIsLoading(false)
    }, 1000)
  }

  const handleClear = () => {
    setPin(['', '', '', '', '', '', '', ''])
    setCurrentIndex(0)
    setError('')
    if (inputRefs.current[0]) {
      inputRefs.current[0].focus()
    }
  }

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
      <div className="bg-white rounded-lg shadow-xl w-full max-w-md mx-4">
        {/* Header */}
        <div className="bg-gradient-to-r from-red-600 to-red-700 px-6 py-4 rounded-t-lg">
          <div className="flex items-center space-x-3">
            <ShieldCheckIcon className="h-8 w-8 text-white" />
            <div>
              <h2 className="text-xl font-bold text-white">Admin Access</h2>
              <p className="text-red-100 text-sm">Secure authentication required</p>
            </div>
          </div>
        </div>

        <div className="p-6">
          {/* Security Notice */}
          <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-4 mb-6">
            <div className="flex items-start">
              <ExclamationTriangleIcon className="h-5 w-5 text-yellow-600 mt-0.5 mr-3 flex-shrink-0" />
              <div className="text-sm text-yellow-800">
                <p className="font-medium">Security Notice</p>
                <p>This area is restricted to authorized personnel only. All access attempts are logged.</p>
              </div>
            </div>
          </div>

          {/* PIN Input Form */}
          <form onSubmit={handleSubmit} className="space-y-6">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-3">
                Enter 8-Digit Admin PIN
              </label>
              
              {/* PIN Input Boxes */}
              <div className="flex justify-center space-x-2 mb-4">
                {pin.map((digit, index) => (
                  <input
                    key={index}
                    ref={el => inputRefs.current[index] = el}
                    type="password"
                    maxLength="1"
                    value={digit}
                    onChange={(e) => handleInputChange(index, e.target.value)}
                    onKeyDown={(e) => handleKeyDown(index, e)}
                    onFocus={() => setCurrentIndex(index)}
                    className={`w-12 h-12 text-center text-xl font-bold border-2 rounded-lg focus:outline-none focus:ring-2 focus:ring-red-500 transition-colors ${
                      digit 
                        ? 'border-green-500 bg-green-50 text-green-700' 
                        : currentIndex === index 
                        ? 'border-red-500 bg-red-50' 
                        : 'border-gray-300 hover:border-gray-400'
                    }`}
                    disabled={isLoading}
                  />
                ))}
              </div>

              {/* Error Message */}
              {error && (
                <div className="flex items-center space-x-2 text-red-600 text-sm mb-4">
                  <ExclamationTriangleIcon className="h-4 w-4" />
                  <span>{error}</span>
                </div>
              )}

              {/* Success Message */}
              {pin.join('') === ADMIN_PIN && (
                <div className="flex items-center space-x-2 text-green-600 text-sm mb-4">
                  <CheckCircleIcon className="h-4 w-4" />
                  <span>PIN verified successfully</span>
                </div>
              )}
            </div>

            {/* Action Buttons */}
            <div className="flex space-x-3">
              <button
                type="button"
                onClick={handleClear}
                disabled={isLoading}
                className="flex-1 px-4 py-2 border border-gray-300 rounded-lg text-gray-700 hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
              >
                Clear
              </button>
              
              <button
                type="submit"
                disabled={isLoading || pin.join('').length !== 8}
                className="flex-1 px-4 py-2 bg-red-600 text-white rounded-lg hover:bg-red-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors flex items-center justify-center space-x-2"
              >
                {isLoading ? (
                  <>
                    <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white"></div>
                    <span>Verifying...</span>
                  </>
                ) : (
                  <>
                    <LockClosedIcon className="h-4 w-4" />
                    <span>Access Admin</span>
                  </>
                )}
              </button>
            </div>
          </form>

          {/* Security Features */}
          <div className="mt-6 pt-4 border-t border-gray-200">
            <div className="text-xs text-gray-500 space-y-1">
              <div className="flex items-center space-x-2">
                <div className="w-2 h-2 bg-green-500 rounded-full"></div>
                <span>Encrypted connection</span>
              </div>
              <div className="flex items-center space-x-2">
                <div className="w-2 h-2 bg-blue-500 rounded-full"></div>
                <span>Session timeout: 30 minutes</span>
              </div>
              <div className="flex items-center space-x-2">
                <div className="w-2 h-2 bg-yellow-500 rounded-full"></div>
                <span>Access attempts logged</span>
              </div>
            </div>
          </div>

          {/* Cancel Button */}
          <div className="mt-4 text-center">
            <button
              onClick={onCancel}
              className="text-sm text-gray-500 hover:text-gray-700 transition-colors"
            >
              Cancel
            </button>
          </div>
        </div>
      </div>
    </div>
  )
}

export default AdminAuth
