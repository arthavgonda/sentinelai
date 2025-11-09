import React, { useState, useEffect } from 'react'
import axios from 'axios'

function StatsPanel() {
  const [stats, setStats] = useState({
    total: 0,
    complete: 0,
    pending: 0
  })

  useEffect(() => {
    const fetchStats = async () => {
      try {
        const response = await axios.get('/api/profiles?limit=1000')
        const profiles = response.data.profiles
        setStats({
          total: profiles.length,
          complete: profiles.filter(p => p.status === 'complete').length,
          pending: profiles.filter(p => p.status === 'pending').length
        })
      } catch (err) {
        console.error('Failed to fetch stats:', err)
      }
    }

    fetchStats()
  }, [])

  return (
    <div className="grid grid-cols-1 sm:grid-cols-3 gap-3 sm:gap-4">
      <div className="bg-white rounded-lg shadow p-4 sm:p-6">
        <h3 className="text-xs sm:text-sm font-medium text-gray-500">Total Profiles</h3>
        <p className="text-xl sm:text-2xl font-bold text-gray-900 mt-2">{stats.total}</p>
      </div>
      <div className="bg-white rounded-lg shadow p-4 sm:p-6">
        <h3 className="text-xs sm:text-sm font-medium text-gray-500">Complete</h3>
        <p className="text-xl sm:text-2xl font-bold text-green-600 mt-2">{stats.complete}</p>
      </div>
      <div className="bg-white rounded-lg shadow p-4 sm:p-6">
        <h3 className="text-xs sm:text-sm font-medium text-gray-500">Pending</h3>
        <p className="text-xl sm:text-2xl font-bold text-yellow-600 mt-2">{stats.pending}</p>
      </div>
    </div>
  )
}

export default StatsPanel

