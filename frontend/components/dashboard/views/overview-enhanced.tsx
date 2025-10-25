"use client"

import { useState, useEffect, useRef } from 'react'
import Link from 'next/link'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Badge } from '@/components/ui/badge'
import { AlertTriangle, TrendingUp, Upload, MapPin, Clock, CheckCircle, BarChart3, Activity, CheckCircle2, ChevronRight, Flame, Package, Grid3x3 } from 'lucide-react'
import { useDashboardStore } from '@/lib/store'
import { actionCenterApi, ActionCenterData } from '@/lib/action-center-api'
import { reportsApi, ReportDetails, SpaceUtilization } from '@/lib/reports'
import { getImprovementDisplayText } from '@/lib/progress-comparison'
import { getLatestWinsData, WinsData } from '@/lib/wins-api'

interface CriticalLocationInsight {
  location: string
  anomalyCount: number
  topIssueType: string
  severity: 'high' | 'medium' | 'low'
}

interface QuickFixAction {
  type: string
  count: number
}

export function EnhancedOverviewView() {
  const { setCurrentView, lastAnalysisTimestamp } = useDashboardStore()

  // OPTIMIZATION: Batch all state into single object to prevent multiple re-renders
  const [dashboardState, setDashboardState] = useState({
    actionData: null as ActionCenterData | null,
    winsData: null as WinsData | null,
    loading: true,
    criticalInsight: null as CriticalLocationInsight | null,
    quickFixActions: [] as QuickFixAction[],
    spaceUtilization: null as SpaceUtilization | null,
    isProcessing: false,  // NEW: Track if backend is still processing
    processingReportId: null as number | null  // NEW: Track which report is processing
  })

  // Destructure for backwards compatibility
  const { actionData, winsData, loading, criticalInsight, quickFixActions, spaceUtilization, isProcessing, processingReportId } = dashboardState

  // Guard against duplicate fetches
  const isFetchingRef = useRef(false)
  const abortControllerRef = useRef<AbortController | null>(null)
  const debounceTimerRef = useRef<NodeJS.Timeout | null>(null)
  const pollingIntervalRef = useRef<NodeJS.Timeout | null>(null)

  useEffect(() => {
    console.log('🔄 Overview refresh triggered. Timestamp:', lastAnalysisTimestamp)

    // CRITICAL FIX: Set flag IMMEDIATELY (synchronously) before any async operations
    if (isFetchingRef.current) {
      console.log('⚠️ Fetch already in progress, skipping duplicate request')
      return
    }

    // Debounce: Clear any pending timers
    if (debounceTimerRef.current) {
      console.log('⏱️ Clearing debounce timer')
      clearTimeout(debounceTimerRef.current)
    }

    // Set fetch flag SYNCHRONOUSLY (before async work begins)
    isFetchingRef.current = true
    console.log('🔒 Fetch guard enabled')

    // Cancel any previous fetch that might still be running
    if (abortControllerRef.current) {
      console.log('🛑 Cancelling previous fetch')
      abortControllerRef.current.abort()
    }

    // Create new abort controller for this fetch
    abortControllerRef.current = new AbortController()

    // Debounce wrapper: Wait 100ms before actually fetching
    debounceTimerRef.current = setTimeout(() => {
      console.log('⚡ Debounce completed, starting fetch')

      const fetchData = async () => {
        try {
          console.log('📊 Fetching dashboard data...')

          // OPTIMIZATION: Single state update to clear data and start loading
          setDashboardState(prev => ({
            ...prev,
            loading: true,
            actionData: null,
            winsData: null,
            criticalInsight: null,
            quickFixActions: [],
            spaceUtilization: null
          }))

          // Fetch action center data
          const data = await actionCenterApi.getActionCenterData()
          console.log('✅ Action center data loaded. Total active items:', data.totalActiveItems)

          // Fetch wins data for achievements
          let wins: WinsData | null = null
          try {
            wins = await getLatestWinsData()
          } catch (winsError) {
            console.log('Wins data not available yet:', winsError)
          }

          // Fetch latest report for critical location insights, resolution types, and space utilization
          const reportsResponse = await reportsApi.getReports()
          const reports = reportsResponse.reports || []

          let criticalLocation: CriticalLocationInsight | null = null
          let quickFixes: QuickFixAction[] = []
          let spaceData: SpaceUtilization | null = null
          let latestReport: any = null  // Declare in outer scope for processing detection

          if (reports.length > 0) {
            latestReport = reports.find(r => r.anomaly_count > 0) || reports[0]
            console.log('📋 Latest report:', latestReport.id, 'Anomaly count:', latestReport.anomaly_count)
            const reportDetails = await reportsApi.getReportDetails(latestReport.id)

            // Find critical location (location with most active anomalies)
            criticalLocation = findCriticalLocation(reportDetails)

            // Calculate quick fix actions (5-15 min resolution opportunities)
            quickFixes = calculateQuickFixActions(reportDetails)

            // Fetch space utilization
            try {
              spaceData = await reportsApi.getSpaceUtilization(latestReport.id)
            } catch (spaceError) {
              console.log('Space utilization not available:', spaceError)
            }
          }

          // SMART PROCESSING DETECTION: Check if we got 0 results from a recent report
          const isLikelyProcessing = reports.length > 0 &&
                                     data.totalActiveItems === 0 &&
                                     latestReport &&
                                     isReportRecent(latestReport.timestamp)

          if (isLikelyProcessing) {
            console.log('🔄 Detected processing state - report is recent with 0 anomalies')
            console.log(`📊 Starting polling for report ID: ${latestReport.id}`)

            // Set processing state
            setDashboardState({
              actionData: data,
              winsData: wins,
              loading: false,
              criticalInsight: criticalLocation,
              quickFixActions: quickFixes,
              spaceUtilization: spaceData,
              isProcessing: true,
              processingReportId: latestReport.id
            })

            // Start polling for updates
            startPolling(latestReport.id)
          } else {
            // Normal state - data is ready
            console.log('✅ Data ready - not in processing state')
            setDashboardState({
              actionData: data,
              winsData: wins,
              loading: false,
              criticalInsight: criticalLocation,
              quickFixActions: quickFixes,
              spaceUtilization: spaceData,
              isProcessing: false,
              processingReportId: null
            })
          }

        } catch (error) {
          console.error('❌ Failed to fetch dashboard data:', error)

          // Check if error was due to abort
          if (error instanceof Error && error.name === 'AbortError') {
            console.log('🛑 Fetch was cancelled')
            return
          }

          // On error, just stop loading
          setDashboardState(prev => ({ ...prev, loading: false }))
        } finally {
          console.log('✨ Dashboard data fetch complete')
          // Mark fetch as complete
          isFetchingRef.current = false
          console.log('🔓 Fetch guard released')
        }
      }

      fetchData()
    }, 100) // 100ms debounce

    // Cleanup function: cancel fetch if component unmounts or effect re-runs
    return () => {
      console.log('🧹 Cleanup triggered')
      if (debounceTimerRef.current) {
        clearTimeout(debounceTimerRef.current)
      }
      if (pollingIntervalRef.current) {
        console.log('🛑 Stopping polling')
        clearInterval(pollingIntervalRef.current)
      }
      if (abortControllerRef.current) {
        console.log('🧹 Cleanup: Aborting ongoing fetch')
        abortControllerRef.current.abort()
      }
      isFetchingRef.current = false
    }
  }, [lastAnalysisTimestamp])

  // Helper: Check if report timestamp is recent (within last 30 seconds)
  const isReportRecent = (timestamp: string): boolean => {
    const reportTime = new Date(timestamp).getTime()
    const now = Date.now()
    const secondsAgo = (now - reportTime) / 1000
    return secondsAgo < 30
  }

  // Helper: Start polling for report updates
  const startPolling = (reportId: number) => {
    let pollCount = 0
    const maxPolls = 30 // Stop after 60 seconds (30 polls × 2s)

    // Clear any existing polling
    if (pollingIntervalRef.current) {
      clearInterval(pollingIntervalRef.current)
    }

    pollingIntervalRef.current = setInterval(async () => {
      pollCount++
      console.log(`🔄 Polling attempt ${pollCount}/${maxPolls} for report ${reportId}`)

      try {
        // Fetch the latest reports to check if anomaly count has updated
        const reportsResponse = await reportsApi.getReports()
        const reports = reportsResponse.reports || []
        const updatedReport = reports.find(r => r.id === reportId)

        if (updatedReport && updatedReport.anomaly_count > 0) {
          console.log(`✅ Report ${reportId} now has ${updatedReport.anomaly_count} anomalies!`)
          console.log('🛑 Stopping polling - data is ready')

          // Stop polling
          if (pollingIntervalRef.current) {
            clearInterval(pollingIntervalRef.current)
            pollingIntervalRef.current = null
          }

          // Trigger a fresh data fetch by updating the timestamp
          const { triggerOverviewRefresh } = useDashboardStore.getState()
          triggerOverviewRefresh()
        } else if (pollCount >= maxPolls) {
          console.log('⏱️ Polling timeout reached - stopping')
          if (pollingIntervalRef.current) {
            clearInterval(pollingIntervalRef.current)
            pollingIntervalRef.current = null
          }
          // Exit processing state even if no data
          setDashboardState(prev => ({
            ...prev,
            isProcessing: false,
            processingReportId: null
          }))
        }
      } catch (error) {
        console.error('❌ Polling error:', error)
      }
    }, 2000) // Poll every 2 seconds
  }

  const findCriticalLocation = (details: ReportDetails): CriticalLocationInsight | null => {
    if (!details.locations || details.locations.length === 0) return null

    // Filter locations with active anomalies
    const locationsWithIssues = details.locations
      .map(loc => ({
        location: loc.name,
        activeAnomalies: (loc.anomalies || []).filter(a => a.status !== 'Resolved' && a.status !== 'Acknowledged'),
      }))
      .filter(loc => loc.activeAnomalies.length > 0)

    if (locationsWithIssues.length === 0) return null

    // Find location with most active anomalies
    const critical = locationsWithIssues.reduce((max, loc) =>
      loc.activeAnomalies.length > max.activeAnomalies.length ? loc : max
    )

    // Determine top issue type
    const issueTypes = critical.activeAnomalies.map(a => a.anomaly_type)
    const topIssue = issueTypes.reduce((a, b, _, arr) =>
      arr.filter(v => v === a).length >= arr.filter(v => v === b).length ? a : b
    )

    // Determine severity
    const severity = critical.activeAnomalies.length >= 10 ? 'high' :
                     critical.activeAnomalies.length >= 5 ? 'medium' : 'low'

    return {
      location: critical.location,
      anomalyCount: critical.activeAnomalies.length,
      topIssueType: topIssue,
      severity
    }
  }

  // Get specific action description for each anomaly type
  const getQuickFixActionDescription = (anomalyType: string): string => {
    const actionMap: Record<string, string> = {
      'Location Mapping Error': 'Update location mapping',
      'Data Integrity Issue': 'Fix data entry errors',
      'Data Integrity': 'Fix data entry errors',
      'Invalid Location': 'Correct location codes',
      'Temperature Zone Mismatch': 'Relocate to correct zone',
      'Lot Straggler': 'Consolidate lot items',
      'Duplicate Scan': 'Remove duplicate entries'
    }
    return actionMap[anomalyType] || 'Quick resolution needed'
  }

  const calculateQuickFixActions = (details: ReportDetails): QuickFixAction[] => {
    if (!details.locations || details.locations.length === 0) return []

    // Define anomaly types that are quick to resolve (5-15 min)
    const quickFixTypes = [
      'Location Mapping Error',
      'Data Integrity Issue',
      'Data Integrity',
      'Invalid Location',
      'Temperature Zone Mismatch',
      'Lot Straggler',
      'Duplicate Scan'
    ]

    // Get all anomalies from all locations
    const allAnomalies = details.locations.flatMap(loc => loc.anomalies || [])
    const typeCount: Record<string, number> = {}

    // Count ACTIVE (unresolved) anomalies that are quick fixes
    allAnomalies.forEach(anomaly => {
      // Only count active anomalies (skip resolved/acknowledged)
      if (anomaly.status === 'Resolved' || anomaly.status === 'Acknowledged') return

      // Only count quick fix types
      if (quickFixTypes.includes(anomaly.anomaly_type)) {
        typeCount[anomaly.anomaly_type] = (typeCount[anomaly.anomaly_type] || 0) + 1
      }
    })

    // Sort by count and return top 2
    return Object.entries(typeCount)
      .sort(([,a], [,b]) => b - a)
      .slice(0, 2)
      .map(([type, count]) => ({ type, count }))
  }

  // Calculate total active issues count (all unresolved anomalies)
  const totalActiveIssuesCount = actionData ? actionData.totalActiveItems : 0

  //  If processing state is active, show processing UI instead of normal dashboard
  if (isProcessing) {
    return (
      <div className="p-8 pt-12 space-y-8">
        <Card className="border-2 border-blue-500 bg-gradient-to-br from-blue-50 to-white">
          <CardContent className="p-12">
            <div className="flex flex-col items-center justify-center space-y-6">
              {/* Animated Spinner */}
              <div className="relative w-24 h-24">
                <div className="absolute inset-0 border-8 border-blue-200 rounded-full"></div>
                <div className="absolute inset-0 border-8 border-blue-600 rounded-full border-t-transparent animate-spin"></div>
              </div>

              {/* Processing Message */}
              <div className="text-center space-y-2">
                <h2 className="text-2xl font-bold text-blue-900">
                  Analyzing Your Warehouse Data...
                </h2>
                <p className="text-blue-700 text-lg">
                  Processing inventory report #{processingReportId}
                </p>
                <p className="text-blue-600">
                  This may take 15-20 seconds for large files
                </p>
              </div>

              {/* Progress Steps */}
              <div className="w-full max-w-md space-y-3">
                <div className="flex items-center space-x-3 p-3 bg-green-50 border border-green-200 rounded-lg">
                  <CheckCircle className="w-5 h-5 text-green-600" />
                  <span className="text-green-900 font-medium">Files uploaded successfully</span>
                </div>
                <div className="flex items-center space-x-3 p-3 bg-blue-100 border-2 border-blue-400 rounded-lg">
                  <div className="w-5 h-5 border-2 border-blue-600 border-t-transparent rounded-full animate-spin"></div>
                  <span className="text-blue-900 font-medium">Running detection algorithms...</span>
                </div>
                <div className="flex items-center space-x-3 p-3 bg-gray-50 border border-gray-200 rounded-lg opacity-50">
                  <Clock className="w-5 h-5 text-gray-400" />
                  <span className="text-gray-600">Generating insights...</span>
                </div>
              </div>

              {/* Info Banner */}
              <div className="mt-6 p-4 bg-blue-100 border border-blue-300 rounded-lg max-w-md">
                <p className="text-sm text-blue-800 text-center">
                  <AlertTriangle className="w-4 h-4 inline mr-2" />
                  Results will appear automatically when ready. No need to refresh!
                </p>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>
    )
  }

  return (
    <div className="p-8 pt-12 space-y-8">
      {/* Main Navigation Cards */}
      <div className="mb-8">
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
          {/* Take Action - Critical Priority (Warehouse Native) */}
          <Card className="border-l-4 border-l-orange-500 hover:shadow-lg hover:scale-[1.02] transition-all duration-200 cursor-pointer group bg-gradient-to-br from-orange-50/20 to-white">
              <CardHeader className="pb-3">
                <div className="flex items-center justify-between py-1 hover:bg-muted/50 rounded px-2 -mx-2 transition-colors cursor-pointer">
                  <Flame className="w-6 h-6 text-orange-600" />
                  <Badge className="bg-orange-500 text-white hover:bg-orange-600">URGENT</Badge>
                </div>
                <CardTitle className="text-lg">Take Action</CardTitle>
                <CardDescription>Fix problems NOW</CardDescription>
              </CardHeader>
              <CardContent>
                <div className="space-y-2 mb-4">
                  <div className="text-2xl font-bold text-orange-600">
                    {loading ? '...' : totalActiveIssuesCount}
                  </div>
                  <div className="text-sm text-muted-foreground">Critical issues need attention</div>
                  <div className="text-xs text-muted-foreground">
                    <Clock className="w-3 h-3 inline mr-1" />
                    Last updated {actionData ? 'just now' : 'loading...'}
                  </div>
                </div>
                <Button
                  className="w-full group-hover:scale-105 transition-transform duration-200 bg-orange-500 hover:bg-orange-600 text-white"
                  onClick={() => setCurrentView('action-center')}
                >
                  View Action Items
                </Button>
              </CardContent>
            </Card>

          {/* View Analytics (Warehouse Native - Zone Grid) */}
          <Card className="border-l-4 border-l-slate-500 hover:shadow-lg hover:scale-[1.02] transition-all duration-200 cursor-pointer group">
              <CardHeader className="pb-3">
                <div className="flex items-center justify-between py-1 hover:bg-muted/50 rounded px-2 -mx-2 transition-colors cursor-pointer">
                  <Grid3x3 className="w-6 h-6 text-slate-600" />
                  <Badge className="bg-slate-600 text-white hover:bg-slate-700">INSIGHTS</Badge>
                </div>
                <CardTitle className="text-lg">View Analytics</CardTitle>
                <CardDescription>
                  {criticalInsight ? 'Critical areas need attention' : 'Understand patterns'}
                </CardDescription>
              </CardHeader>
              <CardContent>
                {loading ? (
                  <div className="space-y-2 mb-4 animate-pulse">
                    <div className="h-8 bg-muted rounded w-3/4"></div>
                    <div className="h-4 bg-muted rounded w-full"></div>
                    <div className="h-3 bg-muted rounded w-2/3"></div>
                  </div>
                ) : criticalInsight ? (
                  <div className="space-y-2 mb-4">
                    <div className="text-2xl font-bold text-slate-700">
                      {criticalInsight.location}
                    </div>
                    <div className="text-sm text-muted-foreground">
                      {criticalInsight.anomalyCount} {criticalInsight.topIssueType.toLowerCase()}{criticalInsight.anomalyCount > 1 ? 's' : ''}
                    </div>
                    <div className={`text-xs flex items-center gap-1 ${
                      criticalInsight.severity === 'high' ? 'text-destructive' :
                      criticalInsight.severity === 'medium' ? 'text-warning' :
                      'text-muted-foreground'
                    }`}>
                      <AlertTriangle className="w-3 h-3 inline" />
                      {criticalInsight.severity === 'high' ? 'Immediate action needed' :
                       criticalInsight.severity === 'medium' ? 'Attention required' :
                       'Monitor closely'}
                    </div>
                  </div>
                ) : (
                  <div className="space-y-2 mb-4">
                    <div className="text-2xl font-bold text-success">All Clear</div>
                    <div className="text-sm text-muted-foreground">No critical locations found</div>
                    <div className="text-xs text-muted-foreground">
                      <CheckCircle className="w-3 h-3 inline mr-1" />
                      Warehouse performing well
                    </div>
                  </div>
                )}
                <Button
                  className="w-full group-hover:scale-105 transition-transform duration-200 bg-slate-600 hover:bg-slate-700 text-white"
                  onClick={() => setCurrentView('analytics')}
                >
                  Open Analytics
                </Button>
              </CardContent>
            </Card>

          {/* Track Progress - Warehouse Green Success (Pallet Stack Icon) */}
          <Card className="border-l-4 border-l-green-600 hover:shadow-lg hover:scale-[1.02] transition-all duration-200 cursor-pointer group">
              <CardHeader className="pb-3">
                <div className="flex items-center justify-between py-1 hover:bg-muted/50 rounded px-2 -mx-2 transition-colors cursor-pointer">
                  <Package className="w-6 h-6 text-green-600" />
                  <Badge className="bg-green-600 text-white hover:bg-green-700">PROGRESS</Badge>
                </div>
                <CardTitle className="text-lg">Track Your Wins</CardTitle>
                <CardDescription>
                  {loading ? (
                    <span className="inline-block h-4 w-32 bg-muted rounded animate-pulse"></span>
                  ) : winsData ? (
                    `${winsData.achievements.unlocked} of ${winsData.achievements.total} achievements unlocked`
                  ) : (
                    `${actionData?.resolvedToday || 0} issues resolved`
                  )}
                </CardDescription>
              </CardHeader>
              <CardContent>
                {loading ? (
                  /* Loading skeleton */
                  <div className="space-y-2 mb-4 animate-pulse">
                    <div className="h-8 bg-muted rounded w-3/4"></div>
                    <div className="h-4 bg-muted rounded w-1/2"></div>
                    <div className="h-3 bg-muted rounded w-2/3"></div>
                  </div>
                ) : (
                  <div className="space-y-2 mb-4">
                    {winsData ? (
                      <>
                        {/* Highest Priority Achievement */}
                        <div className="text-2xl font-bold text-green-600 flex items-center gap-2">
                          {(() => {
                            // Get highest priority unlocked achievement (already sorted by backend)
                            const topUnlocked = winsData.achievements.details
                              .find(a => a.unlocked)
                            return topUnlocked ? (
                              <>{topUnlocked.icon} {topUnlocked.name}</>
                            ) : (
                              <>🏆 Start Earning Achievements</>
                            )
                          })()}
                        </div>
                        <div className="text-sm text-muted-foreground">
                          {(() => {
                            const topUnlocked = winsData.achievements.details
                              .find(a => a.unlocked)
                            return topUnlocked ? 'Your best achievement' : 'Complete your first win'
                          })()}
                        </div>

                        {/* Next Achievement or Health Score */}
                        <div className="text-xs text-green-600">
                          <CheckCircle className="w-3 h-3 inline mr-1" />
                          {(() => {
                            // Next target is the highest priority locked achievement
                            const nextLocked = winsData.achievements.details.find(a => !a.unlocked)
                            if (nextLocked) {
                              return `Next goal: ${nextLocked.name}`
                            } else if (winsData.health_score) {
                              return `Health Score: ${winsData.health_score.score}%`
                            }
                            return 'All achievements unlocked!'
                          })()}
                        </div>
                      </>
                    ) : (
                      <>
                        {/* Fallback to progress comparison */}
                        <div className="text-2xl font-bold text-green-600 flex items-center gap-2">
                          {actionData?.progressComparison ? (
                            <>
                              🔥 {getImprovementDisplayText(
                                actionData.progressComparison.bestCategory,
                                actionData.progressComparison.improvement,
                                actionData.progressComparison.isCleared
                              )}
                            </>
                          ) : (
                            'No comparison data yet'
                          )}
                        </div>
                        <div className="text-sm text-muted-foreground">
                          Best performing category improvement
                        </div>
                        <div className="text-xs text-green-600">
                          <CheckCircle className="w-3 h-3 inline mr-1" />
                          {actionData?.progressComparison ? (
                            actionData.progressComparison.trendDirection === 'up' ? (
                              `+${actionData.progressComparison.overallChange}% improvement vs last report`
                            ) : actionData.progressComparison.trendDirection === 'down' ? (
                              `${actionData.progressComparison.overallChange}% change vs last report`
                            ) : (
                              'First report - establishing baseline'
                            )
                          ) : (
                            'Establishing baseline'
                          )}
                        </div>
                      </>
                    )}
                  </div>
                )}
                <Button
                  className="w-full group-hover:scale-105 transition-transform duration-200 bg-green-600 hover:bg-green-700 text-white"
                  asChild
                >
                  <Link href="/track-wins">
                    See Your Progress
                  </Link>
                </Button>
              </CardContent>
            </Card>

          {/* Upload Report (Warehouse Clipboard) */}
          <Card className="border-l-4 border-l-yellow-500 hover:shadow-lg hover:scale-[1.02] transition-all duration-200 cursor-pointer group">
              <CardHeader className="pb-3">
                <div className="flex items-center justify-between py-1 hover:bg-muted/50 rounded px-2 -mx-2 transition-colors cursor-pointer">
                  <Upload className="w-6 h-6 text-yellow-600" />
                  <Badge className="bg-yellow-500 text-white hover:bg-yellow-600">UPLOAD</Badge>
                </div>
                <CardTitle className="text-lg">Upload Report</CardTitle>
                <CardDescription>Add new inventory data</CardDescription>
              </CardHeader>
              <CardContent>
                <div className="space-y-2 mb-4">
                  <div className="text-2xl font-bold text-yellow-600">Ready</div>
                  <div className="text-sm text-muted-foreground">System ready for new data</div>
                  <div className="text-xs text-muted-foreground">Last upload: Today 8:30 AM</div>
                </div>
                <Button
                  className="w-full group-hover:scale-105 transition-transform duration-200 bg-yellow-500 hover:bg-yellow-600 text-white"
                  onClick={() => setCurrentView('new-analysis')}
                >
                  Upload Data
                </Button>
              </CardContent>
          </Card>
        </div>
      </div>

      {/* Intelligence Preview Cards - Enhanced Design */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
        {/* Warehouse Health Score - Steel Gray Professional */}
        <Card
          className="group relative overflow-hidden cursor-pointer hover:shadow-lg hover:scale-[1.02] transition-all duration-200 border-2 border-slate-200 hover:border-slate-300 bg-white"
          onClick={() => window.location.href = '/track-wins'}
        >
          <CardContent className="relative p-6">
            {/* Chevron Icon */}
            <ChevronRight className="absolute top-4 right-4 w-4 h-4 text-muted-foreground group-hover:text-success transition-colors" />
            <div className="flex flex-col items-center">
              {loading ? (
                /* Loading State */
                <div className="flex flex-col items-center justify-center py-8">
                  <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-success mb-3"></div>
                  <h3 className="text-sm font-bold text-[#2D3748] mb-1">Warehouse Health Score</h3>
                  <div className="text-xs text-[#718096]">Loading...</div>
                </div>
              ) : !winsData ? (
                /* Empty State */
                <div className="flex flex-col items-center justify-center py-8">
                  <CheckCircle className="w-12 h-12 text-muted-foreground/30 mb-3" />
                  <h3 className="text-sm font-bold text-[#2D3748] mb-1">Warehouse Health Score</h3>
                  <div className="text-xs text-muted-foreground">Awaiting report analysis</div>
                </div>
              ) : (
                /* Data Display State */
                <>
                  <div className="relative w-32 h-32 mb-3">
                    <svg className="w-full h-full transform -rotate-90">
                      {/* Background circle - lighter for low scores */}
                      <circle
                        cx="64"
                        cy="64"
                        r="56"
                        stroke={(winsData.health_score?.score || 85) < 50 ? '#FEE2E2' : '#E2E8F0'}
                        strokeWidth="14"
                        fill="none"
                      />
                      {/* Progress circle with enhanced visibility */}
                      <circle
                        cx="64"
                        cy="64"
                        r="56"
                        stroke={winsData.health_score?.color || '#10B981'}
                        strokeWidth="14"
                        fill="none"
                        strokeDasharray={`${((winsData.health_score?.score || 85) / 100) * 351.68} 351.68`}
                        strokeLinecap="round"
                        style={{
                          transition: "stroke-dasharray 1s ease-out",
                          filter: (winsData.health_score?.score || 85) < 50 ? 'drop-shadow(0 0 4px rgba(239, 68, 68, 0.4))' : 'none'
                        }}
                      />
                    </svg>
                    <div className="absolute inset-0 flex flex-col items-center justify-center">
                      <div
                        className="text-3xl font-bold"
                        style={{
                          color: (winsData.health_score?.score || 85) < 50 ? winsData.health_score?.color : '#2D3748'
                        }}
                      >
                        {winsData.health_score?.score || 85}
                      </div>
                      <div className="text-xs text-[#718096]">out of 100</div>
                    </div>
                  </div>
                  <h3 className="text-sm font-bold text-[#2D3748] mb-1">Warehouse Health Score</h3>
                  <div className="text-xs font-bold mb-1" style={{ color: winsData.health_score?.color || '#10B981' }}>
                    {winsData.health_score?.label || 'Excellent'}
                  </div>
                  <div className="text-xs text-[#718096]">
                    Based on {(winsData.totals?.total_pallets || 500).toLocaleString()} pallets
                  </div>
                </>
              )}
            </div>
          </CardContent>
        </Card>

        {/* Quick Fix Actions - Actionable Items (Subtle Green Accents) */}
        <Card
          className="group relative overflow-hidden cursor-pointer hover:shadow-lg hover:scale-[1.02] transition-all duration-200 border-2 border-slate-200 hover:border-green-300"
          onClick={() => setCurrentView('action-center')}
        >
          <CardContent className="relative p-6">
            <div className="flex items-center justify-between mb-4">
              <div className="flex items-center gap-2">
                <CheckCircle2 className="w-5 h-5 text-success" />
                <h3 className="text-sm font-bold text-[#2D3748]">Quick Fix Actions</h3>
              </div>
              <ChevronRight className="w-4 h-4 text-muted-foreground group-hover:text-success transition-colors" />
            </div>
            <div className="space-y-2">
              {loading ? (
                /* Loading State */
                <div className="flex flex-col items-center justify-center py-6">
                  <div className="animate-spin rounded-full h-10 w-10 border-b-2 border-success mb-2"></div>
                  <div className="text-xs text-muted-foreground">Loading...</div>
                </div>
              ) : quickFixActions.length === 0 ? (
                /* Empty State - Show next best action */
                <div className="flex flex-col items-center justify-center py-6">
                  <CheckCircle2 className="w-10 h-10 text-muted-foreground/30 mb-2" />
                  <div className="text-xs font-medium text-muted-foreground">All quick fixes complete!</div>
                  {actionData && actionData.totalActiveItems > 0 ? (
                    <div className="text-xs text-muted-foreground/70 mt-1">
                      Focus on {actionData.totalActiveItems} priority {actionData.totalActiveItems === 1 ? 'action' : 'actions'}
                    </div>
                  ) : (
                    <div className="text-xs text-success mt-1">Warehouse operations smooth</div>
                  )}
                </div>
              ) : (
                /* Data Display State */
                <>
                  {quickFixActions.map((action, index) => (
                    <div key={index} className="flex items-center justify-between p-2 bg-success/5 rounded-lg">
                      <div>
                        <p className="font-medium text-success text-xs">{action.type}</p>
                        <p className="text-xs text-muted-foreground">{getQuickFixActionDescription(action.type)}</p>
                      </div>
                      <span className="text-lg font-bold text-success">{action.count}</span>
                    </div>
                  ))}
                  {/* Total Count Footer */}
                  {quickFixActions.length > 0 && (
                    <div className="pt-2 mt-2 border-t border-success/20">
                      <div className="text-xs text-center text-muted-foreground">
                        <span className="font-medium text-success">
                          {quickFixActions.reduce((sum, action) => sum + action.count, 0)}
                        </span>
                        {' '}total quick fixes available
                      </div>
                    </div>
                  )}
                </>
              )}
            </div>
          </CardContent>
        </Card>

        {/* Space Utilization - Steel Gray Professional */}
        <Card
          className="group relative overflow-hidden cursor-pointer hover:shadow-lg hover:scale-[1.02] transition-all duration-200 border-2 border-slate-200 hover:border-slate-300"
          onClick={() => setCurrentView('analytics')}
        >
          <CardContent className="relative p-6">
            <div className="flex items-center justify-between mb-4">
              <div className="flex items-center gap-2">
                <Activity className="w-5 h-5 text-secondary" />
                <h3 className="text-sm font-bold text-[#2D3748]">Space Utilization</h3>
              </div>
              <ChevronRight className="w-4 h-4 text-muted-foreground group-hover:text-secondary transition-colors" />
            </div>
            {loading ? (
              /* Loading State */
              <div className="flex flex-col items-center justify-center py-6">
                <div className="animate-spin rounded-full h-10 w-10 border-b-2 border-secondary mb-2"></div>
                <div className="text-xs text-muted-foreground">Loading...</div>
              </div>
            ) : !spaceUtilization ? (
              /* Empty State */
              <div className="flex flex-col items-center justify-center py-6">
                <Activity className="w-10 h-10 text-muted-foreground/30 mb-2" />
                <div className="text-xs text-muted-foreground">Awaiting analysis data</div>
              </div>
            ) : (
              /* Data Display State */
              <>
                <div className="text-4xl font-bold text-secondary mb-2" style={{ fontFamily: 'Roboto, sans-serif' }}>
                  {spaceUtilization.utilization_percentage.toFixed(1)}%
                </div>
                <div className="text-xs text-muted-foreground mb-3">
                  {spaceUtilization.inventory_count.toLocaleString()} of {spaceUtilization.warehouse_capacity.toLocaleString()} pallets used
                </div>
                <div className="w-full bg-gray-200 rounded-full h-2">
                  <div
                    className="bg-secondary h-2 rounded-full transition-all duration-500"
                    style={{ width: `${Math.min(spaceUtilization.utilization_percentage, 100)}%` }}
                  ></div>
                </div>
              </>
            )}
          </CardContent>
        </Card>
      </div>

      {/* Footer */}
      <div className="text-center text-base font-medium text-muted-foreground/80 mt-16">
        <p>Built by warehouse professionals • Preventing pallet losses since day one</p>
      </div>
    </div>
  )
}
