"use client"

import { useState, useEffect } from 'react'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { Textarea } from '@/components/ui/textarea'
import { 
  Select, 
  SelectContent, 
  SelectItem, 
  SelectTrigger, 
  SelectValue 
} from '@/components/ui/select'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs'
import { Alert, AlertDescription } from '@/components/ui/alert'
import { 
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuSeparator,
  DropdownMenuTrigger
} from '@/components/ui/dropdown-menu'
import { 
  Search, 
  Plus, 
  Star, 
  Download, 
  Share, 
  MoreHorizontal,
  Zap,
  Clock,
  Users,
  TrendingUp,
  Filter,
  BookOpen,
  Settings,
  Copy,
  Eye,
  Play
} from 'lucide-react'
import { useRulesStore } from '@/lib/rules-store'
import { RULE_CATEGORIES } from '@/lib/rules-types'
import type { RuleTemplate } from '@/lib/rules-types'
import { toast } from '@/lib/hooks/use-toast'

export function RuleTemplates() {
  const { 
    templates,
    loadTemplates,
    createFromTemplate,
    setCurrentSubView,
    isLoading
  } = useRulesStore()

  const [searchQuery, setSearchQuery] = useState('')
  const [selectedCategory, setSelectedCategory] = useState<string>('all')
  const [selectedTemplate, setSelectedTemplate] = useState<RuleTemplate | null>(null)
  const [showCreateDialog, setShowCreateDialog] = useState(false)

  useEffect(() => {
    loadTemplates()
  }, [])

  const filteredTemplates = templates.filter(template => {
    const matchesSearch = template.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
                         template.description.toLowerCase().includes(searchQuery.toLowerCase())
    const matchesCategory = selectedCategory === 'all' || template.category_name === selectedCategory
    return matchesSearch && matchesCategory
  })

  const handleCreateFromTemplate = async (template: RuleTemplate, ruleName: string, parameters: Record<string, unknown>) => {
    try {
      await createFromTemplate(template.id, parameters, ruleName)
      toast({
        title: 'Success',
        description: `Rule "${ruleName}" created from template`
      })
      setShowCreateDialog(false)
      setSelectedTemplate(null)
      setCurrentSubView('overview')
    } catch {
      toast({
        variant: 'destructive',
        title: 'Error',
        description: 'Failed to create rule from template'
      })
    }
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-2xl font-bold">Rule Templates</h2>
          <p className="text-muted-foreground">
            Pre-built rule templates to quickly detect common warehouse anomalies
          </p>
        </div>
        <Button>
          <Plus className="w-4 h-4 mr-2" />
          Create Template
        </Button>
      </div>

      {/* Stats Cards */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <Card>
          <CardContent className="p-6">
            <div className="flex items-center space-x-2">
              <BookOpen className="w-5 h-5 text-blue-500" />
              <div>
                <p className="text-2xl font-bold">{templates.length}</p>
                <p className="text-sm text-muted-foreground">Total Templates</p>
              </div>
            </div>
          </CardContent>
        </Card>
        
        <Card>
          <CardContent className="p-6">
            <div className="flex items-center space-x-2">
              <Star className="w-5 h-5 text-yellow-500" />
              <div>
                <p className="text-2xl font-bold">{templates.filter(t => t.is_public).length}</p>
                <p className="text-sm text-muted-foreground">Public Templates</p>
              </div>
            </div>
          </CardContent>
        </Card>
        
        <Card>
          <CardContent className="p-6">
            <div className="flex items-center space-x-2">
              <Users className="w-5 h-5 text-green-500" />
              <div>
                <p className="text-2xl font-bold">{templates.filter(t => !t.is_public).length}</p>
                <p className="text-sm text-muted-foreground">My Templates</p>
              </div>
            </div>
          </CardContent>
        </Card>
        
        <Card>
          <CardContent className="p-6">
            <div className="flex items-center space-x-2">
              <TrendingUp className="w-5 h-5 text-purple-500" />
              <div>
                <p className="text-2xl font-bold">42</p>
                <p className="text-sm text-muted-foreground">Rules Created</p>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Filters */}
      <div className="flex flex-col sm:flex-row gap-4 items-start sm:items-center justify-between">
        <div className="flex flex-1 gap-4 items-center">
          <div className="relative flex-1 max-w-sm">
            <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 w-4 h-4" />
            <Input
              placeholder="Search templates..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              className="pl-10"
            />
          </div>
          
          <Select value={selectedCategory} onValueChange={setSelectedCategory}>
            <SelectTrigger className="w-48">
              <SelectValue placeholder="All Categories" />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="all">All Categories</SelectItem>
              {Object.entries(RULE_CATEGORIES).map(([key, category]) => (
                <SelectItem key={key} value={category.display_name}>
                  {category.display_name}
                </SelectItem>
              ))}
            </SelectContent>
          </Select>
        </div>

        <div className="flex gap-2">
          <Button variant="outline" size="sm">
            <Filter className="w-4 h-4 mr-2" />
            Filter
          </Button>
          <Button variant="outline" size="sm">
            <Download className="w-4 h-4 mr-2" />
            Export
          </Button>
        </div>
      </div>

      {/* Templates Grid */}
      <Tabs defaultValue="grid" className="w-full">
        <TabsList>
          <TabsTrigger value="grid">Grid View</TabsTrigger>
          <TabsTrigger value="list">List View</TabsTrigger>
          <TabsTrigger value="featured">Featured</TabsTrigger>
        </TabsList>

        <TabsContent value="grid" className="mt-6">
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {filteredTemplates.map((template) => (
              <TemplateCard
                key={template.id}
                template={template}
                onUse={(template) => {
                  setSelectedTemplate(template)
                  setShowCreateDialog(true)
                }}
                onPreview={(template) => setSelectedTemplate(template)}
              />
            ))}
          </div>
        </TabsContent>

        <TabsContent value="list" className="mt-6">
          <div className="space-y-4">
            {filteredTemplates.map((template) => (
              <TemplateListItem
                key={template.id}
                template={template}
                onUse={(template) => {
                  setSelectedTemplate(template)
                  setShowCreateDialog(true)
                }}
              />
            ))}
          </div>
        </TabsContent>

        <TabsContent value="featured" className="mt-6">
          <FeaturedTemplates 
            templates={templates.filter(t => t.is_public)}
            onUse={(template) => {
              setSelectedTemplate(template)
              setShowCreateDialog(true)
            }}
          />
        </TabsContent>
      </Tabs>

      {/* Create from Template Dialog */}
      {showCreateDialog && selectedTemplate && (
        <CreateFromTemplateDialog
          template={selectedTemplate}
          onClose={() => {
            setShowCreateDialog(false)
            setSelectedTemplate(null)
          }}
          onCreate={handleCreateFromTemplate}
        />
      )}

      {/* Empty State */}
      {filteredTemplates.length === 0 && !isLoading && (
        <Card>
          <CardContent className="text-center py-12">
            <BookOpen className="w-16 h-16 text-gray-400 mx-auto mb-4" />
            <h3 className="text-lg font-medium mb-2">No templates found</h3>
            <p className="text-gray-600 mb-6 max-w-md mx-auto">
              {searchQuery || selectedCategory !== 'all' 
                ? 'Try adjusting your search or filters to find templates.'
                : 'Get started by creating your first template or browse the community templates.'
              }
            </p>
            <div className="flex gap-2 justify-center">
              {(searchQuery || selectedCategory !== 'all') && (
                <Button variant="outline" onClick={() => {
                  setSearchQuery('')
                  setSelectedCategory('all')
                }}>
                  Clear Filters
                </Button>
              )}
              <Button>
                <Plus className="w-4 h-4 mr-2" />
                Create Template
              </Button>
            </div>
          </CardContent>
        </Card>
      )}
    </div>
  )
}

// Template Card Component
function TemplateCard({ 
  template, 
  onUse, 
  onPreview 
}: {
  template: RuleTemplate
  onUse: (template: RuleTemplate) => void
  onPreview: (template: RuleTemplate) => void
}) {
  const categoryConfig = Object.values(RULE_CATEGORIES).find(cat => cat.display_name === template.category_name)

  return (
    <Card className="hover:shadow-md transition-shadow">
      <CardHeader className="pb-3">
        <div className="flex items-start justify-between">
          <div className="space-y-2 flex-1">
            <div className="flex items-center gap-2">
              <CardTitle className="text-lg">{template.name}</CardTitle>
              {template.is_public && (
                <Star className="w-4 h-4 text-yellow-500 fill-current" />
              )}
            </div>
            <div className="flex items-center gap-2">
              <Badge variant={categoryConfig?.color === 'red' ? 'destructive' : 'default'}>
                {template.category_name}
              </Badge>
              <Badge variant="outline">
                {template.usage_count || 0} uses
              </Badge>
            </div>
          </div>
          
          <DropdownMenu>
            <DropdownMenuTrigger asChild>
              <Button variant="ghost" size="sm">
                <MoreHorizontal className="h-4 w-4" />
              </Button>
            </DropdownMenuTrigger>
            <DropdownMenuContent align="end">
              <DropdownMenuItem onClick={() => onPreview(template)}>
                <Eye className="w-4 h-4 mr-2" />
                Preview
              </DropdownMenuItem>
              <DropdownMenuItem onClick={() => onUse(template)}>
                <Play className="w-4 h-4 mr-2" />
                Use Template
              </DropdownMenuItem>
              <DropdownMenuItem>
                <Copy className="w-4 h-4 mr-2" />
                Duplicate
              </DropdownMenuItem>
              <DropdownMenuSeparator />
              <DropdownMenuItem>
                <Share className="w-4 h-4 mr-2" />
                Share
              </DropdownMenuItem>
            </DropdownMenuContent>
          </DropdownMenu>
        </div>
      </CardHeader>
      
      <CardContent>
        <p className="text-sm text-muted-foreground mb-4 line-clamp-3">
          {template.description}
        </p>
        
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-2 text-sm text-muted-foreground">
            <Clock className="w-4 h-4" />
            Updated {new Date(template.updated_at).toLocaleDateString()}
          </div>
          <Button size="sm" onClick={() => onUse(template)}>
            <Zap className="w-4 h-4 mr-2" />
            Use Template
          </Button>
        </div>
      </CardContent>
    </Card>
  )
}

// Template List Item
function TemplateListItem({ 
  template, 
  onUse 
}: {
  template: RuleTemplate
  onUse: (template: RuleTemplate) => void
}) {
  return (
    <Card>
      <CardContent className="p-6">
        <div className="flex items-center justify-between">
          <div className="flex-1 space-y-2">
            <div className="flex items-center gap-3">
              <h3 className="font-semibold text-lg">{template.name}</h3>
              {template.is_public && (
                <Star className="w-4 h-4 text-yellow-500 fill-current" />
              )}
              <Badge variant="outline">{template.category_name}</Badge>
              <Badge variant="secondary">{template.usage_count || 0} uses</Badge>
            </div>
            <p className="text-muted-foreground">{template.description}</p>
            <div className="flex items-center gap-4 text-sm text-muted-foreground">
              <span>Updated {new Date(template.updated_at).toLocaleDateString()}</span>
              <span>Created by {template.created_by}</span>
            </div>
          </div>
          <div className="flex items-center gap-2">
            <Button variant="outline" size="sm">
              <Eye className="w-4 h-4 mr-2" />
              Preview
            </Button>
            <Button size="sm" onClick={() => onUse(template)}>
              <Zap className="w-4 h-4 mr-2" />
              Use Template
            </Button>
          </div>
        </div>
      </CardContent>
    </Card>
  )
}

// Featured Templates Section
function FeaturedTemplates({ 
  templates, 
  onUse 
}: {
  templates: RuleTemplate[]
  onUse: (template: RuleTemplate) => void
}) {
  const featuredTemplates = templates.slice(0, 6) // Show top 6

  return (
    <div className="space-y-6">
      <Alert>
        <Star className="h-4 w-4" />
        <AlertDescription>
          These are the most popular and well-tested templates from our community.
        </AlertDescription>
      </Alert>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        {featuredTemplates.map((template) => (
          <Card key={template.id} className="border-yellow-200">
            <CardHeader>
              <div className="flex items-center justify-between">
                <CardTitle className="flex items-center gap-2">
                  <Star className="w-5 h-5 text-yellow-500 fill-current" />
                  {template.name}
                </CardTitle>
                <Badge variant="secondary">{template.usage_count} uses</Badge>
              </div>
            </CardHeader>
            <CardContent>
              <p className="text-muted-foreground mb-4">{template.description}</p>
              <Button className="w-full" onClick={() => onUse(template)}>
                <Zap className="w-4 h-4 mr-2" />
                Use This Template
              </Button>
            </CardContent>
          </Card>
        ))}
      </div>
    </div>
  )
}

// Create from Template Dialog
function CreateFromTemplateDialog({ 
  template, 
  onClose, 
  onCreate 
}: {
  template: RuleTemplate
  onClose: () => void
  onCreate: (template: RuleTemplate, ruleName: string, parameters: Record<string, unknown>) => void
}) {
  const [ruleName, setRuleName] = useState(`${template.name} - Copy`)
  const [parameters, setParameters] = useState(
    JSON.stringify(template.parameters_schema || {}, null, 2)
  )
  const [isCreating, setIsCreating] = useState(false)

  const handleCreate = async () => {
    if (!ruleName.trim()) {
      toast({
        variant: 'destructive',
        title: 'Error',
        description: 'Rule name is required'
      })
      return
    }

    let parsedParameters
    try {
      parsedParameters = JSON.parse(parameters)
    } catch {
      toast({
        variant: 'destructive',
        title: 'Error',
        description: 'Invalid JSON in parameters'
      })
      return
    }

    setIsCreating(true)
    try {
      await onCreate(template, ruleName, parsedParameters)
    } finally {
      setIsCreating(false)
    }
  }

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50">
      <Card className="w-full max-w-2xl max-h-[90vh] overflow-y-auto">
        <CardHeader>
          <CardTitle>Create Rule from Template</CardTitle>
          <p className="text-muted-foreground">
            Configure parameters for &quot;{template.name}&quot;
          </p>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="space-y-2">
            <Label htmlFor="ruleName">Rule Name</Label>
            <Input
              id="ruleName"
              value={ruleName}
              onChange={(e) => setRuleName(e.target.value)}
              placeholder="Enter rule name"
            />
          </div>

          <div className="space-y-2">
            <Label htmlFor="parameters">Parameters (JSON)</Label>
            <Textarea
              id="parameters"
              value={parameters}
              onChange={(e) => setParameters(e.target.value)}
              rows={8}
              className="font-mono"
              placeholder="Configure template parameters"
            />
            <p className="text-sm text-muted-foreground">
              Customize the template parameters for your specific use case
            </p>
          </div>

          <Alert>
            <Settings className="h-4 w-4" />
            <AlertDescription>
              <strong>Template:</strong> {template.description}
            </AlertDescription>
          </Alert>
        </CardContent>
        <div className="flex justify-end gap-2 p-6 pt-0">
          <Button variant="outline" onClick={onClose}>
            Cancel
          </Button>
          <Button onClick={handleCreate} disabled={isCreating}>
            {isCreating ? 'Creating...' : 'Create Rule'}
          </Button>
        </div>
      </Card>
    </div>
  )
}