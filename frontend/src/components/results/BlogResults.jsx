import React from 'react'
import { FaBlog, FaImage, FaCheckCircle } from 'react-icons/fa'

function BlogResults({ data }) {
  if (!data) return <p className="text-gray-500 text-sm">No data available</p>

  const blogs = data.blogs || []
  const totalImages = data.total_images || 0

  return (
    <div className="space-y-4">
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between p-3 bg-gradient-to-r from-purple-50 to-pink-50 rounded-lg border-2 border-purple-200 gap-2">
        <div className="flex items-center gap-2">
          <FaBlog className="text-purple-600 text-xl sm:text-2xl" />
          <p className="font-semibold text-gray-900 text-sm sm:text-base">Found {blogs.length} blog articles</p>
        </div>
        <span className="px-2 sm:px-3 py-1 bg-purple-100 text-purple-800 rounded-full text-xs font-medium flex items-center gap-1">
          <FaImage className="text-xs" />
          {totalImages} images extracted
        </span>
      </div>

      <div className="space-y-3 max-h-96 overflow-y-auto">
        {blogs.map((blog, index) => (
          <div key={index} className="p-3 sm:p-4 bg-white rounded-lg border border-gray-200 hover:border-purple-300 hover:shadow-md transition-all">
            <div className="flex items-start justify-between mb-2">
              <a
                href={blog.url}
                target="_blank"
                rel="noopener noreferrer"
                className="font-semibold text-gray-900 hover:text-purple-600 line-clamp-2 flex-1 text-sm sm:text-base"
              >
                {blog.title}
              </a>
            </div>
            
            {blog.content && (
              <p className="text-xs sm:text-sm text-gray-600 mb-3 line-clamp-3">
                {blog.content}
              </p>
            )}
            
            {blog.matches && blog.matches.length > 0 && (
              <div className="mb-3">
                <p className="text-xs font-medium text-gray-500 mb-1 flex items-center gap-1">
                  <FaCheckCircle className="text-purple-600 text-xs" />
                  Matching Context:
                </p>
                <div className="space-y-1">
                  {blog.matches.slice(0, 2).map((match, i) => (
                    <p key={i} className="text-xs text-gray-700 bg-gray-50 p-2 rounded">
                      ...{match}...
                    </p>
                  ))}
                </div>
              </div>
            )}
            
            {blog.images && blog.images.length > 0 && (
              <div className="mt-3">
                <p className="text-xs font-medium text-gray-500 mb-2 flex items-center gap-1">
                  <FaImage className="text-purple-600 text-xs" />
                  {blog.images.length} images found
                </p>
                <div className="grid grid-cols-2 sm:grid-cols-4 gap-2">
                  {blog.images.slice(0, 4).map((img, imgIndex) => (
                    <img
                      key={imgIndex}
                      src={img.url || img}
                      alt={img.alt || 'Blog image'}
                      className="w-full h-16 sm:h-20 object-cover rounded border border-gray-200 hover:border-purple-300 transition-colors"
                      onError={(e) => {
                        e.target.style.display = 'none'
                      }}
                    />
                  ))}
                </div>
              </div>
            )}
            
            <a
              href={blog.url}
              target="_blank"
              rel="noopener noreferrer"
              className="text-xs text-purple-600 hover:text-purple-800 font-medium mt-2 inline-block"
            >
              Read Article →
            </a>
          </div>
        ))}
      </div>
    </div>
  )
}

export default BlogResults

