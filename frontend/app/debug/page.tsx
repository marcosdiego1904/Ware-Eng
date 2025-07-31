"use client"

import { AuthDebug } from '@/components/debug/auth-debug'
import { RuleEditTest } from '@/components/debug/rule-edit-test'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs'

export default function DebugPage() {
  return (
    <div className="p-6">
      <h1 className="text-2xl font-bold mb-6">Debug Tools</h1>
      
      <Tabs defaultValue="auth" className="w-full">
        <TabsList>
          <TabsTrigger value="auth">Auth Debug</TabsTrigger>
          <TabsTrigger value="rules">Rule Edit Test</TabsTrigger>
        </TabsList>
        
        <TabsContent value="auth">
          <AuthDebug />
        </TabsContent>
        
        <TabsContent value="rules">
          <RuleEditTest />
        </TabsContent>
      </Tabs>
    </div>
  )
}