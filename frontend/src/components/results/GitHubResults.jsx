import React from 'react'
import { FaUsers, FaCode, FaFileCode, FaMapMarkerAlt, FaStar } from 'react-icons/fa'

function GitHubResults({ data }) {
  if (!data) return <p className="text-gray-500 text-sm">No data available</p>

  const user = data.user || {}
  const repos = data.repos || []

  return (
    <div className="space-y-4">
      <div className="p-4 bg-gradient-to-r from-gray-50 to-slate-50 rounded-lg border-2 border-gray-200">
        <div className="flex items-center gap-3 mb-4">
          {user.avatar_url && (
            <img src={user.avatar_url} alt={user.name} className="w-16 h-16 rounded-full border-2 border-white" />
          )}
          <div>
            <p className="text-xl font-bold text-gray-900">{user.name || user.login}</p>
            <p className="text-gray-600">@{user.login}</p>
          </div>
        </div>
      </div>

      <div className="grid grid-cols-2 gap-4">
        <div className="p-3 bg-white rounded-lg border border-gray-200">
          <p className="text-xs text-gray-500 mb-1 flex items-center gap-1">
            <FaUsers className="text-xs" />
            Followers
          </p>
          <p className="text-xl sm:text-2xl font-bold text-gray-900">{user.followers?.toLocaleString() || 0}</p>
        </div>
        <div className="p-3 bg-white rounded-lg border border-gray-200">
          <p className="text-xs text-gray-500 mb-1 flex items-center gap-1">
            <FaCode className="text-xs" />
            Repositories
          </p>
          <p className="text-xl sm:text-2xl font-bold text-gray-900">{user.public_repos || 0}</p>
        </div>
        {user.public_gists && (
          <div className="p-3 bg-white rounded-lg border border-gray-200">
            <p className="text-xs text-gray-500 mb-1 flex items-center gap-1">
              <FaFileCode className="text-xs" />
              Gists
            </p>
            <p className="text-xl sm:text-2xl font-bold text-gray-900">{user.public_gists}</p>
          </div>
        )}
        {user.following !== undefined && (
          <div className="p-3 bg-white rounded-lg border border-gray-200">
            <p className="text-xs text-gray-500 mb-1 flex items-center gap-1">
              <FaUsers className="text-xs" />
              Following
            </p>
            <p className="text-xl sm:text-2xl font-bold text-gray-900">{user.following}</p>
          </div>
        )}
      </div>
      {user.bio && (
        <div className="p-3 bg-white rounded-lg border border-gray-200">
          <p className="text-xs text-gray-500 mb-1">Bio</p>
          <p className="text-sm text-gray-900">{user.bio}</p>
        </div>
      )}
      {user.location && (
        <div className="p-3 bg-white rounded-lg border border-gray-200">
          <p className="text-xs text-gray-500 mb-1 flex items-center gap-1">
            <FaMapMarkerAlt className="text-xs" />
            Location
          </p>
          <p className="text-sm font-medium text-gray-900">{user.location}</p>
        </div>
      )}
      {repos.length > 0 && (
        <div>
          <p className="text-sm font-semibold text-gray-900 mb-3">Recent Repositories</p>
          <div className="space-y-2 max-h-96 overflow-y-auto">
            {repos.slice(0, 5).map((repo, index) => (
              <a
                key={index}
                href={repo.html_url}
                target="_blank"
                rel="noopener noreferrer"
                className="block p-3 bg-white rounded-lg border border-gray-200 hover:border-gray-300 hover:shadow-md transition-all"
              >
                <p className="font-semibold text-sm text-gray-900 mb-1">{repo.name}</p>
                {repo.description && (
                  <p className="text-xs text-gray-600 mb-2 line-clamp-2">{repo.description}</p>
                )}
                <div className="flex items-center gap-3 text-xs text-gray-500">
                  <span className="flex items-center gap-1">
                    <FaStar className="text-xs" />
                    {repo.stargazers_count || 0} stars
                  </span>
                  {repo.language && (
                    <>
                      <span>•</span>
                      <span className="flex items-center gap-1">
                        <FaCode className="text-xs" />
                        {repo.language}
                      </span>
                    </>
                  )}
                </div>
              </a>
            ))}
          </div>
        </div>
      )}
    </div>
  )
}

export default GitHubResults

