"use client"

import { useState } from 'react'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Alert, AlertDescription } from '@/components/ui/alert'
import { Plus, Info } from 'lucide-react'

interface RuleCondition {
  id: string
  field: string
  operator: string
  value: string | number | string[]
  connector?: 'AND' | 'OR'
}

export function VisualBuilderDebug() {
  const [conditions, setConditions] = useState<RuleCondition[]>([
    {
      id: 'condition-initial',
      field: 'time_threshold_hours',
      operator: 'greater_than',
      value: 6
    }
  ])

  const addCondition = () => {
    console.log('Add condition clicked - current conditions:', conditions.length)
    const newCondition: RuleCondition = {
      id: `condition-${Date.now()}`,
      field: 'time_threshold_hours',
      operator: 'greater_than',
      value: 8,
      connector: 'AND'
    }
    console.log('Adding new condition:', newCondition)
    setConditions(prev => {
      const updated = [...prev, newCondition]
      console.log('Updated conditions:', updated)
      return updated
    })
  }

  const removeCondition = (id: string) => {
    console.log('Remove condition clicked:', id)
    setConditions(prev => prev.filter(c => c.id !== id))
  }

  return (
    <div className="max-w-4xl mx-auto p-6 space-y-6">
      <Card>
        <CardHeader>
          <CardTitle>Visual Rule Builder - Debug Mode</CardTitle>
          <p className="text-muted-foreground">
            Testing the "Add Another Condition" functionality
          </p>
        </CardHeader>
        <CardContent className="space-y-4">
          {/* Current Conditions Count */}
          <Alert>
            <Info className="h-4 w-4" />
            <AlertDescription>
              <strong>Current Conditions:</strong> {conditions.length}
            </AlertDescription>
          </Alert>

          {/* Render Conditions */}
          <div className="space-y-3">
            {conditions.map((condition, index) => (
              <Card key={condition.id} className="border-l-4 border-l-blue-500">
                <CardContent className="pt-4">
                  <div className="flex items-center justify-between">
                    <div>
                      <div className="font-medium">
                        Condition {index + 1}: {condition.field}
                      </div>
                      <div className="text-sm text-muted-foreground">
                        {condition.operator} {condition.value}
                        {condition.connector && ` (${condition.connector})`}
                      </div>
                    </div>
                    {conditions.length > 1 && (
                      <Button
                        variant="outline"
                        size="sm"
                        onClick={() => removeCondition(condition.id)}
                        className="text-red-600 hover:text-red-700"
                      >
                        Remove
                      </Button>
                    )}
                  </div>
                </CardContent>
              </Card>
            ))}
          </div>

          {/* Add Another Condition Button */}
          <div className="flex justify-center pt-4">
            <Button 
              variant="outline" 
              onClick={addCondition}
              className="flex items-center gap-2"
            >
              <Plus className="w-4 h-4" />
              Add Another Condition
            </Button>
          </div>

          {/* Debug Info */}
          <Card className="bg-muted/30">
            <CardContent className="pt-4">
              <h4 className="font-medium mb-2">Debug Information:</h4>
              <pre className="text-xs bg-background p-2 rounded overflow-auto">
                {JSON.stringify(conditions, null, 2)}
              </pre>
            </CardContent>
          </Card>

          {/* Test Instructions */}
          <Alert>
            <Info className="h-4 w-4" />
            <AlertDescription>
              <strong>Test Instructions:</strong>
              <ol className="list-decimal list-inside mt-2 space-y-1 text-sm">
                <li>Click "Add Another Condition" - should increase condition count</li>
                <li>Check browser console for debug logs</li>
                <li>Verify new conditions appear in the list</li>
                <li>Test "Remove" buttons work for multiple conditions</li>
              </ol>
            </AlertDescription>
          </Alert>
        </CardContent>
      </Card>
    </div>
  )
}