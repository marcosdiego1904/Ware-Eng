"use client"

import { Badge } from '@/components/ui/badge'
import { cn } from '@/lib/utils'

interface ConfidenceBadgeProps {
  confidence: number
  showPercentage?: boolean
  size?: 'sm' | 'md' | 'lg'
}

/**
 * Confidence Badge Component
 *
 * Visual indicator for column mapping confidence scores.
 * Color-coded based on confidence levels:
 * - Green (85-100%): High confidence - Auto-mappable
 * - Yellow (65-84%): Medium confidence - Requires review
 * - Orange (50-64%): Low confidence - Needs verification
 * - Red (<50%): Very low confidence - Manual mapping required
 */
export function ConfidenceBadge({
  confidence,
  showPercentage = true,
  size = 'sm'
}: ConfidenceBadgeProps) {
  // Convert confidence to percentage
  const percentage = Math.round(confidence * 100)

  // Determine confidence level and styling
  const getConfidenceLevel = () => {
    if (confidence >= 0.85) {
      return {
        label: 'High',
        bgColor: 'bg-green-100',
        textColor: 'text-green-700',
        borderColor: 'border-green-200',
        icon: '✓'
      }
    } else if (confidence >= 0.65) {
      return {
        label: 'Medium',
        bgColor: 'bg-yellow-100',
        textColor: 'text-yellow-700',
        borderColor: 'border-yellow-200',
        icon: '◐'
      }
    } else if (confidence >= 0.50) {
      return {
        label: 'Low',
        bgColor: 'bg-orange-100',
        textColor: 'text-orange-700',
        borderColor: 'border-orange-200',
        icon: '◔'
      }
    } else {
      return {
        label: 'Very Low',
        bgColor: 'bg-red-100',
        textColor: 'text-red-700',
        borderColor: 'border-red-200',
        icon: '✕'
      }
    }
  }

  const level = getConfidenceLevel()

  // Size variants
  const sizeClasses = {
    sm: 'text-xs px-2 py-0.5',
    md: 'text-sm px-3 py-1',
    lg: 'text-base px-4 py-1.5'
  }

  return (
    <Badge
      className={cn(
        level.bgColor,
        level.textColor,
        level.borderColor,
        sizeClasses[size],
        'border font-medium inline-flex items-center gap-1'
      )}
      variant="secondary"
    >
      <span className="font-bold">{level.icon}</span>
      {showPercentage && (
        <span>{percentage}% match</span>
      )}
      {!showPercentage && (
        <span>{level.label}</span>
      )}
    </Badge>
  )
}

interface ConfidenceIndicatorProps {
  confidence: number
  method?: string
  showDetails?: boolean
}

/**
 * Confidence Indicator with Method Badge
 *
 * Shows both confidence level and matching method used.
 */
export function ConfidenceIndicator({
  confidence,
  method,
  showDetails = true
}: ConfidenceIndicatorProps) {
  const getMethodLabel = () => {
    switch (method) {
      case 'exact':
        return { label: 'Exact', color: 'text-blue-600', bg: 'bg-blue-50' }
      case 'fuzzy':
        return { label: 'Fuzzy', color: 'text-purple-600', bg: 'bg-purple-50' }
      case 'semantic':
        return { label: 'Semantic', color: 'text-indigo-600', bg: 'bg-indigo-50' }
      default:
        return { label: 'Unknown', color: 'text-gray-600', bg: 'bg-gray-50' }
    }
  }

  const methodInfo = getMethodLabel()

  return (
    <div className="flex items-center gap-2">
      <ConfidenceBadge confidence={confidence} size="sm" />
      {showDetails && method && (
        <span className={cn(
          'text-xs px-2 py-0.5 rounded-full',
          methodInfo.bg,
          methodInfo.color
        )}>
          {methodInfo.label}
        </span>
      )}
    </div>
  )
}

interface ConfidenceBarProps {
  confidence: number
  height?: number
}

/**
 * Confidence Bar (Progress-style indicator)
 *
 * Visual progress bar showing confidence level.
 */
export function ConfidenceBar({ confidence, height = 4 }: ConfidenceBarProps) {
  const percentage = confidence * 100

  const getBarColor = () => {
    if (confidence >= 0.85) return 'bg-green-500'
    if (confidence >= 0.65) return 'bg-yellow-500'
    if (confidence >= 0.50) return 'bg-orange-500'
    return 'bg-red-500'
  }

  return (
    <div className="w-full bg-gray-200 rounded-full overflow-hidden" style={{ height: `${height}px` }}>
      <div
        className={cn('h-full transition-all duration-300', getBarColor())}
        style={{ width: `${percentage}%` }}
      />
    </div>
  )
}
