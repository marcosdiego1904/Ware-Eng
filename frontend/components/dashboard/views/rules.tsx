"use client"

import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Settings, Package } from 'lucide-react'

export function RulesView() {
  return (
    <div className="p-6">
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Settings className="w-5 h-5" />
            Warehouse Rules
          </CardTitle>
        </CardHeader>
        <CardContent className="text-center py-12">
          <Package className="w-16 h-16 text-gray-400 mx-auto mb-4" />
          <h3 className="text-lg font-medium mb-2">Rules Configuration</h3>
          <p className="text-gray-600 mb-4">
            Configure warehouse rules, location patterns, and detection parameters
          </p>
          <p className="text-sm text-blue-600">
            🚧 Coming next! Rules viewer and configuration interface
          </p>
        </CardContent>
      </Card>
    </div>
  )
}