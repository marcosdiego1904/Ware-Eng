"use client"

import React from 'react'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { useRulesStore } from '@/lib/rules-store'

// Test component to isolate the exact hook violation
export function HookIsolationTest() {
  // Get the exact same store methods used in the edit flow
  const { setSelectedRule, setCurrentSubView } = useRulesStore()

  // Create a test custom rule similar to what would trigger the error
  const testCustomRule = {
    id: 999,
    name: "Test Custom Rule",
    description: "Test description",
    rule_type: "STAGNANT_PALLETS",
    category_id: 1,
    category_name: "Operations",
    priority: "MEDIUM" as const,
    is_active: true,
    is_default: false, // This is the key difference - custom rule
    conditions: {
      time_threshold_hours: { ">=": 6 }
    },
    parameters: {},
    creator_username: "test",
    created_by: 1,
    created_at: new Date().toISOString(),
    updated_at: new Date().toISOString()
  }

  // Test the exact same action sequence that happens during edit
  const testEditFlow = () => {
    console.log('=== TESTING EDIT FLOW ===')
    console.log('1. About to call setSelectedRule with custom rule:', testCustomRule)
    
    try {
      // This is the exact same sequence as handleRuleAction
      setSelectedRule(testCustomRule)
      console.log('2. setSelectedRule succeeded')
      
      setCurrentSubView('create')
      console.log('3. setCurrentSubView succeeded')
      
      console.log('=== EDIT FLOW COMPLETED SUCCESSFULLY ===')
    } catch (error) {
      console.error('=== EDIT FLOW FAILED ===')
      console.error('Error in testEditFlow:', error)
    }
  }

  // Test with a default rule to compare
  const testDefaultRule = {
    ...testCustomRule,
    id: 998,
    name: "Test Default Rule",
    is_default: true, // This is the key difference - default rule
    created_by: 1,
  }

  const testDefaultEditFlow = () => {
    console.log('=== TESTING DEFAULT RULE EDIT FLOW ===')
    console.log('1. About to call setSelectedRule with default rule:', testDefaultRule)
    
    try {
      setSelectedRule(testDefaultRule)
      console.log('2. setSelectedRule succeeded for default rule')
      
      setCurrentSubView('create')
      console.log('3. setCurrentSubView succeeded for default rule')
      
      console.log('=== DEFAULT RULE EDIT FLOW COMPLETED SUCCESSFULLY ===')
    } catch (error) {
      console.error('=== DEFAULT RULE EDIT FLOW FAILED ===')
      console.error('Error in testDefaultEditFlow:', error)
    }
  }

  return (
    <Card className="max-w-2xl mx-auto">
      <CardHeader>
        <CardTitle>Hook Isolation Test</CardTitle>
      </CardHeader>
      <CardContent className="space-y-4">
        <div className="text-sm text-muted-foreground">
          This component isolates the exact edit flow to identify where the hook violation occurs.
          Open browser console to see detailed logs.
        </div>

        <div className="space-y-2">
          <Button
            onClick={testDefaultEditFlow}
            variant="outline"
            className="w-full"
          >
            Test Default Rule Edit Flow (Should Work)
          </Button>
          
          <Button
            onClick={testEditFlow}
            variant="outline"
            className="w-full"
          >
            Test Custom Rule Edit Flow (May Cause Hook Error)
          </Button>
        </div>

        <div className="text-xs text-gray-600 bg-gray-50 p-3 rounded">
          <strong>Instructions:</strong>
          <ol className="list-decimal list-inside mt-1 space-y-1">
            <li>Click &quot;Test Default Rule Edit Flow&quot; first - should work fine</li>
            <li>Click &quot;Test Custom Rule Edit Flow&quot; - may trigger React Hook Error #185</li>
            <li>Compare the console logs to see where the error occurs</li>
          </ol>
        </div>
      </CardContent>
    </Card>
  )
}