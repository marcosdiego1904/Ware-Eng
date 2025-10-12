"use client"

import { useState, useEffect } from "react"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Badge } from "@/components/ui/badge"
import { Checkbox } from "@/components/ui/checkbox"
import { Input } from "@/components/ui/input"
import {
  AlertTriangle,
  Clock,
  MapPin,
  DollarSign,
  Printer,
  CheckCircle2,
  Filter,
  ArrowLeft,
  Timer,
  RefreshCw,
} from "lucide-react"
import { cn } from "@/lib/utils"
import { useDashboardStore } from '@/lib/store'
import { actionCenterApi, ActionCenterData, EnrichedActionAnomaly } from '@/lib/action-center-api'
import { AnomalyManagementModal } from '@/components/reports/anomaly-management-modal'
import { ConfirmationModal } from '@/components/ui/confirmation-modal'

export function ActionCenterView() {
  const { setCurrentView, actionCenterPreselectedCategory, setActionCenterPreselectedCategory } = useDashboardStore()
  const [selectedCategory, setSelectedCategory] = useState<string | null>(null)
  const [selectedItems, setSelectedItems] = useState<string[]>([])
  const [searchQuery, setSearchQuery] = useState("")
  const [showUntriggeredRules, setShowUntriggeredRules] = useState(false)
  const [highlightedCategory, setHighlightedCategory] = useState<string | null>(null)

  // Real data state
  const [actionData, setActionData] = useState<ActionCenterData | null>(null)
  const [isLoading, setIsLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [lastRefresh, setLastRefresh] = useState<Date>(new Date())

  // Resolution modal state (matching reports overview)
  const [isManageModalOpen, setIsManageModalOpen] = useState(false)
  const [managingAnomaly, setManagingAnomaly] = useState<EnrichedActionAnomaly | null>(null)

  // Confirmation modal state
  const [confirmationModal, setConfirmationModal] = useState({
    open: false,
    title: '',
    description: '',
    confirmText: 'Confirm',
    onConfirm: () => {},
    variant: 'default' as 'default' | 'destructive' | 'warning'
  })

  const handleCategorySelect = (categoryId: string) => {
    setSelectedCategory(categoryId)
    setSelectedItems([])
  }

  const handleItemSelect = (itemId: string) => {
    setSelectedItems((prev) => (prev.includes(itemId) ? prev.filter((id) => id !== itemId) : [...prev, itemId]))
  }

  const handleSelectAll = () => {
    if (!actionData || !selectedCategory) return

    const category = actionData.categories.find(cat => cat.id === selectedCategory)
    if (category) {
      setSelectedItems(category.anomalies.map((item) => item.id.toString()))
    }
  }

  const handleClearSelection = () => {
    setSelectedItems([])
  }

  // Handle resolution (matching reports overview exactly)
  const handleMarkResolved = (anomalyId: string) => {
    // Mark item as resolved and refresh data
    console.log('Marking anomaly as resolved:', anomalyId)
    loadActionData() // Refresh to reflect changes
  }

  // Handle opening resolution modal (matching reports overview exactly)
  const handleOpenResolutionModal = (anomaly: EnrichedActionAnomaly) => {
    setManagingAnomaly(anomaly)
    setIsManageModalOpen(true)
  }

  // Show confirmation modal helper
  const showConfirmation = (config: typeof confirmationModal) => {
    setConfirmationModal({ ...config, open: true })
  }

  // Handle global resolution
  const handleResolveAll = async () => {
    if (!actionData) return

    showConfirmation({
      open: false,
      title: 'Resolve All Anomalies',
      description: `Are you sure you want to mark all ${getVisibleActiveItems()} anomalies as resolved? This action cannot be undone.`,
      confirmText: 'Mark All Resolved',
      variant: 'destructive',
      onConfirm: async () => {
        try {
          setIsLoading(true)
          setConfirmationModal(prev => ({ ...prev, open: false }))
          const result = await actionCenterApi.resolveAllAnomalies()

          if (result.success) {
            // Refresh data to show updated counts
            await loadActionData()
            // Show success in a nice way - could add a toast later
          }
        } catch (error) {
          console.error('Failed to resolve all anomalies:', error)
          alert('Failed to resolve anomalies. Please try again.')
        } finally {
          setIsLoading(false)
        }
      }
    })
  }

  // Handle category resolution
  const handleResolveCategory = async (category: any) => {
    showConfirmation({
      open: false,
      title: `Resolve ${category.title}`,
      description: `Are you sure you want to mark all ${category.count} ${category.title} anomalies as resolved? This action cannot be undone.`,
      confirmText: 'Mark as Resolved',
      variant: 'warning',
      onConfirm: async () => {
        try {
          setIsLoading(true)
          setConfirmationModal(prev => ({ ...prev, open: false }))

          // Need to map category to actual anomaly type from backend
          const categoryTypeMap: Record<string, string> = {
            'forgotten-pallets': 'Stagnant Pallet',
            'overcapacity': 'Storage Overcapacity',
            'aisle-stuck': 'Location-Specific Stagnant',
            'invalid-locations': 'Invalid Location',
            'scanner-errors': 'Duplicate Scan',
          }

          const anomalyType = categoryTypeMap[category.id]
          if (!anomalyType) {
            alert('Error: Unknown category type')
            return
          }

          const result = await actionCenterApi.resolveCategoryAnomalies(anomalyType)

          if (result.success) {
            // Refresh data to show updated counts
            await loadActionData()
          }
        } catch (error) {
          console.error('Failed to resolve category:', error)
          alert('Failed to resolve category. Please try again.')
        } finally {
          setIsLoading(false)
        }
      }
    })
  }

  // Handle bulk selection resolution
  const handleMarkSelectedResolved = async () => {
    if (selectedItems.length === 0) return

    showConfirmation({
      open: false,
      title: 'Resolve Selected Anomalies',
      description: `Are you sure you want to mark ${selectedItems.length} selected anomalies as resolved? This action cannot be undone.`,
      confirmText: 'Mark as Resolved',
      variant: 'default',
      onConfirm: async () => {
        try {
          setIsLoading(true)
          setConfirmationModal(prev => ({ ...prev, open: false }))
          const result = await actionCenterApi.resolveBulkAnomalies(selectedItems)

          if (result.success) {
            // Clear selection
            setSelectedItems([])
            // Refresh data to show updated counts
            await loadActionData()
          }
        } catch (error) {
          console.error('Failed to resolve selected anomalies:', error)
          alert('Failed to resolve selected anomalies. Please try again.')
        } finally {
          setIsLoading(false)
        }
      }
    })
  }

  // Handle single anomaly resolution
  const handleMarkSingleResolved = async (anomalyId: string) => {
    showConfirmation({
      open: false,
      title: 'Resolve Anomaly',
      description: 'Are you sure you want to mark this anomaly as resolved? This action cannot be undone.',
      confirmText: 'Mark as Resolved',
      variant: 'default' as const,
      onConfirm: async () => {
        try {
          setIsLoading(true)
          const result = await actionCenterApi.resolveSingleAnomaly(anomalyId)

          if (result.success) {
            // Refresh data to show updated counts
            await loadActionData()
            // Remove from selection if it was selected
            setSelectedItems(prev => prev.filter(id => id !== anomalyId))
            // Could add a toast notification here instead of alert
            console.log('Anomaly marked as resolved successfully!')
          } else {
            console.error(`Error: ${result.message}`)
            // Could add a toast notification here instead of alert
          }
        } catch (error) {
          console.error('Failed to resolve anomaly:', error)
          // Could add a toast notification here instead of alert
        } finally {
          setIsLoading(false)
        }
      }
    })
  }

  // Load action center data
  const loadActionData = async () => {
    try {
      setIsLoading(true)
      setError(null)
      const data = await actionCenterApi.getActionCenterData()
      setActionData(data)
      setLastRefresh(new Date())
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to load action data')
      console.error('Failed to load action center data:', err)
    } finally {
      setIsLoading(false)
    }
  }

  // Auto-refresh every 5 minutes
  useEffect(() => {
    loadActionData()

    const refreshInterval = setInterval(loadActionData, 5 * 60 * 1000) // 5 minutes
    return () => clearInterval(refreshInterval)
  }, [])

  // Handle pre-selected category from navigation
  useEffect(() => {
    if (actionCenterPreselectedCategory && actionData && !isLoading) {
      // Check if the category exists and is triggered
      const category = actionData.categories.find(cat => cat.id === actionCenterPreselectedCategory)
      if (category && category.isTriggered) {
        // Add highlight effect
        setHighlightedCategory(actionCenterPreselectedCategory)

        // Small delay for the transition effect to be visible
        setTimeout(() => {
          setSelectedCategory(actionCenterPreselectedCategory)

          // Remove highlight after animation completes
          setTimeout(() => {
            setHighlightedCategory(null)
          }, 2000) // Keep highlight for 2 seconds
        }, 100)
      }
      // Clear the pre-selected category after handling
      setActionCenterPreselectedCategory(undefined)
    }
  }, [actionCenterPreselectedCategory, actionData, isLoading, setActionCenterPreselectedCategory])

  // Reset selected items when category changes
  useEffect(() => {
    setSelectedItems([])
  }, [selectedCategory])

  // Get current action items for selected category
  const getCurrentActionItems = (): EnrichedActionAnomaly[] => {
    if (!actionData || !selectedCategory) return []

    const category = actionData.categories.find(cat => cat.id === selectedCategory)
    return category?.anomalies || []
  }

  // Filter categories based on toggle state and real data
  const getFilteredCategories = () => {
    if (!actionData) return { all: [], mvp: [], secondary: [] }

    const filtered = showUntriggeredRules
      ? actionData.categories
      : actionData.categories.filter(cat => cat.isTriggered)

    return {
      all: filtered,
      mvp: filtered.filter(cat => cat.category === "MVP"),
      secondary: filtered.filter(cat => cat.category === "SECONDARY")
    }
  }

  const filteredCategoriesData = getFilteredCategories()

  // Calculate active items from currently filtered/visible categories
  const getVisibleActiveItems = () => {
    return filteredCategoriesData.all.reduce((sum, cat) => sum + cat.count, 0)
  }

  const totalFinancialImpact = selectedCategory
    ? actionData?.categories.find((cat) => cat.id === selectedCategory)?.financialImpact || 0
    : actionData?.totalFinancialImpact || 0

  const getPriorityBadge = (priority: string) => {
    switch (priority) {
      case "critical":
        return <Badge className="bg-destructive text-destructive-foreground">CRITICAL</Badge>
      case "high":
        return <Badge className="bg-primary text-primary-foreground">HIGH</Badge>
      case "medium":
        return <Badge className="bg-warning text-warning-foreground">MEDIUM</Badge>
      default:
        return <Badge variant="outline">LOW</Badge>
    }
  }

  return (
    <div className="min-h-screen bg-background">
      {/* Header */}
      <header className="border-b bg-card">
        <div className="px-6 py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-4">
              <Button
                variant="outline"
                size="sm"
                className="bg-background hover:bg-muted border-border"
                onClick={() => setCurrentView('overview')}
              >
                <ArrowLeft className="w-4 h-4 mr-2" />
                Back to Dashboard
              </Button>
              {selectedCategory && (
                <Button
                  variant="outline"
                  size="sm"
                  onClick={() => setSelectedCategory(null)}
                  className="bg-background hover:bg-muted border-border"
                >
                  <ArrowLeft className="w-4 h-4 mr-2" />
                  Back to Categories
                </Button>
              )}
              <div>
                <h1 className="text-xl font-bold text-foreground">
                  {selectedCategory
                    ? actionData?.categories.find((cat) => cat.id === selectedCategory)?.title
                    : "Action Center"}
                </h1>
                <p className="text-sm text-muted-foreground">
                  {selectedCategory
                    ? "Resolve specific items with bulk actions"
                    : "Immediate problem resolution command center"}
                </p>
              </div>
            </div>
            <div className="flex items-center gap-4">
              <Badge variant="outline" className="text-sm">
                <DollarSign className="w-3 h-3 mr-1" />${totalFinancialImpact.toLocaleString()} at risk
              </Badge>
              {selectedItems.length > 0 && (
                <Button size="sm" className="bg-primary hover:bg-primary/90">
                  <Printer className="w-4 h-4 mr-2" />
                  Print Work Orders ({selectedItems.length})
                </Button>
              )}
              <Button
                variant="outline"
                size="sm"
                onClick={loadActionData}
                disabled={isLoading}
                className="bg-background hover:bg-muted border-border"
              >
                <RefreshCw className={cn("w-4 h-4 mr-2", isLoading && "animate-spin")} />
                Refresh
              </Button>
            </div>
          </div>
        </div>
      </header>

      <main className="px-6 py-8">
        {/* Loading State */}
        {isLoading && (
          <div className="flex items-center justify-center h-64">
            <div className="text-center">
              <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto mb-4">
                <RefreshCw className="w-6 h-6" />
              </div>
              <p className="text-gray-600">Loading action center data...</p>
            </div>
          </div>
        )}

        {/* Error State */}
        {error && (
          <div className="bg-red-50 border border-red-200 rounded-lg p-4 mb-6">
            <div className="flex items-center justify-between">
              <div className="flex items-center">
                <AlertTriangle className="h-5 w-5 text-red-400 mr-2" />
                <p className="text-red-800">{error}</p>
              </div>
              <Button
                variant="outline"
                size="sm"
                onClick={loadActionData}
                disabled={isLoading}
              >
                <RefreshCw className="w-4 h-4 mr-2" />
                Retry
              </Button>
            </div>
          </div>
        )}

        {/* Main Content */}
        {!isLoading && !error && actionData && (
          <>
            {!selectedCategory ? (
              // Category View
              <div>
                {/* Empty State - All Anomalies Resolved */}
                {getVisibleActiveItems() === 0 && (
                  <div className="text-center py-16">
                    <div className="mb-6">
                      <CheckCircle2 className="w-16 h-16 text-green-500 mx-auto mb-4" />
                      <h2 className="text-2xl font-bold text-foreground mb-2">🎉 All Clear!</h2>
                      <p className="text-lg text-muted-foreground mb-4">
                        All warehouse anomalies have been resolved successfully.
                      </p>
                      <div className="bg-green-50 border border-green-200 rounded-lg p-4 max-w-md mx-auto">
                        <p className="text-green-800 font-medium">
                          ✅ {actionData.resolvedToday} anomalies resolved today
                        </p>
                        <p className="text-green-600 text-sm mt-1">
                          Your warehouse operations are running smoothly!
                        </p>
                      </div>
                    </div>
                    <div className="space-x-4">
                      <Button
                        onClick={() => setCurrentView('overview')}
                        className="bg-primary hover:bg-primary/90"
                      >
                        Back to Dashboard
                      </Button>
                      <Button
                        variant="outline"
                        onClick={() => window.location.reload()}
                      >
                        Refresh Data
                      </Button>
                    </div>
                  </div>
                )}

                {/* Control Bar - Always show when there are categories */}
                {actionData && actionData.categories.length > 0 && (
                  <div className="mb-8">
                    <div className="flex items-center justify-between p-4 bg-muted/20 rounded-lg border">
                      <div>
                        <h2 className="text-lg font-semibold text-foreground mb-1">Rule Categories</h2>
                        <p className="text-sm text-muted-foreground">
                          {getVisibleActiveItems()} active anomalies • Last updated: {lastRefresh.toLocaleTimeString()}
                        </p>
                      </div>
                      <div className="flex items-center gap-3">
                        <Button
                          variant={showUntriggeredRules ? "default" : "outline"}
                          size="sm"
                          onClick={() => setShowUntriggeredRules(!showUntriggeredRules)}
                          className="flex items-center gap-2"
                        >
                          <AlertTriangle className="w-4 h-4" />
                          {showUntriggeredRules ? "Hide" : "Show"} Untriggered Rules
                        </Button>
                        {getVisibleActiveItems() > 0 && (
                          <Button
                            variant="destructive"
                            size="sm"
                            onClick={handleResolveAll}
                            className="flex items-center gap-2 hover:bg-destructive/90 hover:scale-105 transition-all duration-200 shadow-sm hover:shadow-md"
                          >
                            <CheckCircle2 className="w-4 h-4" />
                            Mark All {getVisibleActiveItems()} Complete
                          </Button>
                        )}
                      </div>
                    </div>
                  </div>
                )}

                {/* Active Categories */}
                {(filteredCategoriesData.mvp.length > 0 || filteredCategoriesData.secondary.length > 0) && (
                  <div>
                {/* MVP Rules Section */}
                {filteredCategoriesData.mvp.length > 0 && (
                  <div className="mb-8">
                    <div className="mb-6">
                      <h2 className="text-2xl font-bold text-foreground mb-1">🎯 Core Operations ({filteredCategoriesData.mvp.filter(r => r.isTriggered).length} active)</h2>
                      <p className="text-sm text-muted-foreground">Critical rules that directly impact warehouse flow and efficiency</p>
                    </div>
                    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                      {filteredCategoriesData.mvp.map((category) => {
                        const IconComponent = category.icon
                        return (
                          <Card
                            key={category.id}
                            className={cn(
                              "cursor-pointer hover:shadow-lg transition-all border-l-4 duration-300",
                              category.borderColor,
                              !category.isTriggered && "opacity-60",
                              highlightedCategory === category.id && "ring-4 ring-primary/50 ring-offset-2 scale-105 shadow-2xl animate-pulse"
                            )}
                            onClick={() => handleCategorySelect(category.id)}
                          >
                            <CardHeader className="pb-3">
                              <div className="flex items-center justify-between">
                                <div className="flex items-center gap-3">
                                  <div className={cn("p-2 rounded-lg", category.bgColor)}>
                                    <IconComponent className={cn("w-6 h-6", category.color)} />
                                  </div>
                                  <div>
                                    <CardTitle className="text-lg">{category.title}</CardTitle>
                                    <CardDescription>{category.description}</CardDescription>
                                  </div>
                                </div>
                                {getPriorityBadge(category.priority)}
                              </div>
                            </CardHeader>
                            <CardContent>
                              <div className="flex items-center justify-between mb-4">
                                <div>
                                  <div className="text-3xl font-bold text-foreground">{category.count}</div>
                                  <div className="text-sm text-muted-foreground">Items requiring action</div>
                                </div>
                                <div className="text-right">
                                  <div className="text-lg font-semibold text-destructive">
                                    ${category.financialImpact.toLocaleString()}
                                  </div>
                                  <div className="text-xs text-muted-foreground">Estimated impact</div>
                                </div>
                              </div>
                              <div className="flex gap-2">
                                <Button
                                  className="flex-1 bg-transparent"
                                  variant="outline"
                                  disabled={!category.isTriggered}
                                  onClick={(e) => {
                                    e.stopPropagation()
                                    if (category.isTriggered) handleCategorySelect(category.id)
                                  }}
                                >
                                  {category.isTriggered ? `View ${category.count} Items` : "No Issues Found"}
                                </Button>
                                {category.isTriggered && (
                                  <Button
                                    variant="ghost"
                                    size="sm"
                                    onClick={(e) => {
                                      e.stopPropagation()
                                      handleResolveCategory(category)
                                    }}
                                    className="px-3"
                                    title={`Mark all ${category.count} ${category.title} anomalies as resolved`}
                                  >
                                    <CheckCircle2 className="w-4 h-4" />
                                  </Button>
                                )}
                              </div>
                            </CardContent>
                          </Card>
                        )
                      })}
                    </div>
                  </div>
                )}

                {/* Secondary Rules Section */}
                {filteredCategoriesData.secondary.length > 0 && (
                  <div className="mb-8">
                    <div className="mb-6">
                      <h2 className="text-2xl font-bold text-foreground mb-1">🔧 Quality & Compliance ({filteredCategoriesData.secondary.filter(r => r.isTriggered).length} active)</h2>
                      <p className="text-sm text-muted-foreground">Supporting rules for data quality, compliance, and system integrity</p>
                    </div>
                    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                      {filteredCategoriesData.secondary.map((category) => {
                        const IconComponent = category.icon
                        return (
                          <Card
                            key={category.id}
                            className={cn(
                              "cursor-pointer hover:shadow-lg transition-all border-l-4 duration-300",
                              category.borderColor,
                              !category.isTriggered && "opacity-60",
                              highlightedCategory === category.id && "ring-4 ring-primary/50 ring-offset-2 scale-105 shadow-2xl animate-pulse"
                            )}
                            onClick={() => handleCategorySelect(category.id)}
                          >
                            <CardHeader className="pb-3">
                              <div className="flex items-center justify-between">
                                <div className="flex items-center gap-3">
                                  <div className={cn("p-2 rounded-lg", category.bgColor)}>
                                    <IconComponent className={cn("w-6 h-6", category.color)} />
                                  </div>
                                  <div>
                                    <CardTitle className="text-lg">{category.title}</CardTitle>
                                    <CardDescription>{category.description}</CardDescription>
                                  </div>
                                </div>
                                {getPriorityBadge(category.priority)}
                              </div>
                            </CardHeader>
                            <CardContent>
                              <div className="flex items-center justify-between mb-4">
                                <div>
                                  <div className="text-3xl font-bold text-foreground">{category.count}</div>
                                  <div className="text-sm text-muted-foreground">Items requiring action</div>
                                </div>
                                <div className="text-right">
                                  <div className="text-lg font-semibold text-destructive">
                                    ${category.financialImpact.toLocaleString()}
                                  </div>
                                  <div className="text-xs text-muted-foreground">Estimated impact</div>
                                </div>
                              </div>
                              <div className="flex gap-2">
                                <Button
                                  className="flex-1 bg-transparent"
                                  variant="outline"
                                  disabled={!category.isTriggered}
                                  onClick={(e) => {
                                    e.stopPropagation()
                                    if (category.isTriggered) handleCategorySelect(category.id)
                                  }}
                                >
                                  {category.isTriggered ? `View ${category.count} Items` : "No Issues Found"}
                                </Button>
                                {category.isTriggered && (
                                  <Button
                                    variant="ghost"
                                    size="sm"
                                    onClick={(e) => {
                                      e.stopPropagation()
                                      handleResolveCategory(category)
                                    }}
                                    className="px-3"
                                    title={`Mark all ${category.count} ${category.title} anomalies as resolved`}
                                  >
                                    <CheckCircle2 className="w-4 h-4" />
                                  </Button>
                                )}
                              </div>
                            </CardContent>
                          </Card>
                        )
                      })}
                    </div>
                  </div>
                )}
                  </div>
                )}

                {/* Quick Stats */}
                <div className="mt-8 grid grid-cols-1 md:grid-cols-4 gap-4">
                  <Card>
                    <CardContent className="p-4">
                      <div className="flex items-center gap-3">
                        <AlertTriangle className="w-8 h-8 text-destructive" />
                        <div>
                          <div className="text-2xl font-bold">{getVisibleActiveItems()}</div>
                          <div className="text-sm text-muted-foreground">Active Items</div>
                        </div>
                      </div>
                    </CardContent>
                  </Card>
                  <Card>
                    <CardContent className="p-4">
                      <div className="flex items-center gap-3">
                        <DollarSign className="w-8 h-8 text-primary" />
                        <div>
                          <div className="text-2xl font-bold">${(actionData.totalFinancialImpact / 1000).toFixed(1)}K</div>
                          <div className="text-sm text-muted-foreground">Active Risk</div>
                        </div>
                      </div>
                    </CardContent>
                  </Card>
                  <Card>
                    <CardContent className="p-4">
                      <div className="flex items-center gap-3">
                        <Timer className="w-8 h-8 text-warning" />
                        <div>
                          <div className="text-2xl font-bold">{actionData.avgHoursCritical}</div>
                          <div className="text-sm text-muted-foreground">Avg Hours Critical</div>
                        </div>
                      </div>
                    </CardContent>
                  </Card>
                  <Card>
                    <CardContent className="p-4">
                      <div className="flex items-center gap-3">
                        <CheckCircle2 className="w-8 h-8 text-success" />
                        <div>
                          <div className="text-2xl font-bold">{actionData.resolvedToday}</div>
                          <div className="text-sm text-muted-foreground">Resolved Today</div>
                        </div>
                      </div>
                    </CardContent>
                  </Card>
                </div>
              </div>
            ) : (
              // Detail View
              <div>
                <div className="mb-6 flex items-center justify-between">
                  <div>
                    <h2 className="text-2xl font-bold text-foreground mb-2">Item Details</h2>
                    <p className="text-muted-foreground">Select items for bulk resolution</p>
                  </div>
                  <div className="flex items-center gap-4">
                    <div className="flex items-center gap-2">
                      <Input
                        placeholder="Search items..."
                        value={searchQuery}
                        onChange={(e) => setSearchQuery(e.target.value)}
                        className="w-64"
                      />
                      <Button variant="outline" size="sm">
                        <Filter className="w-4 h-4" />
                      </Button>
                    </div>
                    <div className="flex items-center gap-2">
                      <Button size="sm" onClick={handleSelectAll}>
                        Select All {getCurrentActionItems().length}
                      </Button>
                      {selectedItems.length > 0 && (
                        <>
                          <Button variant="outline" size="sm" onClick={handleClearSelection}>
                            Clear ({selectedItems.length})
                          </Button>
                          <Button
                            variant="default"
                            size="sm"
                            onClick={handleMarkSelectedResolved}
                            className="bg-primary hover:bg-primary/90"
                          >
                            <CheckCircle2 className="w-4 h-4 mr-2" />
                            Mark {selectedItems.length} Resolved
                          </Button>
                        </>
                      )}
                    </div>
                  </div>
                </div>

                {/* Professional Empty State - Category Complete */}
                {getCurrentActionItems().length === 0 && (
                  <div className="py-12 px-6">
                    <div className="max-w-3xl mx-auto">
                      <div className="border border-border rounded-lg bg-card shadow-sm">
                        <div className="border-b border-border px-6 py-4">
                          <div className="flex items-center gap-3">
                            <div className="flex-shrink-0">
                              <div className="w-12 h-12 bg-green-100 rounded-lg flex items-center justify-center">
                                <CheckCircle2 className="w-6 h-6 text-green-600" />
                              </div>
                            </div>
                            <div>
                              <h2 className="text-lg font-semibold text-foreground">
                                {actionData?.categories.find(cat => cat.id === selectedCategory)?.title || 'Category'} Complete
                              </h2>
                              <p className="text-sm text-muted-foreground">
                                All anomalies resolved — operations optimal
                              </p>
                            </div>
                          </div>
                        </div>

                        {/* Summary Metrics */}
                        <div className="p-6">
                          <div className="grid grid-cols-2 gap-6 mb-6">
                            <div className="bg-muted/30 rounded-lg p-4 text-center">
                              <div className="text-2xl font-semibold text-foreground mb-1">
                                {actionData?.categories.find(cat => cat.id === selectedCategory)?.count || 0}
                              </div>
                              <div className="text-sm font-medium text-muted-foreground">Anomalies Resolved</div>
                            </div>
                            <div className="bg-muted/30 rounded-lg p-4 text-center">
                              <div className="text-2xl font-semibold text-foreground mb-1">
                                ${actionData?.categories.find(cat => cat.id === selectedCategory)?.financialImpact?.toLocaleString() || 0}
                              </div>
                              <div className="text-sm font-medium text-muted-foreground">Cost Impact</div>
                            </div>
                          </div>

                          {/* Navigation Actions */}
                          <div className="flex flex-col sm:flex-row gap-3">
                            <Button
                              onClick={() => setSelectedCategory(null)}
                              variant="default"
                              className="flex-1 sm:flex-none"
                            >
                              <ArrowLeft className="w-4 h-4 mr-2" />
                              Back to Categories
                            </Button>
                            <Button
                              onClick={() => setCurrentView('overview')}
                              variant="outline"
                              className="flex-1 sm:flex-none"
                            >
                              Dashboard
                            </Button>
                          </div>
                        </div>
                      </div>
                    </div>
                  </div>
                )}

                {/* Action Items List */}
                {getCurrentActionItems().length > 0 && (
                  <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
                  {getCurrentActionItems()
                    .filter((item) => {
                      if (searchQuery === '') return true

                      const query = searchQuery.toLowerCase()
                      return (
                        item.location_name?.toLowerCase().includes(query) ||
                        String(item.pallet_id).toLowerCase().includes(query) ||
                        item.anomaly_type?.toLowerCase().includes(query) ||
                        item.details?.toLowerCase().includes(query) ||
                        item.category_id?.toLowerCase().includes(query)
                      )
                    })
                    .map((item) => (
                      <Card key={item.id} className={cn(
                        "hover:shadow-md transition-all duration-200 cursor-pointer border-2",
                        selectedItems.includes(item.id.toString())
                          ? "border-primary bg-primary/5 hover:bg-primary/10"
                          : "border-transparent hover:border-primary/20"
                      )}>
                        <CardContent className="p-4">
                          <div className="flex items-start gap-3">
                            <Checkbox
                              checked={selectedItems.includes(item.id.toString())}
                              onCheckedChange={() => handleItemSelect(item.id.toString())}
                              className="mt-1"
                            />

                            <div
                              className="flex-1 min-w-0 cursor-pointer"
                              onClick={() => handleItemSelect(item.id.toString())}
                            >
                              <div className="flex items-start justify-between mb-3">
                                <div className="flex items-center gap-2">
                                  <span className="font-bold text-lg text-foreground">{item.pallet_id}</span>
                                  {getPriorityBadge(item.priority.toLowerCase())}
                                </div>
                                <div className="text-right">
                                  <div className="font-bold text-lg text-destructive">${item.calculated_financial_impact}</div>
                                  <div className="text-xs text-muted-foreground">daily cost</div>
                                </div>
                              </div>

                              <div className="flex items-center justify-between mb-2 pb-2 border-b border-border/50">
                                <div className="flex items-center gap-2">
                                  <MapPin className="w-4 h-4 text-muted-foreground" />
                                  <span className="text-sm font-medium">{item.location_name}</span>
                                </div>
                                <Badge variant="outline" className="text-xs">
                                  <Clock className="w-3 h-3 mr-1" />
                                  {item.days_idle} days idle
                                </Badge>
                              </div>

                              <div className="mb-3">
                                <p className="text-sm text-muted-foreground leading-relaxed">
                                  {item.details || `${item.anomaly_type} detected - requires attention`}
                                </p>
                              </div>

                              <div
                                className="flex items-center justify-end gap-2"
                                onClick={(e) => e.stopPropagation()}
                              >
                                <Button
                                  variant="outline"
                                  size="sm"
                                  className="h-8 px-3 text-xs bg-primary/5 hover:bg-primary/10 border-primary/30 text-primary font-medium"
                                  onClick={() => handleOpenResolutionModal(item)}
                                >
                                  Resolution Steps
                                </Button>
                                <Button
                                  variant="ghost"
                                  size="sm"
                                  className="h-8 px-3 text-xs"
                                  onClick={() => handleMarkSingleResolved(item.id.toString())}
                                >
                                  <CheckCircle2 className="w-3 h-3 mr-1" />
                                  Mark Done
                                </Button>
                              </div>
                            </div>
                          </div>
                        </CardContent>
                      </Card>
                    ))}
                </div>
                )}

                {/* Bulk Actions */}
                {selectedItems.length > 0 && (
                  <Card className="mt-6 border-primary">
                    <CardContent className="p-6">
                      <div className="flex items-center justify-between">
                        <div>
                          <div className="font-semibold text-lg">Bulk Actions</div>
                          <div className="text-sm text-muted-foreground mt-1">{selectedItems.length} items selected</div>
                        </div>
                        <div className="flex items-center">
                          <Button
                            className="bg-primary hover:bg-primary/90 px-8"
                            onClick={handleMarkSelectedResolved}
                          >
                            <CheckCircle2 className="w-4 h-4 mr-2" />
                            Mark as Resolved
                          </Button>
                        </div>
                      </div>
                    </CardContent>
                  </Card>
                )}
              </div>
            )}
          </>
        )}
      </main>

      {/* Anomaly Management Modal (matching reports overview) */}
      <AnomalyManagementModal
        isOpen={isManageModalOpen}
        onClose={() => {
          setIsManageModalOpen(false)
          setManagingAnomaly(null)
        }}
        onResolve={(anomalyId) => {
          handleMarkResolved(anomalyId)
        }}
        anomaly={managingAnomaly ? {
          id: managingAnomaly.id.toString(),
          anomaly_type: managingAnomaly.anomaly_type,
          location: managingAnomaly.location_name,
          priority: managingAnomaly.priority,
          details: managingAnomaly.details || '',
          detectedTime: '2 hours ago' // Could be calculated from actual data
        } : null}
      />

      {/* Custom Confirmation Modal */}
      <ConfirmationModal
        open={confirmationModal.open}
        onOpenChange={(open) => setConfirmationModal(prev => ({ ...prev, open }))}
        title={confirmationModal.title}
        description={confirmationModal.description}
        confirmText={confirmationModal.confirmText}
        variant={confirmationModal.variant}
        isLoading={isLoading}
        onConfirm={() => {
          confirmationModal.onConfirm()
          setConfirmationModal(prev => ({ ...prev, open: false }))
        }}
      />
    </div>
  )
}