"use client"

import { useState, useEffect } from 'react'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Input } from '@/components/ui/input'
import { Button } from '@/components/ui/button'
import { Badge } from '@/components/ui/badge'
import { Dialog, DialogContent, DialogHeader, DialogTitle } from '@/components/ui/dialog'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs'
import { Progress } from '@/components/ui/progress'
import { Separator } from '@/components/ui/separator'
import { FileText, Search, Filter, Eye, Calendar, AlertTriangle, MapPin, BarChart3, Activity, Clock, CheckCircle2 } from 'lucide-react'
import { reportsApi, Report, ReportDetails, Anomaly, getPriorityColor, getStatusColor } from '@/lib/reports'
import { AnomalyStatusManager } from '@/components/reports/anomaly-status-manager'
import { LocationBreakdownChart } from '@/components/reports/location-breakdown-chart'
import { AnomalyTrendsChart } from '@/components/reports/anomaly-trends-chart'

export function ReportsView() {
  const [reports, setReports] = useState<Report[]>([])
  const [selectedReport, setSelectedReport] = useState<ReportDetails | null>(null)
  const [isLoading, setIsLoading] = useState(true)
  const [searchTerm, setSearchTerm] = useState('')
  const [filterBy, setFilterBy] = useState<'all' | 'has-anomalies' | 'no-anomalies'>('all')
  const [sortBy, setSortBy] = useState<'newest' | 'oldest' | 'most-anomalies' | 'least-anomalies'>('newest')
  const [selectedLocation, setSelectedLocation] = useState<string | null>(null)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    loadReports()
  }, [])

  const loadReports = async () => {
    try {
      setIsLoading(true)
      setError(null)
      const response = await reportsApi.getReports()
      const reportsData = response.reports || []
      setReports(reportsData)
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to load reports')
    } finally {
      setIsLoading(false)
    }
  }

  const filteredAndSortedReports = (() => {
    let filtered = reports.filter(report => {
      const matchesSearch = report.report_name.toLowerCase().includes(searchTerm.toLowerCase())
      const matchesFilter = filterBy === 'all' || 
        (filterBy === 'has-anomalies' && report.anomaly_count > 0) ||
        (filterBy === 'no-anomalies' && report.anomaly_count === 0)
      return matchesSearch && matchesFilter
    })

    return filtered.sort((a, b) => {
      switch (sortBy) {
        case 'newest':
          return new Date(b.timestamp).getTime() - new Date(a.timestamp).getTime()
        case 'oldest':
          return new Date(a.timestamp).getTime() - new Date(b.timestamp).getTime()
        case 'most-anomalies':
          return b.anomaly_count - a.anomaly_count
        case 'least-anomalies':
          return a.anomaly_count - b.anomaly_count
        default:
          return 0
      }
    })
  })()

  const openReportDetails = async (reportId: number) => {
    try {
      const details = await reportsApi.getReportDetails(reportId)
      setSelectedReport(details)
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to load report details')
    }
  }

  if (isLoading) {
    return (
      <div className="p-6">
        <div className="flex items-center justify-center h-64">
          <div className="text-center">
            <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto mb-4"></div>
            <p className="text-gray-600">Loading reports...</p>
          </div>
        </div>
      </div>
    )
  }

  return (
    <div className="p-6 space-y-6">
      {/* Header */}
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Reports</h1>
          <p className="text-gray-600">View and manage warehouse analysis reports</p>
        </div>
      </div>

      {/* Error Alert */}
      {error && (
        <div className="bg-red-50 border border-red-200 rounded-lg p-4">
          <div className="flex items-center">
            <AlertTriangle className="h-5 w-5 text-red-400 mr-2" />
            <p className="text-red-800">{error}</p>
          </div>
        </div>
      )}

      {/* Enhanced Filters */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Filter className="w-5 h-5" />
            Filters & Search
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="space-y-4">
            {/* Search Bar */}
            <div className="relative">
              <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 w-4 h-4" />
              <Input
                placeholder="Search reports by name..."
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                className="pl-10"
              />
            </div>
            
            {/* Filter Controls */}
            <div className="flex flex-wrap gap-4">
              <div className="flex items-center gap-2">
                <label className="text-sm font-medium">Filter:</label>
                <select 
                  value={filterBy} 
                  onChange={(e) => setFilterBy(e.target.value as any)}
                  className="px-3 py-1 border rounded-md text-sm"
                >
                  <option value="all">All Reports</option>
                  <option value="has-anomalies">With Anomalies</option>
                  <option value="no-anomalies">No Anomalies</option>
                </select>
              </div>
              
              <div className="flex items-center gap-2">
                <label className="text-sm font-medium">Sort by:</label>
                <select 
                  value={sortBy} 
                  onChange={(e) => setSortBy(e.target.value as any)}
                  className="px-3 py-1 border rounded-md text-sm"
                >
                  <option value="newest">Newest First</option>
                  <option value="oldest">Oldest First</option>
                  <option value="most-anomalies">Most Anomalies</option>
                  <option value="least-anomalies">Least Anomalies</option>
                </select>
              </div>
              
              <Button 
                variant="outline" 
                onClick={loadReports}
                disabled={isLoading}
                className="ml-auto"
              >
                Refresh
              </Button>
            </div>
            
            {/* Results Summary */}
            <div className="text-sm text-gray-600">
              Showing {filteredAndSortedReports.length} of {reports.length} reports
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Enhanced Reports Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {filteredAndSortedReports.map((report) => {
          const severityLevel = report.anomaly_count === 0 ? 'success' : 
            report.anomaly_count <= 5 ? 'warning' : 'error'
          
          return (
            <Card key={report.id} className="hover:shadow-lg transition-all duration-200 hover:scale-[1.02]">
              <CardHeader>
                <div className="flex items-start justify-between">
                  <div className="flex items-center gap-2 flex-1 min-w-0">
                    <FileText className="w-5 h-5 text-blue-600 flex-shrink-0" />
                    <CardTitle className="text-lg truncate">{report.report_name}</CardTitle>
                  </div>
                  <div className="flex flex-col items-end gap-1">
                    <Badge 
                      variant={report.anomaly_count > 0 ? "destructive" : "secondary"}
                      className="whitespace-nowrap"
                    >
                      {report.anomaly_count} anomalies
                    </Badge>
                    {report.anomaly_count > 0 && (
                      <div className={`w-2 h-2 rounded-full ${
                        severityLevel === 'error' ? 'bg-red-500' :
                        severityLevel === 'warning' ? 'bg-yellow-500' : 'bg-green-500'
                      }`} />
                    )}
                  </div>
                </div>
              </CardHeader>
              <CardContent className="space-y-3">
                <div className="grid grid-cols-2 gap-4 text-sm">
                  <div className="flex items-center gap-2 text-gray-600">
                    <MapPin className="w-4 h-4" />
                    <span>#{report.id}</span>
                  </div>
                  
                  <div className="flex items-center gap-2 text-gray-600">
                    <Calendar className="w-4 h-4" />
                    <span>{new Date(report.timestamp).toLocaleDateString()}</span>
                  </div>
                  
                  <div className="flex items-center gap-2 text-gray-600">
                    <Clock className="w-4 h-4" />
                    <span>{new Date(report.timestamp).toLocaleTimeString([], {hour: '2-digit', minute:'2-digit'})}</span>
                  </div>
                  
                  <div className="flex items-center gap-2 text-gray-600">
                    <Activity className="w-4 h-4" />
                    <span>{report.anomaly_count > 0 ? 'Active' : 'Clear'}</span>
                  </div>
                </div>

                <div className="pt-3 border-t">
                  <Button
                    variant="outline"
                    size="sm"
                    onClick={() => openReportDetails(report.id)}
                    className="w-full hover:bg-blue-50 hover:border-blue-300"
                  >
                    <Eye className="w-4 h-4 mr-2" />
                    View Details
                  </Button>
                </div>
              </CardContent>
            </Card>
          )
        })}
      </div>

      {/* Empty State */}
      {filteredAndSortedReports.length === 0 && !isLoading && (
        <Card>
          <CardContent className="text-center py-12">
            <FileText className="w-12 h-12 text-gray-400 mx-auto mb-4" />
            <h3 className="text-lg font-medium text-gray-900 mb-2">No reports found</h3>
            <p className="text-gray-600">
              {searchTerm || filterBy !== 'all' ? 'Try adjusting your search terms or filters' : 'Create your first analysis to see reports here'}
            </p>
            {(searchTerm || filterBy !== 'all') && (
              <Button 
                variant="outline" 
                size="sm" 
                className="mt-3"
                onClick={() => {
                  setSearchTerm('')
                  setFilterBy('all')
                }}
              >
                Clear Filters
              </Button>
            )}
          </CardContent>
        </Card>
      )}

      {/* Enhanced Report Details Modal */}
      <Dialog open={!!selectedReport} onOpenChange={() => setSelectedReport(null)}>
        <DialogContent className="max-w-6xl max-h-[90vh] overflow-y-auto">
          <DialogHeader>
            <DialogTitle className="flex items-center gap-2">
              <FileText className="w-5 h-5" />
              {selectedReport?.reportName}
            </DialogTitle>
          </DialogHeader>
          
          {selectedReport && (
            <Tabs defaultValue="overview" className="space-y-4">
              <TabsList className="grid w-full grid-cols-4">
                <TabsTrigger value="overview">Overview</TabsTrigger>
                <TabsTrigger value="locations">Locations</TabsTrigger>
                <TabsTrigger value="anomalies">Anomalies</TabsTrigger>
                <TabsTrigger value="analytics">Analytics</TabsTrigger>
              </TabsList>
              
              <TabsContent value="overview" className="space-y-6">
                {/* Report Metadata */}
                <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                  <div className="p-4 bg-gray-50 rounded-lg">
                    <label className="text-sm font-medium text-gray-500">Report ID</label>
                    <p className="text-lg font-semibold text-gray-900">#{selectedReport.reportId}</p>
                  </div>
                  <div className="p-4 bg-gray-50 rounded-lg">
                    <label className="text-sm font-medium text-gray-500">Status</label>
                    <div className="flex items-center gap-2 mt-1">
                      <CheckCircle2 className="w-4 h-4 text-green-600" />
                      <Badge variant="secondary">Completed</Badge>
                    </div>
                  </div>
                  <div className="p-4 bg-gray-50 rounded-lg">
                    <label className="text-sm font-medium text-gray-500">Generated</label>
                    <p className="text-lg font-semibold text-gray-900">
                      {new Date().toLocaleDateString()}
                    </p>
                  </div>
                  <div className="p-4 bg-gray-50 rounded-lg">
                    <label className="text-sm font-medium text-gray-500">Priority Level</label>
                    <p className="text-lg font-semibold text-gray-900">
                      {selectedReport.kpis.find(k => k.label === 'Priority Alerts')?.value || 0 > 0 ? 'High' : 'Normal'}
                    </p>
                  </div>
                </div>

                {/* KPIs */}
                <div>
                  <h3 className="text-lg font-semibold mb-4">Key Performance Indicators</h3>
                  <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-5 gap-4">
                    {selectedReport.kpis.map((kpi, index) => {
                      const isHighPriority = kpi.label === 'Priority Alerts' && Number(kpi.value) > 0
                      const isGoodMetric = kpi.label === 'Resolution Rate' && String(kpi.value).includes('%')
                      
                      return (
                        <Card key={index} className={`${isHighPriority ? 'border-red-200 bg-red-50' : isGoodMetric ? 'border-green-200 bg-green-50' : ''}`}>
                          <CardContent className="p-4 text-center">
                            <p className="text-sm font-medium text-gray-600 mb-1">{kpi.label}</p>
                            <p className={`text-2xl font-bold ${
                              isHighPriority ? 'text-red-600' : 
                              isGoodMetric ? 'text-green-600' : 'text-gray-900'
                            }`}>
                              {kpi.value}
                            </p>
                          </CardContent>
                        </Card>
                      )
                    })}
                  </div>
                </div>
                
                {/* Resolution Progress */}
                <div>
                  <h3 className="text-lg font-semibold mb-4">Resolution Progress</h3>
                  <Card>
                    <CardContent className="p-6">
                      <div className="space-y-4">
                        <div className="flex justify-between items-center">
                          <span className="text-sm font-medium">Overall Progress</span>
                          <span className="text-sm text-gray-500">
                            {selectedReport.kpis.find(k => k.label === 'Resolution Rate')?.value || '0%'}
                          </span>
                        </div>
                        <Progress 
                          value={parseInt(String(selectedReport.kpis.find(k => k.label === 'Resolution Rate')?.value || '0')) || 0} 
                          className="h-2"
                        />
                        <div className="grid grid-cols-4 gap-4 pt-4 border-t">
                          <div className="text-center">
                            <div className="w-3 h-3 bg-blue-500 rounded-full mx-auto mb-1"></div>
                            <p className="text-xs text-gray-600">New</p>
                          </div>
                          <div className="text-center">
                            <div className="w-3 h-3 bg-yellow-500 rounded-full mx-auto mb-1"></div>
                            <p className="text-xs text-gray-600">Acknowledged</p>
                          </div>
                          <div className="text-center">
                            <div className="w-3 h-3 bg-orange-500 rounded-full mx-auto mb-1"></div>
                            <p className="text-xs text-gray-600">In Progress</p>
                          </div>
                          <div className="text-center">
                            <div className="w-3 h-3 bg-green-500 rounded-full mx-auto mb-1"></div>
                            <p className="text-xs text-gray-600">Resolved</p>
                          </div>
                        </div>
                      </div>
                    </CardContent>
                  </Card>
                </div>
              </TabsContent>
              
              <TabsContent value="locations" className="space-y-6">
                <div>
                  <h3 className="text-lg font-semibold mb-4">Location Breakdown</h3>
                  
                  {/* Location Chart */}
                  <Card className="mb-6">
                    <CardHeader>
                      <CardTitle className="flex items-center gap-2">
                        <BarChart3 className="w-5 h-5" />
                        Anomalies by Location
                      </CardTitle>
                    </CardHeader>
                    <CardContent>
                      <LocationBreakdownChart locations={selectedReport.locations} />
                    </CardContent>
                  </Card>
                  
                  {/* Location List */}
                  <div className="grid gap-4">
                    {selectedReport.locations.map((location, index) => (
                      <Card key={index} className="hover:shadow-md transition-shadow">
                        <CardContent className="p-6">
                          <div className="flex items-center justify-between mb-4">
                            <div>
                              <h4 className="font-semibold text-lg">{location.name}</h4>
                              <p className="text-sm text-gray-500">{location.anomaly_count} anomalies detected</p>
                            </div>
                            <div className="flex items-center gap-2">
                              <Badge 
                                variant={location.anomaly_count > 5 ? "destructive" : location.anomaly_count > 0 ? "secondary" : "outline"}
                                className="px-3 py-1"
                              >
                                {location.anomaly_count} issues
                              </Badge>
                              <Button
                                variant="outline"
                                size="sm"
                                onClick={() => setSelectedLocation(location.name)}
                              >
                                View Details
                              </Button>
                            </div>
                          </div>
                          
                          {/* Priority breakdown */}
                          <div className="space-y-2">
                            <p className="text-sm font-medium text-gray-600">Priority Breakdown:</p>
                            <div className="flex gap-2 flex-wrap">
                              {['VERY HIGH', 'HIGH', 'MEDIUM', 'LOW'].map(priority => {
                                const count = location.anomalies?.filter(a => a.priority === priority).length || 0
                                if (count === 0) return null
                                return (
                                  <Badge key={priority} className={getPriorityColor(priority)}>
                                    {priority}: {count}
                                  </Badge>
                                )
                              })}
                            </div>
                          </div>
                        </CardContent>
                      </Card>
                    ))}
                  </div>
                </div>
              </TabsContent>
              
              <TabsContent value="anomalies" className="space-y-6">
                <AnomalyStatusManager 
                  reportId={selectedReport.reportId} 
                  locations={selectedReport.locations}
                  onStatusUpdate={() => {
                    // Refresh report details after status update
                    openReportDetails(selectedReport.reportId)
                  }}
                />
              </TabsContent>
              
              <TabsContent value="analytics" className="space-y-6">
                <div className="grid gap-6">
                  <Card>
                    <CardHeader>
                      <CardTitle>Anomaly Trends</CardTitle>
                    </CardHeader>
                    <CardContent>
                      <AnomalyTrendsChart reportData={selectedReport} />
                    </CardContent>
                  </Card>
                  
                  <div className="grid md:grid-cols-2 gap-6">
                    <Card>
                      <CardHeader>
                        <CardTitle>Priority Distribution</CardTitle>
                      </CardHeader>
                      <CardContent>
                        {/* Priority pie chart would go here */}
                        <div className="text-center py-8 text-gray-500">
                          Priority distribution chart
                        </div>
                      </CardContent>
                    </Card>
                    
                    <Card>
                      <CardHeader>
                        <CardTitle>Status Distribution</CardTitle>
                      </CardHeader>
                      <CardContent>
                        {/* Status pie chart would go here */}
                        <div className="text-center py-8 text-gray-500">
                          Status distribution chart
                        </div>
                      </CardContent>
                    </Card>
                  </div>
                </div>
              </TabsContent>
            </Tabs>
          )}
        </DialogContent>
      </Dialog>
    </div>
  )
}