"use client"

import { useEffect, useState } from 'react'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs'
import { Settings, Zap, BarChart3, Brain, Sparkles } from 'lucide-react'
import { useRulesStore, useRulesViewState } from '@/lib/rules-store'
import { RulesOverview } from '@/components/rules/rules-overview'
import { EnhancedRuleCreator } from '@/components/rules/enhanced-rule-creator'
import { RolloutStrategy } from '@/components/rules/rollout-strategy'
import { RuleTemplates } from '@/components/rules/rule-templates'
import { RuleAnalytics } from '@/components/rules/rule-analytics'
import { LoadingSpinner } from '@/components/ui/loading'
import { SimpleErrorBoundary } from '@/components/ui/error-boundary'

// Feature flag - you can control this from environment variables or admin settings
const ENABLE_ROLLOUT_STRATEGY = process.env.NEXT_PUBLIC_ENABLE_ROLLOUT_STRATEGY === 'true' || false

export function RulesViewWithRollout() {
  const { setCurrentSubView, loadRules, loadCategories, isLoading } = useRulesStore()
  const { currentSubView } = useRulesViewState()
  const [showRolloutStrategy, setShowRolloutStrategy] = useState(ENABLE_ROLLOUT_STRATEGY)

  // Load initial data
  useEffect(() => {
    const initializeRules = async () => {
      await Promise.all([
        loadRules(),
        loadCategories()
      ])
    }
    
    initializeRules()
  }, [loadRules, loadCategories])

  // Check if user has made a preference choice
  useEffect(() => {
    const userPreference = localStorage.getItem('ruleBuilderPreference')
    if (userPreference && userPreference !== 'auto') {
      setShowRolloutStrategy(false)
    }
  }, [])

  if (isLoading) {
    return (
      <div className="p-6">
        <div className="flex items-center justify-center h-64">
          <LoadingSpinner />
        </div>
      </div>
    )
  }

  return (
    <div className="p-6 space-y-6">
      {/* Header */}
      <div className="flex items-center gap-2">
        <Settings className="w-6 h-6 text-primary" />
        <h1 className="text-2xl font-bold">Warehouse Rules</h1>
      </div>

      {/* Navigation Tabs */}
      <Tabs 
        value={currentSubView} 
        onValueChange={(value) => setCurrentSubView(value as 'overview' | 'create' | 'templates' | 'analytics')}
        className="w-full"
      >
        <TabsList className="grid w-full grid-cols-4">
          <TabsTrigger value="overview" className="flex items-center gap-2">
            <Settings className="w-4 h-4" />
            Overview
          </TabsTrigger>
          <TabsTrigger value="create" className="flex items-center gap-2 relative">
            <div className="absolute -top-1 -right-1 opacity-75">
              <div className="w-2 h-2 bg-gradient-to-r from-blue-500 to-purple-500 rounded-full animate-pulse"></div>
            </div>
            <div className="p-1 rounded bg-gradient-to-r from-blue-100 to-purple-100">
              <Brain className="w-4 h-4 text-blue-600" />
            </div>
            <span>Smart Builder</span>
            <Sparkles className="w-3 h-3 text-purple-500 opacity-70" />
          </TabsTrigger>
          <TabsTrigger value="templates" className="flex items-center gap-2">
            <Zap className="w-4 h-4" />
            Templates
          </TabsTrigger>
          <TabsTrigger value="analytics" className="flex items-center gap-2">
            <BarChart3 className="w-4 h-4" />
            Analytics
          </TabsTrigger>
        </TabsList>

        {/* Tab Contents */}
        <TabsContent value="overview" className="mt-6">
          <SimpleErrorBoundary message="Failed to load rules overview">
            <RulesOverview />
          </SimpleErrorBoundary>
        </TabsContent>

        <TabsContent value="create" className="mt-6">
          <SimpleErrorBoundary message="Failed to load AI-powered rule creator">
            {showRolloutStrategy ? (
              <RolloutStrategy 
                onModeChange={(mode) => {
                  // User has made a choice, disable rollout strategy
                  setShowRolloutStrategy(false)
                  localStorage.setItem('ruleBuilderMode', mode)
                }}
              />
            ) : (
              <EnhancedRuleCreator />
            )}
          </SimpleErrorBoundary>
        </TabsContent>

        <TabsContent value="templates" className="mt-6">
          <SimpleErrorBoundary message="Failed to load rule templates">
            <RuleTemplates />
          </SimpleErrorBoundary>
        </TabsContent>

        <TabsContent value="analytics" className="mt-6">
          <SimpleErrorBoundary message="Failed to load rule analytics">
            <RuleAnalytics />
          </SimpleErrorBoundary>
        </TabsContent>
      </Tabs>
    </div>
  )
}