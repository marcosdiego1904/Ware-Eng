"use client"

import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Progress } from '@/components/ui/progress'
import { Badge } from '@/components/ui/badge'
import { BarChart3, TrendingUp, AlertTriangle, Target, Database } from 'lucide-react'
import { OverviewStats } from '@/lib/dashboard-types'

interface StatisticalMetricsPanelProps {
  stats: OverviewStats
  className?: string
}

export function StatisticalMetricsPanel({ stats, className }: StatisticalMetricsPanelProps) {
  // Only show if we have warehouse utilization data
  if (!stats.warehouseUtilization || stats.warehouseUtilization === 0) {
    return null
  }

  const severityRatio = stats.expectedOvercapacityCount && stats.expectedOvercapacityCount > 0 
    ? (stats.actualOvercapacityCount || 0) / stats.expectedOvercapacityCount 
    : 0

  const getSeverityColor = (ratio: number) => {
    if (ratio >= 3.0) return 'text-red-600'
    if (ratio >= 2.0) return 'text-orange-600'
    if (ratio >= 1.5) return 'text-yellow-600'
    return 'text-green-600'
  }

  const getSeverityLabel = (ratio: number) => {
    if (ratio >= 3.0) return 'Critical'
    if (ratio >= 2.0) return 'Elevated'
    if (ratio >= 1.5) return 'Moderate'
    return 'Normal'
  }

  const utilizationHealth = stats.warehouseUtilization <= 80 ? 'optimal' :
                           stats.warehouseUtilization <= 95 ? 'good' :
                           stats.warehouseUtilization <= 100 ? 'near-capacity' : 'overcapacity'

  return (
    <Card className={`border-indigo-200 bg-indigo-50/30 ${className}`}>
      <CardHeader>
        <CardTitle className="flex items-center gap-2">
          <BarChart3 className="w-5 h-5 text-indigo-600" />
          Statistical Analytics Dashboard
        </CardTitle>
      </CardHeader>
      <CardContent>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          
          {/* Warehouse Utilization Breakdown */}
          <div className="space-y-4">
            <div className="text-sm font-semibold text-indigo-900">Warehouse Utilization</div>
            
            <div className="space-y-3">
              <div className="flex justify-between items-center">
                <span className="text-sm text-gray-600">Current Level</span>
                <Badge className={
                  utilizationHealth === 'optimal' ? 'bg-green-100 text-green-800' :
                  utilizationHealth === 'good' ? 'bg-blue-100 text-blue-800' :
                  utilizationHealth === 'near-capacity' ? 'bg-yellow-100 text-yellow-800' :
                  'bg-red-100 text-red-800'
                }>
                  {stats.warehouseUtilization.toFixed(1)}%
                </Badge>
              </div>
              
              <Progress 
                value={Math.min(100, stats.warehouseUtilization)} 
                className="h-3"
              />
              
              <div className="grid grid-cols-2 gap-2 text-xs">
                <div>
                  <span className="text-gray-500">Total Pallets</span>
                  <p className="font-medium">{stats.totalPallets?.toLocaleString()}</p>
                </div>
                <div>
                  <span className="text-gray-500">Capacity</span>
                  <p className="font-medium">{stats.totalCapacity?.toLocaleString()}</p>
                </div>
              </div>

              <div className="text-xs text-gray-500 flex items-center gap-1">
                <TrendingUp className="w-3 h-3" />
                <span>
                  {stats.trendsData.utilizationGrowth && stats.trendsData.utilizationGrowth > 0 ? '+' : ''}
                  {stats.trendsData.utilizationGrowth}% vs last period
                </span>
              </div>
            </div>
          </div>

          {/* Overcapacity Statistical Analysis */}
          <div className="space-y-4">
            <div className="text-sm font-semibold text-indigo-900">Overcapacity Analysis</div>
            
            <div className="space-y-3">
              <div className="flex justify-between items-center">
                <span className="text-sm text-gray-600">Severity Level</span>
                <Badge className={
                  severityRatio >= 3.0 ? 'bg-red-100 text-red-800' :
                  severityRatio >= 2.0 ? 'bg-orange-100 text-orange-800' :
                  severityRatio >= 1.5 ? 'bg-yellow-100 text-yellow-800' :
                  'bg-green-100 text-green-800'
                }>
                  {getSeverityLabel(severityRatio)}
                </Badge>
              </div>

              <div className="bg-white rounded border p-3 space-y-2">
                <div className="flex justify-between text-sm">
                  <span className="text-gray-600">Expected</span>
                  <span className="font-medium">{stats.expectedOvercapacityCount}</span>
                </div>
                <div className="flex justify-between text-sm">
                  <span className="text-gray-600">Actual</span>
                  <span className="font-medium">{stats.actualOvercapacityCount}</span>
                </div>
                <div className="flex justify-between text-sm pt-2 border-t">
                  <span className="text-gray-600">Ratio</span>
                  <span className={`font-medium ${getSeverityColor(severityRatio)}`}>
                    {severityRatio > 0 ? `${severityRatio.toFixed(1)}x` : 'N/A'}
                  </span>
                </div>
              </div>
            </div>
          </div>

          {/* System Health Overview */}
          <div className="space-y-4">
            <div className="text-sm font-semibold text-indigo-900">System Health</div>
            
            <div className="space-y-3">
              <div className="flex items-center gap-2">
                <div className={`w-3 h-3 rounded-full ${
                  stats.systemHealth === 'excellent' ? 'bg-green-500' :
                  stats.systemHealth === 'good' ? 'bg-blue-500' :
                  stats.systemHealth === 'warning' ? 'bg-yellow-500' : 'bg-red-500'
                }`} />
                <span className="text-sm capitalize">{stats.systemHealth} Health</span>
              </div>

              <div className="space-y-2 text-sm">
                <div className="flex justify-between">
                  <span className="text-gray-600">Critical Locations</span>
                  <span className="font-medium flex items-center gap-1">
                    {stats.criticalLocations > 0 && <AlertTriangle className="w-3 h-3 text-red-500" />}
                    {stats.criticalLocations}
                  </span>
                </div>
                
                <div className="flex justify-between">
                  <span className="text-gray-600">Systematic Issues</span>
                  <span className="font-medium text-red-600">
                    {stats.systematicAnomaliesCount}
                  </span>
                </div>
                
                <div className="flex justify-between">
                  <span className="text-gray-600">Resolution Rate</span>
                  <span className="font-medium flex items-center gap-1">
                    <Target className="w-3 h-3 text-green-500" />
                    {stats.resolutionRate.toFixed(1)}%
                  </span>
                </div>
              </div>
            </div>
          </div>

        </div>

        {/* Statistical Model Information */}
        <div className="mt-6 pt-6 border-t border-indigo-200">
          <div className="flex items-center gap-2 text-sm text-indigo-700">
            <Database className="w-4 h-4" />
            <span>
              Analytics based on Poisson-based random distribution and high utilization linear models
            </span>
          </div>
          <p className="text-xs text-gray-600 mt-1">
            Expected overcapacity calculated using statistical models that account for warehouse utilization patterns
          </p>
        </div>
      </CardContent>
    </Card>
  )
}