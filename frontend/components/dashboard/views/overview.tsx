"use client"

import { useEffect, useState } from 'react'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Badge } from '@/components/ui/badge'
import { Progress } from '@/components/ui/progress'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs'
import { useDashboardStore } from '@/lib/store'
import { reportsApi, Report, ReportDetails } from '@/lib/reports'
import { OverviewStats, DetailedReportData } from '@/lib/dashboard-types'
import { 
  AlertTriangle, 
  Package, 
  MapPin, 
  TrendingUp,
  FileText,
  Upload,
  Activity,
  BarChart3,
  Target,
  Zap,
  ArrowUp,
  ArrowDown,
  Minus,
  Gauge,
} from 'lucide-react'
import { SystemHealthIndicator } from '@/components/dashboard/system-health-indicator'
import { RecentActivityFeed } from '@/components/dashboard/recent-activity-feed'
import { WarehouseTrendsChart } from '@/components/dashboard/warehouse-trends-chart'
import { PriorityHeatmap } from '@/components/dashboard/priority-heatmap'
import { StatisticalMetricsPanel } from '@/components/dashboard/statistical-metrics-panel'

export function OverviewView() {
  const { setCurrentView } = useDashboardStore()
  const [reports, setReports] = useState<Report[]>([])
  const [detailedData, setDetailedData] = useState<DetailedReportData | null>(null)
  const [stats, setStats] = useState<OverviewStats>({
    totalReports: 0,
    totalAnomalies: 0,
    recentActivity: 0,
    alertsCount: 0,
    resolutionRate: 0,
    averageAnomaliesPerReport: 0,
    criticalLocations: 0,
    systemHealth: 'good',
    warehouseUtilization: 0,
    totalPallets: 0,
    totalCapacity: 0,
    expectedOvercapacityCount: 0,
    actualOvercapacityCount: 0,
    systematicAnomaliesCount: 0,
    trendsData: {
      reportsGrowth: 0,
      anomaliesGrowth: 0,
      resolutionGrowth: 0,
      utilizationGrowth: 0
    }
  })
  const [isLoading, setIsLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    loadDashboardData()
  }, [])

  const loadDashboardData = async () => {
    try {
      setIsLoading(true)
      setError(null)
      const response = await reportsApi.getReports()
      const reportsData = response.reports || []
      setReports(reportsData)
      
      // Load detailed data for recent reports
      const recentReportIds = reportsData
        .sort((a, b) => new Date(b.timestamp).getTime() - new Date(a.timestamp).getTime())
        .slice(0, 5)
        .map(r => r.id)
      
      const recentReportsDetails = await Promise.all(
        recentReportIds.map(id => reportsApi.getReportDetails(id).catch(() => null))
      )
      
      const validRecentReports = recentReportsDetails.filter(Boolean) as ReportDetails[]
      
      // Calculate comprehensive stats
      const totalAnomalies = reportsData.reduce((sum, report) => sum + report.anomaly_count, 0)
      const recentReports = reportsData.filter(report => {
        const reportDate = new Date(report.timestamp)
        const weekAgo = new Date(Date.now() - 7 * 24 * 60 * 60 * 1000)
        return reportDate > weekAgo
      }).length
      
      // Calculate advanced metrics
      const averageAnomalies = reportsData.length > 0 ? totalAnomalies / reportsData.length : 0
      
      // Calculate resolution rate from recent reports and warehouse utilization metrics
      let resolvedCount = 0
      let totalAnomaliesDetailed = 0
      const priorityBreakdown: Record<string, number> = {}
      const statusBreakdown: Record<string, number> = {}
      const locationHotspots: Array<{ name: string; count: number; severity: string }> = []
      
      // Enhanced warehouse utilization metrics
      let warehouseUtilization = 0
      let totalPallets = 0
      let totalCapacity = 0
      let expectedOvercapacityCount = 0
      let actualOvercapacityCount = 0
      let systematicAnomaliesCount = 0
      
      validRecentReports.forEach(report => {
        report.locations.forEach(location => {
          location.anomalies.forEach(anomaly => {
            totalAnomaliesDetailed++
            if (anomaly.status === 'Resolved') resolvedCount++
            
            priorityBreakdown[anomaly.priority] = (priorityBreakdown[anomaly.priority] || 0) + 1
            statusBreakdown[anomaly.status] = (statusBreakdown[anomaly.status] || 0) + 1
            
            // Extract warehouse utilization data from overcapacity anomalies
            if (anomaly.anomaly_type === 'OVERCAPACITY' && anomaly.utilization_rate !== undefined) {
              warehouseUtilization = Math.max(warehouseUtilization, anomaly.utilization_rate)
              totalPallets = Math.max(totalPallets, anomaly.warehouse_total_pallets || 0)
              totalCapacity = Math.max(totalCapacity, anomaly.warehouse_total_capacity || 0)
              expectedOvercapacityCount = Math.max(expectedOvercapacityCount, anomaly.expected_overcapacity_count || 0)
              actualOvercapacityCount = Math.max(actualOvercapacityCount, anomaly.actual_overcapacity_count || 0)
              
              if (anomaly.overcapacity_category === 'Systematic') {
                systematicAnomaliesCount++
              }
            }
          })
          
          // Track location hotspots
          const existingLocation = locationHotspots.find(l => l.name === location.name)
          if (existingLocation) {
            existingLocation.count += location.anomaly_count
          } else {
            locationHotspots.push({
              name: location.name,
              count: location.anomaly_count,
              severity: location.anomaly_count > 10 ? 'critical' : location.anomaly_count > 5 ? 'high' : 'medium'
            })
          }
        })
      })
      
      const resolutionRate = totalAnomaliesDetailed > 0 ? (resolvedCount / totalAnomaliesDetailed) * 100 : 0
      const criticalLocations = locationHotspots.filter(l => l.severity === 'critical').length
      
      // Determine system health
      let systemHealth: OverviewStats['systemHealth'] = 'excellent'
      if (criticalLocations > 3 || resolutionRate < 50) systemHealth = 'critical'
      else if (criticalLocations > 1 || resolutionRate < 70) systemHealth = 'warning'
      else if (resolutionRate < 85) systemHealth = 'good'
      
      // Calculate trends (mock data for now - in real app, compare with historical data)
      const trendsData = {
        reportsGrowth: Math.random() > 0.5 ? Math.floor(Math.random() * 20) : -Math.floor(Math.random() * 10),
        anomaliesGrowth: Math.random() > 0.3 ? Math.floor(Math.random() * 15) : -Math.floor(Math.random() * 25),
        resolutionGrowth: Math.random() > 0.4 ? Math.floor(Math.random() * 30) : -Math.floor(Math.random() * 15),
        utilizationGrowth: Math.random() > 0.5 ? Math.floor(Math.random() * 10) : -Math.floor(Math.random() * 5)
      }
      
      setStats({
        totalReports: reportsData.length,
        totalAnomalies,
        recentActivity: recentReports,
        alertsCount: reportsData.filter(report => report.anomaly_count > 0).length,
        resolutionRate,
        averageAnomaliesPerReport: averageAnomalies,
        criticalLocations,
        systemHealth,
        // Enhanced warehouse utilization metrics
        warehouseUtilization: warehouseUtilization * 100, // Convert to percentage
        totalPallets,
        totalCapacity,
        expectedOvercapacityCount,
        actualOvercapacityCount,
        systematicAnomaliesCount,
        trendsData
      })
      
      setDetailedData({
        reports: reportsData,
        recentReports: validRecentReports,
        priorityBreakdown,
        statusBreakdown,
        locationHotspots: locationHotspots.sort((a, b) => b.count - a.count).slice(0, 10)
      })
      
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to load dashboard data')
    } finally {
      setIsLoading(false)
    }
  }

  if (isLoading) {
    return (
      <div className="p-6">
        <div className="flex items-center justify-center h-64">
          <div className="text-center">
            <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto mb-4"></div>
            <p className="text-gray-600">Loading dashboard...</p>
          </div>
        </div>
      </div>
    )
  }

  const getTrendIcon = (value: number) => {
    if (value > 0) return <ArrowUp className="w-4 h-4 text-green-600" />
    if (value < 0) return <ArrowDown className="w-4 h-4 text-red-600" />
    return <Minus className="w-4 h-4 text-gray-600" />
  }
  
  const getTrendColor = (value: number) => {
    if (value > 0) return 'text-green-600'
    if (value < 0) return 'text-red-600'
    return 'text-gray-600'
  }

  return (
    <div className="p-6 space-y-6">
      {/* Enhanced Header */}
      <div className="flex justify-between items-start">
        <div>
          <h1 className="text-3xl font-bold text-gray-900 mb-2">Warehouse Intelligence Dashboard</h1>
          <div className="flex items-center gap-4 text-sm text-gray-600">
            <div className="flex items-center gap-2">
              <SystemHealthIndicator status={stats.systemHealth} />
              <span>System Health: {stats.systemHealth.charAt(0).toUpperCase() + stats.systemHealth.slice(1)}</span>
            </div>
            <div className="flex items-center gap-2">
              <Activity className="w-4 h-4" />
              <span>Last updated: {new Date().toLocaleTimeString()}</span>
            </div>
          </div>
        </div>
        <div className="flex gap-3">
          <Button variant="outline" onClick={loadDashboardData} disabled={isLoading}>
            <TrendingUp className="w-4 h-4 mr-2" />
            Refresh
          </Button>
          <Button onClick={() => setCurrentView('new-analysis')}>
            <Upload className="w-4 h-4 mr-2" />
            New Analysis
          </Button>
        </div>
      </div>

      {/* Error Alert */}
      {error && (
        <div className="bg-red-50 border border-red-200 rounded-lg p-4">
          <div className="flex items-center">
            <AlertTriangle className="h-5 w-5 text-red-400 mr-2" />
            <p className="text-red-800">{error}</p>
            <Button 
              variant="outline" 
              size="sm" 
              className="ml-auto"
              onClick={loadDashboardData}
            >
              Retry
            </Button>
          </div>
        </div>
      )}

      {/* Enhanced KPI Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 xl:grid-cols-6 gap-4">
        <Card className="hover:shadow-lg transition-shadow">
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Total Reports</CardTitle>
            <FileText className="h-4 w-4 text-blue-600" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{stats.totalReports}</div>
            <div className={`flex items-center text-xs ${getTrendColor(stats.trendsData.reportsGrowth)}`}>
              {getTrendIcon(stats.trendsData.reportsGrowth)}
              <span className="ml-1">{Math.abs(stats.trendsData.reportsGrowth)}% vs last period</span>
            </div>
          </CardContent>
        </Card>

        <Card className="hover:shadow-lg transition-shadow">
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Total Anomalies</CardTitle>
            <AlertTriangle className="h-4 w-4 text-orange-600" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{stats.totalAnomalies}</div>
            <div className={`flex items-center text-xs ${getTrendColor(stats.trendsData.anomaliesGrowth)}`}>
              {getTrendIcon(stats.trendsData.anomaliesGrowth)}
              <span className="ml-1">{Math.abs(stats.trendsData.anomaliesGrowth)}% vs last period</span>
            </div>
          </CardContent>
        </Card>

        <Card className="hover:shadow-lg transition-shadow">
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Resolution Rate</CardTitle>
            <Target className="h-4 w-4 text-green-600" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{stats.resolutionRate.toFixed(1)}%</div>
            <div className={`flex items-center text-xs ${getTrendColor(stats.trendsData.resolutionGrowth)}`}>
              {getTrendIcon(stats.trendsData.resolutionGrowth)}
              <span className="ml-1">{Math.abs(stats.trendsData.resolutionGrowth)}% vs last period</span>
            </div>
          </CardContent>
        </Card>

        <Card className="hover:shadow-lg transition-shadow">
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Avg Issues/Report</CardTitle>
            <BarChart3 className="h-4 w-4 text-purple-600" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{stats.averageAnomaliesPerReport.toFixed(1)}</div>
            <p className="text-xs text-muted-foreground">
              Per analysis session
            </p>
          </CardContent>
        </Card>

        <Card className="hover:shadow-lg transition-shadow">
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Critical Locations</CardTitle>
            <MapPin className="h-4 w-4 text-red-600" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{stats.criticalLocations}</div>
            <p className="text-xs text-muted-foreground">
              Require immediate attention
            </p>
          </CardContent>
        </Card>

        <Card className="hover:shadow-lg transition-shadow">
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Recent Activity</CardTitle>
            <Activity className="h-4 w-4 text-indigo-600" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{stats.recentActivity}</div>
            <p className="text-xs text-muted-foreground">
              Reports this week
            </p>
          </CardContent>
        </Card>
      </div>

      {/* Warehouse Utilization Section */}
      {(stats.warehouseUtilization ?? 0) > 0 && (
        <Card className="border-blue-200 bg-blue-50/30">
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Gauge className="w-5 h-5 text-blue-600" />
              Warehouse Utilization Analytics
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
              {/* Overall Utilization */}
              <div className="space-y-2">
                <div className="flex justify-between items-center">
                  <span className="text-sm font-medium">Overall Utilization</span>
                  <span className="text-sm text-gray-600">{stats.warehouseUtilization?.toFixed(1)}%</span>
                </div>
                <Progress value={Math.min(100, stats.warehouseUtilization || 0)} className="h-3" />
                <div className="flex items-center text-xs text-gray-600">
                  {getTrendIcon(stats.trendsData.utilizationGrowth || 0)}
                  <span className="ml-1">{Math.abs(stats.trendsData.utilizationGrowth || 0)}% vs last period</span>
                </div>
              </div>

              {/* Pallet Capacity Metrics */}
              <div className="space-y-2">
                <div className="text-sm font-medium">Capacity Overview</div>
                <div className="space-y-1">
                  <div className="flex justify-between text-xs">
                    <span className="text-gray-600">Total Pallets</span>
                    <span className="font-medium">{stats.totalPallets?.toLocaleString()}</span>
                  </div>
                  <div className="flex justify-between text-xs">
                    <span className="text-gray-600">Total Capacity</span>
                    <span className="font-medium">{stats.totalCapacity?.toLocaleString()}</span>
                  </div>
                  <div className="flex justify-between text-xs">
                    <span className="text-gray-600">Available</span>
                    <span className="font-medium text-green-600">
                      {((stats.totalCapacity || 0) - (stats.totalPallets || 0)).toLocaleString()}
                    </span>
                  </div>
                </div>
              </div>

              {/* Overcapacity Analysis */}
              <div className="space-y-2">
                <div className="text-sm font-medium">Overcapacity Analysis</div>
                <div className="space-y-1">
                  <div className="flex justify-between text-xs">
                    <span className="text-gray-600">Expected</span>
                    <span className="font-medium">{stats.expectedOvercapacityCount}</span>
                  </div>
                  <div className="flex justify-between text-xs">
                    <span className="text-gray-600">Actual</span>
                    <span className="font-medium">{stats.actualOvercapacityCount}</span>
                  </div>
                  <div className="flex justify-between text-xs">
                    <span className="text-gray-600">Severity Ratio</span>
                    <span className={`font-medium ${
                      (stats.actualOvercapacityCount || 0) > (stats.expectedOvercapacityCount || 0) * 2 
                        ? 'text-red-600' 
                        : (stats.actualOvercapacityCount || 0) > (stats.expectedOvercapacityCount || 0) 
                        ? 'text-yellow-600' 
                        : 'text-green-600'
                    }`}>
                      {stats.expectedOvercapacityCount ? 
                        ((stats.actualOvercapacityCount || 0) / stats.expectedOvercapacityCount).toFixed(1) + 'x' : 'N/A'}
                    </span>
                  </div>
                </div>
              </div>

              {/* Systematic Issues */}
              <div className="space-y-2">
                <div className="text-sm font-medium">Issue Categories</div>
                <div className="space-y-1">
                  <div className="flex justify-between text-xs">
                    <span className="text-gray-600">Systematic Issues</span>
                    <span className="font-medium text-red-600">{stats.systematicAnomaliesCount}</span>
                  </div>
                  <div className="flex justify-between text-xs">
                    <span className="text-gray-600">Critical Locations</span>
                    <span className="font-medium text-orange-600">{stats.criticalLocations}</span>
                  </div>
                  <div className="flex justify-between text-xs">
                    <span className="text-gray-600">Health Status</span>
                    <span className={`font-medium ${
                      stats.systemHealth === 'excellent' ? 'text-green-600' :
                      stats.systemHealth === 'good' ? 'text-blue-600' :
                      stats.systemHealth === 'warning' ? 'text-yellow-600' : 'text-red-600'
                    }`}>
                      {stats.systemHealth.charAt(0).toUpperCase() + stats.systemHealth.slice(1)}
                    </span>
                  </div>
                </div>
              </div>
            </div>
          </CardContent>
        </Card>
      )}
      
      {/* System Health Progress Bar */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Zap className="w-5 h-5" />
            System Performance Overview
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="space-y-4">
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              <div>
                <div className="flex justify-between items-center mb-2">
                  <span className="text-sm font-medium">Resolution Rate</span>
                  <span className="text-sm text-gray-600">{stats.resolutionRate.toFixed(1)}%</span>
                </div>
                <Progress value={stats.resolutionRate} className="h-2" />
              </div>
              <div>
                <div className="flex justify-between items-center mb-2">
                  <span className="text-sm font-medium">System Health</span>
                  <span className="text-sm text-gray-600">
                    {stats.systemHealth === 'excellent' ? '95%' : 
                     stats.systemHealth === 'good' ? '80%' :
                     stats.systemHealth === 'warning' ? '65%' : '40%'}
                  </span>
                </div>
                <Progress 
                  value={stats.systemHealth === 'excellent' ? 95 : 
                         stats.systemHealth === 'good' ? 80 :
                         stats.systemHealth === 'warning' ? 65 : 40} 
                  className="h-2" 
                />
              </div>
              <div>
                <div className="flex justify-between items-center mb-2">
                  <span className="text-sm font-medium">Analysis Coverage</span>
                  <span className="text-sm text-gray-600">88%</span>
                </div>
                <Progress value={88} className="h-2" />
              </div>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Main Dashboard Content */}
      <Tabs defaultValue="overview" className="space-y-6">
        <TabsList className="grid w-full grid-cols-4">
          <TabsTrigger value="overview">Overview</TabsTrigger>
          <TabsTrigger value="activity">Recent Activity</TabsTrigger>
          <TabsTrigger value="analytics">Analytics</TabsTrigger>
          <TabsTrigger value="actions">Quick Actions</TabsTrigger>
        </TabsList>
        
        <TabsContent value="overview" className="space-y-6">
          {/* Statistical Metrics Panel */}
          <StatisticalMetricsPanel stats={stats} />
          
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            {/* Recent Reports with Enhanced Details */}
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center justify-between">
                  Latest Reports
                  <Button 
                    variant="ghost" 
                    size="sm"
                    onClick={() => setCurrentView('reports')}
                  >
                    View All
                  </Button>
                </CardTitle>
              </CardHeader>
              <CardContent>
                <div className="space-y-4">
                  {reports.slice(0, 4).map((report) => {
                    const severityLevel = report.anomaly_count === 0 ? 'success' : 
                      report.anomaly_count <= 3 ? 'warning' : 'error'
                    
                    return (
                      <div key={report.id} className="group flex items-center justify-between p-4 border rounded-lg hover:shadow-md transition-all">
                        <div className="flex items-center gap-3">
                          <div className={`w-3 h-3 rounded-full ${
                            severityLevel === 'error' ? 'bg-red-500' :
                            severityLevel === 'warning' ? 'bg-yellow-500' : 'bg-green-500'
                          }`} />
                          <FileText className="w-5 h-5 text-blue-600" />
                          <div>
                            <p className="font-medium text-sm">{report.report_name}</p>
                            <div className="flex items-center gap-3 text-xs text-gray-500">
                              <span>#{report.id}</span>
                              <span>{new Date(report.timestamp).toLocaleDateString()}</span>
                              <span>{new Date(report.timestamp).toLocaleTimeString([], {hour: '2-digit', minute:'2-digit'})}</span>
                            </div>
                          </div>
                        </div>
                        <div className="text-right">
                          <Badge variant={report.anomaly_count > 0 ? "destructive" : "secondary"}>
                            {report.anomaly_count} issues
                          </Badge>
                          <div className="mt-1 opacity-0 group-hover:opacity-100 transition-opacity">
                            <Button variant="ghost" size="sm" className="text-xs">
                              View Details
                            </Button>
                          </div>
                        </div>
                      </div>
                    )
                  })}
                  
                  {reports.length === 0 && (
                    <div className="text-center py-8">
                      <FileText className="w-12 h-12 text-gray-400 mx-auto mb-3" />
                      <p className="text-gray-600">No reports yet</p>
                      <Button 
                        variant="outline" 
                        size="sm" 
                        className="mt-2"
                        onClick={() => setCurrentView('new-analysis')}
                      >
                        Create First Analysis
                      </Button>
                    </div>
                  )}
                </div>
              </CardContent>
            </Card>

            {/* Location Hotspots */}
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <MapPin className="w-5 h-5" />
                  Location Hotspots
                </CardTitle>
              </CardHeader>
              <CardContent>
                {detailedData?.locationHotspots && detailedData.locationHotspots.length > 0 ? (
                  <div className="space-y-3">
                    {detailedData.locationHotspots.slice(0, 5).map((location, index) => (
                      <div key={location.name} className="flex items-center justify-between p-3 border rounded-lg">
                        <div className="flex items-center gap-3">
                          <div className="text-sm font-medium text-gray-500">#{index + 1}</div>
                          <div>
                            <p className="font-medium">{location.name}</p>
                            <p className="text-sm text-gray-500">
                              Severity: {location.severity.charAt(0).toUpperCase() + location.severity.slice(1)}
                            </p>
                          </div>
                        </div>
                        <Badge 
                          variant={location.severity === 'critical' ? 'destructive' : 
                                 location.severity === 'high' ? 'secondary' : 'outline'}
                        >
                          {location.count} issues
                        </Badge>
                      </div>
                    ))}
                  </div>
                ) : (
                  <div className="text-center py-8">
                    <MapPin className="w-12 h-12 text-gray-400 mx-auto mb-3" />
                    <p className="text-gray-600">No location data available</p>
                  </div>
                )}
              </CardContent>
            </Card>
          </div>
          
          {/* Priority & Status Overview */}
          {detailedData && (
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              <Card>
                <CardHeader>
                  <CardTitle>Priority Breakdown</CardTitle>
                </CardHeader>
                <CardContent>
                  <PriorityHeatmap priorityData={detailedData.priorityBreakdown} />
                </CardContent>
              </Card>
              
              <Card>
                <CardHeader>
                  <CardTitle>Resolution Status</CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="space-y-3">
                    {Object.entries(detailedData.statusBreakdown).map(([status, count]) => {
                      const total = Object.values(detailedData.statusBreakdown).reduce((a, b) => a + b, 0)
                      const percentage = total > 0 ? (count / total) * 100 : 0
                      
                      return (
                        <div key={status} className="space-y-2">
                          <div className="flex justify-between items-center">
                            <span className="font-medium">{status}</span>
                            <div className="text-sm text-gray-600">
                              {count} ({percentage.toFixed(1)}%)
                            </div>
                          </div>
                          <Progress value={percentage} className="h-2" />
                        </div>
                      )
                    })}
                  </div>
                </CardContent>
              </Card>
            </div>
          )}
        </TabsContent>
        
        <TabsContent value="activity" className="space-y-6">
          <RecentActivityFeed reports={detailedData?.recentReports || []} />
        </TabsContent>
        
        <TabsContent value="analytics" className="space-y-6">
          <WarehouseTrendsChart data={detailedData} stats={stats} />
        </TabsContent>
        
        <TabsContent value="actions" className="space-y-6">
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
            <Button 
              variant="outline" 
              className="h-24 flex flex-col gap-2 hover:bg-blue-50 hover:border-blue-300"
              onClick={() => setCurrentView('new-analysis')}
            >
              <Upload className="w-8 h-8 text-blue-600" />
              <span className="text-sm font-medium">New Analysis</span>
            </Button>
            
            <Button 
              variant="outline" 
              className="h-24 flex flex-col gap-2 hover:bg-green-50 hover:border-green-300"
              onClick={() => setCurrentView('reports')}
            >
              <FileText className="w-8 h-8 text-green-600" />
              <span className="text-sm font-medium">View Reports</span>
            </Button>
            
            <Button 
              variant="outline" 
              className="h-24 flex flex-col gap-2 hover:bg-purple-50 hover:border-purple-300"
              onClick={() => setCurrentView('rules')}
            >
              <Package className="w-8 h-8 text-purple-600" />
              <span className="text-sm font-medium">Manage Rules</span>
            </Button>
            
            <Button 
              variant="outline" 
              className="h-24 flex flex-col gap-2 hover:bg-orange-50 hover:border-orange-300"
              onClick={loadDashboardData}
              disabled={isLoading}
            >
              <TrendingUp className="w-8 h-8 text-orange-600" />
              <span className="text-sm font-medium">{isLoading ? 'Refreshing...' : 'Refresh Data'}</span>
            </Button>
          </div>
          
          {/* Quick Stats */}
          <Card>
            <CardHeader>
              <CardTitle>Quick Statistics</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="grid grid-cols-2 md:grid-cols-4 gap-6 text-center">
                <div>
                  <div className="text-3xl font-bold text-blue-600">{stats.totalReports}</div>
                  <div className="text-sm text-gray-600">Total Reports</div>
                </div>
                <div>
                  <div className="text-3xl font-bold text-orange-600">{stats.totalAnomalies}</div>
                  <div className="text-sm text-gray-600">Total Issues</div>
                </div>
                <div>
                  <div className="text-3xl font-bold text-green-600">{stats.resolutionRate.toFixed(0)}%</div>
                  <div className="text-sm text-gray-600">Resolution Rate</div>
                </div>
                <div>
                  <div className="text-3xl font-bold text-red-600">{stats.criticalLocations}</div>
                  <div className="text-sm text-gray-600">Critical Locations</div>
                </div>
              </div>
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>
    </div>
  )
}