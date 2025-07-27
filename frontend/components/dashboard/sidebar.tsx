"use client"

import React from 'react'
import { useAuth } from '@/lib/auth-context'
import { useDashboardStore } from '@/lib/store'
import { cn } from '@/lib/utils'
import { 
  BarChart3, 
  FileText, 
  Upload, 
  Settings, 
  User, 
  LogOut,
  Package
} from 'lucide-react'
import { Button } from '@/components/ui/button'

const navigationItems = [
  {
    id: 'overview' as const,
    label: 'Dashboard',
    icon: BarChart3,
    description: 'Overview and health metrics'
  },
  {
    id: 'new-analysis' as const,
    label: 'New Analysis',
    icon: Upload,
    description: 'Upload files and start analysis'
  },
  {
    id: 'reports' as const,
    label: 'Reports',
    icon: FileText,
    description: 'View and manage reports'
  },
  {
    id: 'rules' as const,
    label: 'Rules',
    icon: Settings,
    description: 'Warehouse rules configuration'
  },
]

export function Sidebar() {
  const { user, logout } = useAuth()
  const { currentView, setCurrentView } = useDashboardStore()

  return (
    <div className="w-64 bg-slate-900 text-white flex flex-col h-full">
      {/* Header */}
      <div className="p-6">
        <div className="flex items-center gap-2">
          <div className="w-8 h-8 bg-white rounded flex items-center justify-center">
            <Package className="w-5 h-5 text-slate-900" />
          </div>
          <div className="flex flex-col">
            <span className="font-semibold text-lg">WareIntel</span>
            <span className="text-xs text-slate-400">Warehouse Intelligence</span>
          </div>
        </div>
      </div>

      {/* Navigation */}
      <nav className="flex-1 px-4">
        <div className="space-y-1">
          {navigationItems.map((item) => (
            <button
              key={item.id}
              onClick={() => setCurrentView(item.id)}
              className={cn(
                "flex items-center gap-3 px-3 py-3 rounded-lg w-full text-left transition-colors",
                currentView === item.id
                  ? "bg-slate-800 text-white"
                  : "text-slate-300 hover:bg-slate-800 hover:text-white"
              )}
            >
              <item.icon className="w-5 h-5" />
              <div className="flex flex-col">
                <span className="font-medium">{item.label}</span>
                <span className="text-xs text-slate-400">{item.description}</span>
              </div>
            </button>
          ))}
        </div>
      </nav>

      {/* User Section */}
      <div className="p-4 mt-auto border-t border-slate-800">
        <div className="flex items-center justify-between mb-3">
          <div className="flex items-center gap-3">
            <div className="w-8 h-8 bg-slate-700 rounded-full flex items-center justify-center">
              <User className="w-4 h-4" />
            </div>
            <div className="flex flex-col">
              <span className="text-sm font-medium">{user?.username}</span>
              <span className="text-xs text-slate-400">Warehouse Analyst</span>
            </div>
          </div>
        </div>
        
        <Button
          variant="ghost"
          size="sm"
          onClick={logout}
          className="w-full justify-start gap-2 text-slate-300 hover:text-white hover:bg-slate-800"
        >
          <LogOut className="w-4 h-4" />
          Sign Out
        </Button>
      </div>
    </div>
  )
}