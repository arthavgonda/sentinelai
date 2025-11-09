import React from 'react'
import { FaCheckCircle, FaExclamationTriangle, FaTimesCircle, FaQuestionCircle, FaChartLine, FaSearch, FaNewspaper, FaBlog, FaShieldAlt, FaDatabase, FaCheck, FaExclamationCircle } from 'react-icons/fa'

function ConfidenceReport({ analysis }) {
  if (!analysis || !analysis.confidence_score) {
    return null
  }

  const confidenceScore = analysis.confidence_score || 0
  const confidenceLevel = analysis.confidence_level || 'unknown'
  const riskLevel = analysis.risk_assessment?.level || 'unknown'
  
  const getConfidenceColor = (level) => {
    switch (level) {
      case 'high':
        return 'from-green-400 to-emerald-500'
      case 'medium':
        return 'from-yellow-400 to-orange-500'
      case 'low':
        return 'from-orange-400 to-red-500'
      case 'very_low':
        return 'from-red-400 to-red-600'
      default:
        return 'from-gray-400 to-gray-500'
    }
  }

  const getRiskColor = (level) => {
    switch (level) {
      case 'high':
        return 'bg-red-100 text-red-800 border-red-300'
      case 'medium':
        return 'bg-yellow-100 text-yellow-800 border-yellow-300'
      case 'low':
        return 'bg-green-100 text-green-800 border-green-300'
      default:
        return 'bg-gray-100 text-gray-800 border-gray-300'
    }
  }

  const getConfidenceIcon = (level) => {
    switch (level) {
      case 'high':
        return <FaCheckCircle className="text-green-600" />
      case 'medium':
        return <FaExclamationTriangle className="text-yellow-600" />
      case 'low':
        return <FaExclamationCircle className="text-orange-600" />
      case 'very_low':
        return <FaTimesCircle className="text-red-600" />
      default:
        return <FaQuestionCircle className="text-gray-600" />
    }
  }

  return (
    <div className="bg-white rounded-lg shadow-lg p-4 sm:p-6 mb-4 sm:mb-6">
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between mb-4 sm:mb-6">
        <h2 className="text-lg sm:text-xl lg:text-2xl font-bold text-gray-900 mb-2 sm:mb-0">Confidence Report</h2>
        <span className="text-xs sm:text-sm text-gray-500">
          {analysis.analysis_date ? new Date(analysis.analysis_date).toLocaleDateString() : ''}
        </span>
      </div>

      {/* Confidence Score */}
      <div className="mb-6">
        <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between mb-2">
          <span className="text-sm font-medium text-gray-700 mb-2 sm:mb-0">Overall Confidence</span>
          <div className="flex items-center gap-2">
            <span className="text-xl sm:text-2xl">{getConfidenceIcon(confidenceLevel)}</span>
            <span className="text-xl sm:text-2xl font-bold text-gray-900">
              {Math.round(confidenceScore * 100)}%
            </span>
          </div>
        </div>
        <div className="w-full bg-gray-200 rounded-full h-4 mb-2">
          <div
            className={`h-4 rounded-full bg-gradient-to-r ${getConfidenceColor(confidenceLevel)} transition-all duration-500`}
            style={{ width: `${confidenceScore * 100}%` }}
          />
        </div>
        <p className="text-xs text-gray-500 capitalize">
          Confidence Level: <span className="font-semibold">{confidenceLevel.replace('_', ' ')}</span>
        </p>
      </div>

      {/* Risk Assessment */}
      {analysis.risk_assessment && (
        <div className={`mb-6 p-4 rounded-lg border-2 ${getRiskColor(riskLevel)}`}>
          <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between mb-2">
            <div className="flex items-center gap-2 mb-2 sm:mb-0">
              <FaShieldAlt className="text-lg" />
              <span className="font-semibold">Risk Assessment</span>
            </div>
            <span className="text-base sm:text-lg font-bold capitalize">{riskLevel}</span>
          </div>
          <p className="text-sm mt-2">{analysis.risk_assessment.assessment}</p>
          {analysis.risk_assessment.factors && analysis.risk_assessment.factors.length > 0 && (
            <div className="mt-3">
              <p className="text-xs font-medium mb-1">Risk Factors:</p>
              <ul className="list-disc list-inside text-xs space-y-1">
                {analysis.risk_assessment.factors.map((factor, index) => (
                  <li key={index}>{factor}</li>
                ))}
              </ul>
            </div>
          )}
        </div>
      )}

      {/* Key Findings */}
      {analysis.key_findings && analysis.key_findings.length > 0 && (
        <div className="mb-6">
          <h3 className="text-base sm:text-lg font-semibold text-gray-900 mb-3 flex items-center gap-2">
            <FaChartLine />
            Key Findings
          </h3>
          <div className="space-y-2">
            {analysis.key_findings.map((finding, index) => (
              <div key={index} className="p-3 bg-blue-50 rounded-lg border border-blue-200">
                <p className="text-xs sm:text-sm text-gray-800">{finding}</p>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Data Sources */}
      {analysis.data_sources && (
        <div className="mb-6">
          <h3 className="text-base sm:text-lg font-semibold text-gray-900 mb-3 flex items-center gap-2">
            <FaDatabase />
            Data Sources
          </h3>
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-4 mb-3">
            <div className="p-3 bg-gray-50 rounded-lg">
              <p className="text-xs text-gray-500 mb-1">Active Sources</p>
              <p className="text-xl sm:text-2xl font-bold text-gray-900">
                {analysis.data_sources.active_sources || 0}
                <span className="text-sm font-normal text-gray-500">/{analysis.data_sources.total_sources || 0}</span>
              </p>
            </div>
            <div className="p-3 bg-gray-50 rounded-lg">
              <p className="text-xs text-gray-500 mb-1">Coverage</p>
              <p className="text-xl sm:text-2xl font-bold text-gray-900">
                {Math.round(analysis.data_sources.coverage?.percentage || 0)}%
              </p>
              <p className="text-xs text-gray-500 capitalize">
                {analysis.data_sources.coverage?.rating || 'unknown'}
              </p>
            </div>
          </div>
          {analysis.data_sources.source_details && Object.keys(analysis.data_sources.source_details).length > 0 && (
            <div className="mt-3">
              <p className="text-xs font-medium text-gray-700 mb-2">Source Details:</p>
              <div className="grid grid-cols-2 sm:grid-cols-3 gap-2">
                {Object.entries(analysis.data_sources.source_details).slice(0, 9).map(([source, details]) => (
                  <div key={source} className={`p-2 rounded text-xs ${details.has_data ? 'bg-green-100 text-green-800' : 'bg-gray-100 text-gray-600'}`}>
                    <span className="font-medium capitalize">{source.replace('_', ' ')}</span>
                    {details.has_data && (
                      <span className="block text-xs mt-1">{details.data_points} data points</span>
                    )}
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>
      )}

      {/* Consistency & Verification */}
      <div className="grid grid-cols-1 sm:grid-cols-2 gap-4 mb-6">
        {analysis.consistency_score && (
          <div className="p-4 bg-purple-50 rounded-lg border border-purple-200">
            <p className="text-sm font-medium text-gray-700 mb-2">Consistency</p>
            <p className="text-2xl sm:text-3xl font-bold text-purple-600">
              {Math.round(analysis.consistency_score.score * 100)}%
            </p>
            <p className="text-xs text-gray-500 mt-1">
              {analysis.consistency_score.matches || 0} matches found
            </p>
          </div>
        )}
        {analysis.verification_score && (
          <div className="p-4 bg-green-50 rounded-lg border border-green-200">
            <p className="text-sm font-medium text-gray-700 mb-2 flex items-center gap-2">
              <FaCheck className="text-green-600" />
              Verification
            </p>
            <p className="text-2xl sm:text-3xl font-bold text-green-600">
              {Math.round(analysis.verification_score.score * 100)}%
            </p>
            <p className="text-xs text-gray-500 mt-1">
              {analysis.verification_score.verification_sources || 0} verified items
            </p>
          </div>
        )}
      </div>

      {/* Threat Indicators */}
      {analysis.threat_indicators && analysis.threat_indicators.length > 0 && (
        <div className="mb-6">
          <h3 className="text-base sm:text-lg font-semibold text-red-900 mb-3 flex items-center gap-2">
            <FaExclamationCircle className="text-red-600" />
            Threat Indicators
          </h3>
          <div className="space-y-2">
            {analysis.threat_indicators.map((threat, index) => (
              <div
                key={index}
                className={`p-3 rounded-lg border-2 ${
                  threat.severity === 'high'
                    ? 'bg-red-50 border-red-300'
                    : threat.severity === 'medium'
                    ? 'bg-yellow-50 border-yellow-300'
                    : 'bg-orange-50 border-orange-300'
                }`}
              >
                <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between mb-1">
                  <span className="font-semibold text-xs sm:text-sm capitalize mb-1 sm:mb-0">{threat.type}</span>
                  <span className="text-xs px-2 py-1 rounded-full bg-white capitalize self-start sm:self-auto">
                    {threat.severity} severity
                  </span>
                </div>
                <p className="text-xs sm:text-sm text-gray-700">{threat.description}</p>
                <p className="text-xs text-gray-500 mt-1">Source: {threat.source}</p>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Recommendations */}
      {analysis.recommendations && analysis.recommendations.length > 0 && (
        <div className="mb-6">
          <h3 className="text-base sm:text-lg font-semibold text-gray-900 mb-3 flex items-center gap-2">
            <FaChartLine />
            Recommendations
          </h3>
          <div className="space-y-2">
            {analysis.recommendations.map((recommendation, index) => (
              <div key={index} className="p-3 bg-blue-50 rounded-lg border border-blue-200">
                <p className="text-xs sm:text-sm text-gray-800">{recommendation}</p>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Google Analysis */}
      {analysis.google_analysis && analysis.google_analysis.has_data && (
        <div className="mb-6 p-4 bg-blue-50 rounded-lg border border-blue-200">
          <h3 className="text-sm font-semibold text-gray-700 mb-3 flex items-center gap-2">
            <FaSearch className="text-blue-600" />
            Google Search Analysis
          </h3>
          <div className="grid grid-cols-2 gap-3 mb-3">
            <div>
              <p className="text-xs text-gray-500">Search Results</p>
              <p className="text-sm sm:text-base lg:text-lg font-bold text-gray-900">
                {analysis.google_analysis.result_count || 0}
              </p>
            </div>
            <div>
              <p className="text-xs text-gray-500">Relevance Score</p>
              <p className="text-sm sm:text-base lg:text-lg font-bold text-gray-900">
                {Math.round((analysis.google_analysis.relevance_score || 0) * 100)}%
              </p>
            </div>
            {analysis.google_analysis.content_richness !== undefined && (
              <div>
                <p className="text-xs text-gray-500">Content Richness</p>
                <p className="text-sm sm:text-base lg:text-lg font-bold text-gray-900">
                  {Math.round((analysis.google_analysis.content_richness || 0) * 100)}%
                </p>
              </div>
            )}
            {analysis.google_analysis.verification_sources !== undefined && (
              <div>
                <p className="text-xs text-gray-500">Verification Sources</p>
                <p className="text-sm sm:text-base lg:text-lg font-bold text-gray-900">
                  {analysis.google_analysis.verification_sources || 0}
                </p>
              </div>
            )}
          </div>
          <div className="flex flex-wrap gap-2">
            {analysis.google_analysis.ai_summary_available && (
              <span className="inline-flex items-center gap-1 px-2 py-1 bg-green-100 text-green-800 rounded text-xs font-medium">
                <FaCheckCircle className="text-xs" />
                AI Summary Available
              </span>
            )}
            {analysis.google_analysis.knowledge_panel_available && (
              <span className="inline-flex items-center gap-1 px-2 py-1 bg-purple-100 text-purple-800 rounded text-xs font-medium">
                <FaDatabase className="text-xs" />
                Knowledge Panel Available
              </span>
            )}
            {analysis.google_analysis.detailed_description && (
              <span className="inline-flex items-center gap-1 px-2 py-1 bg-blue-100 text-blue-800 rounded text-xs font-medium">
                <FaChartLine className="text-xs" />
                Detailed Description
              </span>
            )}
          </div>
        </div>
      )}

      {/* Blog/Article Analysis */}
      {analysis.blog_analysis && analysis.blog_analysis.has_data && (
        <div className="mb-6 p-4 bg-green-50 rounded-lg border border-green-200">
          <h3 className="text-sm font-semibold text-gray-700 mb-3 flex items-center gap-2">
            <FaBlog className="text-green-600" />
            Blog/Article Analysis
          </h3>
          <div className="grid grid-cols-2 gap-3 mb-3">
            <div>
              <p className="text-xs text-gray-500">Articles Found</p>
              <p className="text-sm sm:text-base lg:text-lg font-bold text-gray-900">
                {analysis.blog_analysis.article_count || 0}
              </p>
            </div>
            <div>
              <p className="text-xs text-gray-500">Relevance Score</p>
              <p className="text-sm sm:text-base lg:text-lg font-bold text-gray-900">
                {Math.round((analysis.blog_analysis.relevance_score || 0) * 100)}%
              </p>
            </div>
            <div>
              <p className="text-xs text-gray-500">Content Quality</p>
              <p className="text-sm sm:text-base lg:text-lg font-bold text-gray-900">
                {Math.round((analysis.blog_analysis.content_quality || 0) * 100)}%
              </p>
            </div>
            <div>
              <p className="text-xs text-gray-500">Verification Matches</p>
              <p className="text-sm sm:text-base lg:text-lg font-bold text-gray-900">
                {analysis.blog_analysis.verification_matches || 0}
              </p>
            </div>
          </div>
          {analysis.blog_analysis.total_content_length > 0 && (
            <p className="text-xs text-gray-600">
              Total content analyzed: {(analysis.blog_analysis.total_content_length / 1000).toFixed(1)}k characters
            </p>
          )}
        </div>
      )}

      {/* News Analysis */}
      {analysis.news_analysis && analysis.news_analysis.has_data && (
        <div className="mb-6 p-4 bg-yellow-50 rounded-lg border border-yellow-200">
          <h3 className="text-sm font-semibold text-gray-700 mb-3 flex items-center gap-2">
            <FaNewspaper className="text-yellow-600" />
            News Article Analysis
          </h3>
          <div className="grid grid-cols-2 gap-3 mb-3">
            <div>
              <p className="text-xs text-gray-500">Total Articles</p>
              <p className="text-sm sm:text-base lg:text-lg font-bold text-gray-900">
                {analysis.news_analysis.total_articles || 0}
              </p>
            </div>
            <div>
              <p className="text-xs text-gray-500">News Sources</p>
              <p className="text-sm sm:text-base lg:text-lg font-bold text-gray-900">
                {analysis.news_analysis.source_count || 0}
              </p>
            </div>
            <div>
              <p className="text-xs text-gray-500">Relevance Score</p>
              <p className="text-sm sm:text-base lg:text-lg font-bold text-gray-900">
                {Math.round((analysis.news_analysis.relevance_score || 0) * 100)}%
              </p>
            </div>
            <div>
              <p className="text-xs text-gray-500">Recent Articles</p>
              <p className="text-sm sm:text-base lg:text-lg font-bold text-gray-900">
                {analysis.news_analysis.recent_articles || 0}
              </p>
            </div>
          </div>
        </div>
      )}

      {/* Data Quality */}
      {analysis.data_quality && (
        <div className="p-4 bg-gray-50 rounded-lg">
          <h3 className="text-sm font-semibold text-gray-700 mb-2 flex items-center gap-2">
            <FaChartLine />
            Data Quality
          </h3>
          <div className="grid grid-cols-3 gap-2 text-center">
            <div>
              <p className="text-xs text-gray-500">Completeness</p>
              <p className="text-sm sm:text-base lg:text-lg font-bold text-gray-900">
                {Math.round((analysis.data_quality.completeness || 0) * 100)}%
              </p>
            </div>
            <div>
              <p className="text-xs text-gray-500">Accuracy</p>
              <p className="text-sm sm:text-base lg:text-lg font-bold text-gray-900">
                {Math.round((analysis.data_quality.accuracy || 0) * 100)}%
              </p>
            </div>
            <div>
              <p className="text-xs text-gray-500">Relevance</p>
              <p className="text-sm sm:text-base lg:text-lg font-bold text-gray-900">
                {Math.round((analysis.data_quality.relevance || 0) * 100)}%
              </p>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}

export default ConfidenceReport

