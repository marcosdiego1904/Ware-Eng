"use client"

import { useState } from 'react'
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
import { Alert, AlertDescription } from '@/components/ui/alert'
import { 
  Clock,
  MapPin,
  Package,
  AlertTriangle,
  CheckCircle,
  Zap,
  Lightbulb,
  Save,
  Eye,
  HelpCircle
} from 'lucide-react'
import type { RuleFormData, CreateRuleRequest } from '@/lib/rules-types'

interface QuickRuleCreatorProps {
  categories: Array<{ id: number; display_name: string }>
  onSave: (ruleData: CreateRuleRequest) => Promise<void>
  onCancel: () => void
  onPreview?: (ruleData: Partial<RuleFormData>) => void
  isSubmitting?: boolean
}

// Quick rule scenarios that cover 80% of use cases
const QUICK_SCENARIOS = [
  {
    id: 'forgotten-pallets',
    name: 'Find Forgotten Pallets',
    description: 'Alert when pallets sit too long in receiving',
    icon: Clock,
    category: 'FLOW_TIME',
    ruleType: 'STAGNANT_PALLETS',
    fields: [
      {
        key: 'hours',
        label: 'Alert after how many hours?',
        type: 'number' as const,
        defaultValue: 6,
        help: 'Pallets sitting longer than this will be flagged',
        suggestions: [2, 4, 6, 8, 12]
      }
    ],
    generateConditions: (values: Record<string, any>) => ({
      location_types: ['RECEIVING'],
      time_threshold_hours: values.hours || 6
    }),
    exampleDescription: (values: Record<string, any>) => 
      `Alerts when pallets sit in receiving for more than ${values.hours || 6} hours`
  },
  {
    id: 'incomplete-lots',
    name: 'Catch Incomplete Lots',
    description: 'Find stragglers when most of lot is stored',
    icon: Package,
    category: 'FLOW_TIME', 
    ruleType: 'UNCOORDINATED_LOTS',
    fields: [
      {
        key: 'percentage',
        label: 'Alert when what % of lot is done?',
        type: 'number' as const,
        defaultValue: 80,
        help: 'Flag remaining pallets when this much of the lot is stored',
        suggestions: [70, 80, 90, 95]
      }
    ],
    generateConditions: (values: Record<string, any>) => ({
      completion_threshold: (values.percentage || 80) / 100,
      location_types: ['RECEIVING']
    }),
    exampleDescription: (values: Record<string, any>) => 
      `Alerts when ${values.percentage || 80}% of a lot is stored but some pallets remain in receiving`
  },
  {
    id: 'aisle-blocking',
    name: 'Clear Blocked Aisles',
    description: 'Flag pallets stuck in aisles',
    icon: MapPin,
    category: 'SPACE',
    ruleType: 'LOCATION_SPECIFIC_STAGNANT',
    fields: [
      {
        key: 'pattern',
        label: 'Aisle location pattern',
        type: 'text' as const,
        defaultValue: 'AISLE*',
        help: 'Pattern to match your aisle locations (use * for wildcards)',
        suggestions: ['AISLE*', 'LANE*', 'CORRIDOR*']
      },
      {
        key: 'hours',
        label: 'Maximum time in aisle (hours)',
        type: 'number' as const,
        defaultValue: 2,
        help: 'How long pallets can sit in aisles before alerting',
        suggestions: [1, 2, 4, 6]
      }
    ],
    generateConditions: (values: Record<string, any>) => ({
      location_pattern: values.pattern || 'AISLE*',
      time_threshold_hours: values.hours || 2
    }),
    exampleDescription: (values: Record<string, any>) => 
      `Alerts when pallets in ${values.pattern || 'AISLE*'} locations sit for more than ${values.hours || 2} hours`
  },
  {
    id: 'wrong-temperature',
    name: 'Temperature Violations',
    description: 'Keep cold products in cold zones',
    icon: AlertTriangle,
    category: 'PRODUCT',
    ruleType: 'TEMPERATURE_ZONE_MISMATCH',
    fields: [
      {
        key: 'products',
        label: 'Product types to monitor',
        type: 'multiselect' as const,
        defaultValue: ['*FROZEN*'],
        help: 'Which product description patterns need temperature control',
        options: [
          { value: '*FROZEN*', label: 'Frozen Products' },
          { value: '*REFRIGERATED*', label: 'Refrigerated Products' },
          { value: '*DAIRY*', label: 'Dairy Products' },
          { value: '*MEAT*', label: 'Meat Products' },
          { value: '*ICE CREAM*', label: 'Ice Cream' }
        ]
      },
      {
        key: 'minutes',
        label: 'Grace period (minutes)',
        type: 'number' as const,
        defaultValue: 30,
        help: 'How long products can be in wrong zone before alerting',
        suggestions: [15, 30, 45, 60]
      }
    ],
    generateConditions: (values: Record<string, any>) => ({
      product_patterns: values.products || ['*FROZEN*'],
      prohibited_zones: ['AMBIENT', 'GENERAL'],
      time_threshold_minutes: values.minutes || 30
    }),
    exampleDescription: (values: Record<string, any>) => 
      `Alerts when ${(values.products || ['*FROZEN*']).join(', ')} products are in warm zones for more than ${values.minutes || 30} minutes`
  }
]

export function QuickRuleCreator({ 
  categories, 
  onSave, 
  onCancel, 
  onPreview, 
  isSubmitting 
}: QuickRuleCreatorProps) {
  const [selectedScenario, setSelectedScenario] = useState<string>('')
  const [ruleName, setRuleName] = useState<string>('')
  const [ruleDescription, setRuleDescription] = useState<string>('')
  const [fieldValues, setFieldValues] = useState<Record<string, any>>({})
  const [priority, setPriority] = useState<'VERY_HIGH' | 'HIGH' | 'MEDIUM' | 'LOW'>('HIGH')

  const scenario = QUICK_SCENARIOS.find(s => s.id === selectedScenario)

  const handleScenarioSelect = (scenarioId: string) => {
    const newScenario = QUICK_SCENARIOS.find(s => s.id === scenarioId)
    setSelectedScenario(scenarioId)
    
    if (newScenario) {
      // Set default values
      setRuleName(newScenario.name)
      setRuleDescription(newScenario.description)
      
      // Initialize field values with defaults
      const defaultValues: Record<string, any> = {}
      newScenario.fields.forEach(field => {
        defaultValues[field.key] = field.defaultValue
      })
      setFieldValues(defaultValues)
    }
  }

  const updateFieldValue = (key: string, value: any) => {
    setFieldValues(prev => ({ ...prev, [key]: value }))
  }

  const handlePreview = () => {
    if (!scenario) return

    const conditions = scenario.generateConditions(fieldValues)
    const categoryId = categories.find(c => c.display_name.includes(scenario.category.replace('_', ' ')))?.id || 1

    const ruleData: Partial<RuleFormData> = {
      name: ruleName,
      description: ruleDescription,
      category_id: categoryId,
      rule_type: scenario.ruleType,
      conditions,
      parameters: {},
      priority,
      is_active: true
    }

    onPreview?.(ruleData)
  }

  const handleSave = async () => {
    if (!scenario || !ruleName.trim()) return

    const conditions = scenario.generateConditions(fieldValues)
    const categoryId = categories.find(c => c.display_name.includes(scenario.category.replace('_', ' ')))?.id || 1

    const ruleData: CreateRuleRequest = {
      name: ruleName,
      description: ruleDescription,
      category_id: categoryId,
      rule_type: scenario.ruleType,
      conditions,
      parameters: {},
      priority,
      is_active: true
    }

    await onSave(ruleData)
  }

  const renderField = (field: any) => {
    const value = fieldValues[field.key]

    switch (field.type) {
      case 'number':
        return (
          <div className="space-y-3">
            <div className="flex items-center gap-4">
              <Input
                type="number"
                value={value || ''}
                onChange={(e) => updateFieldValue(field.key, parseInt(e.target.value) || field.defaultValue)}
                className="w-32"
              />
              <span className="text-sm text-muted-foreground">{field.help}</span>
            </div>
            {field.suggestions && (
              <div className="flex gap-2">
                <span className="text-sm text-muted-foreground">Quick:</span>
                {field.suggestions.map((suggestion: number) => (
                  <Button
                    key={suggestion}
                    variant="outline"
                    size="sm"
                    onClick={() => updateFieldValue(field.key, suggestion)}
                    className="h-7 text-xs"
                  >
                    {suggestion}
                  </Button>
                ))}
              </div>
            )}
          </div>
        )

      case 'text':
        return (
          <div className="space-y-3">
            <div className="space-y-2">
              <Input
                value={value || ''}
                onChange={(e) => updateFieldValue(field.key, e.target.value)}
                placeholder={`Default: ${field.defaultValue}`}
              />
              <p className="text-sm text-muted-foreground">{field.help}</p>
            </div>
            {field.suggestions && (
              <div className="flex gap-2">
                <span className="text-sm text-muted-foreground">Examples:</span>
                {field.suggestions.map((suggestion: string) => (
                  <Button
                    key={suggestion}
                    variant="outline"
                    size="sm"
                    onClick={() => updateFieldValue(field.key, suggestion)}
                    className="h-7 text-xs"
                  >
                    {suggestion}
                  </Button>
                ))}
              </div>
            )}
          </div>
        )

      case 'multiselect':
        const currentValues = Array.isArray(value) ? value : [field.defaultValue]
        return (
          <div className="space-y-3">
            <div className="space-y-2">
              {field.options?.map((option: any) => (
                <label key={option.value} className="flex items-center space-x-3 cursor-pointer">
                  <input
                    type="checkbox"
                    checked={currentValues.includes(option.value)}
                    onChange={(e) => {
                      const newValues = e.target.checked
                        ? [...currentValues, option.value]
                        : currentValues.filter((v: any) => v !== option.value)
                      updateFieldValue(field.key, newValues)
                    }}
                    className="rounded border-gray-300"
                  />
                  <span className="font-medium">{option.label}</span>
                </label>
              ))}
            </div>
            <p className="text-sm text-muted-foreground">{field.help}</p>
          </div>
        )

      default:
        return null
    }
  }

  return (
    <div className="max-w-4xl mx-auto space-y-6">
      {/* Header */}
      <div className="text-center space-y-2">
        <h2 className="text-2xl font-bold">Quick Rule Setup</h2>
        <p className="text-muted-foreground">
          Create a rule in under 2 minutes by choosing a common scenario
        </p>
      </div>

      {/* Step 1: Choose Scenario */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <span className="bg-primary text-primary-foreground rounded-full w-6 h-6 flex items-center justify-center text-sm">1</span>
            What do you want to detect?
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {QUICK_SCENARIOS.map(scenario => (
              <Card 
                key={scenario.id} 
                className={`cursor-pointer transition-all hover:shadow-md ${
                  selectedScenario === scenario.id ? 'ring-2 ring-primary' : ''
                }`}
                onClick={() => handleScenarioSelect(scenario.id)}
              >
                <CardContent className="p-4">
                  <div className="flex items-start gap-3">
                    <div className="p-2 rounded-lg bg-primary/10 flex-shrink-0">
                      <scenario.icon className="w-5 h-5 text-primary" />
                    </div>
                    <div>
                      <h3 className="font-semibold">{scenario.name}</h3>
                      <p className="text-sm text-muted-foreground">{scenario.description}</p>
                    </div>
                  </div>
                </CardContent>
              </Card>
            ))}
          </div>
        </CardContent>
      </Card>

      {/* Step 2: Configure (only show if scenario selected) */}
      {scenario && (
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <span className="bg-primary text-primary-foreground rounded-full w-6 h-6 flex items-center justify-center text-sm">2</span>
              Configure your rule
            </CardTitle>
          </CardHeader>
          <CardContent className="space-y-6">
            {/* Rule Name & Description */}
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div className="space-y-2">
                <Label>Rule Name</Label>
                <Input
                  value={ruleName}
                  onChange={(e) => setRuleName(e.target.value)}
                  placeholder="Enter a clear name for this rule"
                />
              </div>
              <div className="space-y-2">
                <Label>Priority</Label>
                <Select value={priority} onValueChange={(value: any) => setPriority(value)}>
                  <SelectTrigger>
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="VERY_HIGH">
                      <Badge className="bg-red-500 text-white mr-2">Very High</Badge>
                      Critical issues
                    </SelectItem>
                    <SelectItem value="HIGH">
                      <Badge className="bg-orange-500 text-white mr-2">High</Badge>
                      Important issues
                    </SelectItem>
                    <SelectItem value="MEDIUM">
                      <Badge className="bg-blue-500 text-white mr-2">Medium</Badge>
                      Standard monitoring
                    </SelectItem>
                    <SelectItem value="LOW">
                      <Badge className="bg-gray-500 text-white mr-2">Low</Badge>
                      Optional alerts
                    </SelectItem>
                  </SelectContent>
                </Select>
              </div>
            </div>

            <div className="space-y-2">
              <Label>Description (optional)</Label>
              <Textarea
                value={ruleDescription}
                onChange={(e) => setRuleDescription(e.target.value)}
                placeholder="Describe what this rule does and why it's important"
                rows={2}
              />
            </div>

            {/* Scenario-specific fields */}
            <div className="space-y-4">
              {scenario.fields.map(field => (
                <div key={field.key} className="space-y-2">
                  <Label className="text-base font-medium">{field.label}</Label>
                  {renderField(field)}
                </div>
              ))}
            </div>
          </CardContent>
        </Card>
      )}

      {/* Step 3: Preview & Save */}
      {scenario && ruleName && (
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <span className="bg-primary text-primary-foreground rounded-full w-6 h-6 flex items-center justify-center text-sm">3</span>
              Preview & Save
            </CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            <Alert>
              <Lightbulb className="h-4 w-4" />
              <AlertDescription>
                <strong>This rule will:</strong> {scenario.exampleDescription(fieldValues)}
              </AlertDescription>
            </Alert>

            <div className="flex justify-between">
              <Button variant="outline" onClick={onCancel}>
                Cancel
              </Button>
              <div className="flex gap-3">
                {onPreview && (
                  <Button variant="outline" onClick={handlePreview}>
                    <Eye className="w-4 h-4 mr-2" />
                    Preview Results
                  </Button>
                )}
                <Button onClick={handleSave} disabled={isSubmitting || !ruleName.trim()}>
                  <Save className="w-4 h-4 mr-2" />
                  {isSubmitting ? 'Creating...' : 'Create Rule'}
                </Button>
              </div>
            </div>
          </CardContent>
        </Card>
      )}

      {/* Help Section */}
      <Card className="bg-blue-50 border-blue-200">
        <CardContent className="p-4">
          <div className="flex items-start gap-3">
            <HelpCircle className="w-5 h-5 text-blue-600 flex-shrink-0 mt-0.5" />
            <div className="space-y-2">
              <h4 className="font-medium text-blue-900">Need something more specific?</h4>
              <p className="text-sm text-blue-700">
                These quick scenarios cover the most common warehouse rules. If you need more advanced conditions or custom logic, you can use the Advanced Rule Builder after creating this rule.
              </p>
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  )
}