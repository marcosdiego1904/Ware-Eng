"use client"

import { useState } from 'react'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { useRulesStore } from '@/lib/rules-store'
import { SimpleErrorBoundary } from '@/components/ui/error-boundary'

export function MinimalRuleTest() {
  const [step, setStep] = useState(0)
  const [error, setError] = useState<string | null>(null)

  const testStep = (stepNumber: number, testName: string, testFn: () => void) => {
    setError(null)
    console.log(`Testing step ${stepNumber}: ${testName}`)
    
    try {
      testFn()
      setStep(stepNumber)
      console.log(`✅ Step ${stepNumber} passed`)
    } catch (err) {
      console.error(`❌ Step ${stepNumber} failed:`, err)
      setError(`Step ${stepNumber} failed: ${err instanceof Error ? err.message : 'Unknown error'}`)
    }
  }

  return (
    <Card className="max-w-2xl mx-auto">
      <CardHeader>
        <CardTitle>Minimal Rule Hook Test</CardTitle>
      </CardHeader>
      <CardContent className="space-y-4">
        <div className="text-sm text-muted-foreground">
          Current step: {step} | Testing hook calls step by step
        </div>

        <div className="grid grid-cols-2 gap-2">
          <Button
            onClick={() => testStep(1, 'Basic store access', () => {
              const state = useRulesStore.getState()
              console.log('Store state keys:', Object.keys(state))
            })}
            variant="outline"
            size="sm"
          >
            Test 1: Store Access
          </Button>

          <SimpleErrorBoundary message="Test 2 failed">
            <TestComponentWithHook step={2} onSuccess={() => setStep(2)} onError={setError} />
          </SimpleErrorBoundary>

          <Button
            onClick={() => testStep(3, 'Store methods', () => {
              const { loadRules } = useRulesStore.getState()
              console.log('loadRules function:', typeof loadRules)
            })}
            variant="outline"
            size="sm"
          >
            Test 3: Store Methods
          </Button>

          <Button
            onClick={() => testStep(4, 'Set selected rule', () => {
              const { setSelectedRule } = useRulesStore.getState()
              console.log('setSelectedRule function:', typeof setSelectedRule)
            })}
            variant="outline"
            size="sm"
          >
            Test 4: Set Methods
          </Button>
        </div>

        {error && (
          <div className="p-3 bg-red-50 border border-red-200 rounded text-red-700">
            <strong>Error:</strong> {error}
          </div>
        )}

        <div className="text-xs text-gray-500 bg-gray-50 p-2 rounded">
          Use browser dev tools to see detailed console logs for each test
        </div>
      </CardContent>
    </Card>
  )
}

// Test component that uses hooks properly
function TestComponentWithHook({ 
  step, 
  onSuccess, 
  onError 
}: { 
  step: number
  onSuccess: () => void
  onError: (error: string) => void
}) {
  const { rules, isLoading } = useRulesStore()

  const handleTest = () => {
    try {
      console.log(`Testing step ${step}: Hook in component`)
      console.log('Rules array:', rules)
      console.log('Is loading:', isLoading)
      onSuccess()
      console.log(`✅ Step ${step} passed`)
    } catch (err) {
      console.error(`❌ Step ${step} failed:`, err)
      onError(`Step ${step} failed: ${err instanceof Error ? err.message : 'Unknown error'}`)
    }
  }

  return (
    <Button onClick={handleTest} variant="outline" size="sm">
      Test 2: Hook in Component
    </Button>
  )
}