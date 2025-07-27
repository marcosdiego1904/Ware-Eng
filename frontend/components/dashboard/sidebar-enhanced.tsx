"use client"

import { useState, useEffect } from 'react'
import { useAuth } from '@/lib/auth-context'
import { useDashboardStore } from '@/lib/store-enhanced'
import { useToast } from '@/lib/store-enhanced'
import { cn } from '@/lib/utils'
import { 
  BarChart3, 
  FileText, 
  Upload, 
  Settings, 
  User, 
  LogOut,
  Package,
  Menu,
  X,
  ChevronLeft,
  Moon,
  Sun,
  Zap,
  Activity
} from 'lucide-react'
import { Button } from '@/components/ui/button'
import { Badge } from '@/components/ui/badge'

const navigationItems = [
  {
    id: 'overview' as const,
    label: 'Dashboard',
    icon: BarChart3,
    description: 'Overview and health metrics',
    shortcut: '⌘D'
  },
  {
    id: 'new-analysis' as const,
    label: 'New Analysis',
    icon: Upload,
    description: 'Upload files and start analysis',
    shortcut: '⌘N'
  },
  {
    id: 'reports' as const,
    label: 'Reports',
    icon: FileText,
    description: 'View and manage reports',
    shortcut: '⌘R'
  },
  {
    id: 'rules' as const,
    label: 'Rules',
    icon: Settings,
    description: 'Warehouse rules configuration',
    shortcut: '⌘S'
  },
]

export function EnhancedSidebar() {
  const { user, logout } = useAuth()
  const { 
    currentView, 
    setCurrentView, 
    sidebarCollapsed, 
    setSidebarCollapsed,
    theme,
    setTheme,
    reports,
    goBack,
    previousView
  } = useDashboardStore()
  const toast = useToast()
  const [isMobileMenuOpen, setIsMobileMenuOpen] = useState(false)

  // Close mobile menu when view changes
  useEffect(() => {
    setIsMobileMenuOpen(false)
  }, [currentView])

  // Handle keyboard shortcuts
  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      if (e.metaKey || e.ctrlKey) {
        switch (e.key.toLowerCase()) {
          case 'd':
            e.preventDefault()
            setCurrentView('overview')
            break
          case 'n':
            e.preventDefault()
            setCurrentView('new-analysis')
            break
          case 'r':
            e.preventDefault()
            setCurrentView('reports')
            break
          case 's':
            e.preventDefault()
            setCurrentView('rules')
            break
        }
      }
    }

    window.addEventListener('keydown', handleKeyDown)
    return () => window.removeEventListener('keydown', handleKeyDown)
  }, [setCurrentView])

  const handleLogout = () => {
    logout()
    toast.success('Signed out successfully', 'See you next time!')
  }

  const toggleTheme = () => {
    const newTheme = theme === 'light' ? 'dark' : 'light'
    setTheme(newTheme)
    toast.info(`Switched to ${newTheme} theme`, 'Theme preference saved')
  }

  const getActivityBadge = () => {
    const totalAnomalies = reports.reduce((sum, report) => sum + report.anomaly_count, 0)
    if (totalAnomalies > 50) return { count: totalAnomalies, variant: 'destructive' as const }
    if (totalAnomalies > 10) return { count: totalAnomalies, variant: 'secondary' as const }
    return null
  }

  const activityBadge = getActivityBadge()

  // Mobile overlay
  if (isMobileMenuOpen) {
    return (
      <>
        {/* Mobile backdrop */}
        <div 
          className="fixed inset-0 bg-black bg-opacity-50 z-40 lg:hidden"
          onClick={() => setIsMobileMenuOpen(false)}
        />
        
        {/* Mobile sidebar */}
        <div className="fixed inset-y-0 left-0 z-50 w-80 bg-slate-900 text-white transform transition-transform duration-300 ease-in-out lg:hidden">
          <SidebarContent 
            user={user}
            currentView={currentView}
            setCurrentView={setCurrentView}
            sidebarCollapsed={false}
            setSidebarCollapsed={setSidebarCollapsed}
            theme={theme}
            toggleTheme={toggleTheme}
            handleLogout={handleLogout}
            previousView={previousView}
            goBack={goBack}
            activityBadge={activityBadge}
            closeMobileMenu={() => setIsMobileMenuOpen(false)}
            isMobile={true}
          />
        </div>
      </>
    )
  }

  // Desktop sidebar
  return (
    <>
      {/* Mobile menu button */}
      <Button
        variant="ghost"
        size="sm"
        className="fixed top-4 left-4 z-30 lg:hidden bg-white shadow-md"
        onClick={() => setIsMobileMenuOpen(true)}
      >
        <Menu className="w-5 h-5" />
      </Button>

      {/* Desktop sidebar */}
      <div className={cn(
        "hidden lg:flex bg-slate-900 text-white flex-col h-full transition-all duration-300 ease-in-out",
        sidebarCollapsed ? "w-16" : "w-64"
      )}>
        <SidebarContent 
          user={user}
          currentView={currentView}
          setCurrentView={setCurrentView}
          sidebarCollapsed={sidebarCollapsed}
          setSidebarCollapsed={setSidebarCollapsed}
          theme={theme}
          toggleTheme={toggleTheme}
          handleLogout={handleLogout}
          previousView={previousView}
          goBack={goBack}
          activityBadge={activityBadge}
          isMobile={false}
        />
      </div>
    </>
  )
}

interface SidebarContentProps {
  user: { username?: string; name?: string; email?: string } | null
  currentView: string
  setCurrentView: (view: "rules" | "overview" | "new-analysis" | "reports" | "profile") => void
  sidebarCollapsed: boolean
  setSidebarCollapsed: (collapsed: boolean) => void
  theme: string
  toggleTheme: () => void
  handleLogout: () => void
  previousView: string | null
  goBack: () => void
  activityBadge: { count: number; variant: "destructive" | "secondary" } | null
  closeMobileMenu?: () => void
  isMobile: boolean
}

function SidebarContent({
  user,
  currentView,
  setCurrentView,
  sidebarCollapsed,
  setSidebarCollapsed,
  theme,
  toggleTheme,
  handleLogout,
  previousView,
  goBack,
  activityBadge,
  closeMobileMenu,
  isMobile
}: SidebarContentProps) {
  return (
    <>
      {/* Header */}
      <div className="p-6 border-b border-slate-800">
        <div className="flex items-center justify-between">
          {!sidebarCollapsed && (
            <div className="flex items-center gap-2">
              <div className="w-8 h-8 bg-gradient-to-br from-blue-400 to-blue-600 rounded-lg flex items-center justify-center shadow-lg">
                <Package className="w-5 h-5 text-white" />
              </div>
              <div className="flex flex-col">
                <span className="font-bold text-lg bg-gradient-to-r from-blue-400 to-purple-400 bg-clip-text text-transparent">
                  WareIntel
                </span>
                <span className="text-xs text-slate-400">Intelligence Dashboard</span>
              </div>
            </div>
          )}
          
          <div className="flex items-center gap-2">
            {previousView && !sidebarCollapsed && (
              <Button
                variant="ghost"
                size="sm"
                onClick={goBack}
                className="text-slate-400 hover:text-white p-1"
                title="Go back"
              >
                <ChevronLeft className="w-4 h-4" />
              </Button>
            )}
            
            {isMobile ? (
              <Button
                variant="ghost"
                size="sm"
                onClick={closeMobileMenu}
                className="text-slate-400 hover:text-white p-1"
              >
                <X className="w-4 h-4" />
              </Button>
            ) : (
              <Button
                variant="ghost"
                size="sm"
                onClick={() => setSidebarCollapsed(!sidebarCollapsed)}
                className="text-slate-400 hover:text-white p-1"
                title={sidebarCollapsed ? "Expand sidebar" : "Collapse sidebar"}
              >
                <Menu className="w-4 h-4" />
              </Button>
            )}
          </div>
        </div>
      </div>

      {/* Activity Status */}
      {!sidebarCollapsed && activityBadge && (
        <div className="px-6 py-3">
          <div className="flex items-center gap-2 p-2 bg-slate-800 rounded-lg">
            <Activity className="w-4 h-4 text-blue-400" />
            <span className="text-sm text-slate-300">System Activity</span>
            <Badge variant={activityBadge.variant} className="ml-auto">
              {activityBadge.count}
            </Badge>
          </div>
        </div>
      )}

      {/* Navigation */}
      <nav className="flex-1 px-4 py-2">
        <div className="space-y-1">
          {navigationItems.map((item) => {
            const isActive = currentView === item.id
            return (
              <button
                key={item.id}
                onClick={() => setCurrentView(item.id)}
                className={cn(
                  "flex items-center gap-3 px-3 py-3 rounded-xl w-full text-left transition-all duration-200 group relative",
                  isActive
                    ? "bg-gradient-to-r from-blue-600 to-purple-600 text-white shadow-lg transform scale-[1.02]"
                    : "text-slate-300 hover:bg-slate-800 hover:text-white hover:transform hover:scale-[1.01]"
                )}
                title={sidebarCollapsed ? item.label : undefined}
              >
                <item.icon className={cn(
                  "w-5 h-5 transition-transform duration-200",
                  isActive && "drop-shadow-sm"
                )} />
                
                {!sidebarCollapsed && (
                  <>
                    <div className="flex flex-col flex-1">
                      <div className="flex items-center justify-between">
                        <span className="font-medium">{item.label}</span>
                        <span className="text-xs opacity-50">{item.shortcut}</span>
                      </div>
                      <span className="text-xs opacity-70">{item.description}</span>
                    </div>
                    
                    {isActive && (
                      <div className="w-1 h-6 bg-white rounded-full opacity-80" />
                    )}
                  </>
                )}
                
                {/* Tooltip for collapsed state */}
                {sidebarCollapsed && (
                  <div className="absolute left-full ml-2 px-2 py-1 bg-slate-800 text-white text-sm rounded opacity-0 group-hover:opacity-100 transition-opacity duration-200 pointer-events-none whitespace-nowrap z-50">
                    {item.label}
                  </div>
                )}
              </button>
            )
          })}
        </div>
      </nav>

      {/* Settings & Theme Toggle */}
      {!sidebarCollapsed && (
        <div className="px-4 py-2 border-t border-slate-800">
          <Button
            variant="ghost"
            size="sm"
            onClick={toggleTheme}
            className="w-full justify-start gap-3 text-slate-300 hover:text-white hover:bg-slate-800 mb-2"
          >
            {theme === 'light' ? <Moon className="w-4 h-4" /> : <Sun className="w-4 h-4" />}
            {theme === 'light' ? 'Dark Mode' : 'Light Mode'}
          </Button>
        </div>
      )}

      {/* User Section */}
      <div className="p-4 border-t border-slate-800">
        {!sidebarCollapsed ? (
          <>
            <div className="flex items-center gap-3 mb-3">
              <div className="w-10 h-10 bg-gradient-to-br from-slate-600 to-slate-700 rounded-xl flex items-center justify-center shadow-lg">
                <User className="w-5 h-5 text-white" />
              </div>
              <div className="flex flex-col flex-1">
                <span className="text-sm font-semibold text-white">{user?.username}</span>
                <span className="text-xs text-slate-400">Warehouse Analyst</span>
              </div>
              <Zap className="w-4 h-4 text-yellow-400" />
            </div>
            
            <Button
              variant="ghost"
              size="sm"
              onClick={handleLogout}
              className="w-full justify-start gap-3 text-slate-300 hover:text-red-400 hover:bg-slate-800 transition-colors duration-200"
            >
              <LogOut className="w-4 h-4" />
              Sign Out
            </Button>
          </>
        ) : (
          <div className="flex flex-col gap-2">
            <Button
              variant="ghost"
              size="sm"
              onClick={toggleTheme}
              className="p-2 text-slate-300 hover:text-white hover:bg-slate-800"
              title={theme === 'light' ? 'Switch to dark mode' : 'Switch to light mode'}
            >
              {theme === 'light' ? <Moon className="w-4 h-4" /> : <Sun className="w-4 h-4" />}
            </Button>
            <Button
              variant="ghost"
              size="sm"
              onClick={handleLogout}
              className="p-2 text-slate-300 hover:text-red-400 hover:bg-slate-800"
              title="Sign out"
            >
              <LogOut className="w-4 h-4" />
            </Button>
          </div>
        )}
      </div>
    </>
  )
}