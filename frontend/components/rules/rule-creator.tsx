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
import { Tabs, TabsContent } from '@/components/ui/tabs'
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
  RotateCcw
} from 'lucide-react'
import { useRulesStore, useRulesFormState } from '@/lib/rules-store'
import { PRIORITY_LEVELS, RULE_TYPES, type RuleFormData, type CreateRuleRequest } from '@/lib/rules-types'
import { toast } from '@/lib/hooks/use-toast'

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
    validateForm
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
  const isEditMode = !!selectedRule

  // Initialize form for editing
  useEffect(() => {
    if (selectedRule && isEditMode) {
      setFormData({
        name: selectedRule.name,
        description: selectedRule.description,
        category_id: selectedRule.category_id,
        rule_type: selectedRule.rule_type,
        conditions: selectedRule.conditions,
        parameters: selectedRule.parameters,
        priority: selectedRule.priority,
        is_active: selectedRule.is_active
      })
    } else {
      resetForm()
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
        conditions: formData.conditions!,
        parameters: formData.parameters || {},
        priority: formData.priority!,
        is_active: formData.is_active ?? true
      }

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
    } catch {
      toast({
        variant: 'destructive',
        title: 'Error',
        description: `Failed to ${isEditMode ? 'update' : 'create'} rule`
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

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-2xl font-bold">
            {isEditMode ? `Edit Rule: ${selectedRule?.name}` : 'Create New Rule'}
          </h2>
          <p className="text-muted-foreground">
            {isEditMode ? 'Modify your existing warehouse rule' : 'Define a new rule to detect warehouse anomalies'}
          </p>
        </div>
        <div className="flex gap-2">
          <Button variant="outline" onClick={handleCancel}>
            <ArrowLeft className="w-4 h-4 mr-2" />
            Cancel
          </Button>
          <Button onClick={handleSubmit} disabled={isSubmitting}>
            <Save className="w-4 h-4 mr-2" />
            {isSubmitting ? 'Saving...' : isEditMode ? 'Update Rule' : 'Create Rule'}
          </Button>
        </div>
      </div>

      {/* Progress Steps */}
      <Card>
        <CardContent className="pt-6">
          <div className="flex items-center justify-between">
            {steps.map((step, index) => {
              const Icon = step.icon
              const isActive = step.id === currentStep
              const isCompleted = index < currentStepIndex
              
              return (
                <div key={step.id} className="flex items-center">
                  <div className={`flex items-center gap-2 px-3 py-2 rounded-lg cursor-pointer transition-colors ${
                    isActive ? 'bg-primary text-primary-foreground' :
                    isCompleted ? 'bg-green-100 text-green-700' :
                    'bg-gray-100 text-gray-500'
                  }`} onClick={() => setCurrentStep(step.id as any)}>
                    <Icon className="w-4 h-4" />
                    <span className="font-medium">{step.label}</span>
                  </div>
                  {index < steps.length - 1 && (
                    <div className={`w-8 h-0.5 mx-2 ${
                      index < currentStepIndex ? 'bg-green-500' : 'bg-gray-200'
                    }`} />
                  )}
                </div>
              )
            })}
          </div>
        </CardContent>
      </Card>

      {/* Form Content */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Main Form */}
        <div className="lg:col-span-2">
          <Tabs value={currentStep} onValueChange={(value) => setCurrentStep(value as any)}>
            <TabsContent value="basic">
              <BasicInfoStep 
                formData={formData}
                validationErrors={validationErrors}
                categories={categories}
                onFormChange={setFormData}
              />
            </TabsContent>

            <TabsContent value="conditions">
              <ConditionsStep 
                formData={formData}
                validationErrors={validationErrors}
                onFormChange={setFormData}
                onValidate={handleValidate}
                isValidating={isValidating}
                validationResult={validationResult}
              />
            </TabsContent>

            <TabsContent value="parameters">
              <ParametersStep 
                formData={formData}
                validationErrors={validationErrors}
                onFormChange={setFormData}
              />
            </TabsContent>

            <TabsContent value="preview">
              <PreviewStep 
                formData={formData}
                previewResult={previewResult}
                onPreview={handlePreview}
                isValidating={isValidating}
              />
            </TabsContent>
          </Tabs>

          {/* Navigation */}
          <div className="flex justify-between mt-6">
            <Button 
              variant="outline" 
              onClick={handlePrevious}
              disabled={currentStepIndex === 0}
            >
              <ArrowLeft className="w-4 h-4 mr-2" />
              Previous
            </Button>
            
            <div className="flex gap-2">
              {currentStep === 'conditions' && (
                <Button variant="outline" onClick={handleValidate} disabled={isValidating}>
                  <CheckCircle className="w-4 h-4 mr-2" />
                  {isValidating ? 'Validating...' : 'Validate'}
                </Button>
              )}
              
              {currentStep === 'parameters' && (
                <Button variant="outline" onClick={handlePreview} disabled={isValidating}>
                  <Eye className="w-4 h-4 mr-2" />
                  {isValidating ? 'Generating...' : 'Preview'}
                </Button>
              )}
              
              <Button 
                onClick={currentStepIndex === steps.length - 1 ? handleSubmit : handleNext}
                disabled={currentStepIndex === steps.length - 1 ? isSubmitting : false}
              >
                {currentStepIndex === steps.length - 1 ? (
                  <>
                    <Save className="w-4 h-4 mr-2" />
                    {isSubmitting ? 'Saving...' : isEditMode ? 'Update' : 'Create'}
                  </>
                ) : (
                  <>
                    Next
                    <ArrowRight className="w-4 h-4 ml-2" />
                  </>
                )}
              </Button>
            </div>
          </div>
        </div>

        {/* Sidebar */}
        <div className="space-y-4">
          <RuleInfoSidebar formData={formData} />
          <QuickActionsSidebar 
            onValidate={handleValidate}
            onPreview={handlePreview}
            onReset={resetForm}
            isValidating={isValidating}
          />
        </div>
      </div>
    </div>
  )
}

// Step Components
function BasicInfoStep({ 
  formData, 
  validationErrors, 
  categories, 
  onFormChange 
}: {
  formData: Partial<RuleFormData>
  validationErrors: Record<string, string>
  categories: Array<{ id: number; display_name: string }>
  onFormChange: (data: Partial<RuleFormData>) => void
}) {
  return (
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
            />
            {validationErrors.name && (
              <p className="text-sm text-red-500">{validationErrors.name}</p>
            )}
          </div>

          <div className="space-y-2">
            <Label htmlFor="priority">Priority *</Label>
            <Select value={formData.priority} onValueChange={(value) => onFormChange({ priority: value as 'VERY_HIGH' | 'HIGH' | 'MEDIUM' | 'LOW' })}>
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
          />
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
            {validationErrors.category_id && (
              <p className="text-sm text-red-500">{validationErrors.category_id}</p>
            )}
          </div>

          <div className="space-y-2">
            <Label htmlFor="rule_type">Rule Type *</Label>
            <Select 
              value={formData.rule_type} 
              onValueChange={(value) => onFormChange({ rule_type: value })}
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
            {validationErrors.rule_type && (
              <p className="text-sm text-red-500">{validationErrors.rule_type}</p>
            )}
          </div>
        </div>
      </CardContent>
    </Card>
  )
}

function ConditionsStep({ 
  formData, 
  validationErrors, 
  onFormChange, 
  onValidate, 
  isValidating, 
  validationResult 
}: {
  formData: Partial<RuleFormData>
  validationErrors: Record<string, string>
  onFormChange: (data: Partial<RuleFormData>) => void
  onValidate: () => void
  isValidating: boolean
  validationResult: { success: boolean; error?: string } | null
}) {
  const [conditionsJson, setConditionsJson] = useState(
    JSON.stringify(formData.conditions || {}, null, 2)
  )

  const handleConditionsChange = (value: string) => {
    setConditionsJson(value)
    try {
      const parsed = JSON.parse(value)
      onFormChange({ conditions: parsed })
    } catch {
      // Invalid JSON, don't update store
    }
  }

  return (
    <Card>
      <CardHeader>
        <CardTitle>Rule Conditions</CardTitle>
      </CardHeader>
      <CardContent className="space-y-4">
        <Alert>
          <Info className="h-4 w-4" />
          <AlertDescription>
            Define the conditions that trigger this rule. Use JSON format with operators like &gt;, &lt;, ==, !=.
          </AlertDescription>
        </Alert>

        <div className="space-y-2">
          <div className="flex items-center justify-between">
            <Label htmlFor="conditions">Conditions (JSON) *</Label>
            <Button 
              variant="outline" 
              size="sm" 
              onClick={onValidate}
              disabled={isValidating}
            >
              <CheckCircle className="w-4 h-4 mr-2" />
              {isValidating ? 'Validating...' : 'Validate'}
            </Button>
          </div>
          <Textarea
            id="conditions"
            placeholder='{"days_stagnant": {">=": 7}, "location_zone": {"==": "A"}}'
            value={conditionsJson}
            onChange={(e) => handleConditionsChange(e.target.value)}
            className={`font-mono ${validationErrors.conditions ? 'border-red-500' : ''}`}
            rows={8}
          />
          {validationErrors.conditions && (
            <p className="text-sm text-red-500">{validationErrors.conditions}</p>
          )}
        </div>

        {validationResult && (
          <Alert className={validationResult.success ? 'border-green-500' : 'border-red-500'}>
            {validationResult.success ? (
              <CheckCircle className="h-4 w-4 text-green-500" />
            ) : (
              <AlertTriangle className="h-4 w-4 text-red-500" />
            )}
            <AlertDescription>
              {validationResult.success ? 
                'Conditions are valid!' : 
                `Validation error: ${validationResult.error}`
              }
            </AlertDescription>
          </Alert>
        )}
      </CardContent>
    </Card>
  )
}

function ParametersStep({ 
  formData, 
  validationErrors, 
  onFormChange 
}: {
  formData: Partial<RuleFormData>
  validationErrors: Record<string, string>
  onFormChange: (data: Partial<RuleFormData>) => void
}) {
  const [parametersJson, setParametersJson] = useState(
    JSON.stringify(formData.parameters || {}, null, 2)
  )

  const handleParametersChange = (value: string) => {
    setParametersJson(value)
    try {
      const parsed = JSON.parse(value)
      onFormChange({ parameters: parsed })
    } catch {
      // Invalid JSON, don't update store
    }
  }

  return (
    <Card>
      <CardHeader>
        <CardTitle>Rule Parameters</CardTitle>
      </CardHeader>
      <CardContent className="space-y-4">
        <Alert>
          <Settings className="h-4 w-4" />
          <AlertDescription>
            Configure additional parameters for this rule such as thresholds, weights, or custom settings.
          </AlertDescription>
        </Alert>

        <div className="space-y-2">
          <Label htmlFor="parameters">Parameters (JSON)</Label>
          <Textarea
            id="parameters"
            placeholder='{"threshold": 0.8, "include_weekends": false}'
            value={parametersJson}
            onChange={(e) => handleParametersChange(e.target.value)}
            className="font-mono"
            rows={6}
          />
          <p className="text-sm text-muted-foreground">
            Optional: Additional configuration for rule execution
          </p>
        </div>

        <div className="flex items-center space-x-2">
          <input
            type="checkbox"
            id="is_active"
            checked={formData.is_active ?? true}
            onChange={(e) => onFormChange({ is_active: e.target.checked })}
            className="rounded border-gray-300"
          />
          <Label htmlFor="is_active">Activate rule immediately after creation</Label>
        </div>
      </CardContent>
    </Card>
  )
}

function PreviewStep({ 
  formData, 
  previewResult, 
  onPreview, 
  isValidating 
}: {
  formData: Partial<RuleFormData>
  previewResult: { 
    success: boolean;
    preview_results?: { anomalies_found: number; execution_time_ms: number };
    performance_estimate?: { estimated_anomalies: number; confidence_level: number; performance_prediction: string };
  } | null
  onPreview: () => void
  isValidating: boolean
}) {
  return (
    <Card>
      <CardHeader>
        <CardTitle>Rule Preview</CardTitle>
      </CardHeader>
      <CardContent className="space-y-4">
        <div className="flex items-center justify-between">
          <p className="text-muted-foreground">
            Preview how this rule will behave when applied to your data
          </p>
          <Button onClick={onPreview} disabled={isValidating}>
            <Eye className="w-4 h-4 mr-2" />
            {isValidating ? 'Generating...' : 'Generate Preview'}
          </Button>
        </div>

        {previewResult && (
          <div className="space-y-4">
            <Alert>
              <CheckCircle className="h-4 w-4 text-green-500" />
              <AlertDescription>
                Preview generated successfully
              </AlertDescription>
            </Alert>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <Card>
                <CardHeader className="pb-2">
                  <CardTitle className="text-base">Estimated Matches</CardTitle>
                </CardHeader>
                <CardContent>
                  <p className="text-2xl font-bold text-blue-600">
                    {previewResult.performance_estimate?.estimated_anomalies || 0}
                  </p>
                  <p className="text-sm text-muted-foreground">
                    Based on historical data
                  </p>
                </CardContent>
              </Card>

              <Card>
                <CardHeader className="pb-2">
                  <CardTitle className="text-base">Confidence Level</CardTitle>
                </CardHeader>
                <CardContent>
                  <p className="text-2xl font-bold text-green-600">
                    {((previewResult.performance_estimate?.confidence_level || 0) * 100).toFixed(1)}%
                  </p>
                  <p className="text-sm text-muted-foreground">
                    Prediction accuracy
                  </p>
                </CardContent>
              </Card>
            </div>

            {previewResult.performance_estimate?.performance_prediction && (
              <Alert>
                <Info className="h-4 w-4" />
                <AlertDescription>
                  <strong>Performance Prediction:</strong> {previewResult.performance_estimate.performance_prediction}
                </AlertDescription>
              </Alert>
            )}
          </div>
        )}
      </CardContent>
    </Card>
  )
}

// Sidebar Components
function RuleInfoSidebar({ formData }: { formData: Partial<RuleFormData> }) {
  return (
    <Card>
      <CardHeader>
        <CardTitle className="text-base">Rule Summary</CardTitle>
      </CardHeader>
      <CardContent className="space-y-3">
        <div>
          <Label className="text-sm font-medium">Name</Label>
          <p className="text-sm text-muted-foreground">
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
          <p className="text-sm text-muted-foreground">
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