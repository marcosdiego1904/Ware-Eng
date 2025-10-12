"use client"

import { useState } from 'react'
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle
} from '@/components/ui/dialog'
import { Button } from '@/components/ui/button'
import { Badge } from '@/components/ui/badge'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Input } from '@/components/ui/input'
import { Progress } from '@/components/ui/progress'
import {
  AlertTriangle,
  CheckCircle2,
  Clock,
  Wrench,
  MapPin,
  Package,
  Target
} from 'lucide-react'

interface AnomalyManagementModalProps {
  isOpen: boolean
  onClose: () => void
  onResolve?: (anomalyId: string) => void
  anomaly: {
    id: string
    anomaly_type: string
    location: string
    priority: string
    details: string
    detectedTime: string
  } | null
}

export function AnomalyManagementModal({ isOpen, onClose, onResolve, anomaly }: AnomalyManagementModalProps) {

  if (!anomaly) {
    return null
  }

  const getResolutionSteps = (anomalyType: string, location: string) => {
    return [
      {
        title: "1. Locate Pallet",
        description: `Verify pallet location in ${location}`,
        status: "completed",
        bgColor: "bg-green-50 border-green-200",
        iconColor: "text-green-600",
        icon: "check"
      },
      {
        title: "2. Assess Issue",
        description: "Determine specific action needed for this anomaly",
        status: "current",
        bgColor: "bg-blue-50 border-blue-200",
        iconColor: "text-blue-500",
        icon: "number"
      },
      {
        title: "3. Execute Resolution",
        description: "Take appropriate corrective action",
        status: "pending",
        bgColor: "bg-gray-50 border-gray-200",
        iconColor: "text-gray-400",
        icon: "number"
      }
    ]
  }


  const getPriorityColor = (priority: string) => {
    switch (priority) {
      case 'VERY_HIGH': return 'bg-red-500'
      case 'HIGH': return 'bg-orange-500'
      case 'MEDIUM': return 'bg-yellow-500'
      default: return 'bg-blue-500'
    }
  }

  const getPriorityLabel = (priority: string) => {
    switch (priority) {
      case 'VERY_HIGH': return 'URGENT'
      case 'HIGH': return 'HIGH'
      case 'MEDIUM': return 'MEDIUM'
      default: return 'LOW'
    }
  }

  return (
    <Dialog open={isOpen} onOpenChange={onClose}>
      <DialogContent className="max-w-2xl max-h-[90vh] overflow-hidden flex flex-col">
        {/* Header: Anomaly Context & Status */}
        <DialogHeader className="border-b pb-4">
          <div className="flex items-start justify-between">
            <div className="space-y-2">
              <DialogTitle className="flex items-center gap-3 text-xl">
                <AlertTriangle className="w-6 h-6 text-red-500" />
                {anomaly.anomaly_type} - {anomaly.location}
              </DialogTitle>
              <div className="flex items-center gap-4 text-sm text-gray-600">
                <span className="flex items-center gap-1">
                  <Package className="w-4 h-4" />
                  Pallet ID: {anomaly.details.split(' ')[0] || 'N/A'}
                </span>
                <span className="flex items-center gap-1">
                  <MapPin className="w-4 h-4" />
                  Location: {anomaly.location}
                </span>
                <span className="flex items-center gap-1">
                  <Clock className="w-4 h-4" />
                  Detected: {anomaly.detectedTime || '2 hours ago'}
                </span>
              </div>
            </div>
            <Badge className={`${getPriorityColor(anomaly.priority)} text-white font-medium px-3 py-1 mr-8`}>
              {getPriorityLabel(anomaly.priority)}
            </Badge>
          </div>
        </DialogHeader>

        {/* Main Content Area - Action Plan */}
        <div className="flex-1 overflow-y-auto px-6 py-6">
          {/* Action Steps */}
          <div className="space-y-5">
            <div className="flex items-center gap-2">
              <Target className="w-6 h-6 text-slate-600" />
              <h3 className="font-semibold text-xl text-slate-800">Resolution Steps</h3>
            </div>

            <div className="space-y-4">
              {getResolutionSteps(anomaly.anomaly_type, anomaly.location).map((step, index) => (
                <div key={index} className={`flex items-center gap-4 p-4 rounded-lg border ${step.bgColor}`}>
                  {step.icon === "check" ? (
                    <CheckCircle2 className={`w-6 h-6 ${step.iconColor} flex-shrink-0`} />
                  ) : (
                    <div className={`w-6 h-6 rounded-full ${step.iconColor.replace('text-', 'bg-')} text-white flex items-center justify-center text-sm font-bold flex-shrink-0`}>
                      {index + 1}
                    </div>
                  )}
                  <div className="flex-1 min-w-0">
                    <p className="font-semibold text-base text-slate-800">{step.title}</p>
                    <p className="text-sm text-slate-600 mt-1">{step.description}</p>
                  </div>
                </div>
              ))}
            </div>

            {/* Progress Bar */}
            <div className="bg-slate-50 p-4 rounded-lg space-y-3 border border-slate-200">
              <div className="flex justify-between items-center">
                <span className="font-semibold text-sm text-slate-700">Progress</span>
                <span className="text-sm font-medium text-slate-800">
                  {Math.round((getResolutionSteps(anomaly.anomaly_type, anomaly.location).filter(step => step.status === 'completed').length / getResolutionSteps(anomaly.anomaly_type, anomaly.location).length) * 100)}% Complete
                </span>
              </div>
              <Progress
                value={Math.round((getResolutionSteps(anomaly.anomaly_type, anomaly.location).filter(step => step.status === 'completed').length / getResolutionSteps(anomaly.anomaly_type, anomaly.location).length) * 100)}
                className="h-2"
              />
              <div className="flex justify-between text-xs text-slate-500">
                <span>
                  {getResolutionSteps(anomaly.anomaly_type, anomaly.location).filter(step => step.status === 'completed').length} of {getResolutionSteps(anomaly.anomaly_type, anomaly.location).length} steps completed
                </span>
                <span>
                  {getResolutionSteps(anomaly.anomaly_type, anomaly.location).filter(step => step.status === 'pending').length} remaining
                </span>
              </div>
            </div>
          </div>
        </div>

        {/* Footer - Primary Action */}
        <div className="border-t border-slate-200 bg-gradient-to-r from-slate-50 to-blue-50 px-6 py-6">
          <Button
            onClick={() => {
              if (onResolve) {
                onResolve(anomaly.id)
              }
              onClose()
            }}
            className="w-full flex items-center justify-center gap-3 bg-slate-900 hover:bg-slate-800 text-white font-semibold py-4 px-6 rounded-lg shadow-lg hover:shadow-xl transition-all duration-200 transform hover:scale-[1.01]"
            size="lg"
          >
            <Wrench className="w-5 h-5" />
            Resolve Now
          </Button>
        </div>
      </DialogContent>
    </Dialog>
  )
}