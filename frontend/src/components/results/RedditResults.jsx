import React from 'react'
import { format } from 'date-fns'
import { FaReddit, FaStar } from 'react-icons/fa'

function RedditResults({ data }) {
  if (!data) return <p className="text-gray-500 text-sm">No data available</p>

  if (data.username) {
    return (
      <div className="space-y-4">
        <div className="p-4 bg-gradient-to-r from-orange-50 to-red-50 rounded-lg border-2 border-orange-200">
          <div className="flex items-center gap-3 mb-4">
            <FaReddit className="text-orange-600 text-2xl sm:text-3xl" />
            <div>
              <h3 className="text-lg sm:text-xl font-bold text-gray-900">u/{data.username}</h3>
              <p className="text-sm text-gray-600">
                Account created: {data.created_utc ? format(new Date(data.created_utc * 1000), 'PP') : 'Unknown'}
              </p>
            </div>
          </div>

          <div className="grid grid-cols-2 gap-4">
            <div className="p-3 bg-white rounded-lg border border-gray-200">
              <p className="text-xs text-gray-500">Comment Karma</p>
              <p className="text-2xl font-bold text-gray-900">{data.comment_karma?.toLocaleString() || 0}</p>
            </div>
            <div className="p-3 bg-white rounded-lg border border-gray-200">
              <p className="text-xs text-gray-500">Post Karma</p>
              <p className="text-2xl font-bold text-gray-900">{data.link_karma?.toLocaleString() || 0}</p>
            </div>
          </div>
        </div>

        {data.submissions && data.submissions.length > 0 && (
          <div>
            <h4 className="font-semibold text-gray-900 mb-3">Recent Posts</h4>
            <div className="space-y-2">
              {data.submissions.slice(0, 5).map((submission, index) => (
                <a
                  key={index}
                  href={submission.url}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="block p-3 bg-white rounded-lg border border-gray-200 hover:border-orange-300 hover:shadow-md transition-all"
                >
                  <p className="font-medium text-gray-900 mb-1">{submission.title}</p>
                  <div className="flex items-center gap-3 text-xs text-gray-500">
                    <span className="flex items-center gap-1">
                      <FaStar className="text-xs" />
                      {submission.score} points
                    </span>
                    <span>•</span>
                    <span>{format(new Date(submission.created_utc * 1000), 'PP')}</span>
                  </div>
                </a>
              ))}
            </div>
          </div>
        )}
      </div>
    )
  }

  if (data.posts_found || data.subreddits_found) {
    return (
      <div className="space-y-4">
        {data.subreddits_found && data.subreddits_found.length > 0 && (
          <div>
            <h4 className="font-semibold text-gray-900 mb-3">Related Subreddits</h4>
            <div className="grid grid-cols-2 gap-2">
              {data.subreddits_found.map((sub, index) => (
                <div key={index} className="p-3 bg-orange-50 rounded-lg border border-orange-200">
                  <p className="font-medium text-gray-900">r/{sub.name}</p>
                  <p className="text-xs text-gray-600">{sub.subscribers?.toLocaleString()} members</p>
                </div>
              ))}
            </div>
          </div>
        )}

        {data.posts_found && data.posts_found.length > 0 && (
          <div>
            <h4 className="font-semibold text-gray-900 mb-3">Related Posts</h4>
            <div className="space-y-2 max-h-96 overflow-y-auto">
              {data.posts_found.map((post, index) => (
                <a
                  key={index}
                  href={post.url}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="block p-3 bg-white rounded-lg border border-gray-200 hover:border-orange-300 hover:shadow-md transition-all"
                >
                  <p className="font-medium text-gray-900 mb-1">{post.title}</p>
                  <div className="flex items-center gap-3 text-xs text-gray-500">
                    <span>r/{post.subreddit}</span>
                    <span>•</span>
                    <span className="flex items-center gap-1">
                      <FaStar className="text-xs" />
                      {post.score} points
                    </span>
                  </div>
                </a>
              ))}
            </div>
          </div>
        )}
      </div>
    )
  }

  return (
    <div className="p-4 bg-gray-50 rounded-lg">
      <pre className="text-xs overflow-auto">{JSON.stringify(data, null, 2)}</pre>
    </div>
  )
}

export default RedditResults

