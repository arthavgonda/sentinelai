import React, { useState, useMemo } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import TwitterResults from './results/TwitterResults'
import InstagramResults from './results/InstagramResults'
import GitHubResults from './results/GitHubResults'
import HunterResults from './results/HunterResults'
import NewsResults from './results/NewsResults'
import NumverifyResults from './results/NumverifyResults'
import RedditResults from './results/RedditResults'
import BlogResults from './results/BlogResults'
import GoogleSearchResults from './results/GoogleSearchResults'
import OtherResults from './results/OtherResults'

const API_COMPONENTS = {
  twitter: TwitterResults,
  instagram: InstagramResults,
  instagram_scraper: InstagramResults,
  github: GitHubResults,
  hunter: HunterResults,
  newsapi: NewsResults,
  googlenews: NewsResults,
  google_search: GoogleSearchResults,
  numverify: NumverifyResults,
  virustotal: OtherResults,
  etherscan: OtherResults,
  telegram: OtherResults,
  reddit: RedditResults,
  web_scraper: BlogResults,
  ipinfo: OtherResults
}

function APIResults({ results }) {
  const [expanded, setExpanded] = useState(new Set(Object.keys(results).slice(0, 3)))
  const [filter, setFilter] = useState('all')

  const filteredResults = useMemo(() => {
    if (filter === 'all') return results
    return Object.fromEntries(
      Object.entries(results).filter(([key]) => key === filter)
    )
  }, [results, filter])

  const toggleExpanded = (key) => {
    setExpanded(prev => {
      const newSet = new Set(prev)
      if (newSet.has(key)) {
        newSet.delete(key)
      } else {
        newSet.add(key)
      }
      return newSet
    })
  }

  return (
    <div className="bg-white rounded-lg shadow">
      <div className="p-3 sm:p-4 border-b">
        <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-2 sm:gap-0">
          <h2 className="text-base sm:text-lg font-semibold">API Results</h2>
          <select
            value={filter}
            onChange={(e) => setFilter(e.target.value)}
            className="px-2 sm:px-3 py-1 border border-gray-300 rounded-md text-xs sm:text-sm"
          >
            <option value="all">All APIs</option>
            {Object.keys(results).map(key => (
              <option key={key} value={key}>{key.replace('_', ' ')}</option>
            ))}
          </select>
        </div>
      </div>
      <div className="divide-y">
        {Object.entries(filteredResults).map(([apiName, data]) => {
          const Component = API_COMPONENTS[apiName] || OtherResults
          const isExpanded = expanded.has(apiName)
          
          return (
        <div key={apiName} className="p-3 sm:p-4 hover:bg-gray-50 transition-colors">
            <button
                onClick={() => toggleExpanded(apiName)}
                className="w-full flex items-center justify-between text-left group"
            >
                <div className="flex items-center gap-2 sm:gap-3 flex-1 min-w-0">
                    <span className="font-semibold capitalize text-gray-900 group-hover:text-primary-600 transition-colors text-sm sm:text-base truncate">{apiName.replace('_', ' ')}</span>
                    {data && (
                        <span className="px-2 py-0.5 bg-green-100 text-green-800 text-xs font-medium rounded-full flex-shrink-0">
                            Data
                        </span>
                    )}
                </div>
                <span className="text-gray-400 group-hover:text-gray-600 transition-colors flex-shrink-0 ml-2">
                    {isExpanded ? '▼' : '▶'}
                </span>
            </button>
              <AnimatePresence>
                {isExpanded && (
                  <motion.div
                    initial={{ opacity: 0, height: 0 }}
                    animate={{ opacity: 1, height: 'auto' }}
                    exit={{ opacity: 0, height: 0 }}
                    transition={{ duration: 0.2 }}
                  >
                    <div className="mt-4">
                      <Component data={data} />
                    </div>
                  </motion.div>
                )}
              </AnimatePresence>
            </div>
          )
        })}
      </div>
    </div>
  )
}

export default APIResults

