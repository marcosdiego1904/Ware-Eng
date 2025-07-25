"use client"

import { useMemo } from 'react'
import { ReportDetails } from '@/lib/reports'

interface AnomalyTrendsChartProps {
  reportData: ReportDetails
}

export function AnomalyTrendsChart({ reportData }: AnomalyTrendsChartProps) {
  const trendData = useMemo(() => {
    if (!reportData.locations) return null

    // Get all anomalies with their types and priorities
    const allAnomalies = reportData.locations.flatMap(location => 
      location.anomalies.map(anomaly => ({
        ...anomaly,
        location: location.name
      }))
    )

    // Group by anomaly type
    const anomalyTypes = allAnomalies.reduce((acc, anomaly) => {
      const type = anomaly.anomaly_type || 'Unknown'
      if (!acc[type]) {
        acc[type] = { count: 0, priorities: { 'VERY HIGH': 0, 'HIGH': 0, 'MEDIUM': 0, 'LOW': 0 } }
      }
      acc[type].count++
      acc[type].priorities[anomaly.priority]++
      return acc
    }, {} as Record<string, { count: number; priorities: Record<string, number> }>)

    // Group by priority
    const priorityDistribution = allAnomalies.reduce((acc, anomaly) => {
      acc[anomaly.priority] = (acc[anomaly.priority] || 0) + 1
      return acc
    }, {} as Record<string, number>)

    // Group by status
    const statusDistribution = allAnomalies.reduce((acc, anomaly) => {
      acc[anomaly.status] = (acc[anomaly.status] || 0) + 1
      return acc
    }, {} as Record<string, number>)

    return {
      anomalyTypes,
      priorityDistribution,
      statusDistribution,
      totalAnomalies: allAnomalies.length
    }
  }, [reportData])

  if (!trendData) {
    return (
      <div className="text-center py-8">
        <div className="text-gray-400 mb-2">📈</div>
        <p className="text-gray-600">No trend data available</p>
      </div>
    )
  }

  const getPriorityColor = (priority: string) => {
    switch (priority) {
      case 'VERY HIGH': return 'bg-red-500'
      case 'HIGH': return 'bg-orange-500'
      case 'MEDIUM': return 'bg-yellow-500'
      case 'LOW': return 'bg-green-500'
      default: return 'bg-gray-500'
    }
  }

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'New': return 'bg-blue-500'
      case 'Acknowledged': return 'bg-yellow-500'
      case 'In Progress': return 'bg-orange-500'
      case 'Resolved': return 'bg-green-500'
      default: return 'bg-gray-500'
    }
  }

  return (
    <div className="space-y-8">
      {/* Anomaly Types Breakdown */}
      <div>
        <h4 className="font-semibold mb-4">Anomaly Types Distribution</h4>
        <div className="space-y-3">
          {Object.entries(trendData.anomalyTypes)
            .sort(([,a], [,b]) => b.count - a.count)
            .map(([type, data]) => {
              const percentage = (data.count / trendData.totalAnomalies) * 100
              return (
                <div key={type} className="space-y-2">
                  <div className="flex justify-between items-center">
                    <span className="font-medium text-sm">{type}</span>
                    <div className="text-right">
                      <span className="font-semibold">{data.count}</span>
                      <span className="text-gray-500 text-xs ml-1">({percentage.toFixed(1)}%)</span>
                    </div>
                  </div>
                  <div className="relative h-4 bg-gray-100 rounded-full overflow-hidden">
                    <div 
                      className="h-full bg-blue-500 transition-all duration-500"
                      style={{ width: `${percentage}%` }}
                    />
                  </div>
                  
                  {/* Priority breakdown for this type */}
                  <div className="flex gap-1 ml-4">
                    {Object.entries(data.priorities).map(([priority, count]) => {
                      if (count === 0) return null
                      const priorityPercentage = (count / data.count) * 100
                      return (
                        <div 
                          key={priority}
                          className={`h-1 rounded ${getPriorityColor(priority)}`}
                          style={{ width: `${priorityPercentage}%` }}
                          title={`${priority}: ${count}`}
                        />
                      )
                    })}
                  </div>
                </div>
              )
            })
          }
        </div>
      </div>

      {/* Priority Distribution Pie Chart (Visual Representation) */}
      <div>
        <h4 className="font-semibold mb-4">Priority Distribution</h4>
        <div className="grid grid-cols-2 gap-6">
          <div className="space-y-3">
            {Object.entries(trendData.priorityDistribution)
              .sort(([,a], [,b]) => b - a)
              .map(([priority, count]) => {
                const percentage = (count / trendData.totalAnomalies) * 100
                return (
                  <div key={priority} className="flex items-center gap-3">
                    <div className={`w-4 h-4 rounded ${getPriorityColor(priority)}`} />
                    <span className="flex-1">{priority}</span>
                    <div className="text-right">
                      <span className="font-semibold">{count}</span>
                      <span className="text-gray-500 text-xs ml-1">({percentage.toFixed(1)}%)</span>
                    </div>
                  </div>
                )
              })
            }
          </div>
          
          {/* Visual Ring Chart */}
          <div className="flex items-center justify-center">
            <div className="relative w-32 h-32">
              <svg viewBox="0 0 42 42" className="w-full h-full transform -rotate-90">
                <circle
                  cx="21" cy="21" r="15.915"
                  fill="transparent"
                  stroke="#e5e5e5"
                  strokeWidth="3"
                />
                {(() => {
                  let offset = 0
                  return Object.entries(trendData.priorityDistribution).map(([priority, count]) => {
                    const percentage = (count / trendData.totalAnomalies) * 100
                    const strokeDasharray = `${percentage} ${100 - percentage}`
                    const strokeDashoffset = -offset
                    offset += percentage
                    
                    const color = priority === 'VERY HIGH' ? '#ef4444' :
                                 priority === 'HIGH' ? '#f97316' :
                                 priority === 'MEDIUM' ? '#eab308' :
                                 priority === 'LOW' ? '#22c55e' : '#6b7280'
                    
                    if (count === 0) return null
                    
                    return (
                      <circle
                        key={priority}
                        cx="21" cy="21" r="15.915"
                        fill="transparent"
                        stroke={color}
                        strokeWidth="3"
                        strokeDasharray={strokeDasharray}
                        strokeDashoffset={strokeDashoffset}
                        className="transition-all duration-500"
                      />
                    )
                  })
                })()}
              </svg>
              <div className="absolute inset-0 flex items-center justify-center">
                <div className="text-center">
                  <div className="text-lg font-bold">{trendData.totalAnomalies}</div>
                  <div className="text-xs text-gray-500">Total</div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Status Distribution */}
      <div>
        <h4 className="font-semibold mb-4">Status Distribution</h4>
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
          {Object.entries(trendData.statusDistribution).map(([status, count]) => {
            const percentage = (count / trendData.totalAnomalies) * 100
            return (
              <div key={status} className="text-center p-4 border rounded-lg">
                <div className={`w-8 h-8 rounded-full ${getStatusColor(status)} mx-auto mb-2`} />
                <div className="font-semibold text-lg">{count}</div>
                <div className="text-sm text-gray-600">{status}</div>
                <div className="text-xs text-gray-500">{percentage.toFixed(1)}%</div>
              </div>
            )
          })}
        </div>
      </div>

      {/* Insights */}
      <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
        <h4 className="font-semibold mb-2 text-blue-900">Key Insights</h4>
        <div className="space-y-2 text-sm text-blue-800">
          {(() => {
            const insights = []
            
            // Most common anomaly type
            const mostCommonType = Object.entries(trendData.anomalyTypes)
              .sort(([,a], [,b]) => b.count - a.count)[0]
            if (mostCommonType) {
              insights.push(`Most common issue: ${mostCommonType[0]} (${mostCommonType[1].count} cases)`)
            }
            
            // Priority analysis
            const highPriorityCount = (trendData.priorityDistribution['VERY HIGH'] || 0) + (trendData.priorityDistribution['HIGH'] || 0)
            const highPriorityPercentage = (highPriorityCount / trendData.totalAnomalies) * 100
            insights.push(`${highPriorityPercentage.toFixed(1)}% of anomalies are high priority`)
            
            // Resolution rate
            const resolvedCount = trendData.statusDistribution['Resolved'] || 0
            const resolutionRate = (resolvedCount / trendData.totalAnomalies) * 100
            insights.push(`${resolutionRate.toFixed(1)}% resolution rate`)
            
            return insights.map((insight, index) => (
              <div key={index} className="flex items-center gap-2">
                <div className="w-1.5 h-1.5 bg-blue-600 rounded-full" />
                <span>{insight}</span>
              </div>
            ))
          })()}
        </div>
      </div>
    </div>
  )
}