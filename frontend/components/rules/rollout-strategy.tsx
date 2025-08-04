"use client"

import { useState, useEffect } from 'react'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Badge } from '@/components/ui/badge'
import { Alert, AlertDescription } from '@/components/ui/alert'
import { Switch } from '@/components/ui/switch'
import { Label } from '@/components/ui/label'
import { 
  Brain, 
  Sparkles, 
  ArrowRight, 
  Wrench, 
  CheckCircle,
  AlertTriangle,
  Info,
  Users,
  Zap
} from 'lucide-react'
import { RuleCreator } from './rule-creator' // Original rule creator
import { EnhancedRuleCreator } from './enhanced-rule-creator' // New AI-powered creator

interface RolloutStrategyProps {
  onModeChange?: (mode: 'classic' | 'ai-enhanced') => void
}

export function RolloutStrategy({ onModeChange }: RolloutStrategyProps) {
  const [selectedMode, setSelectedMode] = useState<'classic' | 'ai-enhanced'>('ai-enhanced')
  const [showComparison, setShowComparison] = useState(false)
  const [userPreference, setUserPreference] = useState<'auto' | 'classic' | 'ai-enhanced'>('auto')

  // Auto-select based on user experience level (you can enhance this logic)
  useEffect(() => {
    const storedPreference = localStorage.getItem('ruleBuilderPreference')
    if (storedPreference) {
      setUserPreference(storedPreference as any)
      if (storedPreference !== 'auto') {
        setSelectedMode(storedPreference as any)
      }
    }
  }, [])

  const handleModeSelection = (mode: 'classic' | 'ai-enhanced') => {
    setSelectedMode(mode)
    localStorage.setItem('ruleBuilderPreference', mode)
    onModeChange?.(mode)
  }

  const handleToggleComparison = () => {
    setShowComparison(!showComparison)
  }

  if (!showComparison && selectedMode) {
    // Render the selected mode
    return selectedMode === 'ai-enhanced' ? <EnhancedRuleCreator /> : <RuleCreator />
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="text-center space-y-4">
        <div>
          <h2 className="text-3xl font-bold">Choose Your Rule Builder Experience</h2>
          <p className="text-muted-foreground text-lg">
            Select the approach that works best for you
          </p>
        </div>

        {/* Experience Level Toggle */}
        <div className="flex items-center justify-center gap-4 p-4 bg-muted/30 rounded-lg max-w-md mx-auto">
          <Label htmlFor="auto-mode" className="text-sm font-medium">
            Auto-select based on experience
          </Label>
          <Switch
            id="auto-mode"
            checked={userPreference === 'auto'}
            onCheckedChange={(checked: boolean) => {
              const newPreference = checked ? 'auto' : selectedMode
              setUserPreference(newPreference)
              localStorage.setItem('ruleBuilderPreference', newPreference)
            }}
          />
        </div>
      </div>

      {/* Mode Selection Cards */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 max-w-6xl mx-auto">
        {/* Classic Builder */}
        <Card 
          className={`cursor-pointer transition-all ${
            selectedMode === 'classic' 
              ? 'ring-2 ring-orange-500 shadow-lg' 
              : 'hover:shadow-md'
          }`}
          onClick={() => handleModeSelection('classic')}
        >
          <CardHeader className="pb-4">
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-3">
                <div className="p-2 rounded-lg bg-orange-100">
                  <Wrench className="w-6 h-6 text-orange-600" />
                </div>
                <div>
                  <CardTitle className="text-xl">Classic Advanced Builder</CardTitle>
                  <p className="text-sm text-muted-foreground">Technical control & precision</p>
                </div>
              </div>
              <Badge variant="outline" className="border-orange-300 text-orange-700 bg-orange-50">
                Technical
              </Badge>
            </div>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="space-y-3">
              <h4 className="font-medium text-sm">Perfect for:</h4>
              <ul className="space-y-2 text-sm text-muted-foreground">
                <li className="flex items-center gap-2">
                  <CheckCircle className="w-3 h-3 text-green-500" />
                  IT administrators and system experts
                </li>
                <li className="flex items-center gap-2">
                  <CheckCircle className="w-3 h-3 text-green-500" />
                  Users who prefer direct technical control
                </li>
                <li className="flex items-center gap-2">
                  <CheckCircle className="w-3 h-3 text-green-500" />
                  Complex rule configurations with specific parameters
                </li>
                <li className="flex items-center gap-2">
                  <CheckCircle className="w-3 h-3 text-green-500" />
                  Legacy system compatibility requirements
                </li>
              </ul>
            </div>

            <div className="space-y-2">
              <h4 className="font-medium text-sm">Features:</h4>
              <div className="flex flex-wrap gap-2">
                <Badge variant="outline" className="text-xs">Direct Parameter Control</Badge>
                <Badge variant="outline" className="text-xs">Technical Interface</Badge>
                <Badge variant="outline" className="text-xs">Familiar Workflow</Badge>
                <Badge variant="outline" className="text-xs">Full Customization</Badge>
              </div>
            </div>

            <Alert className="border-orange-200 bg-orange-50">
              <AlertTriangle className="h-4 w-4 text-orange-600" />
              <AlertDescription className="text-xs">
                Requires technical knowledge of rule parameters and warehouse operations.
              </AlertDescription>
            </Alert>
          </CardContent>
        </Card>

        {/* AI-Enhanced Builder */}
        <Card 
          className={`cursor-pointer transition-all relative ${
            selectedMode === 'ai-enhanced' 
              ? 'ring-2 ring-blue-500 shadow-lg' 
              : 'hover:shadow-md'
          }`}
          onClick={() => handleModeSelection('ai-enhanced')}
        >
          <div className="absolute -top-2 -right-2">
            <Badge className="bg-gradient-to-r from-blue-500 to-purple-500 text-white text-xs px-2 py-1">
              <Sparkles className="w-3 h-3 mr-1" />
              RECOMMENDED
            </Badge>
          </div>
          
          <CardHeader className="pb-4">
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-3">
                <div className="p-2 rounded-lg bg-gradient-to-r from-blue-100 to-purple-100">
                  <Brain className="w-6 h-6 text-blue-600" />
                </div>
                <div>
                  <CardTitle className="text-xl">AI-Enhanced Smart Builder</CardTitle>
                  <p className="text-sm text-muted-foreground">Human-centered with AI intelligence</p>
                </div>
              </div>
              <Badge className="bg-gradient-to-r from-blue-500 to-purple-500 text-white border-0">
                AI-Powered
              </Badge>
            </div>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="space-y-3">
              <h4 className="font-medium text-sm">Perfect for:</h4>
              <ul className="space-y-2 text-sm text-muted-foreground">
                <li className="flex items-center gap-2">
                  <CheckCircle className="w-3 h-3 text-green-500" />
                  Warehouse managers and operations staff
                </li>
                <li className="flex items-center gap-2">
                  <CheckCircle className="w-3 h-3 text-green-500" />
                  Users who prefer business-focused interface
                </li>
                <li className="flex items-center gap-2">
                  <CheckCircle className="w-3 h-3 text-green-500" />
                  Problem-solving approach with guidance
                </li>
                <li className="flex items-center gap-2">
                  <CheckCircle className="w-3 h-3 text-green-500" />
                  Teams wanting intelligent recommendations
                </li>
              </ul>
            </div>

            <div className="space-y-2">
              <h4 className="font-medium text-sm">AI Features:</h4>
              <div className="flex flex-wrap gap-2">
                <Badge variant="outline" className="text-xs bg-blue-50 text-blue-700 border-blue-300">
                  <Brain className="w-2 h-2 mr-1" />
                  Smart Suggestions
                </Badge>
                <Badge variant="outline" className="text-xs bg-purple-50 text-purple-700 border-purple-300">
                  <Zap className="w-2 h-2 mr-1" />
                  Performance Predictions
                </Badge>
                <Badge variant="outline" className="text-xs bg-green-50 text-green-700 border-green-300">
                  Natural Language
                </Badge>
                <Badge variant="outline" className="text-xs bg-indigo-50 text-indigo-700 border-indigo-300">
                  Visual Scenarios
                </Badge>
              </div>
            </div>

            <Alert className="border-blue-200 bg-gradient-to-r from-blue-50 to-purple-50">
              <Brain className="h-4 w-4 text-blue-600" />
              <AlertDescription className="text-xs">
                <strong>85% faster</strong> rule creation with intelligent guidance and real-world context.
              </AlertDescription>
            </Alert>
          </CardContent>
        </Card>
      </div>

      {/* Comparison Stats */}
      <div className="max-w-4xl mx-auto">
        <Card className="border-2 border-muted">
          <CardHeader>
            <CardTitle className="text-center">Feature Comparison</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-6 text-center">
              <div>
                <h4 className="font-medium mb-2">Setup Time</h4>
                <div className="space-y-2">
                  <div className="text-sm text-muted-foreground">Classic: 10-15 minutes</div>
                  <div className="text-sm font-medium text-blue-600">AI-Enhanced: 3-5 minutes</div>
                </div>
              </div>
              <div>
                <h4 className="font-medium mb-2">Learning Curve</h4>
                <div className="space-y-2">
                  <div className="text-sm text-muted-foreground">Classic: Technical knowledge required</div>
                  <div className="text-sm font-medium text-blue-600">AI-Enhanced: Business knowledge sufficient</div>
                </div>
              </div>
              <div>
                <h4 className="font-medium mb-2">Accuracy</h4>
                <div className="space-y-2">
                  <div className="text-sm text-muted-foreground">Classic: Depends on user expertise</div>
                  <div className="text-sm font-medium text-blue-600">AI-Enhanced: AI-optimized parameters</div>
                </div>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Action Buttons */}
      <div className="flex justify-center gap-4">
        <Button 
          variant="outline" 
          onClick={() => setShowComparison(false)}
          className="flex items-center gap-2"
        >
          Skip Comparison
          <ArrowRight className="w-4 h-4" />
        </Button>
      </div>

      {/* Help Text */}
      <div className="text-center">
        <p className="text-xs text-muted-foreground max-w-2xl mx-auto">
          💡 <strong>New to warehouse rule creation?</strong> The AI-Enhanced Smart Builder guides you through 
          real warehouse problems and provides intelligent suggestions. <strong>Experienced user?</strong> The 
          Classic Builder gives you direct control over all technical parameters.
        </p>
      </div>
    </div>
  )
}