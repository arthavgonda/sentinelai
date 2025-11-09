import React, { useState } from 'react'
import { FaImage, FaUser, FaCheckCircle } from 'react-icons/fa'

function ProfileImage({ images = [], primaryImage = null }) {
  const [selectedImage, setSelectedImage] = useState(primaryImage || (images.length > 0 ? images[0] : null))
  const [imageError, setImageError] = useState(false)

  if (!selectedImage && images.length === 0) {
    return null
  }

  const displayImage = selectedImage || images[0]
  const imageUrl = displayImage?.url || displayImage

  if (!imageUrl) {
    return null
  }

  return (
    <div className="bg-white rounded-lg shadow-lg p-4 sm:p-6 mb-6">
      <h2 className="text-xl sm:text-2xl font-bold text-gray-900 mb-4 flex items-center gap-2">
        <FaImage className="text-blue-600" />
        Profile Photo
      </h2>
      
      <div className="flex flex-col md:flex-row gap-4 sm:gap-6">
        {/* Main Image Display */}
        <div className="flex-1">
          <div className="relative bg-gray-100 rounded-lg overflow-hidden" style={{ minHeight: '200px', maxHeight: '500px' }}>
            {!imageError ? (
              <img
                src={imageUrl}
                alt={displayImage?.alt || "Profile photo"}
                className="w-full h-full object-contain"
                onError={() => setImageError(true)}
                onLoad={() => setImageError(false)}
              />
            ) : (
              <div className="flex items-center justify-center h-full text-gray-400">
                <div className="text-center">
                  <FaImage className="text-4xl mx-auto mb-2" />
                  <span className="text-sm">Image unavailable</span>
                </div>
              </div>
            )}
            
            {displayImage?.source && (
              <div className="absolute top-2 right-2 bg-black bg-opacity-60 text-white text-xs px-2 sm:px-3 py-1 rounded-full">
                Source: {displayImage.source.replace('_', ' ')}
              </div>
            )}
            
            {displayImage?.analysis && (
              <div className="absolute bottom-2 left-2 bg-black bg-opacity-60 text-white text-xs px-2 sm:px-3 py-1 rounded flex items-center gap-1">
                {displayImage.analysis.has_person ? (
                  <>
                    <FaCheckCircle className="text-green-400" />
                    <span>Person detected</span>
                  </>
                ) : (
                  <span>No person detected</span>
                )}
              </div>
            )}
          </div>
          
          {displayImage?.analysis && displayImage.analysis.labels && displayImage.analysis.labels.length > 0 && (
            <div className="mt-3">
              <p className="text-xs text-gray-500 mb-1">Detected Labels:</p>
              <div className="flex flex-wrap gap-2">
                {displayImage.analysis.labels.slice(0, 5).map((label, index) => (
                  <span key={index} className="px-2 py-1 bg-blue-100 text-blue-800 text-xs rounded">
                    {label.description}
                  </span>
                ))}
              </div>
            </div>
          )}
        </div>

        {/* Thumbnail Gallery */}
        {images.length > 1 && (
          <div className="w-full md:w-32 lg:w-40">
            <p className="text-xs sm:text-sm font-medium text-gray-700 mb-2">Other Images</p>
            <div className="grid grid-cols-2 md:grid-cols-1 gap-2">
              {images.slice(0, 4).map((img, index) => {
                const imgUrl = img?.url || img
                return (
                  <div
                    key={index}
                    onClick={() => {
                      setSelectedImage(img)
                      setImageError(false)
                    }}
                    className={`cursor-pointer rounded-lg overflow-hidden border-2 transition-all ${
                      selectedImage === img ? 'border-blue-500 ring-2 ring-blue-200' : 'border-gray-200 hover:border-blue-300'
                    }`}
                  >
                    <img
                      src={imgUrl}
                      alt={img?.alt || `Image ${index + 1}`}
                      className="w-full h-20 sm:h-24 object-cover"
                      onError={(e) => {
                        e.target.style.display = 'none'
                      }}
                    />
                  </div>
                )
              })}
            </div>
          </div>
        )}
      </div>

      {/* Image Analysis Details */}
      {displayImage?.analysis && (
        <div className="mt-4 p-3 sm:p-4 bg-gray-50 rounded-lg">
          <h3 className="text-xs sm:text-sm font-semibold text-gray-700 mb-2 flex items-center gap-2">
            <FaUser />
            Image Analysis
          </h3>
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-3 sm:gap-4 text-xs sm:text-sm">
            {displayImage.analysis.faces && displayImage.analysis.faces.length > 0 && (
              <div>
                <p className="text-gray-600">Faces detected: {displayImage.analysis.faces.length}</p>
                {displayImage.analysis.faces[0].confidence && (
                  <p className="text-xs text-gray-500">
                    Confidence: {Math.round(displayImage.analysis.faces[0].confidence * 100)}%
                  </p>
                )}
              </div>
            )}
            {displayImage.analysis.safe_search && (
              <div>
                <p className="text-gray-600">Content Safety:</p>
                <p className="text-xs text-gray-500">
                  Adult: {displayImage.analysis.safe_search.adult || 'Unknown'}
                </p>
              </div>
            )}
          </div>
        </div>
      )}
    </div>
  )
}

export default ProfileImage

