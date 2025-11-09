import React from 'react'

function CircularProgress({ progress = 0, timeRemaining = null, size = 120, strokeWidth = 8 }) {
  const radius = (size - strokeWidth) / 2
  const circumference = radius * 2 * Math.PI
  const offset = circumference - (progress / 100) * circumference

  const formatTime = (seconds) => {
    if (!seconds || seconds < 0) return 'Calculating...'
    if (seconds < 60) return `${Math.ceil(seconds)}s`
    const minutes = Math.floor(seconds / 60)
    const secs = Math.ceil(seconds % 60)
    return `${minutes}m ${secs}s`
  }

  return (
    <div className="flex flex-col items-center justify-center p-6">
      <div className="relative" style={{ width: size, height: size }}>
        <svg
          width={size}
          height={size}
          className="transform -rotate-90"
        >
          {/* Background circle */}
          <circle
            cx={size / 2}
            cy={size / 2}
            r={radius}
            stroke="currentColor"
            strokeWidth={strokeWidth}
            fill="none"
            className="text-gray-200"
          />
          {/* Progress circle */}
          <circle
            cx={size / 2}
            cy={size / 2}
            r={radius}
            stroke="currentColor"
            strokeWidth={strokeWidth}
            fill="none"
            strokeDasharray={circumference}
            strokeDashoffset={offset}
            strokeLinecap="round"
            className="text-blue-600 transition-all duration-300 ease-in-out"
            style={{
              filter: 'drop-shadow(0 0 8px rgba(37, 99, 235, 0.5))'
            }}
          />
        </svg>
        {/* Progress text */}
        <div className="absolute inset-0 flex flex-col items-center justify-center">
          <div className="text-xl sm:text-2xl font-bold text-gray-900">
            {Math.round(progress)}%
          </div>
          {timeRemaining !== null && (
            <div className="text-xs text-gray-500 mt-1">
              {formatTime(timeRemaining)}
            </div>
          )}
        </div>
      </div>
      {/* Status text */}
      <div className="mt-3 sm:mt-4 text-center">
        <p className="text-xs sm:text-sm font-medium text-gray-700">
          Collecting data from sources...
        </p>
        {progress < 100 && (
          <p className="text-xs text-gray-500 mt-1">
            Please wait while we gather intelligence
          </p>
        )}
      </div>
    </div>
  )
}

export default CircularProgress

