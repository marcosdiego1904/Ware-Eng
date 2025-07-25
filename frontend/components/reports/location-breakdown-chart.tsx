"use client"

import { useMemo } from 'react'
import { LocationSummary } from '@/lib/reports'

interface LocationBreakdownChartProps {
  locations: LocationSummary[]
}

export function LocationBreakdownChart({ locations }: LocationBreakdownChartProps) {
  const chartData = useMemo(() => {
    const sortedLocations = [...locations]
      .sort((a, b) => b.anomaly_count - a.anomaly_count)
      .slice(0, 10) // Show top 10 locations
    
    const maxCount = Math.max(...sortedLocations.map(l => l.anomaly_count), 1)
    
    return sortedLocations.map(location => ({
      ...location,
      percentage: (location.anomaly_count / maxCount) * 100
    }))
  }, [locations])

  const getBarColor = (count: number) => {
    if (count === 0) return 'bg-gray-200'
    if (count <= 2) return 'bg-green-400'
    if (count <= 5) return 'bg-yellow-400'
    if (count <= 10) return 'bg-orange-400'
    return 'bg-red-400'
  }

  const getTextColor = (count: number) => {
    if (count === 0) return 'text-gray-600'
    if (count <= 2) return 'text-green-700'
    if (count <= 5) return 'text-yellow-700'
    if (count <= 10) return 'text-orange-700'
    return 'text-red-700'
  }

  if (locations.length === 0) {
    return (
      <div className="text-center py-8">
        <div className="text-gray-400 mb-2">📊</div>
        <p className="text-gray-600">No location data available</p>
      </div>
    )
  }

  return (
    <div className="space-y-4">
      {/* Chart Legend */}
      <div className="flex flex-wrap gap-4 text-sm">
        <div className="flex items-center gap-2">
          <div className="w-3 h-3 bg-green-400 rounded"></div>
          <span>1-2 issues</span>
        </div>
        <div className="flex items-center gap-2">
          <div className="w-3 h-3 bg-yellow-400 rounded"></div>
          <span>3-5 issues</span>
        </div>
        <div className="flex items-center gap-2">
          <div className="w-3 h-3 bg-orange-400 rounded"></div>
          <span>6-10 issues</span>
        </div>
        <div className="flex items-center gap-2">
          <div className="w-3 h-3 bg-red-400 rounded"></div>
          <span>10+ issues</span>
        </div>
      </div>

      {/* Horizontal Bar Chart */}
      <div className="space-y-3">
        {chartData.map((location, index) => (
          <div key={location.name} className="space-y-1">
            <div className="flex justify-between items-center text-sm">
              <span className="font-medium truncate flex-1 pr-2">
                {location.name}
              </span>
              <span className={`font-semibold ${getTextColor(location.anomaly_count)}`}>
                {location.anomaly_count}
              </span>
            </div>
            <div className="relative h-6 bg-gray-100 rounded-full overflow-hidden">
              <div 
                className={`h-full transition-all duration-500 ${getBarColor(location.anomaly_count)}`}
                style={{ width: `${Math.max(location.percentage, 5)}%` }}
              />
              {location.anomaly_count > 0 && (
                <div className="absolute inset-0 flex items-center justify-center text-xs font-medium text-white mix-blend-difference">
                  {location.anomaly_count > 0 && location.percentage > 20 ? `${location.anomaly_count} issues` : ''}
                </div>
              )}
            </div>
          </div>
        ))}
      </div>

      {/* Summary Stats */}
      <div className="mt-6 p-4 bg-gray-50 rounded-lg">
        <div className="grid grid-cols-3 gap-4 text-center">
          <div>
            <p className="text-2xl font-bold text-gray-900">
              {locations.length}
            </p>
            <p className="text-sm text-gray-600">Total Locations</p>
          </div>
          <div>
            <p className="text-2xl font-bold text-orange-600">
              {locations.filter(l => l.anomaly_count > 0).length}
            </p>
            <p className="text-sm text-gray-600">Affected Locations</p>
          </div>
          <div>
            <p className="text-2xl font-bold text-red-600">
              {Math.max(...locations.map(l => l.anomaly_count), 0)}
            </p>
            <p className="text-sm text-gray-600">Max Issues/Location</p>
          </div>
        </div>
      </div>

      {/* Top Issues by Priority */}
      <div className="mt-6">
        <h4 className="font-semibold mb-3">Priority Breakdown (Top 5 Locations)</h4>
        <div className="space-y-2">
          {chartData.slice(0, 5).map((location) => {
            const priorities = {
              'VERY HIGH': location.anomalies?.filter(a => a.priority === 'VERY HIGH').length || 0,
              'HIGH': location.anomalies?.filter(a => a.priority === 'HIGH').length || 0,
              'MEDIUM': location.anomalies?.filter(a => a.priority === 'MEDIUM').length || 0,
              'LOW': location.anomalies?.filter(a => a.priority === 'LOW').length || 0,
            }
            
            return (
              <div key={location.name} className="p-3 border rounded-lg">
                <div className="flex justify-between items-center mb-2">
                  <span className="font-medium">{location.name}</span>
                  <span className="text-sm text-gray-600">
                    {location.anomaly_count} total
                  </span>
                </div>
                <div className="flex gap-1">
                  {priorities['VERY HIGH'] > 0 && (
                    <div className="h-2 bg-red-500 rounded" style={{ width: `${(priorities['VERY HIGH'] / location.anomaly_count) * 100}%` }} title={`${priorities['VERY HIGH']} Very High`} />
                  )}
                  {priorities['HIGH'] > 0 && (
                    <div className="h-2 bg-orange-500 rounded" style={{ width: `${(priorities['HIGH'] / location.anomaly_count) * 100}%` }} title={`${priorities['HIGH']} High`} />
                  )}
                  {priorities['MEDIUM'] > 0 && (
                    <div className="h-2 bg-yellow-500 rounded" style={{ width: `${(priorities['MEDIUM'] / location.anomaly_count) * 100}%` }} title={`${priorities['MEDIUM']} Medium`} />
                  )}
                  {priorities['LOW'] > 0 && (
                    <div className="h-2 bg-green-500 rounded" style={{ width: `${(priorities['LOW'] / location.anomaly_count) * 100}%` }} title={`${priorities['LOW']} Low`} />
                  )}
                </div>
              </div>
            )
          })}
        </div>
      </div>
    </div>
  )
}