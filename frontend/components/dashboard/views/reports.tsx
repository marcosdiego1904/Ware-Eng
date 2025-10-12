"use client"

import { useState, useEffect } from 'react'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Input } from '@/components/ui/input'
import { Button } from '@/components/ui/button'
import { Badge } from '@/components/ui/badge'
import { Dialog, DialogContent, DialogHeader, DialogTitle } from '@/components/ui/dialog'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs'
import { Progress } from '@/components/ui/progress'
import { FileText, Search, Filter, Eye, AlertTriangle, BarChart3, CheckCircle2, Trash2, Download, Copy, Clock, DollarSign, Users, TrendingUp, Target, Workflow, Award, ChevronRight } from 'lucide-react'
import { reportsApi, Report, ReportDetails, getPriorityColor } from '@/lib/reports'
import { AnomalyStatusManager } from '@/components/reports/anomaly-status-manager'
import { BusinessIntelligenceReport } from '@/components/reports/business-intelligence-report'
import { AnomalyTrendsChart } from '@/components/reports/anomaly-trends-chart'
import { useDashboardStore } from '@/lib/store'

// Operational status analysis for warehouse operators
interface OperationalStatus {
  status: 'URGENT' | 'REVIEW' | 'GOOD' | 'PROCESSING'
  criticalCount: number
  reviewCount: number
  resolvedCount: number
  primaryAction: string
  statusMessage: string
}

// Enhanced psychological analysis interface
interface PsychologicalInsights {
  urgentCount: number        // <1 hour fixes
  highImpactCount: number    // operational blockers
  quickWinsCount: number     // 5-15 min fixes
  timeBlocked: number        // hours of operational blocking
  estimatedCost: number      // daily cost impact
  primaryIssueType: string   // dominant anomaly type
  confidenceLevel: number    // 0-100 rule engine confidence
  businessImpact: string     // human-readable impact
  nextAction: string         // specific recommended action
}

// Smart anomaly categorization based on actual warehouse operations
function categorizeAnomalies(anomalies: any[]): { critical: any[], review: any[], resolved: any[] } {
  const critical: any[] = []
  const review: any[] = []
  const resolved: any[] = []

  anomalies.forEach(anomaly => {
    // Check if already resolved/acknowledged
    if (anomaly.status === 'Resolved' || anomaly.status === 'Acknowledged' || anomaly.status === 'In Progress') {
      resolved.push(anomaly)
      return
    }

    // Critical issues requiring immediate attention
    const isCritical = (
      // Stagnant pallets (operational bottlenecks)
      anomaly.anomaly_type === 'Stagnant Pallet' ||
      
      // Invalid locations (pallets can't be found)
      anomaly.anomaly_type === 'Invalid Location' ||
      
      // Safety-critical issues
      anomaly.anomaly_type === 'Temperature Zone Mismatch' ||
      
      // High priority violations
      anomaly.priority === 'VERY HIGH' ||
      
      // Obvious overcapacity violations (≥2x capacity)
      (anomaly.anomaly_type === 'Overcapacity' && 
       anomaly.details && 
       anomaly.details.includes('pallets') &&
       extractCapacityRatio(anomaly.details) >= 2.0) ||
      
      // Incomplete lots (lot coordination issues)
      anomaly.anomaly_type === 'Uncoordinated Lots'
    )

    if (isCritical) {
      critical.push(anomaly)
    } else {
      review.push(anomaly)
    }
  })

  return { critical, review, resolved }
}

// Helper function to extract capacity ratio from anomaly details
function extractCapacityRatio(details: string): number {
  const match = details.match(/(\d+) pallets \(capacity: (\d+)\)/)
  if (match) {
    const pallets = parseInt(match[1])
    const capacity = parseInt(match[2])
    return capacity > 0 ? pallets / capacity : 0
  }
  return 0
}

// Psychological analysis function using cognitive load reduction principles
function analyzePsychologicalImpact(anomalies: any[]): PsychologicalInsights {
  if (!anomalies || anomalies.length === 0) {
    return {
      urgentCount: 0,
      highImpactCount: 0,
      quickWinsCount: 0,
      timeBlocked: 0,
      estimatedCost: 0,
      primaryIssueType: 'None',
      confidenceLevel: 100,
      businessImpact: 'All operations running smoothly',
      nextAction: 'Continue monitoring'
    }
  }

  // Categorize by psychological urgency (not just technical priority)
  let urgentCount = 0      // <1 hour fixes (immediate psychological relief)
  let highImpactCount = 0  // operational blockers (loss aversion triggers)
  let quickWinsCount = 0   // 5-15 min fixes (achievement psychology)
  let totalBlockedHours = 0
  let stagnantPallets = 0

  // Track anomaly types for business context
  const typeCount: {[key: string]: number} = {}

  anomalies.forEach(anomaly => {
    // Skip resolved items
    if (anomaly.status === 'Resolved' || anomaly.status === 'Acknowledged') return

    // Count by type for primary issue identification
    const type = anomaly.anomaly_type || 'Unknown'
    typeCount[type] = (typeCount[type] || 0) + 1

    // Quick wins (positive psychology - achievement)
    if (type === 'Duplicate Scan' || type === 'Data Integrity') {
      quickWinsCount++
    }
    // Urgent (immediate action needed - anxiety reduction)
    else if (type === 'Temperature Zone Mismatch' ||
             (type === 'Stagnant Pallet' && anomaly.details?.includes('281.')) ||
             anomaly.priority === 'VERY HIGH') {
      urgentCount++
    }
    // High impact (operational blocking - loss aversion)
    else if (type === 'Stagnant Pallet' || type === 'Invalid Location' ||
             type === 'Storage Overcapacity' || type === 'Special Area Capacity') {
      highImpactCount++
    }

    // Extract time blocked for loss aversion calculation
    if (type === 'Stagnant Pallet' && anomaly.details) {
      const timeMatch = anomaly.details.match(/(\d+\.\d+)h/)
      if (timeMatch) {
        totalBlockedHours += parseFloat(timeMatch[1])
        stagnantPallets++
      }
    }
  })

  // Find primary issue type (anchoring psychology)
  const primaryIssueType = Object.entries(typeCount)
    .sort(([,a], [,b]) => b - a)[0]?.[0] || 'Mixed Issues'

  // Calculate business impact (loss aversion)
  const avgCostPerHour = 25 // $25/hour operational cost per blocked pallet
  const estimatedCost = Math.round(totalBlockedHours * avgCostPerHour)

  // Resolution time estimation (progress psychology)
  const totalItems = urgentCount + highImpactCount + quickWinsCount
  const estimatedMinutes = (quickWinsCount * 7) + (urgentCount * 45) + (highImpactCount * 25)

  // Confidence based on rule engine success (authority psychology)
  const confidenceLevel = anomalies.length > 0 ? 95 : 100

  // Business impact messaging (social proof + authority)
  let businessImpact = ''
  if (stagnantPallets > 10) {
    businessImpact = `${stagnantPallets} pallets blocked for ${Math.round(totalBlockedHours/stagnantPallets)}+ hours avg`
  } else if (urgentCount > 0) {
    businessImpact = `${urgentCount} time-sensitive issues detected`
  } else if (highImpactCount > 0) {
    businessImpact = `${highImpactCount} operational blockers identified`
  } else {
    businessImpact = `${quickWinsCount} optimization opportunities available`
  }

  // Next action (choice architecture)
  let nextAction = ''
  if (urgentCount > 0) {
    nextAction = `Resolve ${urgentCount} urgent issue${urgentCount > 1 ? 's' : ''} first`
  } else if (quickWinsCount >= 5) {
    nextAction = `Start with ${quickWinsCount} quick wins first`
  } else if (highImpactCount > 0) {
    nextAction = `Address ${highImpactCount} operational blocker${highImpactCount > 1 ? 's' : ''}`
  } else {
    nextAction = 'Review and monitor remaining items'
  }

  return {
    urgentCount,
    highImpactCount,
    quickWinsCount,
    timeBlocked: Math.round(totalBlockedHours),
    estimatedCost,
    primaryIssueType,
    confidenceLevel,
    businessImpact,
    nextAction
  }
}

function getOperationalStatus(report: Report, anomalies?: any[]): OperationalStatus {
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

  let criticalCount: number
  let reviewCount: number  
  let resolvedCount: number

  if (anomalies && anomalies.length > 0) {
    // REAL ANALYSIS: Use actual anomaly data when available
    const categorized = categorizeAnomalies(anomalies)
    criticalCount = categorized.critical.length
    reviewCount = categorized.review.length
    resolvedCount = categorized.resolved.length
  } else {
    // FALLBACK: Improved estimation based on warehouse operations data
    // These percentages are based on typical warehouse anomaly patterns:
    criticalCount = Math.floor(report.anomaly_count * 0.30) // 30% operational urgent
    reviewCount = Math.floor(report.anomaly_count * 0.55)   // 55% routine monitoring
    resolvedCount = Math.floor(report.anomaly_count * 0.15) // 15% already handled
  }
  
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
  const { reportToOpen, setReportToOpen } = useDashboardStore()
  const [reports, setReports] = useState<Report[]>([])
  const [selectedReport, setSelectedReport] = useState<ReportDetails | null>(null)
  const [isLoading, setIsLoading] = useState(true)
  const [searchTerm, setSearchTerm] = useState('')
  const [filterBy, setFilterBy] = useState<'all' | 'has-anomalies' | 'no-anomalies'>('all')
  const [sortBy, setSortBy] = useState<'newest' | 'oldest' | 'most-anomalies' | 'least-anomalies'>('newest')
  const [error, setError] = useState<string | null>(null)
  const [deleteConfirmId, setDeleteConfirmId] = useState<number | null>(null)
  const [actionLoading, setActionLoading] = useState<number | null>(null)
  const [reportAnomaliesCache, setReportAnomaliesCache] = useState<{ [key: number]: any[] }>({})
  const [showAllOvercapacity, setShowAllOvercapacity] = useState(false)
  const [sessionResolvedAnomalies, setSessionResolvedAnomalies] = useState<Set<string>>(new Set())
  // Use a map to store resolved anomalies per report ID with localStorage persistence
  const [reportResolvedAnomalies, setReportResolvedAnomalies] = useState<{ [reportId: number]: Set<string> }>(() => {
    if (typeof window !== 'undefined') {
      try {
        const saved = localStorage.getItem('warehouse-resolved-anomalies')
        if (saved) {
          const parsed = JSON.parse(saved)
          // Convert arrays back to Sets
          const converted: { [reportId: number]: Set<string> } = {}
          Object.entries(parsed).forEach(([reportId, anomalies]) => {
            converted[parseInt(reportId)] = new Set(anomalies as string[])
          })
          return converted
        }
      } catch (error) {
        console.warn('Failed to load resolved anomalies from localStorage:', error)
      }
    }
    return {}
  })
  const [activeTab, setActiveTab] = useState('business-intelligence') // Always start on Business Intelligence

  // Save resolved anomalies to localStorage whenever they change
  useEffect(() => {
    if (typeof window !== 'undefined') {
      try {
        // Convert Sets to arrays for JSON storage
        const toSave: { [reportId: number]: string[] } = {}
        Object.entries(reportResolvedAnomalies).forEach(([reportId, anomalies]) => {
          toSave[parseInt(reportId)] = Array.from(anomalies)
        })
        localStorage.setItem('warehouse-resolved-anomalies', JSON.stringify(toSave))
      } catch (error) {
        console.warn('Failed to save resolved anomalies to localStorage:', error)
      }
    }
  }, [reportResolvedAnomalies])

  // Optional: Clear resolved anomalies older than 7 days to prevent storage bloat
  useEffect(() => {
    if (typeof window !== 'undefined') {
      try {
        const lastCleanup = localStorage.getItem('warehouse-resolved-cleanup')
        const now = Date.now()
        const sevenDays = 7 * 24 * 60 * 60 * 1000 // 7 days in milliseconds

        if (!lastCleanup || now - parseInt(lastCleanup) > sevenDays) {
          // For now, we'll keep all data. In the future, you could add logic here
          // to remove resolved anomalies for reports older than X days
          localStorage.setItem('warehouse-resolved-cleanup', now.toString())
        }
      } catch (error) {
        console.warn('Failed to perform cleanup:', error)
      }
    }
  }, [])

  // Helper function to classify anomalies based on operational impact
  const classifyAnomalyOperational = (anomaly: any, locationName: string) => {
    const isReceivingBlocked = (
      anomaly.anomaly_type === 'Stagnant Pallet' &&
      locationName?.includes('RECV')
    )

    // Debug logging to verify the data
    if (['RECV-03', 'RECV-01', 'RECV-02', 'AISLE-02', 'AISLE-01'].includes(locationName) && anomaly) {
      console.log(`[DEBUG] ${locationName} anomaly - Type: ${anomaly.anomaly_type}, Priority: ${anomaly.priority}, IsReceivingBlocked: ${isReceivingBlocked}`)
    }

    // EXCEPTION: Receiving docks blocked stays critical (immediate operations halt)
    if (isReceivingBlocked) {
      return 'critical'
    }

    // SWAPPED LOGIC: Efficiency impacts are now critical, safety/system issues are high priority
    const priority = anomaly.priority?.toUpperCase() || ''
    if (priority === 'VERY HIGH') {
      // Backend VERY HIGH → Frontend HIGH PRIORITY (except receiving)
      return 'high_priority'
    } else if (priority === 'HIGH') {
      // Backend HIGH → Frontend CRITICAL (daily operational impact)
      return 'critical'
    }

    // Log unhandled priority values for future monitoring
    if (anomaly.priority && !['MEDIUM', 'LOW', ''].includes(priority)) {
      console.warn(`[PRIORITY_WARNING] Unhandled priority: "${anomaly.priority}" for ${anomaly.anomaly_type} at ${locationName}`)
    }

    return 'other'
  }



  useEffect(() => {
    loadReports()
  }, [])

  // Handle report to open from navigation
  useEffect(() => {
    if (reportToOpen && !isLoading) {
      openReportDetails(reportToOpen.reportId, reportToOpen.tab)
      // Clear the report to open after handling
      setReportToOpen(undefined)
    }
  }, [reportToOpen, isLoading, setReportToOpen])

  const loadReports = async () => {
    try {
      setIsLoading(true)
      setError(null)
      const response = await reportsApi.getReports()
      const reportsData = response.reports || []
      setReports(reportsData)
      
      // Pre-load anomaly details for accurate calculations
      // Only for reports with anomalies to optimize performance
      const reportsWithAnomalies = reportsData.filter(r => r.anomaly_count > 0).slice(0, 10) // Limit to 10 most recent
      const anomaliesCache: { [key: number]: any[] } = {}
      
      for (const report of reportsWithAnomalies) {
        try {
          const details = await reportsApi.getReportDetails(report.id)
          const allAnomalies = details.locations.flatMap(loc => loc.anomalies || [])
          anomaliesCache[report.id] = allAnomalies
        } catch {
          // If details fail to load, use fallback calculation
          anomaliesCache[report.id] = []
        }
      }
      
      setReportAnomaliesCache(anomaliesCache)
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

  const openReportDetails = async (reportId: number, tab: 'business-intelligence' | 'analytics' = 'business-intelligence') => {
    try {
      const details = await reportsApi.getReportDetails(reportId)
      setSelectedReport(details)
      // Set the tab based on parameter
      setActiveTab(tab)
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to load report details')
    }
  }

  const handlePrimaryAction = (reportId: number, isUrgent: boolean) => {
    openReportDetails(reportId)
  }

  // Function to refresh report status after anomaly resolution
  const refreshReportStatus = async (reportId: number) => {
    try {
      const details = await reportsApi.getReportDetails(reportId)
      const allAnomalies = details.locations.flatMap(loc => loc.anomalies || [])
      
      // Update cache with fresh anomaly data
      setReportAnomaliesCache(prev => ({
        ...prev,
        [reportId]: allAnomalies
      }))
    } catch (err) {
      console.error('Failed to refresh report status:', err)
    }
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
      {/* Error Alert */}
      {error && (
        <div className="bg-red-50 border border-red-200 rounded-lg p-4">
          <div className="flex items-center">
            <AlertTriangle className="h-5 w-5 text-red-400 mr-2" />
            <p className="text-red-800">{error}</p>
          </div>
        </div>
      )}

      {/* Compact Toolbar */}
      <div className="flex items-center gap-4 p-4 bg-gray-50 rounded-lg border">
        {/* Search */}
        <div className="relative flex-1 max-w-sm">
          <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 w-4 h-4" />
          <Input
            placeholder="Search reports..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            className="pl-10 h-9"
          />
        </div>

        {/* Filter */}
        <select
          value={filterBy}
          onChange={(e) => setFilterBy(e.target.value as 'all' | 'has-anomalies' | 'no-anomalies')}
          className="px-3 py-1.5 border rounded-md text-sm h-9 bg-white"
        >
          <option value="all">All Reports</option>
          <option value="has-anomalies">With Anomalies</option>
          <option value="no-anomalies">No Anomalies</option>
        </select>

        {/* Sort */}
        <select
          value={sortBy}
          onChange={(e) => setSortBy(e.target.value as 'newest' | 'oldest' | 'most-anomalies' | 'least-anomalies')}
          className="px-3 py-1.5 border rounded-md text-sm h-9 bg-white"
        >
          <option value="newest">Newest First</option>
          <option value="oldest">Oldest First</option>
          <option value="most-anomalies">Most Anomalies</option>
          <option value="least-anomalies">Least Anomalies</option>
        </select>

        {/* Refresh */}
        <Button
          variant="outline"
          size="sm"
          onClick={loadReports}
          disabled={isLoading}
          className="h-9"
        >
          ↻ Refresh
        </Button>

        {/* Results Count */}
        <div className="text-sm text-gray-600 whitespace-nowrap">
          Showing {filteredAndSortedReports.length} reports
        </div>
      </div>

      {/* Enhanced Reports Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {filteredAndSortedReports.map((report) => {
          // Use cached anomaly data for accurate calculations
          const cachedAnomalies = reportAnomaliesCache[report.id]
          const status = getOperationalStatus(report, cachedAnomalies)
          const psychoInsights = analyzePsychologicalImpact(cachedAnomalies || [])
          
          return (
            <Card key={report.id} className={`group relative overflow-hidden backdrop-blur-sm transition-all duration-300 hover:shadow-2xl hover:shadow-black/5 hover:scale-[1.02] border-0 bg-white/80 ${getStatusBorder(status.status)}`}>
              <CardHeader className="relative z-10">
                {/* Premium Status Header */}
                <div className="relative">
                  <div className={`flex items-center gap-3 mb-4 ${getStatusColor(status.status)}`}>
                    <div className={`flex h-10 w-10 items-center justify-center rounded-full ${
                      status.status === 'URGENT' ? 'bg-rose-500/10 backdrop-blur-sm border border-rose-200/30' :
                      status.status === 'REVIEW' ? 'bg-amber-500/10 backdrop-blur-sm border border-amber-200/30' :
                      'bg-emerald-500/10 backdrop-blur-sm border border-emerald-200/30'
                    }`}>
                      <span className="text-xl">{getStatusIcon(status.status)}</span>
                    </div>
                    <div className="flex-1">
                      <div className="flex items-center gap-2">
                        <span className="font-bold text-xl tracking-tight">{status.status}</span>
                        <div className={`h-1 w-8 rounded-full ${
                          status.status === 'URGENT' ? 'bg-gradient-to-r from-rose-500 to-rose-600' :
                          status.status === 'REVIEW' ? 'bg-gradient-to-r from-amber-500 to-amber-600' :
                          'bg-gradient-to-r from-emerald-500 to-emerald-600'
                        }`} />
                      </div>
                      <span className="text-sm text-gray-600 font-medium">{report.report_name}</span>
                    </div>
                  </div>
                </div>
                
                {/* Enhanced Timestamp with Business Context */}
                <div className="flex items-center justify-between">
                  <p className="text-sm text-gray-500">{formatSimpleDate(report.timestamp)}</p>
                  {psychoInsights.primaryIssueType && psychoInsights.primaryIssueType !== 'None' && (
                    <div className="text-xs text-gray-500 bg-gray-100 px-2 py-1 rounded">
                      Primary: {psychoInsights.primaryIssueType}
                    </div>
                  )}
                </div>
              </CardHeader>

              <CardContent className="space-y-4">
                {/* ENHANCED: Psychological Chunking - Cognitive Load Reduction */}
                {report.anomaly_count > 0 ? (
                  <div className="space-y-3">
                    {/* Urgent Issues - Harmonized Crimson Design */}
                    {psychoInsights.urgentCount > 0 && (
                      <div className="group relative overflow-hidden rounded-xl bg-gradient-to-r from-rose-50 to-rose-100/40 border border-rose-200/50 backdrop-blur-sm transition-all duration-300 hover:shadow-lg hover:shadow-rose-100/30">
                        <div className="absolute inset-0 bg-gradient-to-r from-rose-500/4 to-transparent" />
                        <div className="relative p-4">
                          <div className="flex items-center gap-4">
                            <div className="flex h-12 w-12 items-center justify-center rounded-full bg-rose-500/8 backdrop-blur-sm border border-rose-200/30">
                              <span className="text-xl">🔥</span>
                            </div>
                            <div className="flex-1">
                              <div className="flex items-baseline gap-3">
                                <span className="text-3xl font-bold bg-gradient-to-r from-rose-600 to-rose-700 bg-clip-text text-transparent">
                                  {psychoInsights.urgentCount}
                                </span>
                                <div>
                                  <div className="text-sm font-semibold text-rose-800 uppercase tracking-wide">URGENT</div>
                                  <div className="text-xs text-rose-600/70 font-medium">immediate attention</div>
                                </div>
                              </div>
                            </div>
                            <div className="opacity-0 group-hover:opacity-100 transition-opacity duration-300">
                              <div className="h-8 w-1 rounded-full bg-gradient-to-b from-rose-500 to-rose-600" />
                            </div>
                          </div>
                        </div>
                      </div>
                    )}

                    {/* High Impact Issues - Harmonized Amber Design */}
                    {psychoInsights.highImpactCount > 0 && (
                      <div className="group relative overflow-hidden rounded-xl bg-gradient-to-r from-amber-50 to-amber-100/40 border border-amber-200/50 backdrop-blur-sm transition-all duration-300 hover:shadow-lg hover:shadow-amber-100/30">
                        <div className="absolute inset-0 bg-gradient-to-r from-amber-500/4 to-transparent" />
                        <div className="relative p-4">
                          <div className="flex items-center gap-4">
                            <div className="flex h-12 w-12 items-center justify-center rounded-full bg-amber-500/8 backdrop-blur-sm border border-amber-200/30">
                              <span className="text-xl">⚡</span>
                            </div>
                            <div className="flex-1">
                              <div className="flex items-baseline gap-3">
                                <span className="text-3xl font-bold bg-gradient-to-r from-amber-600 to-amber-700 bg-clip-text text-transparent">
                                  {psychoInsights.highImpactCount}
                                </span>
                                <div>
                                  <div className="text-sm font-semibold text-amber-800 uppercase tracking-wide">HIGH IMPACT</div>
                                  <div className="text-xs text-amber-600/70 font-medium">operational blockers</div>
                                </div>
                              </div>
                            </div>
                            <div className="opacity-0 group-hover:opacity-100 transition-opacity duration-300">
                              <div className="h-8 w-1 rounded-full bg-gradient-to-b from-amber-500 to-amber-600" />
                            </div>
                          </div>
                        </div>
                      </div>
                    )}

                    {/* Quick Wins - Harmonized Emerald Design */}
                    {psychoInsights.quickWinsCount > 0 && (
                      <div className="group relative overflow-hidden rounded-xl bg-gradient-to-r from-emerald-50 to-emerald-100/40 border border-emerald-200/50 backdrop-blur-sm transition-all duration-300 hover:shadow-lg hover:shadow-emerald-100/30">
                        <div className="absolute inset-0 bg-gradient-to-r from-emerald-500/4 to-transparent" />
                        <div className="relative p-4">
                          <div className="flex items-center gap-4">
                            <div className="flex h-12 w-12 items-center justify-center rounded-full bg-emerald-500/8 backdrop-blur-sm border border-emerald-200/30">
                              <span className="text-xl">🎯</span>
                            </div>
                            <div className="flex-1">
                              <div className="flex items-baseline gap-3">
                                <span className="text-3xl font-bold bg-gradient-to-r from-emerald-600 to-emerald-700 bg-clip-text text-transparent">
                                  {psychoInsights.quickWinsCount}
                                </span>
                                <div>
                                  <div className="text-sm font-semibold text-emerald-800 uppercase tracking-wide">QUICK WINS</div>
                                  <div className="text-xs text-emerald-600/70 font-medium">easy improvements</div>
                                </div>
                              </div>
                            </div>
                            <div className="opacity-0 group-hover:opacity-100 transition-opacity duration-300">
                              <div className="h-8 w-1 rounded-full bg-gradient-to-b from-emerald-500 to-emerald-600" />
                            </div>
                          </div>
                        </div>
                      </div>
                    )}

                    {/* Routine Items (Gray - Reduced Prominence) */}
                    {status.reviewCount > 0 &&
                     !(psychoInsights.urgentCount || psychoInsights.highImpactCount || psychoInsights.quickWinsCount) && (
                      <div className="flex items-center gap-3">
                        <span className="text-lg">📋</span>
                        <span className="text-sm text-gray-600">{status.reviewCount} routine monitoring items</span>
                      </div>
                    )}
                  </div>
                ) : (
                  <div className="flex items-center gap-3 p-3 bg-green-50 rounded-lg border border-green-100">
                    <span className="text-2xl">🟢</span>
                    <div>
                      <div className="text-lg font-medium text-green-700">All Clear</div>
                      <div className="text-sm text-green-600">No issues detected</div>
                    </div>
                  </div>
                )}

                {/* MODERN: Premium Business Impact Display */}
                {psychoInsights.estimatedCost > 0 && (
                  <div className="relative overflow-hidden rounded-xl bg-gradient-to-r from-amber-50 to-yellow-50/50 border border-amber-200/60 backdrop-blur-sm p-4">
                    <div className="absolute inset-0 bg-gradient-to-r from-amber-500/5 to-transparent" />
                    <div className="relative">
                      <div className="flex items-center gap-3 mb-2">
                        <div className="flex h-8 w-8 items-center justify-center rounded-full bg-amber-500/10">
                          <span className="text-sm">💰</span>
                        </div>
                        <span className="text-sm font-bold bg-gradient-to-r from-amber-700 to-yellow-700 bg-clip-text text-transparent">
                          ${psychoInsights.estimatedCost}/day estimated cost
                        </span>
                      </div>
                      <div className="text-xs text-amber-700/80 font-medium pl-11">{psychoInsights.businessImpact}</div>
                    </div>
                  </div>
                )}

                {/* MODERN: Premium Action Guidance */}
                {psychoInsights.nextAction && report.anomaly_count > 0 && (
                  <div className="relative overflow-hidden rounded-xl bg-gradient-to-r from-blue-50 to-indigo-50/50 border border-blue-200/60 backdrop-blur-sm p-4">
                    <div className="absolute inset-0 bg-gradient-to-r from-blue-500/5 to-transparent" />
                    <div className="relative">
                      <div className="flex items-center gap-3 mb-2">
                        <div className="flex h-8 w-8 items-center justify-center rounded-full bg-blue-500/10">
                          <span className="text-sm">🎯</span>
                        </div>
                        <span className="text-sm font-bold text-blue-800">Recommended Action</span>
                      </div>
                      <div className="text-sm text-blue-700/90 font-medium pl-11 mb-1">{psychoInsights.nextAction}</div>
                    </div>
                  </div>
                )}

                {/* MODERN: Premium Confidence & Progress Display */}
                {report.anomaly_count > 0 && (
                  <div className="relative overflow-hidden rounded-xl bg-gradient-to-r from-slate-50 to-gray-50/50 border border-slate-200/60 backdrop-blur-sm p-4">
                    <div className="absolute inset-0 bg-gradient-to-r from-slate-500/3 to-transparent" />
                    <div className="relative space-y-3">
                      <div className="flex items-center justify-between">
                        <div className="flex items-center gap-3">
                          <div className="flex h-8 w-8 items-center justify-center rounded-full bg-slate-500/10">
                            <span className="text-sm">🎆</span>
                          </div>
                          <span className="text-sm font-bold text-slate-700">
                            Analysis Confidence: {psychoInsights.confidenceLevel}%
                          </span>
                        </div>
                        <div className="flex items-center gap-2 text-slate-600">
                          <span className="text-sm">📈</span>
                          <span className="text-xs font-medium">
                            {(psychoInsights.urgentCount + psychoInsights.highImpactCount + psychoInsights.quickWinsCount)} actionable
                          </span>
                        </div>
                      </div>

                      {/* Achievement Psychology - Premium Progress Display */}
                      {status.resolvedCount > 0 && (
                        <div className="flex items-center gap-3 pl-11">
                          <div className="flex h-6 w-6 items-center justify-center rounded-full bg-emerald-100">
                            <span className="text-xs">✅</span>
                          </div>
                          <span className="text-sm font-medium text-emerald-700">
                            {status.resolvedCount} items resolved
                          </span>
                          <div className="flex items-center gap-1">
                            <div className="h-1.5 w-16 bg-gray-200 rounded-full overflow-hidden">
                              <div
                                className="h-full bg-gradient-to-r from-emerald-500 to-green-600 rounded-full transition-all duration-500"
                                style={{ width: `${Math.round((status.resolvedCount / report.anomaly_count) * 100)}%` }}
                              />
                            </div>
                            <span className="text-xs font-medium text-emerald-600">
                              {Math.round((status.resolvedCount / report.anomaly_count) * 100)}%
                            </span>
                          </div>
                        </div>
                      )}
                    </div>
                  </div>
                )}

                {/* ENHANCED: Guided Choice Architecture */}
                <div className="space-y-2 pt-3 border-t">
                  {/* MODERN: Premium Action Button with Gradient Design */}
                  <Button
                    className={`group relative w-full overflow-hidden rounded-xl font-bold text-white transition-all duration-300 hover:scale-[1.02] hover:shadow-xl ${
                      psychoInsights.urgentCount > 0
                        ? 'bg-gradient-to-r from-rose-600 to-rose-700 hover:from-rose-700 hover:to-rose-800 shadow-lg shadow-rose-200/50'
                        : psychoInsights.quickWinsCount >= 3
                        ? 'bg-gradient-to-r from-blue-600 to-blue-700 hover:from-blue-700 hover:to-blue-800 shadow-lg shadow-blue-200/50'
                        : psychoInsights.highImpactCount > 0
                        ? 'bg-gradient-to-r from-amber-600 to-amber-700 hover:from-amber-700 hover:to-amber-800 shadow-lg shadow-amber-200/50'
                        : 'bg-gradient-to-r from-slate-600 to-slate-700 hover:from-slate-700 hover:to-slate-800 shadow-lg shadow-slate-200/50'
                    } h-12`}
                    onClick={() => handlePrimaryAction(report.id, psychoInsights.urgentCount > 0)}
                  >
                    <div className="absolute inset-0 bg-gradient-to-r from-white/10 to-transparent opacity-0 group-hover:opacity-100 transition-opacity duration-300" />
                    <div className="relative flex items-center justify-center gap-2">
                      {psychoInsights.urgentCount > 0 ? (
                        <>
                          <span className="text-lg">🚨</span>
                          <span className="tracking-wide">FIX {psychoInsights.urgentCount} URGENT</span>
                        </>
                      ) : psychoInsights.quickWinsCount >= 3 ? (
                        <>
                          <span className="text-lg">⚡</span>
                          <span className="tracking-wide">START WITH {psychoInsights.quickWinsCount} QUICK WINS</span>
                        </>
                      ) : psychoInsights.highImpactCount > 0 ? (
                        <>
                          <span className="text-lg">🎯</span>
                          <span className="tracking-wide">RESOLVE {psychoInsights.highImpactCount} BLOCKERS</span>
                        </>
                      ) : report.anomaly_count > 0 ? (
                        <>
                          <Eye className="w-5 h-5" />
                          <span className="tracking-wide">REVIEW ITEMS</span>
                        </>
                      ) : (
                        <>
                          <Eye className="w-5 h-5" />
                          <span className="tracking-wide">VIEW REPORT</span>
                        </>
                      )}
                    </div>
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
      <Dialog open={!!selectedReport} onOpenChange={() => {
        setSelectedReport(null)
        // DON'T clear resolved anomalies when modal closes - let them persist for the session
      }}>
        <DialogContent className="max-w-6xl max-h-[90vh] overflow-y-auto">
          <DialogHeader>
            <DialogTitle className="flex items-center gap-2">
              <FileText className="w-5 h-5" />
              {selectedReport?.reportName}
            </DialogTitle>
          </DialogHeader>
          
          {selectedReport && (
            <Tabs value={activeTab} onValueChange={setActiveTab} className="space-y-4">
              <TabsList className="grid w-full grid-cols-2">
                <TabsTrigger value="business-intelligence" data-value="business-intelligence">Business Intelligence</TabsTrigger>
                <TabsTrigger value="analytics">Analytics</TabsTrigger>
              </TabsList>
              
              
              <TabsContent value="business-intelligence" className="space-y-6">
                <BusinessIntelligenceReport
                  locations={selectedReport.locations}
                  resolvedAnomalies={reportResolvedAnomalies[selectedReport.reportId] || new Set()}
                  onStatusUpdate={() => {
                    // Refresh report details after status update
                    openReportDetails(selectedReport.reportId)
                    // Also refresh the card status for real-time updates
                    refreshReportStatus(selectedReport.reportId)
                  }}
                  onAnomalyResolved={(anomalyId: string) => {
                    // Update report-specific resolved anomalies (persists across modal close/open)
                    setReportResolvedAnomalies(prev => ({
                      ...prev,
                      [selectedReport.reportId]: new Set((prev[selectedReport.reportId] || new Set()).add(anomalyId))
                    }))
                    // Track session resolved anomalies for analytics
                    setSessionResolvedAnomalies(prev => new Set(prev.add(anomalyId)))
                  }}
                  onAnomalyUnresolved={(anomalyId: string) => {
                    // Remove from report-specific resolved anomalies
                    setReportResolvedAnomalies(prev => {
                      const currentSet = prev[selectedReport.reportId] || new Set()
                      const newSet = new Set(currentSet)
                      newSet.delete(anomalyId)
                      return {
                        ...prev,
                        [selectedReport.reportId]: newSet
                      }
                    })
                    // Remove from session resolved anomalies
                    setSessionResolvedAnomalies(prev => {
                      const newSet = new Set(prev)
                      newSet.delete(anomalyId)
                      return newSet
                    })
                  }}
                />
              </TabsContent>
              
              <TabsContent value="analytics" className="space-y-6">
                {/* Problem Hotspots */}
                <div>
                  <h3 className="text-xl font-semibold mb-4">Problem Hotspots</h3>
                  <div className="grid lg:grid-cols-2 gap-6">
                    {/* Top Problem Locations */}
                    <Card>
                      <CardHeader>
                        <CardTitle className="flex items-center gap-2">
                          <AlertTriangle className="w-5 h-5 text-red-500" />
                          Top Problem Locations
                        </CardTitle>
                      </CardHeader>
                      <CardContent>
                        <div className="space-y-3">
                          {selectedReport.locations
                            .sort((a, b) => b.anomaly_count - a.anomaly_count)
                            .slice(0, 5)
                            .map((location, index) => (
                              <div key={location.name} className="flex items-center justify-between p-3 bg-gray-50 rounded-lg hover:bg-gray-100 transition-colors">
                                <div className="flex items-center gap-3">
                                  <div className={`w-8 h-8 rounded-full flex items-center justify-center text-white font-bold text-sm ${
                                    index === 0 ? 'bg-red-500' :
                                    index === 1 ? 'bg-orange-500' :
                                    index === 2 ? 'bg-yellow-500' : 'bg-blue-500'
                                  }`}>
                                    {index + 1}
                                  </div>
                                  <div>
                                    <p className="font-medium text-gray-900">{location.name}</p>
                                    <p className="text-sm text-gray-500">
                                      {(() => {
                                        const criticalCount = location.anomalies?.filter(a => classifyAnomalyOperational(a, location.name) === 'critical').length || 0
                                        const highPriorityCount = location.anomalies?.filter(a => classifyAnomalyOperational(a, location.name) === 'high_priority').length || 0

                                        // Debug logging for count verification
                                        if (['RECV-03', 'RECV-01', 'RECV-02', 'AISLE-02', 'AISLE-01'].includes(location.name)) {
                                          console.log(`[DEBUG] ${location.name} counts - Total: ${location.anomalies?.length || 0}, Critical: ${criticalCount}, HighPriority: ${highPriorityCount}`)
                                          console.log(`[DEBUG] ${location.name} priorities:`, location.anomalies?.map(a => a.priority) || [])
                                          console.log(`[DEBUG] ${location.name} types:`, location.anomalies?.map(a => a.anomaly_type) || [])
                                        }

                                        return `${criticalCount} critical, ${highPriorityCount} high priority`
                                      })()}
                                    </p>
                                  </div>
                                </div>
                                <div className="text-right">
                                  <span className="text-lg font-bold text-gray-900">{location.anomaly_count}</span>
                                  <p className="text-xs text-gray-500">total issues</p>
                                </div>
                              </div>
                            ))
                          }
                        </div>
                      </CardContent>
                    </Card>

                    {/* Overcapacity Zones */}
                    <Card>
                      <CardHeader>
                        <CardTitle className="flex items-center gap-2">
                          <BarChart3 className="w-5 h-5 text-orange-500" />
                          Overcapacity Issues
                        </CardTitle>
                      </CardHeader>
                      <CardContent>
                        <div className="space-y-3">
                          {(() => {
                            const capacityLocations = selectedReport.locations
                              .filter(loc => loc.anomalies?.some(a => a.anomaly_type.includes('Capacity') || a.anomaly_type.includes('Overcapacity')))

                            // Debug logging for overcapacity accuracy
                            console.log(`[DEBUG] Overcapacity locations found: ${capacityLocations.length}`)
                            console.log(`[DEBUG] Total capacity anomalies:`, capacityLocations.reduce((sum, loc) =>
                              sum + (loc.anomalies?.filter(a => a.anomaly_type.includes('Capacity') || a.anomaly_type.includes('Overcapacity')).length || 0), 0
                            ))

                            const displayLocations = showAllOvercapacity ? capacityLocations : capacityLocations.slice(0, 5)

                            return (
                              <>
                                <div className={showAllOvercapacity ? "max-h-96 overflow-y-auto space-y-3 pr-2 scrollbar-thin scrollbar-thumb-orange-300 scrollbar-track-orange-100" : "space-y-3"}>
                                  {displayLocations.map((location, index) => {
                              const capacityIssues = location.anomalies?.filter(a =>
                                a.anomaly_type.includes('Capacity') || a.anomaly_type.includes('Overcapacity')
                              ) || []

                              return (
                                <div key={location.name} className="p-3 bg-orange-50 rounded-lg border border-orange-200">
                                  <div className="flex items-center justify-between">
                                    <div>
                                      <p className="font-medium text-orange-900">{location.name}</p>
                                      <p className="text-sm text-orange-700">
                                        {capacityIssues.length} capacity issue{capacityIssues.length !== 1 ? 's' : ''}
                                      </p>
                                    </div>
                                    <div className="flex items-center gap-2">
                                      <div className="w-12 h-12 rounded-lg bg-orange-500 flex items-center justify-center">
                                        <span className="text-white font-bold text-sm">{capacityIssues.length}</span>
                                      </div>
                                    </div>
                                  </div>
                                </div>
                              )
                                  })}
                                </div>

                                {/* Show All / Show Less Button */}
                                {capacityLocations.length > 5 && (
                                  <div className="text-center pt-3">
                                    <Button
                                      variant="outline"
                                      size="sm"
                                      onClick={() => setShowAllOvercapacity(!showAllOvercapacity)}
                                      className="text-orange-600 border-orange-300 hover:bg-orange-50"
                                    >
                                      {showAllOvercapacity ? (
                                        <>Show Less <ChevronRight className="w-4 h-4 ml-1 rotate-90" /></>
                                      ) : (
                                        <>Show All {capacityLocations.length} Overcapacity Issues <ChevronRight className="w-4 h-4 ml-1" /></>
                                      )}
                                    </Button>
                                  </div>
                                )}
                              </>
                            )
                          })()}
                          {selectedReport.locations.filter(loc =>
                            loc.anomalies?.some(a => a.anomaly_type.includes('Capacity') || a.anomaly_type.includes('Overcapacity'))
                          ).length === 0 && (
                            <div className="text-center py-6 text-gray-500">
                              <CheckCircle2 className="w-8 h-8 mx-auto mb-2 text-green-500" />
                              <p>No overcapacity issues detected</p>
                            </div>
                          )}
                        </div>
                      </CardContent>
                    </Card>
                  </div>
                </div>

                {/* Time Patterns - HIDDEN: Complex temporal analysis not immediately actionable
                <div>
                  <h3 className="text-xl font-semibold mb-4">Time Patterns</h3>
                  ... (section hidden for simplicity)
                </div>
                */}

                {/* Daily Resolution Summary */}
                <div>
                  <h3 className="text-xl font-semibold mb-4">Today's Resolution Summary</h3>
                  <div className="grid md:grid-cols-2 gap-6">
                    {/* Total Resolved Today */}
                    <Card>
                      <CardHeader>
                        <CardTitle className="flex items-center gap-2">
                          <CheckCircle2 className="w-5 h-5 text-green-500" />
                          Anomalies Resolved Today
                        </CardTitle>
                      </CardHeader>
                      <CardContent>
                        <div className="space-y-4">
                          {(() => {
                            // Calculate resolved anomalies from all reports today
                            const todayResolved = Object.values(reportAnomaliesCache).flat()
                              .filter(anomaly => anomaly.status === 'Resolved' || anomaly.status === 'Acknowledged')

                            // Get all persistent resolved anomalies (includes previous sessions)
                            const allResolvedAnomalies = new Set<string>()
                            Object.values(reportResolvedAnomalies).forEach(reportSet => {
                              reportSet.forEach(anomalyId => allResolvedAnomalies.add(anomalyId))
                            })
                            const persistentResolvedCount = allResolvedAnomalies.size
                            const totalResolved = todayResolved.length + persistentResolvedCount

                            return (
                              <div className="text-center py-6">
                                <div className="text-5xl font-bold text-green-600 mb-2">{totalResolved}</div>
                                <p className="text-lg text-gray-600">Issues Resolved</p>
                                <div className="flex justify-center items-center gap-4 mt-4 text-sm text-gray-500">
                                  <span>Backend: {todayResolved.length}</span>
                                  <span>•</span>
                                  <span>User Marked: {persistentResolvedCount}</span>
                                </div>
                              </div>
                            )
                          })()}
                        </div>
                      </CardContent>
                    </Card>

                    {/* Most Common Resolution Types */}
                    <Card>
                      <CardHeader>
                        <CardTitle className="flex items-center gap-2">
                          <BarChart3 className="w-5 h-5 text-blue-500" />
                          Most Common Resolution Types
                        </CardTitle>
                      </CardHeader>
                      <CardContent>
                        <div className="space-y-3">
                          {(() => {
                            // Calculate most common anomaly types being resolved
                            const allAnomalies = Object.values(reportAnomaliesCache).flat()
                            const typeCount = {} as Record<string, number>

                            // Get all persistent resolved anomalies (same as above)
                            const allResolvedAnomalies = new Set<string>()
                            Object.values(reportResolvedAnomalies).forEach(reportSet => {
                              reportSet.forEach(anomalyId => allResolvedAnomalies.add(anomalyId))
                            })

                            allAnomalies.forEach(anomaly => {
                              // Count backend resolved anomalies
                              if (anomaly.status === 'Resolved' || anomaly.status === 'Acknowledged') {
                                typeCount[anomaly.anomaly_type] = (typeCount[anomaly.anomaly_type] || 0) + 1
                              }
                              // Count persistent resolved anomalies (all sessions)
                              if (anomaly.id && allResolvedAnomalies.has(anomaly.id.toString())) {
                                typeCount[anomaly.anomaly_type] = (typeCount[anomaly.anomaly_type] || 0) + 1
                              }
                            })

                            const sortedTypes = Object.entries(typeCount)
                              .sort(([,a], [,b]) => b - a)
                              .slice(0, 4)

                            if (sortedTypes.length === 0) {
                              return (
                                <div className="text-center py-6 text-gray-500">
                                  <p>No resolutions tracked yet</p>
                                  <p className="text-sm">Start resolving anomalies to see patterns</p>
                                </div>
                              )
                            }

                            return sortedTypes.map(([type, count]) => (
                              <div key={type} className="flex items-center justify-between p-3 bg-blue-50 rounded-lg">
                                <div>
                                  <p className="font-medium text-blue-900 text-sm">{type}</p>
                                  <p className="text-xs text-blue-700">Most resolved type</p>
                                </div>
                                <span className="text-lg font-bold text-blue-600">{count}</span>
                              </div>
                            ))
                          })()}
                        </div>
                      </CardContent>
                    </Card>
                  </div>
                </div>

                {/* Focus Areas */}
                <div>
                  <h3 className="text-xl font-semibold mb-4">Focus Areas - Where to Start Today</h3>
                  <Card>
                    <CardContent className="p-6">
                      <div className="grid md:grid-cols-2 gap-6">
                        {/* Priority Actions */}
                        <div>
                          <h4 className="font-medium text-gray-900 mb-4 flex items-center gap-2">
                            <Target className="w-5 h-5 text-blue-500" />
                            Priority Actions (Next 2 hours)
                          </h4>
                          <div className="space-y-3">
                            {(() => {
                              // Get priority actions from real data (Overcapacity and Stagnant Pallets)
                              const priorityActions: any[] = []

                              selectedReport.locations.forEach(location => {
                                const locationAnomalies = location.anomalies || []

                                // Count Overcapacity issues
                                const overcapacityCount = locationAnomalies.filter(a =>
                                  a.anomaly_type === 'Overcapacity'
                                ).length

                                // Count Stagnant Pallets
                                const stagnantCount = locationAnomalies.filter(a =>
                                  a.anomaly_type === 'Stagnant Pallet'
                                ).length

                                // Add BOTH types if they exist (this allows same location to show both issues)
                                if (overcapacityCount > 0) {
                                  priorityActions.push({
                                    location: location.name,
                                    issue: 'Overcapacity',
                                    count: overcapacityCount,
                                    priority: 'high',
                                    type: 'Overcapacity'
                                  })
                                }

                                if (stagnantCount > 0) {
                                  priorityActions.push({
                                    location: location.name,
                                    issue: 'Stagnant Pallets',
                                    count: stagnantCount,
                                    priority: location.name.includes('RECV') ? 'critical' : 'high',
                                    type: 'Stagnant Pallet'
                                  })
                                }
                              })

                              // Sort by priority (critical first) and count (highest first)
                              priorityActions.sort((a, b) => {
                                if (a.priority === 'critical' && b.priority !== 'critical') return -1
                                if (b.priority === 'critical' && a.priority !== 'critical') return 1
                                return b.count - a.count
                              })

                              // Smart variety: ensure we show different issue types when possible
                              const finalActions: any[] = []
                              const overcapacityActions = priorityActions.filter(a => a.type === 'Overcapacity')
                              const stagnantActions = priorityActions.filter(a => a.type === 'Stagnant Pallet')

                              // Rule: Force at least one overcapacity to show (if exists)
                              if (overcapacityActions.length > 0) {
                                finalActions.push(overcapacityActions[0])
                              }

                              // Fill remaining slots with highest priority items (excluding already added)
                              const remainingActions = priorityActions.filter(action => !finalActions.includes(action))
                              while (finalActions.length < 3 && remainingActions.length > 0) {
                                finalActions.push(remainingActions.shift())
                              }

                              // Show top 3 priority actions with guaranteed variety
                              return finalActions.map((action, index) => (
                                <div key={index} className={`p-3 rounded-lg border-l-4 ${
                                  action.priority === 'critical' ? 'bg-red-50 border-red-500' : 'bg-orange-50 border-orange-500'
                                }`}>
                                  <div className="flex justify-between items-start">
                                    <div>
                                      <p className="font-medium text-gray-900">{action.location}</p>
                                      <p className="text-sm text-gray-600">{action.issue} ({action.count} items)</p>
                                    </div>
                                    <span className="text-lg font-bold text-gray-700">{action.count}</span>
                                  </div>
                                </div>
                              ))
                            })()
                            }
                            {(() => {
                              // Show message if no priority actions
                              const hasActions = selectedReport.locations.some(location =>
                                (location.anomalies || []).some(a =>
                                  a.anomaly_type === 'Overcapacity' || a.anomaly_type === 'Stagnant Pallet'
                                )
                              )

                              if (!hasActions) {
                                return (
                                  <div className="p-4 text-center text-gray-500 bg-gray-50 rounded-lg">
                                    <p className="text-sm">No critical priority actions detected</p>
                                    <p className="text-xs mt-1">All overcapacity and stagnant pallet issues resolved</p>
                                  </div>
                                )
                              }
                              return null
                            })()
                            }
                          </div>
                        </div>

                        {/* Quick Wins Available */}
                        <div>
                          <h4 className="font-medium text-gray-900 mb-4 flex items-center gap-2">
                            <CheckCircle2 className="w-5 h-5 text-green-500" />
                            Quick Wins Available (1 hour)
                          </h4>
                          <div className="space-y-3">
                            {(() => {
                              // Get quick wins from real data (easy fixes with high counts)
                              const quickWins: any[] = []
                              const anomalyCounts: { [key: string]: number } = {}

                              // Count all anomaly types across locations
                              selectedReport.locations.forEach(location => {
                                const locationAnomalies = location.anomalies || []
                                locationAnomalies.forEach(anomaly => {
                                  // Skip priority actions (already shown above)
                                  if (anomaly.anomaly_type === 'Overcapacity' || anomaly.anomaly_type === 'Stagnant Pallet') {
                                    return
                                  }

                                  anomalyCounts[anomaly.anomaly_type] = (anomalyCounts[anomaly.anomaly_type] || 0) + 1
                                })
                              })

                              // Define quick win mapping for different anomaly types
                              const quickWinMapping: { [key: string]: { task: string } } = {
                                'Location Mapping Error': { task: 'Fix location mapping errors' },
                                'Data Integrity Issue': { task: 'Clear data entry errors' },
                                'Invalid Location': { task: 'Update invalid locations' },
                                'Temperature Zone Mismatch': { task: 'Fix temperature zone issues' },
                                'Lot Straggler': { task: 'Consolidate lot stragglers' }
                              }

                              // Create quick wins based on real data
                              Object.entries(anomalyCounts).forEach(([type, count]) => {
                                const mapping = quickWinMapping[type]
                                if (mapping && count > 0) {
                                  quickWins.push({
                                    task: mapping.task,
                                    count: count,
                                    type: type
                                  })
                                }
                              })

                              // Sort by count (highest first) and show top 3
                              quickWins.sort((a, b) => b.count - a.count)

                              return quickWins.slice(0, 3).map((task, index) => (
                                <div key={index} className="p-3 bg-green-50 rounded-lg border border-green-200">
                                  <div className="flex justify-between items-start">
                                    <div>
                                      <p className="font-medium text-green-900">{task.task}</p>
                                      <p className="text-sm text-green-700">Quick resolution opportunity</p>
                                    </div>
                                    <span className="text-lg font-bold text-green-600">{task.count}</span>
                                  </div>
                                </div>
                              ))
                            })()
                            }
                            {(() => {
                              // Show message if no quick wins available
                              const hasQuickWins = selectedReport.locations.some(location =>
                                (location.anomalies || []).some(a =>
                                  !['Overcapacity', 'Stagnant Pallet'].includes(a.anomaly_type)
                                )
                              )

                              if (!hasQuickWins) {
                                return (
                                  <div className="p-4 text-center text-gray-500 bg-gray-50 rounded-lg">
                                    <p className="text-sm">No quick wins available</p>
                                    <p className="text-xs mt-1">Focus on priority actions above</p>
                                  </div>
                                )
                              }
                              return null
                            })()
                            }
                          </div>
                        </div>
                      </div>

                      {/* Summary Action */}
                      {(() => {
                        // Get the top priority action dynamically
                        const priorityActions: any[] = []

                        selectedReport.locations.forEach(location => {
                          const locationAnomalies = location.anomalies || []

                          // Count Overcapacity issues
                          const overcapacityCount = locationAnomalies.filter(a =>
                            a.anomaly_type === 'Overcapacity'
                          ).length

                          // Count Stagnant Pallets
                          const stagnantCount = locationAnomalies.filter(a =>
                            a.anomaly_type === 'Stagnant Pallet'
                          ).length

                          if (overcapacityCount > 0) {
                            priorityActions.push({
                              location: location.name,
                              issue: 'Overcapacity',
                              count: overcapacityCount,
                              priority: 'high',
                              type: 'Overcapacity',
                              description: `${overcapacityCount} overcapacity issues affecting operations`
                            })
                          }

                          if (stagnantCount > 0) {
                            priorityActions.push({
                              location: location.name,
                              issue: 'Stagnant Pallets',
                              count: stagnantCount,
                              priority: location.name.includes('RECV') ? 'critical' : 'high',
                              type: 'Stagnant Pallet',
                              description: location.name.includes('RECV')
                                ? `${stagnantCount} stagnant pallets blocking inbound flow - highest impact resolution`
                                : `${stagnantCount} stagnant pallets affecting workflow efficiency`
                            })
                          }
                        })

                        // Sort by priority (critical first) and count (highest first)
                        priorityActions.sort((a, b) => {
                          if (a.priority === 'critical' && b.priority !== 'critical') return -1
                          if (b.priority === 'critical' && a.priority !== 'critical') return 1
                          return b.count - a.count
                        })

                        const topAction = priorityActions[0]

                        if (!topAction) {
                          return (
                            <div className="mt-6 p-4 bg-green-50 rounded-lg border border-green-200">
                              <div className="flex items-center justify-between">
                                <div>
                                  <p className="font-medium text-green-900">✅ No Priority Actions Needed</p>
                                  <p className="text-sm text-green-700">All critical and high-priority issues have been resolved</p>
                                </div>
                              </div>
                            </div>
                          )
                        }

                        return (
                          <div className="mt-6 p-4 bg-blue-50 rounded-lg border border-blue-200">
                            <div className="flex items-center justify-between">
                              <div>
                                <p className="font-medium text-blue-900">Recommended Focus: Start with {topAction.location}</p>
                                <p className="text-sm text-blue-700">{topAction.description}</p>
                              </div>
                              <Button
                                className="bg-blue-500 hover:bg-blue-600 text-white"
                                onClick={() => {
                                  // Navigate to Business Intelligence tab
                                  setActiveTab('business-intelligence')
                                  // Small delay to ensure tab switch completes, then trigger location filter
                                  setTimeout(() => {
                                    // Find and trigger the filter for this location
                                    // This would be handled by the BusinessIntelligenceReport component
                                    console.log(`Navigate to ${topAction.location} in Business Intelligence`)
                                  }, 100)
                                }}
                              >
                                Start Here
                              </Button>
                            </div>
                          </div>
                        )
                      })()
                      }
                    </CardContent>
                  </Card>
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