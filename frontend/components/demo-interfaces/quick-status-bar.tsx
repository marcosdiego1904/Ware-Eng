'use client'

import * as React from "react"
import { Badge } from "@/components/ui/badge"
import { cn } from "@/lib/utils"

// Mock data for demonstration
const mockStatusData = {
  critical: 38,
  medium: 49,
  resolved: 12
}

interface QuickStatusBarProps {
  className?: string
  onStatusClick?: (type: 'critical' | 'medium' | 'resolved') => void
}

export function QuickStatusBar({ className, onStatusClick }: QuickStatusBarProps) {
  return (
    <div className={cn(
      "sticky top-0 z-50 bg-background/95 backdrop-blur supports-[backdrop-filter]:bg-background/60 border-b",
      className
    )}>
      <div className="container mx-auto px-4 py-2">
        <div className="flex items-center justify-center gap-6 text-sm">

          {/* Critical Status */}
          <button
            onClick={() => onStatusClick?.('critical')}
            className="flex items-center gap-2 hover:bg-red-50 dark:hover:bg-red-900/20 px-3 py-1.5 rounded-md transition-colors group"
          >
            <div className="w-3 h-3 bg-red-500 rounded-full group-hover:scale-110 transition-transform"></div>
            <Badge variant="destructive" className="font-mono">
              {mockStatusData.critical}
            </Badge>
            <span className="text-muted-foreground group-hover:text-red-600 dark:group-hover:text-red-400 transition-colors">
              Critical
            </span>
          </button>

          {/* Divider */}
          <div className="w-px h-6 bg-border"></div>

          {/* Medium Status */}
          <button
            onClick={() => onStatusClick?.('medium')}
            className="flex items-center gap-2 hover:bg-yellow-50 dark:hover:bg-yellow-900/20 px-3 py-1.5 rounded-md transition-colors group"
          >
            <div className="w-3 h-3 bg-yellow-500 rounded-full group-hover:scale-110 transition-transform"></div>
            <Badge variant="secondary" className="font-mono bg-yellow-100 text-yellow-700 dark:bg-yellow-900/30 dark:text-yellow-300">
              {mockStatusData.medium}
            </Badge>
            <span className="text-muted-foreground group-hover:text-yellow-600 dark:group-hover:text-yellow-400 transition-colors">
              Medium
            </span>
          </button>

          {/* Divider */}
          <div className="w-px h-6 bg-border"></div>

          {/* Resolved Status */}
          <button
            onClick={() => onStatusClick?.('resolved')}
            className="flex items-center gap-2 hover:bg-green-50 dark:hover:bg-green-900/20 px-3 py-1.5 rounded-md transition-colors group"
          >
            <div className="w-3 h-3 bg-green-500 rounded-full group-hover:scale-110 transition-transform"></div>
            <Badge variant="secondary" className="font-mono bg-green-100 text-green-700 dark:bg-green-900/30 dark:text-green-300">
              {mockStatusData.resolved}
            </Badge>
            <span className="text-muted-foreground group-hover:text-green-600 dark:group-hover:text-green-400 transition-colors">
              Resolved Today
            </span>
          </button>

          {/* Quick Hint */}
          <div className="hidden md:flex items-center gap-2 text-xs text-muted-foreground ml-4">
            <span>Click any status to jump to that list</span>
            <span className="text-xs bg-muted px-1.5 py-0.5 rounded">💡</span>
          </div>
        </div>
      </div>
    </div>
  )
}

// Enhanced version with progress indicators
interface EnhancedQuickStatusBarProps extends QuickStatusBarProps {
  showProgress?: boolean
  totalProcessed?: number
  processingSpeed?: string
}

export function EnhancedQuickStatusBar({
  className,
  onStatusClick,
  showProgress = false,
  totalProcessed = 0,
  processingSpeed
}: EnhancedQuickStatusBarProps) {
  return (
    <div className={cn(
      "sticky top-0 z-50 bg-background/95 backdrop-blur supports-[backdrop-filter]:bg-background/60 border-b",
      className
    )}>
      <div className="container mx-auto px-4 py-2">
        <div className="flex items-center justify-between">

          {/* Status Items (Left) */}
          <div className="flex items-center gap-6 text-sm">

            {/* Critical Status */}
            <button
              onClick={() => onStatusClick?.('critical')}
              className="flex items-center gap-2 hover:bg-red-50 dark:hover:bg-red-900/20 px-3 py-1.5 rounded-md transition-colors group"
            >
              <div className="w-3 h-3 bg-red-500 rounded-full group-hover:scale-110 transition-transform"></div>
              <Badge variant="destructive" className="font-mono">
                {mockStatusData.critical}
              </Badge>
              <span className="text-muted-foreground group-hover:text-red-600 dark:group-hover:text-red-400 transition-colors">
                Critical
              </span>
            </button>

            {/* Medium Status */}
            <button
              onClick={() => onStatusClick?.('medium')}
              className="flex items-center gap-2 hover:bg-yellow-50 dark:hover:bg-yellow-900/20 px-3 py-1.5 rounded-md transition-colors group"
            >
              <div className="w-3 h-3 bg-yellow-500 rounded-full group-hover:scale-110 transition-transform"></div>
              <Badge variant="secondary" className="font-mono bg-yellow-100 text-yellow-700 dark:bg-yellow-900/30 dark:text-yellow-300">
                {mockStatusData.medium}
              </Badge>
              <span className="text-muted-foreground group-hover:text-yellow-600 dark:group-hover:text-yellow-400 transition-colors">
                Medium
              </span>
            </button>

            {/* Resolved Status */}
            <button
              onClick={() => onStatusClick?.('resolved')}
              className="flex items-center gap-2 hover:bg-green-50 dark:hover:bg-green-900/20 px-3 py-1.5 rounded-md transition-colors group"
            >
              <div className="w-3 h-3 bg-green-500 rounded-full group-hover:scale-110 transition-transform"></div>
              <Badge variant="secondary" className="font-mono bg-green-100 text-green-700 dark:bg-green-900/30 dark:text-green-300">
                {mockStatusData.resolved}
              </Badge>
              <span className="text-muted-foreground group-hover:text-green-600 dark:group-hover:text-green-400 transition-colors">
                Resolved Today
              </span>
            </button>
          </div>

          {/* Progress Info (Right) */}
          {showProgress && (
            <div className="hidden md:flex items-center gap-4 text-xs text-muted-foreground">
              {totalProcessed > 0 && (
                <div className="flex items-center gap-2">
                  <span>Processed:</span>
                  <Badge variant="outline" className="font-mono">{totalProcessed}</Badge>
                </div>
              )}
              {processingSpeed && (
                <div className="flex items-center gap-2">
                  <span>Speed:</span>
                  <Badge variant="outline" className="font-mono">{processingSpeed}</Badge>
                </div>
              )}
            </div>
          )}
        </div>
      </div>
    </div>
  )
}