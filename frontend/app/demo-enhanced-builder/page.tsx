"use client"

import { useState } from 'react'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Badge } from '@/components/ui/badge'
import { Alert, AlertDescription } from '@/components/ui/alert'
import { EnhancedVisualBuilder } from '@/components/rules/enhanced-visual-builder'
import { EnhancedSmartBuilder } from '@/components/rules/enhanced-smart-builder'
import { VisualRuleBuilder } from '@/components/rules/visual-rule-builder'
import { 
  ArrowRight, 
  ArrowLeft,
  Sparkles,
  Wrench,
  Eye,
  CheckCircle,
  Info,
  Lightbulb
} from 'lucide-react'

export default function DemoEnhancedBuilderPage() {
  const [currentView, setCurrentView] = useState<'comparison' | 'enhanced' | 'smart' | 'original'>('comparison')
  const [createdRule, setCreatedRule] = useState<any>(null)

  const handleRuleCreate = (ruleData: any) => {
    setCreatedRule(ruleData)
    console.log('Rule created:', ruleData)
  }

  const renderComparison = () => (
    <div className="min-h-screen bg-gradient-to-br from-purple-50 via-white to-blue-50 p-6">
      <div className="max-w-6xl mx-auto space-y-8">
        {/* Header */}
        <div className="text-center space-y-4">
          <h1 className="text-4xl font-bold">Enhanced Rule Builder Demo</h1>
          <p className="text-xl text-muted-foreground max-w-3xl mx-auto">
            Compare the current advanced builder with the new human-centered approach
          </p>
          <Badge variant="outline" className="text-lg px-4 py-2">
            🚀 Prototype Demo
          </Badge>
        </div>

        {/* Key Improvements */}
        <Alert className="max-w-4xl mx-auto border-blue-200 bg-blue-50">
          <Lightbulb className="h-5 w-5 text-blue-600" />
          <AlertDescription className="text-base">
            <strong>Key Improvements in Enhanced Builder:</strong>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mt-3 text-sm">
              <div>• Problem-first approach (not technical configuration)</div>
              <div>• Visual scenarios with real-world examples</div>
              <div>• Natural language instead of technical terms</div>
              <div>• Context and impact information at every step</div>
              <div>• Progressive confidence building</div>
              <div>• Business impact predictions</div>
            </div>
          </AlertDescription>
        </Alert>

        {/* Comparison Cards */}
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* Current Builder */}
          <Card className="border-2 border-orange-200">
            <CardHeader className="bg-orange-50">
              <div className="flex items-center gap-3">
                <div className="p-2 rounded-lg bg-orange-100">
                  <Wrench className="w-5 h-5 text-orange-600" />
                </div>
                <div>
                  <CardTitle className="text-xl">Current Advanced Builder</CardTitle>
                  <p className="text-muted-foreground">Technical, configuration-focused</p>
                </div>
              </div>
            </CardHeader>
            <CardContent className="space-y-4 pt-6">
              <div className="space-y-3">
                <h4 className="font-medium">Current Approach:</h4>
                <ul className="space-y-2 text-sm text-muted-foreground">
                  <li>• Start with technical rule types</li>
                  <li>• Configure abstract conditions</li>
                  <li>• Set numeric thresholds</li>
                  <li>• Limited context or guidance</li>
                  <li>• Requires technical understanding</li>
                </ul>
              </div>
              
              <div className="space-y-3">
                <h4 className="font-medium">User Experience:</h4>
                <div className="bg-orange-50 p-3 rounded-lg text-sm">
                  <p>"What does 'time_threshold_hours: 6' actually mean?"</p>
                  <p className="text-muted-foreground mt-1">- Typical user confusion</p>
                </div>
              </div>

              <Button 
                variant="outline" 
                onClick={() => setCurrentView('original')}
                className="w-full"
              >
                <Eye className="w-4 h-4 mr-2" />
                Try Current Builder
              </Button>
            </CardContent>
          </Card>

          {/* Enhanced Builder */}
          <Card className="border-2 border-green-200 shadow-lg">
            <CardHeader className="bg-green-50">
              <div className="flex items-center gap-3">
                <div className="p-2 rounded-lg bg-green-100">
                  <Sparkles className="w-5 h-5 text-green-600" />
                </div>
                <div>
                  <CardTitle className="text-lg">Enhanced Visual Builder</CardTitle>
                  <p className="text-muted-foreground text-sm">Problem-focused approach</p>
                  <Badge variant="outline" className="mt-1 border-green-300 text-green-700 bg-green-50 text-xs">
                    Level 1
                  </Badge>
                </div>
              </div>
            </CardHeader>
            <CardContent className="space-y-4 pt-4">
              <div className="space-y-2">
                <h4 className="font-medium text-sm">Enhanced Approach:</h4>
                <ul className="space-y-1 text-xs text-muted-foreground">
                  <li>• Start with real warehouse problems</li>
                  <li>• Visual scenarios with examples</li>
                  <li>• Natural language configuration</li>
                  <li>• Business impact context</li>
                </ul>
              </div>

              <Button 
                onClick={() => setCurrentView('enhanced')}
                variant="outline"
                className="w-full"
              >
                <Sparkles className="w-4 h-4 mr-2" />
                Try Enhanced Builder
              </Button>
            </CardContent>
          </Card>

          {/* Smart Builder */}
          <Card className="border-2 border-blue-200 shadow-xl ring-2 ring-blue-100">
            <CardHeader className="bg-gradient-to-r from-blue-50 to-purple-50">
              <div className="flex items-center gap-3">
                <div className="p-2 rounded-lg bg-gradient-to-r from-blue-100 to-purple-100">
                  <Sparkles className="w-5 h-5 text-blue-600" />
                </div>
                <div>
                  <CardTitle className="text-lg">Smart AI Builder</CardTitle>
                  <p className="text-muted-foreground text-sm">AI-powered suggestions</p>
                  <Badge variant="outline" className="mt-1 border-blue-300 text-blue-700 bg-blue-50 text-xs">
                    Level 2 - NEW! ✨
                  </Badge>
                </div>
              </div>
            </CardHeader>
            <CardContent className="space-y-4 pt-4">
              <div className="space-y-2">
                <h4 className="font-medium text-sm">Smart Features:</h4>
                <ul className="space-y-1 text-xs text-muted-foreground">
                  <li>• AI-powered smart suggestions</li>
                  <li>• Context-aware recommendations</li>
                  <li>• Intelligent parameter tuning</li>
                  <li>• Performance predictions</li>
                  <li>• Advanced visual conditions</li>
                </ul>
              </div>
              
              <div className="space-y-2">
                <div className="bg-gradient-to-r from-blue-50 to-purple-50 p-2 rounded-lg text-xs">
                  <p className="font-medium">"AI suggests: 4-hour limit for your warehouse size"</p>
                  <p className="text-muted-foreground">- Intelligent recommendations</p>
                </div>
              </div>

              <Button 
                onClick={() => setCurrentView('smart')}
                className="w-full bg-gradient-to-r from-blue-600 to-purple-600 hover:from-blue-700 hover:to-purple-700"
              >
                <Sparkles className="w-4 h-4 mr-2" />
                Try Smart Builder
                <ArrowRight className="w-4 h-4 ml-2" />
              </Button>
            </CardContent>
          </Card>
        </div>

        {/* User Personas */}
        <div className="max-w-4xl mx-auto">
          <h3 className="text-2xl font-bold text-center mb-6">Who Benefits?</h3>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            <Card>
              <CardContent className="p-6 text-center">
                <div className="text-4xl mb-3">👩‍💼</div>
                <h4 className="font-medium mb-2">Warehouse Manager</h4>
                <p className="text-sm text-muted-foreground">
                  Understands business impact and can create rules that solve real problems
                </p>
              </CardContent>
            </Card>
            <Card>
              <CardContent className="p-6 text-center">
                <div className="text-4xl mb-3">📋</div>
                <h4 className="font-medium mb-2">Inventory Clerk</h4>
                <p className="text-sm text-muted-foreground">
                  Can set up alerts using familiar warehouse language and scenarios
                </p>
              </CardContent>
            </Card>
            <Card>
              <CardContent className="p-6 text-center">
                <div className="text-4xl mb-3">🔧</div>
                <h4 className="font-medium mb-2">Operations Team</h4>
                <p className="text-sm text-muted-foreground">
                  Quickly configure rules based on daily operational challenges
                </p>
              </CardContent>
            </Card>
          </div>
        </div>

        {/* Results Preview */}
        {createdRule && (
          <Card className="max-w-4xl mx-auto border-2 border-green-200 bg-green-50">
            <CardHeader>
              <div className="flex items-center gap-3">
                <CheckCircle className="w-6 h-6 text-green-600" />
                <div>
                  <CardTitle className="text-green-800">Rule Created Successfully!</CardTitle>
                  <p className="text-green-700">Here's what was generated from the enhanced builder</p>
                </div>
              </div>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="bg-white p-4 rounded-lg">
                <h4 className="font-medium mb-2">Generated Rule Data:</h4>
                <pre className="text-xs bg-gray-100 p-3 rounded overflow-auto">
                  {JSON.stringify(createdRule, null, 2)}
                </pre>
              </div>
              <Alert>
                <Info className="h-4 w-4" />
                <AlertDescription>
                  <strong>Next Step:</strong> This data would be converted to the backend rule format and saved to the database.
                  The enhanced builder makes it easy for users to create rules, then translates their intent into technical specifications.
                </AlertDescription>
              </Alert>
            </CardContent>
          </Card>
        )}
      </div>
    </div>
  )

  const renderEnhancedBuilder = () => (
    <div>
      <div className="fixed top-4 left-4 z-50">
        <Button variant="outline" onClick={() => setCurrentView('comparison')}>
          <ArrowLeft className="w-4 h-4 mr-2" />
          Back to Comparison
        </Button>
      </div>
      <EnhancedVisualBuilder 
        onRuleCreate={handleRuleCreate}
        onCancel={() => setCurrentView('comparison')}
      />
    </div>
  )

  const renderSmartBuilder = () => (
    <div>
      <div className="fixed top-4 left-4 z-50">
        <Button variant="outline" onClick={() => setCurrentView('comparison')}>
          <ArrowLeft className="w-4 h-4 mr-2" />
          Back to Comparison
        </Button>
      </div>
      <EnhancedSmartBuilder 
        onRuleCreate={handleRuleCreate}
        onCancel={() => setCurrentView('comparison')}
      />
    </div>
  )

  const renderOriginalBuilder = () => (
    <div className="min-h-screen bg-white p-6">
      <div className="max-w-4xl mx-auto space-y-6">
        <div className="flex items-center justify-between">
          <div>
            <h2 className="text-2xl font-bold">Current Advanced Builder</h2>
            <p className="text-muted-foreground">The technical approach currently in use</p>
          </div>
          <Button variant="outline" onClick={() => setCurrentView('comparison')}>
            <ArrowLeft className="w-4 h-4 mr-2" />
            Back to Comparison
          </Button>
        </div>
        
        <Alert className="border-orange-200 bg-orange-50">
          <Info className="h-4 w-4 text-orange-600" />
          <AlertDescription>
            <strong>Note:</strong> This is the current approach. Try creating a rule and notice the technical complexity.
            Compare this experience with the Enhanced Builder.
          </AlertDescription>
        </Alert>

        <VisualRuleBuilder
          initialConditions={{}}
          ruleType="STAGNANT_PALLETS"
          onConditionsChange={(conditions) => console.log('Conditions changed:', conditions)}
          onValidate={() => console.log('Validating...')}
          isValidating={false}
          validationResult={null}
        />
      </div>
    </div>
  )

  return (
    <div>
      {currentView === 'comparison' && renderComparison()}
      {currentView === 'enhanced' && renderEnhancedBuilder()}
      {currentView === 'smart' && renderSmartBuilder()}
      {currentView === 'original' && renderOriginalBuilder()}
    </div>
  )
}