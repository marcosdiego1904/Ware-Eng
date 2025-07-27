"use client"

import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { ReportDetails } from '@/lib/reports'
import { FileText, Clock, AlertTriangle, CheckCircle2 } from 'lucide-react'

interface RecentActivityFeedProps {
  reports: ReportDetails[]
}

export function RecentActivityFeed({ reports }: RecentActivityFeedProps) {
  // Generate activity items from reports
  const activityItems = reports.flatMap(report => {
    const items = []
    
    // Add report creation activity
    items.push({
      id: `report-${report.reportId}`,
      timestamp: new Date().toISOString(), // In real app, this would come from report data
      type: 'report_created',
      title: 'New Analysis Report Generated',
      description: report.reportName,
      details: `${report.locations.reduce((sum, loc) => sum + loc.anomaly_count, 0)} anomalies detected`,
      icon: FileText,
      color: 'text-blue-600',
      bgColor: 'bg-blue-50'
    })
    
    // Add high-priority anomaly activities
    report.locations.forEach(location => {
      location.anomalies
        .filter(anomaly => anomaly.priority === 'VERY HIGH' || anomaly.priority === 'HIGH')
        .slice(0, 2) // Limit to prevent too many items
        .forEach(anomaly => {
          items.push({
            id: `anomaly-${anomaly.id}`,
            timestamp: new Date(Date.now() - Math.random() * 7 * 24 * 60 * 60 * 1000).toISOString(),
            type: 'high_priority_anomaly',
            title: `${anomaly.priority} Priority Alert`,
            description: anomaly.anomaly_type,
            details: `Location: ${location.name} - Pallet: ${anomaly.pallet_id}`,
            icon: AlertTriangle,
            color: anomaly.priority === 'VERY HIGH' ? 'text-red-600' : 'text-orange-600',
            bgColor: anomaly.priority === 'VERY HIGH' ? 'bg-red-50' : 'bg-orange-50'
          })
        })
    })
    
    // Add status change activities for resolved items
    report.locations.forEach(location => {
      location.anomalies
        .filter(anomaly => anomaly.status === 'Resolved')
        .slice(0, 1) // Limit resolved items
        .forEach(anomaly => {
          items.push({
            id: `resolved-${anomaly.id}`,
            timestamp: new Date(Date.now() - Math.random() * 3 * 24 * 60 * 60 * 1000).toISOString(),
            type: 'anomaly_resolved',
            title: 'Anomaly Resolved',
            description: anomaly.anomaly_type,
            details: `Location: ${location.name}`,
            icon: CheckCircle2,
            color: 'text-green-600',
            bgColor: 'bg-green-50'
          })
        })
    })
    
    return items
  })
  
  // Sort by timestamp and limit items
  const sortedActivity = activityItems
    .sort((a, b) => new Date(b.timestamp).getTime() - new Date(a.timestamp).getTime())
    .slice(0, 10)

  const getTimeAgo = (timestamp: string) => {
    const now = new Date()
    const time = new Date(timestamp)
    const diffInHours = Math.floor((now.getTime() - time.getTime()) / (1000 * 60 * 60))
    
    if (diffInHours < 1) return 'Just now'
    if (diffInHours < 24) return `${diffInHours}h ago`
    const diffInDays = Math.floor(diffInHours / 24)
    if (diffInDays < 7) return `${diffInDays}d ago`
    return time.toLocaleDateString()
  }

  return (
    <div className="space-y-6">
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Clock className="w-5 h-5" />
            Recent Activity
          </CardTitle>
          <p className="text-sm text-gray-600">
            Latest system events and anomaly updates
          </p>
        </CardHeader>
        <CardContent>
          {sortedActivity.length > 0 ? (
            <div className="space-y-4">
              {sortedActivity.map((item) => {
                const IconComponent = item.icon
                return (
                  <div key={item.id} className="flex items-start gap-4 p-4 border rounded-lg hover:shadow-sm transition-shadow">
                    <div className={`p-2 rounded-full ${item.bgColor} flex-shrink-0`}>
                      <IconComponent className={`w-4 h-4 ${item.color}`} />
                    </div>
                    <div className="flex-1 min-w-0">
                      <div className="flex items-start justify-between">
                        <div className="flex-1">
                          <p className="font-medium text-gray-900">{item.title}</p>
                          <p className="text-sm text-gray-600 mt-1">{item.description}</p>
                          {item.details && (
                            <p className="text-xs text-gray-500 mt-1">{item.details}</p>
                          )}
                        </div>
                        <div className="text-right flex-shrink-0 ml-4">
                          <p className="text-xs text-gray-500">{getTimeAgo(item.timestamp)}</p>
                          {item.type === 'high_priority_anomaly' && (
                            <Badge 
                              variant="outline" 
                              className={`mt-1 text-xs ${
                                item.color === 'text-red-600' ? 'border-red-200 text-red-600' : 'border-orange-200 text-orange-600'
                              }`}
                            >
                              Urgent
                            </Badge>
                          )}
                        </div>
                      </div>
                    </div>
                  </div>
                )
              })}
            </div>
          ) : (
            <div className="text-center py-12">
              <Clock className="w-12 h-12 text-gray-400 mx-auto mb-4" />
              <p className="text-gray-600">No recent activity</p>
              <p className="text-sm text-gray-500 mt-2">
                Activity will appear here as you generate reports and manage anomalies
              </p>
            </div>
          )}
        </CardContent>
      </Card>

      {/* Activity Summary */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <Card>
          <CardContent className="p-4 text-center">
            <FileText className="w-8 h-8 text-blue-600 mx-auto mb-2" />
            <div className="text-2xl font-bold">{reports.length}</div>
            <div className="text-sm text-gray-600">Recent Reports</div>
          </CardContent>
        </Card>
        
        <Card>
          <CardContent className="p-4 text-center">
            <AlertTriangle className="w-8 h-8 text-orange-600 mx-auto mb-2" />
            <div className="text-2xl font-bold">
              {sortedActivity.filter(item => item.type === 'high_priority_anomaly').length}
            </div>
            <div className="text-sm text-gray-600">Priority Alerts</div>
          </CardContent>
        </Card>
        
        <Card>
          <CardContent className="p-4 text-center">
            <CheckCircle2 className="w-8 h-8 text-green-600 mx-auto mb-2" />
            <div className="text-2xl font-bold">
              {sortedActivity.filter(item => item.type === 'anomaly_resolved').length}
            </div>
            <div className="text-sm text-gray-600">Resolved Issues</div>
          </CardContent>
        </Card>
      </div>
    </div>
  )
}