"use client"

import React, { useState, useEffect } from 'react'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { Slider } from '@/components/ui/slider'
import { Alert, AlertDescription } from '@/components/ui/alert'
import { 
  Clock,
  MapPin,
  Package,
  AlertTriangle,
  CheckCircle,
  ArrowRight,
  ArrowLeft,
  Eye,
  Lightbulb,
  Users,
  TrendingUp,
  Zap,
  Target,
  Timer,
  Thermometer,
  Truck,
  WarehouseIcon as Warehouse,
  ShoppingCart,
  AlertCircle,
  Settings,
  Sparkles,
  Brain,
  Plus,
  X,
  ChevronDown,
  ChevronUp,
  BarChart3,
  Activity,
  Layers,
  Wand2,
  Info
} from 'lucide-react'

// Enhanced warehouse problems with more context
const WAREHOUSE_PROBLEMS = [
  {
    id: 'traffic-jams',
    title: 'Pallets Creating Traffic Jams',
    description: 'Pallets blocking aisles and creating bottlenecks',
    icon: Truck,
    illustration: '🚛➡️📦📦📦⛔', 
    realWorldExample: 'Like when forklifts can\'t get through aisle 3 because pallets are scattered everywhere',
    businessImpact: 'Costs 2-3 hours of overtime per occurrence',
    frequency: 'Happens 2-4 times per week in busy warehouses',
    category: 'flow',
    color: 'bg-orange-100 border-orange-300 text-orange-800',
    smartSuggestions: [
      'Most warehouses your size use 2-4 hour limits for aisles',
      'Consider different limits for main vs. side aisles',
      'Peak hours (10am-2pm) might need stricter rules'
    ],
    relatedConditions: [
      { field: 'location_priority', label: 'High-traffic areas get priority', suggested: true },
      { field: 'time_of_day', label: 'Stricter during peak hours', suggested: false },
      { field: 'pallet_count', label: 'Alert when multiple pallets in same aisle', suggested: true }
    ]
  },
  {
    id: 'forgotten-items',
    title: 'Items Getting "Forgotten"',
    description: 'Pallets sitting in receiving way too long',
    icon: Clock,
    illustration: '📦💤⏰❗',
    realWorldExample: 'Like that pallet of dog food that sat in receiving for 3 days last month',
    businessImpact: 'Delays customer orders and wastes storage space',
    frequency: 'Usually 5-10 items per day get forgotten',
    category: 'time',
    color: 'bg-red-100 border-red-300 text-red-800',
    smartSuggestions: [
      'Grocery warehouses typically use 4-6 hours',
      'Electronics/high-value items often use 2-3 hours',
      'Consider shorter times for perishable goods'
    ],
    relatedConditions: [
      { field: 'product_value', label: 'High-value items get priority', suggested: true },
      { field: 'perishable_flag', label: 'Shorter time for perishables', suggested: true },
      { field: 'customer_priority', label: 'VIP customer orders get alerts sooner', suggested: false }
    ]
  },
  {
    id: 'temperature-violations',
    title: 'Cold Products Getting Warm',
    description: 'Frozen/refrigerated items in wrong temperature zones',
    icon: Thermometer,
    illustration: '🧊➡️🔥❌',
    realWorldExample: 'Like when frozen vegetables end up in the ambient storage area',
    businessImpact: 'Product spoilage can cost $500-2000 per incident',
    frequency: 'Critical - even one incident is too many',
    category: 'safety',
    color: 'bg-blue-100 border-blue-300 text-blue-800',
    smartSuggestions: [
      'Food safety requires immediate alerts (0-15 minutes)',
      'Different products have different temperature tolerances',
      'Consider grace periods for brief transfers'
    ],
    relatedConditions: [
      { field: 'product_temperature_category', label: 'Different rules for frozen vs refrigerated', suggested: true },
      { field: 'transfer_in_progress', label: 'Ignore items being actively moved', suggested: true },
      { field: 'emergency_bypass', label: 'Allow manual overrides for maintenance', suggested: false }
    ]
  },
  {
    id: 'incomplete-deliveries',
    title: 'Incomplete Truck Unloading',
    description: 'Some pallets left behind when truck is "done"',
    icon: ShoppingCart,
    illustration: '🚛📦📦✅ 📦❓',
    realWorldExample: 'Like when 90% of a truck is unloaded but 2 pallets are still sitting in receiving',
    businessImpact: 'Causes delivery delays and customer complaints',
    frequency: 'Happens with 1 in 10 large deliveries',
    category: 'completion',
    color: 'bg-purple-100 border-purple-300 text-purple-800',
    smartSuggestions: [
      'Most effective at 80-90% completion threshold',
      'Smaller deliveries might need different rules',
      'Consider truck size in the calculation'
    ],
    relatedConditions: [
      { field: 'delivery_size', label: 'Different thresholds for small vs large trucks', suggested: true },
      { field: 'delivery_priority', label: 'Rush deliveries get immediate alerts', suggested: false },
      { field: 'dock_assignment', label: 'Different rules per dock door', suggested: true }
    ]
  }
]

// Enhanced time options with smart context
const TIME_OPTIONS = [
  { 
    id: 'end-of-shift', 
    label: 'End of current shift', 
    hours: 8, 
    description: 'Items should be moved before shift ends',
    smartNote: 'Most popular for daily operations',
    warehouseTypes: ['general', 'retail', 'manufacturing']
  },
  { 
    id: 'next-morning', 
    label: 'By next morning', 
    hours: 16, 
    description: 'Overnight items are flagged',
    smartNote: 'Good for 24/7 operations',
    warehouseTypes: ['distribution', 'fulfillment', 'logistics']
  },
  { 
    id: 'same-day', 
    label: 'Same day', 
    hours: 24, 
    description: 'Nothing should sit overnight',
    smartNote: 'Strict but comprehensive',
    warehouseTypes: ['perishable', 'high-value', 'just-in-time']
  },
  { 
    id: 'rush-processing', 
    label: 'Rush processing', 
    hours: 4, 
    description: 'For high-priority or time-sensitive items',
    smartNote: 'Use for critical operations',
    warehouseTypes: ['medical', 'emergency', 'express']
  },
  { 
    id: 'custom', 
    label: 'Custom timing', 
    hours: 0, 
    description: 'Set your own specific timeframe',
    smartNote: 'Full control over timing',
    warehouseTypes: ['all']
  }
]

// Smart sensitivity levels with predictions
const SENSITIVITY_LEVELS = [
  { 
    level: 1, 
    label: 'Very Relaxed', 
    description: 'Only catch the most obvious problems',
    alertsPerWeek: '2-5 alerts',
    example: 'Only pallets sitting for days',
    falsePositiveRate: '< 5%',
    coverage: '~40% of issues caught'
  },
  { 
    level: 2, 
    label: 'Relaxed', 
    description: 'Catch clear problems without being picky',
    alertsPerWeek: '5-15 alerts',
    example: 'Pallets sitting longer than usual',
    falsePositiveRate: '< 10%',
    coverage: '~60% of issues caught'
  },
  { 
    level: 3, 
    label: 'Balanced', 
    description: 'Good balance of catching issues vs noise',
    alertsPerWeek: '10-25 alerts',
    example: 'Most warehouses start here',
    falsePositiveRate: '< 15%',
    coverage: '~75% of issues caught'
  },
  { 
    level: 4, 
    label: 'Strict', 
    description: 'Catch problems early, more alerts',
    alertsPerWeek: '20-40 alerts',
    example: 'Be proactive about potential issues',
    falsePositiveRate: '< 25%',
    coverage: '~85% of issues caught'
  },
  { 
    level: 5, 
    label: 'Very Strict', 
    description: 'Catch everything, expect many alerts',
    alertsPerWeek: '40+ alerts',
    example: 'Zero tolerance approach',
    falsePositiveRate: '< 35%',
    coverage: '~95% of issues caught'
  }
]

interface EnhancedSmartBuilderProps {
  onRuleCreate?: (ruleData: any) => void
  onCancel?: () => void
}

export function EnhancedSmartBuilder({ onRuleCreate, onCancel }: EnhancedSmartBuilderProps) {
  const [currentStep, setCurrentStep] = useState<'problem' | 'scenario' | 'smart-enhance' | 'advanced' | 'preview'>('problem')
  const [selectedProblem, setSelectedProblem] = useState<string | null>(null)
  const [ruleName, setRuleName] = useState('')
  const [selectedTimeframe, setSelectedTimeframe] = useState<string>('end-of-shift')
  const [customHours, setCustomHours] = useState(6)
  const [sensitivity, setSensitivity] = useState(3)
  const [selectedAreas, setSelectedAreas] = useState<string[]>(['receiving'])
  const [advancedMode, setAdvancedMode] = useState(false)
  const [selectedSuggestions, setSelectedSuggestions] = useState<string[]>([])
  const [additionalConditions, setAdditionalConditions] = useState<any[]>([])
  const [showSmartSuggestions, setShowSmartSuggestions] = useState(true)
  
  const problem = WAREHOUSE_PROBLEMS.find(p => p.id === selectedProblem)
  const timeOption = TIME_OPTIONS.find(t => t.id === selectedTimeframe)
  const sensitivityInfo = SENSITIVITY_LEVELS.find(s => s.level === sensitivity)

  // Smart suggestions based on context
  const getSmartSuggestions = () => {
    if (!problem) return []
    
    const baseSuggestions = problem.smartSuggestions
    const contextualSuggestions = []
    
    // Add time-based suggestions
    if (selectedTimeframe === 'end-of-shift') {
      contextualSuggestions.push('Consider different rules for night vs day shifts')
    }
    if (selectedTimeframe === 'custom' && customHours <= 2) {
      contextualSuggestions.push('Very short timeframes work best for critical items')
    }
    if (selectedTimeframe === 'same-day' && selectedAreas.includes('receiving')) {
      contextualSuggestions.push('24-hour receiving rules catch most overnight issues')
    }
    
    // Add sensitivity-based suggestions
    if (sensitivity >= 4) {
      contextualSuggestions.push('High sensitivity works best with good data quality')
    }
    if (sensitivity <= 2) {
      contextualSuggestions.push('Low sensitivity reduces alert fatigue but may miss issues')
    }
    
    // Add area-based suggestions
    if (selectedAreas.includes('aisles') && problem.id === 'traffic-jams') {
      contextualSuggestions.push('Aisle monitoring prevents 80% of traffic jam incidents')
    }
    if (selectedAreas.includes('receiving') && selectedAreas.includes('staging')) {
      contextualSuggestions.push('Monitoring both receiving and staging catches handoff delays')
    }
    
    return [...baseSuggestions, ...contextualSuggestions]
  }

  // Intelligent parameter recommendations based on warehouse context
  const getIntelligentRecommendations = (): {
    timeframe: string;
    sensitivity: string;
    areas: string;
    businessImpact: string;
  } => {
    if (!problem) return {
      timeframe: '',
      sensitivity: '',
      areas: '',
      businessImpact: ''
    }
    
    const recommendations = {
      timeframe: '',
      sensitivity: '',
      areas: '',
      businessImpact: ''
    }
    
    // Time recommendations based on problem type
    if (problem.id === 'temperature-violations') {
      recommendations.timeframe = 'Use 15-30 minutes max - temperature compliance is critical'
      recommendations.sensitivity = 'Maximum sensitivity recommended for food safety'
    } else if (problem.id === 'forgotten-items') {
      recommendations.timeframe = 'Most warehouses find 4-6 hours optimal for receiving items'
      recommendations.sensitivity = 'Balanced sensitivity catches 75% of issues with minimal noise'
    } else if (problem.id === 'traffic-jams') {
      recommendations.timeframe = '2-4 hours prevents most bottlenecks without over-alerting'
      recommendations.sensitivity = 'Strict sensitivity helps during peak hours (10am-2pm)'
    }
    
    // Area recommendations
    if (selectedAreas.length === 1) {
      recommendations.areas = 'Consider monitoring related areas for better coverage'
    } else if (selectedAreas.length > 3) {
      recommendations.areas = 'Many areas selected - consider separate rules for different zones'
    }
    
    // Business impact predictions
    const timeHours = selectedTimeframe === 'custom' ? customHours : (timeOption?.hours || 8)
    const avgIssuesPerWeek = Math.max(1, Math.floor((10 - sensitivity) * (timeHours / 4) * selectedAreas.length * 0.8))
    const estimatedSavings = avgIssuesPerWeek * (problem.id === 'temperature-violations' ? 1500 : 
                                                 problem.id === 'traffic-jams' ? 300 : 200)
    
    recommendations.businessImpact = `Estimated ${avgIssuesPerWeek} issues/week, ~$${estimatedSavings} monthly savings`
    
    return recommendations
  }

  const steps = [
    { id: 'problem', label: 'What Problem?', completed: !!selectedProblem },
    { id: 'scenario', label: 'Your Scenario', completed: !!ruleName },
    { id: 'smart-enhance', label: 'Smart Suggestions', completed: true },
    { id: 'advanced', label: 'Advanced (Optional)', completed: !advancedMode },
    { id: 'preview', label: 'Preview & Save', completed: false }
  ]

  const handleNext = () => {
    const currentIndex = steps.findIndex(s => s.id === currentStep)
    if (currentIndex < steps.length - 1) {
      const nextStep = steps[currentIndex + 1].id
      // Skip advanced step if not in advanced mode
      if (nextStep === 'advanced' && !advancedMode) {
        setCurrentStep('preview')
      } else {
        setCurrentStep(nextStep as any)
      }
    }
  }

  // Auto-populate suggestions for first-time users
  useEffect(() => {
    if (selectedProblem && problem?.relatedConditions) {
      const suggestedConditions = problem.relatedConditions
        .filter(c => c.suggested)
        .map(c => c.field)
      setSelectedSuggestions(suggestedConditions)
    }
  }, [selectedProblem])

  const handleBack = () => {
    const currentIndex = steps.findIndex(s => s.id === currentStep)
    if (currentIndex > 0) {
      const prevStep = steps[currentIndex - 1].id
      // Skip advanced step if not in advanced mode
      if (prevStep === 'advanced' && !advancedMode) {
        setCurrentStep('smart-enhance')
      } else {
        setCurrentStep(prevStep as any)
      }
    }
  }

  const canProceed = () => {
    switch (currentStep) {
      case 'problem': return !!selectedProblem
      case 'scenario': return !!ruleName.trim()
      case 'smart-enhance': return true
      case 'advanced': return true
      case 'preview': return true
      default: return false
    }
  }

  const renderStepHeader = () => (
    <div className="mb-8">
      {/* Progress Steps */}
      <div className="flex items-center justify-center mb-6 flex-wrap">
        {steps.map((step, index) => (
          <React.Fragment key={step.id}>
            <div className={`flex items-center ${
              step.id === currentStep ? 'text-primary' : 
              step.completed ? 'text-green-600' : 'text-muted-foreground'
            }`}>
              <div className={`w-8 h-8 rounded-full flex items-center justify-center text-sm font-medium ${
                step.id === currentStep ? 'bg-primary text-primary-foreground' :
                step.completed ? 'bg-green-500 text-white' : 'bg-muted'
              }`}>
                {step.completed && step.id !== currentStep ? (
                  <CheckCircle className="w-4 h-4" />
                ) : (
                  index + 1
                )}
              </div>
              <span className="ml-2 font-medium text-sm">{step.label}</span>
            </div>
            {index < steps.length - 1 && (
              <div className={`mx-2 md:mx-4 w-6 md:w-12 h-0.5 ${
                steps[index + 1].completed || steps[index + 1].id === currentStep ? 'bg-primary' : 'bg-muted'
              }`} />
            )}
          </React.Fragment>
        ))}
      </div>
    </div>
  )

  const renderProblemSelection = () => (
    <div className="space-y-6">
      <div className="text-center space-y-2">
        <h2 className="text-2xl font-bold">What warehouse problem bugs you most?</h2>
        <p className="text-muted-foreground text-lg">
          Choose the situation that happens in your warehouse and causes headaches
        </p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-4 max-w-5xl mx-auto">
        {WAREHOUSE_PROBLEMS.map((problem) => (
          <Card 
            key={problem.id}
            className={`cursor-pointer transition-all hover:shadow-lg ${
              selectedProblem === problem.id 
                ? 'ring-2 ring-primary shadow-lg' 
                : 'hover:shadow-md'
            }`}
            onClick={() => setSelectedProblem(problem.id)}
          >
            <CardHeader className="pb-3">
              <div className="flex items-start gap-4">
                <div className={`p-3 rounded-lg ${problem.color}`}>
                  <problem.icon className="w-6 h-6" />
                </div>
                <div className="flex-1">
                  <CardTitle className="text-lg mb-2">{problem.title}</CardTitle>
                  <p className="text-sm text-muted-foreground mb-3">{problem.description}</p>
                  
                  {/* Visual illustration */}
                  <div className="text-2xl mb-3 font-mono">{problem.illustration}</div>
                  
                  {/* Real world example */}
                  <Alert className="mb-3">
                    <Lightbulb className="h-4 w-4" />
                    <AlertDescription className="text-xs">
                      <strong>Real example:</strong> {problem.realWorldExample}
                    </AlertDescription>
                  </Alert>
                  
                  {/* Business impact */}
                  <div className="space-y-2 text-xs">
                    <div className="flex items-center gap-2">
                      <TrendingUp className="w-3 h-3 text-red-500" />
                      <span><strong>Impact:</strong> {problem.businessImpact}</span>
                    </div>
                    <div className="flex items-center gap-2">
                      <Target className="w-3 h-3 text-blue-500" />
                      <span><strong>Frequency:</strong> {problem.frequency}</span>
                    </div>
                  </div>
                </div>
              </div>
            </CardHeader>
          </Card>
        ))}
      </div>
    </div>
  )

  const renderScenarioConfiguration = () => (
    <div className="space-y-6 max-w-3xl mx-auto">
      <div className="text-center space-y-2">
        <h2 className="text-2xl font-bold">Tell us about your specific situation</h2>
        <p className="text-muted-foreground">
          Let's make this rule perfect for your warehouse operation
        </p>
      </div>

      {problem && (
        <Card className="mb-6">
          <CardHeader>
            <div className="flex items-center gap-3">
              <div className={`p-2 rounded-lg ${problem.color}`}>
                <problem.icon className="w-5 h-5" />
              </div>
              <div>
                <CardTitle className="text-lg">Solving: {problem.title}</CardTitle>
                <p className="text-sm text-muted-foreground">{problem.realWorldExample}</p>
              </div>
            </div>
          </CardHeader>
        </Card>
      )}

      <div className="space-y-6">
        {/* Rule Name */}
        <Card>
          <CardHeader>
            <CardTitle className="text-base">What should we call this rule?</CardTitle>
            <p className="text-sm text-muted-foreground">Give it a name that your team will understand</p>
          </CardHeader>
          <CardContent>
            <Input
              value={ruleName}
              onChange={(e) => setRuleName(e.target.value)}
              placeholder={`e.g., "Catch ${problem?.title.toLowerCase() || 'problems'} in receiving"`}
              className="text-lg p-4"
            />
            <div className="mt-2 text-xs text-muted-foreground">
              💡 <strong>Tip:</strong> Use names like "Morning dock cleanup check" or "Frozen goods safety watch"
            </div>
          </CardContent>
        </Card>

        {/* Smart Time Configuration */}
        <Card>
          <CardHeader>
            <div className="flex items-center justify-between">
              <div>
                <CardTitle className="text-base">How long is "too long" for items to sit?</CardTitle>
                <p className="text-sm text-muted-foreground">When should we alert you about this problem?</p>
              </div>
              <Badge variant="outline" className="bg-blue-50 text-blue-700 border-blue-200">
                <Brain className="w-3 h-3 mr-1" />
                Smart Suggestions
              </Badge>
            </div>
          </CardHeader>
          <CardContent className="space-y-4">
            {/* Smart recommendations based on problem type */}
            {problem && (
              <Alert className="border-blue-200 bg-blue-50">
                <Wand2 className="h-4 w-4 text-blue-600" />
                <AlertDescription>
                  <strong>For {problem.title.toLowerCase()}:</strong> {problem.smartSuggestions[0]}
                </AlertDescription>
              </Alert>
            )}

            <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
              {TIME_OPTIONS.filter(opt => opt.id !== 'custom').map((option) => (
                <button
                  key={option.id}
                  onClick={() => setSelectedTimeframe(option.id)}
                  className={`p-4 text-left rounded-lg border-2 transition-all ${
                    selectedTimeframe === option.id
                      ? 'border-primary bg-primary/5'
                      : 'border-muted hover:border-primary/50'
                  }`}
                >
                  <div className="flex items-center justify-between">
                    <div className="font-medium">{option.label}</div>
                    {option.smartNote && (
                      <Badge variant="outline" className="text-xs">{option.smartNote}</Badge>
                    )}
                  </div>
                  <div className="text-sm text-muted-foreground mt-1">{option.description}</div>
                  <div className="text-xs text-primary mt-2">≈ {option.hours} hours</div>
                </button>
              ))}
            </div>

            {/* Custom timing with smart suggestions */}
            <div className="border-t pt-4">
              <button
                onClick={() => setSelectedTimeframe('custom')}
                className={`w-full p-4 text-left rounded-lg border-2 transition-all ${
                  selectedTimeframe === 'custom'
                    ? 'border-primary bg-primary/5'
                    : 'border-muted hover:border-primary/50'
                }`}
              >
                <div className="font-medium">Custom timing</div>
                <div className="text-sm text-muted-foreground mt-1">Set your own specific timeframe</div>
              </button>
              
              {selectedTimeframe === 'custom' && (
                <div className="mt-4 p-4 bg-muted/50 rounded-lg">
                  <Label className="text-sm font-medium">Hours</Label>
                  <div className="flex items-center gap-4 mt-2">
                    <Slider
                      value={[customHours]}
                      onValueChange={(value) => setCustomHours(value[0])}
                      max={48}
                      min={1}
                      step={1}
                      className="flex-1"
                    />
                    <div className="text-lg font-medium w-16 text-center">
                      {customHours}h
                    </div>
                  </div>
                  <div className="text-xs text-muted-foreground mt-1">
                    Alert when items sit for more than {customHours} hours
                  </div>
                  
                  {/* Smart suggestions for custom values */}
                  <div className="mt-3 p-3 bg-blue-50 rounded-lg">
                    <div className="text-xs font-medium text-blue-800 mb-1">💡 Smart Suggestion:</div>
                    <div className="text-xs text-blue-700">
                      {customHours <= 2 ? 'Very strict - good for high-priority items' :
                       customHours <= 4 ? 'Strict - catches problems early' :
                       customHours <= 8 ? 'Balanced - most common choice' :
                       customHours <= 12 ? 'Relaxed - fewer false alarms' :
                       'Very relaxed - only obvious problems'}
                    </div>
                  </div>
                </div>
              )}
            </div>
          </CardContent>
        </Card>

        {/* Smart Area Selection */}
        {(selectedProblem === 'forgotten-items' || selectedProblem === 'traffic-jams') && (
          <Card>
            <CardHeader>
              <CardTitle className="text-base">Which areas should we monitor?</CardTitle>
              <p className="text-sm text-muted-foreground">Select the warehouse areas where this problem happens</p>
            </CardHeader>
            <CardContent>
              <div className="grid grid-cols-2 md:grid-cols-3 gap-3">
                {[
                  { id: 'receiving', label: 'Receiving Docks', icon: '🚚', priority: 'high' },
                  { id: 'staging', label: 'Staging Areas', icon: '📦', priority: 'medium' },
                  { id: 'aisles', label: 'Aisles', icon: '🛣️', priority: selectedProblem === 'traffic-jams' ? 'high' : 'low' },
                  { id: 'picking', label: 'Pick Zones', icon: '🛒', priority: 'medium' },
                  { id: 'shipping', label: 'Shipping Docks', icon: '📤', priority: 'low' },
                  { id: 'returns', label: 'Returns Area', icon: '↩️', priority: 'low' }
                ].map((area) => (
                  <button
                    key={area.id}
                    onClick={() => {
                      setSelectedAreas(prev => 
                        prev.includes(area.id) 
                          ? prev.filter(a => a !== area.id)
                          : [...prev, area.id]
                      )
                    }}
                    className={`p-3 text-center rounded-lg border-2 transition-all relative ${
                      selectedAreas.includes(area.id)
                        ? 'border-primary bg-primary/5'
                        : 'border-muted hover:border-primary/50'
                    }`}
                  >
                    {area.priority === 'high' && (
                      <Badge variant="outline" className="absolute -top-2 -right-2 bg-yellow-100 text-yellow-800 border-yellow-300 text-xs">
                        Recommended
                      </Badge>
                    )}
                    <div className="text-2xl mb-1">{area.icon}</div>
                    <div className="text-sm font-medium">{area.label}</div>
                  </button>
                ))}
              </div>
            </CardContent>
          </Card>
        )}
      </div>
    </div>
  )

  const renderSmartEnhancement = () => {
    const recommendations = getIntelligentRecommendations()
    const smartSuggestions = getSmartSuggestions()
    
    return (
      <div className="space-y-6 max-w-4xl mx-auto">
        <div className="text-center space-y-2">
          <h2 className="text-2xl font-bold">Smart suggestions to make your rule even better</h2>
          <p className="text-muted-foreground">
            Based on your choices, here are some intelligent recommendations
          </p>
        </div>

        {/* AI Recommendations Panel */}
        <Card className="border-2 border-blue-200 bg-gradient-to-r from-blue-50 to-purple-50">
          <CardHeader>
            <div className="flex items-center gap-3">
              <div className="p-2 rounded-lg bg-gradient-to-r from-blue-100 to-purple-100">
                <Brain className="w-5 h-5 text-blue-600" />
              </div>
              <div>
                <CardTitle className="text-base">AI Analysis & Recommendations</CardTitle>
                <p className="text-sm text-muted-foreground">
                  Personalized suggestions based on your warehouse scenario
                </p>
              </div>
              <Badge variant="outline" className="bg-blue-100 text-blue-800 border-blue-300">
                <Sparkles className="w-3 h-3 mr-1" />
                AI Powered
              </Badge>
            </div>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              {recommendations.timeframe && (
                <Alert className="border-green-200 bg-green-50">
                  <Timer className="h-4 w-4 text-green-600" />
                  <AlertDescription className="text-sm">
                    <strong>Timing:</strong> {recommendations.timeframe}
                  </AlertDescription>
                </Alert>
              )}
              {recommendations.sensitivity && (
                <Alert className="border-purple-200 bg-purple-50">
                  <Target className="h-4 w-4 text-purple-600" />
                  <AlertDescription className="text-sm">
                    <strong>Sensitivity:</strong> {recommendations.sensitivity}
                  </AlertDescription>
                </Alert>
              )}
              {recommendations.areas && (
                <Alert className="border-orange-200 bg-orange-50">
                  <MapPin className="h-4 w-4 text-orange-600" />
                  <AlertDescription className="text-sm">
                    <strong>Areas:</strong> {recommendations.areas}
                  </AlertDescription>
                </Alert>
              )}
              {recommendations.businessImpact && (
                <Alert className="border-indigo-200 bg-indigo-50">
                  <TrendingUp className="h-4 w-4 text-indigo-600" />
                  <AlertDescription className="text-sm">
                    <strong>Impact:</strong> {recommendations.businessImpact}
                  </AlertDescription>
                </Alert>
              )}
            </div>
            
            {/* Contextual Smart Suggestions */}
            {smartSuggestions.length > 0 && (
              <div className="mt-4 p-4 bg-white/80 rounded-lg border border-blue-200">
                <h4 className="font-medium mb-2 text-sm">💡 Additional Smart Insights:</h4>
                <ul className="space-y-1">
                  {smartSuggestions.slice(0, 3).map((suggestion, index) => (
                    <li key={index} className="text-xs text-muted-foreground flex items-start gap-2">
                      <span className="text-blue-500 mt-0.5">•</span>
                      {suggestion}
                    </li>
                  ))}
                </ul>
              </div>
            )}
          </CardContent>
        </Card>

        {/* Smart Sensitivity Adjustment */}
        <Card>
        <CardHeader>
          <div className="flex items-center justify-between">
            <div>
              <CardTitle className="text-base">How strict should this rule be?</CardTitle>
              <p className="text-sm text-muted-foreground">
                More strict = catch problems earlier but more alerts
              </p>
            </div>
            <Badge variant="outline" className="bg-green-50 text-green-700 border-green-200">
              <Activity className="w-3 h-3 mr-1" />
              AI Optimized
            </Badge>
          </div>
        </CardHeader>
        <CardContent className="space-y-6">
          {/* Smart recommendation based on problem */}
          {problem && (
            <Alert className="border-green-200 bg-green-50">
              <Sparkles className="h-4 w-4 text-green-600" />
              <AlertDescription>
                <strong>Smart Recommendation:</strong> For {problem.title.toLowerCase()}, most successful warehouses start with <strong>Balanced</strong> sensitivity and adjust based on results.
              </AlertDescription>
            </Alert>
          )}

          {/* Sensitivity Slider with Smart Context */}
          <div>
            <div className="flex items-center justify-between mb-4">
              <span className="text-sm text-muted-foreground">Fewer Alerts</span>
              <span className="text-sm text-muted-foreground">More Alerts</span>
            </div>
            <Slider
              value={[sensitivity]}
              onValueChange={(value) => setSensitivity(value[0])}
              max={5}
              min={1}
              step={1}
              className="mb-4"
            />
            
            {/* Current Selection with Predictions */}
            {sensitivityInfo && (
              <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mt-4">
                <Card className="p-4">
                  <div className="text-center">
                    <BarChart3 className="w-8 h-8 mx-auto mb-2 text-blue-500" />
                    <div className="font-medium text-lg">{sensitivityInfo.label}</div>
                    <div className="text-sm text-muted-foreground">{sensitivityInfo.description}</div>
                  </div>
                </Card>
                <Card className="p-4">
                  <div className="text-center">
                    <Target className="w-8 h-8 mx-auto mb-2 text-green-500" />
                    <div className="font-medium text-lg">{sensitivityInfo.alertsPerWeek}</div>
                    <div className="text-sm text-muted-foreground">Expected alerts per week</div>
                  </div>
                </Card>
                <Card className="p-4">
                  <div className="text-center">
                    <CheckCircle className="w-8 h-8 mx-auto mb-2 text-orange-500" />
                    <div className="font-medium text-lg">{sensitivityInfo.coverage}</div>
                    <div className="text-sm text-muted-foreground">Issues caught</div>
                  </div>
                </Card>
              </div>
            )}
          </div>
        </CardContent>
      </Card>

      {/* Smart Additional Conditions */}
      {problem && problem.relatedConditions && (
        <Card>
          <CardHeader>
            <CardTitle className="text-base">Want to make this rule even smarter?</CardTitle>
            <p className="text-sm text-muted-foreground">
              Add these optional conditions for better accuracy
            </p>
          </CardHeader>
          <CardContent className="space-y-3">
            {problem.relatedConditions.map((condition, index) => (
              <div key={index} className="flex items-start gap-3 p-3 border rounded-lg">
                <input
                  type="checkbox"
                  id={condition.field}
                  checked={selectedSuggestions.includes(condition.field)}
                  onChange={(e) => {
                    if (e.target.checked) {
                      setSelectedSuggestions(prev => [...prev, condition.field])
                    } else {
                      setSelectedSuggestions(prev => prev.filter(s => s !== condition.field))
                    }
                  }}
                  className="rounded border-gray-300 mt-1"
                />
                <div className="flex-1">
                  <label htmlFor={condition.field} className="font-medium cursor-pointer">
                    {condition.label}
                  </label>
                  {condition.suggested && (
                    <Badge variant="outline" className="ml-2 bg-yellow-100 text-yellow-800 border-yellow-300 text-xs">
                      Recommended
                    </Badge>
                  )}
                </div>
              </div>
            ))}
          </CardContent>
        </Card>
      )}

      {/* Advanced Mode Toggle */}
      <Card className="border-2 border-dashed border-purple-200">
        <CardContent className="p-6">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-3">
              <div className="p-2 rounded-lg bg-purple-100">
                <Layers className="w-5 h-5 text-purple-600" />
              </div>
              <div>
                <h3 className="font-medium">Want even more control?</h3>
                <p className="text-sm text-muted-foreground">
                  Try the advanced visual builder for complex conditions
                </p>
              </div>
            </div>
            <div className="flex items-center gap-3">
              <Badge variant="outline" className="bg-purple-50 text-purple-700 border-purple-200">
                Power User Mode
              </Badge>
              <Button
                variant={advancedMode ? "default" : "outline"}
                onClick={() => setAdvancedMode(!advancedMode)}
                className="flex items-center gap-2"
              >
                <Settings className="w-4 h-4" />
                {advancedMode ? 'Exit Advanced' : 'Try Advanced'}
              </Button>
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
    )
  }

  const renderAdvancedBuilder = () => (
    <div className="space-y-6 max-w-5xl mx-auto">
      <div className="text-center space-y-2">
        <h2 className="text-2xl font-bold">Advanced Visual Rule Builder</h2>
        <p className="text-muted-foreground">
          Build complex conditions with drag-and-drop simplicity
        </p>
        <Badge variant="outline" className="bg-purple-50 text-purple-700 border-purple-200">
          <Layers className="w-3 h-3 mr-1" />
          Power User Mode
        </Badge>
      </div>

      {/* Visual Condition Builder */}
      <Card>
        <CardHeader>
          <CardTitle className="text-base">Build Your Conditions Visually</CardTitle>
          <p className="text-sm text-muted-foreground">
            Drag and drop to create complex logic
          </p>
        </CardHeader>
        <CardContent className="space-y-4">
          {/* Base Condition (always present) */}
          <div className="bg-blue-50 border-2 border-blue-200 rounded-lg p-4">
            <div className="flex items-center gap-3 mb-3">
              <div className="w-8 h-8 rounded bg-blue-500 text-white flex items-center justify-center text-sm font-medium">
                1
              </div>
              <div className="font-medium">Main Condition</div>
              <Badge variant="outline" className="bg-blue-100 text-blue-800 border-blue-300">
                Required
              </Badge>
            </div>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-3">
              <div>
                <Label className="text-xs">Field</Label>
                <div className="p-2 bg-white border rounded text-sm">
                  {selectedTimeframe === 'custom' ? `Time > ${customHours}h` : `Time > ${timeOption?.hours}h`}
                </div>
              </div>
              <div>
                <Label className="text-xs">Location</Label>
                <div className="p-2 bg-white border rounded text-sm">
                  {selectedAreas.join(' OR ')}
                </div>
              </div>
              <div>
                <Label className="text-xs">Priority</Label>
                <div className="p-2 bg-white border rounded text-sm">
                  {sensitivityInfo?.label}
                </div>
              </div>
            </div>
          </div>

          {/* Additional Conditions */}
          {selectedSuggestions.length > 0 && (
            <div className="space-y-3">
              <div className="flex items-center justify-between">
                <h4 className="font-medium">Additional Conditions</h4>
                <Badge variant="outline" className="bg-green-100 text-green-800 border-green-300">
                  {selectedSuggestions.length} active
                </Badge>
              </div>
              {selectedSuggestions.map((suggestionField, index) => {
                const condition = problem?.relatedConditions.find(c => c.field === suggestionField)
                return (
                  <div key={suggestionField} className="bg-green-50 border-2 border-green-200 rounded-lg p-4">
                    <div className="flex items-center gap-3 mb-3">
                      <div className="w-8 h-8 rounded bg-green-500 text-white flex items-center justify-center text-sm font-medium">
                        {index + 2}
                      </div>
                      <div className="font-medium">{condition?.label}</div>
                      <div className="text-sm text-muted-foreground">AND</div>
                      <Button
                        variant="ghost"
                        size="sm"
                        onClick={() => setSelectedSuggestions(prev => prev.filter(s => s !== suggestionField))}
                        className="ml-auto"
                      >
                        <X className="w-4 h-4" />
                      </Button>
                    </div>
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
                      <div>
                        <Label className="text-xs">Condition</Label>
                        <div className="p-2 bg-white border rounded text-sm">
                          {condition?.field.replace(/_/g, ' ')}
                        </div>
                      </div>
                      <div>
                        <Label className="text-xs">Value</Label>
                        <div className="p-2 bg-white border rounded text-sm">
                          Auto-detected
                        </div>
                      </div>
                    </div>
                  </div>
                )
              })}
            </div>
          )}

          {/* Add More Conditions */}
          <div className="border-2 border-dashed border-gray-200 rounded-lg p-4 text-center">
            <Button variant="outline" className="flex items-center gap-2">
              <Plus className="w-4 h-4" />
              Add Another Condition
            </Button>
            <p className="text-xs text-muted-foreground mt-2">
              Connect with AND/OR logic
            </p>
          </div>

          {/* Logic Preview */}
          <Alert>
            <AlertCircle className="h-4 w-4" />
            <AlertDescription>
              <strong>Logic Preview:</strong> Alert when items meet the main condition
              {selectedSuggestions.length > 0 && (
                <span> AND {selectedSuggestions.length} additional condition{selectedSuggestions.length > 1 ? 's' : ''}</span>
              )}
            </AlertDescription>
          </Alert>
        </CardContent>
      </Card>
    </div>
  )

  const renderPreview = () => {
    const recommendations = getIntelligentRecommendations()
    const timeHours = selectedTimeframe === 'custom' ? customHours : (timeOption?.hours || 8)
    
    // Enhanced data simulation based on actual parameters
    const simulateRealData = () => {
      const baseIssuesPerWeek = problem?.id === 'temperature-violations' ? 12 : 
                               problem?.id === 'traffic-jams' ? 8 : 
                               problem?.id === 'forgotten-items' ? 15 : 10
      
      const sensitivityMultiplier = sensitivity <= 2 ? 0.4 : sensitivity >= 4 ? 1.6 : 1.0
      const areaMultiplier = selectedAreas.length * 0.7
      const timeMultiplier = timeHours <= 4 ? 1.4 : timeHours >= 12 ? 0.6 : 1.0
      
      const issuesPerWeek = Math.max(1, Math.floor(baseIssuesPerWeek * sensitivityMultiplier * areaMultiplier * timeMultiplier))
      const savingsPerIssue = problem?.id === 'temperature-violations' ? 1200 : 
                             problem?.id === 'traffic-jams' ? 250 : 180
      const monthlySavings = issuesPerWeek * 4.3 * savingsPerIssue
      const timesSavedHours = issuesPerWeek * (problem?.id === 'traffic-jams' ? 2.5 : 1.5)
      const coveragePercent = Math.min(95, Math.max(40, 40 + (sensitivity * 10) + (selectedSuggestions.length * 5)))
      
      return {
        issuesPerWeek,
        monthlySavings: Math.floor(monthlySavings),
        timesSavedHours: Math.floor(timesSavedHours),
        coveragePercent
      }
    }
    
    const liveData = simulateRealData()
    
    return (
      <div className="space-y-6 max-w-4xl mx-auto">
        <div className="text-center space-y-2">
          <h2 className="text-2xl font-bold">Your smart rule is ready!</h2>
          <p className="text-muted-foreground">
            Here's what your enhanced rule will do with live predictions
          </p>
        </div>

      <Card className="border-2 border-primary/20">
        <CardHeader>
          <div className="flex items-center gap-3">
            <div className="p-2 rounded-lg bg-primary/10">
              <CheckCircle className="w-5 h-5 text-primary" />
            </div>
            <div>
              <CardTitle className="text-xl">{ruleName || 'Your Smart Rule'}</CardTitle>
              <p className="text-muted-foreground">Enhanced with AI recommendations</p>
            </div>
            {advancedMode && (
              <Badge variant="outline" className="bg-purple-50 text-purple-700 border-purple-200">
                <Layers className="w-3 h-3 mr-1" />
                Advanced Mode
              </Badge>
            )}
          </div>
        </CardHeader>
        <CardContent className="space-y-6">
          {/* Rule Summary */}
          <Alert>
            <Brain className="h-4 w-4" />
            <AlertDescription>
              <strong>Smart Rule Summary:</strong>
              <br />
              This rule will alert you when {problem?.title.toLowerCase()} occur in{' '}
              {selectedAreas.length > 0 ? selectedAreas.join(' or ') : 'monitored areas'} for longer than{' '}
              {selectedTimeframe === 'custom' ? `${customHours} hours` : timeOption?.label.toLowerCase()}.
              <br />
              <br />
              <strong>Intelligence Level:</strong> {sensitivityInfo?.label} sensitivity with {selectedSuggestions.length} smart enhancements active.
            </AlertDescription>
          </Alert>

          {/* Live Performance Predictions */}
          <div className="space-y-4">
            <div className="flex items-center justify-between">
              <h4 className="font-medium">📊 Live Performance Predictions</h4>
              <Badge variant="outline" className="bg-green-100 text-green-800 border-green-300">
                <Activity className="w-3 h-3 mr-1" />
                Based on your settings
              </Badge>
            </div>
            
            <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
              <Card className="p-4 bg-blue-50 border-blue-200">
                <div className="text-center">
                  <div className="text-2xl font-bold text-blue-600">
                    {liveData.issuesPerWeek}
                  </div>
                  <div className="text-xs text-muted-foreground">Issues caught/week</div>
                  <div className="text-xs text-blue-600 mt-1">
                    {sensitivityInfo?.label} sensitivity
                  </div>
                </div>
              </Card>
              <Card className="p-4 bg-green-50 border-green-200">
                <div className="text-center">
                  <div className="text-2xl font-bold text-green-600">
                    ${liveData.monthlySavings.toLocaleString()}
                  </div>
                  <div className="text-xs text-muted-foreground">Monthly savings</div>
                  <div className="text-xs text-green-600 mt-1">
                    {selectedAreas.length} area{selectedAreas.length > 1 ? 's' : ''}
                  </div>
                </div>
              </Card>
              <Card className="p-4 bg-orange-50 border-orange-200">
                <div className="text-center">
                  <div className="text-2xl font-bold text-orange-600">
                    {liveData.timesSavedHours}h
                  </div>
                  <div className="text-xs text-muted-foreground">Time saved/week</div>
                  <div className="text-xs text-orange-600 mt-1">
                    {timeHours}h threshold
                  </div>
                </div>
              </Card>
              <Card className="p-4 bg-purple-50 border-purple-200">
                <div className="text-center">
                  <div className="text-2xl font-bold text-purple-600">
                    {liveData.coveragePercent}%
                  </div>
                  <div className="text-xs text-muted-foreground">Issue coverage</div>
                  <div className="text-xs text-purple-600 mt-1">
                    {selectedSuggestions.length} enhancements
                  </div>
                </div>
              </Card>
            </div>
            
            {/* Real-time insights */}
            <Alert className="border-blue-200 bg-gradient-to-r from-blue-50 to-indigo-50">
              <Lightbulb className="h-4 w-4 text-blue-600" />
              <AlertDescription>
                <strong>Real-time Analysis:</strong> Based on your {problem?.title.toLowerCase()} rule with {sensitivityInfo?.label.toLowerCase()} sensitivity 
                in {selectedAreas.length} area{selectedAreas.length > 1 ? 's' : ''}, you'll catch approximately <strong>{liveData.issuesPerWeek} issues per week</strong>.
                {liveData.monthlySavings > 1000 && (
                  <span> This could save your warehouse over <strong>${liveData.monthlySavings.toLocaleString()}</strong> monthly!</span>
                )}
              </AlertDescription>
            </Alert>
          </div>

          {/* Smart Features Summary */}
          <div>
            <h4 className="font-medium mb-3">Smart Features Enabled:</h4>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
              <div className="flex items-center gap-2 p-3 bg-blue-50 rounded-lg">
                <Brain className="w-4 h-4 text-blue-600" />
                <span className="text-sm">AI-optimized sensitivity</span>
              </div>
              <div className="flex items-center gap-2 p-3 bg-green-50 rounded-lg">
                <Target className="w-4 h-4 text-green-600" />
                <span className="text-sm">Context-aware timing</span>
              </div>
              {selectedSuggestions.length > 0 && (
                <div className="flex items-center gap-2 p-3 bg-purple-50 rounded-lg">
                  <Sparkles className="w-4 h-4 text-purple-600" />
                  <span className="text-sm">{selectedSuggestions.length} smart conditions</span>
                </div>
              )}
              {advancedMode && (
                <div className="flex items-center gap-2 p-3 bg-orange-50 rounded-lg">
                  <Layers className="w-4 h-4 text-orange-600" />
                  <span className="text-sm">Advanced visual logic</span>
                </div>
              )}
            </div>
          </div>
        </CardContent>
      </Card>

      <div className="flex justify-center">
        <Button 
          onClick={() => onRuleCreate?.({
            name: ruleName,
            problem: selectedProblem,
            timeframe: selectedTimeframe,
            customHours,
            sensitivity,
            areas: selectedAreas,
            smartSuggestions: selectedSuggestions,
            advancedMode,
            additionalConditions
          })}
          size="lg"
          className="px-8 bg-gradient-to-r from-blue-600 to-purple-600 hover:from-blue-700 hover:to-purple-700"
        >
          <Sparkles className="w-4 h-4 mr-2" />
          Create Smart Rule
        </Button>
        </div>
      </div>
    )
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 via-white to-purple-50 p-6">
      <div className="max-w-7xl mx-auto">
        {renderStepHeader()}
        
        <div className="mb-8">
          {currentStep === 'problem' && renderProblemSelection()}
          {currentStep === 'scenario' && renderScenarioConfiguration()}
          {currentStep === 'smart-enhance' && renderSmartEnhancement()}
          {currentStep === 'advanced' && renderAdvancedBuilder()}
          {currentStep === 'preview' && renderPreview()}
        </div>

        {/* Navigation */}
        <div className="flex justify-between items-center max-w-4xl mx-auto">
          <Button 
            variant="outline" 
            onClick={currentStep === 'problem' ? onCancel : handleBack}
            className="flex items-center gap-2"
          >
            <ArrowLeft className="w-4 h-4" />
            {currentStep === 'problem' ? 'Cancel' : 'Back'}
          </Button>

          {currentStep !== 'preview' && (
            <Button 
              onClick={handleNext}
              disabled={!canProceed()}
              className="flex items-center gap-2"
            >
              Continue
              <ArrowRight className="w-4 h-4" />
            </Button>
          )}
        </div>

        {/* Help text */}
        <div className="text-center mt-8">
          <p className="text-xs text-muted-foreground">
            ✨ This enhanced builder uses AI to optimize your rules and provide intelligent suggestions.
          </p>
        </div>
      </div>
    </div>
  )
}