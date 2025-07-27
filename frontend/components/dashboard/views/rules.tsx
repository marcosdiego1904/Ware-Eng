"use client"

import { useEffect } from 'react'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs'
import { Settings, Plus, Zap, BarChart3 } from 'lucide-react'
import { useRulesStore, useRulesViewState } from '@/lib/rules-store'
import { RulesOverview } from '@/components/rules/rules-overview'
import { RuleCreator } from '@/components/rules/rule-creator'
import { RuleTemplates } from '@/components/rules/rule-templates'
import { RuleAnalytics } from '@/components/rules/rule-analytics'
import { LoadingSpinner } from '@/components/ui/loading'

export function RulesView() {
  const { setCurrentSubView, loadRules, loadCategories, isLoading } = useRulesStore()
  const { currentSubView } = useRulesViewState()

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
          <TabsTrigger value="create" className="flex items-center gap-2">
            <Plus className="w-4 h-4" />
            Create Rule
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
          <RulesOverview />
        </TabsContent>

        <TabsContent value="create" className="mt-6">
          <RuleCreator />
        </TabsContent>

        <TabsContent value="templates" className="mt-6">
          <RuleTemplates />
        </TabsContent>

        <TabsContent value="analytics" className="mt-6">
          <RuleAnalytics />
        </TabsContent>
      </Tabs>
    </div>
  )
}