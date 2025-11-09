import React from 'react'
import { format } from 'date-fns'
import { FaNewspaper, FaCalendarAlt } from 'react-icons/fa'

function NewsResults({ data }) {
  if (!data) return <p className="text-gray-500 text-sm">No data available</p>

  const articles = data.articles || data.items || []

  return (
    <div className="space-y-4">
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between p-3 bg-gradient-to-r from-green-50 to-emerald-50 rounded-lg border-2 border-green-200 gap-2">
        <div className="flex items-center gap-2">
          <FaNewspaper className="text-green-600 text-xl sm:text-2xl" />
          <p className="font-semibold text-gray-900 text-sm sm:text-base">Found {articles.length} articles</p>
        </div>
        <span className="px-2 sm:px-3 py-1 bg-green-100 text-green-800 rounded-full text-xs font-medium">
          {articles.length} results
        </span>
      </div>
      <div className="space-y-3 max-h-96 overflow-y-auto">
        {articles.slice(0, 10).map((article, index) => (
          <a
            key={index}
            href={article.url || article.link}
            target="_blank"
            rel="noopener noreferrer"
            className="block p-4 bg-white rounded-lg border border-gray-200 hover:border-green-300 hover:shadow-lg transition-all group"
          >
            <h4 className="font-semibold text-gray-900 group-hover:text-green-600 mb-2 line-clamp-2">
              {article.title}
            </h4>
            {article.description && (
              <p className="text-sm text-gray-600 mb-3 line-clamp-2">
                {article.description}
              </p>
            )}
            <div className="flex items-center gap-3 text-xs text-gray-500">
              {article.publishedAt && (
                <span className="flex items-center gap-1">
                  <FaCalendarAlt className="text-xs" />
                  {format(new Date(article.publishedAt), 'PP')}
                </span>
              )}
              {article.source && (
                <>
                  <span>•</span>
                  <span> source: {article.source.name || article.source}</span>
                </>
              )}
            </div>
          </a>
        ))}
      </div>
    </div>
  )
}

export default NewsResults

