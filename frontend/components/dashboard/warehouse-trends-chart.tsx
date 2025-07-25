"use client"

import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { OverviewStats, DetailedReportData } from '@/lib/dashboard-types'
import { TrendingUp, TrendingDown, BarChart3, PieChart, Target, MapPin } from 'lucide-react'

interface WarehouseTrendsChartProps {
  data: DetailedReportData | null
  stats: OverviewStats
}

export function WarehouseTrendsChart({ data, stats }: WarehouseTrendsChartProps) {
  if (!data) {
    return (
      <Card>
        <CardContent className="p-8 text-center">
          <BarChart3 className="w-12 h-12 text-gray-400 mx-auto mb-4" />
          <p className="text-gray-600">No trend data available</p>
        </CardContent>
      </Card>
    )
  }

  // Generate mock trend data for visualization
  const weeklyData = Array.from({ length: 7 }, (_, i) => ({
    day: ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'][i],
    reports: Math.floor(Math.random() * 5) + 1,
    anomalies: Math.floor(Math.random() * 20) + 5,
    resolved: Math.floor(Math.random() * 15) + 3
  }))

  const maxValue = Math.max(...weeklyData.flatMap(d => [d.reports * 5, d.anomalies, d.resolved]))

  return (
    <div className="space-y-6">
      {/* Trend Overview Cards */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <Card className="border-l-4 border-l-blue-500">
          <CardHeader className="pb-3">
            <CardTitle className="text-sm font-medium text-gray-600">Weekly Report Trend</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="flex items-center justify-between">
              <span className="text-2xl font-bold">{weeklyData.reduce((sum, d) => sum + d.reports, 0)}</span>
              <div className={`flex items-center gap-1 text-sm ${
                stats.trendsData.reportsGrowth >= 0 ? 'text-green-600' : 'text-red-600'
              }`}>
                {stats.trendsData.reportsGrowth >= 0 ? 
                  <TrendingUp className="w-4 h-4" /> : 
                  <TrendingDown className="w-4 h-4" />
                }
                {Math.abs(stats.trendsData.reportsGrowth)}%
              </div>
            </div>
            <p className="text-xs text-gray-500 mt-1">Total reports this week</p>
          </CardContent>
        </Card>

        <Card className="border-l-4 border-l-orange-500">
          <CardHeader className="pb-3">
            <CardTitle className="text-sm font-medium text-gray-600">Anomaly Detection Rate</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="flex items-center justify-between">
              <span className="text-2xl font-bold">{weeklyData.reduce((sum, d) => sum + d.anomalies, 0)}</span>
              <div className={`flex items-center gap-1 text-sm ${
                stats.trendsData.anomaliesGrowth <= 0 ? 'text-green-600' : 'text-orange-600'
              }`}>
                {stats.trendsData.anomaliesGrowth <= 0 ? 
                  <TrendingDown className="w-4 h-4" /> : 
                  <TrendingUp className="w-4 h-4" />
                }
                {Math.abs(stats.trendsData.anomaliesGrowth)}%
              </div>
            </div>
            <p className="text-xs text-gray-500 mt-1">Issues detected this week</p>
          </CardContent>
        </Card>

        <Card className="border-l-4 border-l-green-500">
          <CardHeader className="pb-3">
            <CardTitle className="text-sm font-medium text-gray-600">Resolution Efficiency</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="flex items-center justify-between">
              <span className="text-2xl font-bold">{stats.resolutionRate.toFixed(0)}%</span>
              <div className={`flex items-center gap-1 text-sm ${
                stats.trendsData.resolutionGrowth >= 0 ? 'text-green-600' : 'text-red-600'
              }`}>
                {stats.trendsData.resolutionGrowth >= 0 ? 
                  <TrendingUp className="w-4 h-4" /> : 
                  <TrendingDown className="w-4 h-4" />
                }
                {Math.abs(stats.trendsData.resolutionGrowth)}%
              </div>
            </div>
            <p className="text-xs text-gray-500 mt-1">Current resolution rate</p>
          </CardContent>
        </Card>
      </div>

      {/* Weekly Activity Chart */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <BarChart3 className="w-5 h-5" />
            Weekly Activity Trends
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="space-y-4">
            {/* Chart Legend */}
            <div className="flex gap-6 text-sm">
              <div className="flex items-center gap-2">
                <div className="w-3 h-3 bg-blue-500 rounded"></div>
                <span>Reports</span>
              </div>
              <div className="flex items-center gap-2">
                <div className="w-3 h-3 bg-orange-500 rounded"></div>
                <span>Anomalies</span>
              </div>
              <div className="flex items-center gap-2">
                <div className="w-3 h-3 bg-green-500 rounded"></div>
                <span>Resolved</span>
              </div>
            </div>

            {/* Chart Bars */}
            <div className="space-y-3">
              {weeklyData.map((day, index) => (
                <div key={day.day} className="space-y-2">
                  <div className="flex justify-between items-center text-sm font-medium">
                    <span>{day.day}</span>
                    <span className="text-gray-500">
                      {day.reports} reports, {day.anomalies} issues, {day.resolved} resolved
                    </span>
                  </div>
                  
                  {/* Stacked bar chart */}
                  <div className="flex gap-1 h-6">
                    <div 
                      className="bg-blue-500 rounded-l"
                      style={{ width: `${(day.reports * 5 / maxValue) * 100}%` }}
                      title={`${day.reports} reports`}
                    />
                    <div 
                      className="bg-orange-500"
                      style={{ width: `${(day.anomalies / maxValue) * 100}%` }}
                      title={`${day.anomalies} anomalies`}
                    />
                    <div 
                      className="bg-green-500 rounded-r"
                      style={{ width: `${(day.resolved / maxValue) * 100}%` }}
                      title={`${day.resolved} resolved`}
                    />
                  </div>
                </div>
              ))}
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Analytics Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        {/* Anomaly Type Distribution */}
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <PieChart className="w-5 h-5" />
              Anomaly Type Distribution
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-3">
              {Object.entries(data.priorityBreakdown)
                .sort(([,a], [,b]) => b - a)
                .map(([priority, count]) => {
                  const total = Object.values(data.priorityBreakdown).reduce((a, b) => a + b, 0)
                  const percentage = total > 0 ? (count / total) * 100 : 0
                  
                  const priorityColors = {
                    'VERY HIGH': 'bg-red-500',
                    'HIGH': 'bg-orange-500',
                    'MEDIUM': 'bg-yellow-500',
                    'LOW': 'bg-green-500'
                  }
                  
                  return (
                    <div key={priority} className="space-y-2">
                      <div className="flex justify-between items-center">
                        <div className="flex items-center gap-2">
                          <div className={`w-3 h-3 rounded ${priorityColors[priority as keyof typeof priorityColors] || 'bg-gray-500'}`} />
                          <span className="text-sm font-medium">{priority}</span>
                        </div>
                        <div className="text-sm text-gray-600">
                          {count} ({percentage.toFixed(1)}%)
                        </div>
                      </div>
                      <div className="w-full bg-gray-200 rounded-full h-2">
                        <div 
                          className={`h-2 rounded-full ${priorityColors[priority as keyof typeof priorityColors] || 'bg-gray-500'}`}
                          style={{ width: `${percentage}%` }}
                        />
                      </div>
                    </div>
                  )
                })
              }
            </div>
          </CardContent>
        </Card>

        {/* Location Performance */}
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <MapPin className="w-5 h-5" />
              Location Performance
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-3">
              {data.locationHotspots.slice(0, 5).map((location, index) => (
                <div key={location.name} className="flex items-center justify-between p-3 border rounded-lg">
                  <div className="flex items-center gap-3">
                    <span className="text-sm font-medium text-gray-500">#{index + 1}</span>
                    <div>
                      <p className="font-medium">{location.name}</p>
                      <p className="text-sm text-gray-500">
                        {location.count} issues detected
                      </p>
                    </div>
                  </div>
                  <Badge 
                    variant={location.severity === 'critical' ? 'destructive' : 
                           location.severity === 'high' ? 'secondary' : 'outline'}
                  >
                    {location.severity}
                  </Badge>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Performance Insights */}
      <Card className="bg-gradient-to-r from-blue-50 to-indigo-50 border-blue-200">
        <CardHeader>
          <CardTitle className="flex items-center gap-2 text-blue-900">
            <Target className="w-5 h-5" />
            Performance Insights
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div>
              <h4 className="font-semibold text-blue-900 mb-3">Key Metrics</h4>
              <div className="space-y-2 text-sm text-blue-800">
                <div className="flex justify-between">
                  <span>Average anomalies per report:</span>
                  <span className="font-medium">{stats.averageAnomaliesPerReport.toFixed(1)}</span>
                </div>
                <div className="flex justify-between">
                  <span>System health score:</span>
                  <span className="font-medium">
                    {stats.systemHealth === 'excellent' ? '95%' : 
                     stats.systemHealth === 'good' ? '80%' :
                     stats.systemHealth === 'warning' ? '65%' : '40%'}
                  </span>
                </div>
                <div className="flex justify-between">
                  <span>Critical locations:</span>
                  <span className="font-medium">{stats.criticalLocations}</span>
                </div>
              </div>
            </div>
            
            <div>
              <h4 className="font-semibold text-blue-900 mb-3">Recommendations</h4>
              <div className="space-y-1 text-sm text-blue-800">
                {stats.resolutionRate < 70 && (
                  <div className="flex items-center gap-2">
                    <div className="w-1.5 h-1.5 bg-blue-600 rounded-full" />
                    <span>Focus on improving resolution processes</span>
                  </div>
                )}
                {stats.criticalLocations > 2 && (
                  <div className="flex items-center gap-2">
                    <div className="w-1.5 h-1.5 bg-blue-600 rounded-full" />
                    <span>Address critical location issues immediately</span>
                  </div>
                )}
                {stats.averageAnomaliesPerReport > 10 && (
                  <div className="flex items-center gap-2">
                    <div className="w-1.5 h-1.5 bg-blue-600 rounded-full" />
                    <span>Review warehouse processes for improvements</span>
                  </div>
                )}
                <div className="flex items-center gap-2">
                  <div className="w-1.5 h-1.5 bg-blue-600 rounded-full" />
                  <span>Continue regular monitoring and analysis</span>
                </div>
              </div>
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  )
}