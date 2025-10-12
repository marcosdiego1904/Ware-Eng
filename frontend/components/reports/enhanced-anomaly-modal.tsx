"use client"

import { useState } from 'react'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Badge } from '@/components/ui/badge'
import { Input } from '@/components/ui/input'
import { Dialog, DialogContent, DialogHeader, DialogTitle } from '@/components/ui/dialog'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs'
import { Progress } from '@/components/ui/progress'
import {
  AlertTriangle,
  CheckCircle2,
  Clock,
  Eye,
  MessageSquare,
  User,
  Calendar,
  Workflow,
  Target,
  Users,
  MapPin,
  DollarSign,
  ArrowRight,
  Zap,
  TrendingUp,
  FileText,
  Settings
} from 'lucide-react'
import { reportsApi, getPriorityColor, getStatusColor } from '@/lib/reports'

interface EnrichedAnomaly {
  id: number
  pallet_id: string
  location: string
  anomaly_type: string
  priority: string
  status: string
  details?: string
  history: Array<{
    old_status: string
    new_status: string
    comment: string
    user: string
    timestamp: string
  }>
  businessImpact: string
  resourceRequirements: string
  estimatedDuration: string
  dependencies: string[]
  operationalContext: string
  urgencyReason: string
}

interface EnhancedAnomalyModalProps {
  anomaly: EnrichedAnomaly | null
  isOpen: boolean
  onClose: () => void
  onStatusUpdate?: () => void
}

export function EnhancedAnomalyModal({ anomaly, isOpen, onClose, onStatusUpdate }: EnhancedAnomalyModalProps) {
  const [isUpdating, setIsUpdating] = useState(false)
  const [newStatus, setNewStatus] = useState<string>('')
  const [comment, setComment] = useState('')
  const [activeWorkflowStep, setActiveWorkflowStep] = useState(0)

  if (!anomaly) return null

  const handleStatusUpdate = async () => {
    if (!newStatus) return

    try {
      setIsUpdating(true)
      await reportsApi.updateAnomalyStatus(anomaly.id, newStatus, comment)

      // Update the anomaly in our local state
      anomaly.status = newStatus as any
      if (comment) {
        anomaly.history.push({
          old_status: anomaly.status,
          new_status: newStatus,
          comment,
          user: 'Current User',
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

  const generateWorkflowSteps = (anomaly: EnrichedAnomaly): Array<{title: string, description: string, completed: boolean}> => {
    const baseSteps = [
      { title: 'Issue Identified', description: 'Anomaly detected by system', completed: true },
      { title: 'Assessment', description: 'Evaluate business impact and resources', completed: anomaly.status !== 'New' },
      { title: 'Action Planning', description: 'Plan resolution approach', completed: anomaly.status === 'In Progress' || anomaly.status === 'Resolved' },
      { title: 'Resolution', description: 'Execute fix and verify', completed: anomaly.status === 'Resolved' }
    ]

    // Add specific steps based on anomaly type
    if (anomaly.anomaly_type === 'Storage Overcapacity') {
      baseSteps.splice(2, 0, {
        title: 'Locate Alternative Space',
        description: 'Find available locations for relocation',
        completed: anomaly.status === 'In Progress' || anomaly.status === 'Resolved'
      })
    }

    if (anomaly.anomaly_type === 'Stagnant Pallet' && anomaly.location.includes('RECV')) {
      baseSteps.splice(2, 0, {
        title: 'Coordinate with Receiving',
        description: 'Ensure receiving workflow not disrupted',
        completed: anomaly.status === 'In Progress' || anomaly.status === 'Resolved'
      })
    }

    return baseSteps
  }

  const workflowSteps = generateWorkflowSteps(anomaly)
  const currentStep = workflowSteps.findIndex(step => !step.completed)
  const progressPercentage = ((workflowSteps.filter(step => step.completed).length) / workflowSteps.length) * 100

  const getBusinessPriorityColor = (priority: string) => {
    switch (priority) {
      case 'VERY_HIGH': return 'from-rose-500 to-rose-600'
      case 'HIGH': return 'from-amber-500 to-amber-600'
      case 'MEDIUM': return 'from-blue-500 to-blue-600'
      case 'LOW': return 'from-slate-500 to-slate-600'
      default: return 'from-gray-500 to-gray-600'
    }
  }

  return (
    <Dialog open={isOpen} onOpenChange={onClose}>
      <DialogContent className="max-w-4xl max-h-[90vh] overflow-y-auto">
        <DialogHeader>
          <DialogTitle className="flex items-center gap-3">
            <div className={`flex h-10 w-10 items-center justify-center rounded-full bg-gradient-to-r ${getBusinessPriorityColor(anomaly.priority)} text-white`}>
              <Workflow className="w-5 h-5" />
            </div>
            <div>
              <div>{anomaly.anomaly_type}</div>
              <div className="text-sm font-normal text-gray-600">{anomaly.location} • Pallet {anomaly.pallet_id}</div>
            </div>
          </DialogTitle>
        </DialogHeader>

        <Tabs defaultValue="overview" className="space-y-6">
          <TabsList className="grid w-full grid-cols-4">
            <TabsTrigger value="overview" className="flex items-center gap-2">
              <TrendingUp className="w-4 h-4" />
              Business Overview
            </TabsTrigger>
            <TabsTrigger value="workflow" className="flex items-center gap-2">
              <Workflow className="w-4 h-4" />
              Resolution Workflow
            </TabsTrigger>
            <TabsTrigger value="technical" className="flex items-center gap-2">
              <Settings className="w-4 h-4" />
              Technical Details
            </TabsTrigger>
            <TabsTrigger value="history" className="flex items-center gap-2">
              <FileText className="w-4 h-4" />
              Activity History
            </TabsTrigger>
          </TabsList>

          {/* Business Overview Tab */}
          <TabsContent value="overview" className="space-y-6">
            {/* Business Impact Card */}
            <Card className="relative overflow-hidden bg-gradient-to-r from-blue-50 to-indigo-50/50 border border-blue-200/60">
              <div className="absolute inset-0 bg-gradient-to-r from-blue-500/4 to-transparent" />
              <CardHeader className="relative">
                <CardTitle className="flex items-center gap-3 text-blue-900">
                  <Target className="w-5 h-5" />
                  Business Impact Analysis
                </CardTitle>
              </CardHeader>
              <CardContent className="relative space-y-4">
                <div className="grid md:grid-cols-2 gap-6">
                  <div className="space-y-4">
                    <div>
                      <label className="text-sm font-medium text-blue-800">Primary Impact</label>
                      <p className="text-blue-700 mt-1">{anomaly.businessImpact}</p>
                    </div>
                    <div>
                      <label className="text-sm font-medium text-blue-800">Operational Context</label>
                      <p className="text-blue-700 mt-1">{anomaly.operationalContext}</p>
                    </div>
                    <div>
                      <label className="text-sm font-medium text-blue-800">Urgency Reason</label>
                      <p className="text-blue-700 mt-1">{anomaly.urgencyReason}</p>
                    </div>
                  </div>
                  <div className="space-y-4">
                    <div className="bg-white/60 rounded-lg p-4 border border-blue-200/30">
                      <div className="flex items-center gap-2 mb-3">
                        <Users className="w-5 h-5 text-blue-600" />
                        <span className="font-medium text-blue-900">Resource Requirements</span>
                      </div>
                      <p className="text-blue-700 text-sm">{anomaly.resourceRequirements}</p>
                    </div>
                    <div className="bg-white/60 rounded-lg p-4 border border-blue-200/30">
                      <div className="flex items-center gap-2 mb-3">
                        <Clock className="w-5 h-5 text-blue-600" />
                        <span className="font-medium text-blue-900">Estimated Duration</span>
                      </div>
                      <p className="text-blue-700 text-sm">{anomaly.estimatedDuration}</p>
                    </div>
                  </div>
                </div>

                {anomaly.dependencies.length > 0 && (
                  <div className="border-t border-blue-200/50 pt-4">
                    <label className="text-sm font-medium text-blue-800 mb-3 block">Dependencies & Prerequisites</label>
                    <div className="space-y-2">
                      {anomaly.dependencies.map((dep, index) => (
                        <div key={index} className="flex items-center gap-2 text-blue-700">
                          <ArrowRight className="w-4 h-4 text-blue-500" />
                          <span className="text-sm">{dep}</span>
                        </div>
                      ))}
                    </div>
                  </div>
                )}
              </CardContent>
            </Card>

            {/* Quick Actions */}
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-3">
                  <Zap className="w-5 h-5 text-amber-600" />
                  Quick Actions
                </CardTitle>
              </CardHeader>
              <CardContent>
                <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                  <Button
                    className="bg-gradient-to-r from-emerald-600 to-emerald-700 hover:from-emerald-700 hover:to-emerald-800 text-white h-12"
                    onClick={() => setNewStatus('In Progress')}
                  >
                    Start Resolution
                  </Button>
                  <Button
                    variant="outline"
                    className="h-12 border-blue-200 hover:bg-blue-50"
                    onClick={() => setNewStatus('Acknowledged')}
                  >
                    Acknowledge Issue
                  </Button>
                  <Button
                    variant="outline"
                    className="h-12 border-amber-200 hover:bg-amber-50"
                  >
                    Request Assistance
                  </Button>
                </div>
              </CardContent>
            </Card>
          </TabsContent>

          {/* Resolution Workflow Tab */}
          <TabsContent value="workflow" className="space-y-6">
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-3">
                  <Workflow className="w-5 h-5" />
                  Resolution Progress
                </CardTitle>
              </CardHeader>
              <CardContent className="space-y-6">
                {/* Progress Overview */}
                <div className="space-y-3">
                  <div className="flex justify-between text-sm">
                    <span className="font-medium">Overall Progress</span>
                    <span>{progressPercentage.toFixed(0)}% Complete</span>
                  </div>
                  <Progress value={progressPercentage} className="h-3" />
                </div>

                {/* Workflow Steps */}
                <div className="space-y-4">
                  {workflowSteps.map((step, index) => (
                    <div
                      key={index}
                      className={`flex items-start gap-4 p-4 rounded-lg border transition-all duration-200 ${
                        step.completed
                          ? 'bg-emerald-50 border-emerald-200'
                          : index === currentStep
                          ? 'bg-blue-50 border-blue-200 ring-1 ring-blue-200'
                          : 'bg-gray-50 border-gray-200'
                      }`}
                    >
                      <div className={`flex h-8 w-8 items-center justify-center rounded-full flex-shrink-0 ${
                        step.completed
                          ? 'bg-emerald-500 text-white'
                          : index === currentStep
                          ? 'bg-blue-500 text-white'
                          : 'bg-gray-300 text-gray-600'
                      }`}>
                        {step.completed ? (
                          <CheckCircle2 className="w-4 h-4" />
                        ) : index === currentStep ? (
                          <Clock className="w-4 h-4" />
                        ) : (
                          <span className="text-sm font-medium">{index + 1}</span>
                        )}
                      </div>
                      <div className="flex-1">
                        <h4 className={`font-medium ${
                          step.completed ? 'text-emerald-900' : index === currentStep ? 'text-blue-900' : 'text-gray-700'
                        }`}>
                          {step.title}
                        </h4>
                        <p className={`text-sm mt-1 ${
                          step.completed ? 'text-emerald-700' : index === currentStep ? 'text-blue-700' : 'text-gray-600'
                        }`}>
                          {step.description}
                        </p>
                      </div>
                      {index === currentStep && (
                        <Button size="sm" variant="outline" className="border-blue-200 hover:bg-blue-50">
                          Start Step
                        </Button>
                      )}
                    </div>
                  ))}
                </div>

                {/* Status Update Section */}
                <Card className="bg-slate-50 border-slate-200">
                  <CardHeader>
                    <CardTitle className="text-lg">Update Status</CardTitle>
                  </CardHeader>
                  <CardContent className="space-y-4">
                    <div>
                      <label className="text-sm font-medium">Current Status</label>
                      <div className="mt-1">
                        <Badge className={getStatusColor(anomaly.status)}>
                          {getStatusIcon(anomaly.status)}
                          <span className="ml-1">{anomaly.status}</span>
                        </Badge>
                      </div>
                    </div>

                    <div>
                      <label className="text-sm font-medium">New Status</label>
                      <select
                        value={newStatus}
                        onChange={(e) => setNewStatus(e.target.value)}
                        className="mt-1 w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                      >
                        <option value="">Select new status...</option>
                        <option value="New">New</option>
                        <option value="Acknowledged">Acknowledged</option>
                        <option value="In Progress">In Progress</option>
                        <option value="Resolved">Resolved</option>
                      </select>
                    </div>

                    <div>
                      <label className="text-sm font-medium">Progress Comment</label>
                      <Input
                        value={comment}
                        onChange={(e) => setComment(e.target.value)}
                        placeholder="Add details about progress or actions taken..."
                        className="mt-1"
                      />
                    </div>

                    <Button
                      onClick={handleStatusUpdate}
                      disabled={!newStatus || isUpdating}
                      className="w-full bg-gradient-to-r from-blue-600 to-blue-700 hover:from-blue-700 hover:to-blue-800"
                    >
                      {isUpdating ? 'Updating...' : 'Update Status'}
                    </Button>
                  </CardContent>
                </Card>
              </CardContent>
            </Card>
          </TabsContent>

          {/* Technical Details Tab */}
          <TabsContent value="technical" className="space-y-6">
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-3">
                  <Settings className="w-5 h-5" />
                  Technical Information
                </CardTitle>
              </CardHeader>
              <CardContent>
                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <label className="text-sm font-medium text-gray-500">Anomaly Type</label>
                    <p className="text-gray-900">{anomaly.anomaly_type}</p>
                  </div>
                  <div>
                    <label className="text-sm font-medium text-gray-500">Priority Level</label>
                    <Badge className={getPriorityColor(anomaly.priority)}>
                      {anomaly.priority}
                    </Badge>
                  </div>
                  <div>
                    <label className="text-sm font-medium text-gray-500">Location</label>
                    <p className="text-gray-900">{anomaly.location}</p>
                  </div>
                  <div>
                    <label className="text-sm font-medium text-gray-500">Pallet ID</label>
                    <p className="text-gray-900">{anomaly.pallet_id}</p>
                  </div>
                  <div>
                    <label className="text-sm font-medium text-gray-500">Anomaly ID</label>
                    <p className="text-gray-900">#{anomaly.id}</p>
                  </div>
                  <div>
                    <label className="text-sm font-medium text-gray-500">Current Status</label>
                    <Badge className={getStatusColor(anomaly.status)}>
                      {anomaly.status}
                    </Badge>
                  </div>
                </div>

                {anomaly.details && (
                  <div className="mt-6">
                    <label className="text-sm font-medium text-gray-500">Technical Details</label>
                    <p className="text-gray-900 bg-gray-50 p-3 rounded mt-1 font-mono text-sm">
                      {anomaly.details}
                    </p>
                  </div>
                )}
              </CardContent>
            </Card>
          </TabsContent>

          {/* Activity History Tab */}
          <TabsContent value="history" className="space-y-6">
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-3">
                  <FileText className="w-5 h-5" />
                  Activity History
                </CardTitle>
              </CardHeader>
              <CardContent>
                <div className="space-y-4">
                  {anomaly.history?.length > 0 ? (
                    <div className="space-y-3">
                      {anomaly.history.map((entry, index) => (
                        <Card key={index} className="bg-gray-50">
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
                      <p className="text-gray-600">No activity history available</p>
                      <p className="text-gray-500 text-sm mt-1">Status changes and comments will appear here</p>
                    </div>
                  )}
                </div>
              </CardContent>
            </Card>
          </TabsContent>
        </Tabs>
      </DialogContent>
    </Dialog>
  )
}