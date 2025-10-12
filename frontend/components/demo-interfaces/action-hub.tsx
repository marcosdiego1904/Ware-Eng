'use client'

import * as React from "react"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Badge } from "@/components/ui/badge"
import { Separator } from "@/components/ui/separator"
import { cn } from "@/lib/utils"

// Mock data for demonstration
const mockAnomalyData = {
  forgottenPallets: {
    count: 23,
    avgHours: 78,
    maxHours: 125,
    locations: ["RECV-01", "RECV-02", "RECV-03", "RECV-04"],
    priority: "critical",
    estimatedValue: "$45,000"
  },
  stuckPallets: {
    count: 15,
    avgHours: 45,
    maxHours: 67,
    locations: ["AISLE-02", "AISLE-05", "AISLE-09"],
    priority: "high",
    estimatedImpact: "Flow disruption"
  },
  overcapacity: {
    count: 31,
    avgPercentage: 150,
    maxPercentage: 210,
    locations: ["Various storage areas"],
    priority: "medium",
    physicalRisk: "Safety concern"
  },
  lotStragglers: {
    count: 8,
    status: "Incomplete",
    locations: ["Mixed areas"],
    priority: "medium",
    completionRisk: "Delivery delays"
  }
}

const mockDetailedItems = [
  { id: "PLT-4829", location: "RECV-01", duration: "125h", product: "Electronics", priority: "critical" },
  { id: "PLT-4723", location: "RECV-01", duration: "98h", product: "Furniture", priority: "critical" },
  { id: "PLT-4651", location: "RECV-02", duration: "87h", product: "Clothing", priority: "high" },
  { id: "PLT-4590", location: "RECV-02", duration: "78h", product: "Tools", priority: "high" },
  { id: "PLT-4502", location: "RECV-03", duration: "72h", product: "Books", priority: "medium" },
  { id: "PLT-4445", location: "RECV-03", duration: "68h", product: "Electronics", priority: "medium" },
]

interface ActionHubProps {
  className?: string
  onCategoryClick?: (category: string) => void
  onBackToHub?: () => void
}

export function ActionHub({ className, onCategoryClick, onBackToHub }: ActionHubProps) {
  return (
    <div className={cn("max-w-6xl mx-auto p-6 space-y-6", className)}>

      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-foreground flex items-center gap-3">
            🎯 Action Required - Monday
          </h1>
          <p className="text-muted-foreground mt-1">
            Prioritized list of warehouse issues requiring immediate attention
          </p>
        </div>
        <Button variant="outline" onClick={onBackToHub}>
          ← Back to Hub
        </Button>
      </div>

      {/* Action Categories Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">

        {/* Forgotten Pallets - Critical */}
        <Card
          className="cursor-pointer hover:shadow-lg transition-shadow border-l-4 border-l-red-500"
          onClick={() => onCategoryClick?.('forgotten-pallets')}
        >
          <CardHeader className="pb-4">
            <div className="flex items-center justify-between">
              <CardTitle className="text-lg flex items-center gap-2">
                <span>FORGOTTEN PALLETS</span>
                <Badge variant="destructive">CRITICAL</Badge>
              </CardTitle>
              <div className="text-right text-sm text-muted-foreground">
                Est. Value: {mockAnomalyData.forgottenPallets.estimatedValue}
              </div>
            </div>
          </CardHeader>
          <CardContent>
            <div className="grid grid-cols-2 gap-4">
              <div>
                <div className="text-2xl font-bold text-red-600 dark:text-red-400">
                  {mockAnomalyData.forgottenPallets.count} pallets
                </div>
                <div className="text-sm text-muted-foreground">Need attention</div>
              </div>
              <div className="text-right">
                <div className="text-lg font-semibold">
                  Avg: {mockAnomalyData.forgottenPallets.avgHours}h
                </div>
                <div className="text-sm text-muted-foreground">
                  Max: {mockAnomalyData.forgottenPallets.maxHours}h
                </div>
              </div>
            </div>
            <Separator className="my-3" />
            <div className="flex items-center justify-between">
              <div className="text-sm text-muted-foreground">
                Areas: {mockAnomalyData.forgottenPallets.locations.slice(0, 2).join(", ")} + {mockAnomalyData.forgottenPallets.locations.length - 2} more
              </div>
              <Button size="sm" variant="destructive">
                View Details →
              </Button>
            </div>
          </CardContent>
        </Card>

        {/* Stuck Pallets - High */}
        <Card
          className="cursor-pointer hover:shadow-lg transition-shadow border-l-4 border-l-orange-500"
          onClick={() => onCategoryClick?.('stuck-pallets')}
        >
          <CardHeader className="pb-4">
            <div className="flex items-center justify-between">
              <CardTitle className="text-lg flex items-center gap-2">
                <span>STUCK PALLETS</span>
                <Badge variant="secondary" className="bg-orange-100 text-orange-700 dark:bg-orange-900/30 dark:text-orange-300">
                  HIGH
                </Badge>
              </CardTitle>
              <div className="text-right text-sm text-muted-foreground">
                Impact: {mockAnomalyData.stuckPallets.estimatedImpact}
              </div>
            </div>
          </CardHeader>
          <CardContent>
            <div className="grid grid-cols-2 gap-4">
              <div>
                <div className="text-2xl font-bold text-orange-600 dark:text-orange-400">
                  {mockAnomalyData.stuckPallets.count} pallets
                </div>
                <div className="text-sm text-muted-foreground">In aisles</div>
              </div>
              <div className="text-right">
                <div className="text-lg font-semibold">
                  Avg: {mockAnomalyData.stuckPallets.avgHours}h
                </div>
                <div className="text-sm text-muted-foreground">
                  Max: {mockAnomalyData.stuckPallets.maxHours}h
                </div>
              </div>
            </div>
            <Separator className="my-3" />
            <div className="flex items-center justify-between">
              <div className="text-sm text-muted-foreground">
                Areas: {mockAnomalyData.stuckPallets.locations.join(", ")}
              </div>
              <Button size="sm" variant="outline" className="border-orange-200 hover:bg-orange-50 dark:border-orange-800">
                View Details →
              </Button>
            </div>
          </CardContent>
        </Card>

        {/* Overcapacity - Medium */}
        <Card
          className="cursor-pointer hover:shadow-lg transition-shadow border-l-4 border-l-yellow-500"
          onClick={() => onCategoryClick?.('overcapacity')}
        >
          <CardHeader className="pb-4">
            <div className="flex items-center justify-between">
              <CardTitle className="text-lg flex items-center gap-2">
                <span>OVERCAPACITY</span>
                <Badge variant="secondary" className="bg-yellow-100 text-yellow-700 dark:bg-yellow-900/30 dark:text-yellow-300">
                  MEDIUM
                </Badge>
              </CardTitle>
              <div className="text-right text-sm text-muted-foreground">
                Risk: {mockAnomalyData.overcapacity.physicalRisk}
              </div>
            </div>
          </CardHeader>
          <CardContent>
            <div className="grid grid-cols-2 gap-4">
              <div>
                <div className="text-2xl font-bold text-yellow-600 dark:text-yellow-400">
                  {mockAnomalyData.overcapacity.count} locations
                </div>
                <div className="text-sm text-muted-foreground">Over capacity</div>
              </div>
              <div className="text-right">
                <div className="text-lg font-semibold">
                  Avg: {mockAnomalyData.overcapacity.avgPercentage}%
                </div>
                <div className="text-sm text-muted-foreground">
                  Max: {mockAnomalyData.overcapacity.maxPercentage}%
                </div>
              </div>
            </div>
            <Separator className="my-3" />
            <div className="flex items-center justify-between">
              <div className="text-sm text-muted-foreground">
                Areas: {mockAnomalyData.overcapacity.locations[0]}
              </div>
              <Button size="sm" variant="outline" className="border-yellow-200 hover:bg-yellow-50 dark:border-yellow-800">
                View Details →
              </Button>
            </div>
          </CardContent>
        </Card>

        {/* Lot Stragglers - Medium */}
        <Card
          className="cursor-pointer hover:shadow-lg transition-shadow border-l-4 border-l-blue-500"
          onClick={() => onCategoryClick?.('lot-stragglers')}
        >
          <CardHeader className="pb-4">
            <div className="flex items-center justify-between">
              <CardTitle className="text-lg flex items-center gap-2">
                <span>LOT STRAGGLERS</span>
                <Badge variant="secondary" className="bg-blue-100 text-blue-700 dark:bg-blue-900/30 dark:text-blue-300">
                  MEDIUM
                </Badge>
              </CardTitle>
              <div className="text-right text-sm text-muted-foreground">
                Risk: {mockAnomalyData.lotStragglers.completionRisk}
              </div>
            </div>
          </CardHeader>
          <CardContent>
            <div className="grid grid-cols-2 gap-4">
              <div>
                <div className="text-2xl font-bold text-blue-600 dark:text-blue-400">
                  {mockAnomalyData.lotStragglers.count} lots
                </div>
                <div className="text-sm text-muted-foreground">Incomplete</div>
              </div>
              <div className="text-right">
                <div className="text-lg font-semibold">
                  Status: {mockAnomalyData.lotStragglers.status}
                </div>
                <div className="text-sm text-muted-foreground">
                  Various stages
                </div>
              </div>
            </div>
            <Separator className="my-3" />
            <div className="flex items-center justify-between">
              <div className="text-sm text-muted-foreground">
                Areas: {mockAnomalyData.lotStragglers.locations[0]}
              </div>
              <Button size="sm" variant="outline" className="border-blue-200 hover:bg-blue-50 dark:border-blue-800">
                View Details →
              </Button>
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Quick Actions Footer */}
      <Card className="bg-muted/30">
        <CardContent className="py-4">
          <div className="flex items-center justify-between">
            <div className="text-sm text-muted-foreground">
              Total items requiring attention: <span className="font-semibold text-foreground">77</span>
            </div>
            <div className="flex gap-2">
              <Button variant="outline" size="sm">
                Export All Lists
              </Button>
              <Button variant="outline" size="sm">
                Print Work Orders
              </Button>
              <Button size="sm">
                Mark Multiple as Resolved
              </Button>
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  )
}

// Detailed view for a specific category
interface ActionDetailViewProps {
  category: string
  onBack?: () => void
}

export function ActionDetailView({ category, onBack }: ActionDetailViewProps) {
  const [selectedItems, setSelectedItems] = React.useState<string[]>([])

  const handleSelectAll = () => {
    if (selectedItems.length === mockDetailedItems.length) {
      setSelectedItems([])
    } else {
      setSelectedItems(mockDetailedItems.map(item => item.id))
    }
  }

  const handleItemToggle = (itemId: string) => {
    setSelectedItems(prev =>
      prev.includes(itemId)
        ? prev.filter(id => id !== itemId)
        : [...prev, itemId]
    )
  }

  return (
    <div className="max-w-6xl mx-auto p-6 space-y-6">

      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-foreground flex items-center gap-3">
            🎯 {category.replace('-', ' ').toUpperCase()} - {mockDetailedItems.length} ITEMS
          </h1>
          <p className="text-muted-foreground mt-1">
            Detailed list with actions for resolution
          </p>
        </div>
        <Button variant="outline" onClick={onBack}>
          ← Back to Action Hub
        </Button>
      </div>

      {/* Items Table */}
      <Card>
        <CardHeader>
          <div className="flex items-center justify-between">
            <CardTitle>Item Details</CardTitle>
            <div className="flex gap-2">
              <Button
                variant="outline"
                size="sm"
                onClick={handleSelectAll}
              >
                {selectedItems.length === mockDetailedItems.length ? 'Deselect All' : 'Select All'}
              </Button>
              <Button
                size="sm"
                disabled={selectedItems.length === 0}
              >
                Mark {selectedItems.length} as Resolved
              </Button>
            </div>
          </div>
        </CardHeader>
        <CardContent>
          <div className="space-y-3">
            {mockDetailedItems.map((item) => (
              <div
                key={item.id}
                className={cn(
                  "flex items-center gap-4 p-3 rounded-lg border transition-colors",
                  selectedItems.includes(item.id) ? "bg-muted/50 border-primary" : "hover:bg-muted/30"
                )}
              >
                <input
                  type="checkbox"
                  checked={selectedItems.includes(item.id)}
                  onChange={() => handleItemToggle(item.id)}
                  className="rounded"
                />
                <div className="flex-1 grid grid-cols-4 gap-4">
                  <div>
                    <div className="font-semibold flex items-center gap-2">
                      {item.id}
                      {item.priority === 'critical' && (
                        <Badge variant="destructive" className="text-xs">🔴</Badge>
                      )}
                    </div>
                    <div className="text-sm text-muted-foreground">{item.product}</div>
                  </div>
                  <div>
                    <div className="font-medium">{item.location}</div>
                    <div className="text-sm text-muted-foreground">Location</div>
                  </div>
                  <div>
                    <div className="font-medium text-red-600 dark:text-red-400">{item.duration}</div>
                    <div className="text-sm text-muted-foreground">Duration</div>
                  </div>
                  <div className="text-right">
                    <Button size="sm" variant="outline">
                      View Details
                    </Button>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </CardContent>
      </Card>

      {/* Actions Footer */}
      <Card className="bg-muted/30">
        <CardContent className="py-4">
          <div className="flex items-center justify-between">
            <div className="text-sm text-muted-foreground">
              Selected: <span className="font-semibold text-foreground">{selectedItems.length}</span> of {mockDetailedItems.length} items
            </div>
            <div className="flex gap-2">
              <Button variant="outline" size="sm">
                Export List
              </Button>
              <Button variant="outline" size="sm">
                Print Work Order
              </Button>
              <Button
                size="sm"
                disabled={selectedItems.length === 0}
              >
                Mark Selected as Resolved
              </Button>
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  )
}