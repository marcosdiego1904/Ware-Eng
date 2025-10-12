'use client'

import * as React from "react"
import { cn } from "@/lib/utils"
import { SmartLandingHub } from "./smart-landing-hub"
import { QuickStatusBar, EnhancedQuickStatusBar } from "./quick-status-bar"
import { ActionHub, ActionDetailView } from "./action-hub"
import { AnalyticsDashboard } from "./analytics-dashboard"
import { ProgressTracker } from "./progress-tracker"

// Types for navigation state
type ViewType = 'hub' | 'action' | 'analytics' | 'progress' | 'upload' | 'action-detail'
type StatusType = 'critical' | 'medium' | 'resolved'

interface NavigationState {
  currentView: ViewType
  selectedCategory?: string
  previousView?: ViewType
}

interface WarehouseIntelligenceDemoProps {
  className?: string
  showStatusBar?: boolean
}

export function WarehouseIntelligenceDemo({
  className,
  showStatusBar = true
}: WarehouseIntelligenceDemoProps) {
  const [navigation, setNavigation] = React.useState<NavigationState>({
    currentView: 'hub'
  })

  // Navigation handlers
  const navigateTo = (view: ViewType, category?: string) => {
    setNavigation(prev => ({
      currentView: view,
      selectedCategory: category,
      previousView: prev.currentView
    }))
  }

  const navigateBack = () => {
    setNavigation(prev => ({
      currentView: prev.previousView || 'hub',
      selectedCategory: undefined,
      previousView: 'hub'
    }))
  }

  const handleStatusClick = (type: StatusType) => {
    // Navigate to Action Hub with appropriate filter
    navigateTo('action')
  }

  const handleCategoryClick = (category: string) => {
    navigateTo('action-detail', category)
  }

  const handleUploadComplete = () => {
    // After upload, navigate directly to Action Hub
    navigateTo('action')
  }

  // Render the appropriate interface based on current view
  const renderCurrentView = () => {
    switch (navigation.currentView) {
      case 'hub':
        return (
          <SmartLandingHub
            onNavigate={(destination) => {
              if (destination === 'upload') {
                // Simulate upload complete and redirect to action
                handleUploadComplete()
              } else {
                navigateTo(destination)
              }
            }}
          />
        )

      case 'action':
        return (
          <ActionHub
            onCategoryClick={handleCategoryClick}
            onBackToHub={() => navigateTo('hub')}
          />
        )

      case 'action-detail':
        return (
          <ActionDetailView
            category={navigation.selectedCategory || 'unknown'}
            onBack={() => navigateTo('action')}
          />
        )

      case 'analytics':
        return (
          <AnalyticsDashboard
            onBackToHub={() => navigateTo('hub')}
          />
        )

      case 'progress':
        return (
          <ProgressTracker
            onBackToHub={() => navigateTo('hub')}
            onContinueWorking={() => navigateTo('action')}
          />
        )

      case 'upload':
        // Simulate upload process and redirect
        React.useEffect(() => {
          const timer = setTimeout(() => {
            handleUploadComplete()
          }, 2000)
          return () => clearTimeout(timer)
        }, [])

        return (
          <div className="max-w-4xl mx-auto p-6 text-center">
            <div className="space-y-4">
              <h1 className="text-3xl font-bold">Processing Upload...</h1>
              <p className="text-muted-foreground">Analyzing inventory data and detecting anomalies</p>
              <div className="w-full bg-gray-200 rounded-full h-2">
                <div className="bg-blue-600 h-2 rounded-full animate-pulse" style={{ width: '70%' }}></div>
              </div>
              <p className="text-sm text-muted-foreground">Redirecting to Action Hub...</p>
            </div>
          </div>
        )

      default:
        return <SmartLandingHub onNavigate={(dest) => navigateTo(dest)} />
    }
  }

  return (
    <div className={cn("min-h-screen bg-background", className)}>
      {/* Persistent Quick Status Bar - Only show on non-hub views */}
      {showStatusBar && navigation.currentView !== 'hub' && (
        <EnhancedQuickStatusBar
          onStatusClick={handleStatusClick}
          showProgress={navigation.currentView !== ('hub' as ViewType)}
          totalProcessed={700}
          processingSpeed="1.01s"
        />
      )}

      {/* Main Content Area */}
      <main className="container mx-auto">
        {renderCurrentView()}
      </main>

      {/* Demo Controls (for demonstration purposes) */}
      <div className="fixed bottom-4 right-4 z-50">
        <div className="bg-black/80 text-white text-xs p-3 rounded-lg backdrop-blur">
          <div className="font-semibold mb-1">Demo Controls</div>
          <div>Current: {navigation.currentView}</div>
          {navigation.selectedCategory && (
            <div>Category: {navigation.selectedCategory}</div>
          )}
          <div className="flex gap-2 mt-2">
            <button
              onClick={() => navigateTo('hub')}
              className="px-2 py-1 bg-white/20 rounded text-xs hover:bg-white/30"
            >
              Hub
            </button>
            <button
              onClick={() => navigateTo('action')}
              className="px-2 py-1 bg-white/20 rounded text-xs hover:bg-white/30"
            >
              Action
            </button>
            <button
              onClick={() => navigateTo('analytics')}
              className="px-2 py-1 bg-white/20 rounded text-xs hover:bg-white/30"
            >
              Analytics
            </button>
            <button
              onClick={() => navigateTo('progress')}
              className="px-2 py-1 bg-white/20 rounded text-xs hover:bg-white/30"
            >
              Progress
            </button>
          </div>
        </div>
      </div>
    </div>
  )
}

// Export individual components for use in other contexts
export {
  SmartLandingHub,
  QuickStatusBar,
  EnhancedQuickStatusBar,
  ActionHub,
  ActionDetailView,
  AnalyticsDashboard,
  ProgressTracker
}