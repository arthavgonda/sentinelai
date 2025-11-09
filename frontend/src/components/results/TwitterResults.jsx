import React from 'react'
import { format } from 'date-fns'
import { FaComment, FaHeart, FaMapMarkerAlt } from 'react-icons/fa'

function TwitterResults({ data }) {
  if (!data) return <p className="text-gray-500 text-sm">No data available</p>

  if (data.users && Array.isArray(data.users)) {
    return (
      <div className="space-y-4">
        <div className="p-3 bg-blue-50 rounded-lg border border-blue-200">
          <p className="text-sm font-medium text-blue-900">Found {data.count || data.users.length} users matching this name</p>
        </div>
        <div className="space-y-3">
          {data.users.map((user, index) => (
            <div key={index} className="p-4 bg-gradient-to-r from-blue-50 to-cyan-50 rounded-lg border-2 border-blue-200">
              <div className="flex items-start gap-3">
                {user.profile_image && (
                  <img src={user.profile_image} alt={user.name} className="w-12 h-12 rounded-full border-2 border-white" />
                )}
                <div className="flex-1">
                  <div className="flex items-center gap-2 mb-1">
                    <p className="font-bold text-gray-900">{user.name}</p>
                    <p className="text-gray-600">@{user.username}</p>
                  </div>
                  {user.description && (
                    <p className="text-sm text-gray-700 mb-2">{user.description}</p>
                  )}
                  <div className="flex items-center gap-4 text-sm">
                    <span className="text-gray-600"><strong>{user.followers?.toLocaleString() || 0}</strong> followers</span>
                    <span className="text-gray-600"><strong>{user.following?.toLocaleString() || 0}</strong> following</span>
                  </div>
                  {user.location && (
                    <p className="text-xs text-gray-500 mt-2 flex items-center gap-1">
                      <FaMapMarkerAlt className="text-xs" />
                      {user.location}
                    </p>
                  )}
                </div>
              </div>
            </div>
          ))}
        </div>
      </div>
    )
  }

  return (
    <div className="space-y-4">
      <div className="p-4 bg-gradient-to-r from-blue-50 to-cyan-50 rounded-lg border-2 border-blue-200">
        <div className="flex items-center gap-3 mb-4">
          {data.profile_image && (
            <img src={data.profile_image} alt={data.name} className="w-16 h-16 rounded-full border-2 border-white" />
          )}
          <div>
            <p className="text-xl font-bold text-gray-900">{data.name}</p>
            <p className="text-gray-600">@{data.username}</p>
          </div>
        </div>
      </div>

      <div className="grid grid-cols-2 gap-4">
        <div className="p-3 bg-white rounded-lg border border-gray-200">
          <p className="text-xs text-gray-500 mb-1">Followers</p>
          <p className="text-2xl font-bold text-gray-900">{data.followers?.toLocaleString() || 0}</p>
        </div>
        <div className="p-3 bg-white rounded-lg border border-gray-200">
          <p className="text-xs text-gray-500 mb-1">Following</p>
          <p className="text-2xl font-bold text-gray-900">{data.following?.toLocaleString() || 0}</p>
        </div>
      </div>
      {data.description && (
        <div className="p-3 bg-white rounded-lg border border-gray-200">
          <p className="text-xs text-gray-500 mb-1">Bio</p>
          <p className="text-sm text-gray-900">{data.description}</p>
        </div>
      )}
      {data.location && (
        <div className="p-3 bg-white rounded-lg border border-gray-200">
          <p className="text-xs text-gray-500 mb-1 flex items-center gap-1">
            <FaMapMarkerAlt className="text-xs" />
            Location
          </p>
          <p className="text-sm font-medium text-gray-900">{data.location}</p>
        </div>
      )}
      {data.recent_tweets && data.recent_tweets.length > 0 && (
        <div>
          <p className="text-sm font-semibold text-gray-900 mb-3">Recent Tweets</p>
          <div className="space-y-2 max-h-96 overflow-y-auto">
            {data.recent_tweets.slice(0, 5).map((tweet, index) => (
              <div key={index} className="p-3 bg-white rounded-lg border border-gray-200 hover:border-blue-300 transition-colors">
                <p className="text-sm text-gray-900 mb-2">{tweet.text}</p>
                <div className="flex items-center gap-3 text-xs text-gray-500">
                  <span className="flex items-center gap-1">
                    <FaComment className="text-xs" />
                    {format(new Date(tweet.created_at), 'PP')}
                  </span>
                  <span className="flex items-center gap-1">
                    <FaHeart className="text-xs" />
                    {tweet.likes || 0} likes
                  </span>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  )
}

export default TwitterResults

