"use client"

import { useState, useEffect } from 'react'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { 
  Select, 
  SelectContent, 
  SelectItem, 
  SelectTrigger, 
  SelectValue 
} from '@/components/ui/select'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs'
import { Progress } from '@/components/ui/progress'
import { 
  BarChart3, 
  TrendingUp, 
  TrendingDown, 
  Activity, 
  AlertTriangle,
  CheckCircle,
  Clock,
  Target,
  Zap,
  Download,
  RefreshCw,
  Filter,
  Calendar,
  Gauge
} from 'lucide-react'
import { useRulesStore, useRulesStats } from '@/lib/rules-store'
import { PRIORITY_LEVELS } from '@/lib/rules-types'

export function RuleAnalytics() {
  const { 
    rules,
    loadAnalytics
  } = useRulesStore()

  const rulesStats = useRulesStats()
  const [timeRange, setTimeRange] = useState('7d')
  const [selectedMetric, setSelectedMetric] = useState('performance')

  useEffect(() => {
    loadAnalytics()
  }, [])

  const mockAnalyticsData = {
    totalDetections: 1247,
    accuracyRate: 94.2,
    falsePositiveRate: 5.8,
    averageResponseTime: 1.3,
    topPerformingRules: [
      { name: 'Stagnant Pallets Detection', detections: 156, accuracy: 97.1 },
      { name: 'Location Mismatch Alert', detections: 134, accuracy: 95.8 },
      { name: 'Inventory Overflow Warning', detections: 98, accuracy: 92.4 }
    ],
    performanceTrends: {
      week: [85, 87, 91, 89, 94, 96, 94],
      month: [88, 90, 92, 89, 91, 94, 93, 95, 94, 96, 97, 94]
    }
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-2xl font-bold">Rule Analytics</h2>
          <p className="text-muted-foreground">
            Monitor performance and effectiveness of your warehouse rules
          </p>
        </div>
        <div className="flex gap-2">
          <Select value={timeRange} onValueChange={setTimeRange}>
            <SelectTrigger className="w-32">
              <SelectValue />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="24h">Last 24h</SelectItem>
              <SelectItem value="7d">Last 7 days</SelectItem>
              <SelectItem value="30d">Last 30 days</SelectItem>
              <SelectItem value="90d">Last 90 days</SelectItem>
            </SelectContent>
          </Select>
          <Button variant="outline" size="sm">
            <RefreshCw className="w-4 h-4 mr-2" />
            Refresh
          </Button>
          <Button variant="outline" size="sm">
            <Download className="w-4 h-4 mr-2" />
            Export
          </Button>
        </div>
      </div>

      {/* Key Metrics */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        <MetricCard
          title="Total Detections"
          value={mockAnalyticsData.totalDetections}
          change={+12.5}
          icon={Target}
          trend="up"
        />
        <MetricCard
          title="Accuracy Rate"
          value={`${mockAnalyticsData.accuracyRate}%`}
          change={+2.1}
          icon={CheckCircle}
          trend="up"
        />
        <MetricCard
          title="False Positive Rate"
          value={`${mockAnalyticsData.falsePositiveRate}%`}
          change={-1.3}
          icon={AlertTriangle}
          trend="down"
        />
        <MetricCard
          title="Avg Response Time"
          value={`${mockAnalyticsData.averageResponseTime}s`}
          change={-0.2}
          icon={Clock}
          trend="down"
        />
      </div>

      {/* Main Analytics Tabs */}
      <Tabs value={selectedMetric} onValueChange={setSelectedMetric} className="w-full">
        <TabsList className="grid w-full grid-cols-4">
          <TabsTrigger value="performance">Performance</TabsTrigger>
          <TabsTrigger value="rules">Rules Analysis</TabsTrigger>
          <TabsTrigger value="trends">Trends</TabsTrigger>
          <TabsTrigger value="insights">Insights</TabsTrigger>
        </TabsList>

        <TabsContent value="performance" className="space-y-6">
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            <PerformanceChart data={mockAnalyticsData.performanceTrends} timeRange={timeRange} />
            <RuleEfficiencyBreakdown rules={rules} />
          </div>
          <TopPerformingRules rules={mockAnalyticsData.topPerformingRules} />
        </TabsContent>

        <TabsContent value="rules" className="space-y-6">
          <RulesAnalysisGrid rules={rules} stats={rulesStats} />
        </TabsContent>

        <TabsContent value="trends" className="space-y-6">
          <TrendsAnalysis data={mockAnalyticsData} />
        </TabsContent>

        <TabsContent value="insights" className="space-y-6">
          <InsightsAndRecommendations rules={rules} analytics={mockAnalyticsData} />
        </TabsContent>
      </Tabs>
    </div>
  )
}

// Metric Card Component
function MetricCard({ 
  title, 
  value, 
  change, 
  icon: Icon, 
  trend 
}: {
  title: string
  value: string | number
  change: number
  icon: React.ComponentType<{ className?: string }>
  trend: 'up' | 'down'
}) {
  const changeColor = trend === 'up' ? 'text-green-600' : 'text-red-600'
  const TrendIcon = trend === 'up' ? TrendingUp : TrendingDown

  return (
    <Card>
      <CardContent className="p-6">
        <div className="flex items-center justify-between">
          <div className="space-y-2">
            <p className="text-sm font-medium text-muted-foreground">{title}</p>
            <p className="text-2xl font-bold">{value}</p>
            <div className={`flex items-center text-sm ${changeColor}`}>
              <TrendIcon className="w-4 h-4 mr-1" />
              {Math.abs(change)}% from last period
            </div>
          </div>
          <Icon className="w-8 h-8 text-muted-foreground" />
        </div>
      </CardContent>
    </Card>
  )
}

// Performance Chart Component
function PerformanceChart({ 
  data, 
  timeRange 
}: {
  data: { week: number[]; month: number[] }
  timeRange: string
}) {
  const chartData = timeRange === '7d' ? data.week : data.month
  const maxValue = Math.max(...chartData)

  return (
    <Card>
      <CardHeader>
        <CardTitle className="flex items-center gap-2">
          <BarChart3 className="w-5 h-5" />
          Detection Accuracy Over Time
        </CardTitle>
      </CardHeader>
      <CardContent>
        <div className="space-y-4">
          <div className="flex items-center justify-between text-sm">
            <span className="text-muted-foreground">Accuracy %</span>
            <span className="font-medium">Current: {chartData[chartData.length - 1]}%</span>
          </div>
          <div className="space-y-2">
            {chartData.map((value, index) => (
              <div key={index} className="flex items-center gap-3">
                <span className="text-xs text-muted-foreground w-8">
                  {timeRange === '7d' ? `D${index + 1}` : `W${index + 1}`}
                </span>
                <div className="flex-1">
                  <Progress 
                    value={(value / maxValue) * 100} 
                    className="h-3"
                  />
                </div>
                <span className="text-sm font-medium w-10">{value}%</span>
              </div>
            ))}
          </div>
        </div>
      </CardContent>
    </Card>
  )
}

// Rule Efficiency Breakdown
function RuleEfficiencyBreakdown({ rules }: { rules: Array<{ priority: string; is_active: boolean }> }) {
  const priorityBreakdown = Object.entries(PRIORITY_LEVELS).map(([key, priority]) => {
    const rulesInPriority = rules.filter(r => r.priority === key)
    const activeRules = rulesInPriority.filter(r => r.is_active)
    
    return {
      priority: priority.label,
      color: priority.color,
      total: rulesInPriority.length,
      active: activeRules.length,
      percentage: rulesInPriority.length > 0 ? (activeRules.length / rulesInPriority.length) * 100 : 0
    }
  })

  return (
    <Card>
      <CardHeader>
        <CardTitle className="flex items-center gap-2">
          <Gauge className="w-5 h-5" />
          Rules by Priority
        </CardTitle>
      </CardHeader>
      <CardContent className="space-y-4">
        {priorityBreakdown.map((item) => (
          <div key={item.priority} className="space-y-2">
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-2">
                <Badge variant={item.color as any}>{item.priority}</Badge>
                <span className="text-sm text-muted-foreground">
                  {item.active}/{item.total} active
                </span>
              </div>
              <span className="text-sm font-medium">{item.percentage.toFixed(1)}%</span>
            </div>
            <Progress value={item.percentage} className="h-2" />
          </div>
        ))}
      </CardContent>
    </Card>
  )
}

// Top Performing Rules
function TopPerformingRules({ 
  rules 
}: {
  rules: Array<{ name: string; detections: number; accuracy: number }>
}) {
  return (
    <Card>
      <CardHeader>
        <CardTitle className="flex items-center gap-2">
          <Zap className="w-5 h-5" />
          Top Performing Rules
        </CardTitle>
      </CardHeader>
      <CardContent>
        <div className="space-y-4">
          {rules.map((rule, index) => (
            <div key={index} className="flex items-center justify-between p-3 border rounded-lg">
              <div className="space-y-1">
                <h4 className="font-medium">{rule.name}</h4>
                <p className="text-sm text-muted-foreground">
                  {rule.detections} detections
                </p>
              </div>
              <div className="text-right">
                <Badge variant="default">{rule.accuracy}% accurate</Badge>
              </div>
            </div>
          ))}
        </div>
      </CardContent>
    </Card>
  )
}

// Rules Analysis Grid
function RulesAnalysisGrid({ 
  rules, 
  stats 
}: {
  rules: Array<{ priority: string; is_active: boolean }>
  stats: ReturnType<typeof useRulesStats>
}) {
  return (
    <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
      <Card>
        <CardHeader>
          <CardTitle>Rule Distribution</CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="grid grid-cols-2 gap-4">
            <div className="text-center">
              <p className="text-2xl font-bold text-green-600">{stats.active}</p>
              <p className="text-sm text-muted-foreground">Active Rules</p>
            </div>
            <div className="text-center">
              <p className="text-2xl font-bold text-gray-600">{stats.inactive}</p>
              <p className="text-sm text-muted-foreground">Inactive Rules</p>
            </div>
          </div>
          <Progress value={(stats.active / stats.total) * 100} className="h-3" />
          <p className="text-sm text-center text-muted-foreground">
            {((stats.active / stats.total) * 100).toFixed(1)}% of rules are currently active
          </p>
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <CardTitle>Rule Types</CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="grid grid-cols-2 gap-4">
            <div className="text-center">
              <p className="text-2xl font-bold text-blue-600">{stats.custom}</p>
              <p className="text-sm text-muted-foreground">Custom Rules</p>
            </div>
            <div className="text-center">
              <p className="text-2xl font-bold text-purple-600">{stats.default}</p>
              <p className="text-sm text-muted-foreground">Default Rules</p>
            </div>
          </div>
          <Progress value={(stats.custom / stats.total) * 100} className="h-3" />
          <p className="text-sm text-center text-muted-foreground">
            {((stats.custom / stats.total) * 100).toFixed(1)}% are custom-created rules
          </p>
        </CardContent>
      </Card>
    </div>
  )
}

// Trends Analysis
function TrendsAnalysis({ data: _data }: { data: Record<string, unknown> }) {
  return (
    <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Activity className="w-5 h-5" />
            Detection Trends
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="space-y-4">
            <div className="flex items-center justify-between">
              <span className="text-sm">This week vs last week</span>
              <Badge variant="default" className="bg-green-100 text-green-700">
                +12.5% increase
              </Badge>
            </div>
            <div className="flex items-center justify-between">
              <span className="text-sm">Accuracy improvement</span>
              <Badge variant="default" className="bg-blue-100 text-blue-700">
                +2.1% better
              </Badge>
            </div>
            <div className="flex items-center justify-between">
              <span className="text-sm">Response time optimization</span>
              <Badge variant="default" className="bg-purple-100 text-purple-700">
                -15% faster
              </Badge>
            </div>
          </div>
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Calendar className="w-5 h-5" />
            Peak Activity Times
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="space-y-3">
            <div className="flex items-center justify-between">
              <span className="text-sm">Monday 9:00 AM</span>
              <div className="flex items-center gap-2">
                <Progress value={85} className="w-16 h-2" />
                <span className="text-xs">85%</span>
              </div>
            </div>
            <div className="flex items-center justify-between">
              <span className="text-sm">Wednesday 2:00 PM</span>
              <div className="flex items-center gap-2">
                <Progress value={72} className="w-16 h-2" />
                <span className="text-xs">72%</span>
              </div>
            </div>
            <div className="flex items-center justify-between">
              <span className="text-sm">Friday 11:00 AM</span>
              <div className="flex items-center gap-2">
                <Progress value={68} className="w-16 h-2" />
                <span className="text-xs">68%</span>
              </div>
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  )
}

// Insights and Recommendations
function InsightsAndRecommendations({ 
  rules: _rules, 
  analytics: _analytics 
}: {
  rules: Array<{ priority: string; is_active: boolean }>
  analytics: Record<string, unknown>
}) {
  const insights = [
    {
      type: 'success',
      title: 'High Accuracy Achieved',
      description: 'Your rules are performing exceptionally well with 94.2% accuracy rate.',
      action: 'Consider expanding successful rule patterns to other areas.'
    },
    {
      type: 'warning',
      title: 'Potential Optimization',
      description: 'Some rules have higher false positive rates during peak hours.',
      action: 'Review time-based conditions for better accuracy.'
    },
    {
      type: 'info',
      title: 'Usage Pattern Detected',
      description: 'Most detections occur on Mondays and Wednesdays.',
      action: 'Consider rule priority adjustments for these days.'
    }
  ]

  return (
    <div className="space-y-6">
      <Card>
        <CardHeader>
          <CardTitle>AI-Powered Insights</CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          {insights.map((insight, index) => (
            <div key={index} className="border rounded-lg p-4 space-y-2">
              <div className="flex items-center gap-2">
                {insight.type === 'success' && <CheckCircle className="w-5 h-5 text-green-500" />}
                {insight.type === 'warning' && <AlertTriangle className="w-5 h-5 text-yellow-500" />}
                {insight.type === 'info' && <Activity className="w-5 h-5 text-blue-500" />}
                <h4 className="font-medium">{insight.title}</h4>
              </div>
              <p className="text-sm text-muted-foreground">{insight.description}</p>
              <p className="text-sm font-medium text-blue-600">{insight.action}</p>
            </div>
          ))}
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <CardTitle>Recommended Actions</CardTitle>
        </CardHeader>
        <CardContent className="space-y-3">
          <Button variant="outline" className="w-full justify-start">
            <Target className="w-4 h-4 mr-2" />
            Optimize rules for Monday peak activity
          </Button>
          <Button variant="outline" className="w-full justify-start">
            <Zap className="w-4 h-4 mr-2" />
            Create new rule based on top performer
          </Button>
          <Button variant="outline" className="w-full justify-start">
            <Filter className="w-4 h-4 mr-2" />
            Review false positive patterns
          </Button>
        </CardContent>
      </Card>
    </div>
  )
}