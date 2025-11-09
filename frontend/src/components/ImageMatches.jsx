import React from 'react'
import { FaImage, FaInfoCircle } from 'react-icons/fa'

function ImageMatches({ matches = [] }) {
  if (!matches || matches.length === 0) {
    return null
  }

  const getMatchColor = (similarity) => {
    if (similarity > 0.9) return 'from-green-400 to-emerald-500'
    if (similarity > 0.8) return 'from-yellow-400 to-orange-500'
    return 'from-blue-400 to-cyan-500'
  }

  const getMatchLabel = (similarity) => {
    if (similarity > 0.9) return 'Very High Match'
    if (similarity > 0.8) return 'High Match'
    return 'Medium Match'
  }

  return (
    <div className="bg-white rounded-lg shadow p-4 sm:p-6">
      <div className="flex items-center gap-3 mb-4">
        <FaImage className="text-blue-600 text-2xl sm:text-3xl" />
        <div>
          <h2 className="text-lg sm:text-xl font-bold text-gray-900">Photo Matches</h2>
          <p className="text-xs sm:text-sm text-gray-600">Found {matches.length} matching images</p>
        </div>
      </div>

      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
        {matches.map((match, index) => (
          <div
            key={index}
            className={`relative overflow-hidden rounded-lg border-2 border-gray-200 hover:shadow-xl transition-all group bg-gradient-to-br ${getMatchColor(match.similarity)}`}
          >
            <div className="aspect-w-16 aspect-h-9 bg-gray-100">
              <img
                src={match.candidate_image_url || match.url}
                alt={match.title || 'Match'}
                className="w-full h-40 sm:h-48 object-cover group-hover:scale-105 transition-transform duration-300"
                onError={(e) => {
                  e.target.src = 'data:image/svg+xml,%3Csvg xmlns="http://www.w3.org/2000/svg" width="400" height="300"%3E%3Crect fill="%23ddd" width="400" height="300"/%3E%3Ctext fill="%23999" font-family="sans-serif" font-size="20" dy="10.5" font-weight="bold" x="50%25" y="50%25" text-anchor="middle"%3EImage Not Available%3C/text%3E%3C/svg%3E'
                }}
              />
            </div>
            
            <div className="absolute top-2 right-2">
              <span className={`px-2 sm:px-3 py-1 rounded-full text-xs font-bold text-white bg-black bg-opacity-60 backdrop-blur-sm`}>
                {Math.round(match.similarity * 100)}% Match
              </span>
            </div>

            <div className="p-3 sm:p-4 bg-white bg-opacity-95 backdrop-blur-sm">
              <div className="flex items-center justify-between mb-2">
                <span className={`px-2 py-1 rounded text-xs font-semibold ${
                  match.similarity > 0.9 ? 'bg-green-100 text-green-800' : 
                  match.similarity > 0.8 ? 'bg-yellow-100 text-yellow-800' : 
                  'bg-blue-100 text-blue-800'
                }`}>
                  {getMatchLabel(match.similarity)}
                </span>
              </div>
              
              {match.title && (
                <h3 className="font-semibold text-gray-900 text-xs sm:text-sm mb-1 line-clamp-2">
                  {match.title}
                </h3>
              )}
              
              {match.context && (
                <p className="text-xs text-gray-600 line-clamp-2 mb-2">
                  {match.context}
                </p>
              )}
              
              {match.source && (
                <a
                  href={match.source}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="text-xs text-blue-600 hover:text-blue-800 font-medium"
                >
                  View Source →
                </a>
              )}
            </div>
          </div>
        ))}
      </div>

      {matches.length > 0 && (
        <div className="mt-4 p-3 sm:p-4 bg-blue-50 rounded-lg border border-blue-200">
          <p className="text-xs sm:text-sm text-blue-900 flex items-start gap-2">
            <FaInfoCircle className="text-blue-600 mt-0.5 flex-shrink-0" />
            <span>These images were matched using facial recognition and image hashing. Higher similarity scores indicate stronger matches.</span>
          </p>
        </div>
      )}
    </div>
  )
}

export default ImageMatches

