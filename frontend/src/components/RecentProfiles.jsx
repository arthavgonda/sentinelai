import React, { useState, useEffect } from 'react'
import { Link } from 'react-router-dom'
import axios from 'axios'
import { format } from 'date-fns'

function RecentProfiles() {
  const [profiles, setProfiles] = useState([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    const fetchProfiles = async () => {
      try {
        const response = await axios.get('/api/profiles?limit=10')
        setProfiles(response.data.profiles)
      } catch (err) {
        console.error('Failed to fetch profiles:', err)
      } finally {
        setLoading(false)
      }
    }

    fetchProfiles()
  }, [])

  if (loading) {
    return <div className="bg-white rounded-lg shadow p-4 sm:p-6 text-sm">Loading...</div>
  }

  return (
    <div className="bg-white rounded-lg shadow">
      <div className="p-4 sm:p-6 border-b">
        <h2 className="text-base sm:text-lg font-semibold">Recent Profiles</h2>
      </div>
      <div className="divide-y">
        {profiles.length === 0 ? (
          <div className="p-4 sm:p-6 text-center text-gray-500 text-sm">No profiles yet</div>
        ) : (
          profiles.map(profile => (
            <Link
              key={profile.id}
              to={`/profile/${profile.id}`}
              className="block p-3 sm:p-4 hover:bg-gray-50 transition-colors"
            >
              <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-2 sm:gap-0">
                <div className="flex-1 min-w-0">
                  <p className="font-medium text-sm sm:text-base truncate">{profile.query}</p>
                  <p className="text-xs sm:text-sm text-gray-500">
                    {profile.query_type} • {format(new Date(profile.created_at), 'PPpp')}
                  </p>
                </div>
                <span className={`px-2 py-1 rounded text-xs flex-shrink-0 ${
                  profile.status === 'complete'
                    ? 'bg-green-100 text-green-800'
                    : 'bg-yellow-100 text-yellow-800'
                }`}>
                  {profile.status}
                </span>
              </div>
            </Link>
          ))
        )}
      </div>
    </div>
  )
}

export default RecentProfiles

