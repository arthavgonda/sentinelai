import React, { useState, useEffect, useCallback } from 'react'
import { useParams } from 'react-router-dom'
import axios from 'axios'
import { useWebSocket } from '../hooks/useWebSocket'
import ProfileHeader from './ProfileHeader'
import APIResults from './APIResults'
import CorrelationPanel from './CorrelationPanel'
import LoadingSkeleton from './LoadingSkeleton'
import ImageMatches from './ImageMatches'
import CircularProgress from './CircularProgress'
import ConfidenceReport from './ConfidenceReport'
import ProfileImage from './ProfileImage'

function ProfileView() {
  const { id } = useParams()
  const [profile, setProfile] = useState(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)
  const [progress, setProgress] = useState(0)
  const [progressMessage, setProgressMessage] = useState('Starting search...')
  const [timeRemaining, setTimeRemaining] = useState(null)
  const [completedApis, setCompletedApis] = useState(0)
  const [totalApis, setTotalApis] = useState(0)
  const [startTime, setStartTime] = useState(null)

  const handleWebSocketMessage = useCallback((data) => {
    if (data.type === 'progress' && data.profile_id === parseInt(id)) {
      setProgress(data.progress || 0)
      setProgressMessage(data.message || 'Processing...')
      setCompletedApis(data.completed || 0)
      setTotalApis(data.total || 0)
      
      if (!startTime) {
        setStartTime(Date.now())
      }
      
      // Calculate time remaining
      if (data.progress > 0 && data.progress < 100 && startTime) {
        const elapsed = (Date.now() - startTime) / 1000
        const rate = data.progress / elapsed
        const remaining = (100 - data.progress) / rate
        setTimeRemaining(remaining)
      } else if (data.progress >= 100) {
        setTimeRemaining(0)
      }
      
      setLoading(data.progress < 100)
    } else if (data.type === 'update' && data.profile_id === parseInt(id)) {
      setProfile(prev => ({
        ...prev,
        data: data.data,
        status: data.data.status || prev?.status || 'complete'
      }))
      setProgress(100)
      setTimeRemaining(0)
      setLoading(false)
    } else if (data.type === 'error') {
      setError(data.error)
      setLoading(false)
      setProgress(0)
    }
  }, [id, startTime])

  const { connected } = useWebSocket(`/ws/${id}`, handleWebSocketMessage)

  useEffect(() => {
    const fetchProfile = async () => {
      try {
        const response = await axios.get(`/api/profile/${id}`)
        setProfile(response.data)
        setLoading(false)
      } catch (err) {
        setError(err.response?.data?.detail || 'Failed to load profile')
        setLoading(false)
      }
    }

    fetchProfile()
  }, [id])

  if (loading && !profile) {
    return (
      <div className="flex items-center justify-center min-h-screen bg-gray-50 px-4">
        <div className="bg-white rounded-lg shadow-lg p-6 sm:p-8 max-w-md w-full">
          <CircularProgress 
            progress={progress} 
            timeRemaining={timeRemaining}
            size={120}
            strokeWidth={10}
          />
          <div className="mt-4 sm:mt-6 text-center">
            <p className="text-xs sm:text-sm font-medium text-gray-700">{progressMessage}</p>
            {totalApis > 0 && (
              <p className="text-xs text-gray-500 mt-2">
                {completedApis} of {totalApis} sources completed
              </p>
            )}
          </div>
        </div>
      </div>
    )
  }

  if (error) {
    return (
      <div className="bg-red-50 border border-red-200 rounded-lg p-4">
        <p className="text-red-700">{error}</p>
      </div>
    )
  }

  if (!profile) {
    return <div>Profile not found</div>
  }

  return (
    <div className="space-y-4 sm:space-y-6 px-2 sm:px-0">
      <ProfileHeader profile={profile} connected={connected} />
      
      {profile.status === 'pending' && (
        <div className="bg-white rounded-lg shadow-lg p-4 sm:p-8 mb-4 sm:mb-6">
          <CircularProgress 
            progress={progress} 
            timeRemaining={timeRemaining}
            size={100}
            strokeWidth={8}
          />
          <div className="mt-4 text-center">
            <p className="text-xs sm:text-sm font-medium text-gray-700">{progressMessage}</p>
            {totalApis > 0 && (
              <p className="text-xs text-gray-500 mt-2">
                {completedApis} of {totalApis} sources completed
              </p>
            )}
          </div>
        </div>
      )}

      {/* Profile Image */}
      {(profile.data?.primary_image || (profile.data?.images && profile.data.images.length > 0)) && (
        <div className="mb-4 sm:mb-6">
          <ProfileImage 
            images={profile.data?.images || []} 
            primaryImage={profile.data?.primary_image}
          />
        </div>
      )}

      {/* Confidence Report */}
      {profile.data?.analysis && (
        <div className="mb-4 sm:mb-6">
          <ConfidenceReport analysis={profile.data.analysis} />
        </div>
      )}

      {profile.data?.image_matches && Array.isArray(profile.data.image_matches) && profile.data.image_matches.length > 0 && (
        <div className="mb-4 sm:mb-6">
          <ImageMatches matches={profile.data.image_matches} />
        </div>
      )}

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-4 sm:gap-6">
        <div className="lg:col-span-2 order-2 lg:order-1">
          <APIResults results={profile.data?.results || {}} />
        </div>
        <div className="order-1 lg:order-2">
          <CorrelationPanel correlation={profile.data?.correlation || {}} />
        </div>
      </div>
    </div>
  )
}

export default ProfileView

