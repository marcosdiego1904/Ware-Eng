"use client"

import { useDashboardStore } from '@/lib/store'
import { Sidebar } from './sidebar'
import { EnhancedOverviewView } from './views/overview-enhanced'
import { NewAnalysisView } from './views/new-analysis'
import { ReportsView } from './views/reports'
import { RulesView } from './views/rules'
import { WarehouseSettingsView } from './views/warehouse-settings'
import { ActionCenterView } from './views/action-center'
import { LocationIntelligenceView } from './views/location-intelligence'
import { RuleCenterView } from './views/rule-center'
import { AnalyticsView } from './views/analytics'

export function WarehouseDashboard() {
  const { currentView } = useDashboardStore()

  const renderCurrentView = () => {
    switch (currentView) {
      case 'overview':
        return <EnhancedOverviewView />
      case 'new-analysis':
        return <NewAnalysisView />
      case 'reports':
        return <ReportsView />
      case 'rule-center':
        return <RuleCenterView />
      case 'rules':
        return <RulesView />
      case 'warehouse-settings':
        return <WarehouseSettingsView />
      case 'action-center':
        return <ActionCenterView />
      case 'analytics':
        return <AnalyticsView />
      default:
        return <EnhancedOverviewView />
    }
  }

  return (
    <div className="flex h-screen bg-gray-50 overflow-hidden">
      {/* Sidebar */}
      <Sidebar />

      {/* Main Content */}
      <div className="flex-1 overflow-auto">
        {renderCurrentView()}
      </div>
    </div>
  )
}