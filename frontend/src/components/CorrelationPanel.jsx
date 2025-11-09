import React from 'react'
import { PieChart, Pie, Cell, ResponsiveContainer, Legend, Tooltip } from 'recharts'

const COLORS = ['#0088FE', '#00C49F', '#FFBB28', '#FF8042', '#8884d8', '#82ca9d']

function CorrelationPanel({ correlation }) {
  const clusters = correlation.clusters || []
  const confidenceScores = correlation.confidence_scores || {}

  const chartData = Object.entries(confidenceScores).map(([name, value]) => ({
    name,
    value: Math.round(value * 100)
  }))

  return (
    <div className="bg-white rounded-lg shadow p-4 sm:p-6 space-y-4 sm:space-y-6">
      <h2 className="text-base sm:text-lg font-semibold">Correlation Analysis</h2>
      
      <div>
        <h3 className="text-xs sm:text-sm font-medium text-gray-700 mb-2">Confidence Scores</h3>
        {chartData.length > 0 ? (
          <ResponsiveContainer width="100%" height={180}>
            <PieChart>
              <Pie
                data={chartData}
                cx="50%"
                cy="50%"
                labelLine={false}
                label={({ name, percent }) => `${name}: ${(percent * 100).toFixed(0)}%`}
                outerRadius={60}
                fill="#8884d8"
                dataKey="value"
              >
                {chartData.map((entry, index) => (
                  <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                ))}
              </Pie>
              <Tooltip />
            </PieChart>
          </ResponsiveContainer>
        ) : (
          <p className="text-xs sm:text-sm text-gray-500">No correlation data available</p>
        )}
      </div>

      <div>
        <h3 className="text-xs sm:text-sm font-medium text-gray-700 mb-2">Clusters</h3>
        <div className="space-y-2">
          {clusters.slice(0, 5).map((cluster, index) => (
            <div key={index} className="p-2 bg-gray-50 rounded">
              <div className="flex items-center justify-between">
                <span className="text-xs sm:text-sm font-medium capitalize">{cluster.type}</span>
                <span className="text-xs text-gray-500">
                  {Math.round(cluster.confidence * 100)}%
                </span>
              </div>
              <p className="text-xs text-gray-600 mt-1">
                {cluster.source_count} sources
              </p>
            </div>
          ))}
        </div>
      </div>

      <div className="pt-3 sm:pt-4 border-t">
        <div className="flex items-center justify-between text-xs sm:text-sm">
          <span className="text-gray-600">Total Connections</span>
          <span className="font-medium">{correlation.total_connections || 0}</span>
        </div>
        <div className="flex items-center justify-between text-xs sm:text-sm mt-2">
          <span className="text-gray-600">High Confidence</span>
          <span className="font-medium">
            {correlation.high_confidence_matches?.length || 0}
          </span>
        </div>
      </div>
    </div>
  )
}

export default CorrelationPanel

