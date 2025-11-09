import React from 'react'
import Skeleton from 'react-loading-skeleton'
import 'react-loading-skeleton/dist/skeleton.css'

function LoadingSkeleton() {
  return (
    <div className="space-y-6">
      <Skeleton height={80} />
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <div className="lg:col-span-2 space-y-4">
          <Skeleton height={200} />
          <Skeleton height={200} />
          <Skeleton height={200} />
        </div>
        <div>
          <Skeleton height={300} />
        </div>
      </div>
    </div>
  )
}

export default LoadingSkeleton

