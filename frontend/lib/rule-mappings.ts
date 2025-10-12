import {
  Clock,
  TrendingDown,
  Package,
  Users,
  Thermometer,
  MapPin,
  AlertTriangle,
  Shield
} from 'lucide-react'

// Mapping from backend anomaly types to Action Center rule categories
export const RULE_TYPE_MAPPING: Record<string, string> = {
  // MVP Rules - Core operational issues
  'Stagnant Pallet': 'forgotten-pallets',
  'Forgotten Pallet Alert': 'forgotten-pallets',

  'Storage Overcapacity': 'overcapacity',
  'Special Area Capacity': 'overcapacity',
  'Overcapacity': 'overcapacity',

  'Location-Specific Stagnant': 'aisle-stuck',
  'AISLE Stuck Pallets': 'aisle-stuck',

  'Uncoordinated Lots': 'incomplete-lots',
  'Lot Straggler': 'incomplete-lots',
  'Incomplete Lots': 'incomplete-lots',

  // Secondary Rules - Quality & Compliance
  'Temperature Zone Violation': 'cold-chain',
  'Temperature Zone Mismatch': 'cold-chain',

  'Invalid Location': 'invalid-locations',

  'Duplicate Scan': 'scanner-errors',
  'Data Integrity Issue': 'scanner-errors',
  'Data Integrity': 'scanner-errors',

  'Location Mapping Error': 'location-mapping',
  'Location Type Mismatch': 'location-mapping'
}

// Reverse mapping for category to anomaly types
export const CATEGORY_TO_TYPES: Record<string, string[]> = {
  'forgotten-pallets': ['Stagnant Pallet', 'Forgotten Pallet Alert'],
  'overcapacity': ['Storage Overcapacity', 'Special Area Capacity', 'Overcapacity'],
  'aisle-stuck': ['Location-Specific Stagnant', 'AISLE Stuck Pallets'],
  'incomplete-lots': ['Uncoordinated Lots', 'Lot Straggler', 'Incomplete Lots'],
  'cold-chain': ['Temperature Zone Violation', 'Temperature Zone Mismatch'],
  'invalid-locations': ['Invalid Location'],
  'scanner-errors': ['Duplicate Scan', 'Data Integrity Issue', 'Data Integrity'],
  'location-mapping': ['Location Mapping Error', 'Location Type Mismatch']
}

// Action Center rule category definitions with real metadata
export const ACTION_CATEGORIES_TEMPLATE = {
  // MVP RULES - Core operational issues that directly impact warehouse flow
  'forgotten-pallets': {
    id: 'forgotten-pallets',
    title: 'Forgotten Pallets Alert',
    description: 'Pallets in receiving areas for >10 hours',
    icon: Clock,
    priority: 'high',
    color: 'text-primary',
    bgColor: 'bg-primary/10',
    borderColor: 'border-primary',
    category: 'MVP',
    ruleType: 'STAGNANT_PALLETS',
    baseFinancialImpact: 25, // $25 per hour per pallet
    urgencyMultiplier: 2.0   // Higher urgency for receiving areas
  },

  'overcapacity': {
    id: 'overcapacity',
    title: 'Overcapacity Alert',
    description: 'Locations exceeding designated capacity',
    icon: TrendingDown,
    priority: 'high',
    color: 'text-primary',
    bgColor: 'bg-primary/10',
    borderColor: 'border-primary',
    category: 'MVP',
    ruleType: 'OVERCAPACITY',
    baseFinancialImpact: 50, // $50 per excess pallet per day
    urgencyMultiplier: 1.5
  },

  'aisle-stuck': {
    id: 'aisle-stuck',
    title: 'AISLE Stuck Pallets',
    description: 'Pallets blocked in aisles for 4+ hours',
    icon: Package,
    priority: 'high',
    color: 'text-primary',
    bgColor: 'bg-primary/10',
    borderColor: 'border-primary',
    category: 'MVP',
    ruleType: 'LOCATION_SPECIFIC_STAGNANT',
    baseFinancialImpact: 30, // $30 per hour (blocks traffic)
    urgencyMultiplier: 1.8
  },

  'incomplete-lots': {
    id: 'incomplete-lots',
    title: 'Incomplete Lots Alert',
    description: 'Stragglers when 80%+ of lot is stored',
    icon: Users,
    priority: 'critical',
    color: 'text-destructive',
    bgColor: 'bg-destructive/10',
    borderColor: 'border-destructive',
    category: 'MVP',
    ruleType: 'UNCOORDINATED_LOTS',
    baseFinancialImpact: 75, // $75 per day (order delays)
    urgencyMultiplier: 2.5
  },

  // SECONDARY RULES - Supporting operational quality and compliance
  'cold-chain': {
    id: 'cold-chain',
    title: 'Cold Chain Violations',
    description: 'Temperature-sensitive products in wrong zones',
    icon: Thermometer,
    priority: 'critical',
    color: 'text-destructive',
    bgColor: 'bg-destructive/10',
    borderColor: 'border-destructive',
    category: 'SECONDARY',
    ruleType: 'TEMPERATURE_ZONE_MISMATCH',
    baseFinancialImpact: 200, // $200 per hour (product loss risk)
    urgencyMultiplier: 3.0
  },

  'invalid-locations': {
    id: 'invalid-locations',
    title: 'Invalid Locations Alert',
    description: 'Pallets in undefined location codes',
    icon: MapPin,
    priority: 'high',
    color: 'text-primary',
    bgColor: 'bg-primary/10',
    borderColor: 'border-primary',
    category: 'SECONDARY',
    ruleType: 'INVALID_LOCATION',
    baseFinancialImpact: 40, // $40 per day (lost pallets)
    urgencyMultiplier: 1.5
  },

  'scanner-errors': {
    id: 'scanner-errors',
    title: 'Scanner Error Detection',
    description: 'Data integrity issues from scanning errors',
    icon: AlertTriangle,
    priority: 'medium',
    color: 'text-warning',
    bgColor: 'bg-warning/10',
    borderColor: 'border-warning',
    category: 'SECONDARY',
    ruleType: 'DATA_INTEGRITY',
    baseFinancialImpact: 15, // $15 per error (time to fix)
    urgencyMultiplier: 1.0
  },

  'location-mapping': {
    id: 'location-mapping',
    title: 'Location Type Mismatches',
    description: 'Inconsistencies in location type mapping',
    icon: Shield,
    priority: 'high',
    color: 'text-primary',
    bgColor: 'bg-primary/10',
    borderColor: 'border-primary',
    category: 'SECONDARY',
    ruleType: 'LOCATION_MAPPING_ERROR',
    baseFinancialImpact: 20, // $20 per day (confusion)
    urgencyMultiplier: 1.2
  }
}

// Helper function to get category ID from anomaly type
export function getCategoryFromAnomalyType(anomalyType: string): string | null {
  return RULE_TYPE_MAPPING[anomalyType] || null
}

// Helper function to check if anomaly belongs to MVP rules
export function isMVPRule(categoryId: string): boolean {
  const category = ACTION_CATEGORIES_TEMPLATE[categoryId as keyof typeof ACTION_CATEGORIES_TEMPLATE]
  return category?.category === 'MVP'
}

// Helper function to get all anomaly types for a category
export function getAnomalyTypesForCategory(categoryId: string): string[] {
  return CATEGORY_TO_TYPES[categoryId] || []
}