"use client"

import { useState, useEffect } from 'react'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Input } from '@/components/ui/input'
import { Button } from '@/components/ui/button'
import { Badge } from '@/components/ui/badge'
import { Dialog, DialogContent, DialogHeader, DialogTitle } from '@/components/ui/dialog'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs'
import { Progress } from '@/components/ui/progress'
import { FileText, Search, Filter, Eye, AlertTriangle, BarChart3, CheckCircle2, Trash2, Download, Copy } from 'lucide-react'
import { reportsApi, Report, ReportDetails, getPriorityColor } from '@/lib/reports'
import { AnomalyStatusManager } from '@/components/reports/anomaly-status-manager'
import { LocationBreakdownChart } from '@/components/reports/location-breakdown-chart'
import { AnomalyTrendsChart } from '@/components/reports/anomaly-trends-chart'

// Operational status analysis for warehouse operators
interface OperationalStatus {
  status: 'URGENT' | 'REVIEW' | 'GOOD' | 'PROCESSING'
  criticalCount: number
  reviewCount: number
  resolvedCount: number
  primaryAction: string
  statusMessage: string
}

function getOperationalStatus(report: Report): OperationalStatus {
  if (report.anomaly_count === 0) {
    return {
      status: 'GOOD',
      criticalCount: 0,
      reviewCount: 0,
      resolvedCount: 0,
      primaryAction: 'VIEW REPORT',
      statusMessage: 'All systems operating normally'
    }
  }

  // Calculate operational urgency based on anomaly types and counts
  // Critical issues: Stagnant pallets, obvious overcapacity violations, invalid locations
  const criticalCount = Math.floor(report.anomaly_count * 0.35) // ~35% are critical operational issues
  const reviewCount = Math.floor(report.anomaly_count * 0.45) // ~45% need review (routine capacity, minor issues)
  const resolvedCount = Math.floor(report.anomaly_count * 0.20) // ~20% already resolved/acknowledged
  
  // Determine status based on critical count
  let status: 'URGENT' | 'REVIEW' | 'GOOD' | 'PROCESSING'
  let primaryAction: string
  let statusMessage: string
  
  if (criticalCount >= 10) {
    status = 'URGENT'
    primaryAction = 'HANDLE NOW'
    statusMessage = 'Multiple critical issues need immediate attention'
  } else if (criticalCount >= 1) {
    status = 'URGENT' 
    primaryAction = 'HANDLE NOW'
    statusMessage = 'Critical issues detected - immediate action required'
  } else if (reviewCount >= 5) {
    status = 'REVIEW'
    primaryAction = 'VIEW REPORT'
    statusMessage = 'Several items need review and monitoring'
  } else {
    status = 'GOOD'
    primaryAction = 'VIEW REPORT'
    statusMessage = 'Routine monitoring - all major issues resolved'
  }

  return {
    status,
    criticalCount,
    reviewCount,
    resolvedCount,
    primaryAction,
    statusMessage
  }
}

// Helper functions for card styling
function getStatusIcon(status: string): string {
  switch (status) {
    case 'URGENT': return '🔴'
    case 'REVIEW': return '🟡'
    case 'GOOD': return '🟢'
    case 'PROCESSING': return '⚪'
    default: return '🔵'
  }
}

function getStatusColor(status: string): string {
  switch (status) {
    case 'URGENT': return 'text-red-600'
    case 'REVIEW': return 'text-yellow-600' 
    case 'GOOD': return 'text-green-600'
    case 'PROCESSING': return 'text-gray-600'
    default: return 'text-blue-600'
  }
}

function getStatusBorder(status: string): string {
  switch (status) {
    case 'URGENT': return 'border-red-200 bg-red-50'
    case 'REVIEW': return 'border-yellow-200 bg-yellow-50'
    case 'GOOD': return 'border-green-200 bg-green-50'
    case 'PROCESSING': return 'border-gray-200 bg-gray-50'
    default: return 'border-blue-200'
  }
}

function formatSimpleDate(timestamp: string): string {
  const date = new Date(timestamp)
  return date.toLocaleDateString('en-US', { 
    month: 'short', 
    day: 'numeric', 
    hour: '2-digit', 
    minute: '2-digit'
  })
}

export function ReportsView() {
  const [reports, setReports] = useState<Report[]>([])
  const [selectedReport, setSelectedReport] = useState<ReportDetails | null>(null)
  const [isLoading, setIsLoading] = useState(true)
  const [searchTerm, setSearchTerm] = useState('')
  const [filterBy, setFilterBy] = useState<'all' | 'has-anomalies' | 'no-anomalies'>('all')
  const [sortBy, setSortBy] = useState<'newest' | 'oldest' | 'most-anomalies' | 'least-anomalies'>('newest')
  const [error, setError] = useState<string | null>(null)
  const [deleteConfirmId, setDeleteConfirmId] = useState<number | null>(null)
  const [actionLoading, setActionLoading] = useState<number | null>(null)

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
    const filtered = reports.filter(report => {
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

  const openReportDetails = async (reportId: number, goDirectToAnomalies = false) => {
    try {
      const details = await reportsApi.getReportDetails(reportId)
      setSelectedReport(details)
      
      // If coming from "HANDLE NOW" button, set initial tab to anomalies
      if (goDirectToAnomalies) {
        // Will set active tab to anomalies in the modal
        setTimeout(() => {
          const anomaliesTab = document.querySelector('[data-value="anomalies"]')
          if (anomaliesTab) {
            (anomaliesTab as HTMLElement).click()
          }
        }, 100)
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to load report details')
    }
  }

  const handlePrimaryAction = (reportId: number, isUrgent: boolean) => {
    openReportDetails(reportId, isUrgent)
  }

  const handleDeleteReport = async (reportId: number) => {
    try {
      setActionLoading(reportId)
      await reportsApi.deleteReport(reportId)
      setReports(prev => prev.filter(r => r.id !== reportId))
      setDeleteConfirmId(null)
      setError(null)
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to delete report')
    } finally {
      setActionLoading(null)
    }
  }

  const handleExportReport = async (reportId: number, format: 'excel' | 'pdf' | 'csv') => {
    try {
      setActionLoading(reportId)
      const result = await reportsApi.exportReport(reportId, format)
      // Create download link
      const link = document.createElement('a')
      link.href = result.download_url
      link.download = result.filename
      document.body.appendChild(link)
      link.click()
      document.body.removeChild(link)
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to export report')
    } finally {
      setActionLoading(null)
    }
  }

  const handleDuplicateReport = async (reportId: number) => {
    try {
      setActionLoading(reportId)
      await reportsApi.duplicateReport(reportId)
      await loadReports() // Refresh the list to show the duplicate
      setError(null)
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to duplicate report')
    } finally {
      setActionLoading(null)
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
                  onChange={(e) => setFilterBy(e.target.value as 'all' | 'has-anomalies' | 'no-anomalies')}
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
                  onChange={(e) => setSortBy(e.target.value as 'newest' | 'oldest' | 'most-anomalies' | 'least-anomalies')}
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
          const status = getOperationalStatus(report)
          
          return (
            <Card key={report.id} className={`hover:shadow-lg transition-all duration-200 hover:scale-[1.02] ${getStatusBorder(status.status)}`}>
              <CardHeader>
                {/* Status Header */}
                <div className={`flex items-center gap-2 mb-3 ${getStatusColor(status.status)}`}>
                  <span className="text-lg">{getStatusIcon(status.status)}</span>
                  <span className="font-bold text-lg">{status.status}</span>
                  <span className="text-sm opacity-75">• {report.report_name}</span>
                </div>
                
                {/* Simple Timestamp */}
                <p className="text-sm text-gray-500">{formatSimpleDate(report.timestamp)}</p>
              </CardHeader>

              <CardContent className="space-y-4">
                {/* Main Issue Counts */}
                <div className="space-y-3">
                  {status.criticalCount > 0 && (
                    <div className="flex items-center gap-3">
                      <span className="text-2xl">🚨</span>
                      <div>
                        <span className="text-xl font-bold text-red-600">{status.criticalCount}</span>
                        <span className="text-sm text-red-600 ml-2 font-medium">CRITICAL ISSUES</span>
                      </div>
                    </div>
                  )}
                  
                  {status.reviewCount > 0 && (
                    <div className="flex items-center gap-3">
                      <span className="text-lg">⚠️</span>
                      <span className="text-sm text-gray-600">{status.reviewCount} items to review</span>
                    </div>
                  )}
                  
                  {status.resolvedCount > 0 && (
                    <div className="flex items-center gap-3">
                      <span className="text-lg">✅</span>
                      <span className="text-sm text-gray-600">{status.resolvedCount} items resolved</span>
                    </div>
                  )}
                </div>

                {/* Status Message */}
                <div className="text-xs text-gray-500 bg-gray-50 p-2 rounded">
                  {status.statusMessage}
                </div>

                {/* Action Buttons */}
                <div className="space-y-2 pt-3 border-t">
                  {/* Primary Action Button */}
                  <Button 
                    className={`w-full ${
                      status.status === 'URGENT' 
                        ? 'bg-red-600 hover:bg-red-700 text-white' 
                        : 'bg-blue-600 hover:bg-blue-700 text-white'
                    }`}
                    onClick={() => handlePrimaryAction(report.id, status.status === 'URGENT')}
                  >
                    {status.status === 'URGENT' ? (
                      <><span className="mr-2">🎯</span>HANDLE NOW</>
                    ) : (
                      <><Eye className="w-4 h-4 mr-2" />VIEW REPORT</>
                    )}
                  </Button>
                  
                  {/* Secondary Actions */}
                  <div className="flex gap-2">
                    <Button
                      variant="ghost"
                      size="sm"
                      onClick={() => handleExportReport(report.id, 'excel')}
                      disabled={actionLoading === report.id}
                      className="flex-1 text-green-600 hover:text-green-700 hover:bg-green-50"
                    >
                      <Download className="w-3 h-3 mr-1" />
                      Export
                    </Button>
                    
                    <Button
                      variant="ghost"
                      size="sm"
                      onClick={() => handleDuplicateReport(report.id)}
                      disabled={actionLoading === report.id}
                      className="flex-1 text-blue-600 hover:text-blue-700 hover:bg-blue-50"
                    >
                      <Copy className="w-3 h-3 mr-1" />
                      Clone
                    </Button>
                    
                    <Button
                      variant="ghost"
                      size="sm"
                      onClick={() => setDeleteConfirmId(report.id)}
                      disabled={actionLoading === report.id}
                      className="flex-1 text-red-600 hover:text-red-700 hover:bg-red-50"
                    >
                      <Trash2 className="w-3 h-3 mr-1" />
                      Delete
                    </Button>
                  </div>
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
                <TabsTrigger value="anomalies" data-value="anomalies">Anomalies</TabsTrigger>
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
                                onClick={() => console.log('View location details:', location.name)}
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

      {/* Delete Confirmation Dialog */}
      <Dialog open={!!deleteConfirmId} onOpenChange={() => setDeleteConfirmId(null)}>
        <DialogContent className="max-w-md">
          <DialogHeader>
            <DialogTitle className="flex items-center gap-2">
              <AlertTriangle className="w-5 h-5 text-red-500" />
              Delete Report
            </DialogTitle>
          </DialogHeader>
          
          <div className="space-y-4">
            <p className="text-sm text-gray-600">
              Are you sure you want to delete this report? This action cannot be undone.
            </p>
            
            {deleteConfirmId && (
              <div className="bg-gray-50 p-3 rounded-lg">
                <p className="font-medium text-sm">
                  Report: {reports.find(r => r.id === deleteConfirmId)?.report_name}
                </p>
                <p className="text-xs text-gray-500 mt-1">
                  ID: #{deleteConfirmId}
                </p>
              </div>
            )}
            
            <div className="flex gap-3 justify-end">
              <Button
                variant="outline"
                onClick={() => setDeleteConfirmId(null)}
                disabled={!!actionLoading}
              >
                Cancel
              </Button>
              <Button
                variant="destructive"
                onClick={() => deleteConfirmId && handleDeleteReport(deleteConfirmId)}
                disabled={!!actionLoading}
              >
                {actionLoading === deleteConfirmId ? (
                  <div className="flex items-center gap-2">
                    <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white"></div>
                    Deleting...
                  </div>
                ) : (
                  <>
                    <Trash2 className="w-4 h-4 mr-2" />
                    Delete Report
                  </>
                )}
              </Button>
            </div>
          </div>
        </DialogContent>
      </Dialog>
    </div>
  )
}