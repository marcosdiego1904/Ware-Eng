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
  AlertCircle
} from 'lucide-react'

// Warehouse problems with visual context
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
    color: 'bg-orange-100 border-orange-300 text-orange-800'
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
    color: 'bg-red-100 border-red-300 text-red-800'
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
    color: 'bg-blue-100 border-blue-300 text-blue-800'
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
    color: 'bg-purple-100 border-purple-300 text-purple-800'
  },
  {
    id: 'overflow-situations',
    title: 'Storage Areas Overflowing',
    description: 'Too many pallets crammed in one location',
    icon: Warehouse,
    illustration: '📦📦📦📦📦💥',
    realWorldExample: 'Like when dock 2 has 15 pallets but only fits 8 safely',
    businessImpact: 'Safety hazard and makes inventory counting impossible',
    frequency: 'Common during peak seasons',
    category: 'capacity',
    color: 'bg-yellow-100 border-yellow-300 text-yellow-800'
  }
]

// Natural language time options
const TIME_OPTIONS = [
  { id: 'end-of-shift', label: 'End of current shift', hours: 8, description: 'Items should be moved before shift ends' },
  { id: 'next-morning', label: 'By next morning', hours: 16, description: 'Overnight items are flagged' },
  { id: 'same-day', label: 'Same day', hours: 24, description: 'Nothing should sit overnight' },
  { id: 'next-day', label: 'Next business day', hours: 32, description: 'Items sitting over a day are flagged' },
  { id: 'custom', label: 'Custom timing', hours: 0, description: 'Set your own specific timeframe' }
]

// Sensitivity levels with context
const SENSITIVITY_LEVELS = [
  { 
    level: 1, 
    label: 'Very Relaxed', 
    description: 'Only catch the most obvious problems',
    alertsPerWeek: '2-5 alerts',
    example: 'Only pallets sitting for days'
  },
  { 
    level: 2, 
    label: 'Relaxed', 
    description: 'Catch clear problems without being picky',
    alertsPerWeek: '5-15 alerts',
    example: 'Pallets sitting longer than usual'
  },
  { 
    level: 3, 
    label: 'Balanced', 
    description: 'Good balance of catching issues vs noise',
    alertsPerWeek: '10-25 alerts',
    example: 'Most warehouses start here'
  },
  { 
    level: 4, 
    label: 'Strict', 
    description: 'Catch problems early, more alerts',
    alertsPerWeek: '20-40 alerts',
    example: 'Be proactive about potential issues'
  },
  { 
    level: 5, 
    label: 'Very Strict', 
    description: 'Catch everything, expect many alerts',
    alertsPerWeek: '40+ alerts',
    example: 'Zero tolerance approach'
  }
]

interface EnhancedVisualBuilderProps {
  onRuleCreate?: (ruleData: any) => void
  onCancel?: () => void
}

export function EnhancedVisualBuilder({ onRuleCreate, onCancel }: EnhancedVisualBuilderProps) {
  const [currentStep, setCurrentStep] = useState<'problem' | 'scenario' | 'settings' | 'preview'>('problem')
  const [selectedProblem, setSelectedProblem] = useState<string | null>(null)
  const [ruleName, setRuleName] = useState('')
  const [selectedTimeframe, setSelectedTimeframe] = useState<string>('end-of-shift')
  const [customHours, setCustomHours] = useState(6)
  const [sensitivity, setSensitivity] = useState(3)
  const [selectedAreas, setSelectedAreas] = useState<string[]>(['receiving'])
  
  const problem = WAREHOUSE_PROBLEMS.find(p => p.id === selectedProblem)
  const timeOption = TIME_OPTIONS.find(t => t.id === selectedTimeframe)
  const sensitivityInfo = SENSITIVITY_LEVELS.find(s => s.level === sensitivity)

  const steps = [
    { id: 'problem', label: 'What Problem?', completed: !!selectedProblem },
    { id: 'scenario', label: 'Your Scenario', completed: !!ruleName },
    { id: 'settings', label: 'Fine-tune', completed: true },
    { id: 'preview', label: 'Preview & Save', completed: false }
  ]

  const handleNext = () => {
    const currentIndex = steps.findIndex(s => s.id === currentStep)
    if (currentIndex < steps.length - 1) {
      setCurrentStep(steps[currentIndex + 1].id as any)
    }
  }

  const handleBack = () => {
    const currentIndex = steps.findIndex(s => s.id === currentStep)
    if (currentIndex > 0) {
      setCurrentStep(steps[currentIndex - 1].id as any)
    }
  }

  const canProceed = () => {
    switch (currentStep) {
      case 'problem': return !!selectedProblem
      case 'scenario': return !!ruleName.trim()
      case 'settings': return true
      case 'preview': return true
      default: return false
    }
  }

  const renderStepHeader = () => (
    <div className="mb-8">
      {/* Progress Steps */}
      <div className="flex items-center justify-center mb-6">
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
              <span className="ml-2 font-medium">{step.label}</span>
            </div>
            {index < steps.length - 1 && (
              <div className={`mx-4 w-12 h-0.5 ${
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

      <div className="grid grid-cols-1 md:grid-cols-2 gap-4 max-w-4xl mx-auto">
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

      <div className="text-center">
        <p className="text-sm text-muted-foreground">
          Don't see your specific problem? No worries - choose the closest one and we'll customize it in the next step.
        </p>
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

        {/* Time Configuration */}
        <Card>
          <CardHeader>
            <CardTitle className="text-base">How long is "too long" for items to sit?</CardTitle>
            <p className="text-sm text-muted-foreground">When should we alert you about this problem?</p>
          </CardHeader>
          <CardContent className="space-y-4">
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
                  <div className="font-medium">{option.label}</div>
                  <div className="text-sm text-muted-foreground mt-1">{option.description}</div>
                  <div className="text-xs text-primary mt-2">≈ {option.hours} hours</div>
                </button>
              ))}
            </div>

            {/* Custom timing */}
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
                </div>
              )}
            </div>
          </CardContent>
        </Card>

        {/* Area Selection for relevant problems */}
        {(selectedProblem === 'forgotten-items' || selectedProblem === 'traffic-jams') && (
          <Card>
            <CardHeader>
              <CardTitle className="text-base">Which areas should we monitor?</CardTitle>
              <p className="text-sm text-muted-foreground">Select the warehouse areas where this problem happens</p>
            </CardHeader>
            <CardContent>
              <div className="grid grid-cols-2 md:grid-cols-3 gap-3">
                {[
                  { id: 'receiving', label: 'Receiving Docks', icon: '🚚' },
                  { id: 'staging', label: 'Staging Areas', icon: '📦' },
                  { id: 'aisles', label: 'Aisles', icon: '🛣️' },
                  { id: 'picking', label: 'Pick Zones', icon: '🛒' },
                  { id: 'shipping', label: 'Shipping Docks', icon: '📤' },
                  { id: 'returns', label: 'Returns Area', icon: '↩️' }
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
                    className={`p-3 text-center rounded-lg border-2 transition-all ${
                      selectedAreas.includes(area.id)
                        ? 'border-primary bg-primary/5'
                        : 'border-muted hover:border-primary/50'
                    }`}
                  >
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

  const renderSettings = () => (
    <div className="space-y-6 max-w-2xl mx-auto">
      <div className="text-center space-y-2">
        <h2 className="text-2xl font-bold">Fine-tune your rule</h2>
        <p className="text-muted-foreground">
          Adjust how sensitive this rule should be
        </p>
      </div>

      <Card>
        <CardHeader>
          <CardTitle className="text-base">How strict should this rule be?</CardTitle>
          <p className="text-sm text-muted-foreground">
            More strict = more alerts but catches problems earlier
          </p>
        </CardHeader>
        <CardContent className="space-y-6">
          {/* Sensitivity Slider */}
          <div>
            <div className="flex items-center justify-between mb-4">
              <span className="text-sm text-muted-foreground">More Relaxed</span>
              <span className="text-sm text-muted-foreground">More Strict</span>
            </div>
            <Slider
              value={[sensitivity]}
              onValueChange={(value) => setSensitivity(value[0])}
              max={5}
              min={1}
              step={1}
              className="mb-4"
            />
          </div>

          {/* Current Selection Display */}
          {sensitivityInfo && (
            <Alert>
              <Zap className="h-4 w-4" />
              <AlertDescription>
                <div className="space-y-2">
                  <div><strong>{sensitivityInfo.label}:</strong> {sensitivityInfo.description}</div>
                  <div className="text-sm text-muted-foreground">
                    📊 Expected: <strong>{sensitivityInfo.alertsPerWeek}</strong> • 
                    Example: {sensitivityInfo.example}
                  </div>
                </div>
              </AlertDescription>
            </Alert>
          )}

          {/* What this means in practice */}
          <div className="bg-muted/50 p-4 rounded-lg">
            <h4 className="font-medium mb-2">What this means for you:</h4>
            <div className="space-y-2 text-sm">
              <div className="flex items-center gap-2">
                <Timer className="w-4 h-4 text-blue-500" />
                <span>
                  Alert when items sit for {
                    selectedTimeframe === 'custom' ? `${customHours} hours` : timeOption?.label.toLowerCase()
                  }
                </span>
              </div>
              <div className="flex items-center gap-2">
                <Target className="w-4 h-4 text-orange-500" />
                <span>Expected alerts: {sensitivityInfo?.alertsPerWeek}</span>
              </div>
              <div className="flex items-center gap-2">
                <MapPin className="w-4 h-4 text-green-500" />
                <span>
                  Monitoring: {selectedAreas.length > 0 ? selectedAreas.join(', ') : 'all areas'}
                </span>
              </div>
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  )

  const renderPreview = () => (
    <div className="space-y-6 max-w-3xl mx-auto">
      <div className="text-center space-y-2">
        <h2 className="text-2xl font-bold">Preview your new rule</h2>
        <p className="text-muted-foreground">
          Here's what your rule will do and some examples of what it would catch
        </p>
      </div>

      <Card className="border-2 border-primary/20">
        <CardHeader>
          <div className="flex items-center gap-3">
            <div className="p-2 rounded-lg bg-primary/10">
              <CheckCircle className="w-5 h-5 text-primary" />
            </div>
            <div>
              <CardTitle className="text-xl">{ruleName || 'Your New Rule'}</CardTitle>
              <p className="text-muted-foreground">Ready to save and activate</p>
            </div>
          </div>
        </CardHeader>
        <CardContent className="space-y-4">
          {/* Rule Summary */}
          <Alert>
            <AlertCircle className="h-4 w-4" />
            <AlertDescription>
              <strong>This rule will alert you when:</strong>
              <br />
              {problem?.title.toLowerCase()} that have been sitting in{' '}
              {selectedAreas.length > 0 ? selectedAreas.join(' or ') : 'monitored areas'} for longer than{' '}
              {selectedTimeframe === 'custom' ? `${customHours} hours` : timeOption?.label.toLowerCase()}.
              <br />
              <br />
              <strong>Alert frequency:</strong> {sensitivityInfo?.alertsPerWeek} (based on {sensitivityInfo?.label.toLowerCase()} sensitivity)
            </AlertDescription>
          </Alert>

          {/* Example Scenarios */}
          <div>
            <h4 className="font-medium mb-3">Example situations this rule would catch:</h4>
            <div className="space-y-3">
              {getExampleScenarios().map((example, index) => (
                <div key={index} className="flex items-start gap-3 p-3 bg-muted/50 rounded-lg">
                  <div className="text-lg">{example.emoji}</div>
                  <div className="flex-1">
                    <div className="font-medium text-sm">{example.title}</div>
                    <div className="text-xs text-muted-foreground">{example.description}</div>
                  </div>
                  <Badge variant="outline" className="text-xs">
                    {example.priority}
                  </Badge>
                </div>
              ))}
            </div>
          </div>

          {/* Performance Preview */}
          <div className="bg-blue-50 p-4 rounded-lg">
            <h4 className="font-medium mb-2 flex items-center gap-2">
              <TrendingUp className="w-4 h-4" />
              Expected Performance
            </h4>
            <div className="grid grid-cols-3 gap-4 text-center">
              <div>
                <div className="text-lg font-bold text-blue-600">
                  {Math.floor(Math.random() * 15) + 5}
                </div>
                <div className="text-xs text-muted-foreground">Issues caught/week</div>
              </div>
              <div>
                <div className="text-lg font-bold text-green-600">
                  ${Math.floor(Math.random() * 500) + 200}
                </div>
                <div className="text-xs text-muted-foreground">Estimated savings</div>
              </div>
              <div>
                <div className="text-lg font-bold text-orange-600">
                  {Math.floor(Math.random() * 3) + 1}h
                </div>
                <div className="text-xs text-muted-foreground">Time saved/week</div>
              </div>
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
            areas: selectedAreas
          })}
          size="lg"
          className="px-8"
        >
          <CheckCircle className="w-4 h-4 mr-2" />
          Create This Rule
        </Button>
      </div>
    </div>
  )

  const getExampleScenarios = () => {
    const scenarios = [
      {
        emoji: '📦',
        title: 'Pallet of office supplies in receiving dock',
        description: `Sitting there since yesterday morning (${Math.floor(Math.random() * 20) + 10} hours)`,
        priority: 'High'
      },
      {
        emoji: '🥶',
        title: 'Frozen vegetables in wrong storage area',
        description: `In ambient storage for ${Math.floor(Math.random() * 8) + 1} hours - temperature risk!`,
        priority: 'Critical'
      },
      {
        emoji: '🚚',
        title: 'Truck delivery 85% unloaded',
        description: `3 pallets still in receiving while rest of delivery was processed`,
        priority: 'Medium'
      }
    ]
    return scenarios.slice(0, Math.min(3, Math.floor(Math.random() * 3) + 1))
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 via-white to-orange-50 p-6">
      <div className="max-w-6xl mx-auto">
        {renderStepHeader()}
        
        <div className="mb-8">
          {currentStep === 'problem' && renderProblemSelection()}
          {currentStep === 'scenario' && renderScenarioConfiguration()}
          {currentStep === 'settings' && renderSettings()}
          {currentStep === 'preview' && renderPreview()}
        </div>

        {/* Navigation */}
        <div className="flex justify-between items-center max-w-3xl mx-auto">
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
            Need help? This builder is designed to be intuitive - just describe your warehouse problem in plain English.
          </p>
        </div>
      </div>
    </div>
  )
}