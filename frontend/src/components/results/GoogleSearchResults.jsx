import React from 'react'
import { FaRobot, FaDatabase, FaQuestionCircle, FaImage, FaCheckCircle } from 'react-icons/fa'

function GoogleSearchResults({ data }) {
  if (!data) return <p className="text-gray-500 text-sm">No data available</p>

  const results = data.results || []
  const aiSummary = data.ai_summary
  const knowledgePanel = data.knowledge_panel
  const description = data.description || (aiSummary && aiSummary.text) || (knowledgePanel && knowledgePanel.description)
  const peopleAlsoAsk = data.people_also_ask || []
  const images = data.images || []

  return (
    <div className="space-y-4">
      {/* Main Description / AI Summary */}
      {description && (
        <div className="p-4 sm:p-5 bg-gradient-to-r from-blue-50 to-indigo-50 rounded-lg border-2 border-blue-200">
          <div className="flex items-center gap-2 mb-3">
            <FaRobot className="text-blue-600 text-xl sm:text-2xl" />
            <div>
              <h3 className="font-bold text-gray-900 text-sm sm:text-base">
                {aiSummary ? 'AI Summary' : knowledgePanel ? 'Description' : 'Summary'}
              </h3>
              <p className="text-xs text-gray-600">
                {aiSummary?.source || 'Google Knowledge Panel' || 'Google Search'}
              </p>
            </div>
          </div>
          <p className="text-xs sm:text-sm text-gray-800 leading-relaxed whitespace-pre-wrap">{description}</p>
        </div>
      )}

      {/* Images from Google */}
      {images.length > 0 && (
        <div className="p-3 sm:p-4 bg-gray-50 rounded-lg">
          <h3 className="text-xs sm:text-sm font-semibold text-gray-700 mb-3 flex items-center gap-2">
            <FaImage className="text-gray-600" />
            Images Found
          </h3>
          <div className="grid grid-cols-2 sm:grid-cols-3 gap-2 sm:gap-3">
            {images.map((img, index) => (
              <div key={index} className="relative">
                <img
                  src={img.url}
                  alt={img.alt || `Image ${index + 1}`}
                  className="w-full h-24 sm:h-32 object-cover rounded border border-gray-200"
                  onError={(e) => {
                    e.target.style.display = 'none'
                  }}
                />
                {img.source && (
                  <div className="absolute bottom-0 left-0 right-0 bg-black bg-opacity-60 text-white text-xs px-2 py-1 truncate">
                    {img.source.replace('_', ' ')}
                  </div>
                )}
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Knowledge Panel */}
      {knowledgePanel && Object.keys(knowledgePanel).length > 0 && (
        <div className="p-3 sm:p-4 bg-yellow-50 rounded-lg border border-yellow-200">
          <h3 className="font-semibold text-gray-900 mb-2 text-sm sm:text-base flex items-center gap-2">
            <FaDatabase className="text-yellow-600" />
            Knowledge Panel
          </h3>
          <div className="space-y-1">
            {Object.entries(knowledgePanel).map(([key, value], index) => (
              <div key={index} className="text-xs sm:text-sm">
                <span className="font-medium text-gray-700">{key}:</span>{' '}
                <span className="text-gray-600">{value}</span>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* People Also Ask */}
      {peopleAlsoAsk.length > 0 && (
        <div className="p-3 sm:p-4 bg-purple-50 rounded-lg border border-purple-200">
          <h3 className="font-semibold text-gray-900 mb-2 text-sm sm:text-base flex items-center gap-2">
            <FaQuestionCircle className="text-purple-600" />
            People Also Ask
          </h3>
          <div className="space-y-2">
            {peopleAlsoAsk.map((question, index) => (
              <div key={index} className="text-xs sm:text-sm text-gray-700">
                • {question}
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Search Results */}
      {results.length > 0 && (
        <div>
          <h3 className="font-semibold text-gray-900 mb-3 text-sm sm:text-base flex items-center gap-2">
            <FaDatabase className="text-gray-600" />
            Search Results ({results.length})
          </h3>
          <div className="space-y-2 sm:space-y-3">
            {results.map((result, index) => (
              <div
                key={index}
                className="p-3 sm:p-4 bg-white rounded-lg border border-gray-200 hover:border-blue-300 hover:shadow-md transition-all"
              >
                <a
                  href={result.url}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="text-blue-600 hover:text-blue-800 font-medium text-xs sm:text-sm mb-1 block line-clamp-2"
                >
                  {result.title}
                </a>
                <p className="text-xs text-gray-500 mb-2 truncate">{result.url}</p>
                {result.snippet && (
                  <p className="text-xs sm:text-sm text-gray-700 line-clamp-3">{result.snippet}</p>
                )}
                {result.query_match && (
                  <span className="inline-flex items-center gap-1 mt-2 px-2 py-1 bg-green-100 text-green-800 text-xs rounded">
                    <FaCheckCircle className="text-xs" />
                    Query Match
                  </span>
                )}
              </div>
            ))}
          </div>
        </div>
      )}

      {results.length === 0 && !aiSummary && !knowledgePanel && (
        <p className="text-gray-500">No Google search results found</p>
      )}
    </div>
  )
}

export default GoogleSearchResults

