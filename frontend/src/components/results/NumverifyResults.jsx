import React from 'react'
import ValidationBadge from '../ValidationBadge'
import { FaExclamationTriangle } from 'react-icons/fa'

function NumverifyResults({ data }) {
  if (!data) return <p className="text-gray-500 text-sm">No data available</p>

  const getStatus = (data) => {
    if (data.valid === true) {
      return data.line_type === 'mobile' ? 'valid' : 'warning'
    }
    return 'invalid'
  }

  const status = getStatus(data)

  return (
    <div className="space-y-4">
      <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
        <div className="p-3 sm:p-4 bg-gradient-to-br from-purple-50 to-blue-50 rounded-lg border-2 border-purple-200">
          <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between mb-3 gap-2">
            <h4 className="font-semibold text-gray-900 text-sm sm:text-base">Phone Number</h4>
            <ValidationBadge status={status} label={data.valid ? 'Valid' : 'Invalid'} />
          </div>
          <p className="text-xl sm:text-2xl font-bold text-gray-900 mb-2">{data.number || data.phone_number}</p>
          {data.local_format && (
            <p className="text-xs sm:text-sm text-gray-600">Local: {data.local_format}</p>
          )}
        </div>

        {data.country_name && (
          <div className="p-3 sm:p-4 bg-white rounded-lg border border-gray-200">
            <h4 className="text-xs sm:text-sm font-medium text-gray-500 mb-2">Location</h4>
            <p className="text-base sm:text-lg font-semibold text-gray-900">{data.country_name}</p>
            {data.location && <p className="text-xs sm:text-sm text-gray-600 mt-1">{data.location}</p>}
          </div>
        )}

        {data.carrier && (
          <div className="p-3 sm:p-4 bg-white rounded-lg border border-gray-200">
            <h4 className="text-xs sm:text-sm font-medium text-gray-500 mb-2">Carrier</h4>
            <p className="text-base sm:text-lg font-semibold text-gray-900">{data.carrier}</p>
          </div>
        )}

        {data.line_type && (
          <div className="p-3 sm:p-4 bg-white rounded-lg border border-gray-200">
            <h4 className="text-xs sm:text-sm font-medium text-gray-500 mb-2">Line Type</h4>
            <p className="text-base sm:text-lg font-semibold text-gray-900 capitalize">{data.line_type}</p>
          </div>
        )}
      </div>

      {data.valid === false && (
        <div className="p-3 sm:p-4 bg-red-50 border border-red-200 rounded-lg">
          <p className="text-xs sm:text-sm text-red-800 font-medium flex items-center gap-2">
            <FaExclamationTriangle className="text-red-600" />
            This phone number could not be validated
          </p>
        </div>
      )}
    </div>
  )
}

export default NumverifyResults

