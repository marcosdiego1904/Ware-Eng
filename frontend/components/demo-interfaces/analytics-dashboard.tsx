'use client'

import * as React from "react"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Badge } from "@/components/ui/badge"
import { Progress } from "@/components/ui/progress"
import { Separator } from "@/components/ui/separator"
import { cn } from "@/lib/utils"

// Mock data for demonstration
const mockAnalyticsData = {
  performance: {
    resolvedToday: 12,
    remainingItems: 75,
    weeklyCompletion: 67,
    avgResolutionTime: 15,
    warehouseHealth: 82
  },
  hotspots: [
    { area: "RECV-01", percentage: 45, issue: "forgotten pallets", trend: "up" },
    { area: "AISLE-02", percentage: 32, issue: "stuck pallets", trend: "stable" },
    { area: "DOCK-B", percentage: 28, issue: "overcapacity violations", trend: "down" }
  ],
  rulePerformance: [
    { rule: "Stagnant Pallet Detection", triggers: 234, avgTime: "12ms", effectiveness: 95 },
    { rule: "Overcapacity Monitor", triggers: 89, avgTime: "18ms", effectiveness: 87 },
    { rule: "Lot Completion Tracker", triggers: 67, avgTime: "25ms", effectiveness: 92 },
    { rule: "Location Validator", triggers: 45, avgTime: "8ms", effectiveness: 98 }
  ],
  trends: {
    mondayAnomalies: 130,
    fridayAnomalies: 85,
    weeklyImprovement: 15,
    monthlyPattern: "December shows 40% more capacity issues"
  }
}

interface AnalyticsDashboardProps {
  className?: string
  onBackToHub?: () => void
}

export function AnalyticsDashboard({ className, onBackToHub }: AnalyticsDashboardProps) {
  return (
    <div className={cn("max-w-7xl mx-auto p-6 space-y-6", className)}>

      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-foreground flex items-center gap-3">
            📊 Warehouse Intelligence Report
          </h1>
          <p className="text-muted-foreground mt-1">
            Strategic analysis and performance insights for operational optimization
          </p>
        </div>
        <Button variant="outline" onClick={onBackToHub}>
          ← Back to Hub
        </Button>
      </div>

      {/* Performance Snapshot */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-5 gap-4">
        <Card>
          <CardContent className="p-4 text-center">
            <div className="text-2xl font-bold text-green-600 dark:text-green-400">
              {mockAnalyticsData.performance.resolvedToday}
            </div>
            <div className="text-sm text-muted-foreground mt-1">Resolved Today</div>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="p-4 text-center">
            <div className="text-2xl font-bold text-red-600 dark:text-red-400">
              {mockAnalyticsData.performance.remainingItems}
            </div>
            <div className="text-sm text-muted-foreground mt-1">Still Remaining</div>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="p-4 text-center">
            <div className="text-2xl font-bold text-blue-600 dark:text-blue-400">
              {mockAnalyticsData.performance.weeklyCompletion}%
            </div>
            <div className="text-sm text-muted-foreground mt-1">Week Completion</div>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="p-4 text-center">
            <div className="text-2xl font-bold text-purple-600 dark:text-purple-400">
              {mockAnalyticsData.performance.avgResolutionTime}m
            </div>
            <div className="text-sm text-muted-foreground mt-1">Avg Resolution</div>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="p-4 text-center">
            <div className="text-2xl font-bold text-emerald-600 dark:text-emerald-400">
              {mockAnalyticsData.performance.warehouseHealth}/100
            </div>
            <div className="text-sm text-muted-foreground mt-1">Health Score</div>
          </CardContent>
        </Card>
      </div>

      {/* Problem Hotspots and Rule Performance */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">

        {/* Problem Hotspots */}
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              🔥 Problem Hotspots
            </CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            {mockAnalyticsData.hotspots.map((hotspot, index) => (
              <div key={index} className="space-y-2">
                <div className="flex items-center justify-between">
                  <div className="font-medium">{hotspot.area}</div>
                  <div className="flex items-center gap-2">
                    <Badge variant="secondary">{hotspot.percentage}%</Badge>
                    <div className={cn(
                      "w-3 h-3 rounded-full",
                      hotspot.trend === "up" && "bg-red-500",
                      hotspot.trend === "down" && "bg-green-500",
                      hotspot.trend === "stable" && "bg-yellow-500"
                    )}></div>
                  </div>
                </div>
                <div className="text-sm text-muted-foreground">{hotspot.issue}</div>
                <Progress value={hotspot.percentage} className="h-2" />
              </div>
            ))}

            {/* Heatmap Visualization Placeholder */}
            <Separator className="my-4" />
            <div className="bg-muted/50 rounded-lg p-4 text-center">
              <div className="text-sm text-muted-foreground mb-2">Warehouse Layout Heatmap</div>
              <div className="grid grid-cols-8 gap-1">
                {Array.from({ length: 32 }, (_, i) => (
                  <div
                    key={i}
                    className={cn(
                      "aspect-square rounded-sm",
                      i < 8 ? "bg-red-200 dark:bg-red-900/50" :
                      i < 16 ? "bg-yellow-200 dark:bg-yellow-900/50" :
                      i < 24 ? "bg-green-200 dark:bg-green-900/50" :
                      "bg-gray-200 dark:bg-gray-700"
                    )}
                  ></div>
                ))}
              </div>
              <div className="text-xs text-muted-foreground mt-2">
                🔴 High Issues  🟡 Medium Issues  🟢 Good Performance  ⚪ Unused
              </div>
            </div>
          </CardContent>
        </Card>

        {/* Rule Performance */}
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              ⚡ Rule Performance
            </CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            {mockAnalyticsData.rulePerformance.map((rule, index) => (
              <div key={index} className="space-y-2">
                <div className="flex items-center justify-between">
                  <div className="font-medium text-sm">{rule.rule}</div>
                  <Badge variant="outline" className="text-xs">{rule.avgTime}</Badge>
                </div>
                <div className="flex items-center justify-between text-sm">
                  <div className="text-muted-foreground">
                    {rule.triggers} triggers this week
                  </div>
                  <div className="flex items-center gap-2">
                    <span className="text-xs text-muted-foreground">Effectiveness:</span>
                    <Badge variant="secondary" className="bg-green-100 text-green-700 dark:bg-green-900/30 dark:text-green-300">
                      {rule.effectiveness}%
                    </Badge>
                  </div>
                </div>
                <Progress value={rule.effectiveness} className="h-1.5" />
              </div>
            ))}

            <Separator className="my-4" />
            <div className="text-sm text-muted-foreground">
              <div className="flex items-center justify-between mb-2">
                <span>System Processing Speed:</span>
                <span className="font-medium text-foreground">700 records/1.01s</span>
              </div>
              <div className="flex items-center justify-between">
                <span>Rule Success Rate:</span>
                <span className="font-medium text-green-600 dark:text-green-400">100% (8/8)</span>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Trends & Patterns */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            📈 Trends & Patterns
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">

            {/* Day of Week Analysis */}
            <div className="space-y-3">
              <h4 className="font-semibold text-sm">Day-of-Week Impact</h4>
              <div className="space-y-2">
                <div className="flex items-center justify-between text-sm">
                  <span>Monday Anomalies:</span>
                  <Badge variant="destructive">{mockAnalyticsData.trends.mondayAnomalies}</Badge>
                </div>
                <div className="flex items-center justify-between text-sm">
                  <span>Friday Anomalies:</span>
                  <Badge variant="secondary">{mockAnalyticsData.trends.fridayAnomalies}</Badge>
                </div>
                <div className="text-xs text-muted-foreground mt-2">
                  Mondays show 53% more issues than Fridays
                </div>
              </div>
            </div>

            {/* Weekly Improvement */}
            <div className="space-y-3">
              <h4 className="font-semibold text-sm">Weekly Progress</h4>
              <div className="space-y-2">
                <div className="text-2xl font-bold text-green-600 dark:text-green-400">
                  +{mockAnalyticsData.trends.weeklyImprovement}%
                </div>
                <div className="text-xs text-muted-foreground">
                  Resolution speed improvement
                </div>
                <Progress value={mockAnalyticsData.trends.weeklyImprovement * 3} className="h-2" />
              </div>
            </div>

            {/* Seasonal Patterns */}
            <div className="space-y-3">
              <h4 className="font-semibold text-sm">Seasonal Impact</h4>
              <div className="text-sm">
                <div className="text-yellow-600 dark:text-yellow-400 font-medium mb-1">
                  December Alert
                </div>
                <div className="text-xs text-muted-foreground">
                  {mockAnalyticsData.trends.monthlyPattern}
                </div>
              </div>
            </div>

            {/* Capacity Trends */}
            <div className="space-y-3">
              <h4 className="font-semibold text-sm">Capacity Utilization</h4>
              <div className="space-y-2">
                <div className="text-2xl font-bold text-blue-600 dark:text-blue-400">20.7%</div>
                <div className="text-xs text-muted-foreground">Current utilization</div>
                <div className="text-xs text-green-600 dark:text-green-400">
                  ↗️ +5% from last week
                </div>
              </div>
            </div>
          </div>

          {/* Trend Chart Placeholder */}
          <Separator className="my-6" />
          <div className="bg-muted/50 rounded-lg p-6 text-center">
            <div className="text-sm text-muted-foreground mb-4">Weekly Anomaly Trends</div>
            <div className="flex items-end justify-center gap-2 h-32">
              {['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'].map((day, index) => (
                <div key={day} className="flex flex-col items-center gap-1">
                  <div
                    className="bg-blue-500 rounded-t"
                    style={{
                      width: '16px',
                      height: `${20 + (index * 8)}px`
                    }}
                  ></div>
                  <span className="text-xs text-muted-foreground">{day}</span>
                </div>
              ))}
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Actions Footer */}
      <Card className="bg-muted/30">
        <CardContent className="py-4">
          <div className="flex items-center justify-between">
            <div className="text-sm text-muted-foreground">
              Analysis updated: <span className="font-semibold text-foreground">2 minutes ago</span>
            </div>
            <div className="flex gap-2">
              <Button variant="outline" size="sm">
                Export Report
              </Button>
              <Button variant="outline" size="sm">
                Schedule Email
              </Button>
              <Button size="sm">
                View Detailed Analytics
              </Button>
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  )
}