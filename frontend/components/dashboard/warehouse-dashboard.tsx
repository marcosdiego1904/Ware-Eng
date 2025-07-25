"use client"

import { useDashboardStore } from '@/lib/store'
import { Sidebar } from './sidebar'
import { DashboardHeader } from './header'
import { OverviewView } from './views/overview'
import { NewAnalysisView } from './views/new-analysis'
import { ReportsView } from './views/reports'
import { RulesView } from './views/rules'

export function WarehouseDashboard() {
  const { currentView } = useDashboardStore()

  const renderCurrentView = () => {
    switch (currentView) {
      case 'overview':
        return <OverviewView />
      case 'new-analysis':
        return <NewAnalysisView />
      case 'reports':
        return <ReportsView />
      case 'rules':
        return <RulesView />
      default:
        return <OverviewView />
    }
  }

  return (
    <div className="flex h-screen bg-gray-50 overflow-hidden">
      {/* Sidebar */}
      <Sidebar />
      
      {/* Main Content */}
      <div className="flex-1 flex flex-col overflow-hidden">
        {/* Header */}
        <DashboardHeader />
        
        {/* Content Area */}
        <main className="flex-1 overflow-auto">
          {renderCurrentView()}
        </main>
      </div>
    </div>
  )
}