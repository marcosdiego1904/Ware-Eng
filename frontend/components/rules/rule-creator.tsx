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
import { Separator } from '@/components/ui/separator'
import { 
  Save, 
  ArrowLeft, 
  ArrowRight, 
  Eye,
  Settings,
  AlertTriangle,
  CheckCircle,
  Info,
  Zap,
  RotateCcw,
  Sparkles,
  Rocket,
  Wrench
} from 'lucide-react'
import { useRulesStore, useRulesFormState } from '@/lib/rules-store'
import { PRIORITY_LEVELS, RULE_TYPES, type RuleFormData, type CreateRuleRequest } from '@/lib/rules-types'
import { toast } from '@/lib/hooks/use-toast'
import { VisualRuleBuilder } from './visual-rule-builder'
import { SmartTemplates } from './smart-templates'
import { QuickRuleCreator } from './quick-rule-creator'
import { ContextHelp, SmartHelpSuggestions } from './context-help'
import { SimpleErrorBoundary } from '@/components/ui/error-boundary'

export function RuleCreator() {
  const { 
    categories,
    selectedRule,
    createRule,
    updateRule,
    validateRule,
    previewRule,
    setCurrentSubView,
    setSelectedRule,
    setFormData,
    setCurrentStep,
    resetForm,
    validateForm,
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
  const [creationMode, setCreationMode] = useState<'quick' | 'template' | 'advanced'>('quick')
  const isEditMode = !!selectedRule

  // Show loading spinner if categories are not loaded yet
  if (isLoading || categories.length === 0) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-slate-900"></div>
      </div>
    )
  }

  const [isFormInitialized, setIsFormInitialized] = useState(false);

  // Initialize form for editing
  useEffect(() => {
    if (selectedRule && isEditMode) {
      try {
        console.log('Initializing form for editing rule:', selectedRule)
        
        const conditions = selectedRule.conditions || {}
        const parameters = selectedRule.parameters || {}
        
        if (!selectedRule.name || !selectedRule.rule_type || !selectedRule.category_id) {
          console.error('Selected rule is missing required fields:', selectedRule)
          throw new Error('Invalid rule data: missing required fields')
        }
        
        setFormData({
          name: selectedRule.name,
          description: selectedRule.description || '',
          category_id: selectedRule.category_id,
          rule_type: selectedRule.rule_type,
          conditions: conditions,
          parameters: parameters,
          priority: selectedRule.priority || 'MEDIUM',
          is_active: selectedRule.is_active ?? true
        })
        
        setIsFormInitialized(true);
        console.log('Form data set successfully for edit mode')
      } catch (error) {
        console.error('Error initializing form for editing:', error)
        toast({
          variant: 'destructive',
          title: 'Error',
          description: 'Failed to load rule for editing. Please try again.'
        })
        setCurrentSubView('overview')
        setSelectedRule(null)
      }
    } else {
      setIsFormInitialized(false);
      if (!isEditMode) {
        resetForm();
      }
    }
  }, [selectedRule, isEditMode, setFormData, resetForm])

  const steps = [
    { id: 'basic', label: 'Basic Info', icon: Info },
    { id: 'conditions', label: 'Conditions', icon: Settings },
    { id: 'parameters', label: 'Parameters', icon: Zap },
    { id: 'preview', label: 'Preview', icon: Eye }
  ]

  const currentStepIndex = steps.findIndex(step => step.id === currentStep)

  const handleNext = () => {
    if (currentStepIndex < steps.length - 1) {
      const nextStep = steps[currentStepIndex + 1]
      setCurrentStep(nextStep.id as 'basic' | 'conditions' | 'parameters' | 'preview')
    }
  }

  const handlePrevious = () => {
    if (currentStepIndex > 0) {
      const prevStep = steps[currentStepIndex - 1]
      setCurrentStep(prevStep.id as 'basic' | 'conditions' | 'parameters' | 'preview')
    }
  }

  const handleValidate = async () => {
    try {
      await validateRule(formData)
      toast({
        title: 'Validation Complete',
        description: 'Rule conditions are valid'
      })
    } catch {
      toast({
        variant: 'destructive',
        title: 'Validation Failed',
        description: 'Please check your rule conditions'
      })
    }
  }

  const handlePreview = async () => {
    try {
      await previewRule(formData)
      setCurrentStep('preview')
      toast({
        title: 'Preview Generated',
        description: 'Check the preview tab to see expected results'
      })
    } catch {
      toast({
        variant: 'destructive',
        title: 'Preview Failed',
        description: 'Unable to generate preview'
      })
    }
  }

  const handleSubmit = async () => {
    if (!validateForm()) {
      toast({
        variant: 'destructive',
        title: 'Validation Error',
        description: 'Please fix the form errors before submitting'
      })
      return
    }

    setIsSubmitting(true)
    try {
      const ruleData: CreateRuleRequest = {
        name: formData.name!,
        description: formData.description!,
        category_id: formData.category_id!,
        rule_type: formData.rule_type!,
        conditions: formData.conditions || {},
        parameters: formData.parameters || {},
        priority: formData.priority!,
        is_active: formData.is_active ?? true
      }

      console.log('Submitting rule data:', ruleData)

      if (isEditMode && selectedRule) {
        await updateRule(selectedRule.id, ruleData)
        toast({
          title: 'Success',
          description: 'Rule updated successfully'
        })
      } else {
        await createRule(ruleData)
        toast({
          title: 'Success',
          description: 'Rule created successfully'
        })
      }

      setCurrentSubView('overview')
      setSelectedRule(null)
      resetForm()
    } catch (error) {
      console.error('Rule submission error:', error)
      toast({
        variant: 'destructive',
        title: 'Error',
        description: `Failed to ${isEditMode ? 'update' : 'create'} rule: ${error instanceof Error ? error.message : 'Unknown error'}`
      })
    } finally {
      setIsSubmitting(false)
    }
  }

  const handleCancel = () => {
    setCurrentSubView('overview')
    setSelectedRule(null)
    resetForm()
  }

  // Handle template selection
  const handleTemplateSelect = async (template: any, configuration: Record<string, any>) => {
    try {
      const categoryId = categories.find(c => c.display_name.includes(template.category.replace('_', ' ')))?.id || 1
      
      const ruleData: CreateRuleRequest = {
        name: configuration.name || template.name,
        description: configuration.description || template.description,
        category_id: categoryId,
        rule_type: template.conditions.rule_type || 'STAGNANT_PALLETS',
        conditions: { ...template.conditions, ...configuration },
        parameters: template.parameters || {},
        priority: 'HIGH',
        is_active: true
      }

      await createRule(ruleData)
      toast({
        title: 'Success',
        description: 'Rule created from template successfully'
      })
      setCurrentSubView('overview')
      setSelectedRule(null)
      resetForm()
    } catch {
      toast({
        variant: 'destructive',
        title: 'Error',
        description: 'Failed to create rule from template'
      })
    }
  }

  // If editing, show advanced mode
  if (isEditMode) {
    if (!selectedRule) {
      console.error('Edit mode is true but selectedRule is null')
      return (
        <div className="p-4 text-center">
          <p className="text-red-600">Error: No rule selected for editing</p>
          <Button onClick={() => setCurrentSubView('overview')} className="mt-2">
            Back to Overview
          </Button>
        </div>
      )
    }

    // Check if form data is synced with the selected rule to prevent rendering with stale state
    if (!isFormInitialized) {
      return (
        <div className="flex items-center justify-center h-64">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-slate-900" />
          <p className="ml-4 text-muted-foreground">Loading rule editor...</p>
        </div>
      );
    }

    const isDefaultRule = selectedRule.is_default
    
    try {
      return (
        <div className="space-y-6">
          {/* Header */}
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-3">
              <div>
                <div className="flex items-center gap-2 mb-1">
                  <h2 className="text-2xl font-bold">{isDefaultRule ? 'View/Edit' : 'Edit'} Rule: {selectedRule.name || 'Unnamed Rule'}</h2>
                  {isDefaultRule && (
                    <div className="flex items-center gap-1">
                      <div className="w-2 h-2 rounded-full bg-blue-500" />
                      <Badge variant="outline" className="border-blue-300 text-blue-700 bg-blue-50">
                        System Rule
                      </Badge>
                    </div>
                  )}
                </div>
                <p className="text-muted-foreground">
                  {isDefaultRule 
                    ? 'System default rule - some fields may be protected' 
                    : 'Modify your custom warehouse rule'
                  }
                </p>
              </div>
            </div>
            <div className="flex gap-2">
              <Button variant="outline" onClick={handleCancel}>
                <ArrowLeft className="w-4 h-4 mr-2" />
                Cancel
              </Button>
              <Button onClick={handleSubmit} disabled={isSubmitting}>
                <Save className="w-4 h-4 mr-2" />
                {isSubmitting ? 'Saving...' : (isDefaultRule ? 'Update Settings' : 'Update Rule')}
              </Button>
            </div>
          </div>

          {/* Warning for default rules */}
          {isDefaultRule && (
            <Alert className="border-blue-200 bg-blue-50">
              <Info className="h-4 w-4 text-blue-600" />
              <AlertDescription>
                <strong>System Default Rule:</strong> This is a protected system rule. You can modify its priority, activation status, and some parameters, but core conditions cannot be changed. Consider duplicating this rule to create a fully customizable version.
              </AlertDescription>
            </Alert>
          )}

          {/* Advanced form for editing */}
          <SimpleErrorBoundary message="Failed to load rule editing form">
            <AdvancedRuleCreator 
              formData={formData}
              validationErrors={validationErrors}
              categories={categories}
              onFormChange={setFormData}
              onSubmit={handleSubmit}
              onCancel={handleCancel}
              onValidate={handleValidate}
              onPreview={handlePreview}
              isSubmitting={isSubmitting}
              isValidating={isValidating}
              validationResult={validationResult}
              previewResult={previewResult}
              isEditMode={isEditMode}
              isDefaultRule={isDefaultRule}
            />
          </SimpleErrorBoundary>
        </div>
      )
    } catch (error) {
      console.error('Error rendering edit mode:', error)
      return (
        <div className="p-4 text-center">
          <p className="text-red-600">Error rendering edit form. Please try again.</p>
          <Button onClick={() => {
            setCurrentSubView('overview')
            setSelectedRule(null)
          }} className="mt-2">
            Back to Overview
          </Button>
        </div>
      )
    }
  }

  return (
    <div className="space-y-6">
      {/* Header with Mode Selection */}
      <div className="text-center space-y-4">
        <div>
          <h2 className="text-3xl font-bold">Create a New Rule</h2>
          <p className="text-muted-foreground text-lg">
            Choose the best way to create your warehouse rule
          </p>
        </div>

        {/* Mode Selection Tabs */}
        <Tabs value={creationMode} onValueChange={(value: any) => setCreationMode(value)} className="w-full">
          <TabsList className="grid w-full max-w-2xl mx-auto grid-cols-3">
            <TabsTrigger value="quick" className="flex items-center gap-2">
              <Rocket className="w-4 h-4" />
              Quick Setup
            </TabsTrigger>
            <TabsTrigger value="template" className="flex items-center gap-2">
              <Sparkles className="w-4 h-4" />
              Use Template
            </TabsTrigger>
            <TabsTrigger value="advanced" className="flex items-center gap-2">
              <Wrench className="w-4 h-4" />
              Advanced Builder
            </TabsTrigger>
          </TabsList>

          {/* Mode Descriptions */}
          <div className="max-w-4xl mx-auto">
            <TabsContent value="quick" className="space-y-4">
              <Alert className="border-green-200 bg-green-50">
                <Rocket className="h-4 w-4 text-green-600" />
                <AlertDescription>
                  <strong>Recommended for beginners.</strong> Answer a few simple questions to create common warehouse rules in under 2 minutes.
                </AlertDescription>
              </Alert>
              <QuickRuleCreator 
                categories={categories}
                onSave={async (ruleData) => {
                  setIsSubmitting(true)
                  try {
                    await createRule(ruleData)
                    toast({
                      title: 'Success',
                      description: 'Rule created successfully'
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
                onPreview={handlePreview}
                isSubmitting={isSubmitting}
              />
            </TabsContent>

            <TabsContent value="template" className="space-y-4">
              <Alert className="border-blue-200 bg-blue-50">
                <Sparkles className="h-4 w-4 text-blue-600" />
                <AlertDescription>
                  <strong>Great for common scenarios.</strong> Start with a proven template and customize it for your specific needs.
                </AlertDescription>
              </Alert>
              <SmartTemplates 
                onTemplateSelect={handleTemplateSelect}
                onCancel={handleCancel}
                categories={categories}
              />
            </TabsContent>

            <TabsContent value="advanced" className="space-y-4">
              <Alert className="border-purple-200 bg-purple-50">
                <Wrench className="h-4 w-4 text-purple-600" />
                <AlertDescription>
                  <strong>For experienced users.</strong> Full control over rule conditions and parameters with visual tools.
                </AlertDescription>
              </Alert>
              <AdvancedRuleCreator 
                formData={formData}
                validationErrors={validationErrors}
                categories={categories}
                onFormChange={setFormData}
                onSubmit={handleSubmit}
                onCancel={handleCancel}
                onValidate={handleValidate}
                onPreview={handlePreview}
                isSubmitting={isSubmitting}
                isValidating={isValidating}
                validationResult={validationResult}
                previewResult={previewResult}
                isEditMode={false}
                isDefaultRule={false}
              />
            </TabsContent>
          </div>
        </Tabs>
      </div>
    </div>
  )
}

// Advanced Rule Creator Component
function AdvancedRuleCreator({
  formData,
  validationErrors,
  categories,
  onFormChange,
  onSubmit,
  onCancel,
  onValidate,
  onPreview,
  isSubmitting,
  isValidating,
  validationResult,
  previewResult,
  isEditMode = false,
  isDefaultRule = false
}: {
  formData: Partial<RuleFormData>
  validationErrors: Record<string, string>
  categories: Array<{ id: number; display_name: string }>
  onFormChange: (data: Partial<RuleFormData>) => void
  onSubmit: () => void
  onCancel: () => void
  onValidate: () => void
  onPreview: () => void
  isSubmitting: boolean
  isValidating: boolean
  validationResult: { success: boolean; error?: string } | null
  previewResult: any
  isEditMode?: boolean
  isDefaultRule?: boolean
}) {
  return (
    <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
      {/* Main Form */}
      <div className="lg:col-span-2 space-y-6">
        {/* Basic Info */}
        <Card>
          <CardHeader>
            <CardTitle>Basic Information</CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div className="space-y-2">
                <Label htmlFor="name">Rule Name *</Label>
                <Input
                  id="name"
                  placeholder="Enter rule name"
                  value={formData.name || ''}
                  onChange={(e) => onFormChange({ name: e.target.value })}
                  className={validationErrors.name ? 'border-red-500' : ''}
                  disabled={isDefaultRule}
                />
                {isDefaultRule && (
                  <p className="text-xs text-blue-600">System rule names cannot be modified</p>
                )}
                {validationErrors.name && (
                  <p className="text-sm text-red-500">{validationErrors.name}</p>
                )}
              </div>

              <div className="space-y-2">
                <Label htmlFor="priority">Priority *</Label>
                <Select value={formData.priority} onValueChange={(value) => onFormChange({ priority: value as any })}>
                  <SelectTrigger className={validationErrors.priority ? 'border-red-500' : ''}>
                    <SelectValue placeholder="Select priority" />
                  </SelectTrigger>
                  <SelectContent>
                    {Object.entries(PRIORITY_LEVELS).map(([key, priority]) => (
                      <SelectItem key={key} value={key}>
                        <div className="flex items-center gap-2">
                          <Badge variant={priority.color as any}>{priority.label}</Badge>
                        </div>
                      </SelectItem>
                    ))}
                  </SelectContent>
                </Select>
                {validationErrors.priority && (
                  <p className="text-sm text-red-500">{validationErrors.priority}</p>
                )}
              </div>
            </div>

            <div className="space-y-2">
              <Label htmlFor="description">Description *</Label>
              <Textarea
                id="description"
                placeholder="Describe what this rule detects"
                value={formData.description || ''}
                onChange={(e) => onFormChange({ description: e.target.value })}
                className={validationErrors.description ? 'border-red-500' : ''}
                rows={3}
                disabled={isDefaultRule}
              />
              {isDefaultRule && (
                <p className="text-xs text-blue-600">System rule descriptions cannot be modified</p>
              )}
              {validationErrors.description && (
                <p className="text-sm text-red-500">{validationErrors.description}</p>
              )}
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div className="space-y-2">
                <Label htmlFor="category">Category *</Label>
                <Select 
                  value={formData.category_id?.toString()} 
                  onValueChange={(value) => onFormChange({ category_id: parseInt(value) })}
                  disabled={isDefaultRule}
                >
                  <SelectTrigger className={validationErrors.category_id ? 'border-red-500' : ''}>
                    <SelectValue placeholder="Select category" />
                  </SelectTrigger>
                  <SelectContent>
                    {categories.map((category) => (
                      <SelectItem key={category.id} value={category.id.toString()}>
                        {category.display_name}
                      </SelectItem>
                    ))}
                  </SelectContent>
                </Select>
                {isDefaultRule && (
                  <p className="text-xs text-blue-600">System rule category cannot be changed</p>
                )}
                {validationErrors.category_id && (
                  <p className="text-sm text-red-500">{validationErrors.category_id}</p>
                )}
              </div>

              <div className="space-y-2">
                <Label htmlFor="rule_type">Rule Type *</Label>
                <Select 
                  value={formData.rule_type} 
                  onValueChange={(value) => onFormChange({ rule_type: value })}
                  disabled={isDefaultRule}
                >
                  <SelectTrigger className={validationErrors.rule_type ? 'border-red-500' : ''}>
                    <SelectValue placeholder="Select rule type" />
                  </SelectTrigger>
                  <SelectContent>
                    {Object.entries(RULE_TYPES).map(([key, type]) => (
                      <SelectItem key={key} value={key}>
                        <div className="space-y-1">
                          <div className="font-medium">{type.label}</div>
                          <div className="text-sm text-muted-foreground">{type.description}</div>
                        </div>
                      </SelectItem>
                    ))}
                  </SelectContent>
                </Select>
                {isDefaultRule && (
                  <p className="text-xs text-blue-600">System rule type cannot be changed</p>
                )}
                {validationErrors.rule_type && (
                  <p className="text-sm text-red-500">{validationErrors.rule_type}</p>
                )}
              </div>
            </div>
          </CardContent>
        </Card>

        {/* Visual Rule Builder */}
        {isDefaultRule ? (
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Settings className="w-5 h-5" />
                Rule Conditions (Read-Only)
              </CardTitle>
            </CardHeader>
            <CardContent>
              <Alert className="border-blue-200 bg-blue-50 mb-4">
                <Info className="h-4 w-4 text-blue-600" />
                <AlertDescription>
                  System rule conditions are protected and cannot be modified. The logic is maintained by the system to ensure consistency.
                </AlertDescription>
              </Alert>
              <div className="p-4 bg-gray-50 rounded-lg">
                <pre className="text-sm text-gray-700 overflow-auto">
                  {JSON.stringify(formData.conditions || {}, null, 2)}
                </pre>
              </div>
            </CardContent>
          </Card>
        ) : (
          <VisualRuleBuilder
            initialConditions={formData.conditions || {}}
            ruleType={formData.rule_type}
            onConditionsChange={(conditions) => onFormChange({ conditions })}
            onValidate={onValidate}
            isValidating={isValidating}
            validationResult={validationResult}
          />
        )}

        {/* Preview Results */}
        {previewResult && (
          <Card>
            <CardHeader>
              <CardTitle>Preview Results</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div className="text-center">
                  <div className="text-2xl font-bold text-blue-600">
                    {previewResult.preview_results?.anomalies_found || 0}
                  </div>
                  <div className="text-sm text-muted-foreground">Anomalies Found</div>
                </div>
                <div className="text-center">
                  <div className="text-2xl font-bold text-green-600">
                    {previewResult.preview_results?.execution_time_ms || 0}ms
                  </div>
                  <div className="text-sm text-muted-foreground">Execution Time</div>
                </div>
              </div>
            </CardContent>
          </Card>
        )}

        {/* Action Buttons */}
        <div className="flex justify-between">
          <Button variant="outline" onClick={onCancel}>
            Cancel
          </Button>
          <div className="flex gap-3">
            <Button variant="outline" onClick={onPreview} disabled={isValidating}>
              <Eye className="w-4 h-4 mr-2" />
              {isValidating ? 'Generating...' : 'Preview'}
            </Button>
            <Button onClick={onSubmit} disabled={isSubmitting}>
              <Save className="w-4 h-4 mr-2" />
              {isSubmitting ? 'Creating...' : 'Create Rule'}
            </Button>
          </div>
        </div>
      </div>

      {/* Sidebar */}
      <div className="space-y-4">
        <RuleInfoSidebar formData={formData} isDefaultRule={isDefaultRule} />
        {!isDefaultRule && (
          <>
            <SmartHelpSuggestions 
              ruleType={formData.rule_type}
              currentFields={formData.conditions}
            />
            <ContextHelp 
              context="rule_type"
              ruleType={formData.rule_type}
            />
          </>
        )}
        {isDefaultRule && (
          <Card>
            <CardHeader>
              <CardTitle className="text-base flex items-center gap-2">
                <Info className="w-4 h-4 text-blue-600" />
                Default Rule Options
              </CardTitle>
            </CardHeader>
            <CardContent className="space-y-3">
              <p className="text-sm text-muted-foreground">
                As a system default rule, you can only modify:
              </p>
              <ul className="text-sm space-y-1 ml-4">
                <li className="flex items-center gap-2">
                  <CheckCircle className="w-3 h-3 text-green-600" />
                  Priority level
                </li>
                <li className="flex items-center gap-2">
                  <CheckCircle className="w-3 h-3 text-green-600" />
                  Active/Inactive status
                </li>
                <li className="flex items-center gap-2">
                  <CheckCircle className="w-3 h-3 text-green-600" />
                  Some parameters
                </li>
              </ul>
              <Separator />
              <p className="text-xs text-blue-600">
                Want full control? Duplicate this rule to create a custom version.
              </p>
            </CardContent>
          </Card>
        )}
      </div>
    </div>
  )
}


// Sidebar Components
function RuleInfoSidebar({ formData, isDefaultRule = false }: { formData: Partial<RuleFormData>; isDefaultRule?: boolean }) {
  return (
    <Card className={isDefaultRule ? 'border-l-4 border-l-blue-500 bg-gradient-to-r from-blue-50/50 to-transparent' : ''}>
      <CardHeader>
        <CardTitle className="text-base flex items-center gap-2">
          Rule Summary
          {isDefaultRule && (
            <Badge variant="outline" className="border-blue-300 text-blue-700 bg-blue-50 text-xs">
              System
            </Badge>
          )}
        </CardTitle>
      </CardHeader>
      <CardContent className="space-y-3">
        <div>
          <Label className="text-sm font-medium">Name</Label>
          <p className={`text-sm ${isDefaultRule ? 'text-blue-700 font-medium' : 'text-muted-foreground'}`}>
            {formData.name || 'Untitled Rule'}
          </p>
        </div>
        
        <Separator />
        
        <div>
          <Label className="text-sm font-medium">Priority</Label>
          <div className="mt-1">
            {formData.priority ? (
              <Badge variant={PRIORITY_LEVELS[formData.priority].color as 'default' | 'secondary' | 'destructive' | 'outline'}>
                {PRIORITY_LEVELS[formData.priority].label}
              </Badge>
            ) : (
              <p className="text-sm text-muted-foreground">Not set</p>
            )}
          </div>
        </div>
        
        <div>
          <Label className="text-sm font-medium">Type</Label>
          <p className={`text-sm ${isDefaultRule ? 'text-blue-700' : 'text-muted-foreground'}`}>
            {formData.rule_type ? 
              RULE_TYPES[formData.rule_type]?.label || formData.rule_type :
              'Not selected'
            }
          </p>
        </div>
        
        <div>
          <Label className="text-sm font-medium">Status</Label>
          <Badge variant={formData.is_active ? 'default' : 'secondary'}>
            {formData.is_active ? 'Active' : 'Inactive'}
          </Badge>
        </div>
        
        {isDefaultRule && (
          <>
            <Separator />
            <div className="flex items-center gap-2 text-xs text-blue-600">
              <div className="w-2 h-2 rounded-full bg-blue-500" />
              <span>Protected System Rule</span>
            </div>
          </>
        )}
      </CardContent>
    </Card>
  )
}

function QuickActionsSidebar({ 
  onValidate, 
  onPreview, 
  onReset, 
  isValidating 
}: {
  onValidate: () => void
  onPreview: () => void
  onReset: () => void
  isValidating: boolean
}) {
  return (
    <Card>
      <CardHeader>
        <CardTitle className="text-base">Quick Actions</CardTitle>
      </CardHeader>
      <CardContent className="space-y-3">
        <Button 
          variant="outline" 
          size="sm" 
          className="w-full" 
          onClick={onValidate}
          disabled={isValidating}
        >
          <CheckCircle className="w-4 h-4 mr-2" />
          Validate Rule
        </Button>
        
        <Button 
          variant="outline" 
          size="sm" 
          className="w-full" 
          onClick={onPreview}
          disabled={isValidating}
        >
          <Eye className="w-4 h-4 mr-2" />
          Generate Preview
        </Button>
        
        <Button 
          variant="outline" 
          size="sm" 
          className="w-full" 
          onClick={onReset}
        >
          <RotateCcw className="w-4 h-4 mr-2" />
          Reset Form
        </Button>
      </CardContent>
    </Card>
  )
}