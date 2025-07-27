"use client"

import React from 'react'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { 
  Select, 
  SelectContent, 
  SelectItem, 
  SelectTrigger, 
  SelectValue 
} from '@/components/ui/select'
import { 
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuSeparator,
  DropdownMenuTrigger
} from '@/components/ui/dropdown-menu'
import { 
  Plus, 
  Search, 
  
  MoreHorizontal, 
  Play, 
  Pause, 
  Copy, 
  Edit, 
  Trash2,
  Download,
  Upload,
  Zap,
  Activity,
  Timer,
  MapPin
} from 'lucide-react'
import { 
  useRulesStore, 
  useFilteredRules, 
  useRulesStats, 
  useRulesByCategory 
} from '@/lib/rules-store'
import { PRIORITY_LEVELS, RULE_CATEGORIES } from '@/lib/rules-types'
import type { Rule, RuleFilters } from '@/lib/rules-types'
import { toast } from '@/lib/hooks/use-toast'

export function RulesOverview() {
  const {
    filters,
    searchQuery,
    categories,
    setFilters,
    setSearchQuery,
    setCurrentSubView,
    setSelectedRule,
    toggleRuleActivation,
    deleteRule,
    duplicateRule,
    isLoading
  } = useRulesStore()

  const filteredRules = useFilteredRules()
  const rulesStats = useRulesStats()
  const rulesByCategory = useRulesByCategory()

  return (
    <div className="space-y-6">
      {/* Stats Cards */}
      <RulesStatsCards stats={rulesStats} />
      
      {/* Actions and Filters */}
      <RulesFiltersAndActions 
        filters={filters}
        searchQuery={searchQuery}
        categories={categories}
        onFiltersChange={setFilters}
        onSearchChange={setSearchQuery}
        onCreateRule={() => setCurrentSubView('create')}
      />

      {/* Rules by Category */}
      <div className="space-y-6">
        {Object.entries(RULE_CATEGORIES).map(([categoryKey, categoryInfo]) => {
          const categoryRules = rulesByCategory[categoryInfo.display_name] || []
          
          if (categoryRules.length === 0) return null

          return (
            <CategorySection
              key={categoryKey}
              category={categoryInfo}
              rules={categoryRules}
              onRuleAction={handleRuleAction}
              onRuleSelect={setSelectedRule}
            />
          )
        })}
      </div>

      {/* Empty State */}
      {filteredRules.length === 0 && !isLoading && (
        <EmptyState 
          hasFilters={Object.keys(filters).length > 1 || searchQuery.length > 0}
          onClearFilters={() => {
            setFilters({ status: 'all' })
            setSearchQuery('')
          }}
          onCreateRule={() => setCurrentSubView('create')}
        />
      )}
    </div>
  )

  async function handleRuleAction(action: string, rule: Rule) {
    try {
      switch (action) {
        case 'toggle':
          await toggleRuleActivation(rule.id, !rule.is_active)
          toast({
            title: 'Success',
            description: `Rule ${rule.is_active ? 'deactivated' : 'activated'} successfully`
          })
          break
          
        case 'duplicate':
          await duplicateRule(rule.id, `${rule.name} (Copy)`)
          toast({
            title: 'Success',
            description: 'Rule duplicated successfully'
          })
          break
          
        case 'delete':
          if (confirm(`Are you sure you want to delete "${rule.name}"?`)) {
            await deleteRule(rule.id)
            toast({
              title: 'Success',
              description: 'Rule deleted successfully'
            })
          }
          break
          
        case 'edit':
          setSelectedRule(rule)
          setCurrentSubView('create') // Will be edit mode
          break
      }
    } catch {
      toast({
        variant: 'destructive',
        title: 'Error',
        description: `Failed to ${action} rule`
      })
    }
  }
}

// Stats Cards Component
function RulesStatsCards({ stats }: { stats: ReturnType<typeof useRulesStats> }) {
  return (
    <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
      <Card>
        <CardContent className="p-6">
          <div className="flex items-center space-x-2">
            <Activity className="w-5 h-5 text-blue-500" />
            <div>
              <p className="text-2xl font-bold">{stats.total}</p>
              <p className="text-sm text-muted-foreground">Total Rules</p>
            </div>
          </div>
        </CardContent>
      </Card>
      
      <Card>
        <CardContent className="p-6">
          <div className="flex items-center space-x-2">
            <Play className="w-5 h-5 text-green-500" />
            <div>
              <p className="text-2xl font-bold text-green-600">{stats.active}</p>
              <p className="text-sm text-muted-foreground">Active Rules</p>
            </div>
          </div>
        </CardContent>
      </Card>
      
      <Card>
        <CardContent className="p-6">
          <div className="flex items-center space-x-2">
            <Zap className="w-5 h-5 text-purple-500" />
            <div>
              <p className="text-2xl font-bold text-purple-600">{stats.custom}</p>
              <p className="text-sm text-muted-foreground">Custom Rules</p>
            </div>
          </div>
        </CardContent>
      </Card>
      
      <Card>
        <CardContent className="p-6">
          <div className="flex items-center space-x-2">
            <Timer className="w-5 h-5 text-orange-500" />
            <div>
              <p className="text-2xl font-bold text-orange-600">{stats.default}</p>
              <p className="text-sm text-muted-foreground">Default Rules</p>
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  )
}

// Filters and Actions Component
function RulesFiltersAndActions({
  filters,
  searchQuery,
  categories,
  onFiltersChange,
  onSearchChange,
  onCreateRule
}: {
  filters: RuleFilters
  searchQuery: string
  categories: Array<{ id: number; name: string; display_name: string }>
  onFiltersChange: (filters: Partial<RuleFilters>) => void
  onSearchChange: (query: string) => void
  onCreateRule: () => void
}) {
  return (
    <div className="flex flex-col sm:flex-row gap-4 items-start sm:items-center justify-between">
      {/* Search and Filters */}
      <div className="flex flex-1 gap-4 items-center">
        <div className="relative flex-1 max-w-sm">
          <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 w-4 h-4" />
          <Input
            placeholder="Search rules..."
            value={searchQuery}
            onChange={(e) => onSearchChange(e.target.value)}
            className="pl-10"
          />
        </div>
        
        <Select 
          value={filters.category || 'all'} 
          onValueChange={(value) => onFiltersChange({ category: value === 'all' ? undefined : value })}
        >
          <SelectTrigger className="w-48">
            <SelectValue placeholder="All Categories" />
          </SelectTrigger>
          <SelectContent>
            <SelectItem value="all">All Categories</SelectItem>
            {categories.map((cat) => (
              <SelectItem key={cat.id} value={cat.name}>
                {cat.display_name}
              </SelectItem>
            ))}
          </SelectContent>
        </Select>
        
        <Select 
          value={filters.priority || 'all'} 
          onValueChange={(value) => onFiltersChange({ priority: value === 'all' ? undefined : value as 'VERY_HIGH' | 'HIGH' | 'MEDIUM' | 'LOW' })}
        >
          <SelectTrigger className="w-32">
            <SelectValue placeholder="Priority" />
          </SelectTrigger>
          <SelectContent>
            <SelectItem value="all">All</SelectItem>
            {Object.entries(PRIORITY_LEVELS).map(([key, priority]) => (
              <SelectItem key={key} value={key}>
                {priority.label}
              </SelectItem>
            ))}
          </SelectContent>
        </Select>
        
        <Select 
          value={filters.status || 'all'} 
          onValueChange={(value) => onFiltersChange({ status: value as 'all' | 'active' | 'inactive' })}
        >
          <SelectTrigger className="w-28">
            <SelectValue placeholder="Status" />
          </SelectTrigger>
          <SelectContent>
            <SelectItem value="all">All</SelectItem>
            <SelectItem value="active">Active</SelectItem>
            <SelectItem value="inactive">Inactive</SelectItem>
          </SelectContent>
        </Select>
      </div>

      {/* Action Buttons */}
      <div className="flex gap-2">
        <Button variant="outline" size="sm">
          <Upload className="w-4 h-4 mr-2" />
          Import
        </Button>
        <Button variant="outline" size="sm">
          <Download className="w-4 h-4 mr-2" />
          Export
        </Button>
        <Button onClick={onCreateRule} size="sm">
          <Plus className="w-4 h-4 mr-2" />
          Create Rule
        </Button>
      </div>
    </div>
  )
}

// Category Section Component
function CategorySection({
  category,
  rules,
  onRuleAction,
  onRuleSelect
}: {
  category: { name: string; display_name: string; description: string; color: string }
  rules: Rule[]
  onRuleAction: (action: string, rule: Rule) => void
  onRuleSelect: (rule: Rule) => void
}) {
  const categoryColor = category.color === 'red' ? 'destructive' : 
                       category.color === 'orange' ? 'secondary' : 'default'

  return (
    <Card>
      <CardHeader className="pb-4">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className={`w-3 h-3 rounded-full bg-${category.color}-500`} />
            <div>
              <CardTitle className="text-lg">{category.display_name}</CardTitle>
              <p className="text-sm text-muted-foreground mt-1">
                {category.description}
              </p>
            </div>
          </div>
          <Badge variant={categoryColor}>
            {rules.length} rule{rules.length !== 1 ? 's' : ''}
          </Badge>
        </div>
      </CardHeader>
      <CardContent>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {rules.map((rule) => (
            <RuleCard
              key={rule.id}
              rule={rule}
              onAction={onRuleAction}
              onSelect={onRuleSelect}
            />
          ))}
        </div>
      </CardContent>
    </Card>
  )
}

// Rule Card Component
function RuleCard({
  rule,
  onAction,
  onSelect
}: {
  rule: Rule
  onAction: (action: string, rule: Rule) => void
  onSelect: (rule: Rule) => void
}) {
  const priorityConfig = PRIORITY_LEVELS[rule.priority]

  return (
    <Card className="hover:shadow-md transition-shadow cursor-pointer group">
      <CardHeader className="pb-3">
        <div className="flex items-start justify-between">
          <div className="space-y-2 flex-1" onClick={() => onSelect(rule)}>
            <CardTitle className="text-base leading-tight">{rule.name}</CardTitle>
            <div className="flex items-center gap-2">
              <Badge variant={rule.is_active ? "default" : "secondary"}>
                {rule.is_active ? "Active" : "Inactive"}
              </Badge>
              <Badge variant={priorityConfig.color as 'default' | 'secondary' | 'destructive' | 'outline'}>
                {priorityConfig.label}
              </Badge>
              {rule.is_default && (
                <Badge variant="outline">Default</Badge>
              )}
            </div>
          </div>
          
          <DropdownMenu>
            <DropdownMenuTrigger asChild>
              <Button 
                variant="ghost" 
                size="sm" 
                className="opacity-0 group-hover:opacity-100 transition-opacity"
              >
                <MoreHorizontal className="h-4 w-4" />
              </Button>
            </DropdownMenuTrigger>
            <DropdownMenuContent align="end">
              <DropdownMenuItem onClick={() => onAction('edit', rule)}>
                <Edit className="w-4 h-4 mr-2" />
                Edit
              </DropdownMenuItem>
              <DropdownMenuItem onClick={() => onAction('duplicate', rule)}>
                <Copy className="w-4 h-4 mr-2" />
                Duplicate
              </DropdownMenuItem>
              <DropdownMenuItem onClick={() => onAction('toggle', rule)}>
                {rule.is_active ? (
                  <>
                    <Pause className="w-4 h-4 mr-2" />
                    Deactivate
                  </>
                ) : (
                  <>
                    <Play className="w-4 h-4 mr-2" />
                    Activate
                  </>
                )}
              </DropdownMenuItem>
              <DropdownMenuSeparator />
              <DropdownMenuItem 
                onClick={() => onAction('delete', rule)}
                className="text-destructive"
                disabled={rule.is_default}
              >
                <Trash2 className="w-4 h-4 mr-2" />
                Delete
              </DropdownMenuItem>
            </DropdownMenuContent>
          </DropdownMenu>
        </div>
      </CardHeader>
      
      <CardContent onClick={() => onSelect(rule)}>
        <p className="text-sm text-muted-foreground mb-3 line-clamp-2">
          {rule.description}
        </p>
        <div className="flex items-center justify-between text-sm">
          <span className="text-muted-foreground">
            {rule.rule_type.replace(/_/g, ' ')}
          </span>
          <span className="text-muted-foreground">
            By {rule.creator_username}
          </span>
        </div>
      </CardContent>
    </Card>
  )
}

// Empty State Component
function EmptyState({
  hasFilters,
  onClearFilters,
  onCreateRule
}: {
  hasFilters: boolean
  onClearFilters: () => void
  onCreateRule: () => void
}) {
  return (
    <Card>
      <CardContent className="text-center py-12">
        <MapPin className="w-16 h-16 text-gray-400 mx-auto mb-4" />
        <h3 className="text-lg font-medium mb-2">
          {hasFilters ? 'No rules found' : 'No rules configured yet'}
        </h3>
        <p className="text-gray-600 mb-6 max-w-md mx-auto">
          {hasFilters 
            ? 'Try adjusting your filters or search terms to find the rules you\'re looking for.'
            : 'Get started by creating your first warehouse rule or using one of our templates.'
          }
        </p>
        <div className="flex gap-2 justify-center">
          {hasFilters && (
            <Button variant="outline" onClick={onClearFilters}>
              Clear Filters
            </Button>
          )}
          <Button onClick={onCreateRule}>
            <Plus className="w-4 h-4 mr-2" />
            Create Your First Rule
          </Button>
        </div>
      </CardContent>
    </Card>
  )
}