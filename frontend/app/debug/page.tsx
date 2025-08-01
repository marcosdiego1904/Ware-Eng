"use client"

import { AuthDebug } from '@/components/debug/auth-debug'
import { RuleEditTest } from '@/components/debug/rule-edit-test'
import { MinimalRuleTest } from '@/components/debug/minimal-rule-test'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs'

export default function DebugPage() {
  return (
    <div className="p-6">
      <h1 className="text-2xl font-bold mb-6">Debug Tools</h1>
      
      <Tabs defaultValue="auth" className="w-full">
        <TabsList>
          <TabsTrigger value="auth">Auth Debug</TabsTrigger>
          <TabsTrigger value="rules">Rule Edit Test</TabsTrigger>
          <TabsTrigger value="minimal">Hook Test</TabsTrigger>
        </TabsList>
        
        <TabsContent value="auth">
          <AuthDebug />
        </TabsContent>
        
        <TabsContent value="rules">
          <RuleEditTest />
        </TabsContent>
        
        <TabsContent value="minimal">
          <MinimalRuleTest />
        </TabsContent>
      </Tabs>
    </div>
  )
}