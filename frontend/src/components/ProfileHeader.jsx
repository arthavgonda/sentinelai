import React from 'react'
import { format } from 'date-fns'

function ProfileHeader({ profile, connected }) {
  return (
    <div className="bg-white rounded-lg shadow p-4 sm:p-6">
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-3 sm:gap-0">
        <div className="flex-1 min-w-0">
          <h1 className="text-xl sm:text-2xl font-bold text-gray-900 truncate">
            {profile.query}
          </h1>
          <p className="text-xs sm:text-sm text-gray-500 mt-1">
            {profile.query_type} • Created {format(new Date(profile.created_at), 'PPpp')}
          </p>
        </div>
        <div className="flex items-center gap-2 sm:space-x-4">
          <div className={`px-2 sm:px-3 py-1 rounded-full text-xs sm:text-sm font-medium ${
            profile.status === 'complete' 
              ? 'bg-green-100 text-green-800' 
              : 'bg-yellow-100 text-yellow-800'
          }`}>
            {profile.status}
          </div>
          <div className={`px-2 sm:px-3 py-1 rounded-full text-xs sm:text-sm font-medium ${
            connected 
              ? 'bg-green-100 text-green-800' 
              : 'bg-gray-100 text-gray-800'
          }`}>
            {connected ? 'Live' : 'Offline'}
          </div>
        </div>
      </div>
      {profile.data?.collection_time && (
        <div className="mt-3 sm:mt-4 text-xs sm:text-sm text-gray-600">
          Collection time: {typeof profile.data.collection_time === 'number' ? profile.data.collection_time.toFixed(2) : profile.data.collection_time}s
        </div>
      )}
    </div>
  )
}

export default ProfileHeader

