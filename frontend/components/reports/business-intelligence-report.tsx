"use client"

import { useState, useMemo } from 'react'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Badge } from '@/components/ui/badge'
import { Progress } from '@/components/ui/progress'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs'
import {
  AlertTriangle,
  Zap,
  Target,
  Clipboard,
  TrendingUp,
  Clock,
  DollarSign,
  Users,
  MapPin,
  ChevronRight,
  CheckCircle2,
  ArrowRight,
  BarChart3,
  Filter,
  Eye,
  Workflow,
  Search,
  X,
  Settings,
  Truck,
  Package,
  ShoppingCart,
  Database,
  Building,
  Thermometer,
  RefreshCw,
  XCircle,
  RotateCcw,
  Activity,
  CheckCircle,
  Undo2
} from 'lucide-react'
import { Anomaly, LocationSummary, getPriorityColor } from '@/lib/reports'
import { AnomalyManagementModal } from './anomaly-management-modal'

interface BusinessIntelligenceReportProps {
  locations: LocationSummary[]
  onStatusUpdate?: () => void
  onAnomalyResolved?: (anomalyId: string) => void
  onAnomalyUnresolved?: (anomalyId: string) => void
  resolvedAnomalies?: Set<string>
}

interface BusinessIntelligenceData {
  fixNow: EnrichedAnomaly[]
  fixToday: EnrichedAnomaly[]
  fixThisWeek: EnrichedAnomaly[]
  dataIssues: EnrichedAnomaly[]
  allIssues: EnrichedAnomaly[]
  totalPallets: number
  affectedLocations: number
  possiblePalletsLost: number
  resolutionProgress: number
}

interface EnrichedAnomaly extends Anomaly {
  location: string
  businessImpact: string
  resourceRequirements: string
  // Filter metadata
  urgencyLevel: 'critical' | 'high' | 'medium' | 'low'
  operationalArea: 'receiving' | 'storage' | 'picking' | 'data' | 'infrastructure'
  resourceType: 'single' | 'team' | 'equipment' | 'management' | 'system'
  ruleCategory: string
  estimatedMinutes: number
  isBlocking: boolean
}

// Filter interfaces
interface FilterState {
  searchQuery: string
  urgencyLevels: string[]
  operationalAreas: string[]
  resourceTypes: string[]
  ruleCategories: string[]
  activePreset: string | null
}

interface FilterPreset {
  id: string
  name: string
  description: string
  icon: React.ReactNode
  filters: Partial<FilterState>
}

interface FilterDimension {
  id: string
  name: string
  icon: React.ReactNode
  color: string
  options: FilterOption[]
}

interface FilterOption {
  value: string
  label: string
  count?: number
  description?: string
}

// Filter configuration
const FILTER_PRESETS: FilterPreset[] = [
  {
    id: 'my-shift',
    name: 'My Shift Focus',
    description: 'Items relevant to current operations',
    icon: <Users className="w-4 h-4" />,
    filters: { urgencyLevels: ['critical', 'high'], operationalAreas: ['receiving', 'storage'] }
  },
  {
    id: 'quick-wins',
    name: 'Quick Wins',
    description: 'Fast resolution items',
    icon: <Zap className="w-4 h-4" />,
    filters: { resourceTypes: ['single'], urgencyLevels: ['high', 'medium'] }
  },
  {
    id: 'blocking-flow',
    name: 'Blocking Flow',
    description: 'Operations blocking warehouse flow',
    icon: <AlertTriangle className="w-4 h-4" />,
    filters: { urgencyLevels: ['critical'], operationalAreas: ['receiving', 'picking'] }
  },
  {
    id: 'overcapacity-issues',
    name: 'Overcapacity',
    description: 'Storage capacity problems',
    icon: <Package className="w-4 h-4" />,
    filters: { ruleCategories: ['Storage Overcapacity', 'Special Area Capacity'] }
  },
  {
    id: 'stuck-pallets',
    name: 'Stuck Pallets',
    description: 'Stagnant and blocked pallets',
    icon: <Truck className="w-4 h-4" />,
    filters: { ruleCategories: ['Stagnant Pallet', 'Location-Specific Stagnant', 'Forgotten Pallet Alert'] }
  },
  {
    id: 'data-issues',
    name: 'Data Problems',
    description: 'Location and scanning issues',
    icon: <Database className="w-4 h-4" />,
    filters: { ruleCategories: ['Invalid Location', 'Duplicate Scan', 'Lot Straggler'] }
  }
]

const FILTER_DIMENSIONS: FilterDimension[] = [
  {
    id: 'urgencyLevels',
    name: 'Urgency & Impact',
    icon: <AlertTriangle className="w-4 h-4" />,
    color: 'rose',
    options: [
      { value: 'critical', label: 'Critical Operations', description: '0-15 min impact' },
      { value: 'high', label: 'High Business Impact', description: '1-4 hour impact' },
      { value: 'medium', label: 'Operational Efficiency', description: 'Same day impact' },
      { value: 'low', label: 'Strategic Planning', description: 'This week impact' }
    ]
  },
  {
    id: 'operationalAreas',
    name: 'Operational Context',
    icon: <Workflow className="w-4 h-4" />,
    color: 'blue',
    options: [
      { value: 'receiving', label: 'Receiving Operations', description: 'Inbound flow' },
      { value: 'storage', label: 'Storage Management', description: 'Space optimization' },
      { value: 'picking', label: 'Picking Operations', description: 'Outbound flow' },
      { value: 'data', label: 'Data Integrity', description: 'System accuracy' },
      { value: 'infrastructure', label: 'Infrastructure', description: 'Physical warehouse' }
    ]
  },
  {
    id: 'resourceTypes',
    name: 'Resource Requirements',
    icon: <Users className="w-4 h-4" />,
    color: 'amber',
    options: [
      { value: 'single', label: 'Single Person', description: 'One operator' },
      { value: 'team', label: 'Team Required', description: 'Multiple resources' },
      { value: 'equipment', label: 'Equipment Needed', description: 'Forklift, systems' },
      { value: 'management', label: 'Management Decision', description: 'Supervisor approval' },
      { value: 'system', label: 'System Update', description: 'IT/configuration' }
    ]
  },
  {
    id: 'ruleCategories',
    name: 'Warehouse Rules',
    icon: <Package className="w-4 h-4" />,
    color: 'indigo',
    options: [
      { value: 'Storage Overcapacity', label: 'Overcapacity', description: 'Storage location at capacity' },
      { value: 'Stagnant Pallet', label: 'Stagnant Pallets', description: 'Pallets not moving' },
      { value: 'Location-Specific Stagnant', label: 'AISLE Stuck Pallets', description: 'Pallets blocking aisles' },
      { value: 'Lot Straggler', label: 'Lot Incompletes', description: 'Incomplete lot processing' },
      { value: 'Forgotten Pallet Alert', label: 'Forgotten Pallets', description: 'Pallets left unprocessed' },
      { value: 'Invalid Location', label: 'Location Errors', description: 'Location mapping issues' },
      { value: 'Special Area Capacity', label: 'Special Areas', description: 'Temperature/restricted zones' },
      { value: 'Duplicate Scan', label: 'Data Issues', description: 'Scanning and data problems' },
      { value: 'Temperature Zone Violation', label: 'Temperature Violations', description: 'Wrong temperature zone placement' }
    ]
  }
]

// Business intelligence processing functions
function enrichAnomalyWithBusinessContext(anomaly: Anomaly, location: string): EnrichedAnomaly {
  const enriched: EnrichedAnomaly = {
    ...anomaly,
    location,
    businessImpact: generateBusinessImpact(anomaly),
    resourceRequirements: generateResourceRequirements(anomaly),
    // Filter metadata
    urgencyLevel: generateUrgencyLevel(anomaly),
    operationalArea: generateOperationalArea(anomaly),
    resourceType: generateResourceType(anomaly),
    ruleCategory: anomaly.anomaly_type,
    estimatedMinutes: generateEstimatedMinutes(anomaly),
    isBlocking: generateIsBlocking(anomaly)
  }

  return enriched
}

function generateBusinessImpact(anomaly: Anomaly): string {
  switch (anomaly.anomaly_type) {
    case 'Stagnant Pallet':
      return 'Blocks receiving flow'
    case 'Storage Overcapacity':
      return 'Phantom pallet detected - prevent loss'
    case 'Special Area Capacity':
      return 'Special area overcapacity - investigate mismatch'
    case 'Invalid Location':
      return 'Pallet missing - can\'t locate'
    case 'Location-Specific Stagnant':
      return 'Blocking aisle traffic'
    case 'Duplicate Scan':
      return 'Data error - fix inventory record'
    case 'Lot Straggler':
      return 'Lot incomplete - delays orders'
    case 'Forgotten Pallet Alert':
      return 'Unprocessed - potential loss'
    case 'Temperature Zone Violation':
      return 'Wrong temperature zone - product safety risk'
    default:
      return 'Needs investigation'
  }
}

function generateResourceRequirements(anomaly: Anomaly): string {
  switch (anomaly.anomaly_type) {
    case 'Stagnant Pallet':
    case 'Forgotten Pallet Alert':
      return '👷 Forklift operator needed'
    case 'Storage Overcapacity':
    case 'Special Area Capacity':
      return '👥 Material handling team needed'
    case 'Invalid Location':
      return '📋 Warehouse coordinator needed'
    case 'Location-Specific Stagnant':
      return '👷 Forklift operator needed'
    case 'Duplicate Scan':
      return '💻 Data analyst needed'
    case 'Lot Straggler':
      return '📊 Inventory coordinator needed'
    case 'Temperature Zone Violation':
      return '🌡️ Quality control team needed'
    default:
      return '👥 Operations team needed'
  }
}

function generateEstimatedDuration(anomaly: Anomaly): string {
  switch (anomaly.anomaly_type) {
    case 'Duplicate Scan':
      return '⏱️ 5-10 min'
    case 'Invalid Location':
      return '⏱️ 10-15 min'
    case 'Stagnant Pallet':
      return '⏱️ 15-20 min'
    case 'Location-Specific Stagnant':
      return '⏱️ 20-30 min'
    case 'Storage Overcapacity':
    case 'Special Area Capacity':
      return '⏱️ 30-45 min'
    case 'Temperature Zone Violation':
      return '⏱️ 20-30 min'
    default:
      return '⏱️ 15-30 min'
  }
}

function generateDependencies(anomaly: Anomaly, location: string): string[] {
  const dependencies: string[] = []

  if (anomaly.anomaly_type === 'Storage Overcapacity') {
    dependencies.push('Clear receiving backlog first')
    dependencies.push('Ensure destination locations available')
  }

  if (location.includes('RECV') || location.includes('RECEIVING')) {
    dependencies.push('May affect inbound operations')
  }

  if (anomaly.priority === 'VERY HIGH' || anomaly.priority === 'HIGH') {
    dependencies.push('Coordinate with operations supervisor')
  }

  return dependencies
}

function generateOperationalContext(anomaly: Anomaly, location: string): string {
  if (location.includes('RECV') || location.includes('RECEIVING')) {
    return 'Receiving Area - impacts inbound processing capability'
  }

  if (location.match(/^\d+\./)) {
    return `Storage Area - affects picking and put-away operations`
  }

  if (location.includes('AISLE')) {
    return 'Transit Area - may cause traffic congestion'
  }

  return 'General warehouse area - monitor for operational impact'
}

function generateUrgencyReason(anomaly: Anomaly): string {
  switch (anomaly.priority) {
    case 'VERY HIGH':
      return 'Critical business impact - immediate resolution required'
    case 'HIGH':
      return 'Significant operational impact - prioritize resolution'
    case 'MEDIUM':
      return 'Moderate impact - schedule resolution today'
    case 'LOW':
      return 'Minor impact - address during routine maintenance'
    default:
      return 'Review and assess impact'
  }
}

// Filter metadata generation functions
function generateUrgencyLevel(anomaly: Anomaly): 'critical' | 'high' | 'medium' | 'low' {
  switch (anomaly.priority) {
    case 'VERY HIGH':
      return 'critical'
    case 'HIGH':
      return 'high'
    case 'MEDIUM':
      return 'medium'
    case 'LOW':
    default:
      return 'low'
  }
}

function generateOperationalArea(anomaly: Anomaly): 'receiving' | 'storage' | 'picking' | 'data' | 'infrastructure' {
  switch (anomaly.anomaly_type) {
    case 'Stagnant Pallet':
    case 'Forgotten Pallet Alert':
      return 'receiving'
    case 'Storage Overcapacity':
    case 'Special Area Capacity':
      return 'storage'
    case 'Location-Specific Stagnant':
      return 'picking'
    case 'Duplicate Scan':
    case 'Invalid Location':
    case 'Lot Straggler':
      return 'data'
    case 'Temperature Zone Violation':
      return 'storage'
    default:
      return 'infrastructure'
  }
}

function generateResourceType(anomaly: Anomaly): 'single' | 'team' | 'equipment' | 'management' | 'system' {
  switch (anomaly.anomaly_type) {
    case 'Duplicate Scan':
    case 'Invalid Location':
    case 'Lot Straggler':
      return 'single'
    case 'Stagnant Pallet':
    case 'Forgotten Pallet Alert':
      return 'equipment'
    case 'Storage Overcapacity':
    case 'Special Area Capacity':
      return 'team'
    case 'Location-Specific Stagnant':
      return anomaly.priority === 'VERY HIGH' ? 'management' : 'team'
    case 'Temperature Zone Violation':
      return 'team'
    default:
      return 'system'
  }
}

function generateEstimatedMinutes(anomaly: Anomaly): number {
  switch (anomaly.anomaly_type) {
    case 'Duplicate Scan':
      return 5
    case 'Invalid Location':
    case 'Lot Straggler':
      return 10
    case 'Stagnant Pallet':
    case 'Forgotten Pallet Alert':
      return 15
    case 'Location-Specific Stagnant':
      return 30
    case 'Storage Overcapacity':
    case 'Special Area Capacity':
      return 45
    case 'Temperature Zone Violation':
      return 25
    default:
      return 20
  }
}

function generateIsBlocking(anomaly: Anomaly): boolean {
  return (
    anomaly.priority === 'VERY HIGH' ||
    (anomaly.anomaly_type === 'Stagnant Pallet' && anomaly.priority === 'HIGH') ||
    anomaly.anomaly_type === 'Special Area Capacity'
  )
}

function processBusinessIntelligence(locations: LocationSummary[]): BusinessIntelligenceData {
  const allAnomalies = locations.flatMap(location =>
    location.anomalies.map(anomaly => enrichAnomalyWithBusinessContext(anomaly, location.name))
  )

  // Debug: Check what anomalies we have
  console.log(`[FRONTEND_DEBUG] Total locations: ${locations.length}`)
  console.log(`[FRONTEND_DEBUG] Total anomalies: ${allAnomalies.length}`)

  const overcapacityAnomalies = allAnomalies.filter(a =>
    a.anomaly_type === 'Storage Overcapacity' || a.anomaly_type === 'Special Area Capacity'
  )
  console.log(`[FRONTEND_DEBUG] Overcapacity anomalies found: ${overcapacityAnomalies.length}`)
  console.log(`[FRONTEND_DEBUG] Overcapacity breakdown:`,
    overcapacityAnomalies.reduce((acc, a) => {
      acc[a.anomaly_type] = (acc[a.anomaly_type] || 0) + 1
      return acc
    }, {} as Record<string, number>)
  )

  // Categorize by urgency and action timeline (operator-friendly)
  const fixNow: EnrichedAnomaly[] = []
  const fixToday: EnrichedAnomaly[] = []
  const fixThisWeek: EnrichedAnomaly[] = []
  const dataIssues: EnrichedAnomaly[] = []

  allAnomalies.forEach(anomaly => {
    // Skip already resolved items
    if (anomaly.status === 'Resolved') return

    // FIX NOW: Operations are blocked right now
    if (
      (anomaly.anomaly_type === 'Stagnant Pallet' && anomaly.location.includes('RECV')) ||
      (anomaly.anomaly_type === 'Special Area Capacity') ||
      (anomaly.priority === 'VERY HIGH' && anomaly.anomaly_type === 'Storage Overcapacity') ||
      (anomaly.anomaly_type === 'Invalid Location' && anomaly.priority === 'VERY HIGH')
    ) {
      fixNow.push(anomaly)
    }
    // DATA ISSUES: System/scanning problems (quick fixes)
    else if (
      anomaly.anomaly_type === 'Duplicate Scan' ||
      anomaly.anomaly_type === 'Invalid Location' ||
      anomaly.anomaly_type === 'Lot Straggler'
    ) {
      dataIssues.push(anomaly)
    }
    // FIX TODAY: Affecting efficiency, need same-day resolution
    else if (
      (anomaly.anomaly_type === 'Stagnant Pallet') ||
      (anomaly.anomaly_type === 'Storage Overcapacity' && anomaly.priority === 'HIGH') ||
      (anomaly.anomaly_type === 'Location-Specific Stagnant' && anomaly.priority === 'HIGH')
    ) {
      fixToday.push(anomaly)
    }
    // FIX THIS WEEK: Important but not urgent
    else {
      fixThisWeek.push(anomaly)
    }
  })

  // Calculate realistic warehouse metrics
  const totalPallets = calculateTotalPalletsAffected(allAnomalies)

  // Enhanced Affected Locations: categorize by operational impact
  const affectedLocations = calculateAffectedLocations(allAnomalies)

  // Calculate possible pallets lost from overcapacity situations
  const possiblePalletsLost = calculatePossiblePalletsLost(allAnomalies)

  // Enhanced Resolution Progress: weighted by business impact and time sensitivity
  const resolutionProgress = calculateWeightedResolutionProgress(allAnomalies)

  return {
    fixNow,
    fixToday,
    fixThisWeek,
    dataIssues,
    allIssues: allAnomalies,
    totalPallets,
    affectedLocations,
    possiblePalletsLost,
    resolutionProgress
  }
}

// Realistic warehouse metrics that operators can trust and verify
function calculateTotalPalletsAffected(anomalies: EnrichedAnomaly[]): number {
  // Count total anomalies (each anomaly represents at least 1 pallet affected)
  // Don't skip resolved items - they were still part of the analysis
  let totalAnomalies = anomalies.length

  // For debugging: log the count to verify against backend
  console.log(`[FRONTEND_DEBUG] Total anomalies in frontend: ${totalAnomalies}`)
  console.log(`[FRONTEND_DEBUG] Anomaly types breakdown:`,
    anomalies.reduce((acc, a) => {
      acc[a.anomaly_type] = (acc[a.anomaly_type] || 0) + 1
      return acc
    }, {} as Record<string, number>)
  )

  return totalAnomalies
}

function calculatePossiblePalletsLost(anomalies: EnrichedAnomaly[]): number {
  let possiblePalletsLost = 0
  let overcapacityCount = 0

  anomalies.forEach(anomaly => {
    // Focus ONLY on overcapacity anomalies (as per user request)
    if (anomaly.anomaly_type === 'Storage Overcapacity' ||
        anomaly.anomaly_type === 'Special Area Capacity') {

      overcapacityCount++

      // Use the actual excess_pallets field from the backend calculation
      if (anomaly.excess_pallets !== undefined) {
        possiblePalletsLost += anomaly.excess_pallets
        console.log(`[OVERCAPACITY_DEBUG] ${anomaly.anomaly_type} at ${anomaly.location}: +${anomaly.excess_pallets} excess pallets`)
      }
      // Fallback: parse from details string
      else {
        const overLimitMatch = anomaly.details?.match(/\+(\d+)\s+over limit/)
        if (overLimitMatch) {
          const excess = parseInt(overLimitMatch[1])
          possiblePalletsLost += excess
          console.log(`[OVERCAPACITY_DEBUG] ${anomaly.anomaly_type} at ${anomaly.location}: +${excess} excess pallets (parsed)`)
        } else {
          // Last resort: extract capacity difference
          const capacityMatch = anomaly.details?.match(/(\d+)\/(\d+)\s+pallets/)
          if (capacityMatch) {
            const current = parseInt(capacityMatch[1])
            const capacity = parseInt(capacityMatch[2])
            const excess = Math.max(0, current - capacity)
            possiblePalletsLost += excess
            console.log(`[OVERCAPACITY_DEBUG] ${anomaly.anomaly_type} at ${anomaly.location}: ${current}/${capacity} = +${excess} excess pallets`)
          }
        }
      }
    }
  })

  console.log(`[OVERCAPACITY_DEBUG] Total overcapacity anomalies found: ${overcapacityCount}`)
  console.log(`[OVERCAPACITY_DEBUG] Total possible pallets lost: ${possiblePalletsLost}`)
  console.log(`[OVERCAPACITY_DEBUG] Expected from backend: Storage Overcapacity: 48 + Special Area Capacity: 3 = 51 total`)

  return possiblePalletsLost
}

// Helper function to extract pallet count from anomaly details
function extractPalletCount(details: string): number {
  const palletMatch = details.match(/(\d+)\s*pallet/i)
  if (palletMatch) {
    return parseInt(palletMatch[1])
  }
  return 1 // Default to 1 pallet if not specified
}

// Helper function to extract time multiplier for stagnant pallets
function extractTimeMultiplier(details: string): number {
  const timeMatch = details.match(/(\d+\.?\d*)\s*h/i)
  if (timeMatch) {
    const hours = parseFloat(timeMatch[1])
    // Escalate cost: >8h = 1.5x, >24h = 2x, >48h = 3x
    if (hours > 48) return 3.0
    if (hours > 24) return 2.0
    if (hours > 8) return 1.5
  }
  return 1.0 // Default multiplier
}

// Helper function to extract capacity ratio from anomaly details
function extractCapacityRatioFromDetails(details: string): number {
  const match = details.match(/(\d+) pallets \(capacity: (\d+)\)/)
  if (match) {
    const pallets = parseInt(match[1])
    const capacity = parseInt(match[2])
    return capacity > 0 ? pallets / capacity : 1
  }
  return 1 // Default ratio if not found
}

// Enhanced calculation functions for business metrics
function calculateAffectedLocations(anomalies: EnrichedAnomaly[]): number {
  const locationTypes = new Set<string>()

  anomalies.forEach(anomaly => {
    if (anomaly.status === 'Resolved') return // Skip resolved

    const location = anomaly.location

    // Categorize locations by operational significance
    if (location.includes('RECV')) {
      locationTypes.add('RECEIVING_AREA')
    } else if (location.match(/^\d+\./)) {
      locationTypes.add('STORAGE_ZONE')
    } else if (location.includes('AISLE')) {
      locationTypes.add('TRANSIT_CORRIDOR')
    } else if (location.includes('TEMP') || location.includes('COLD') || location.includes('FREEZER')) {
      locationTypes.add('SPECIAL_ENVIRONMENT')
    } else if (location.includes('PICK') || location.includes('STAGE')) {
      locationTypes.add('FULFILLMENT_AREA')
    } else {
      locationTypes.add('GENERAL_STORAGE')
    }
  })

  // Count unique operational areas affected, not just location names
  // This gives a better sense of warehouse-wide impact
  return locationTypes.size
}


function calculateWeightedResolutionProgress(anomalies: EnrichedAnomaly[]): number {
  if (anomalies.length === 0) return 100

  let totalWeight = 0
  let resolvedWeight = 0

  anomalies.forEach(anomaly => {
    // Calculate weight based on business impact and urgency
    let weight = 1

    // Priority weighting
    switch (anomaly.priority) {
      case 'VERY HIGH': weight *= 4; break
      case 'HIGH': weight *= 2.5; break
      case 'MEDIUM': weight *= 1.5; break
      case 'LOW': weight *= 1; break
    }

    // Anomaly type weighting (operational impact)
    switch (anomaly.anomaly_type) {
      case 'Stagnant Pallet':
        weight *= anomaly.location.includes('RECV') ? 3 : 1.5
        break
      case 'Storage Overcapacity':
      case 'Special Area Capacity':
        weight *= 2.5
        break
      case 'Invalid Location':
        weight *= 2
        break
      case 'Location-Specific Stagnant':
        weight *= 1.8
        break
      case 'Duplicate Scan':
        weight *= 1.2
        break
      case 'Temperature Zone Violation':
        weight *= 2.2
        break
      default:
        weight *= 1
    }

    // Time sensitivity weighting (longer issues are more important to resolve)
    const timeMultiplier = extractTimeMultiplier(anomaly.details || '')
    weight *= timeMultiplier

    totalWeight += weight

    if (anomaly.status === 'Resolved' || anomaly.status === 'Acknowledged') {
      resolvedWeight += weight
    }
  })

  return totalWeight > 0 ? Math.round((resolvedWeight / totalWeight) * 100) : 0
}

// Filter functions
function filterAnomalies(anomalies: EnrichedAnomaly[], filters: FilterState): EnrichedAnomaly[] {
  const filtered = anomalies.filter((anomaly) => {
    // Search query filter
    if (filters.searchQuery) {
      const searchLower = filters.searchQuery.toLowerCase()
      const searchMatch =
        anomaly.location.toLowerCase().includes(searchLower) ||
        anomaly.anomaly_type.toLowerCase().includes(searchLower) ||
        anomaly.businessImpact.toLowerCase().includes(searchLower) ||
        anomaly.resourceRequirements.toLowerCase().includes(searchLower) ||
        (anomaly.details && anomaly.details.toLowerCase().includes(searchLower))

      if (!searchMatch) return false
    }

    // Urgency levels filter
    if (filters.urgencyLevels.length > 0 && !filters.urgencyLevels.includes(anomaly.urgencyLevel)) {
      return false
    }

    // Operational areas filter
    if (filters.operationalAreas.length > 0 && !filters.operationalAreas.includes(anomaly.operationalArea)) {
      return false
    }

    // Resource types filter
    if (filters.resourceTypes.length > 0 && !filters.resourceTypes.includes(anomaly.resourceType)) {
      return false
    }

    // Rule categories filter
    if (filters.ruleCategories.length > 0 && !filters.ruleCategories.includes(anomaly.ruleCategory)) {
      return false
    }

    return true
  })

  return filtered
}

// FilterBar component
function FilterBar({
  filters,
  onFiltersChange,
  totalCount,
  filteredCount
}: {
  filters: FilterState
  onFiltersChange: (filters: FilterState) => void
  totalCount: number
  filteredCount: number
}) {
  const [showAdvanced, setShowAdvanced] = useState(false)

  const applyPreset = (preset: FilterPreset) => {
    // If this preset is already active, deactivate it (clear filters)
    if (filters.activePreset === preset.id) {
      onFiltersChange({
        searchQuery: '',
        urgencyLevels: [],
        operationalAreas: [],
        resourceTypes: [],
        ruleCategories: [],
        activePreset: null
      })
    } else {
      // Clear everything and apply only this preset (single preset mode)
      onFiltersChange({
        searchQuery: '',
        urgencyLevels: [],
        operationalAreas: [],
        resourceTypes: [],
        ruleCategories: [],
        ...preset.filters,
        activePreset: preset.id
      })
    }
  }

  const clearFilters = () => {
    onFiltersChange({
      searchQuery: '',
      urgencyLevels: [],
      operationalAreas: [],
      resourceTypes: [],
      ruleCategories: [],
      activePreset: null
    })
  }

  const toggleFilter = (dimension: keyof FilterState, value: string) => {
    if (Array.isArray(filters[dimension])) {
      const currentValues = filters[dimension] as string[]
      const isActive = currentValues.includes(value)
      const newValues = isActive
        ? currentValues.filter(v => v !== value)
        : [...currentValues, value]

      onFiltersChange({
        ...filters,
        [dimension]: newValues,
        activePreset: null
      })
    }
  }

  const hasActiveFilters = filters.searchQuery ||
    filters.urgencyLevels.length > 0 ||
    filters.operationalAreas.length > 0 ||
    filters.resourceTypes.length > 0 ||
    filters.ruleCategories.length > 0

  return (
    <div className="space-y-4 mb-6">
      {/* Search and Quick Actions */}
      <div className="flex flex-col sm:flex-row gap-4">
        {/* Search Bar */}
        <div className="relative flex-1">
          <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 w-4 h-4 text-gray-400" />
          <input
            type="text"
            placeholder="Search anomalies, locations, pallets..."
            value={filters.searchQuery}
            onChange={(e) => onFiltersChange({ ...filters, searchQuery: e.target.value, activePreset: null })}
            className="w-full pl-10 pr-4 py-2 border border-gray-200 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
          />
        </div>

        {/* Advanced Toggle */}
        <Button
          variant="outline"
          onClick={() => setShowAdvanced(!showAdvanced)}
          className="flex items-center gap-2"
        >
          <Filter className="w-4 h-4" />
          Filters
          {hasActiveFilters && (
            <Badge variant="secondary" className="ml-1 px-1.5 py-0.5 text-xs">
              {[filters.urgencyLevels.length, filters.operationalAreas.length, filters.resourceTypes.length, filters.ruleCategories.length].reduce((a, b) => a + b, 0) + (filters.searchQuery ? 1 : 0)}
            </Badge>
          )}
        </Button>
      </div>

      {/* Quick Filter Presets */}
      <div className="space-y-2">
        <div className="text-xs font-medium text-gray-600">Quick Filters:</div>
        <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-6 gap-2">
          {FILTER_PRESETS.map((preset) => (
            <Button
              key={preset.id}
              variant={filters.activePreset === preset.id ? "default" : "outline"}
              size="sm"
              onClick={() => applyPreset(preset)}
              className="flex items-center gap-2 text-xs"
              title={preset.description}
            >
              {preset.icon}
              {preset.name}
            </Button>
          ))}
        </div>
        {hasActiveFilters && (
          <div className="flex justify-end">
            <Button
              variant="ghost"
              size="sm"
              onClick={clearFilters}
              className="text-gray-500 hover:text-gray-700 text-xs"
            >
              <X className="w-3 h-3 mr-1" />
              Clear All Filters
            </Button>
          </div>
        )}
      </div>

      {/* Advanced Filters */}
      {showAdvanced && (
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4 p-4 bg-gray-50 rounded-lg">
          {FILTER_DIMENSIONS.map((dimension) => (
            <div key={dimension.id} className="space-y-2">
              <div className="flex items-center gap-2 text-sm font-medium text-gray-700">
                {dimension.icon}
                {dimension.name}
              </div>
              <div className="flex flex-wrap gap-1">
                {dimension.options.map((option) => {
                  const isActive = (filters[dimension.id as keyof FilterState] as string[])?.includes(option.value)
                  return (
                    <button
                      key={option.value}
                      onClick={() => toggleFilter(dimension.id as keyof FilterState, option.value)}
                      className={`px-2 py-1 text-xs rounded-md transition-colors ${
                        isActive
                          ? dimension.color === 'rose' ? 'bg-rose-500 text-white' :
                            dimension.color === 'blue' ? 'bg-blue-500 text-white' :
                            dimension.color === 'amber' ? 'bg-amber-500 text-white' :
                            dimension.color === 'indigo' ? 'bg-indigo-500 text-white' :
                            'bg-gray-500 text-white'
                          : dimension.color === 'rose' ? 'bg-white border border-gray-200 text-gray-600 hover:bg-rose-50' :
                            dimension.color === 'blue' ? 'bg-white border border-gray-200 text-gray-600 hover:bg-blue-50' :
                            dimension.color === 'amber' ? 'bg-white border border-gray-200 text-gray-600 hover:bg-amber-50' :
                            dimension.color === 'indigo' ? 'bg-white border border-gray-200 text-gray-600 hover:bg-indigo-50' :
                            'bg-white border border-gray-200 text-gray-600 hover:bg-gray-50'
                      }`}
                    >
                      {option.label}
                    </button>
                  )
                })}
              </div>
            </div>
          ))}
        </div>
      )}

      {/* Results Summary */}
      {(hasActiveFilters || filteredCount !== totalCount) && (
        <div className="flex items-center justify-between text-sm text-gray-600 bg-blue-50 px-4 py-2 rounded-lg">
          <span>
            Showing <strong>{filteredCount}</strong> of <strong>{totalCount}</strong> anomalies
          </span>
          {filteredCount !== totalCount && (
            <span className="text-blue-600">
              Filters applied
            </span>
          )}
        </div>
      )}
    </div>
  )
}

export function BusinessIntelligenceReport({ locations, onStatusUpdate, onAnomalyResolved, onAnomalyUnresolved, resolvedAnomalies = new Set() }: BusinessIntelligenceReportProps) {
  const [selectedCategory, setSelectedCategory] = useState<'fixNow' | 'dataIssues' | 'fixToday' | 'fixThisWeek' | 'allIssues' | null>('fixNow')
  const [selectedAnomaly, setSelectedAnomaly] = useState<EnrichedAnomaly | null>(null)
  const [viewMode, setViewMode] = useState<'business' | 'location' | 'resource'>('business')
  const [isManageModalOpen, setIsManageModalOpen] = useState(false)
  const [managingAnomaly, setManagingAnomaly] = useState<EnrichedAnomaly | null>(null)
  // Resolve/Undo functions
  const handleMarkResolved = (anomalyId: string) => {
    // Direct immediate update - no delay needed!
    if (onAnomalyResolved) onAnomalyResolved(anomalyId)
  }

  const handleUndoResolve = (anomalyId: string) => {
    // DON'T call onStatusUpdate() here as it clears resolved anomalies!
    if (onAnomalyUnresolved) onAnomalyUnresolved(anomalyId)
  }

  const isResolved = (anomalyId: string) => resolvedAnomalies.has(anomalyId)

  // Filter state
  const [filters, setFilters] = useState<FilterState>({
    searchQuery: '',
    urgencyLevels: [],
    operationalAreas: [],
    resourceTypes: [],
    ruleCategories: [],
    activePreset: null
  })

  const businessData = useMemo(() => processBusinessIntelligence(locations), [locations])

  // Calculate updated resolution progress including locally resolved anomalies
  const updatedResolutionProgress = useMemo(() => {
    if (businessData.allIssues.length === 0) return 100

    let totalWeight = 0
    let resolvedWeight = 0

    businessData.allIssues.forEach(anomaly => {
      // Calculate weight based on business impact and urgency
      let weight = 1

      // Priority weighting
      switch (anomaly.priority) {
        case 'VERY HIGH': weight *= 4; break
        case 'HIGH': weight *= 2.5; break
        case 'MEDIUM': weight *= 1.5; break
        case 'LOW': weight *= 1; break
      }

      // Anomaly type weighting (operational impact)
      switch (anomaly.anomaly_type) {
        case 'Stagnant Pallet':
          weight *= anomaly.location.includes('RECV') ? 3 : 1.5
          break
        case 'Storage Overcapacity':
        case 'Special Area Capacity':
          weight *= 2.5
          break
        case 'Invalid Location':
          weight *= 2
          break
        case 'Location-Specific Stagnant':
          weight *= 1.8
          break
        case 'Duplicate Scan':
          weight *= 1.2
          break
        case 'Temperature Zone Violation':
          weight *= 2.2
          break
        default:
          weight *= 1
      }

      // Time sensitivity weighting (longer issues are more important to resolve)
      const timeMultiplier = extractTimeMultiplier(anomaly.details || '')
      weight *= timeMultiplier

      totalWeight += weight

      // Check if resolved locally OR already resolved in backend
      if (anomaly.status === 'Resolved' || anomaly.status === 'Acknowledged' || isResolved(anomaly.id.toString())) {
        resolvedWeight += weight
      }
    })

    return totalWeight > 0 ? Math.round((resolvedWeight / totalWeight) * 100) : 0
  }, [businessData.allIssues, resolvedAnomalies])

  // Apply filters to the current category
  const filteredAnomalies = useMemo(() => {
    // If no category is selected, show all issues
    const categoryAnomalies = selectedCategory === null
      ? businessData.allIssues
      : businessData[selectedCategory] || businessData.allIssues

    console.log(`[CATEGORY_FILTER] Selected category: ${selectedCategory}`)
    console.log(`[CATEGORY_FILTER] Anomalies in category: ${categoryAnomalies?.length || 0}`)

    return filterAnomalies(categoryAnomalies || [], filters)
  }, [businessData, selectedCategory, filters])

  const getCategoryIcon = (category: string) => {
    switch (category) {
      case 'fixNow': return <AlertTriangle className="w-5 h-5" />
      case 'dataIssues': return <Database className="w-5 h-5" />
      case 'fixToday': return <Clock className="w-5 h-5" />
      case 'fixThisWeek': return <Target className="w-5 h-5" />
      case 'allIssues': return <BarChart3 className="w-5 h-5" />
      default: return <BarChart3 className="w-5 h-5" />
    }
  }

  const getAnomalyIcon = (anomalyType: string) => {
    switch (anomalyType) {
      case 'Stagnant Pallet': return <Activity className="w-5 h-5" />
      case 'Storage Overcapacity': return <Package className="w-5 h-5" />
      case 'Special Area Capacity': return <Building className="w-5 h-5" />
      case 'Invalid Location': return <XCircle className="w-5 h-5" />
      case 'Location-Specific Stagnant': return <Truck className="w-5 h-5" />
      case 'Duplicate Scan': return <RefreshCw className="w-5 h-5" />
      case 'Lot Straggler': return <BarChart3 className="w-5 h-5" />
      case 'Forgotten Pallet Alert': return <AlertTriangle className="w-5 h-5" />
      case 'Temperature Zone Violation': return <Thermometer className="w-5 h-5" />
      default: return <Package className="w-5 h-5" />
    }
  }

  const getAnomalyIconColor = (anomalyType: string) => {
    switch (anomalyType) {
      case 'Stagnant Pallet': return { bg: 'bg-orange-500/10 border border-orange-200/30', text: 'text-orange-600' }
      case 'Storage Overcapacity': return { bg: 'bg-red-500/10 border border-red-200/30', text: 'text-red-600' }
      case 'Special Area Capacity': return { bg: 'bg-purple-500/10 border border-purple-200/30', text: 'text-purple-600' }
      case 'Invalid Location': return { bg: 'bg-rose-500/10 border border-rose-200/30', text: 'text-rose-600' }
      case 'Location-Specific Stagnant': return { bg: 'bg-amber-500/10 border border-amber-200/30', text: 'text-amber-600' }
      case 'Duplicate Scan': return { bg: 'bg-blue-500/10 border border-blue-200/30', text: 'text-blue-600' }
      case 'Lot Straggler': return { bg: 'bg-indigo-500/10 border border-indigo-200/30', text: 'text-indigo-600' }
      case 'Forgotten Pallet Alert': return { bg: 'bg-yellow-500/10 border border-yellow-200/30', text: 'text-yellow-600' }
      case 'Temperature Zone Violation': return { bg: 'bg-cyan-500/10 border border-cyan-200/30', text: 'text-cyan-600' }
      default: return { bg: 'bg-gray-500/10 border border-gray-200/30', text: 'text-gray-600' }
    }
  }

  const getCategoryColor = (category: string) => {
    switch (category) {
      case 'fixNow': return 'from-rose-500 to-rose-600'
      case 'dataIssues': return 'from-blue-500 to-blue-600'
      case 'fixToday': return 'from-amber-500 to-amber-600'
      case 'fixThisWeek': return 'from-slate-500 to-slate-600'
      case 'allIssues': return 'from-purple-500 to-purple-600'
      default: return 'from-gray-500 to-gray-600'
    }
  }

  return (
    <div className="space-y-6">
      {/* Executive Summary Dashboard */}
      <Card className="relative overflow-hidden bg-gradient-to-r from-slate-50 to-gray-50 border-slate-200/60">
        <div className="absolute inset-0 bg-gradient-to-r from-slate-500/3 to-transparent" />
        <CardHeader className="relative">
          <CardTitle className="flex items-center gap-3">
            <div className="flex h-10 w-10 items-center justify-center rounded-full bg-slate-500/10">
              <TrendingUp className="w-5 h-5" />
            </div>
            Business Intelligence Summary
          </CardTitle>
        </CardHeader>
        <CardContent className="relative space-y-6">
          {/* Key Metrics */}
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
            <div className="text-center p-4 bg-white/50 rounded-xl border border-slate-200/50">
              <Package className="w-6 h-6 mx-auto mb-2 text-amber-600" />
              <div className="text-2xl font-bold text-gray-900">{businessData.totalPallets}</div>
              <div className="text-sm text-gray-600">Total Pallets</div>
            </div>
            <div className="text-center p-4 bg-white/50 rounded-xl border border-slate-200/50">
              <MapPin className="w-6 h-6 mx-auto mb-2 text-blue-600" />
              <div className="text-2xl font-bold text-gray-900">{businessData.affectedLocations}</div>
              <div className="text-sm text-gray-600">Affected Areas</div>
            </div>
            <div className="text-center p-4 bg-white/50 rounded-xl border border-slate-200/50">
              <AlertTriangle className="w-6 h-6 mx-auto mb-2 text-rose-600" />
              <div className="text-2xl font-bold text-gray-900">{businessData.possiblePalletsLost}</div>
              <div className="text-sm text-gray-600">Possible Pallets Lost</div>
            </div>
            <div className="text-center p-4 bg-white/50 rounded-xl border border-slate-200/50">
              <CheckCircle2 className="w-6 h-6 mx-auto mb-2 text-emerald-600" />
              <div className="text-2xl font-bold text-gray-900">{updatedResolutionProgress.toFixed(0)}%</div>
              <div className="text-sm text-gray-600">Resolution Progress</div>
            </div>
          </div>

          {/* Progress Bar */}
          <div className="space-y-2">
            <div className="flex justify-between text-sm">
              <span className="font-medium">Overall Resolution Progress</span>
              <span>{updatedResolutionProgress.toFixed(1)}%</span>
            </div>
            <Progress value={updatedResolutionProgress} className="h-2" />
          </div>
        </CardContent>
      </Card>

      {/* Operator-Friendly Workflow Categories */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        {[
          { key: 'fixNow', label: 'Fix Now', count: businessData.fixNow.length, description: 'Operations blocked', urgency: 'critical' },
          { key: 'dataIssues', label: 'Data Issues', count: businessData.dataIssues.length, description: 'System problems', urgency: 'data' },
          { key: 'fixToday', label: 'Fix Today', count: businessData.fixToday.length, description: 'Affecting efficiency', urgency: 'high' },
          { key: 'fixThisWeek', label: 'Fix This Week', count: businessData.fixThisWeek.length, description: 'Important, not urgent', urgency: 'medium' },
          { key: 'allIssues', label: 'All Issues', count: businessData.allIssues.length, description: 'Complete warehouse view', urgency: 'all' }
        ].map((category) => (
          <Card
            key={category.key}
            className={`group cursor-pointer transition-all duration-300 hover:shadow-lg hover:scale-[1.02] ${
              selectedCategory === category.key ? 'ring-2 ring-blue-500 shadow-lg' : ''
            }`}
            onClick={() => {
              // Toggle functionality: if same category is clicked, deselect it
              if (selectedCategory === category.key) {
                console.log(`[CATEGORY_CLICK] Deselecting category: ${category.key}`)
                setSelectedCategory(null)
              } else {
                console.log(`[CATEGORY_CLICK] Switching to category: ${category.key}`)
                setSelectedCategory(category.key as 'fixNow' | 'dataIssues' | 'fixToday' | 'fixThisWeek' | 'allIssues')
              }
            }}
          >
            <CardContent className="p-6">
              <div className="flex items-center gap-3 mb-4">
                <div className={`flex h-12 w-12 items-center justify-center rounded-full bg-gradient-to-r ${getCategoryColor(category.key)} text-white`}>
                  {getCategoryIcon(category.key)}
                </div>
                <div className="flex-1">
                  <div className="text-3xl font-bold text-gray-900">{category.count}</div>
                  <div className="text-sm font-medium text-gray-600">{category.label}</div>
                </div>
              </div>
              <div className="text-xs text-gray-500">{category.description}</div>
              <div className="mt-3 flex items-center text-sm font-medium text-gray-600 group-hover:text-blue-600 transition-colors">
                View Details <ChevronRight className="w-4 h-4 ml-1" />
              </div>
            </CardContent>
          </Card>
        ))}
      </div>

      {/* Detailed Category View */}
      <Card>
        <CardHeader>
          <div className="flex items-center justify-between">
            <CardTitle className="flex items-center gap-3">
              {getCategoryIcon(selectedCategory || 'allIssues')}
              {selectedCategory === 'fixNow' && 'Fix Now - Operations Blocked'}
              {selectedCategory === 'dataIssues' && 'Data Issues - System Problems'}
              {selectedCategory === 'fixToday' && 'Fix Today - Affecting Efficiency'}
              {selectedCategory === 'fixThisWeek' && 'Fix This Week - Important Items'}
              {selectedCategory === 'allIssues' && 'All Issues - Complete Warehouse View'}
              {selectedCategory === null && 'All Issues - Complete Warehouse View'}
            </CardTitle>
            <div className="flex items-center gap-2">
              <Badge variant="outline">{filteredAnomalies.length} items</Badge>
              {(() => {
                const totalInCategory = selectedCategory === null
                  ? businessData.allIssues.length
                  : businessData[selectedCategory]?.length || businessData.allIssues.length
                return filteredAnomalies.length !== totalInCategory && (
                  <Badge variant="secondary" className="text-xs">
                    of {totalInCategory} total
                  </Badge>
                )
              })()}
            </div>
          </div>
        </CardHeader>
        <CardContent>
          {/* Smart Filter Bar */}
          <FilterBar
            filters={filters}
            onFiltersChange={setFilters}
            totalCount={selectedCategory === null ? businessData.allIssues.length : businessData[selectedCategory].length}
            filteredCount={filteredAnomalies.length}
          />

          <div className="space-y-4">
            {filteredAnomalies.length === 0 ? (
              <div className="text-center py-12">
                <Filter className="w-12 h-12 mx-auto text-gray-300 mb-4" />
                <h3 className="text-lg font-medium text-gray-500 mb-2">No items match your filters</h3>
                <p className="text-gray-400 mb-4">Try adjusting your search or filter criteria</p>
                <Button
                  variant="outline"
                  onClick={() => setFilters({
                    searchQuery: '',
                    urgencyLevels: [],
                    operationalAreas: [],
                    resourceTypes: [],
                    ruleCategories: [],
                    activePreset: null
                  })}
                >
                  Clear All Filters
                </Button>
              </div>
            ) : (
              filteredAnomalies.map((anomaly) => {
                const resolved = isResolved(anomaly.id.toString())

                return (
                  <Card
                    key={anomaly.id}
                    className={`group relative overflow-hidden backdrop-blur-sm transition-all duration-300 hover:shadow-lg border rounded-xl cursor-pointer ${
                      resolved
                        ? 'border-emerald-200/60 bg-emerald-50/30'
                        : 'border-gray-200/60 hover:border-blue-200'
                    }`}
                    onClick={() => {
                      if (!resolved) {
                        setManagingAnomaly(anomaly)
                        setIsManageModalOpen(true)
                      }
                    }}
                  >
                    <CardContent className="p-4">
                      <div className="flex items-start gap-2.5">
                        <div className={`flex h-12 w-12 items-center justify-center rounded-full flex-shrink-0 shadow-sm ${
                          resolved
                            ? 'bg-emerald-100 text-emerald-700'
                            : getAnomalyIconColor(anomaly.anomaly_type).bg
                        }`}>
                          <div className={resolved ? 'text-emerald-700' : getAnomalyIconColor(anomaly.anomaly_type).text}>
                            {resolved ? <CheckCircle className="w-6 h-6" /> : getAnomalyIcon(anomaly.anomaly_type)}
                          </div>
                        </div>

                        <div className="flex-1 space-y-1.5">
                          <div className="flex items-start justify-between">
                            <div>
                              <h3 className={`font-semibold text-lg leading-tight ${resolved ? 'text-emerald-800' : 'text-gray-900'}`}>
                                {anomaly.anomaly_type}
                              </h3>
                              <p className={`text-sm leading-tight ${resolved ? 'text-emerald-700' : 'text-gray-600'}`}>
                                <span className={`font-bold ${resolved ? 'text-emerald-800' : 'text-gray-900'}`}>{anomaly.location}</span> • Pallet {anomaly.pallet_id}
                              </p>
                            </div>
                            <div className="flex items-center gap-2">
                              <Badge className={`px-3 py-1 text-sm font-bold ${
                                resolved
                                  ? 'bg-emerald-500 text-white'
                                  : getPriorityColor(anomaly.priority)
                              }`}>
                                {resolved ? 'RESOLVED' : anomaly.priority}
                              </Badge>
                            </div>
                          </div>

                          <div className={`grid md:grid-cols-2 gap-3 text-sm mt-2 ${resolved ? 'opacity-75' : ''}`}>
                            <div>
                              <span className={`font-medium ${resolved ? 'text-emerald-700' : 'text-gray-700'}`}>Business Impact:</span>
                              <p className={`mt-1 ${resolved ? 'text-emerald-600' : 'text-gray-600'}`}>{anomaly.businessImpact}</p>
                            </div>
                            <div>
                              <span className={`font-medium ${resolved ? 'text-emerald-700' : 'text-gray-700'}`}>Resources Needed:</span>
                              <p className={`mt-1 ${resolved ? 'text-emerald-600' : 'text-gray-600'}`}>{anomaly.resourceRequirements}</p>
                            </div>
                          </div>

                          <div className="flex items-center justify-end pt-2.5">
                            <div className="flex gap-2">
                              <Button
                                variant="outline"
                                size="default"
                                onClick={(e) => {
                                  e.stopPropagation()
                                  setManagingAnomaly(anomaly)
                                  setIsManageModalOpen(true)
                                }}
                                className="group-hover:bg-blue-50 group-hover:border-blue-200 transition-all duration-200 px-4 py-2 font-semibold"
                              >
                                <Workflow className="w-4 h-4 mr-2" />
                                Resolution Steps
                              </Button>

                              <Button
                                variant="outline"
                                size="default"
                                onClick={(e) => {
                                  e.stopPropagation()
                                  if (!resolved) {
                                    handleMarkResolved(anomaly.id.toString())
                                  }
                                }}
                                className={`transition-all duration-200 px-4 py-2 ${
                                  resolved
                                    ? "text-emerald-700 border-emerald-300 bg-emerald-50"
                                    : "text-slate-600 border-slate-300 hover:bg-slate-50 hover:border-slate-400 hover:text-slate-700"
                                }`}
                              >
                                <CheckCircle className={`w-4 h-4 mr-2 ${resolved ? 'text-emerald-600' : ''}`} />
                                {resolved ? 'Marked Resolved ✓' : 'Mark Resolved'}
                              </Button>

                              {resolved && (
                                <Button
                                  variant="outline"
                                  size="default"
                                  onClick={(e) => {
                                    e.stopPropagation()
                                    handleUndoResolve(anomaly.id.toString())
                                  }}
                                  className="text-gray-500 border-gray-300 hover:bg-gray-50 hover:border-gray-400 transition-all duration-200 px-3 py-2"
                                >
                                  <Undo2 className="w-4 h-4 mr-1" />
                                  Undo
                                </Button>
                              )}
                            </div>
                          </div>
                        </div>
                      </div>
                    </CardContent>
                  </Card>
                )
              })
            )}
          </div>
        </CardContent>
      </Card>

      {/* Anomaly Management Modal */}
      <AnomalyManagementModal
        isOpen={isManageModalOpen}
        onClose={() => {
          setIsManageModalOpen(false)
          setManagingAnomaly(null)
        }}
        onResolve={(anomalyId) => {
          handleMarkResolved(anomalyId)
        }}
        anomaly={managingAnomaly ? {
          id: managingAnomaly.id.toString(),
          anomaly_type: managingAnomaly.anomaly_type,
          location: managingAnomaly.location,
          priority: managingAnomaly.priority,
          details: managingAnomaly.details || '',
          detectedTime: '2 hours ago' // This would come from actual data
        } : null}
      />
    </div>
  )
}