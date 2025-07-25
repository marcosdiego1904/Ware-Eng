"use client"

interface PriorityHeatmapProps {
  priorityData: Record<string, number>
}

export function PriorityHeatmap({ priorityData }: PriorityHeatmapProps) {
  const priorities = ['VERY HIGH', 'HIGH', 'MEDIUM', 'LOW']
  const total = Object.values(priorityData).reduce((sum, count) => sum + count, 0)
  
  const getPriorityConfig = (priority: string) => {
    switch (priority) {
      case 'VERY HIGH':
        return {
          color: 'bg-red-500',
          lightColor: 'bg-red-100',
          textColor: 'text-red-700',
          borderColor: 'border-red-200'
        }
      case 'HIGH':
        return {
          color: 'bg-orange-500',
          lightColor: 'bg-orange-100',
          textColor: 'text-orange-700',
          borderColor: 'border-orange-200'
        }
      case 'MEDIUM':
        return {
          color: 'bg-yellow-500',
          lightColor: 'bg-yellow-100',
          textColor: 'text-yellow-700',
          borderColor: 'border-yellow-200'
        }
      case 'LOW':
        return {
          color: 'bg-green-500',
          lightColor: 'bg-green-100',
          textColor: 'text-green-700',
          borderColor: 'border-green-200'
        }
      default:
        return {
          color: 'bg-gray-500',
          lightColor: 'bg-gray-100',
          textColor: 'text-gray-700',
          borderColor: 'border-gray-200'
        }
    }
  }

  if (total === 0) {
    return (
      <div className="text-center py-8">
        <div className="text-4xl mb-2">📊</div>
        <p className="text-gray-600">No priority data available</p>
      </div>
    )
  }

  return (
    <div className="space-y-6">
      {/* Priority Grid Heatmap */}
      <div className="grid grid-cols-2 gap-4">
        {priorities.map(priority => {
          const count = priorityData[priority] || 0
          const percentage = (count / total) * 100
          const config = getPriorityConfig(priority)
          
          return (
            <div 
              key={priority} 
              className={`p-4 rounded-lg border ${config.lightColor} ${config.borderColor} hover:shadow-md transition-shadow`}
            >
              <div className="flex items-center justify-between mb-2">
                <span className={`text-sm font-medium ${config.textColor}`}>
                  {priority}
                </span>
                <div className={`w-3 h-3 rounded ${config.color}`} />
              </div>
              
              <div className="space-y-2">
                <div className={`text-2xl font-bold ${config.textColor}`}>
                  {count}
                </div>
                <div className="text-xs text-gray-600">
                  {percentage.toFixed(1)}% of total
                </div>
                
                {/* Mini progress bar */}
                <div className="w-full bg-gray-200 rounded-full h-1.5">
                  <div 
                    className={`h-1.5 rounded-full ${config.color} transition-all duration-300`}
                    style={{ width: `${percentage}%` }}
                  />
                </div>
              </div>
            </div>
          )
        })}
      </div>

      {/* Horizontal Bar Chart */}
      <div className="space-y-3">
        <h4 className="font-semibold text-gray-700">Priority Distribution</h4>
        {priorities.map(priority => {
          const count = priorityData[priority] || 0
          const percentage = (count / total) * 100
          const config = getPriorityConfig(priority)
          
          if (count === 0) return null
          
          return (
            <div key={priority} className="space-y-2">
              <div className="flex justify-between items-center">
                <span className="text-sm font-medium">{priority}</span>
                <div className="text-sm text-gray-600">
                  {count} issues ({percentage.toFixed(1)}%)
                </div>
              </div>
              <div className="relative h-4 bg-gray-100 rounded-full overflow-hidden">
                <div 
                  className={`h-full ${config.color} transition-all duration-500`}
                  style={{ width: `${Math.max(percentage, 5)}%` }}
                />
                {percentage > 15 && (
                  <div className="absolute inset-0 flex items-center justify-center text-xs font-medium text-white">
                    {count}
                  </div>
                )}
              </div>
            </div>
          )
        })}
      </div>

      {/* Summary Statistics */}
      <div className="grid grid-cols-2 gap-4 pt-4 border-t">
        <div className="text-center">
          <div className="text-2xl font-bold text-gray-900">
            {(priorityData['VERY HIGH'] || 0) + (priorityData['HIGH'] || 0)}
          </div>
          <div className="text-sm text-red-600 font-medium">High Priority Issues</div>
        </div>
        <div className="text-center">
          <div className="text-2xl font-bold text-gray-900">
            {((((priorityData['VERY HIGH'] || 0) + (priorityData['HIGH'] || 0)) / total) * 100).toFixed(0)}%
          </div>
          <div className="text-sm text-gray-600">Require Immediate Attention</div>
        </div>
      </div>

      {/* Priority Insights */}
      <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
        <h4 className="font-semibold mb-2 text-blue-900">Priority Insights</h4>
        <div className="space-y-1 text-sm text-blue-800">
          {(() => {
            const insights = []
            const highPriorityCount = (priorityData['VERY HIGH'] || 0) + (priorityData['HIGH'] || 0)
            const highPriorityPercentage = (highPriorityCount / total) * 100
            
            if (highPriorityPercentage > 50) {
              insights.push('High concentration of priority issues requires immediate attention')
            } else if (highPriorityPercentage > 25) {
              insights.push('Significant number of priority issues detected')
            } else {
              insights.push('Most issues are low to medium priority')
            }
            
            const mostCommon = Object.entries(priorityData)
              .sort(([,a], [,b]) => b - a)[0]
            if (mostCommon) {
              insights.push(`${mostCommon[0]} priority issues are most common (${mostCommon[1]} cases)`)
            }
            
            return insights.map((insight, index) => (
              <div key={index} className="flex items-center gap-2">
                <div className="w-1.5 h-1.5 bg-blue-600 rounded-full flex-shrink-0" />
                <span>{insight}</span>
              </div>
            ))
          })()}
        </div>
      </div>
    </div>
  )
}