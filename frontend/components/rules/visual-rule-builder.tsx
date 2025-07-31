"use client"

import { useState, useEffect } from 'react'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { 
  Select, 
  SelectContent, 
  SelectItem, 
  SelectTrigger, 
  SelectValue 
} from '@/components/ui/select'
import { Alert, AlertDescription } from '@/components/ui/alert'
import { 
  Plus, 
  Trash2, 
  Info,
  CheckCircle,
  AlertCircle,
  Clock,
  MapPin,
  Package
} from 'lucide-react'

interface RuleCondition {
  id: string
  field: string
  operator: string
  value: string | number | string[]
  connector?: 'AND' | 'OR'
}

interface VisualRuleBuilderProps {
  initialConditions?: Record<string, any>
  ruleType?: string
  onConditionsChange: (conditions: Record<string, any>) => void
  onValidate?: () => void
  isValidating?: boolean
  validationResult?: { success: boolean; error?: string } | null
}

// Field definitions with user-friendly labels and help text
const FIELD_DEFINITIONS = {
  'time_based': {
    label: 'Time-Based Rules',
    icon: Clock,
    fields: {
      'time_threshold_hours': {
        label: 'Hours since arrival',
        description: 'How many hours a pallet has been in the location',
        type: 'number',
        operators: ['greater_than', 'less_than', 'equals'],
        defaultValue: 6,
        suggestions: [2, 4, 6, 8, 12, 24]
      },
      'time_threshold_minutes': {
        label: 'Minutes since arrival', 
        description: 'How many minutes a pallet has been in the location',
        type: 'number',
        operators: ['greater_than', 'less_than', 'equals'],
        defaultValue: 30,
        suggestions: [15, 30, 60, 120]
      }
    }
  },
  'location_based': {
    label: 'Location-Based Rules',
    icon: MapPin,
    fields: {
      'location_types': {
        label: 'Location types to check',
        description: 'Which types of warehouse locations to monitor',
        type: 'multiselect',
        operators: ['includes', 'excludes', 'equals'],
        options: [
          { value: 'RECEIVING', label: 'Receiving Areas', description: 'Where pallets first arrive' },
          { value: 'TRANSITIONAL', label: 'Transitional Areas', description: 'Temporary staging areas' },
          { value: 'FINAL', label: 'Final Storage', description: 'Long-term storage locations' },
          { value: 'UNKNOWN', label: 'Unknown Locations', description: 'Unclassified areas' }
        ],
        defaultValue: ['RECEIVING']
      },
      'location_pattern': {
        label: 'Location pattern',
        description: 'Pattern to match location codes (use * for wildcards)',
        type: 'text',
        operators: ['matches', 'not_matches'],
        defaultValue: 'AISLE*',
        suggestions: ['AISLE*', 'RECEIVING*', 'DOCK*', 'ZONE-*']
      }
    }
  },
  'product_based': {
    label: 'Product-Based Rules',
    icon: Package,
    fields: {
      'product_patterns': {
        label: 'Product patterns',
        description: 'Product description patterns to match (use * for wildcards)',
        type: 'multitext',
        operators: ['matches_any', 'matches_none'],
        defaultValue: ['*FROZEN*'],
        suggestions: ['*FROZEN*', '*REFRIGERATED*', '*DAIRY*', '*MEAT*', '*PRODUCE*']
      },
      'completion_threshold': {
        label: 'Lot completion percentage',
        description: 'What percentage of a lot must be stored before flagging stragglers',
        type: 'percentage',
        operators: ['greater_than', 'less_than'],
        defaultValue: 80,
        suggestions: [50, 70, 80, 90, 95]
      }
    }
  }
}

const OPERATORS = {
  'greater_than': { label: 'is greater than', symbol: '>' },
  'less_than': { label: 'is less than', symbol: '<' },
  'equals': { label: 'equals', symbol: '=' },
  'not_equals': { label: 'does not equal', symbol: '≠' },
  'includes': { label: 'includes', symbol: '∈' },
  'excludes': { label: 'excludes', symbol: '∉' },
  'matches': { label: 'matches pattern', symbol: '~' },
  'not_matches': { label: 'does not match', symbol: '!~' },
  'matches_any': { label: 'matches any of', symbol: '∈' },
  'matches_none': { label: 'matches none of', symbol: '∉' }
}

export function VisualRuleBuilder({ 
  initialConditions = {},
  ruleType,
  onConditionsChange,
  onValidate,
  isValidating,
  validationResult 
}: VisualRuleBuilderProps) {
  const [conditions, setConditions] = useState<RuleCondition[]>([])
  const [showAdvanced, setShowAdvanced] = useState(false)

  // Initialize conditions from props
  useEffect(() => {
    if (initialConditions && Object.keys(initialConditions).length > 0) {
      try {
        const parsedConditions = parseConditionsFromObject(initialConditions)
        if (parsedConditions.length > 0) {
          setConditions(parsedConditions)
        } else {
          // If parsing failed or returned empty, add default condition
          addDefaultCondition()
        }
      } catch (error) {
        console.warn('Failed to parse initial conditions:', error)
        // Fallback to default condition if parsing fails
        addDefaultCondition()
      }
    } else if (conditions.length === 0) {
      // Add a default condition based on rule type
      addDefaultCondition()
    }
  }, [initialConditions, ruleType])

  // Convert visual conditions to JSON format
  useEffect(() => {
    const jsonConditions = convertToJsonConditions(conditions)
    onConditionsChange(jsonConditions)
  }, [conditions])

  const parseConditionsFromObject = (obj: Record<string, any>): RuleCondition[] => {
    const parsed: RuleCondition[] = []
    let conditionIndex = 0
    
    Object.entries(obj).forEach(([key, value]) => {
      if (key === 'rule_type') {
        // Skip rule_type field as it's not a condition
        return
      }
      
      if (typeof value === 'object' && value !== null && !Array.isArray(value)) {
        // Handle complex conditions like { ">=": 6 }
        Object.entries(value).forEach(([operator, operatorValue]) => {
          parsed.push({
            id: `condition-${Date.now()}-${conditionIndex++}`,
            field: key,
            operator: convertOperatorFromJson(operator),
            value: operatorValue as string | number | string[],
            connector: parsed.length > 0 ? 'AND' : undefined
          })
        })
      } else {
        // Handle simple conditions like "field": "value"
        parsed.push({
          id: `condition-${Date.now()}-${conditionIndex++}`,
          field: key,
          operator: 'equals',
          value: value,
          connector: parsed.length > 0 ? 'AND' : undefined
        })
      }
    })
    
    return parsed
  }

  const convertOperatorFromJson = (jsonOp: string): string => {
    const mapping: Record<string, string> = {
      '>=': 'greater_than',
      '>': 'greater_than', 
      '<=': 'less_than',
      '<': 'less_than',
      '==': 'equals',
      '=': 'equals',
      '!=': 'not_equals',
      'in': 'includes',
      'not_in': 'excludes',
      'matches': 'matches',
      'not_matches': 'not_matches',
      'contains': 'includes',
      'not_contains': 'excludes'
    }
    return mapping[jsonOp] || 'equals'
  }

  const convertToJsonConditions = (visualConditions: RuleCondition[]): Record<string, any> => {
    const result: Record<string, any> = {}
    
    visualConditions.forEach(condition => {
      const { field, operator, value } = condition
      
      // Convert operator to JSON format
      let jsonOperator: string
      let jsonValue: any = value

      switch (operator) {
        case 'greater_than':
          jsonOperator = '>='
          break
        case 'less_than':
          jsonOperator = '<='
          break
        case 'equals':
          jsonOperator = '=='
          break
        case 'not_equals':
          jsonOperator = '!='
          break
        case 'includes':
        case 'matches_any':
          jsonOperator = 'in'
          jsonValue = Array.isArray(value) ? value : [value]
          break
        case 'excludes':
        case 'matches_none':
          jsonOperator = 'not_in'
          jsonValue = Array.isArray(value) ? value : [value]
          break
        default:
          jsonOperator = '=='
      }

      // Handle special field mappings
      if (field === 'completion_threshold' && typeof value === 'number') {
        jsonValue = value / 100 // Convert percentage to decimal
      }

      if (result[field]) {
        // Multiple conditions for same field - convert to object
        if (typeof result[field] !== 'object' || Array.isArray(result[field])) {
          const oldValue = result[field]
          result[field] = { '==': oldValue }
        }
        result[field][jsonOperator] = jsonValue
      } else {
        if (jsonOperator === '==') {
          result[field] = jsonValue
        } else {
          result[field] = { [jsonOperator]: jsonValue }
        }
      }
    })
    
    return result
  }

  const addDefaultCondition = () => {
    let defaultCondition: RuleCondition

    // Suggest condition based on rule type
    switch (ruleType) {
      case 'STAGNANT_PALLETS':
        defaultCondition = {
          id: `condition-${Date.now()}`,
          field: 'time_threshold_hours',
          operator: 'greater_than',
          value: 6
        }
        break
      case 'UNCOORDINATED_LOTS':
        defaultCondition = {
          id: `condition-${Date.now()}`,
          field: 'completion_threshold', 
          operator: 'greater_than',
          value: 80
        }
        break
      case 'LOCATION_SPECIFIC_STAGNANT':
        defaultCondition = {
          id: `condition-${Date.now()}`,
          field: 'location_pattern',
          operator: 'matches',
          value: 'AISLE*'
        }
        break
      default:
        defaultCondition = {
          id: `condition-${Date.now()}`,
          field: 'time_threshold_hours',
          operator: 'greater_than', 
          value: 6
        }
    }

    setConditions([defaultCondition])
  }

  const addCondition = () => {
    const newCondition: RuleCondition = {
      id: `condition-${Date.now()}`,
      field: 'time_threshold_hours',
      operator: 'greater_than',
      value: 6,
      connector: 'AND'
    }
    setConditions([...conditions, newCondition])
  }

  const updateCondition = (id: string, updates: Partial<RuleCondition>) => {
    setConditions(prev => prev.map(condition => 
      condition.id === id ? { ...condition, ...updates } : condition
    ))
  }

  const removeCondition = (id: string) => {
    setConditions(prev => prev.filter(condition => condition.id !== id))
  }

  const getFieldDefinition = (fieldKey: string) => {
    for (const category of Object.values(FIELD_DEFINITIONS)) {
      if ((category.fields as any)[fieldKey]) {
        return (category.fields as any)[fieldKey]
      }
    }
    return null
  }

  const getAvailableOperators = (fieldKey: string) => {
    const fieldDef = getFieldDefinition(fieldKey)
    return fieldDef?.operators || ['equals']
  }

  const renderCondition = (condition: RuleCondition, index: number) => {
    const fieldDef = getFieldDefinition(condition.field)
    const availableOperators = getAvailableOperators(condition.field)

    return (
      <Card key={condition.id} className="border-l-4 border-l-blue-500">
        <CardContent className="pt-6">
          {/* Connector */}
          {index > 0 && (
            <div className="flex items-center mb-4">
              <Select 
                value={condition.connector || 'AND'} 
                onValueChange={(value) => updateCondition(condition.id, { connector: value as 'AND' | 'OR' })}
              >
                <SelectTrigger className="w-20">
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="AND">AND</SelectItem>
                  <SelectItem value="OR">OR</SelectItem>
                </SelectContent>
              </Select>
              <span className="ml-2 text-sm text-muted-foreground">this condition must also be true</span>
            </div>
          )}

          <div className="grid grid-cols-1 md:grid-cols-3 gap-4 items-end">
            {/* Field Selection */}
            <div className="space-y-2">
              <Label>When</Label>
              <Select value={condition.field} onValueChange={(value) => updateCondition(condition.id, { field: value })}>
                <SelectTrigger>
                  <SelectValue placeholder="Select field" />
                </SelectTrigger>
                <SelectContent>
                  {Object.entries(FIELD_DEFINITIONS).map(([categoryKey, category]) => (
                    <div key={categoryKey}>
                      <div className="px-2 py-1 text-sm font-medium text-muted-foreground flex items-center gap-2">
                        <category.icon className="w-4 h-4" />
                        {category.label}
                      </div>
                      {Object.entries(category.fields).map(([fieldKey, field]) => (
                        <SelectItem key={fieldKey} value={fieldKey} className="pl-6">
                          <div>
                            <div className="font-medium">{field.label}</div>
                            <div className="text-xs text-muted-foreground">{field.description}</div>
                          </div>
                        </SelectItem>
                      ))}
                    </div>
                  ))}
                </SelectContent>
              </Select>
            </div>

            {/* Operator Selection */}
            <div className="space-y-2">
              <Label>Is</Label>
              <Select value={condition.operator} onValueChange={(value) => updateCondition(condition.id, { operator: value })}>
                <SelectTrigger>
                  <SelectValue placeholder="Select operator" />
                </SelectTrigger>
                <SelectContent>
                  {availableOperators.map((op: string) => (
                    <SelectItem key={op} value={op}>
                      {(OPERATORS as any)[op]?.label || op}
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>

            {/* Value Input */}
            <div className="space-y-2">
              <Label>Value</Label>
              {renderValueInput(condition, fieldDef)}
            </div>
          </div>

          {/* Field Help */}
          {fieldDef && (
            <Alert className="mt-4">
              <Info className="h-4 w-4" />
              <AlertDescription>
                <strong>About this field:</strong> {fieldDef.description}
                {fieldDef.suggestions && (
                  <div className="mt-2">
                    <span className="text-sm font-medium">Typical values: </span>
                    {fieldDef.suggestions.map((suggestion: any, idx: number) => (
                      <Button
                        key={idx}
                        variant="outline"
                        size="sm"
                        className="mx-1 h-6 text-xs"
                        onClick={() => updateCondition(condition.id, { value: suggestion })}
                      >
                        {fieldDef.type === 'percentage' ? `${suggestion}%` : suggestion}
                      </Button>
                    ))}
                  </div>
                )}
              </AlertDescription>
            </Alert>
          )}

          {/* Remove Button */}
          {conditions.length > 1 && (
            <div className="flex justify-end mt-4">
              <Button
                variant="outline"
                size="sm"
                onClick={() => removeCondition(condition.id)}
                className="text-destructive hover:text-destructive"
              >
                <Trash2 className="w-4 h-4 mr-2" />
                Remove Condition
              </Button>
            </div>
          )}
        </CardContent>
      </Card>
    )
  }

  const renderValueInput = (condition: RuleCondition, fieldDef: any) => {
    if (!fieldDef) {
      return (
        <Input
          value={condition.value?.toString() || ''}
          onChange={(e) => updateCondition(condition.id, { value: e.target.value })}
          placeholder="Enter value"
        />
      )
    }

    switch (fieldDef.type) {
      case 'number':
        return (
          <Input
            type="number"
            value={condition.value?.toString() || ''}
            onChange={(e) => updateCondition(condition.id, { value: parseInt(e.target.value) || 0 })}
            placeholder="Enter number"
          />
        )

      case 'percentage':
        return (
          <div className="flex items-center">
            <Input
              type="number"
              min="0"
              max="100"
              value={condition.value?.toString() || ''}
              onChange={(e) => updateCondition(condition.id, { value: parseInt(e.target.value) || 0 })}
              placeholder="0"
              className="rounded-r-none"
            />
            <span className="bg-muted px-3 py-2 text-sm rounded-r border border-l-0">%</span>
          </div>
        )

      case 'multiselect':
        const currentValues = Array.isArray(condition.value) ? condition.value : []
        return (
          <div className="space-y-2">
            {fieldDef.options?.map((option: any) => (
              <label key={option.value} className="flex items-center space-x-2 cursor-pointer">
                <input
                  type="checkbox"
                  checked={currentValues.includes(option.value)}
                  onChange={(e) => {
                    const newValues = e.target.checked
                      ? [...currentValues, option.value]
                      : currentValues.filter(v => v !== option.value)
                    updateCondition(condition.id, { value: newValues })
                  }}
                  className="rounded border-gray-300"
                />
                <div>
                  <span className="font-medium">{option.label}</span>
                  <div className="text-xs text-muted-foreground">{option.description}</div>
                </div>
              </label>
            ))}
          </div>
        )

      case 'multitext':
        const textValues = Array.isArray(condition.value) ? condition.value : [condition.value || '']
        return (
          <div className="space-y-2">
            {textValues.map((value, idx) => (
              <div key={idx} className="flex gap-2">
                <Input
                  value={value?.toString() || ''}
                  onChange={(e) => {
                    const newValues = [...textValues]
                    newValues[idx] = e.target.value
                    updateCondition(condition.id, { value: newValues.filter(v => v).map(String) })
                  }}
                  placeholder="Enter pattern (use * for wildcards)"
                />
                {textValues.length > 1 && (
                  <Button
                    variant="outline"
                    size="sm"
                    onClick={() => {
                      const newValues = textValues.filter((_, i) => i !== idx)
                      updateCondition(condition.id, { value: newValues.map(String) })
                    }}
                  >
                    <Trash2 className="w-4 h-4" />
                  </Button>
                )}
              </div>
            ))}
            <Button
              variant="outline"
              size="sm"
              onClick={() => updateCondition(condition.id, { value: [...textValues.map(String), ''] })}
            >
              <Plus className="w-4 h-4 mr-2" />
              Add Pattern
            </Button>
          </div>
        )

      default:
        return (
          <Input
            value={condition.value?.toString() || ''}
            onChange={(e) => updateCondition(condition.id, { value: e.target.value })}
            placeholder="Enter value"
          />
        )
    }
  }

  return (
    <div className="space-y-6">
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <CheckCircle className="w-5 h-5 text-green-500" />
            Rule Conditions
          </CardTitle>
          <p className="text-muted-foreground">
            Define when this rule should trigger using simple conditions. The rule will activate when ALL conditions are met.
          </p>
        </CardHeader>
        <CardContent className="space-y-4">
          {conditions.map((condition, index) => renderCondition(condition, index))}

          {/* Add Condition Button */}
          <div className="flex justify-center pt-4">
            <Button variant="outline" onClick={addCondition}>
              <Plus className="w-4 h-4 mr-2" />
              Add Another Condition
            </Button>
          </div>

          {/* Validation Results */}
          {validationResult && (
            <Alert className={validationResult.success ? 'border-green-500' : 'border-red-500'}>
              {validationResult.success ? (
                <CheckCircle className="h-4 w-4 text-green-500" />
              ) : (
                <AlertCircle className="h-4 w-4 text-red-500" />
              )}
              <AlertDescription>
                {validationResult.success ? 
                  'Conditions are valid and ready to use!' : 
                  `Validation error: ${validationResult.error}`
                }
              </AlertDescription>
            </Alert>
          )}

          {/* Validate Button */}
          {onValidate && (
            <div className="flex justify-end pt-4">
              <Button variant="outline" onClick={onValidate} disabled={isValidating}>
                <CheckCircle className="w-4 h-4 mr-2" />
                {isValidating ? 'Validating...' : 'Test Conditions'}
              </Button>
            </div>
          )}

          {/* Advanced JSON View */}
          <details className="pt-4">
            <summary className="cursor-pointer text-sm font-medium text-muted-foreground hover:text-foreground">
              Advanced: View Generated JSON
            </summary>
            <div className="mt-2 p-4 bg-muted rounded-lg">
              <pre className="text-sm overflow-auto">
                {JSON.stringify(convertToJsonConditions(conditions), null, 2)}
              </pre>
            </div>
          </details>
        </CardContent>
      </Card>
    </div>
  )
}