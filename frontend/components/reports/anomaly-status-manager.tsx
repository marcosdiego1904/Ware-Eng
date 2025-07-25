"use client"

import { useState } from 'react'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Badge } from '@/components/ui/badge'
import { Input } from '@/components/ui/input'
import { Dialog, DialogContent, DialogHeader, DialogTitle } from '@/components/ui/dialog'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs'
import { AlertTriangle, CheckCircle2, Clock, Eye, MessageSquare, User, Calendar } from 'lucide-react'
import { Anomaly, LocationSummary, reportsApi, getStatusColor, getPriorityColor } from '@/lib/reports'

interface AnomalyStatusManagerProps {
  reportId: number
  locations: LocationSummary[]
  onStatusUpdate?: () => void
}

export function AnomalyStatusManager({ reportId, locations, onStatusUpdate }: AnomalyStatusManagerProps) {
  const [selectedAnomaly, setSelectedAnomaly] = useState<Anomaly | null>(null)
  const [isUpdating, setIsUpdating] = useState(false)
  const [newStatus, setNewStatus] = useState<string>('')
  const [comment, setComment] = useState('')
  const [statusFilter, setStatusFilter] = useState<string>('all')
  const [priorityFilter, setPriorityFilter] = useState<string>('all')

  const allAnomalies = locations.flatMap(location => 
    location.anomalies.map(anomaly => ({ ...anomaly, location: location.name }))
  )

  const filteredAnomalies = allAnomalies.filter(anomaly => {
    const statusMatch = statusFilter === 'all' || anomaly.status === statusFilter
    const priorityMatch = priorityFilter === 'all' || anomaly.priority === priorityFilter
    return statusMatch && priorityMatch
  })

  const handleStatusUpdate = async () => {
    if (!selectedAnomaly || !newStatus) return

    try {
      setIsUpdating(true)
      await reportsApi.updateAnomalyStatus(selectedAnomaly.id, newStatus, comment)
      
      // Update the anomaly in our local state
      selectedAnomaly.status = newStatus as any
      if (comment) {
        selectedAnomaly.history.push({
          old_status: selectedAnomaly.status,
          new_status: newStatus,
          comment,
          user: 'Current User', // This should come from auth context
          timestamp: new Date().toISOString()
        })
      }
      
      setComment('')
      setNewStatus('')
      onStatusUpdate?.()
    } catch (error) {
      console.error('Failed to update anomaly status:', error)
    } finally {
      setIsUpdating(false)
    }
  }

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'New':
        return <AlertTriangle className="w-4 h-4 text-blue-600" />
      case 'Acknowledged':
        return <Eye className="w-4 h-4 text-yellow-600" />
      case 'In Progress':
        return <Clock className="w-4 h-4 text-orange-600" />
      case 'Resolved':
        return <CheckCircle2 className="w-4 h-4 text-green-600" />
      default:
        return <AlertTriangle className="w-4 h-4 text-gray-600" />
    }
  }

  const statusCounts = {
    New: allAnomalies.filter(a => a.status === 'New').length,
    Acknowledged: allAnomalies.filter(a => a.status === 'Acknowledged').length,
    'In Progress': allAnomalies.filter(a => a.status === 'In Progress').length,
    Resolved: allAnomalies.filter(a => a.status === 'Resolved').length,
  }

  return (
    <div className="space-y-6">
      {/* Status Overview */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        {Object.entries(statusCounts).map(([status, count]) => (
          <Card key={status} className="text-center">
            <CardContent className="p-4">
              <div className="flex items-center justify-center mb-2">
                {getStatusIcon(status)}
              </div>
              <p className="text-2xl font-bold">{count}</p>
              <p className="text-sm text-gray-600">{status}</p>
            </CardContent>
          </Card>
        ))}
      </div>

      {/* Filters */}
      <Card>
        <CardHeader>
          <CardTitle>Filter Anomalies</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="flex gap-4">
            <div>
              <label className="text-sm font-medium">Status:</label>
              <select 
                value={statusFilter} 
                onChange={(e) => setStatusFilter(e.target.value)}
                className="ml-2 px-3 py-1 border rounded-md text-sm"
              >
                <option value="all">All Statuses</option>
                <option value="New">New</option>
                <option value="Acknowledged">Acknowledged</option>
                <option value="In Progress">In Progress</option>
                <option value="Resolved">Resolved</option>
              </select>
            </div>
            <div>
              <label className="text-sm font-medium">Priority:</label>
              <select 
                value={priorityFilter} 
                onChange={(e) => setPriorityFilter(e.target.value)}
                className="ml-2 px-3 py-1 border rounded-md text-sm"
              >
                <option value="all">All Priorities</option>
                <option value="VERY HIGH">Very High</option>
                <option value="HIGH">High</option>
                <option value="MEDIUM">Medium</option>
                <option value="LOW">Low</option>
              </select>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Anomalies List */}
      <div className="space-y-4">
        <div className="flex justify-between items-center">
          <h3 className="text-lg font-semibold">
            Anomalies ({filteredAnomalies.length})
          </h3>
        </div>
        
        <div className="grid gap-4">
          {filteredAnomalies.map((anomaly) => (
            <Card key={anomaly.id} className="hover:shadow-md transition-shadow">
              <CardContent className="p-6">
                <div className="flex items-start justify-between">
                  <div className="flex-1 space-y-2">
                    <div className="flex items-center gap-3">
                      <Badge className={getPriorityColor(anomaly.priority)}>
                        {anomaly.priority}
                      </Badge>
                      <Badge className={getStatusColor(anomaly.status)}>
                        {getStatusIcon(anomaly.status)}
                        <span className="ml-1">{anomaly.status}</span>
                      </Badge>
                    </div>
                    
                    <h4 className="font-semibold text-lg">{anomaly.anomaly_type}</h4>
                    <p className="text-gray-600">{anomaly.location} - Pallet {anomaly.pallet_id}</p>
                    
                    {anomaly.details && (
                      <p className="text-sm text-gray-500 bg-gray-50 p-2 rounded">
                        {anomaly.details}
                      </p>
                    )}
                  </div>
                  
                  <Button
                    variant="outline"
                    size="sm"
                    onClick={() => setSelectedAnomaly(anomaly)}
                  >
                    Manage
                  </Button>
                </div>
                
                {/* Quick status indicators */}
                <div className="mt-4 pt-4 border-t">
                  <div className="flex items-center gap-4 text-sm text-gray-500">
                    <span>ID: {anomaly.id}</span>
                    <span>History: {anomaly.history?.length || 0} entries</span>
                    {anomaly.history?.length > 0 && (
                      <span>Last updated: {new Date(anomaly.history[anomaly.history.length - 1].timestamp).toLocaleDateString()}</span>
                    )}
                  </div>
                </div>
              </CardContent>
            </Card>
          ))}
        </div>
        
        {filteredAnomalies.length === 0 && (
          <Card>
            <CardContent className="text-center py-12">
              <AlertTriangle className="w-12 h-12 text-gray-400 mx-auto mb-4" />
              <h3 className="text-lg font-medium text-gray-900 mb-2">No anomalies found</h3>
              <p className="text-gray-600">
                No anomalies match the current filters.
              </p>
            </CardContent>
          </Card>
        )}
      </div>

      {/* Anomaly Detail Modal */}
      <Dialog open={!!selectedAnomaly} onOpenChange={() => setSelectedAnomaly(null)}>
        <DialogContent className="max-w-2xl max-h-[80vh] overflow-y-auto">
          <DialogHeader>
            <DialogTitle className="flex items-center gap-2">
              <AlertTriangle className="w-5 h-5" />
              Manage Anomaly #{selectedAnomaly?.id}
            </DialogTitle>
          </DialogHeader>
          
          {selectedAnomaly && (
            <Tabs defaultValue="details" className="space-y-4">
              <TabsList className="grid w-full grid-cols-3">
                <TabsTrigger value="details">Details</TabsTrigger>
                <TabsTrigger value="status">Update Status</TabsTrigger>
                <TabsTrigger value="history">History</TabsTrigger>
              </TabsList>
              
              <TabsContent value="details" className="space-y-4">
                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <label className="text-sm font-medium text-gray-500">Type</label>
                    <p className="text-gray-900">{selectedAnomaly.anomaly_type}</p>
                  </div>
                  <div>
                    <label className="text-sm font-medium text-gray-500">Priority</label>
                    <Badge className={getPriorityColor(selectedAnomaly.priority)}>
                      {selectedAnomaly.priority}
                    </Badge>
                  </div>
                  <div>
                    <label className="text-sm font-medium text-gray-500">Location</label>
                    <p className="text-gray-900">{selectedAnomaly.location}</p>
                  </div>
                  <div>
                    <label className="text-sm font-medium text-gray-500">Pallet ID</label>
                    <p className="text-gray-900">{selectedAnomaly.pallet_id}</p>
                  </div>
                </div>
                
                {selectedAnomaly.details && (
                  <div>
                    <label className="text-sm font-medium text-gray-500">Details</label>
                    <p className="text-gray-900 bg-gray-50 p-3 rounded mt-1">
                      {selectedAnomaly.details}
                    </p>
                  </div>
                )}
              </TabsContent>
              
              <TabsContent value="status" className="space-y-4">
                <div className="space-y-4">
                  <div>
                    <label className="text-sm font-medium">Current Status</label>
                    <div className="mt-1">
                      <Badge className={getStatusColor(selectedAnomaly.status)}>
                        {getStatusIcon(selectedAnomaly.status)}
                        <span className="ml-1">{selectedAnomaly.status}</span>
                      </Badge>
                    </div>
                  </div>
                  
                  <div>
                    <label className="text-sm font-medium">New Status</label>
                    <select 
                      value={newStatus} 
                      onChange={(e) => setNewStatus(e.target.value)}
                      className="mt-1 w-full px-3 py-2 border rounded-md"
                    >
                      <option value="">Select new status...</option>
                      <option value="New">New</option>
                      <option value="Acknowledged">Acknowledged</option>
                      <option value="In Progress">In Progress</option>
                      <option value="Resolved">Resolved</option>
                    </select>
                  </div>
                  
                  <div>
                    <label className="text-sm font-medium">Comment (Optional)</label>
                    <Input
                      value={comment}
                      onChange={(e) => setComment(e.target.value)}
                      placeholder="Add a comment about this status change..."
                      className="mt-1"
                    />
                  </div>
                  
                  <Button 
                    onClick={handleStatusUpdate}
                    disabled={!newStatus || isUpdating}
                    className="w-full"
                  >
                    {isUpdating ? 'Updating...' : 'Update Status'}
                  </Button>
                </div>
              </TabsContent>
              
              <TabsContent value="history" className="space-y-4">
                <div className="space-y-3">
                  <h4 className="font-semibold">Status History</h4>
                  {selectedAnomaly.history?.length > 0 ? (
                    <div className="space-y-3">
                      {selectedAnomaly.history.map((entry, index) => (
                        <Card key={index}>
                          <CardContent className="p-4">
                            <div className="flex items-start gap-3">
                              <div className="flex-shrink-0">
                                {getStatusIcon(entry.new_status)}
                              </div>
                              <div className="flex-1">
                                <div className="flex items-center gap-2 mb-1">
                                  <span className="font-medium">{entry.old_status} → {entry.new_status}</span>
                                  <Badge variant="outline" className="text-xs">
                                    <User className="w-3 h-3 mr-1" />
                                    {entry.user}
                                  </Badge>
                                </div>
                                {entry.comment && (
                                  <div className="flex items-start gap-2 mb-2">
                                    <MessageSquare className="w-4 h-4 text-gray-400 mt-0.5 flex-shrink-0" />
                                    <p className="text-sm text-gray-600">{entry.comment}</p>
                                  </div>
                                )}
                                <div className="flex items-center gap-1 text-xs text-gray-500">
                                  <Calendar className="w-3 h-3" />
                                  {new Date(entry.timestamp).toLocaleString()}
                                </div>
                              </div>
                            </div>
                          </CardContent>
                        </Card>
                      ))}
                    </div>
                  ) : (
                    <div className="text-center py-8">
                      <MessageSquare className="w-12 h-12 text-gray-400 mx-auto mb-4" />
                      <p className="text-gray-600">No status history available</p>
                    </div>
                  )}
                </div>
              </TabsContent>
            </Tabs>
          )}
        </DialogContent>
      </Dialog>
    </div>
  )
}