"use client"

import { useState, useEffect } from 'react'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs'
import { Alert, AlertDescription } from '@/components/ui/alert'
import { 
  Save, 
  ArrowLeft, 
  Eye,
  AlertTriangle,
  CheckCircle,
  Info,
  Sparkles,
  Rocket,
  Wrench,
  Brain,
  Zap,
  Star,
  Wand2
} from 'lucide-react'
import { useRulesStore, useRulesFormState } from '@/lib/rules-store'
import { type CreateRuleRequest } from '@/lib/rules-types'
import { toast } from '@/lib/hooks/use-toast'
import { EnhancedSmartBuilder } from './enhanced-smart-builder'
import { SmartTemplates } from './smart-templates'
import { QuickRuleCreator } from './quick-rule-creator'
import { SimpleErrorBoundary } from '@/components/ui/error-boundary'

export function EnhancedRuleCreator() {
  const { 
    categories,
    selectedRule,
    createRule,
    updateRule,
    setCurrentSubView,
    setSelectedRule,
    setFormData,
    resetForm,
    isLoading
  } = useRulesStore()

  const {
    formData,
    validationErrors,
    currentStep,
    isValidating,
    validationResult,
    previewResult
  } = useRulesFormState()

  const [isSubmitting, setIsSubmitting] = useState(false)
  const [creationMode, setCreationMode] = useState<'quick' | 'template' | 'smart'>('quick')
  const isEditMode = !!selectedRule

  // Show loading spinner if categories are not loaded yet
  if (isLoading || categories.length === 0) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-slate-900"></div>
      </div>
    )
  }

  const handleCancel = () => {
    resetForm()
    setCurrentSubView('overview')
    setSelectedRule(null)
  }

  const handleSubmit = async () => {
    setIsSubmitting(true)
    try {
      if (isEditMode) {
        await updateRule(selectedRule.id, formData as CreateRuleRequest)
        toast({
          title: 'Success',
          description: 'Rule updated successfully'
        })
      } else {
        await createRule(formData as CreateRuleRequest)
        toast({
          title: 'Success', 
          description: 'Rule created successfully'
        })
      }
      setCurrentSubView('overview')
    } catch (error) {
      toast({
        variant: 'destructive',
        title: 'Error',
        description: `Failed to ${isEditMode ? 'update' : 'create'} rule`
      })
    } finally {
      setIsSubmitting(false)
    }
  }

  // Convert enhanced builder data to API format
  const convertEnhancedToRuleRequest = (enhancedData: any): CreateRuleRequest => {
    // Problem type to rule type mapping - CORRECTED to match backend rule types
    const problemToRuleType: Record<string, string> = {
      // Original problems - FIXED mappings
      'forgotten-items': 'STAGNANT_PALLETS',
      'traffic-jams': 'LOCATION_SPECIFIC_STAGNANT',
      'temperature-violations': 'TEMPERATURE_ZONE_MISMATCH',
      'incomplete-deliveries': 'UNCOORDINATED_LOTS',
      'storage-overflow': 'OVERCAPACITY',
      
      // New problems added in enhanced smart builder
      'scanner-errors': 'DATA_INTEGRITY',
      'lost-pallets': 'MISSING_LOCATION',
      'wrong-locations': 'INVALID_LOCATION',
      'wrong-product-areas': 'PRODUCT_INCOMPATIBILITY',
      'location-setup-errors': 'LOCATION_MAPPING_ERROR'
    }

    // Problem to category mapping - CORRECTED to align with backend three-pillar system
    const problemToCategory: Record<string, number> = {
      // FLOW_TIME category (ID: 1) - Highest priority
      'forgotten-items': 1,
      'traffic-jams': 1,
      'incomplete-deliveries': 1,
      
      // SPACE category (ID: 2) - High priority
      'storage-overflow': 2,
      'scanner-errors': 2,
      'lost-pallets': 2,
      'wrong-locations': 2,
      'location-setup-errors': 2,
      
      // PRODUCT category (ID: 3) - Medium priority
      'temperature-violations': 3,
      'wrong-product-areas': 3
    }

    // Convert sensitivity to priority
    const sensitivityToPriority: Record<number, 'VERY_HIGH' | 'HIGH' | 'MEDIUM' | 'LOW'> = {
      1: 'LOW',
      2: 'LOW', 
      3: 'MEDIUM',
      4: 'HIGH',
      5: 'VERY_HIGH'
    }

    const timeHours = enhancedData.selectedTimeframe === 'custom' 
      ? enhancedData.customHours 
      : getTimeOptionHours(enhancedData.selectedTimeframe)

    // Get the correct rule type
    const ruleType = problemToRuleType[enhancedData.problem] || 'STAGNANT_PALLETS'
    
    // Build conditions based on actual rule type requirements
    let conditions: Record<string, any> = {}
    
    // If advanced conditions are provided, use them as the base
    if (enhancedData.advancedConditions && Object.keys(enhancedData.advancedConditions).length > 0) {
      conditions = { ...enhancedData.advancedConditions }
    } else {
      // Otherwise, build conditions based on basic configuration
      switch (ruleType) {
      case 'STAGNANT_PALLETS':
        conditions.time_threshold_hours = timeHours
        if (enhancedData.areas && enhancedData.areas.length > 0) {
          conditions.location_types = enhancedData.areas.map((area: string) => area.toUpperCase())
        } else {
          conditions.location_types = ['RECEIVING', 'TRANSITIONAL']
        }
        break
        
      case 'LOCATION_SPECIFIC_STAGNANT':
        conditions.time_threshold_hours = timeHours
        // Smart location pattern selection based on problem type
        if (enhancedData.problem === 'traffic-jams') {
          conditions.location_pattern = 'AISLE*'
        } else {
          conditions.location_pattern = enhancedData.areas?.length > 0 ? 
            `${enhancedData.areas[0].toUpperCase()}*` : 'AISLE*'
        }
        break
        
      case 'TEMPERATURE_ZONE_MISMATCH':
        conditions.product_patterns = ['*FROZEN*', '*REFRIGERATED*']
        conditions.prohibited_zones = ['AMBIENT', 'GENERAL']
        conditions.time_threshold_minutes = Math.max(15, Math.min(120, timeHours * 60))
        break
        
      case 'UNCOORDINATED_LOTS':
        conditions.completion_threshold = 0.8
        conditions.location_types = ['RECEIVING']
        break
        
      case 'DATA_INTEGRITY':
        conditions.check_duplicate_scans = true
        conditions.check_impossible_locations = true
        break
        
      case 'MISSING_LOCATION':
        // No specific conditions - rule checks for null/empty locations
        break
        
      case 'INVALID_LOCATION':
        conditions.check_undefined_locations = true
        break
        
      case 'OVERCAPACITY':
        conditions.check_all_locations = true
        // Add safety buffer based on sensitivity
        if (enhancedData.sensitivity >= 4) {
          conditions.capacity_buffer = 10 // Alert at 90% capacity
        } else {
          conditions.capacity_buffer = 15 // Alert at 85% capacity
        }
        break
        
      case 'PRODUCT_INCOMPATIBILITY':
        // Use location allowed_products - no additional conditions needed
        break
        
      case 'LOCATION_MAPPING_ERROR':
        conditions.validate_location_types = true
        conditions.check_pattern_consistency = true
        break
        
      default:
        // Fallback for any unmapped rule types
        conditions.time_threshold_hours = timeHours
        console.warn(`Unmapped rule type: ${ruleType}, using default conditions`)
      }
    }
    
    return {
      name: enhancedData.name || 'AI-Generated Rule',
      description: `AI Smart Builder: ${enhancedData.name || 'Unnamed Rule'} - Monitors for warehouse issues using intelligent detection`,
      category_id: problemToCategory[enhancedData.problem] || 1,
      rule_type: ruleType,
      priority: sensitivityToPriority[enhancedData.sensitivity] || 'MEDIUM',
      conditions,
      parameters: {
        ai_enhanced: true,
        problem_type: enhancedData.problem,
        sensitivity_level: enhancedData.sensitivity || 3,
        timeframe_setting: enhancedData.selectedTimeframe,
        custom_hours: enhancedData.customHours,
        selected_areas: enhancedData.areas || [],
        smart_enhancements: enhancedData.selectedSuggestions || [],
        advanced_mode: enhancedData.advancedMode || false,
        advanced_conditions_used: enhancedData.advancedConditions && Object.keys(enhancedData.advancedConditions).length > 0,
        advanced_conditions_count: enhancedData.advancedConditions ? Object.keys(enhancedData.advancedConditions).length : 0,
        created_by: 'ai_smart_builder'
      },
      is_active: true
    }
  }

  const getTimeOptionHours = (timeframe: string): number => {
    const timeOptions: Record<string, number> = {
      'end-of-shift': 8,
      'next-morning': 16,
      'same-day': 24,
      'rush-processing': 4
    }
    return timeOptions[timeframe] || 8
  }

  const handleEnhancedRuleCreate = async (enhancedData: any) => {
    setIsSubmitting(true)
    try {
      const ruleRequest = convertEnhancedToRuleRequest(enhancedData)
      await createRule(ruleRequest)
      toast({
        title: 'AI Rule Created Successfully! 🎉',
        description: `Your smart rule "${enhancedData.name}" is now active and monitoring your warehouse.`
      })
      setCurrentSubView('overview')
    } catch (error) {
      toast({
        variant: 'destructive',
        title: 'Failed to Create Rule',
        description: 'There was an error creating your AI-powered rule. Please try again.'
      })
    } finally {
      setIsSubmitting(false)
    }
  }

  const handleTemplateSelect = async (template: any, configuration: any, ruleData?: any) => {
    setIsSubmitting(true)
    try {
      // If ruleData is provided, use it directly (from enhanced template)
      if (ruleData) {
        const ruleRequest = convertEnhancedToRuleRequest(ruleData)
        await createRule(ruleRequest)
      } else {
        // Fallback: convert template to rule request
        const templateRuleRequest = convertTemplateToRuleRequest(template, configuration)
        await createRule(templateRuleRequest)
      }
      
      toast({
        title: 'Template Rule Created! 🚀',
        description: `Your rule "${template.name}" is now active and monitoring your warehouse.`
      })
      setCurrentSubView('overview')
    } catch (error) {
      toast({
        variant: 'destructive',
        title: 'Failed to Create Template Rule',
        description: 'There was an error creating your template-based rule. Please try again.'
      })
    } finally {
      setIsSubmitting(false)
    }
  }

  const convertTemplateToRuleRequest = (template: any, configuration: any): CreateRuleRequest => {
    // Map template categories to rule categories - CORRECTED alignment
    const categoryMap: Record<string, number> = {
      'common': 1, // Most common templates go to FLOW_TIME for high priority
      'advanced': 2, // Advanced templates typically deal with SPACE management
      'industry': 3  // Industry-specific templates often involve PRODUCT compliance
    }
    
    // Merge template conditions with user configuration
    const conditions = { ...template.conditions, ...configuration }
    
    return {
      name: template.name,
      description: `Template: ${template.description}`,
      category_id: categoryMap[template.category] || 1,
      rule_type: template.ruleType || 'STAGNANT_PALLETS',
      conditions,
      parameters: {
        template_based: true,
        template_id: template.id,
        difficulty: template.difficulty,
        estimated_time: template.estimatedTime
      },
      priority: template.difficulty === 'advanced' ? 'HIGH' : 'MEDIUM',
      is_active: true
    }
  }

  // Handle edit mode - simplified for now, you can enhance later
  if (isEditMode) {
    return (
      <div className="space-y-6">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-3">
            <h2 className="text-2xl font-bold">Edit Rule: {selectedRule.name}</h2>
          </div>
          <div className="flex gap-2">
            <Button variant="outline" onClick={handleCancel}>
              <ArrowLeft className="w-4 h-4 mr-2" />
              Cancel
            </Button>
            <Button onClick={handleSubmit} disabled={isSubmitting}>
              <Save className="w-4 h-4 mr-2" />
              {isSubmitting ? 'Saving...' : 'Update Rule'}
            </Button>
          </div>
        </div>
        
        <Alert className="border-blue-200 bg-blue-50">
          <Info className="h-4 w-4 text-blue-600" />
          <AlertDescription>
            Edit mode is currently using the standard form. AI-enhanced editing will be available in a future update.
          </AlertDescription>
        </Alert>
        
        {/* You can add the standard form here or redirect to overview */}
        <div className="text-center py-8">
          <Button onClick={() => setCurrentSubView('overview')}>
            Back to Rules Overview
          </Button>
        </div>
      </div>
    )
  }

  return (
    <div className="space-y-6">
      {/* Enhanced Header with Gradient and Branding */}
      <div className="text-center space-y-4">
        <div className="relative">
          <div className="absolute inset-0 bg-gradient-to-r from-blue-600 via-purple-600 to-indigo-600 rounded-lg blur-xl opacity-20"></div>
          <div className="relative bg-white border border-gray-200 rounded-lg p-6">
            <div className="flex items-center justify-center gap-3 mb-3">
              <div className="p-2 rounded-lg bg-gradient-to-r from-blue-100 to-purple-100">
                <Brain className="w-6 h-6 text-blue-600" />
              </div>
              <h2 className="text-3xl font-bold bg-gradient-to-r from-blue-600 to-purple-600 bg-clip-text text-transparent">
                Create a Smart Rule
              </h2>
              <Badge className="bg-gradient-to-r from-blue-500 to-purple-500 text-white border-0">
                <Sparkles className="w-3 h-3 mr-1" />
                AI-Powered
              </Badge>
            </div>
            <p className="text-muted-foreground text-lg">
              Choose your approach: Quick setup, proven templates, or AI-powered smart builder
            </p>
          </div>
        </div>

        {/* Enhanced Mode Selection */}
        <Tabs value={creationMode} onValueChange={(value: any) => setCreationMode(value)} className="w-full">
          <TabsList className="grid w-full max-w-3xl mx-auto grid-cols-3 h-14">
            <TabsTrigger value="quick" className="flex items-center gap-2 p-3">
              <Rocket className="w-4 h-4" />
              <div className="text-left">
                <div className="font-medium">Quick Setup</div>
                <div className="text-xs text-muted-foreground">2 min</div>
              </div>
            </TabsTrigger>
            <TabsTrigger value="template" className="flex items-center gap-2 p-3">
              <Star className="w-4 h-4" />
              <div className="text-left">
                <div className="font-medium">Use Template</div>
                <div className="text-xs text-muted-foreground">Proven</div>
              </div>
            </TabsTrigger>
            <TabsTrigger value="smart" className="flex items-center gap-2 p-3 relative">
              <div className="absolute -top-1 -right-1">
                <Badge className="bg-gradient-to-r from-blue-500 to-purple-500 text-white text-xs px-1 py-0 h-4">
                  NEW
                </Badge>
              </div>
              <div className="p-1 rounded bg-gradient-to-r from-blue-100 to-purple-100">
                <Brain className="w-4 h-4 text-blue-600" />
              </div>
              <div className="text-left">
                <div className="font-medium">AI Smart Builder</div>
                <div className="text-xs text-muted-foreground">Intelligent</div>
              </div>
            </TabsTrigger>
          </TabsList>

          {/* Enhanced Tab Content */}
          <div className="max-w-6xl mx-auto">
            <TabsContent value="quick" className="space-y-4">
              <Alert className="border-green-200 bg-green-50">
                <Rocket className="h-4 w-4 text-green-600" />
                <AlertDescription>
                  <strong>Perfect for beginners.</strong> Answer simple questions to create common warehouse rules in under 2 minutes.
                </AlertDescription>
              </Alert>
              <QuickRuleCreator 
                categories={categories}
                onSave={async (ruleData) => {
                  setIsSubmitting(true)
                  try {
                    await createRule(ruleData)
                    toast({
                      title: 'Rule Created Successfully!',
                      description: 'Your quick rule is now active'
                    })
                    setCurrentSubView('overview')
                  } catch {
                    toast({
                      variant: 'destructive',
                      title: 'Error',
                      description: 'Failed to create rule'
                    })
                  } finally {
                    setIsSubmitting(false)
                  }
                }}
                onCancel={handleCancel}
                isSubmitting={isSubmitting}
              />
            </TabsContent>

            <TabsContent value="template" className="space-y-4">
              <Alert className="border-blue-200 bg-blue-50">
                <Star className="h-4 w-4 text-blue-600" />
                <AlertDescription>
                  <strong>Great for common scenarios.</strong> Start with battle-tested templates and customize for your needs.
                </AlertDescription>
              </Alert>
              <SmartTemplates 
                onTemplateSelect={handleTemplateSelect}
                onCancel={handleCancel}
                categories={categories}
              />
            </TabsContent>

            <TabsContent value="smart" className="space-y-4">
              {/* Enhanced Smart Builder Intro */}
              <div className="relative">
                <div className="absolute inset-0 bg-gradient-to-r from-blue-50 via-purple-50 to-indigo-50 rounded-lg"></div>
                <Alert className="relative border-2 border-transparent bg-gradient-to-r from-blue-100 via-purple-100 to-indigo-100">
                  <div className="flex items-center gap-3">
                    <div className="p-2 rounded-lg bg-gradient-to-r from-blue-200 to-purple-200">
                      <Brain className="h-5 w-5 text-blue-700" />
                    </div>
                    <div className="flex-1">
                      <AlertDescription className="text-base">
                        <strong className="text-blue-800">AI-Powered Smart Builder</strong>
                        <div className="text-sm text-blue-700 mt-1">
                          Start with real warehouse problems, get intelligent suggestions, and see performance predictions
                        </div>
                      </AlertDescription>
                    </div>
                    <div className="flex gap-2">
                      <Badge variant="outline" className="bg-blue-50 text-blue-700 border-blue-300">
                        <Sparkles className="w-3 h-3 mr-1" />
                        Smart Suggestions
                      </Badge>
                      <Badge variant="outline" className="bg-purple-50 text-purple-700 border-purple-300">
                        <Zap className="w-3 h-3 mr-1" />
                        Performance Predictions
                      </Badge>
                    </div>
                  </div>
                </Alert>
              </div>

              {/* AI-Powered Builder */}
              <SimpleErrorBoundary message="Failed to load AI Smart Builder">
                <EnhancedSmartBuilder 
                  onRuleCreate={handleEnhancedRuleCreate}
                  onCancel={handleCancel}
                />
              </SimpleErrorBoundary>
            </TabsContent>
          </div>
        </Tabs>
      </div>
    </div>
  )
}