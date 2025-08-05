"use client"

import { useState } from 'react'
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
import { 
  Clock,
  MapPin,
  Package,
  AlertTriangle,
  CheckCircle,
  Lightbulb,
  Zap,
  Users,
  Shield,
  ArrowRight,
  Info,
  AlertCircle,
  Settings
} from 'lucide-react'

interface SmartTemplate {
  id: string
  name: string
  description: string
  category: 'common' | 'advanced' | 'industry'
  icon: React.ComponentType<{ className?: string }>
  difficulty: 'beginner' | 'intermediate' | 'advanced'
  estimatedTime: string
  useCase: string
  ruleType: string
  conditions: Record<string, unknown>
  parameters: Record<string, unknown>
  configurableFields: {
    key: string
    label: string
    description: string
    type: 'number' | 'select' | 'text' | 'multiselect'
    defaultValue: any
    options?: { value: any; label: string; description?: string }[]
    min?: number
    max?: number
    suggestions?: any[]
  }[]
  examples: {
    scenario: string
    configuration: Record<string, any>
    expectedResult: string
  }[]
  tips: string[]
}

interface SmartTemplatesProps {
  onTemplateSelect: (template: SmartTemplate, configuration: Record<string, unknown>, ruleData?: unknown) => void
  onCancel: () => void
  categories: Array<{ id: number; display_name: string }>
}

const SMART_TEMPLATES: SmartTemplate[] = [
  // BASIC TEMPLATES - All 10 rule types covered
  {
    id: 'forgotten-pallets',
    name: 'Find Forgotten Pallets',
    description: 'Catch pallets sitting too long in receiving areas',
    category: 'common',
    icon: Clock,
    difficulty: 'beginner',
    estimatedTime: '2 minutes',
    useCase: 'Daily operations - prevent bottlenecks in receiving',
    ruleType: 'STAGNANT_PALLETS',
    conditions: {
      location_types: ['RECEIVING'],
      time_threshold_hours: 6
    },
    parameters: {},
    configurableFields: [
      {
        key: 'time_threshold_hours',
        label: 'Alert after how many hours?',
        description: 'Pallets sitting longer than this will be flagged',
        type: 'number',
        defaultValue: 6,
        min: 1,
        max: 48,
        suggestions: [2, 4, 6, 8, 12, 24]
      },
      {
        key: 'location_types',
        label: 'Which areas to monitor?',
        description: 'Select the warehouse areas you want to check',
        type: 'multiselect',
        defaultValue: ['RECEIVING'],
        options: [
          { value: 'RECEIVING', label: 'Receiving Areas', description: 'Where trucks unload' },
          { value: 'TRANSITIONAL', label: 'Staging Areas', description: 'Temporary holding zones' },
          { value: 'UNKNOWN', label: 'Unclassified Areas', description: 'Locations without clear type' }
        ]
      }
    ],
    examples: [
      {
        scenario: 'Small warehouse with fast turnaround',
        configuration: { time_threshold_hours: 4, location_types: ['RECEIVING'] },
        expectedResult: 'Alerts for pallets in receiving after 4 hours'
      },
      {
        scenario: 'Large distribution center',
        configuration: { time_threshold_hours: 8, location_types: ['RECEIVING', 'TRANSITIONAL'] },
        expectedResult: 'Broader monitoring with longer grace period'
      }
    ],
    tips: [
      'Start with 6-8 hours for most operations',
      'Include staging areas if you use them for temporary storage',
      'Adjust timing based on your typical processing speed'
    ]
  },
  {
    id: 'incomplete-lots',
    name: 'Catch Incomplete Lots',
    description: 'Find stragglers when most of a lot is already stored',
    category: 'common',
    icon: Package,
    difficulty: 'beginner',
    estimatedTime: '3 minutes',
    useCase: 'Lot coordination - ensure complete lot processing',
    ruleType: 'UNCOORDINATED_LOTS',
    conditions: {
      completion_threshold: 0.8,
      location_types: ['RECEIVING']
    },
    parameters: {},
    configurableFields: [
      {
        key: 'completion_threshold',
        label: 'Alert when what % of lot is stored?',
        description: 'Flag remaining pallets when this much of the lot is done',
        type: 'number',
        defaultValue: 80,
        min: 50,
        max: 100,
        suggestions: [70, 80, 90, 95]
      }
    ],
    examples: [
      {
        scenario: 'Strict lot completion requirements',
        configuration: { completion_threshold: 90 },
        expectedResult: 'Alerts when 90% of lot is stored but some pallets remain'
      },
      {
        scenario: 'Flexible processing',
        configuration: { completion_threshold: 70 },
        expectedResult: 'Earlier alerts to prevent stragglers'
      }
    ],
    tips: [
      '80% is a good starting point for most operations',
      'Higher percentages catch fewer but more critical cases',
      'Lower percentages give more early warnings'
    ]
  },
  {
    id: 'wrong-temperature-zone',
    name: 'Temperature Zone Violations',
    description: 'Ensure cold products stay in cold areas',
    category: 'common',
    icon: Shield,
    difficulty: 'intermediate',
    estimatedTime: '4 minutes',
    useCase: 'Food safety - prevent temperature violations',
    ruleType: 'TEMPERATURE_ZONE_MISMATCH',
    conditions: {
      product_patterns: ['*FROZEN*', '*REFRIGERATED*'],
      prohibited_zones: ['AMBIENT', 'GENERAL'],
      time_threshold_minutes: 30
    },
    parameters: {},
    configurableFields: [
      {
        key: 'product_patterns',
        label: 'Which products need temperature control?',
        description: 'Product description patterns (use * for wildcards)',
        type: 'multiselect',
        defaultValue: ['*FROZEN*', '*REFRIGERATED*'],
        options: [
          { value: '*FROZEN*', label: 'Frozen Products', description: 'Items with "FROZEN" in description' },
          { value: '*REFRIGERATED*', label: 'Refrigerated Products', description: 'Items with "REFRIGERATED" in description' },
          { value: '*DAIRY*', label: 'Dairy Products', description: 'Dairy items requiring cold storage' },
          { value: '*MEAT*', label: 'Meat Products', description: 'Fresh meat requiring refrigeration' },
          { value: '*ICE CREAM*', label: 'Ice Cream', description: 'Frozen desserts' }
        ]
      },
      {
        key: 'time_threshold_minutes',
        label: 'Grace period (minutes)',
        description: 'How long products can be in wrong zone before alerting',
        type: 'number',
        defaultValue: 30,
        min: 5,
        max: 120,
        suggestions: [15, 30, 45, 60]
      }
    ],
    examples: [
      {
        scenario: 'Strict food safety requirements',
        configuration: { time_threshold_minutes: 15, product_patterns: ['*FROZEN*', '*DAIRY*'] },
        expectedResult: 'Immediate alerts for any cold products in warm zones'
      },
      {
        scenario: 'Standard grocery operation',
        configuration: { time_threshold_minutes: 30, product_patterns: ['*FROZEN*', '*REFRIGERATED*'] },
        expectedResult: '30-minute grace period for temperature-sensitive items'
      }
    ],
    tips: [
      'Start with common patterns like *FROZEN* and *REFRIGERATED*',
      'Add your specific product naming patterns',
      'Shorter time limits for critical items like ice cream'
    ]
  },
  {
    id: 'aisle-congestion',
    name: 'Aisle Congestion Alert',
    description: 'Flag pallets stuck in aisles blocking movement',
    category: 'advanced',
    icon: MapPin,
    difficulty: 'intermediate',
    estimatedTime: '3 minutes',
    useCase: 'Traffic flow - keep aisles clear for operations',
    ruleType: 'LOCATION_SPECIFIC_STAGNANT',
    conditions: {
      location_pattern: 'AISLE*',
      time_threshold_hours: 2
    },
    parameters: {},
    configurableFields: [
      {
        key: 'location_pattern',
        label: 'Aisle location pattern',
        description: 'Pattern to match aisle locations (use * for wildcards)',
        type: 'text',
        defaultValue: 'AISLE*',
        suggestions: ['AISLE*', 'LANE*', 'CORRIDOR*', 'PICK*']
      },
      {
        key: 'time_threshold_hours',
        label: 'Maximum time in aisle (hours)',
        description: 'How long pallets can sit in aisles before alerting',
        type: 'number',
        defaultValue: 2,
        min: 0.5,
        max: 8,
        suggestions: [1, 2, 4, 6]
      }
    ],
    examples: [
      {
        scenario: 'High-traffic warehouse',
        configuration: { time_threshold_hours: 1, location_pattern: 'AISLE*' },
        expectedResult: 'Quick alerts for any pallets blocking aisles'
      },
      {
        scenario: 'Pick aisles monitoring',
        configuration: { time_threshold_hours: 4, location_pattern: 'PICK*' },
        expectedResult: 'Monitor picking aisles with longer grace period'
      }
    ],
    tips: [
      'Use patterns that match your location naming scheme',
      'Shorter times for main traffic aisles',
      'Consider different rules for pick vs. putaway aisles'
    ]
  },
  {
    id: 'capacity-violations',
    name: 'Overcapacity Prevention',
    description: 'Alert when locations exceed their storage limits',
    category: 'advanced',
    icon: AlertTriangle,
    difficulty: 'advanced',
    estimatedTime: '5 minutes',
    useCase: 'Safety & efficiency - prevent overloading locations',
    ruleType: 'OVERCAPACITY',
    conditions: {
      check_all_locations: true
    },
    parameters: {},
    configurableFields: [
      {
        key: 'capacity_buffer',
        label: 'Safety buffer (%)',
        description: 'Alert before reaching 100% capacity',
        type: 'number',
        defaultValue: 10,
        min: 0,
        max: 50,
        suggestions: [5, 10, 15, 20]
      },
      {
        key: 'priority_locations',
        label: 'High-priority locations',
        description: 'Locations that need stricter monitoring',
        type: 'text',
        defaultValue: 'DOCK*',
        suggestions: ['DOCK*', 'HAZMAT*', 'COOLER*', 'STAGING*']
      }
    ],
    examples: [
      {
        scenario: 'Safety-critical areas',
        configuration: { capacity_buffer: 5, priority_locations: 'HAZMAT*' },
        expectedResult: 'Early warnings for hazmat storage areas'
      },
      {
        scenario: 'General warehouse monitoring',
        configuration: { capacity_buffer: 15, priority_locations: 'DOCK*' },
        expectedResult: 'Buffer alerts for all locations, strict for docks'
      }
    ],
    tips: [
      'Set lower buffers for safety-critical areas',
      'Consider seasonal capacity variations',
      'Monitor dock doors more strictly than storage areas'
    ]
  },
  // NEW TEMPLATES - Missing rule types
  {
    id: 'data-integrity-check',
    name: 'Scanner Error Detection',
    description: 'Catch duplicate scans and invalid location codes',
    category: 'common',
    icon: AlertTriangle,
    difficulty: 'beginner',
    estimatedTime: '2 minutes',
    useCase: 'Data quality - prevent scanning errors',
    ruleType: 'DATA_INTEGRITY',
    conditions: {
      check_duplicate_scans: true,
      check_impossible_locations: true
    },
    parameters: {},
    configurableFields: [
      {
        key: 'check_duplicate_scans',
        label: 'Check for duplicate scans',
        description: 'Flag when same pallet is scanned multiple times',
        type: 'select',
        defaultValue: true,
        options: [
          { value: true, label: 'Enabled', description: 'Check for duplicate pallet IDs' },
          { value: false, label: 'Disabled', description: 'Skip duplicate scan checks' }
        ]
      },
      {
        key: 'check_impossible_locations',
        label: 'Check for invalid location codes',
        description: 'Flag locations that are clearly wrong (too long, special characters)',
        type: 'select',
        defaultValue: true,
        options: [
          { value: true, label: 'Enabled', description: 'Check for invalid location formats' },
          { value: false, label: 'Disabled', description: 'Skip location format checks' }
        ]
      }
    ],
    examples: [
      {
        scenario: 'Busy receiving dock with multiple scanners',
        configuration: { check_duplicate_scans: true, check_impossible_locations: true },
        expectedResult: 'Catch scanning errors and data entry mistakes in real-time'
      }
    ],
    tips: [
      'Run this check every 2-4 hours during busy periods',
      'Most common after shift changes or new employee training',
      'Essential for inventory accuracy'
    ]
  },
  {
    id: 'missing-locations',
    name: 'Find Lost Pallets',
    description: 'Locate pallets with no location assigned',
    category: 'common',
    icon: MapPin,
    difficulty: 'beginner',
    estimatedTime: '1 minute',
    useCase: 'Location tracking - find pallets that went missing',
    ruleType: 'MISSING_LOCATION',
    conditions: {},
    parameters: {},
    configurableFields: [],
    examples: [
      {
        scenario: 'After system update or network issues',
        configuration: {},
        expectedResult: 'Quickly identify pallets that lost their location data'
      }
    ],
    tips: [
      'Run immediately after any system maintenance',
      'Check hourly during high-volume periods',
      'Often caused by network interruptions during scanning'
    ]
  },
  {
    id: 'invalid-locations',
    name: 'Invalid Location Checker',
    description: 'Find pallets in non-existent locations',
    category: 'common',
    icon: AlertCircle,
    difficulty: 'beginner',
    estimatedTime: '2 minutes',
    useCase: 'Location validation - ensure all locations exist',
    ruleType: 'INVALID_LOCATION',
    conditions: {},
    parameters: {},
    configurableFields: [],
    examples: [
      {
        scenario: 'After warehouse layout changes',
        configuration: {},
        expectedResult: 'Find pallets assigned to old or incorrect location codes'
      }
    ],
    tips: [
      'Essential after any warehouse reconfiguration',
      'Run weekly as preventive maintenance',
      'Helps maintain location master data accuracy'
    ]
  },
  {
    id: 'product-restrictions',
    name: 'Product Storage Compliance',
    description: 'Ensure products are in approved locations only',
    category: 'advanced',
    icon: Package,
    difficulty: 'intermediate',
    estimatedTime: '4 minutes',
    useCase: 'Compliance - enforce product placement rules',
    ruleType: 'PRODUCT_INCOMPATIBILITY',
    conditions: {},
    parameters: {},
    configurableFields: [],
    examples: [
      {
        scenario: 'Food safety compliance in grocery warehouse',
        configuration: {},
        expectedResult: 'Prevent food items from being stored near chemicals or hazmat'
      }
    ],
    tips: [
      'Critical for food, pharmaceutical, and chemical warehouses',
      'Set up location restrictions in your location master first',
      'Run continuously for compliance-critical operations'
    ]
  },
  {
    id: 'location-setup-audit',
    name: 'Location Configuration Audit',
    description: 'Find inconsistent location type assignments',
    category: 'advanced',
    icon: Settings,
    difficulty: 'advanced',
    estimatedTime: '5 minutes',
    useCase: 'System maintenance - audit location setup',
    ruleType: 'LOCATION_MAPPING_ERROR',
    conditions: {
      validate_location_types: true,
      check_pattern_consistency: true
    },
    parameters: {},
    configurableFields: [
      {
        key: 'validate_location_types',
        label: 'Check location type consistency',
        description: 'Flag locations with conflicting type assignments',
        type: 'select',
        defaultValue: true,
        options: [
          { value: true, label: 'Enabled', description: 'Check for conflicting location types' },
          { value: false, label: 'Disabled', description: 'Skip location type validation' }
        ]
      },
      {
        key: 'check_pattern_consistency',
        label: 'Check naming pattern consistency',
        description: 'Validate location codes follow naming conventions',
        type: 'select',
        defaultValue: true,
        options: [
          { value: true, label: 'Enabled', description: 'Check naming pattern consistency' },
          { value: false, label: 'Disabled', description: 'Skip pattern validation' }
        ]
      }
    ],
    examples: [
      {
        scenario: 'After WMS configuration changes',
        configuration: { validate_location_types: true, check_pattern_consistency: true },
        expectedResult: 'Find and fix location setup inconsistencies'
      }
    ],
    tips: [
      'Run after any WMS updates or configuration changes',
      'Essential for maintaining data integrity',
      'Schedule monthly as preventive maintenance'
    ]
  }
]

export function SmartTemplates({ onTemplateSelect, onCancel }: SmartTemplatesProps) {
  const [selectedTemplate, setSelectedTemplate] = useState<SmartTemplate | null>(null)
  const [configuration, setConfiguration] = useState<Record<string, unknown>>({})
  const [currentStep, setCurrentStep] = useState<'browse' | 'configure'>('browse')

  const handleTemplateClick = (template: SmartTemplate) => {
    setSelectedTemplate(template)
    
    // Initialize configuration with default values
    const defaultConfig: Record<string, any> = {}
    template.configurableFields.forEach(field => {
      defaultConfig[field.key] = field.defaultValue
    })
    setConfiguration(defaultConfig)
    setCurrentStep('configure')
  }

  const handleCreateRule = () => {
    if (selectedTemplate) {
      // Create enhanced template data for rule creation
      const templateRuleData = {
        name: `${selectedTemplate.name} (Template)`,
        problem: selectedTemplate.id, // Use template ID as problem identifier
        ruleType: selectedTemplate.ruleType, // Pass the actual rule type
        template: selectedTemplate,
        configuration,
        timeframe: 'template-based',
        sensitivity: 3, // Default sensitivity
        areas: [],
        selectedSuggestions: [],
        advancedMode: false,
        isTemplate: true
      }
      onTemplateSelect(selectedTemplate, configuration, templateRuleData)
    }
  }

  const updateConfiguration = (key: string, value: any) => {
    setConfiguration(prev => ({ ...prev, [key]: value }))
  }

  const renderBrowseStep = () => (
    <div className="space-y-6">
      <div className="text-center space-y-2">
        <h2 className="text-2xl font-bold">Choose a Template</h2>
        <p className="text-muted-foreground">
          Start with a proven template and customize it for your needs
        </p>
      </div>

      {/* Common Templates */}
      <div className="space-y-4">
        <h3 className="text-lg font-semibold flex items-center gap-2">
          <Zap className="w-5 h-5 text-yellow-500" />
          Quick Start Templates
        </h3>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          {SMART_TEMPLATES.filter(t => t.category === 'common').map(template => (
            <TemplateCard 
              key={template.id} 
              template={template} 
              onClick={() => handleTemplateClick(template)}
            />
          ))}
        </div>
      </div>

      {/* Advanced Templates */}
      <div className="space-y-4">
        <h3 className="text-lg font-semibold flex items-center gap-2">
          <Users className="w-5 h-5 text-blue-500" />
          Advanced Templates
        </h3>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          {SMART_TEMPLATES.filter(t => t.category === 'advanced').map(template => (
            <TemplateCard 
              key={template.id} 
              template={template} 
              onClick={() => handleTemplateClick(template)}
            />
          ))}
        </div>
      </div>

      <div className="flex justify-center">
        <Button variant="outline" onClick={onCancel}>
          Cancel
        </Button>
      </div>
    </div>
  )

  const renderConfigureStep = () => {
    if (!selectedTemplate) return null

    return (
      <div className="space-y-6">
        <div className="flex items-center gap-4">
          <Button 
            variant="ghost" 
            onClick={() => setCurrentStep('browse')}
            className="p-2"
          >
            ← Back
          </Button>
          <div>
            <h2 className="text-xl font-bold">Configure: {selectedTemplate.name}</h2>
            <p className="text-muted-foreground">{selectedTemplate.description}</p>
          </div>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* Configuration Form */}
          <div className="lg:col-span-2 space-y-6">
            <Card>
              <CardHeader>
                <CardTitle>Customize Your Rule</CardTitle>
                <p className="text-muted-foreground">
                  Adjust these settings to match your warehouse operations
                </p>
              </CardHeader>
              <CardContent className="space-y-6">
                {selectedTemplate.configurableFields.map(field => (
                  <div key={field.key} className="space-y-3">
                    <Label className="text-base font-medium">{field.label}</Label>
                    <p className="text-sm text-muted-foreground">{field.description}</p>
                    
                    {renderConfigField(field, configuration[field.key], (value) => updateConfiguration(field.key, value))}

                    {field.suggestions && (
                      <div className="flex flex-wrap gap-2">
                        <span className="text-sm text-muted-foreground">Quick options:</span>
                        {field.suggestions.map((suggestion, idx) => (
                          <Button
                            key={idx}
                            variant="outline"
                            size="sm"
                            onClick={() => updateConfiguration(field.key, suggestion)}
                            className="h-7 text-xs"
                          >
                            {field.type === 'number' && field.key.includes('percentage') ? `${suggestion}%` : suggestion}
                          </Button>
                        ))}
                      </div>
                    )}
                  </div>
                ))}
              </CardContent>
            </Card>

            <div className="flex justify-end gap-3">
              <Button variant="outline" onClick={() => setCurrentStep('browse')}>
                Back to Templates
              </Button>
              <Button onClick={handleCreateRule}>
                <CheckCircle className="w-4 h-4 mr-2" />
                Create This Rule
              </Button>
            </div>
          </div>

          {/* Preview & Help */}
          <div className="space-y-4">
            <PreviewCard template={selectedTemplate} configuration={configuration} />
            <ExamplesCard template={selectedTemplate} />
            <TipsCard template={selectedTemplate} />
          </div>
        </div>
      </div>
    )
  }

  const renderConfigField = (field: any, value: any, onChange: (value: any) => void) => {
    switch (field.type) {
      case 'number':
        return (
          <Input
            type="number"
            min={field.min}
            max={field.max}
            value={value || ''}
            onChange={(e) => onChange(parseInt(e.target.value) || field.defaultValue)}
            placeholder={`Default: ${field.defaultValue}`}
          />
        )

      case 'text':
        return (
          <Input
            value={value || ''}
            onChange={(e) => onChange(e.target.value)}
            placeholder={`Default: ${field.defaultValue}`}
          />
        )

      case 'select':
        return (
          <Select value={value} onValueChange={onChange}>
            <SelectTrigger>
              <SelectValue />
            </SelectTrigger>
            <SelectContent>
              {field.options?.map((option: any) => (
                <SelectItem key={option.value} value={option.value}>
                  <div>
                    <div className="font-medium">{option.label}</div>
                    {option.description && (
                      <div className="text-xs text-muted-foreground">{option.description}</div>
                    )}
                  </div>
                </SelectItem>
              ))}
            </SelectContent>
          </Select>
        )

      case 'multiselect':
        const currentValues = Array.isArray(value) ? value : []
        return (
          <div className="space-y-2">
            {field.options?.map((option: any) => (
              <label key={option.value} className="flex items-start space-x-3 cursor-pointer">
                <input
                  type="checkbox"
                  checked={currentValues.includes(option.value)}
                  onChange={(e) => {
                    const newValues = e.target.checked
                      ? [...currentValues, option.value]
                      : currentValues.filter((v: any) => v !== option.value)
                    onChange(newValues)
                  }}
                  className="rounded border-gray-300 mt-1"
                />
                <div>
                  <div className="font-medium">{option.label}</div>
                  {option.description && (
                    <div className="text-sm text-muted-foreground">{option.description}</div>
                  )}
                </div>
              </label>
            ))}
          </div>
        )

      default:
        return null
    }
  }

  return (
    <div className="max-w-6xl mx-auto p-6">
      {currentStep === 'browse' ? renderBrowseStep() : renderConfigureStep()}
    </div>
  )
}

function TemplateCard({ template, onClick }: { template: SmartTemplate; onClick: () => void }) {
  const getDifficultyColor = (difficulty: string) => {
    switch (difficulty) {
      case 'beginner': return 'bg-green-100 text-green-800'
      case 'intermediate': return 'bg-yellow-100 text-yellow-800'
      case 'advanced': return 'bg-red-100 text-red-800'
      default: return 'bg-gray-100 text-gray-800'
    }
  }

  return (
    <Card className="cursor-pointer hover:shadow-md transition-shadow group" onClick={onClick}>
      <CardHeader className="pb-3">
        <div className="flex items-start justify-between">
          <div className="flex items-center gap-3">
            <div className="p-2 rounded-lg bg-primary/10">
              <template.icon className="w-5 h-5 text-primary" />
            </div>
            <div>
              <CardTitle className="text-lg group-hover:text-primary transition-colors">
                {template.name}
              </CardTitle>
              <p className="text-sm text-muted-foreground">{template.description}</p>
            </div>
          </div>
          <ArrowRight className="w-4 h-4 text-muted-foreground group-hover:text-primary transition-colors" />
        </div>
      </CardHeader>
      <CardContent>
        <div className="space-y-3">
          <p className="text-sm">{template.useCase}</p>
          <div className="flex items-center gap-2 flex-wrap">
            <Badge className={getDifficultyColor(template.difficulty)}>
              {template.difficulty}
            </Badge>
            <Badge variant="outline">
              <Clock className="w-3 h-3 mr-1" />
              {template.estimatedTime}
            </Badge>
          </div>
        </div>
      </CardContent>
    </Card>
  )
}

function PreviewCard({ template, configuration }: { template: SmartTemplate; configuration: Record<string, any> }) {
  const previewConditions = { ...template.conditions, ...configuration }
  
  return (
    <Card>
      <CardHeader>
        <CardTitle className="text-base">Rule Preview</CardTitle>
      </CardHeader>
      <CardContent className="space-y-3">
        <div className="space-y-2">
          <div className="text-sm font-medium">This rule will trigger when:</div>
          {Object.entries(previewConditions).map(([key, value]) => (
            <div key={key} className="text-sm bg-muted p-2 rounded flex items-center gap-2">
              <CheckCircle className="w-3 h-3 text-green-500 flex-shrink-0" />
              <span>{formatConditionPreview(key, value)}</span>
            </div>
          ))}
        </div>
      </CardContent>
    </Card>
  )
}

function ExamplesCard({ template }: { template: SmartTemplate }) {
  return (
    <Card>
      <CardHeader>
        <CardTitle className="text-base flex items-center gap-2">
          <Lightbulb className="w-4 h-4" />
          Examples
        </CardTitle>
      </CardHeader>
      <CardContent className="space-y-4">
        {template.examples.map((example, idx) => (
          <div key={idx} className="space-y-2">
            <div className="font-medium text-sm">{example.scenario}</div>
            <div className="text-xs text-muted-foreground">
              Result: {example.expectedResult}
            </div>
          </div>
        ))}
      </CardContent>
    </Card>
  )
}

function TipsCard({ template }: { template: SmartTemplate }) {
  return (
    <Card>
      <CardHeader>
        <CardTitle className="text-base flex items-center gap-2">
          <Info className="w-4 h-4" />
          Tips
        </CardTitle>
      </CardHeader>
      <CardContent>
        <ul className="space-y-2">
          {template.tips.map((tip, idx) => (
            <li key={idx} className="text-sm flex items-start gap-2">
              <span className="text-primary mt-1">•</span>
              <span>{tip}</span>
            </li>
          ))}
        </ul>
      </CardContent>
    </Card>
  )
}

function formatConditionPreview(key: string, value: any): string {
  switch (key) {
    case 'time_threshold_hours':
      return `Pallets older than ${value} hours`
    case 'time_threshold_minutes':
      return `Pallets older than ${value} minutes`
    case 'location_types':
      return `In ${Array.isArray(value) ? value.join(', ') : value} areas`
    case 'location_pattern':
      return `Location matches "${value}"`
    case 'completion_threshold':
      return `${value}% of lot is already stored`
    case 'product_patterns':
      return `Product matches ${Array.isArray(value) ? value.join(' or ') : value}`
    default:
      return `${key}: ${value}`
  }
}