"use client"

import React from 'react'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'

// Nuclear test - absolutely minimal button that triggers the edit flow
export function NuclearTest() {
  
  // Test 1: Absolutely minimal button with no hooks at all
  const testMinimalButton = () => {
    console.log("=== MINIMAL BUTTON TEST ===")
    console.log("This should NOT cause any hook errors")
  }

  // Test 2: Button that simulates the problematic edit action
  const testEditAction = () => {
    console.log("=== EDIT ACTION TEST ===")
    try {
      // Simulate the problematic action without any hooks
      console.log("Simulating rule edit without hooks...")
      console.log("If this logs successfully, the issue is elsewhere")
    } catch (error) {
      console.error("ERROR in testEditAction:", error)
    }
  }

  return (
    <Card className="max-w-2xl mx-auto">
      <CardHeader>
        <CardTitle>Nuclear Test - Zero Dependencies</CardTitle>
      </CardHeader>
      <CardContent className="space-y-4">
        <div className="text-sm text-red-600 font-medium">
          ⚠️ NUCLEAR TEST: If these buttons cause React Hook Error #185, 
          the problem is in the basic button/event system itself.
        </div>

        <div className="space-y-3">
          <Button
            onClick={testMinimalButton}
            variant="outline"
            className="w-full"
          >
            Test 1: Minimal Button (NO HOOKS)
          </Button>
          
          <Button
            onClick={testEditAction}
            variant="outline"
            className="w-full"
          >
            Test 2: Simulate Edit Action (NO HOOKS)
          </Button>
        </div>

        <div className="text-xs bg-gray-100 p-3 rounded">
          <strong>Expected Results:</strong>
          <ul className="list-disc list-inside mt-1">
            <li>Both buttons should work without any errors</li>
            <li>Console should show the test messages</li>
            <li>NO React Hook Error #185 should occur</li>
          </ul>
          <p className="mt-2 text-red-600">
            <strong>If errors still occur:</strong> The problem is in the core React/Next.js setup, 
            not in our rule editing code.
          </p>
        </div>
      </CardContent>
    </Card>
  )
}