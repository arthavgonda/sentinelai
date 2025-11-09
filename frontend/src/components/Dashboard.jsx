import React, { useState, useCallback, useMemo } from 'react'
import { useNavigate } from 'react-router-dom'
import axios from 'axios'
import SearchForm from './SearchForm'
import RecentProfiles from './RecentProfiles'
import StatsPanel from './StatsPanel'

function Dashboard() {
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState(null)
  const navigate = useNavigate()

  const handleSearch = useCallback(async (query, queryType) => {
    setLoading(true)
    setError(null)
    
    try {
      const response = await axios.post('/api/search', {
        query,
        query_type: queryType
      })
      
      navigate(`/profile/${response.data.profile_id}`)
    } catch (err) {
      setError(err.response?.data?.detail || 'Search failed')
      setLoading(false)
    }
  }, [navigate])

  return (
    <div className="space-y-6 sm:space-y-8 px-2 sm:px-0">
      <div className="text-center">
        <h1 className="text-2xl sm:text-3xl lg:text-4xl font-bold text-gray-900 mb-3 sm:mb-4">
          OSINT & Threat Actor Profiling System
        </h1>
        <p className="text-sm sm:text-base lg:text-lg text-gray-600">
          Fast, comprehensive intelligence gathering from 12+ sources
        </p>
      </div>

      <StatsPanel />

      <div className="bg-white rounded-lg shadow p-4 sm:p-6">
        <SearchForm onSubmit={handleSearch} loading={loading} error={error} />
      </div>

      <RecentProfiles />
    </div>
  )
}

export default Dashboard

