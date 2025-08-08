"use client"

import { useDashboardStore } from '@/lib/store'
import { Search, Bell, RefreshCw } from 'lucide-react'
import { Input } from '@/components/ui/input'
import { Button } from '@/components/ui/button'
import { Badge } from '@/components/ui/badge'

const viewTitles = {
  'overview': 'Dashboard Overview',
  'new-analysis': 'New Analysis',
  'reports': 'Reports Management',
  'rules': 'Warehouse Rules',
  'warehouse-settings': 'Warehouse Settings',
  'profile': 'Profile Settings'
}

const viewDescriptions = {
  'overview': 'Monitor warehouse health and recent activity',
  'new-analysis': 'Upload inventory files and start anomaly detection',
  'reports': 'View, manage and track analysis reports',
  'rules': 'Configure warehouse rules and settings',
  'warehouse-settings': 'Manage warehouse configurations and locations',
  'profile': 'Manage your account settings'
}

export function DashboardHeader() {
  const { currentView, isLoading } = useDashboardStore()

  return (
    <header className="bg-white border-b border-gray-200 px-6 py-4">
      <div className="flex items-center justify-between">
        <div className="flex flex-col">
          <h1 className="text-2xl font-semibold text-gray-900">
            {viewTitles[currentView]}
          </h1>
          <p className="text-sm text-gray-600 mt-1">
            {viewDescriptions[currentView]}
          </p>
        </div>

        <div className="flex items-center gap-4">
          {/* Search */}
          <div className="relative">
            <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 w-4 h-4" />
            <Input 
              placeholder="Search reports, anomalies..." 
              className="pl-10 w-64" 
            />
          </div>

          {/* Status indicators */}
          <div className="flex items-center gap-2">
            {isLoading && (
              <Badge variant="secondary" className="gap-1">
                <RefreshCw className="w-3 h-3 animate-spin" />
                Processing
              </Badge>
            )}
          </div>

          {/* Notifications */}
          <Button variant="ghost" size="icon" className="relative">
            <Bell className="w-5 h-5" />
            <span className="absolute -top-1 -right-1 w-3 h-3 bg-red-500 rounded-full text-xs"></span>
          </Button>
        </div>
      </div>
    </header>
  )
}