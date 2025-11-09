import React from 'react'
import { FaUsers, FaImage, FaHeart, FaCheckCircle } from 'react-icons/fa'

function InstagramResults({ data }) {
  if (!data) return <p className="text-gray-500 text-sm">No data available</p>

  if (data.profiles && Array.isArray(data.profiles)) {
    return (
      <div className="space-y-4">
        <div className="p-3 bg-pink-50 rounded-lg border border-pink-200">
          <p className="text-sm font-medium text-pink-900">Found {data.count || data.profiles.length} Instagram profiles</p>
        </div>
        <div className="space-y-3">
          {data.profiles.map((profile, index) => (
            <div key={index} className="p-4 bg-gradient-to-r from-pink-50 to-rose-50 rounded-lg border-2 border-pink-200">
              <div className="flex items-start gap-3">
                {profile.profile_pic_url && (
                  <img src={profile.profile_pic_url} alt={profile.full_name} className="w-16 h-16 rounded-full border-2 border-white" />
                )}
                <div className="flex-1">
                  <div className="flex items-center gap-2 mb-1">
                    <p className="font-bold text-gray-900">{profile.full_name || profile.username}</p>
                    <p className="text-gray-600">@{profile.username}</p>
                    {profile.is_verified && (
                      <FaCheckCircle className="text-blue-500" />
                    )}
                  </div>
                  {profile.biography && (
                    <p className="text-sm text-gray-700 mb-2">{profile.biography}</p>
                  )}
                  <div className="flex items-center gap-4 text-sm">
                    <span className="text-gray-600"><strong>{profile.followers?.toLocaleString() || 0}</strong> followers</span>
                    {profile.is_private && (
                      <span className="px-2 py-1 bg-gray-100 text-gray-700 rounded text-xs">Private</span>
                    )}
                  </div>
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
      <div className="p-4 bg-gradient-to-r from-pink-50 to-rose-50 rounded-lg border-2 border-pink-200">
        <div className="flex items-center gap-3 mb-4">
          {data.profile_pic_url && (
            <img src={data.profile_pic_url} alt={data.full_name} className="w-16 h-16 rounded-full border-2 border-white" />
          )}
          <div>
            <div className="flex items-center gap-2">
              <p className="text-xl font-bold text-gray-900">{data.full_name || data.username}</p>
              {data.is_verified && (
                <FaCheckCircle className="text-blue-500 text-lg" />
              )}
            </div>
            <p className="text-gray-600">@{data.username}</p>
          </div>
        </div>
      </div>

      <div className="grid grid-cols-2 gap-4">
        <div className="p-3 bg-white rounded-lg border border-gray-200">
          <p className="text-xs text-gray-500 mb-1 flex items-center gap-1">
            <FaUsers className="text-xs" />
            Followers
          </p>
          <p className="text-xl sm:text-2xl font-bold text-gray-900">{data.followers?.toLocaleString() || 0}</p>
        </div>
        <div className="p-3 bg-white rounded-lg border border-gray-200">
          <p className="text-xs text-gray-500 mb-1 flex items-center gap-1">
            <FaImage className="text-xs" />
            Posts
          </p>
          <p className="text-xl sm:text-2xl font-bold text-gray-900">{data.posts_count?.toLocaleString() || 0}</p>
        </div>
      </div>

      {data.biography && (
        <div className="p-3 bg-white rounded-lg border border-gray-200">
          <p className="text-xs text-gray-500 mb-1">Bio</p>
          <p className="text-sm text-gray-900">{data.biography}</p>
        </div>
      )}

      {data.posts && data.posts.length > 0 && (
        <div>
          <p className="text-xs sm:text-sm font-semibold text-gray-900 mb-3">Recent Posts</p>
          <div className="grid grid-cols-2 sm:grid-cols-3 gap-2">
            {data.posts.slice(0, 9).map((post, index) => (
              <a
                key={index}
                href={post.url}
                target="_blank"
                rel="noopener noreferrer"
                className="relative group"
              >
                {post.thumbnail_url && (
                  <img
                    src={post.thumbnail_url}
                    alt={post.caption || 'Post'}
                    className="w-full h-24 sm:h-32 object-cover rounded border border-gray-200 group-hover:border-pink-300 transition-colors"
                  />
                )}
                <div className="absolute inset-0 bg-black bg-opacity-0 group-hover:bg-opacity-30 transition-opacity rounded flex items-center justify-center">
                  <span className="text-white opacity-0 group-hover:opacity-100 text-xs flex items-center gap-1">
                    <FaHeart className="text-xs" />
                    {post.likes || 0}
                  </span>
                </div>
              </a>
            ))}
          </div>
        </div>
      )}
    </div>
  )
}

export default InstagramResults

