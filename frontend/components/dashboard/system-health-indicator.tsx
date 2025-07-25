"use client"

import { CheckCircle2, AlertTriangle, XCircle, Shield } from 'lucide-react'

interface SystemHealthIndicatorProps {
  status: 'excellent' | 'good' | 'warning' | 'critical'
  size?: 'sm' | 'md' | 'lg'
}

export function SystemHealthIndicator({ status, size = 'sm' }: SystemHealthIndicatorProps) {
  const getHealthConfig = (status: SystemHealthIndicatorProps['status']) => {
    switch (status) {
      case 'excellent':
        return {
          icon: CheckCircle2,
          color: 'text-green-600',
          bgColor: 'bg-green-100',
          borderColor: 'border-green-200',
          label: 'Excellent',
          description: 'All systems operating optimally'
        }
      case 'good':
        return {
          icon: Shield,
          color: 'text-blue-600',
          bgColor: 'bg-blue-100',
          borderColor: 'border-blue-200',
          label: 'Good',
          description: 'Systems operating normally'
        }
      case 'warning':
        return {
          icon: AlertTriangle,
          color: 'text-yellow-600',
          bgColor: 'bg-yellow-100',
          borderColor: 'border-yellow-200',
          label: 'Warning',
          description: 'Some issues detected'
        }
      case 'critical':
        return {
          icon: XCircle,
          color: 'text-red-600',
          bgColor: 'bg-red-100',
          borderColor: 'border-red-200',
          label: 'Critical',
          description: 'Immediate attention required'
        }
    }
  }

  const config = getHealthConfig(status)
  const IconComponent = config.icon
  
  const sizeClasses = {
    sm: 'w-4 h-4',
    md: 'w-5 h-5',
    lg: 'w-6 h-6'
  }

  return (
    <div className="flex items-center gap-2">
      <div className={`p-1 rounded-full ${config.bgColor} ${config.borderColor} border`}>
        <IconComponent className={`${sizeClasses[size]} ${config.color}`} />
      </div>
      {size !== 'sm' && (
        <div>
          <span className={`font-medium ${config.color}`}>{config.label}</span>
          {size === 'lg' && (
            <p className="text-sm text-gray-600">{config.description}</p>
          )}
        </div>
      )}
    </div>
  )
}