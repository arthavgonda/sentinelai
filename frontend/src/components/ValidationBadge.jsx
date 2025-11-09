import React from 'react'
import { FaCheckCircle, FaTimesCircle, FaExclamationTriangle, FaQuestionCircle } from 'react-icons/fa'

function ValidationBadge({ status, label, value }) {
  const getStatusConfig = (status) => {
    switch (status) {
      case 'valid':
      case 'good':
      case 'verified':
        return {
          bg: 'bg-green-100',
          text: 'text-green-800',
          border: 'border-green-300',
          icon: <FaCheckCircle className="text-green-600" />,
          iconColor: 'text-green-600'
        }
      case 'invalid':
      case 'bad':
      case 'risky':
        return {
          bg: 'bg-red-100',
          text: 'text-red-800',
          border: 'border-red-300',
          icon: <FaTimesCircle className="text-red-600" />,
          iconColor: 'text-red-600'
        }
      case 'warning':
      case 'unknown':
      case 'unverified':
        return {
          bg: 'bg-yellow-100',
          text: 'text-yellow-800',
          border: 'border-yellow-300',
          icon: <FaExclamationTriangle className="text-yellow-600" />,
          iconColor: 'text-yellow-600'
        }
      default:
        return {
          bg: 'bg-gray-100',
          text: 'text-gray-800',
          border: 'border-gray-300',
          icon: <FaQuestionCircle className="text-gray-600" />,
          iconColor: 'text-gray-600'
        }
    }
  }

  const config = getStatusConfig(status)

  return (
    <div className={`inline-flex items-center px-2 sm:px-3 py-1 sm:py-1.5 rounded-lg border ${config.bg} ${config.border} ${config.text}`}>
      <span className={`text-sm sm:text-base mr-1 sm:mr-2 ${config.iconColor}`}>{config.icon}</span>
      <div className="flex flex-col">
        <span className="text-xs font-medium uppercase tracking-wide opacity-75">{label}</span>
        {value && <span className="text-xs sm:text-sm font-semibold">{value}</span>}
      </div>
    </div>
  )
}

export default ValidationBadge

