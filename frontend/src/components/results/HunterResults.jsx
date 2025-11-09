import React from 'react'
import ValidationBadge from '../ValidationBadge'
import { FaEnvelope } from 'react-icons/fa'

function HunterResults({ data }) {
  if (!data) return <p className="text-gray-500 text-sm">No data available</p>

  const emails = data.emails || []
  const emailList = Array.isArray(emails) ? emails : (emails.data || [])

  const getEmailStatus = (email) => {
    if (email.verification) {
      if (email.verification.status === 'valid') return 'valid'
      if (email.verification.status === 'invalid') return 'invalid'
      return 'unknown'
    }
    if (email.confidence_score > 70) return 'valid'
    if (email.confidence_score > 40) return 'warning'
    return 'unknown'
  }

  const getEmailType = (email) => {
    return email.type || email.sources?.[0]?.type || 'unknown'
  }

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between mb-4">
        <h3 className="text-lg font-semibold text-gray-900">Email Intelligence</h3>
        {emailList.length > 0 && (
          <span className="px-3 py-1 bg-blue-100 text-blue-800 rounded-full text-sm font-medium">
            {emailList.length} {emailList.length === 1 ? 'email' : 'emails'} found
          </span>
        )}
      </div>

      {emailList.length > 0 ? (
        <div className="space-y-3">
          {emailList.map((email, index) => {
            const emailValue = email.value || email.email || email
            const status = getEmailStatus(email)
            const emailType = getEmailType(email)

            return (
              <div key={index} className="p-4 bg-gradient-to-r from-blue-50 to-indigo-50 rounded-lg border-2 border-blue-200 hover:shadow-lg transition-shadow">
                <div className="flex items-start justify-between mb-3">
                  <div className="flex-1">
                    <div className="flex items-center gap-2 mb-2">
                      <FaEnvelope className="text-blue-600 text-xl sm:text-2xl" />
                      <p className="text-base sm:text-lg font-bold text-gray-900">{emailValue}</p>
                    </div>
                    {emailType && emailType !== 'unknown' && (
                      <span className="inline-block px-2 py-1 bg-white rounded text-xs font-medium text-gray-700 border border-gray-300">
                        {emailType}
                      </span>
                    )}
                  </div>
                  <ValidationBadge status={status} label={status === 'valid' ? 'Verified' : status === 'invalid' ? 'Invalid' : 'Unverified'} />
                </div>

                <div className="grid grid-cols-2 gap-3 mt-3">
                  {email.confidence_score && (
                    <div className="p-2 bg-white rounded border border-gray-200">
                      <p className="text-xs text-gray-500">Confidence</p>
                      <p className="text-sm font-semibold text-gray-900">{email.confidence_score}%</p>
                    </div>
                  )}
                  {email.sources && email.sources.length > 0 && (
                    <div className="p-2 bg-white rounded border border-gray-200">
                      <p className="text-xs text-gray-500">Sources</p>
                      <p className="text-sm font-semibold text-gray-900">{email.sources.length}</p>
                    </div>
                  )}
                </div>

                {email.verification && (
                  <div className="mt-3 p-2 bg-white rounded border border-gray-200">
                    <p className="text-xs text-gray-500">Verification</p>
                    <p className="text-sm font-medium text-gray-900 capitalize">{email.verification.status || 'Unknown'}</p>
                  </div>
                )}
              </div>
            )
          })}
        </div>
      ) : (
        <div className="p-6 bg-gray-50 rounded-lg border border-gray-200 text-center">
          <p className="text-gray-500">No emails found for this query</p>
        </div>
      )}

      {data.domain && (
        <div className="p-4 bg-gray-50 rounded-lg border border-gray-200">
          <p className="text-sm text-gray-600">
            <span className="font-medium">Domain:</span> {data.domain}
          </p>
        </div>
      )}
    </div>
  )
}

export default HunterResults
