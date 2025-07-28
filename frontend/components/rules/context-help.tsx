"use client"

import { useState } from 'react'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { Alert, AlertDescription } from '@/components/ui/alert'
import { 
  HelpCircle,
  Info,
  CheckCircle,
  AlertTriangle,
  Lightbulb,
  BookOpen,
  ChevronRight,
  Clock,
  MapPin,
  Package,
  Shield,
  X
} from 'lucide-react'

interface ContextHelpProps {
  context: 'field' | 'rule_type' | 'validation' | 'general'
  topic?: string
  ruleType?: string
  fieldKey?: string
  validationErrors?: string[]
  className?: string
}

interface HelpContent {
  title: string
  description: string
  tips?: string[]
  examples?: Array<{
    label: string
    value: string
    description: string
  }>
  warnings?: string[]
  relatedTopics?: string[]
}

const HELP_DATABASE: Record<string, HelpContent> = {
  // Field-specific help
  'field:time_threshold_hours': {
    title: 'Time Threshold (Hours)',
    description: 'How many hours a pallet can sit before being flagged as stagnant.',
    tips: [
      'Start with 6-8 hours for most warehouse operations',
      'Use shorter times (2-4 hours) for high-throughput facilities',
      'Consider longer times (12-24 hours) for weekend or holiday periods'
    ],
    examples: [
      { label: 'Fast turnaround', value: '4', description: 'Quick processing facility' },
      { label: 'Standard operation', value: '6', description: 'Typical warehouse timing' },
      { label: 'Bulk processing', value: '12', description: 'Large lots with slower processing' }
    ],
    warnings: [
      'Very short times (< 2 hours) may create too many false alerts',
      'Very long times (> 24 hours) may miss real issues'
    ]
  },
  'field:location_types': {
    title: 'Location Types',
    description: 'The types of warehouse areas to monitor with this rule.',
    tips: [
      'RECEIVING: Where pallets first arrive from trucks',
      'TRANSITIONAL: Temporary staging areas between receiving and storage',
      'FINAL: Long-term storage locations',
      'UNKNOWN: Locations that haven\'t been classified'
    ],
    examples: [
      { label: 'Intake monitoring', value: 'RECEIVING', description: 'Focus on newly arrived pallets' },
      { label: 'Flow monitoring', value: 'RECEIVING, TRANSITIONAL', description: 'Monitor pallets in motion' },
      { label: 'Full coverage', value: 'All types', description: 'Monitor everywhere except final storage' }
    ]
  },
  'field:location_pattern': {
    title: 'Location Pattern',
    description: 'A pattern to match location codes using wildcards (* and ?).',
    tips: [
      'Use * to match any characters: AISLE* matches AISLE-A1, AISLE-B2, etc.',
      'Use ? to match single character: DOCK? matches DOCK1, DOCK2, etc.',
      'Be specific enough to avoid matching unintended locations'
    ],
    examples: [
      { label: 'All aisles', value: 'AISLE*', description: 'Matches any location starting with AISLE' },
      { label: 'Specific zone', value: 'ZONE-A*', description: 'Matches only Zone A locations' },
      { label: 'Dock doors', value: 'DOCK*', description: 'Matches all dock door locations' }
    ],
    warnings: [
      'Pattern * matches everything - be more specific',
      'Test your pattern against actual location names'
    ]
  },
  'field:completion_threshold': {
    title: 'Completion Threshold',
    description: 'What percentage of a lot must be stored before flagging remaining pallets.',
    tips: [
      '80% is a good starting point for most operations',
      'Higher percentages (90-95%) catch only the most critical stragglers',
      'Lower percentages (70-75%) provide earlier warnings'
    ],
    examples: [
      { label: 'Early warning', value: '70%', description: 'Flag stragglers early in the process' },
      { label: 'Standard', value: '80%', description: 'Balanced approach for most operations' },
      { label: 'Critical only', value: '95%', description: 'Only flag nearly complete lots' }
    ]
  },
  'field:product_patterns': {
    title: 'Product Patterns',
    description: 'Patterns to match product descriptions for temperature-sensitive items.',
    tips: [
      'Use wildcards (*) to match partial text: *FROZEN* matches any description containing FROZEN',
      'Add multiple patterns to catch variations in naming',
      'Consider your actual product naming conventions'
    ],
    examples: [
      { label: 'Frozen goods', value: '*FROZEN*', description: 'Any product description containing FROZEN' },
      { label: 'Dairy products', value: '*DAIRY*, *MILK*, *CHEESE*', description: 'Multiple patterns for dairy' },
      { label: 'Ice cream', value: '*ICE CREAM*, *GELATO*', description: 'Specific frozen desserts' }
    ]
  },

  // Rule type help
  'rule_type:STAGNANT_PALLETS': {
    title: 'Stagnant Pallets Detection',
    description: 'Finds pallets that have been sitting in the same location for too long, typically in receiving or staging areas.',
    tips: [
      'Most effective for monitoring receiving areas',
      'Helps prevent bottlenecks in warehouse flow',
      'Can be customized for different location types'
    ],
    examples: [
      { label: 'Basic setup', value: '6 hours in RECEIVING', description: 'Alert for pallets stuck in receiving' },
      { label: 'Multi-area', value: '4 hours in RECEIVING or TRANSITIONAL', description: 'Monitor multiple area types' }
    ]
  },
  'rule_type:UNCOORDINATED_LOTS': {
    title: 'Uncoordinated Lots Detection',
    description: 'Identifies pallets that remain in receiving when most of their lot has already been processed and stored.',
    tips: [
      'Helps ensure complete lot processing',
      'Prevents stragglers from being forgotten',
      'Threshold can be adjusted based on lot sizes'
    ],
    examples: [
      { label: 'Standard', value: '80% completion threshold', description: 'Flag stragglers when lot is mostly done' },
      { label: 'Strict', value: '90% completion threshold', description: 'Only flag near-complete lots' }
    ]
  },
  'rule_type:TEMPERATURE_ZONE_MISMATCH': {
    title: 'Temperature Zone Violations',
    description: 'Ensures temperature-sensitive products are stored in appropriate climate-controlled areas.',
    tips: [
      'Critical for food safety compliance',
      'Define clear product patterns for frozen/refrigerated items',
      'Set appropriate grace periods for movement'
    ],
    examples: [
      { label: 'Frozen products', value: 'FROZEN items not in COOLER zones', description: 'Ensure frozen goods stay cold' },
      { label: 'Dairy monitoring', value: 'DAIRY items with 30-minute grace period', description: 'Allow time for movement' }
    ]
  },

  // Validation help
  'validation:field_not_found': {
    title: 'Field Not Found',
    description: 'The rule references a data field that doesn\'t exist in your inventory data.',
    tips: [
      'Check your data file column names',
      'Ensure field names match exactly (case-sensitive)',
      'Common fields: pallet_id, location, creation_date, receipt_number'
    ],
    warnings: [
      'Rule will not work properly until this is fixed',
      'Double-check your data file format'
    ]
  },
  'validation:invalid_json': {
    title: 'Invalid JSON Format',
    description: 'The rule conditions contain syntax errors that prevent proper parsing.',
    tips: [
      'Check for missing commas between items',
      'Ensure all quotes are properly matched',
      'Use the visual rule builder to avoid syntax errors'
    ]
  },
  'validation:time_threshold_too_high': {
    title: 'Time Threshold Too High',
    description: 'The time threshold seems unusually high and may miss important issues.',
    tips: [
      'Consider if such a long threshold is intentional',
      'Most operations work well with 2-24 hour thresholds',
      'Very high thresholds may delay problem detection'
    ]
  },

  // General help topics
  'general:getting_started': {
    title: 'Getting Started with Rules',
    description: 'Rules help you automatically detect issues in your warehouse operations.',
    tips: [
      'Start with simple rules like "Forgotten Pallets"',
      'Use the Quick Rule Creator for common scenarios',
      'Test rules with sample data before activating',
      'Monitor rule performance and adjust as needed'
    ]
  },
  'general:rule_priorities': {
    title: 'Setting Rule Priorities',
    description: 'Priorities help you focus on the most important alerts first.',
    tips: [
      'VERY HIGH: Safety issues, regulatory violations',
      'HIGH: Operational bottlenecks, customer impact',
      'MEDIUM: Process improvements, efficiency',
      'LOW: Nice-to-know information, trends'
    ]
  },
  'general:testing_rules': {
    title: 'Testing Your Rules',
    description: 'Always test rules with real data before putting them into production.',
    tips: [
      'Use the Preview function to see expected results',
      'Start with inactive rules to observe behavior',
      'Review alerts for false positives',
      'Adjust thresholds based on real performance'
    ]
  }
}

export function ContextHelp({ 
  context, 
  topic, 
  ruleType, 
  fieldKey, 
  validationErrors, 
  className = '' 
}: ContextHelpProps) {
  const [isExpanded, setIsExpanded] = useState(false)

  const getHelpKey = (): string => {
    switch (context) {
      case 'field':
        return `field:${fieldKey}`
      case 'rule_type':
        return `rule_type:${ruleType}`
      case 'validation':
        return `validation:${topic}`
      case 'general':
        return `general:${topic}`
      default:
        return 'general:getting_started'
    }
  }

  const helpContent = HELP_DATABASE[getHelpKey()]
  
  if (!helpContent) {
    return null
  }

  const getContextIcon = () => {
    switch (context) {
      case 'validation':
        return validationErrors?.length ? AlertTriangle : CheckCircle
      case 'field':
        return HelpCircle
      case 'rule_type':
        return Info
      default:
        return BookOpen
    }
  }

  const getContextColor = () => {
    switch (context) {
      case 'validation':
        return validationErrors?.length ? 'border-red-200 bg-red-50' : 'border-green-200 bg-green-50'
      case 'field':
        return 'border-blue-200 bg-blue-50'
      default:
        return 'border-gray-200 bg-gray-50'
    }
  }

  const ContextIcon = getContextIcon()

  return (
    <Card className={`${getContextColor()} ${className}`}>
      <CardHeader className="pb-3">
        <div className="flex items-center justify-between">
          <CardTitle className="text-sm flex items-center gap-2">
            <ContextIcon className="w-4 h-4" />
            {helpContent.title}
          </CardTitle>
          <Button
            variant="ghost"
            size="sm"
            onClick={() => setIsExpanded(!isExpanded)}
            className="p-1 h-auto"
          >
            {isExpanded ? <X className="w-4 h-4" /> : <ChevronRight className="w-4 h-4" />}
          </Button>
        </div>
      </CardHeader>
      
      {(isExpanded || context === 'validation') && (
        <CardContent className="pt-0 space-y-4">
          <p className="text-sm">{helpContent.description}</p>

          {/* Validation Errors */}
          {context === 'validation' && validationErrors && validationErrors.length > 0 && (
            <Alert className="border-red-200 bg-red-50">
              <AlertTriangle className="h-4 w-4 text-red-600" />
              <AlertDescription>
                <ul className="list-disc list-inside space-y-1">
                  {validationErrors.map((error, idx) => (
                    <li key={idx} className="text-sm text-red-800">{error}</li>
                  ))}
                </ul>
              </AlertDescription>
            </Alert>
          )}

          {/* Tips */}
          {helpContent.tips && helpContent.tips.length > 0 && (
            <div className="space-y-2">
              <h4 className="text-sm font-medium flex items-center gap-1">
                <Lightbulb className="w-4 h-4" />
                Tips
              </h4>
              <ul className="space-y-1">
                {helpContent.tips.map((tip, idx) => (
                  <li key={idx} className="text-sm flex items-start gap-2">
                    <span className="text-primary mt-1">•</span>
                    <span>{tip}</span>
                  </li>
                ))}
              </ul>
            </div>
          )}

          {/* Examples */}
          {helpContent.examples && helpContent.examples.length > 0 && (
            <div className="space-y-2">
              <h4 className="text-sm font-medium">Examples</h4>
              <div className="space-y-2">
                {helpContent.examples.map((example, idx) => (
                  <div key={idx} className="bg-white/50 p-2 rounded border">
                    <div className="flex items-center justify-between">
                      <span className="font-medium text-sm">{example.label}</span>
                      <Badge variant="outline" className="text-xs">{example.value}</Badge>
                    </div>
                    <p className="text-xs text-muted-foreground mt-1">{example.description}</p>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Warnings */}
          {helpContent.warnings && helpContent.warnings.length > 0 && (
            <Alert>
              <AlertTriangle className="h-4 w-4" />
              <AlertDescription>
                <ul className="list-disc list-inside space-y-1">
                  {helpContent.warnings.map((warning, idx) => (
                    <li key={idx} className="text-sm">{warning}</li>
                  ))}
                </ul>
              </AlertDescription>
            </Alert>
          )}
        </CardContent>
      )}
    </Card>
  )
}

// Inline help component for form fields
export function InlineFieldHelp({ 
  fieldKey, 
  value, 
  className = '' 
}: { 
  fieldKey: string
  value?: any
  className?: string 
}) {
  const [showHelp, setShowHelp] = useState(false)
  
  const getValidationState = (fieldKey: string, value: any) => {
    const warnings: string[] = []
    
    switch (fieldKey) {
      case 'time_threshold_hours':
        if (value > 24) warnings.push('Very high threshold may miss issues')
        if (value < 1) warnings.push('Very low threshold may cause false alerts')
        break
      case 'completion_threshold':
        if (value < 50) warnings.push('Low threshold may be too aggressive')
        if (value > 95) warnings.push('High threshold may miss stragglers')
        break
      case 'location_pattern':
        if (value === '*') warnings.push('Pattern matches everything')
        break
    }
    
    return warnings
  }

  const warnings = getValidationState(fieldKey, value)
  const hasIssues = warnings.length > 0

  return (
    <div className={`relative ${className}`}>
      <Button
        variant="ghost"
        size="sm"
        onClick={() => setShowHelp(!showHelp)}
        className={`p-1 h-auto ${hasIssues ? 'text-orange-600' : 'text-muted-foreground'}`}
      >
        <HelpCircle className="w-4 h-4" />
      </Button>
      
      {showHelp && (
        <div className="absolute z-10 top-8 right-0 w-80">
          <ContextHelp
            context="field"
            fieldKey={fieldKey}
            validationErrors={warnings}
          />
        </div>
      )}
    </div>
  )
}

// Smart help suggestions based on context
export function SmartHelpSuggestions({ 
  ruleType, 
  currentFields,
  className = '' 
}: { 
  ruleType?: string
  currentFields?: Record<string, any>
  className?: string 
}) {
  const getSuggestions = () => {
    const suggestions: Array<{ title: string; description: string; action: string }> = []
    
    if (ruleType === 'STAGNANT_PALLETS') {
      suggestions.push({
        title: 'Consider location types',
        description: 'Monitor RECEIVING and TRANSITIONAL areas for best results',
        action: 'Add location_types condition'
      })
      
      if (!currentFields?.time_threshold_hours) {
        suggestions.push({
          title: 'Set time threshold',
          description: 'Start with 6-8 hours for typical operations',
          action: 'Add time threshold'
        })
      }
    }
    
    if (ruleType === 'TEMPERATURE_ZONE_MISMATCH') {
      suggestions.push({
        title: 'Define product patterns',
        description: 'Use patterns like *FROZEN* to catch temperature-sensitive items',
        action: 'Add product patterns'
      })
    }
    
    return suggestions
  }

  const suggestions = getSuggestions()
  
  if (suggestions.length === 0) {
    return null
  }

  return (
    <Card className={`border-blue-200 bg-blue-50 ${className}`}>
      <CardHeader className="pb-3">
        <CardTitle className="text-sm flex items-center gap-2">
          <Lightbulb className="w-4 h-4 text-blue-600" />
          Suggestions
        </CardTitle>
      </CardHeader>
      <CardContent className="pt-0">
        <div className="space-y-3">
          {suggestions.map((suggestion, idx) => (
            <div key={idx} className="flex items-start gap-3">
              <CheckCircle className="w-4 h-4 text-blue-600 mt-0.5 flex-shrink-0" />
              <div>
                <h5 className="font-medium text-sm text-blue-900">{suggestion.title}</h5>
                <p className="text-xs text-blue-700">{suggestion.description}</p>
              </div>
            </div>
          ))}
        </div>
      </CardContent>
    </Card>
  )
}