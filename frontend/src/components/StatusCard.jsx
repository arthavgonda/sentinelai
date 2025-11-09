import React from 'react'
import ValidationBadge from './ValidationBadge'
import { FaEnvelope, FaPhone, FaUser, FaInfoCircle } from 'react-icons/fa'

function StatusCard({ title, items = [], type = 'info' }) {
  const getTypeStyles = (type) => {
    switch (type) {
      case 'email':
        return {
          headerBg: 'bg-blue-50',
          headerText: 'text-blue-900',
          border: 'border-blue-200',
          icon: <FaEnvelope className="text-blue-600" />
        }
      case 'phone':
        return {
          headerBg: 'bg-purple-50',
          headerText: 'text-purple-900',
          border: 'border-purple-200',
          icon: <FaPhone className="text-purple-600" />
        }
      case 'username':
        return {
          headerBg: 'bg-indigo-50',
          headerText: 'text-indigo-900',
          border: 'border-indigo-200',
          icon: <FaUser className="text-indigo-600" />
        }
      default:
        return {
          headerBg: 'bg-gray-50',
          headerText: 'text-gray-900',
          border: 'border-gray-200',
          icon: <FaInfoCircle className="text-gray-600" />
        }
    }
  }

  const styles = getTypeStyles(type)

  return (
    <div className={`rounded-lg border-2 ${styles.border} overflow-hidden shadow-sm hover:shadow-md transition-shadow`}>
      <div className={`${styles.headerBg} px-3 sm:px-4 py-2 sm:py-3 border-b ${styles.border}`}>
        <div className="flex items-center gap-2">
          <span className="text-lg sm:text-xl">{styles.icon}</span>
          <h3 className={`font-semibold ${styles.headerText} text-sm sm:text-base`}>{title}</h3>
        </div>
      </div>
      <div className="p-3 sm:p-4 bg-white">
        {items.length > 0 ? (
          <div className="space-y-2 sm:space-y-3">
            {items.map((item, index) => (
              <div key={index} className="flex flex-col sm:flex-row sm:items-center sm:justify-between p-3 bg-gray-50 rounded-lg gap-2">
                <div className="flex-1 min-w-0">
                  <p className="font-medium text-gray-900 text-sm sm:text-base truncate">{item.value || item}</p>
                  {item.description && (
                    <p className="text-xs sm:text-sm text-gray-600 mt-1">{item.description}</p>
                  )}
                </div>
                {item.status && (
                  <ValidationBadge status={item.status} label={item.statusLabel || ''} />
                )}
              </div>
            ))}
          </div>
        ) : (
          <p className="text-gray-500 text-xs sm:text-sm">No data available</p>
        )}
      </div>
    </div>
  )
}

export default StatusCard

