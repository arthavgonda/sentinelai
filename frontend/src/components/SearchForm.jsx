import React, { useState } from 'react'

function SearchForm({ onSubmit, loading, error }) {
  const [query, setQuery] = useState('')
  const [queryType, setQueryType] = useState('auto')

  const handleSubmit = (e) => {
    e.preventDefault()
    if (query.trim()) {
      onSubmit(query.trim(), queryType === 'auto' ? null : queryType)
    }
  }

  const detectType = (value) => {
    if (value.includes('@')) return 'email'
    if (/^\+?[\d\s-]+$/.test(value) && value.replace(/\D/g, '').length >= 10) return 'phone'
    if (/\s/.test(value) && /^[a-zA-Z\s\-\'\.]+$/.test(value)) return 'name'
    return 'username'
  }

  return (
    <form onSubmit={handleSubmit} className="space-y-4">
      <div>
        <label className="block text-xs sm:text-sm font-medium text-gray-700 mb-2">
          Search Query
        </label>
        <div className="flex flex-col sm:flex-row gap-2">
          <input
            type="text"
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            placeholder="Enter name, email, username, or phone number"
            className="flex-1 px-3 sm:px-4 py-2 border border-gray-300 rounded-md focus:ring-primary-500 focus:border-primary-500 text-sm sm:text-base"
            disabled={loading}
          />
          <select
            value={queryType}
            onChange={(e) => setQueryType(e.target.value)}
            className="px-3 sm:px-4 py-2 border border-gray-300 rounded-md focus:ring-primary-500 focus:border-primary-500 text-sm sm:text-base"
            disabled={loading}
          >
            <option value="auto">Auto-detect</option>
            <option value="name">Name</option>
            <option value="email">Email</option>
            <option value="username">Username</option>
            <option value="phone">Phone</option>
          </select>
          <button
            type="submit"
            disabled={loading || !query.trim()}
            className="px-4 sm:px-6 py-2 bg-primary-600 text-white rounded-md hover:bg-primary-700 disabled:bg-gray-400 disabled:cursor-not-allowed text-sm sm:text-base whitespace-nowrap"
          >
            {loading ? 'Searching...' : 'Search'}
          </button>
        </div>
        {query && queryType === 'auto' && (
          <p className="mt-2 text-xs sm:text-sm text-gray-500">
            Detected type: {detectType(query)}
          </p>
        )}
      </div>
      {error && (
        <div className="p-2 sm:p-3 bg-red-50 border border-red-200 rounded-md text-red-700 text-xs sm:text-sm">
          {error}
        </div>
      )}
    </form>
  )
}

export default SearchForm

