import React from 'react'

function OtherResults({ data }) {
  if (!data) return <p className="text-gray-500">No data available</p>

  return (
    <div className="space-y-4">
      <pre className="text-xs bg-gray-50 p-4 rounded overflow-auto max-h-96">
        {JSON.stringify(data, null, 2)}
      </pre>
    </div>
  )
}

export default OtherResults

