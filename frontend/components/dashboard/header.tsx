"use client"

import { useDashboardStore } from '@/lib/store'
import { Bell, RefreshCw } from 'lucide-react'
import { Button } from '@/components/ui/button'
import { Badge } from '@/components/ui/badge'
import { ThemeToggle } from '@/components/ui/theme-toggle'

const viewTitles = {
  'overview': 'Dashboard Overview',
  'new-analysis': 'New Analysis',
  'reports': 'Reports Management',
  'rules': 'Warehouse Rules',
  'warehouse-settings': 'Warehouse Settings',
  'profile': 'Profile Settings',
  'action-center': 'Action Center'
}

const viewDescriptions = {
  'overview': 'Quick access to key warehouse operations',
  'new-analysis': 'Upload inventory files and start anomaly detection',
  'reports': 'View, manage and track analysis reports',
  'rules': 'Configure warehouse rules and settings',
  'warehouse-settings': 'Manage warehouse configurations and locations',
  'profile': 'Manage your account settings',
  'action-center': 'Immediate problem resolution command center'
}

export function DashboardHeader() {
  const { currentView, isLoading } = useDashboardStore()

  return (
    <header className="bg-white border-b border-gray-200 px-6 py-3">
      <div className="flex items-center justify-end">
        <div className="flex items-center gap-4">
          {/* Status indicators */}
          <div className="flex items-center gap-2">
            {isLoading && (
              <Badge variant="secondary" className="gap-1">
                <RefreshCw className="w-3 h-3 animate-spin" />
                Processing
              </Badge>
            )}
          </div>

          {/* Theme toggle */}
          <div>
            <ThemeToggle />
          </div>

          {/* Notifications */}
          <Button variant="ghost" size="icon" className="relative hover:bg-orange-50 hover:text-orange-600">
            <Bell className="w-5 h-5" />
            <span className="absolute -top-1 -right-1 w-3 h-3 bg-red-500 rounded-full text-xs"></span>
          </Button>
        </div>
      </div>
    </header>
  )
}