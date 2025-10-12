"use client"

import { useState, useEffect } from 'react'
import { Button } from "@/components/ui/button"
import { Badge } from "@/components/ui/badge"
import { Card } from "@/components/ui/card"
import { Progress } from "@/components/ui/progress"
import { Activity, Calendar, ArrowLeft, AlertTriangle, Sparkles, MapPin } from "lucide-react"
import { useDashboardStore } from '@/lib/store'
import { reportsApi, Report, ReportDetails, Anomaly, SpaceUtilization } from '@/lib/reports'

interface AnalyticsData {
  total: number
  criticalLocations: string[]
  breakdown: {
    receiving: number
    aisle: number
    capacity: number
    errors: number
  }
  spaceUtilization: {
    percentage: number
    availableLocations: number
    totalLocations: number
    inventoryCount: number  // Actual pallets in warehouse
  }
  resolvedToday: number
  resolvedReceiving: number
}

export function LocationIntelligenceView() {
  const { setCurrentView, setActionCenterPreselectedCategory, setReportToOpen } = useDashboardStore()
  const [analyticsData, setAnalyticsData] = useState<AnalyticsData | null>(null)
  const [isLoading, setIsLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [latestReportId, setLatestReportId] = useState<number | null>(null)

  useEffect(() => {
    loadAnalyticsData()
  }, [])

  const loadAnalyticsData = async () => {
    try {
      setIsLoading(true)
      setError(null)

      // Get all reports
      const response = await reportsApi.getReports()
      const reports = response.reports || []

      if (reports.length === 0) {
        setAnalyticsData({
          total: 0,
          criticalLocations: [],
          breakdown: { receiving: 0, aisle: 0, capacity: 0, errors: 0 },
          spaceUtilization: { percentage: 0, availableLocations: 0, totalLocations: 0, inventoryCount: 0 },
          resolvedToday: 0,
          resolvedReceiving: 0
        })
        setIsLoading(false)
        return
      }

      // Get the most recent report with anomalies
      const recentReport = reports.find(r => r.anomaly_count > 0) || reports[0]

      // Store the report ID for navigation
      setLatestReportId(recentReport.id)

      // Fetch detailed report data
      const details = await reportsApi.getReportDetails(recentReport.id)

      // Fetch space utilization data with fallback
      let spaceUtilization
      try {
        console.log(`[ANALYTICS] Fetching space utilization for report ${recentReport.id}...`)
        spaceUtilization = await reportsApi.getSpaceUtilization(recentReport.id)
        console.log('[ANALYTICS] Space utilization API response:', spaceUtilization)
      } catch (spaceUtilErr) {
        console.warn('[ANALYTICS] Space utilization API failed, using fallback calculation')
        console.error('[ANALYTICS] Error details:', spaceUtilErr)
        // Fallback: use problem density calculation
        const totalLocations = details.locations.length
        const locationsWithActiveAnomalies = details.locations.filter(loc =>
          (loc.anomalies || []).some(a => a.status !== 'Resolved')
        ).length
        const healthyLocations = totalLocations - locationsWithActiveAnomalies
        const problemDensityPercentage = totalLocations > 0
          ? ((locationsWithActiveAnomalies / totalLocations) * 100)
          : 0

        spaceUtilization = {
          warehouse_capacity: totalLocations,
          inventory_count: 0,
          utilization_percentage: parseFloat(problemDensityPercentage.toFixed(1)),
          available_space: healthyLocations,
          warehouse_name: 'Default',
          warehouse_id: 'DEFAULT'
        } as SpaceUtilization
      }

      // Calculate analytics from real data
      const analytics = calculateAnalytics(details, reports, spaceUtilization)
      setAnalyticsData(analytics)
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to load analytics data')
      console.error('Analytics data loading error:', err)
    } finally {
      setIsLoading(false)
    }
  }

  const calculateAnalytics = (
    details: ReportDetails,
    allReports: Report[],
    spaceUtilization: SpaceUtilization
  ): AnalyticsData => {
    // Extract all anomalies from locations
    const allAnomalies = details.locations.flatMap(loc =>
      (loc.anomalies || []).map(anomaly => ({
        ...anomaly,
        locationName: loc.name
      }))
    )

    // Filter out resolved anomalies for "at risk" count
    const activeAnomalies = allAnomalies.filter(a =>
      a.status !== 'Resolved' && a.status !== 'Acknowledged'
    )

    // Total pallets at risk = count of active anomalies
    const totalAtRisk = activeAnomalies.length

    // Categorize by location type
    const breakdownCounts = {
      receiving: 0,
      aisle: 0,
      capacity: 0,
      errors: 0
    }

    activeAnomalies.forEach(anomaly => {
      const locationName = anomaly.locationName?.toUpperCase() || ''

      // Categorize by anomaly type and location
      if (anomaly.anomaly_type === 'Stagnant Pallet' && locationName.includes('RECV')) {
        breakdownCounts.receiving++
      } else if (anomaly.anomaly_type === 'Stagnant Pallet' &&
                 (locationName.includes('AISLE') || locationName.match(/^\d+\./))) {
        breakdownCounts.aisle++
      } else if (anomaly.anomaly_type.includes('Capacity') ||
                 anomaly.anomaly_type.includes('Overcapacity')) {
        breakdownCounts.capacity++
      } else if (anomaly.anomaly_type === 'Invalid Location' ||
                 anomaly.anomaly_type === 'Location Mapping Error' ||
                 anomaly.anomaly_type === 'Data Integrity') {
        breakdownCounts.errors++
      } else {
        // Default categorization based on location name
        if (locationName.includes('RECV') || locationName.includes('DOCK')) {
          breakdownCounts.receiving++
        } else if (locationName.includes('AISLE') || locationName.match(/^\d+\./)) {
          breakdownCounts.aisle++
        } else {
          breakdownCounts.errors++
        }
      }
    })

    // Find high maintenance locations (locations with 3+ active anomalies)
    const locationAnomalyCounts = new Map<string, number>()
    activeAnomalies.forEach(anomaly => {
      const loc = anomaly.locationName || anomaly.location
      locationAnomalyCounts.set(loc, (locationAnomalyCounts.get(loc) || 0) + 1)
    })

    const criticalLocations = Array.from(locationAnomalyCounts.entries())
      .filter(([_, count]) => count >= 3)
      .sort((a, b) => b[1] - a[1])
      .slice(0, 5)
      .map(([location]) => location)

    // Count resolved anomalies (from current report)
    const resolvedAnomalies = allAnomalies.filter(a =>
      a.status === 'Resolved' || a.status === 'Acknowledged'
    )
    const resolvedToday = resolvedAnomalies.length

    // Count resolved by category for motivational message
    const resolvedReceiving = resolvedAnomalies.filter(a => {
      const locationName = a.locationName?.toUpperCase() || ''
      return locationName.includes('RECV') || locationName.includes('DOCK')
    }).length

    return {
      total: totalAtRisk,
      criticalLocations,
      breakdown: breakdownCounts,
      spaceUtilization: {
        percentage: spaceUtilization.utilization_percentage,
        availableLocations: spaceUtilization.available_space,
        totalLocations: spaceUtilization.warehouse_capacity,
        inventoryCount: spaceUtilization.inventory_count
      },
      resolvedToday,
      resolvedReceiving
    }
  }

  // Use real data if loaded, otherwise show loading/error state
  const riskData = analyticsData ? {
    total: analyticsData.total,
    criticalLocations: analyticsData.criticalLocations,
    breakdown: analyticsData.breakdown
  } : {
    total: 0,
    criticalLocations: [],
    breakdown: { receiving: 0, aisle: 0, capacity: 0, errors: 0 }
  }

  const warehouseHealth = analyticsData ? {
    spaceUtilization: analyticsData.spaceUtilization
  } : {
    spaceUtilization: { percentage: 0, availableLocations: 0, totalLocations: 0, inventoryCount: 0 }
  }

  // Calculate max value for bar scaling
  const maxRiskValue = Math.max(
    riskData.breakdown.receiving,
    riskData.breakdown.aisle,
    riskData.breakdown.capacity,
    riskData.breakdown.errors,
  )

  const getRiskBarWidth = (value: number) => {
    return (value / maxRiskValue) * 100
  }

  const handleNavigateToActionCenter = (categoryId?: string) => {
    // Set the pre-selected category before navigating
    setActionCenterPreselectedCategory(categoryId)
    setCurrentView('action-center')
  }

  const handleNavigateToReportsAnalytics = () => {
    // Navigate to reports view and open the latest report's Analytics tab
    if (latestReportId) {
      setReportToOpen({ reportId: latestReportId, tab: 'analytics' })
    }
    setCurrentView('reports')
  }

  // Loading state
  if (isLoading) {
    return (
      <div className="min-h-screen bg-background">
        <header className="border-b bg-card">
          <div className="px-6 py-4">
            <div className="flex items-center gap-4">
              <Button variant="ghost" size="sm" onClick={() => setCurrentView('overview')}>
                <ArrowLeft className="w-4 h-4" />
                Back to Dashboard
              </Button>
              <div>
                <h1 className="text-xl font-bold text-foreground">Analytics Dashboard</h1>
                <p className="text-sm text-muted-foreground">Loading analytics data...</p>
              </div>
            </div>
          </div>
        </header>
        <main className="px-6 py-8 max-w-7xl mx-auto">
          <div className="flex items-center justify-center h-64">
            <div className="text-center">
              <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-[#FF6B35] mx-auto mb-4"></div>
              <p className="text-gray-600">Analyzing warehouse data...</p>
            </div>
          </div>
        </main>
      </div>
    )
  }

  // Error state
  if (error) {
    return (
      <div className="min-h-screen bg-background">
        <header className="border-b bg-card">
          <div className="px-6 py-4">
            <div className="flex items-center gap-4">
              <Button variant="ghost" size="sm" onClick={() => setCurrentView('overview')}>
                <ArrowLeft className="w-4 h-4" />
                Back to Dashboard
              </Button>
              <div>
                <h1 className="text-xl font-bold text-foreground">Analytics Dashboard</h1>
              </div>
            </div>
          </div>
        </header>
        <main className="px-6 py-8 max-w-7xl mx-auto">
          <Card className="p-6 border-2 border-red-200 bg-red-50">
            <div className="flex items-center gap-3">
              <AlertTriangle className="w-6 h-6 text-red-600" />
              <div>
                <h3 className="text-lg font-bold text-red-900">Failed to Load Analytics</h3>
                <p className="text-sm text-red-700">{error}</p>
                <Button
                  variant="outline"
                  size="sm"
                  className="mt-3"
                  onClick={loadAnalyticsData}
                >
                  Try Again
                </Button>
              </div>
            </div>
          </Card>
        </main>
      </div>
    )
  }

  return (
    <div className="min-h-screen bg-background">
      {/* Header */}
      <header className="border-b bg-card">
        <div className="px-6 py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-4">
              <Button
                variant="ghost"
                size="sm"
                onClick={() => setCurrentView('overview')}
                className="flex items-center gap-2"
              >
                <ArrowLeft className="w-4 h-4" />
                Back to Dashboard
              </Button>
              <div>
                <h1 className="text-xl font-bold text-foreground">Analytics Dashboard</h1>
                <p className="text-sm text-muted-foreground">Strategic pattern recognition and performance analysis</p>
              </div>
            </div>
            <div className="flex items-center gap-4">
              <Badge variant="outline" className="text-sm">
                <Activity className="w-3 h-3 mr-1" />
                Live Data
              </Badge>
              <Button variant="outline" size="sm" onClick={loadAnalyticsData}>
                <Calendar className="w-4 h-4 mr-2" />
                Refresh Data
              </Button>
            </div>
          </div>
        </div>
      </header>

      <main className="px-6 py-8 max-w-7xl mx-auto">
        {/* TIER 1: PALLET LOSS RISK ASSESSMENT */}
        <Card className="p-5 mb-8 border-2 border-[#CBD5E0]">
          {/* Integrated Headline with Metric */}
          <div className="flex items-baseline gap-3 mb-4">
            <AlertTriangle className="w-6 h-6 text-[#FF6B35] flex-shrink-0" />
            <h2 className="text-4xl font-bold text-[#FF6B35]">{riskData.total}</h2>
            <span className="text-lg font-semibold text-[#2D3748]">pallets at risk</span>
            <div className="ml-auto">
              <span className="text-sm text-[#718096]">
                {riskData.criticalLocations.length} high-maintenance locations
              </span>
            </div>
          </div>

          {/* Compact Horizontal Bar Chart */}
          <div className="space-y-2.5">
            {/* RECEIVING */}
            <div
              onClick={() => handleNavigateToActionCenter('forgotten-pallets')}
              className="flex items-center gap-3 group cursor-pointer hover:bg-[#FFF5F0] px-2 py-1.5 rounded-lg transition-colors"
            >
              <span className="text-sm font-semibold text-[#2D3748] w-24">Receiving</span>
              <div className="flex-1">
                <div className="h-6 bg-[#F7FAFC] rounded-full overflow-hidden border border-[#E2E8F0]">
                  <div
                    className="h-full bg-[#FF6B35] transition-all flex items-center justify-end pr-2"
                    style={{ width: getRiskBarWidth(riskData.breakdown.receiving) + "%" }}
                  >
                    <span className="text-xs font-bold text-white">{riskData.breakdown.receiving}</span>
                  </div>
                </div>
              </div>
              <span className="text-[#FF6B35] opacity-0 group-hover:opacity-100 transition-opacity text-sm">→</span>
            </div>

            {/* AISLE */}
            <div
              onClick={() => handleNavigateToActionCenter('aisle-stuck')}
              className="flex items-center gap-3 group cursor-pointer hover:bg-[#FFF5F0] px-2 py-1.5 rounded-lg transition-colors"
            >
              <span className="text-sm font-semibold text-[#2D3748] w-24">Aisle</span>
              <div className="flex-1">
                <div className="h-6 bg-[#F7FAFC] rounded-full overflow-hidden border border-[#E2E8F0]">
                  <div
                    className="h-full bg-[#FF6B35] transition-all flex items-center justify-end pr-2"
                    style={{ width: getRiskBarWidth(riskData.breakdown.aisle) + "%" }}
                  >
                    <span className="text-xs font-bold text-white">{riskData.breakdown.aisle}</span>
                  </div>
                </div>
              </div>
              <span className="text-[#FF6B35] opacity-0 group-hover:opacity-100 transition-opacity text-sm">→</span>
            </div>

            {/* CAPACITY */}
            <div
              onClick={() => handleNavigateToActionCenter('overcapacity')}
              className="flex items-center gap-3 group cursor-pointer hover:bg-[#FFFBEB] px-2 py-1.5 rounded-lg transition-colors"
            >
              <span className="text-sm font-semibold text-[#2D3748] w-24">Capacity</span>
              <div className="flex-1">
                <div className="h-6 bg-[#F7FAFC] rounded-full overflow-hidden border border-[#E2E8F0]">
                  <div
                    className="h-full bg-[#D69E2E] transition-all flex items-center justify-end pr-2"
                    style={{ width: getRiskBarWidth(riskData.breakdown.capacity) + "%" }}
                  >
                    <span className="text-xs font-bold text-white">{riskData.breakdown.capacity}</span>
                  </div>
                </div>
              </div>
              <span className="text-[#D69E2E] opacity-0 group-hover:opacity-100 transition-opacity text-sm">→</span>
            </div>

            {/* ERRORS */}
            <div
              onClick={() => handleNavigateToActionCenter('invalid-locations')}
              className="flex items-center gap-3 group cursor-pointer hover:bg-[#FFFBEB] px-2 py-1.5 rounded-lg transition-colors"
            >
              <span className="text-sm font-semibold text-[#2D3748] w-24">Errors</span>
              <div className="flex-1">
                <div className="h-6 bg-[#F7FAFC] rounded-full overflow-hidden border border-[#E2E8F0]">
                  <div
                    className="h-full bg-[#D69E2E] transition-all flex items-center justify-end pr-2"
                    style={{ width: getRiskBarWidth(riskData.breakdown.errors) + "%" }}
                  >
                    <span className="text-xs font-bold text-white">{riskData.breakdown.errors}</span>
                  </div>
                </div>
              </div>
              <span className="text-[#D69E2E] opacity-0 group-hover:opacity-100 transition-opacity text-sm">→</span>
            </div>
          </div>

          {/* Compact Action Button */}
          <div className="flex justify-end mt-4">
            <Button
              variant="ghost"
              size="sm"
              className="text-sm"
              onClick={handleNavigateToReportsAnalytics}
            >
              View Complete Analysis →
            </Button>
          </div>
        </Card>

        {/* TIER 2: WAREHOUSE HEALTH AT-A-GLANCE */}
        <div className="grid grid-cols-2 gap-6 mb-10">
          {/* High Maintenance Locations Card */}
          <Card className="p-6 border-2 border-[#CBD5E0]">
            <div className="flex items-center gap-2 mb-4">
              <MapPin className="w-5 h-5 text-[#FF6B35]" />
              <h3 className="text-sm font-bold text-[#2D3748]">High Maintenance Locations</h3>
            </div>

            <div className="text-4xl font-bold text-[#FF6B35] mb-3">{riskData.criticalLocations.length}</div>

            <div className="flex flex-wrap gap-2">
              {riskData.criticalLocations.map((location) => (
                <Badge
                  key={location}
                  variant="outline"
                  className="bg-[#FFF5F0] border-[#FF6B35] text-[#FF6B35] text-xs font-semibold"
                >
                  {location}
                </Badge>
              ))}
            </div>
          </Card>

          {/* Space Utilization Card */}
          <Card className="p-6 border-2 border-[#CBD5E0]">
            <div className="flex items-center gap-2 mb-4">
              <Activity className="w-5 h-5 text-[#4299E1]" />
              <h3 className="text-sm font-bold text-[#2D3748]">Space Utilization</h3>
            </div>

            <div className="mb-4">
              <Progress
                value={Math.min(warehouseHealth.spaceUtilization.percentage, 100)}
                className="h-2.5"
              />
            </div>

            <div className="text-4xl font-bold text-[#2D3748] mb-2">
              {warehouseHealth.spaceUtilization.percentage.toFixed(1)}%
              {warehouseHealth.spaceUtilization.percentage > 100 && (
                <span className="text-red-600 text-sm ml-2">(Over Capacity)</span>
              )}
            </div>

            <div className="text-sm text-[#718096]">
              {(() => {
                const capacity = warehouseHealth.spaceUtilization.totalLocations
                const inventoryCount = warehouseHealth.spaceUtilization.inventoryCount
                const overCapacity = inventoryCount - capacity

                return (
                  <>
                    {inventoryCount.toLocaleString()} of {capacity.toLocaleString()} pallets used
                    {overCapacity > 0 && (
                      <span className="text-red-600 block mt-1">
                        {overCapacity.toLocaleString()} pallets over capacity
                      </span>
                    )}
                  </>
                )
              })()}
            </div>
          </Card>
        </div>

        {/* TIER 3: MOTIVATIONAL CONTEXT */}
        {analyticsData && analyticsData.resolvedToday > 0 && (
          <Card className="p-5 bg-[#F7FAFC] border-2 border-[#9AE6B4] mb-8">
            <div className="flex items-start gap-3">
              <Sparkles className="w-5 h-5 text-[#38A169] flex-shrink-0 mt-0.5" />
              <div>
                <div className="text-base font-bold text-[#2D3748] mb-1">Nice Work!</div>
                <div className="text-sm text-[#4A5568]">
                  {analyticsData.resolvedToday === 1
                    ? '1 anomaly has been resolved'
                    : `${analyticsData.resolvedToday} anomalies have been resolved`}
                  {analyticsData.resolvedReceiving > 0 && (
                    <span> (including {analyticsData.resolvedReceiving} in RECEIVING)</span>
                  )}
                </div>
              </div>
            </div>
          </Card>
        )}

        {/* Footer */}
        <div className="text-center text-sm text-muted-foreground pt-4">
          <p>Analytics separated from operations to prevent analysis paralysis • Focus on patterns, not problems</p>
        </div>
      </main>
    </div>
  )
}