"use client"

import { useEffect, useState } from "react"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { MetricCard, StatCard } from "@/components/analytics/metric-card"
import { ExportButton } from "@/components/analytics/export-button"
import { Button } from "@/components/ui/button"
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select"
import {
  getDashboardMetrics,
  DashboardMetrics,
  DashboardFilters
} from "@/lib/pilot-analytics-api"
import {
  Users,
  FileUp,
  AlertCircle,
  Clock,
  TrendingUp,
  DollarSign,
  CheckCircle,
  XCircle,
  Activity,
  Monitor
} from "lucide-react"
import { useToast } from "@/hooks/use-toast"

export default function PilotAnalyticsPage() {
  const [metrics, setMetrics] = useState<DashboardMetrics | null>(null)
  const [loading, setLoading] = useState(true)
  const [dateRange, setDateRange] = useState<'7d' | '30d' | '90d' | 'all'>('30d')
  const { toast } = useToast()

  const filters: DashboardFilters = {
    start_date: getStartDate(dateRange),
    end_date: new Date().toISOString()
  }

  function getStartDate(range: typeof dateRange): string {
    const now = new Date()
    switch (range) {
      case '7d':
        return new Date(now.setDate(now.getDate() - 7)).toISOString()
      case '30d':
        return new Date(now.setDate(now.getDate() - 30)).toISOString()
      case '90d':
        return new Date(now.setDate(now.getDate() - 90)).toISOString()
      case 'all':
        return new Date(2024, 0, 1).toISOString() // Start of 2024
      default:
        return new Date(now.setDate(now.getDate() - 30)).toISOString()
    }
  }

  useEffect(() => {
    loadMetrics()
  }, [dateRange])

  async function loadMetrics() {
    setLoading(true)
    try {
      const data = await getDashboardMetrics(filters)
      setMetrics(data)
    } catch (error) {
      console.error('Failed to load metrics:', error)
      toast({
        title: "Failed to load analytics",
        description: "Could not fetch pilot program metrics. Please try again.",
        variant: "destructive"
      })
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="container mx-auto p-6 space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold">Pilot Analytics Dashboard</h1>
          <p className="text-muted-foreground mt-1">
            Monitor pilot program performance, usage, and ROI metrics
          </p>
        </div>
        <div className="flex items-center gap-3">
          <Select value={dateRange} onValueChange={(value: any) => setDateRange(value)}>
            <SelectTrigger className="w-[180px]">
              <SelectValue placeholder="Select range" />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="7d">Last 7 days</SelectItem>
              <SelectItem value="30d">Last 30 days</SelectItem>
              <SelectItem value="90d">Last 90 days</SelectItem>
              <SelectItem value="all">All time</SelectItem>
            </SelectContent>
          </Select>
          <ExportButton filters={filters} />
          <Button onClick={loadMetrics} variant="outline">
            Refresh
          </Button>
        </div>
      </div>

      {/* Usage Overview */}
      <section className="space-y-4">
        <h2 className="text-xl font-semibold">Usage Metrics</h2>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
          <MetricCard
            title="Total Sessions"
            value={metrics?.usage.total_sessions || 0}
            description="Login sessions"
            icon={<Users className="h-5 w-5" />}
            loading={loading}
          />

          <MetricCard
            title="Time Spent"
            value={`${Math.round((metrics?.usage.total_time_minutes || 0) / 60)}h ${Math.round((metrics?.usage.total_time_minutes || 0) % 60)}m`}
            description="Total active time"
            icon={<Clock className="h-5 w-5" />}
            loading={loading}
          />

          <MetricCard
            title="Files Uploaded"
            value={metrics?.usage.files_uploaded || 0}
            description="Inventory files processed"
            icon={<FileUp className="h-5 w-5" />}
            loading={loading}
          />

          <MetricCard
            title="Avg Session"
            value={`${Math.round(metrics?.usage.avg_session_duration || 0)} min`}
            description="Average session duration"
            icon={<Activity className="h-5 w-5" />}
            loading={loading}
          />
        </div>
      </section>

      {/* Business Impact */}
      <section className="space-y-4">
        <h2 className="text-xl font-semibold">Business Impact</h2>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <DollarSign className="h-5 w-5 text-green-600" />
                Time & Cost Savings
              </CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              <div>
                <p className="text-sm text-muted-foreground">Time Saved</p>
                <p className="text-3xl font-bold">
                  {Math.round((metrics?.business.time_saved_minutes || 0) / 60)} hours
                </p>
                <p className="text-xs text-muted-foreground mt-1">
                  {Math.round(metrics?.business.time_saved_minutes || 0)} minutes total
                </p>
              </div>

              <div>
                <p className="text-sm text-muted-foreground">Cost Savings</p>
                <p className="text-3xl font-bold text-green-600">
                  ${(metrics?.business.cost_savings || 0).toLocaleString(undefined, { minimumFractionDigits: 2, maximumFractionDigits: 2 })}
                </p>
                <p className="text-xs text-muted-foreground mt-1">
                  Based on $50/hr labor rate
                </p>
              </div>
            </CardContent>
          </Card>

          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <AlertCircle className="h-5 w-5 text-orange-600" />
                Issues Detected
              </CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              <div>
                <p className="text-sm text-muted-foreground">Total Issues</p>
                <p className="text-3xl font-bold">
                  {metrics?.business.total_issues || 0}
                </p>
              </div>

              <div className="grid grid-cols-2 gap-2 text-sm">
                <div>
                  <p className="text-muted-foreground">Resolved</p>
                  <p className="text-lg font-semibold text-green-600">
                    {metrics?.business.resolved_issues || 0}
                  </p>
                </div>
                <div>
                  <p className="text-muted-foreground">Pending</p>
                  <p className="text-lg font-semibold text-orange-600">
                    {(metrics?.business.total_issues || 0) - (metrics?.business.resolved_issues || 0)}
                  </p>
                </div>
              </div>

              <div>
                <p className="text-sm text-muted-foreground">Resolution Rate</p>
                <p className="text-2xl font-bold">
                  {metrics?.business.resolution_rate || 0}%
                </p>
              </div>
            </CardContent>
          </Card>

          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <TrendingUp className="h-5 w-5 text-blue-600" />
                Issues by Type
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="space-y-3">
                {Object.entries(metrics?.business.issues_by_rule || {}).slice(0, 5).map(([rule, count]) => (
                  <div key={rule} className="flex items-center justify-between">
                    <span className="text-sm truncate flex-1">{rule.replace(/_/g, ' ')}</span>
                    <span className="font-semibold ml-2">{count}</span>
                  </div>
                ))}
                {Object.keys(metrics?.business.issues_by_rule || {}).length === 0 && (
                  <p className="text-sm text-muted-foreground text-center py-4">
                    No issues detected yet
                  </p>
                )}
              </div>
            </CardContent>
          </Card>
        </div>
      </section>

      {/* Technical Performance */}
      <section className="space-y-4">
        <h2 className="text-xl font-semibold">Technical Performance</h2>

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
          <StatCard
            label="Upload Success Rate"
            value={`${metrics?.technical.success_rate || 0}%`}
            subtext={`${metrics?.technical.successful_uploads || 0} / ${metrics?.technical.total_uploads || 0} uploads`}
            icon={<CheckCircle className="h-5 w-5" />}
            color={
              (metrics?.technical.success_rate || 0) >= 95 ? 'green' :
              (metrics?.technical.success_rate || 0) >= 80 ? 'orange' : 'red'
            }
            loading={loading}
          />

          <StatCard
            label="Failed Uploads"
            value={metrics?.technical.failed_uploads || 0}
            subtext="Errors encountered"
            icon={<XCircle className="h-5 w-5" />}
            color={(metrics?.technical.failed_uploads || 0) === 0 ? 'green' : 'red'}
            loading={loading}
          />

          <StatCard
            label="Avg Processing Time"
            value={`${(metrics?.technical.avg_processing_time || 0).toFixed(1)}s`}
            subtext={`Min: ${(metrics?.technical.min_processing_time || 0).toFixed(1)}s, Max: ${(metrics?.technical.max_processing_time || 0).toFixed(1)}s`}
            icon={<Clock className="h-5 w-5" />}
            color={
              (metrics?.technical.avg_processing_time || 0) < 5 ? 'green' :
              (metrics?.technical.avg_processing_time || 0) < 10 ? 'orange' : 'red'
            }
            loading={loading}
          />

          <StatCard
            label="Primary Device"
            value={Object.keys(metrics?.technical.devices || {})[0] || 'N/A'}
            subtext={`Browser: ${Object.keys(metrics?.technical.browsers || {})[0] || 'N/A'}`}
            icon={<Monitor className="h-5 w-5" />}
            color="blue"
            loading={loading}
          />
        </div>
      </section>

      {/* Feature Usage */}
      {metrics?.usage.feature_usage && Object.keys(metrics.usage.feature_usage).length > 0 && (
        <section className="space-y-4">
          <h2 className="text-xl font-semibold">Feature Usage</h2>
          <Card>
            <CardHeader>
              <CardTitle>Event Breakdown</CardTitle>
              <CardDescription>Most frequently used features</CardDescription>
            </CardHeader>
            <CardContent>
              <div className="space-y-3">
                {Object.entries(metrics.usage.feature_usage)
                  .sort(([, a], [, b]) => b - a)
                  .slice(0, 10)
                  .map(([feature, count]) => (
                    <div key={feature} className="flex items-center justify-between">
                      <span className="text-sm font-medium">{feature.replace(/_/g, ' ')}</span>
                      <div className="flex items-center gap-3">
                        <div className="w-32 bg-gray-200 rounded-full h-2">
                          <div
                            className="bg-blue-600 h-2 rounded-full"
                            style={{
                              width: `${Math.min((count / Math.max(...Object.values(metrics.usage.feature_usage))) * 100, 100)}%`
                            }}
                          />
                        </div>
                        <span className="font-semibold text-sm w-12 text-right">{count}</span>
                      </div>
                    </div>
                  ))}
              </div>
            </CardContent>
          </Card>
        </section>
      )}

      {/* Error Summary */}
      {metrics?.technical.error_types && Object.keys(metrics.technical.error_types).length > 0 && (
        <section className="space-y-4">
          <h2 className="text-xl font-semibold">Errors & Issues</h2>
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <XCircle className="h-5 w-5 text-red-600" />
                Error Breakdown
              </CardTitle>
              <CardDescription>Common errors encountered during pilot</CardDescription>
            </CardHeader>
            <CardContent>
              <div className="space-y-2">
                {Object.entries(metrics.technical.error_types).map(([error, count]) => (
                  <div key={error} className="flex items-center justify-between p-2 bg-red-50 border border-red-200 rounded">
                    <span className="text-sm text-red-900">{error}</span>
                    <span className="font-semibold text-red-600">{count} occurrences</span>
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>
        </section>
      )}
    </div>
  )
}
