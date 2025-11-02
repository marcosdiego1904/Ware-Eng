"use client"

import React, { useState } from 'react'
import Image from 'next/image'
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
  Building2,
  Shield,
  ChevronLeft,
  ChevronRight,
  TrendingUp
} from 'lucide-react'
import { Button } from '@/components/ui/button'

const navigationItems = [
  {
    id: 'overview' as const,
    label: 'Dashboard',
    icon: BarChart3,
    description: 'Overview and health metrics',
    adminOnly: false
  },
  {
    id: 'new-analysis' as const,
    label: 'New Analysis',
    icon: Upload,
    description: 'Upload files and start analysis',
    adminOnly: false
  },
  {
    id: 'reports' as const,
    label: 'Reports',
    icon: FileText,
    description: 'View and manage reports',
    adminOnly: false
  },
  {
    id: 'rule-center' as const,
    label: 'Rule Center',
    icon: Shield,
    description: '7 rules protecting your inventory',
    adminOnly: false
  },
  {
    id: 'rules' as const,
    label: 'Rules',
    icon: Settings,
    description: 'Warehouse rules configuration',
    adminOnly: false
  },
  {
    id: 'warehouse-settings' as const,
    label: 'Warehouse Settings',
    icon: Building2,
    description: 'Location management & setup',
    adminOnly: false
  },
  {
    id: 'analytics' as const,
    label: 'Analytics',
    icon: TrendingUp,
    description: 'Pilot program metrics & ROI',
    adminOnly: true
  },
]

export function Sidebar() {
  const { user, logout } = useAuth()
  const { currentView, setCurrentView } = useDashboardStore()
  const [isCollapsed, setIsCollapsed] = useState(true)

  return (
    <div className={cn(
      "bg-white flex flex-col h-full border-r border-gray-200 transition-all duration-300",
      isCollapsed ? "w-20" : "w-64"
    )}>
      {/* Header */}
      <div className={cn(
        "bg-white relative",
        isCollapsed ? "p-4 pb-6" : "p-6 pb-8"
      )}>
        <div className="flex items-center justify-center">
          {isCollapsed ? (
            <Image
              src="/mobilelogo.png"
              alt="RackHawk Icon"
              width={40}
              height={40}
              priority
              className="object-contain"
            />
          ) : (
            <Image
              src="/logo.png"
              alt="RackHawk Logo"
              width={220}
              height={80}
              priority
              className="object-contain"
            />
          )}
        </div>

        {/* Toggle Button */}
        <button
          onClick={() => setIsCollapsed(!isCollapsed)}
          className={cn(
            "absolute -right-3 top-8 w-6 h-6 bg-white border-2 border-gray-200 rounded-full flex items-center justify-center hover:bg-[#FFF4F0] hover:border-[#F08A5D] transition-colors duration-200",
            "shadow-sm"
          )}
          aria-label={isCollapsed ? "Expand sidebar" : "Collapse sidebar"}
        >
          {isCollapsed ? (
            <ChevronRight className="w-3 h-3 text-gray-600" />
          ) : (
            <ChevronLeft className="w-3 h-3 text-gray-600" />
          )}
        </button>
      </div>

      {/* Navigation */}
      <nav className={cn("flex-1", isCollapsed ? "px-2" : "px-4")}>
        <div className="space-y-1">
          {navigationItems
            .filter((item) => !item.adminOnly || user?.is_admin)
            .map((item) => (
              <button
                key={item.id}
                onClick={() => setCurrentView(item.id)}
                title={isCollapsed ? item.label : undefined}
                className={cn(
                  "group flex items-center rounded-lg w-full text-left transition-all duration-200",
                  isCollapsed ? "gap-0 py-3 justify-center" : "gap-3 py-3",
                  currentView === item.id
                    ? isCollapsed
                      ? "bg-[#FFF4F0] text-[#F08A5D]"
                      : "bg-[#FFF4F0] text-[#F08A5D] pl-2 border-l-4 border-[#F08A5D] font-semibold shadow-sm"
                    : isCollapsed
                      ? "text-gray-600 hover:bg-[#FFF4F0]/40 hover:text-[#F08A5D]"
                      : "text-gray-600 hover:bg-[#FFF4F0]/40 hover:text-[#F08A5D] pl-3",
                  item.id === 'rules' && "hidden"
                )}
              >
                <item.icon className={cn(
                  "transition-colors duration-200",
                  isCollapsed ? "w-6 h-6" : "w-5 h-5",
                  currentView === item.id
                    ? "text-[#F08A5D]"
                    : "text-gray-400 group-hover:text-[#F08A5D]"
                )} />
                {!isCollapsed && (
                  <div className="flex flex-col">
                    <span className="font-medium">{item.label}</span>
                    <span className={cn(
                      "text-xs transition-colors duration-200",
                      currentView === item.id ? "text-[#F08A5D]/70" : "text-gray-500 group-hover:text-gray-600"
                    )}>{item.description}</span>
                  </div>
                )}
              </button>
            ))}
        </div>
      </nav>

      {/* User Section */}
      <div className={cn(
        "mt-auto border-t border-gray-200",
        isCollapsed ? "p-2" : "p-4"
      )}>
        {isCollapsed ? (
          /* Collapsed User Section - Icon Only */
          <div className="flex flex-col items-center gap-2">
            <button
              title={user?.username}
              className="w-10 h-10 bg-[#FFF4F0] rounded-full flex items-center justify-center hover:bg-[#F08A5D]/20 transition-colors"
            >
              <User className="w-5 h-5 text-[#F08A5D]" />
            </button>
            <button
              onClick={logout}
              title="Sign Out"
              className="w-10 h-10 rounded-lg flex items-center justify-center text-gray-600 hover:text-[#F08A5D] hover:bg-[#FFF4F0] transition-all duration-200"
            >
              <LogOut className="w-5 h-5" />
            </button>
          </div>
        ) : (
          /* Expanded User Section */
          <>
            <div className="flex items-center justify-between mb-3">
              <div className="flex items-center gap-3">
                <div className="w-8 h-8 bg-[#FFF4F0] rounded-full flex items-center justify-center">
                  <User className="w-4 h-4 text-[#F08A5D]" />
                </div>
                <div className="flex flex-col">
                  <span className="text-sm font-medium text-[#F08A5D]">{user?.username}</span>
                  <span className="text-xs text-gray-500">Warehouse Analyst</span>
                </div>
              </div>
            </div>

            <Button
              variant="ghost"
              size="sm"
              onClick={logout}
              className="w-full justify-start gap-2 text-gray-600 hover:text-[#F08A5D] hover:bg-[#FFF4F0] transition-all duration-200"
            >
              <LogOut className="w-4 h-4" />
              Sign Out
            </Button>
          </>
        )}
      </div>
    </div>
  )
}