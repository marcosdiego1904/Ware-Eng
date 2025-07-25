"use client"

import { useEffect, useState } from 'react'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Badge } from '@/components/ui/badge'
import { useDashboardStore } from '@/lib/store'
import { reportsApi, Report } from '@/lib/reports'
import { 
  AlertTriangle, 
  Package, 
  MapPin, 
  CheckCircle2, 
  Clock,
  TrendingUp,
  FileText,
  Upload
} from 'lucide-react'

export function OverviewView() {
  const { reports, setReports, setCurrentView } = useDashboardStore()
  const [isLoading, setIsLoading] = useState(true)
  const [latestReport, setLatestReport] = useState<Report | null>(null)

  useEffect(() => {
    loadReports()
  }, [])

  const loadReports = async () => {
    try {
      setIsLoading(true)
      const data = await reportsApi.getReports()
      setReports(data.reports)
      if (data.reports.length > 0) {
        setLatestReport(data.reports[0]) // Most recent report
      }
    } catch (error) {
      console.error('Failed to load reports:', error)
    } finally {
      setIsLoading(false)
    }
  }

  // Calculate summary metrics from reports
  const totalReports = reports.length
  const totalAnomalies = reports.reduce((sum, report) => sum + report.anomaly_count, 0)
  const reportsThisWeek = reports.filter(report => {
    const reportDate = new Date(report.timestamp)
    const oneWeekAgo = new Date()
    oneWeekAgo.setDate(oneWeekAgo.getDate() - 7)
    return reportDate >= oneWeekAgo
  }).length

  const quickStats = [
    {
      title: "Total Reports",
      value: totalReports.toString(),
      icon: FileText,
      color: "text-blue-600 bg-blue-100",
      change: `+${reportsThisWeek} this week`
    },
    {
      title: "Total Anomalies",
      value: totalAnomalies.toString(),
      icon: AlertTriangle,
      color: "text-red-600 bg-red-100",
      change: latestReport ? `${latestReport.anomaly_count} in latest` : "No recent data"
    },
    {
      title: "Active Analysis",
      value: Math.max(0, 3 - totalReports).toString(),
      icon: Package,
      color: "text-green-600 bg-green-100",
      change: `${3 - totalReports} remaining`
    },
    {
      title: "System Status",
      value: "Operational",
      icon: CheckCircle2,
      color: "text-green-600 bg-green-100",
      change: "All systems online"
    }
  ]

  return (
    <div className="p-6 space-y-6">
      {/* Quick Stats */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        {quickStats.map((stat, index) => (
          <Card key={index}>
            <CardContent className="p-4">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm text-gray-600 mb-1">{stat.title}</p>
                  <p className="text-2xl font-bold">{stat.value}</p>
                  <p className="text-xs text-gray-500 mt-1">{stat.change}</p>
                </div>
                <div className={`p-3 rounded-full ${stat.color}`}>
                  <stat.icon className="w-6 h-6" />
                </div>
              </div>
            </CardContent>
          </Card>
        ))}
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Recent Reports */}
        <Card>
          <CardHeader className="pb-3">
            <CardTitle className="flex items-center justify-between">
              Recent Reports
              <Button 
                variant="outline" 
                size="sm"
                onClick={() => setCurrentView('reports')}
              >
                View All
              </Button>
            </CardTitle>
          </CardHeader>
          <CardContent>
            {isLoading ? (
              <div className="space-y-2">
                {[1, 2, 3].map((i) => (
                  <div key={i} className="h-16 bg-gray-100 rounded animate-pulse"></div>
                ))}
              </div>
            ) : reports.length === 0 ? (
              <div className="text-center py-8">
                <FileText className="w-12 h-12 text-gray-400 mx-auto mb-3" />
                <p className="text-gray-600 mb-2">No reports yet</p>
                <Button 
                  size="sm"
                  onClick={() => setCurrentView('new-analysis')}
                >
                  Create Your First Report
                </Button>
              </div>
            ) : (
              <div className="space-y-3">
                {reports.slice(0, 5).map((report) => (
                  <div key={report.id} className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
                    <div className="flex items-center gap-3">
                      <div className="w-10 h-10 bg-blue-100 rounded-lg flex items-center justify-center">
                        <FileText className="w-5 h-5 text-blue-600" />
                      </div>
                      <div>
                        <p className="font-medium text-sm">{report.report_name}</p>
                        <p className="text-xs text-gray-500">
                          {new Date(report.timestamp).toLocaleDateString()}
                        </p>
                      </div>
                    </div>
                    <Badge variant={report.anomaly_count > 0 ? "destructive" : "secondary"}>
                      {report.anomaly_count} anomalies
                    </Badge>
                  </div>
                ))}
              </div>
            )}
          </CardContent>
        </Card>

        {/* Quick Actions */}
        <Card>
          <CardHeader className="pb-3">
            <CardTitle>Quick Actions</CardTitle>
          </CardHeader>
          <CardContent className="space-y-3">
            <Button 
              className="w-full justify-start gap-3 h-auto p-4"
              onClick={() => setCurrentView('new-analysis')}
            >
              <Upload className="w-5 h-5" />
              <div className="text-left">
                <div className="font-medium">Start New Analysis</div>
                <div className="text-xs text-blue-100">Upload inventory files and detect anomalies</div>
              </div>
            </Button>
            
            <Button 
              variant="outline" 
              className="w-full justify-start gap-3 h-auto p-4"
              onClick={() => setCurrentView('reports')}
            >
              <FileText className="w-5 h-5" />
              <div className="text-left">
                <div className="font-medium">View Reports</div>
                <div className="text-xs text-gray-500">Manage and review analysis reports</div>
              </div>
            </Button>
            
            <Button 
              variant="outline" 
              className="w-full justify-start gap-3 h-auto p-4"
              onClick={() => setCurrentView('rules')}
            >
              <Package className="w-5 h-5" />
              <div className="text-left">
                <div className="font-medium">Configure Rules</div>
                <div className="text-xs text-gray-500">Set up warehouse rules and parameters</div>
              </div>
            </Button>
          </CardContent>
        </Card>
      </div>

      {/* Latest Report Preview */}
      {latestReport && (
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <TrendingUp className="w-5 h-5" />
              Latest Analysis Overview
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              <div className="text-center p-4 bg-gray-50 rounded-lg">
                <div className="text-2xl font-bold text-blue-600">{latestReport.anomaly_count}</div>
                <div className="text-sm text-gray-600">Total Anomalies</div>
              </div>
              <div className="text-center p-4 bg-gray-50 rounded-lg">
                <div className="text-2xl font-bold text-green-600">
                  {new Date(latestReport.timestamp).toLocaleDateString()}
                </div>
                <div className="text-sm text-gray-600">Analysis Date</div>
              </div>
              <div className="text-center p-4 bg-gray-50 rounded-lg">
                <div className="text-2xl font-bold text-purple-600">Active</div>
                <div className="text-sm text-gray-600">Status</div>
              </div>
            </div>
            <div className="mt-4 text-center">
              <Button 
                variant="outline"
                onClick={() => setCurrentView('reports')}
              >
                View Full Report
              </Button>
            </div>
          </CardContent>
        </Card>
      )}
    </div>
  )
}