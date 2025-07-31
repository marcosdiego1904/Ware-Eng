"use client"

import { useState, useEffect } from 'react'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { useRulesStore } from '@/lib/rules-store'

export function RuleEditTest() {
  const [error, setError] = useState<string | null>(null)
  const [success, setSuccess] = useState<string | null>(null)
  const { rules, loadRules, updateRule } = useRulesStore()

  useEffect(() => {
    loadRules().catch(err => {
      setError(`Failed to load rules: ${err.message}`)
    })
  }, [loadRules])

  const testEditCustomRule = async () => {
    setError(null)
    setSuccess(null)
    
    try {
      // Find the first custom rule (non-default)
      const customRule = rules.find(rule => !rule.is_default)
      
      if (!customRule) {
        setError('No custom rules found to test with')
        return
      }

      console.log('Testing edit of custom rule:', customRule)
      console.log('Rule conditions:', customRule.conditions)
      console.log('Rule parameters:', customRule.parameters)

      // Validate rule data structure
      const requiredFields = ['name', 'rule_type', 'category_id']
      const missingFields = requiredFields.filter(field => !customRule[field as keyof typeof customRule])
      
      if (missingFields.length > 0) {
        setError(`Rule is missing required fields: ${missingFields.join(', ')}`)
        return
      }

      // Try to update the rule with minimal changes
      const updateData = {
        name: customRule.name,
        description: customRule.description || '',
        category_id: customRule.category_id,
        rule_type: customRule.rule_type,
        conditions: customRule.conditions || {},
        parameters: customRule.parameters || {},
        priority: customRule.priority || 'MEDIUM',
        is_active: customRule.is_active ?? true
      }

      console.log('Update data:', updateData)

      await updateRule(customRule.id, updateData)
      setSuccess(`Successfully updated rule: ${customRule.name}`)
    } catch (err) {
      console.error('Test edit failed:', err)
      setError(`Test edit failed: ${err instanceof Error ? err.message : 'Unknown error'}`)
    }
  }

  const testUIEdit = () => {
    setError(null)
    setSuccess(null)
    
    try {
      const customRule = rules.find(rule => !rule.is_default)
      
      if (!customRule) {
        setError('No custom rules found to test with')
        return
      }

      console.log('Testing UI edit simulation for rule:', customRule)
      
      // Simulate what happens when clicking edit
      const { setSelectedRule, setCurrentSubView } = useRulesStore.getState()
      
      console.log('Setting selected rule...')
      setSelectedRule(customRule)
      
      console.log('Setting current sub view to create...')
      setCurrentSubView('create')
      
      setSuccess('UI edit simulation completed - check the Create Rule tab')
    } catch (err) {
      console.error('UI edit simulation failed:', err)
      setError(`UI edit simulation failed: ${err instanceof Error ? err.message : 'Unknown error'}`)
    }
  }

  const testEditDefaultRule = async () => {
    setError(null)
    setSuccess(null)
    
    try {
      // Find the first default rule
      const defaultRule = rules.find(rule => rule.is_default)
      
      if (!defaultRule) {
        setError('No default rules found to test with')
        return
      }

      console.log('Testing edit of default rule:', defaultRule)

      // Try to update the rule with minimal changes
      const updateData = {
        name: defaultRule.name,
        description: defaultRule.description,
        category_id: defaultRule.category_id,
        rule_type: defaultRule.rule_type,
        conditions: defaultRule.conditions || {},
        parameters: defaultRule.parameters || {},
        priority: 'HIGH' as const, // Change priority to test
        is_active: defaultRule.is_active
      }

      console.log('Update data:', updateData)

      await updateRule(defaultRule.id, updateData)
      setSuccess(`Successfully updated rule: ${defaultRule.name}`)
    } catch (err) {
      console.error('Test edit failed:', err)
      setError(`Test edit failed: ${err instanceof Error ? err.message : 'Unknown error'}`)
    }
  }

  return (
    <Card className="max-w-2xl mx-auto">
      <CardHeader>
        <CardTitle>Rule Edit Test</CardTitle>
      </CardHeader>
      <CardContent className="space-y-4">
        <div className="text-sm text-muted-foreground">
          Found {rules.length} rules ({rules.filter(r => !r.is_default).length} custom, {rules.filter(r => r.is_default).length} default)
        </div>
        
        <div className="flex gap-4 flex-wrap">
          <Button onClick={testEditCustomRule} variant="outline">
            Test Edit Custom Rule (API)
          </Button>
          <Button onClick={testEditDefaultRule} variant="outline">
            Test Edit Default Rule (API)
          </Button>
          <Button onClick={testUIEdit} variant="secondary">
            Test UI Edit Flow
          </Button>
        </div>

        {error && (
          <div className="p-3 bg-red-50 border border-red-200 rounded text-red-700">
            <strong>Error:</strong> {error}
          </div>
        )}

        {success && (
          <div className="p-3 bg-green-50 border border-green-200 rounded text-green-700">
            <strong>Success:</strong> {success}
          </div>
        )}

        <div className="mt-6">
          <h4 className="font-medium mb-2">Available Rules:</h4>
          <div className="space-y-2 max-h-60 overflow-y-auto">
            {rules.map(rule => (
              <div key={rule.id} className="text-sm p-2 bg-gray-50 rounded">
                <div className="flex items-center justify-between">
                  <span className="font-medium">{rule.name}</span>
                  <span className={`px-2 py-1 rounded text-xs ${
                    rule.is_default 
                      ? 'bg-blue-100 text-blue-700' 
                      : 'bg-green-100 text-green-700'
                  }`}>
                    {rule.is_default ? 'Default' : 'Custom'}
                  </span>
                </div>
                <div className="text-gray-600 mt-1">
                  Type: {rule.rule_type}, Priority: {rule.priority}
                </div>
                <div className="text-gray-500 text-xs mt-1">
                  Conditions: {JSON.stringify(rule.conditions)}
                </div>
              </div>
            ))}
          </div>
        </div>
      </CardContent>
    </Card>
  )
}