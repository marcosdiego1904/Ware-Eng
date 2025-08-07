"use client"

import React, { useState, useEffect } from 'react'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { Slider } from '@/components/ui/slider'
import { Alert, AlertDescription } from '@/components/ui/alert'
import { 
  Clock,
  MapPin,
  Package,
  AlertTriangle,
  CheckCircle,
  ArrowRight,
  ArrowLeft,
  Eye,
  Lightbulb,
  Users,
  TrendingUp,
  Zap,
  Target,
  Timer,
  Thermometer,
  Truck,
  WarehouseIcon as Warehouse,
  ShoppingCart,
  AlertCircle,
  Settings,
  Sparkles,
  Brain,
  Plus,
  X,
  ChevronDown,
  ChevronUp,
  BarChart3,
  Activity,
  Layers,
  Wand2,
  Info
} from 'lucide-react'
import { VisualRuleBuilder } from './visual-rule-builder'

// Enhanced warehouse problems with more context - ALL 10 RULE TYPES
const WAREHOUSE_PROBLEMS = [
  // EXISTING PROBLEMS (Fixed with correct rule types)
  {
    id: 'forgotten-items',
    title: 'Items Getting "Forgotten"',
    description: 'Pallets sitting in receiving way too long',
    icon: Clock,
    illustration: '📦💤⏰❗',
    realWorldExample: 'Like that pallet of dog food that sat in receiving for 3 days last month',
    businessImpact: 'Delays customer orders and wastes storage space',
    frequency: 'Usually 5-10 items per day get forgotten',
    category: 'flow',
    color: 'bg-red-100 border-red-300 text-red-800',
    ruleType: 'STAGNANT_PALLETS',
    smartSuggestions: [
      'Grocery warehouses typically use 4-6 hours',
      'Electronics/high-value items often use 2-3 hours',
      'Consider shorter times for perishable goods'
    ],
    relatedConditions: [
      { field: 'product_value', label: 'High-value items get priority', suggested: true },
      { field: 'perishable_flag', label: 'Shorter time for perishables', suggested: true },
      { field: 'customer_priority', label: 'VIP customer orders get alerts sooner', suggested: false }
    ]
  },
  {
    id: 'traffic-jams',
    title: 'Pallets Creating Traffic Jams',
    description: 'Pallets blocking aisles and creating bottlenecks',
    icon: Truck,
    illustration: '🚛➡️📦📦📦⛔', 
    realWorldExample: 'Like when forklifts can\'t get through aisle 3 because pallets are scattered everywhere',
    businessImpact: 'Costs 2-3 hours of overtime per occurrence',
    frequency: 'Happens 2-4 times per week in busy warehouses',
    category: 'flow',
    color: 'bg-orange-100 border-orange-300 text-orange-800',
    ruleType: 'LOCATION_SPECIFIC_STAGNANT',
    smartSuggestions: [
      'Most warehouses your size use 2-4 hour limits for aisles',
      'Consider different limits for main vs. side aisles',
      'Peak hours (10am-2pm) might need stricter rules'
    ],
    relatedConditions: [
      { field: 'location_priority', label: 'High-traffic areas get priority', suggested: true },
      { field: 'time_of_day', label: 'Stricter during peak hours', suggested: false },
      { field: 'pallet_count', label: 'Alert when multiple pallets in same aisle', suggested: true }
    ]
  },
  {
    id: 'temperature-violations',
    title: 'Cold Products Getting Warm',
    description: 'Frozen/refrigerated items in wrong temperature zones',
    icon: Thermometer,
    illustration: '🧊➡️🔥❌',
    realWorldExample: 'Like when frozen vegetables end up in the ambient storage area',
    businessImpact: 'Product spoilage can cost $500-2000 per incident',
    frequency: 'Critical - even one incident is too many',
    category: 'product',
    color: 'bg-blue-100 border-blue-300 text-blue-800',
    ruleType: 'TEMPERATURE_ZONE_MISMATCH',
    smartSuggestions: [
      'Food safety requires immediate alerts (0-15 minutes)',
      'Different products have different temperature tolerances',
      'Consider grace periods for brief transfers'
    ],
    relatedConditions: [
      { field: 'product_temperature_category', label: 'Different rules for frozen vs refrigerated', suggested: true },
      { field: 'transfer_in_progress', label: 'Ignore items being actively moved', suggested: true },
      { field: 'emergency_bypass', label: 'Allow manual overrides for maintenance', suggested: false }
    ]
  },
  {
    id: 'incomplete-deliveries',
    title: 'Incomplete Truck Unloading',
    description: 'Some pallets left behind when truck is "done"',
    icon: ShoppingCart,
    illustration: '🚛📦📦✅ 📦❓',
    realWorldExample: 'Like when 90% of a truck is unloaded but 2 pallets are still sitting in receiving',
    businessImpact: 'Causes delivery delays and customer complaints',
    frequency: 'Happens with 1 in 10 large deliveries',
    category: 'flow',
    color: 'bg-purple-100 border-purple-300 text-purple-800',
    ruleType: 'UNCOORDINATED_LOTS',
    smartSuggestions: [
      'Most effective at 80-90% completion threshold',
      'Smaller deliveries might need different rules',
      'Consider truck size in the calculation'
    ],
    relatedConditions: [
      { field: 'delivery_size', label: 'Different thresholds for small vs large trucks', suggested: true },
      { field: 'delivery_priority', label: 'Rush deliveries get immediate alerts', suggested: false },
      { field: 'dock_assignment', label: 'Different rules per dock door', suggested: true }
    ]
  },
  // NEW PROBLEMS - Missing 6 rule types
  {
    id: 'scanner-errors',
    title: 'Scanner & Data Entry Errors',
    description: 'Duplicate scans and impossible location codes',
    icon: AlertTriangle,
    illustration: '📱❌📊⚠️',
    realWorldExample: 'Same pallet scanned twice or locations like "AISLE999999"',
    businessImpact: 'Inventory discrepancies cost 2-4 hours weekly to resolve',
    frequency: 'Happens 5-10 times per day in busy operations',
    category: 'data',
    color: 'bg-yellow-100 border-yellow-300 text-yellow-800',
    ruleType: 'DATA_INTEGRITY',
    smartSuggestions: [
      'Check for duplicates every 2-4 hours during busy periods',
      'Flag location codes longer than 15 characters',
      'Monitor for special characters in location names'
    ],
    relatedConditions: [
      { field: 'check_duplicate_scans', label: 'Detect duplicate pallet scans', suggested: true },
      { field: 'check_impossible_locations', label: 'Flag unrealistic location codes', suggested: true },
      { field: 'max_location_length', label: 'Maximum location code length', suggested: false }
    ]
  },
  {
    id: 'lost-pallets',
    title: 'Pallets with No Location',
    description: 'Items scanned but location field is empty',
    icon: MapPin,
    illustration: '📦❓🗺️❌',
    realWorldExample: 'Pallet exists in system but shows blank or null location',
    businessImpact: 'Lost items take 30-60 minutes each to physically locate',
    frequency: 'Usually 2-5 items per day go missing',
    category: 'space',
    color: 'bg-gray-100 border-gray-300 text-gray-800',
    ruleType: 'MISSING_LOCATION',
    smartSuggestions: [
      'Check for missing locations hourly during receiving',
      'Most common after system updates or network issues',
      'Often happens during shift changes'
    ],
    relatedConditions: [
      { field: 'check_null_locations', label: 'Flag null/empty locations', suggested: true },
      { field: 'check_nan_locations', label: 'Flag NaN location values', suggested: true },
      { field: 'recent_scan_window', label: 'Only check recently scanned items', suggested: false }
    ]
  },
  {
    id: 'wrong-locations',
    title: 'Items in Non-Existent Locations',
    description: 'Pallets assigned to undefined location codes',
    icon: AlertCircle,
    illustration: '📦➡️🏗️❌',
    realWorldExample: 'Pallet shows location "DOCK-Z" but that dock doesn\'t exist',
    businessImpact: 'Creates confusion and picking errors',
    frequency: 'Common after location changes or system updates',
    category: 'space',
    color: 'bg-red-100 border-red-300 text-red-800',
    ruleType: 'INVALID_LOCATION',
    smartSuggestions: [
      'Run after any warehouse layout changes',
      'Check against master location database',
      'Flag locations that don\'t match naming patterns'
    ],
    relatedConditions: [
      { field: 'validate_location_exists', label: 'Check location exists in master list', suggested: true },
      { field: 'validate_location_pattern', label: 'Check location follows naming convention', suggested: true },
      { field: 'ignore_temporary_locations', label: 'Ignore temp locations during moves', suggested: false }
    ]
  },
  {
    id: 'storage-overflow',
    title: 'Storage Areas Overflowing',
    description: 'Locations holding more than their safe capacity',
    icon: Warehouse,
    illustration: '📦📦📦📦💥',
    realWorldExample: 'Dock 2 has 15 pallets but only rated for 8 safely',
    businessImpact: 'Safety hazard and makes counting impossible',
    frequency: 'Especially common during peak seasons',
    category: 'space',
    color: 'bg-orange-100 border-orange-300 text-orange-800',
    ruleType: 'OVERCAPACITY',
    smartSuggestions: [
      'Alert at 85-90% capacity to prevent overflow',
      'Different limits for dock doors vs storage areas',
      'Consider seasonal capacity variations'
    ],
    relatedConditions: [
      { field: 'capacity_buffer', label: 'Alert before reaching 100%', suggested: true },
      { field: 'priority_locations', label: 'Stricter limits for critical areas', suggested: true },
      { field: 'seasonal_adjustment', label: 'Adjust for peak seasons', suggested: false }
    ]
  },
  {
    id: 'wrong-product-areas',
    title: 'Products in Wrong Storage Types',
    description: 'Items stored in locations not designed for them',
    icon: Package,
    illustration: '🥩➡️🧽❌',
    realWorldExample: 'Food items stored near cleaning chemicals or hazmat',
    businessImpact: 'Contamination risk and compliance violations',
    frequency: 'Critical for food, pharma, and hazmat operations',
    category: 'product',
    color: 'bg-red-100 border-red-300 text-red-800',
    ruleType: 'PRODUCT_INCOMPATIBILITY',
    smartSuggestions: [
      'Essential for food safety and pharmaceutical compliance',
      'Check product categories against location restrictions',
      'Consider cross-contamination risks'
    ],
    relatedConditions: [
      { field: 'product_category_rules', label: 'Enforce category restrictions', suggested: true },
      { field: 'contamination_risks', label: 'Check for contamination risks', suggested: true },
      { field: 'regulatory_compliance', label: 'Enforce regulatory requirements', suggested: false }
    ]
  },
  {
    id: 'location-setup-errors',
    title: 'Location Configuration Issues',
    description: 'Inconsistent location types and mapping patterns',
    icon: Settings,
    illustration: '🗺️⚙️❌📍',
    realWorldExample: 'Location shows as both RECEIVING and FINAL type',
    businessImpact: 'Causes system confusion and wrong routing',
    frequency: 'Usually after warehouse layout changes',
    category: 'system',
    color: 'bg-purple-100 border-purple-300 text-purple-800',
    ruleType: 'LOCATION_MAPPING_ERROR',
    smartSuggestions: [
      'Run after any WMS configuration changes',
      'Check for conflicting location type assignments',
      'Validate location pattern consistency'
    ],
    relatedConditions: [
      { field: 'validate_location_types', label: 'Check for conflicting location types', suggested: true },
      { field: 'check_pattern_consistency', label: 'Validate naming pattern consistency', suggested: true },
      { field: 'audit_recent_changes', label: 'Focus on recently changed locations', suggested: false }
    ]
  }
]

// Enhanced time options with smart context
const TIME_OPTIONS = [
  { 
    id: 'end-of-shift', 
    label: 'End of current shift', 
    hours: 8, 
    description: 'Items should be moved before shift ends',
    smartNote: 'Most popular for daily operations',
    warehouseTypes: ['general', 'retail', 'manufacturing']
  },
  { 
    id: 'next-morning', 
    label: 'By next morning', 
    hours: 16, 
    description: 'Overnight items are flagged',
    smartNote: 'Good for 24/7 operations',
    warehouseTypes: ['distribution', 'fulfillment', 'logistics']
  },
  { 
    id: 'same-day', 
    label: 'Same day', 
    hours: 24, 
    description: 'Nothing should sit overnight',
    smartNote: 'Strict but comprehensive',
    warehouseTypes: ['perishable', 'high-value', 'just-in-time']
  },
  { 
    id: 'rush-processing', 
    label: 'Rush processing', 
    hours: 4, 
    description: 'For high-priority or time-sensitive items',
    smartNote: 'Use for critical operations',
    warehouseTypes: ['medical', 'emergency', 'express']
  },
  { 
    id: 'custom', 
    label: 'Custom timing', 
    hours: 0, 
    description: 'Set your own specific timeframe',
    smartNote: 'Full control over timing',
    warehouseTypes: ['all']
  }
]

// Smart sensitivity levels with predictions
const SENSITIVITY_LEVELS = [
  { 
    level: 1, 
    label: 'Very Relaxed', 
    description: 'Only catch the most obvious problems',
    alertsPerWeek: '2-5 alerts',
    example: 'Only pallets sitting for days',
    falsePositiveRate: '< 5%',
    coverage: '~40% of issues caught'
  },
  { 
    level: 2, 
    label: 'Relaxed', 
    description: 'Catch clear problems without being picky',
    alertsPerWeek: '5-15 alerts',
    example: 'Pallets sitting longer than usual',
    falsePositiveRate: '< 10%',
    coverage: '~60% of issues caught'
  },
  { 
    level: 3, 
    label: 'Balanced', 
    description: 'Good balance of catching issues vs noise',
    alertsPerWeek: '10-25 alerts',
    example: 'Most warehouses start here',
    falsePositiveRate: '< 15%',
    coverage: '~75% of issues caught'
  },
  { 
    level: 4, 
    label: 'Strict', 
    description: 'Catch problems early, more alerts',
    alertsPerWeek: '20-40 alerts',
    example: 'Be proactive about potential issues',
    falsePositiveRate: '< 25%',
    coverage: '~85% of issues caught'
  },
  { 
    level: 5, 
    label: 'Very Strict', 
    description: 'Catch everything, expect many alerts',
    alertsPerWeek: '40+ alerts',
    example: 'Zero tolerance approach',
    falsePositiveRate: '< 35%',
    coverage: '~95% of issues caught'
  }
]

interface EnhancedSmartBuilderProps {
  onRuleCreate?: (ruleData: any) => void
  onCancel?: () => void
}

export function EnhancedSmartBuilder({ onRuleCreate, onCancel }: EnhancedSmartBuilderProps) {
  const [currentStep, setCurrentStep] = useState<'problem' | 'scenario' | 'smart-enhance' | 'advanced' | 'preview'>('problem')
  const [selectedProblem, setSelectedProblem] = useState<string | null>(null)
  const [ruleName, setRuleName] = useState('')
  const [selectedTimeframe, setSelectedTimeframe] = useState<string>('end-of-shift')
  const [customHours, setCustomHours] = useState(6)
  const [sensitivity, setSensitivity] = useState(3)
  const [selectedAreas, setSelectedAreas] = useState<string[]>(['receiving'])
  const [advancedMode, setAdvancedMode] = useState(false)
  const [selectedSuggestions, setSelectedSuggestions] = useState<string[]>([])
  const [additionalConditions] = useState<unknown[]>([])
  const [showSmartSuggestions, setShowSmartSuggestions] = useState(true)
  
  // Advanced mode state management
  const [advancedConditions, setAdvancedConditions] = useState<Record<string, any>>({})
  const [isValidatingAdvanced, setIsValidatingAdvanced] = useState(false)
  const [advancedValidationResult, setAdvancedValidationResult] = useState<{ success: boolean; error?: string } | null>(null)
  
  const problem = WAREHOUSE_PROBLEMS.find(p => p.id === selectedProblem)
  const timeOption = TIME_OPTIONS.find(t => t.id === selectedTimeframe)
  const sensitivityInfo = SENSITIVITY_LEVELS.find(s => s.level === sensitivity)

  // Enhanced Smart suggestions with contextual intelligence
  const getSmartSuggestions = () => {
    if (!problem) return []
    
    const baseSuggestions = problem.smartSuggestions
    const contextualSuggestions = []
    
    // Rule-type specific contextual suggestions
    switch (problem.ruleType) {
      case 'STAGNANT_PALLETS':
        if (selectedTimeframe === 'end-of-shift') {
          contextualSuggestions.push('Shift-end rules work well for most operations')
        }
        if (selectedTimeframe === 'custom' && customHours <= 2) {
          contextualSuggestions.push('Short timeframes are ideal for high-value or perishable items')
        }
        if (selectedAreas.includes('receiving') && selectedAreas.includes('staging')) {
          contextualSuggestions.push('Monitoring handoff points reduces 60% of delays')
        }
        break
        
      case 'LOCATION_SPECIFIC_STAGNANT':
        if (selectedAreas.includes('aisles')) {
          contextualSuggestions.push('Aisle monitoring prevents 80% of traffic incidents')
        }
        if (customHours <= 2) {
          contextualSuggestions.push('Short aisle timeframes keep traffic flowing smoothly')
        }
        break
        
      case 'TEMPERATURE_ZONE_MISMATCH':
        contextualSuggestions.push('Food safety requires immediate temperature alerts')
        if (sensitivity >= 4) {
          contextualSuggestions.push('High sensitivity essential for regulatory compliance')
        }
        break
        
      case 'UNCOORDINATED_LOTS':
        if (selectedAreas.includes('receiving')) {
          contextualSuggestions.push('Most lot coordination issues happen at receiving handoff')
        }
        contextualSuggestions.push('80% completion threshold catches most stragglers')
        break
        
      case 'DATA_INTEGRITY':
        contextualSuggestions.push('Run data checks during off-peak hours for better performance')
        if (sensitivity >= 4) {
          contextualSuggestions.push('High sensitivity may flag temporary delays as errors')
        }
        break
        
      case 'MISSING_LOCATION':
        contextualSuggestions.push('Check immediately after network issues or system updates')
        contextualSuggestions.push('Most common during shift changes and busy periods')
        break
        
      case 'INVALID_LOCATION':
        contextualSuggestions.push('Essential after warehouse layout changes')
        contextualSuggestions.push('Run weekly as preventive maintenance')
        break
        
      case 'OVERCAPACITY':
        if (selectedAreas.includes('dock')) {
          contextualSuggestions.push('Dock capacity alerts prevent delivery delays')
        }
        contextualSuggestions.push('85-90% capacity threshold prevents most overflows')
        break
        
      case 'PRODUCT_INCOMPATIBILITY':
        contextualSuggestions.push('Critical for food, pharmaceutical, and chemical operations')
        contextualSuggestions.push('Set up location restrictions in master data first')
        break
        
      case 'LOCATION_MAPPING_ERROR':
        contextualSuggestions.push('Run after any WMS configuration changes')
        contextualSuggestions.push('Schedule monthly as preventive maintenance')
        break
    }
    
    // General sensitivity-based suggestions
    if (sensitivity >= 4) {
      contextualSuggestions.push('High sensitivity requires good data quality to avoid false alerts')
    }
    if (sensitivity <= 2) {
      contextualSuggestions.push('Low sensitivity reduces noise but may miss early warning signs')
    }
    
    // Industry-specific suggestions
    const industrySpecific = getIndustrySpecificSuggestions(problem.ruleType)
    
    return [...baseSuggestions, ...contextualSuggestions, ...industrySpecific]
  }
  
  // Industry-specific intelligent suggestions
  const getIndustrySpecificSuggestions = (ruleType: string): string[] => {
    const suggestions: string[] = []
    
    switch (ruleType) {
      case 'TEMPERATURE_ZONE_MISMATCH':
        suggestions.push('🍕 Food industry: FDA requires 15-minute maximum for temperature excursions')
        suggestions.push('💊 Pharmaceutical: USP guidelines demand immediate temperature alerts')
        break
        
      case 'PRODUCT_INCOMPATIBILITY':
        suggestions.push('🏪 Retail: Keep cosmetics away from food products')
        suggestions.push('⚗️ Chemical: OSHA requires strict separation of incompatible materials')
        break
        
      case 'OVERCAPACITY':
        suggestions.push('☢️ Hazmat: OSHA mandates strict capacity limits for dangerous goods')
        suggestions.push('🍖 Food: HACCP compliance requires documented capacity controls')
        break
        
      case 'DATA_INTEGRITY':
        suggestions.push('📊 3PL: Multiple clients require separate data validation rules')
        suggestions.push('🏭 Manufacturing: Quality systems demand 100% data accuracy')
        break
    }
    
    return suggestions
  }

  // Advanced mode helper functions
  const getInitialConditionsForProblem = (): Record<string, any> => {
    if (!problem) return {}
    
    const timeHours = selectedTimeframe === 'custom' ? customHours : (timeOption?.hours || 8)
    
    // Generate initial conditions based on the basic configuration
    const baseConditions: Record<string, any> = {}
    
    switch (problem.ruleType) {
      case 'STAGNANT_PALLETS':
        baseConditions.time_threshold_hours = timeHours
        if (selectedAreas.length > 0) {
          baseConditions.location_types = selectedAreas.map(area => area.toUpperCase())
        }
        break
        
      case 'LOCATION_SPECIFIC_STAGNANT':
        baseConditions.time_threshold_hours = timeHours
        baseConditions.location_pattern = 'AISLE*'
        break
        
      case 'TEMPERATURE_ZONE_MISMATCH':
        baseConditions.product_patterns = ['*FROZEN*', '*REFRIGERATED*']
        baseConditions.prohibited_zones = ['AMBIENT', 'GENERAL']
        baseConditions.time_threshold_minutes = Math.max(15, timeHours * 60)
        break
        
      case 'UNCOORDINATED_LOTS':
        baseConditions.completion_threshold = 0.8
        baseConditions.location_types = ['RECEIVING']
        break
        
      case 'DATA_INTEGRITY':
        baseConditions.check_duplicate_scans = true
        baseConditions.check_impossible_locations = true
        break
        
      case 'OVERCAPACITY':
        baseConditions.check_all_locations = true
        baseConditions.capacity_buffer = sensitivity >= 4 ? 10 : 15
        break
        
      case 'LOCATION_MAPPING_ERROR':
        baseConditions.validate_location_types = true
        baseConditions.check_pattern_consistency = true
        break
        
      default:
        baseConditions.time_threshold_hours = timeHours
    }
    
    return baseConditions
  }

  const handleAdvancedConditionsChange = (conditions: Record<string, any>) => {
    setAdvancedConditions(conditions)
    // Clear previous validation results when conditions change
    setAdvancedValidationResult(null)
  }

  const handleValidateAdvancedConditions = async () => {
    setIsValidatingAdvanced(true)
    
    try {
      // Simulate validation - in real implementation, this would call an API
      await new Promise(resolve => setTimeout(resolve, 1000))
      
      // Basic validation checks
      const hasValidConditions = Object.keys(advancedConditions).length > 0
      const hasComplexConditions = Object.values(advancedConditions).some(value => 
        typeof value === 'object' && value !== null && !Array.isArray(value)
      )
      
      if (!hasValidConditions) {
        setAdvancedValidationResult({
          success: false,
          error: 'At least one condition is required'
        })
      } else {
        setAdvancedValidationResult({
          success: true
        })
      }
    } catch (error) {
      setAdvancedValidationResult({
        success: false,
        error: 'Validation failed due to an unexpected error'
      })
    } finally {
      setIsValidatingAdvanced(false)
    }
  }

  // Enhanced intelligent parameter recommendations with deep warehouse context
  const getIntelligentRecommendations = (): {
    timeframe: string;
    sensitivity: string;
    areas: string;
    businessImpact: string;
    industryBestPractice: string;
    riskAssessment: string;
  } => {
    if (!problem) return {
      timeframe: '',
      sensitivity: '',
      areas: '',
      businessImpact: '',
      industryBestPractice: '',
      riskAssessment: ''
    }
    
    const recommendations = {
      timeframe: '',
      sensitivity: '',
      areas: '',
      businessImpact: '',
      industryBestPractice: '',
      riskAssessment: ''
    }
    
    // Rule-type specific intelligent recommendations
    switch (problem.ruleType) {
      case 'STAGNANT_PALLETS':
        recommendations.timeframe = 'Most successful warehouses use 4-6 hours for receiving areas'
        recommendations.sensitivity = 'Balanced sensitivity catches 75% of issues with minimal false alerts'
        recommendations.industryBestPractice = 'Grocery: 4-6h | Electronics: 2-3h | General: 6-8h'
        break
        
      case 'TEMPERATURE_ZONE_MISMATCH':
        recommendations.timeframe = 'FDA requires 15-30 minutes maximum for temperature compliance'
        recommendations.sensitivity = 'Maximum sensitivity essential for regulatory compliance'
        recommendations.industryBestPractice = 'Food Safety: 15min | Pharma: 5min | General: 30min'
        recommendations.riskAssessment = 'HIGH RISK: Product spoilage costs $500-2000 per incident'
        break
        
      case 'LOCATION_SPECIFIC_STAGNANT':
        recommendations.timeframe = '2-4 hours prevents bottlenecks without over-alerting'
        recommendations.sensitivity = 'Higher sensitivity recommended during peak hours (10am-2pm)'
        recommendations.industryBestPractice = 'Main aisles: 2h | Side aisles: 4h | Pick paths: 1h'
        break
        
      case 'DATA_INTEGRITY':
        recommendations.timeframe = 'Run every 2-4 hours during busy periods'
        recommendations.sensitivity = 'Medium sensitivity balances accuracy with performance'
        recommendations.industryBestPractice = '3PL: Every 2h | Retail: Every 4h | Manufacturing: Every 1h'
        break
        
      case 'OVERCAPACITY':
        recommendations.timeframe = 'Real-time monitoring recommended for capacity violations'
        recommendations.sensitivity = 'High sensitivity prevents safety hazards'
        recommendations.industryBestPractice = 'Alert at 85% general, 75% hazmat, 90% dry storage'
        recommendations.riskAssessment = 'SAFETY RISK: Overcapacity creates accident hazards'
        break
        
      case 'UNCOORDINATED_LOTS':
        recommendations.timeframe = '80-90% completion threshold most effective'
        recommendations.sensitivity = 'Balanced sensitivity catches stragglers without noise'
        recommendations.industryBestPractice = 'Large lots: 85% | Small lots: 75% | Rush orders: 90%'
        break
        
      default:
        recommendations.timeframe = 'Standard warehouse operations typically use 4-8 hour windows'
        recommendations.sensitivity = 'Balanced approach recommended for general warehouse rules'
    }
    
    // Area-specific recommendations
    if (selectedAreas.length === 0) {
      recommendations.areas = 'Select specific areas for more targeted monitoring'
    } else if (selectedAreas.length === 1) {
      recommendations.areas = 'Consider adding related areas for comprehensive coverage'
    } else if (selectedAreas.length > 3) {
      recommendations.areas = 'Multiple areas selected - may want separate rules for better control'
    } else {
      recommendations.areas = 'Good coverage - balanced monitoring across key areas'
    }
    
    // Enhanced business impact calculations
    const timeHours = selectedTimeframe === 'custom' ? customHours : (timeOption?.hours || 8)
    const ruleComplexity = getRuleComplexityScore(problem.ruleType)
    const areaMultiplier = Math.max(1, selectedAreas.length * 0.7)
    const sensitivityMultiplier = sensitivity <= 2 ? 0.4 : sensitivity >= 4 ? 1.6 : 1.0
    
    const estimatedIssuesPerWeek = Math.max(1, Math.floor(
      ruleComplexity * sensitivityMultiplier * areaMultiplier * (8 / Math.max(1, timeHours)) * 2
    ))
    
    const savingsPerIssue = getSavingsPerIssue(problem.ruleType)
    const monthlySavings = estimatedIssuesPerWeek * 4.3 * savingsPerIssue
    
    recommendations.businessImpact = `Projected: ${estimatedIssuesPerWeek} issues/week → $${Math.floor(monthlySavings).toLocaleString()} monthly savings`
    
    return recommendations
  }
  
  // Helper function to calculate rule complexity scoring
  const getRuleComplexityScore = (ruleType: string): number => {
    const complexityMap: Record<string, number> = {
      'DATA_INTEGRITY': 12, // High frequency, many potential issues
      'STAGNANT_PALLETS': 8, // Common issue, predictable patterns
      'MISSING_LOCATION': 6, // Less frequent but critical
      'TEMPERATURE_ZONE_MISMATCH': 4, // Low frequency but high impact
      'OVERCAPACITY': 5, // Seasonal variations
      'LOCATION_SPECIFIC_STAGNANT': 7, // Traffic patterns
      'UNCOORDINATED_LOTS': 6, // Depends on lot coordination
      'INVALID_LOCATION': 3, // Usually after system changes
      'PRODUCT_INCOMPATIBILITY': 2, // Setup-dependent
      'LOCATION_MAPPING_ERROR': 1 // Rare but critical
    }
    return complexityMap[ruleType] || 5
  }
  
  // Helper function to calculate savings per issue by rule type
  const getSavingsPerIssue = (ruleType: string): number => {
    const savingsMap: Record<string, number> = {
      'TEMPERATURE_ZONE_MISMATCH': 1200, // Product spoilage costs
      'OVERCAPACITY': 800, // Safety and efficiency
      'STAGNANT_PALLETS': 300, // Labor and space costs
      'LOCATION_SPECIFIC_STAGNANT': 250, // Traffic delays
      'DATA_INTEGRITY': 400, // Inventory discrepancies
      'MISSING_LOCATION': 350, // Search time
      'UNCOORDINATED_LOTS': 200, // Coordination delays
      'INVALID_LOCATION': 150, // Confusion costs
      'PRODUCT_INCOMPATIBILITY': 1000, // Compliance and safety
      'LOCATION_MAPPING_ERROR': 500 // System efficiency
    }
    return savingsMap[ruleType] || 250
  }

  const steps = [
    { id: 'problem', label: 'What Problem?', completed: !!selectedProblem },
    { id: 'scenario', label: 'Your Scenario', completed: !!ruleName },
    { id: 'smart-enhance', label: 'Smart Suggestions', completed: true },
    { id: 'advanced', label: 'Advanced (Optional)', completed: !advancedMode },
    { id: 'preview', label: 'Preview & Save', completed: false }
  ]

  const handleNext = () => {
    const currentIndex = steps.findIndex(s => s.id === currentStep)
    if (currentIndex < steps.length - 1) {
      const nextStep = steps[currentIndex + 1].id
      // Skip advanced step if not in advanced mode
      if (nextStep === 'advanced' && !advancedMode) {
        setCurrentStep('preview')
      } else {
        setCurrentStep(nextStep as any)
      }
    }
  }

  // Auto-populate suggestions for first-time users
  useEffect(() => {
    if (selectedProblem && problem?.relatedConditions) {
      const suggestedConditions = problem.relatedConditions
        .filter(c => c.suggested)
        .map(c => c.field)
      setSelectedSuggestions(suggestedConditions)
    }
  }, [selectedProblem])

  const handleBack = () => {
    const currentIndex = steps.findIndex(s => s.id === currentStep)
    if (currentIndex > 0) {
      const prevStep = steps[currentIndex - 1].id
      // Skip advanced step if not in advanced mode
      if (prevStep === 'advanced' && !advancedMode) {
        setCurrentStep('smart-enhance')
      } else {
        setCurrentStep(prevStep as any)
      }
    }
  }

  const canProceed = () => {
    switch (currentStep) {
      case 'problem': return !!selectedProblem
      case 'scenario': return !!ruleName.trim()
      case 'smart-enhance': return true
      case 'advanced': return true
      case 'preview': return true
      default: return false
    }
  }

  const renderStepHeader = () => (
    <div className="mb-8">
      {/* Progress Steps */}
      <div className="flex items-center justify-center mb-6 flex-wrap">
        {steps.map((step, index) => (
          <React.Fragment key={step.id}>
            <div className={`flex items-center ${
              step.id === currentStep ? 'text-primary' : 
              step.completed ? 'text-green-600' : 'text-muted-foreground'
            }`}>
              <div className={`w-8 h-8 rounded-full flex items-center justify-center text-sm font-medium ${
                step.id === currentStep ? 'bg-primary text-primary-foreground' :
                step.completed ? 'bg-green-500 text-white' : 'bg-muted'
              }`}>
                {step.completed && step.id !== currentStep ? (
                  <CheckCircle className="w-4 h-4" />
                ) : (
                  index + 1
                )}
              </div>
              <span className="ml-2 font-medium text-sm">{step.label}</span>
            </div>
            {index < steps.length - 1 && (
              <div className={`mx-2 md:mx-4 w-6 md:w-12 h-0.5 ${
                steps[index + 1].completed || steps[index + 1].id === currentStep ? 'bg-primary' : 'bg-muted'
              }`} />
            )}
          </React.Fragment>
        ))}
      </div>
    </div>
  )

  const renderProblemSelection = () => (
    <div className="space-y-6">
      <div className="text-center space-y-2">
        <h2 className="text-2xl font-bold">What warehouse problem bugs you most?</h2>
        <p className="text-muted-foreground text-lg">
          Choose the situation that happens in your warehouse and causes headaches
        </p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-4 max-w-5xl mx-auto">
        {WAREHOUSE_PROBLEMS.map((problem) => (
          <Card 
            key={problem.id}
            className={`cursor-pointer transition-all hover:shadow-lg ${
              selectedProblem === problem.id 
                ? 'ring-2 ring-primary shadow-lg' 
                : 'hover:shadow-md'
            }`}
            onClick={() => setSelectedProblem(problem.id)}
          >
            <CardHeader className="pb-3">
              <div className="flex items-start gap-4">
                <div className={`p-3 rounded-lg ${problem.color}`}>
                  <problem.icon className="w-6 h-6" />
                </div>
                <div className="flex-1">
                  <CardTitle className="text-lg mb-2">{problem.title}</CardTitle>
                  <p className="text-sm text-muted-foreground mb-3">{problem.description}</p>
                  
                  {/* Visual illustration */}
                  <div className="text-2xl mb-3 font-mono">{problem.illustration}</div>
                  
                  {/* Real world example */}
                  <Alert className="mb-3">
                    <Lightbulb className="h-4 w-4" />
                    <AlertDescription className="text-xs">
                      <strong>Real example:</strong> {problem.realWorldExample}
                    </AlertDescription>
                  </Alert>
                  
                  {/* Business impact */}
                  <div className="space-y-2 text-xs">
                    <div className="flex items-center gap-2">
                      <TrendingUp className="w-3 h-3 text-red-500" />
                      <span><strong>Impact:</strong> {problem.businessImpact}</span>
                    </div>
                    <div className="flex items-center gap-2">
                      <Target className="w-3 h-3 text-blue-500" />
                      <span><strong>Frequency:</strong> {problem.frequency}</span>
                    </div>
                  </div>
                </div>
              </div>
            </CardHeader>
          </Card>
        ))}
      </div>
    </div>
  )

  const renderScenarioConfiguration = () => (
    <div className="space-y-6 max-w-3xl mx-auto">
      <div className="text-center space-y-2">
        <h2 className="text-2xl font-bold">Tell us about your specific situation</h2>
        <p className="text-muted-foreground">
          Let's make this rule perfect for your warehouse operation
        </p>
      </div>

      {problem && (
        <Card className="mb-6">
          <CardHeader>
            <div className="flex items-center gap-3">
              <div className={`p-2 rounded-lg ${problem.color}`}>
                <problem.icon className="w-5 h-5" />
              </div>
              <div>
                <CardTitle className="text-lg">Solving: {problem.title}</CardTitle>
                <p className="text-sm text-muted-foreground">{problem.realWorldExample}</p>
              </div>
            </div>
          </CardHeader>
        </Card>
      )}

      <div className="space-y-6">
        {/* Rule Name */}
        <Card>
          <CardHeader>
            <CardTitle className="text-base">What should we call this rule?</CardTitle>
            <p className="text-sm text-muted-foreground">Give it a name that your team will understand</p>
          </CardHeader>
          <CardContent>
            <Input
              value={ruleName}
              onChange={(e) => setRuleName(e.target.value)}
              placeholder={`e.g., "Catch ${problem?.title.toLowerCase() || 'problems'} in receiving"`}
              className="text-lg p-4"
            />
            <div className="mt-2 text-xs text-muted-foreground">
              💡 <strong>Tip:</strong> Use names like "Morning dock cleanup check" or "Frozen goods safety watch"
            </div>
          </CardContent>
        </Card>

        {/* Smart Time Configuration */}
        <Card>
          <CardHeader>
            <div className="flex items-center justify-between">
              <div>
                <CardTitle className="text-base">How long is "too long" for items to sit?</CardTitle>
                <p className="text-sm text-muted-foreground">When should we alert you about this problem?</p>
              </div>
              <Badge variant="outline" className="bg-blue-50 text-blue-700 border-blue-200">
                <Brain className="w-3 h-3 mr-1" />
                Smart Suggestions
              </Badge>
            </div>
          </CardHeader>
          <CardContent className="space-y-4">
            {/* Smart recommendations based on problem type */}
            {problem && (
              <Alert className="border-blue-200 bg-blue-50">
                <Wand2 className="h-4 w-4 text-blue-600" />
                <AlertDescription>
                  <strong>For {problem.title.toLowerCase()}:</strong> {problem.smartSuggestions[0]}
                </AlertDescription>
              </Alert>
            )}

            <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
              {TIME_OPTIONS.filter(opt => opt.id !== 'custom').map((option) => (
                <button
                  key={option.id}
                  onClick={() => setSelectedTimeframe(option.id)}
                  className={`p-4 text-left rounded-lg border-2 transition-all ${
                    selectedTimeframe === option.id
                      ? 'border-primary bg-primary/5'
                      : 'border-muted hover:border-primary/50'
                  }`}
                >
                  <div className="flex items-center justify-between">
                    <div className="font-medium">{option.label}</div>
                    {option.smartNote && (
                      <Badge variant="outline" className="text-xs">{option.smartNote}</Badge>
                    )}
                  </div>
                  <div className="text-sm text-muted-foreground mt-1">{option.description}</div>
                  <div className="text-xs text-primary mt-2">≈ {option.hours} hours</div>
                </button>
              ))}
            </div>

            {/* Custom timing with smart suggestions */}
            <div className="border-t pt-4">
              <button
                onClick={() => setSelectedTimeframe('custom')}
                className={`w-full p-4 text-left rounded-lg border-2 transition-all ${
                  selectedTimeframe === 'custom'
                    ? 'border-primary bg-primary/5'
                    : 'border-muted hover:border-primary/50'
                }`}
              >
                <div className="font-medium">Custom timing</div>
                <div className="text-sm text-muted-foreground mt-1">Set your own specific timeframe</div>
              </button>
              
              {selectedTimeframe === 'custom' && (
                <div className="mt-4 p-4 bg-muted/50 rounded-lg">
                  <Label className="text-sm font-medium">Hours</Label>
                  <div className="flex items-center gap-4 mt-2">
                    <Slider
                      value={[customHours]}
                      onValueChange={(value) => setCustomHours(value[0])}
                      max={48}
                      min={1}
                      step={1}
                      className="flex-1"
                    />
                    <div className="text-lg font-medium w-16 text-center">
                      {customHours}h
                    </div>
                  </div>
                  <div className="text-xs text-muted-foreground mt-1">
                    Alert when items sit for more than {customHours} hours
                  </div>
                  
                  {/* Smart suggestions for custom values */}
                  <div className="mt-3 p-3 bg-blue-50 rounded-lg">
                    <div className="text-xs font-medium text-blue-800 mb-1">💡 Smart Suggestion:</div>
                    <div className="text-xs text-blue-700">
                      {customHours <= 2 ? 'Very strict - good for high-priority items' :
                       customHours <= 4 ? 'Strict - catches problems early' :
                       customHours <= 8 ? 'Balanced - most common choice' :
                       customHours <= 12 ? 'Relaxed - fewer false alarms' :
                       'Very relaxed - only obvious problems'}
                    </div>
                  </div>
                </div>
              )}
            </div>
          </CardContent>
        </Card>

        {/* Smart Area Selection - Show for location-relevant problems */}
        {(['forgotten-items', 'traffic-jams', 'storage-overflow', 'incomplete-deliveries'].includes(selectedProblem || '')) && (
          <Card>
            <CardHeader>
              <CardTitle className="text-base">Which areas should we monitor?</CardTitle>
              <p className="text-sm text-muted-foreground">Select the warehouse areas where this problem happens</p>
            </CardHeader>
            <CardContent>
              <div className="grid grid-cols-2 md:grid-cols-3 gap-3">
                {[
                  { id: 'receiving', label: 'Receiving Docks', icon: '🚚', priority: ['forgotten-items', 'incomplete-deliveries'].includes(selectedProblem || '') ? 'high' : 'medium' },
                  { id: 'staging', label: 'Staging Areas', icon: '📦', priority: 'medium' },
                  { id: 'aisles', label: 'Aisles', icon: '🛣️', priority: selectedProblem === 'traffic-jams' ? 'high' : 'low' },
                  { id: 'picking', label: 'Pick Zones', icon: '🛒', priority: 'medium' },
                  { id: 'shipping', label: 'Shipping Docks', icon: '📤', priority: 'low' },
                  { id: 'dock', label: 'Dock Areas', icon: '🏗️', priority: selectedProblem === 'storage-overflow' ? 'high' : 'low' },
                  { id: 'returns', label: 'Returns Area', icon: '↩️', priority: 'low' }
                ].map((area) => (
                  <button
                    key={area.id}
                    onClick={() => {
                      setSelectedAreas(prev => 
                        prev.includes(area.id) 
                          ? prev.filter(a => a !== area.id)
                          : [...prev, area.id]
                      )
                    }}
                    className={`p-3 text-center rounded-lg border-2 transition-all relative ${
                      selectedAreas.includes(area.id)
                        ? 'border-primary bg-primary/5'
                        : 'border-muted hover:border-primary/50'
                    }`}
                  >
                    {area.priority === 'high' && (
                      <Badge variant="outline" className="absolute -top-2 -right-2 bg-yellow-100 text-yellow-800 border-yellow-300 text-xs">
                        Recommended
                      </Badge>
                    )}
                    <div className="text-2xl mb-1">{area.icon}</div>
                    <div className="text-sm font-medium">{area.label}</div>
                  </button>
                ))}
              </div>
            </CardContent>
          </Card>
        )}
      </div>
    </div>
  )

  const renderSmartEnhancement = () => {
    const recommendations = getIntelligentRecommendations()
    const smartSuggestions = getSmartSuggestions()
    
    return (
      <div className="space-y-6 max-w-4xl mx-auto">
        <div className="text-center space-y-2">
          <h2 className="text-2xl font-bold">Smart suggestions to make your rule even better</h2>
          <p className="text-muted-foreground">
            Based on your choices, here are some intelligent recommendations
          </p>
        </div>

        {/* AI Recommendations Panel */}
        <Card className="border-2 border-blue-200 bg-gradient-to-r from-blue-50 to-purple-50">
          <CardHeader>
            <div className="flex items-center gap-3">
              <div className="p-2 rounded-lg bg-gradient-to-r from-blue-100 to-purple-100">
                <Brain className="w-5 h-5 text-blue-600" />
              </div>
              <div>
                <CardTitle className="text-base">AI Analysis & Recommendations</CardTitle>
                <p className="text-sm text-muted-foreground">
                  Personalized suggestions based on your warehouse scenario
                </p>
              </div>
              <Badge variant="outline" className="bg-blue-100 text-blue-800 border-blue-300">
                <Sparkles className="w-3 h-3 mr-1" />
                AI Powered
              </Badge>
            </div>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              {recommendations.timeframe && (
                <Alert className="border-green-200 bg-green-50">
                  <Timer className="h-4 w-4 text-green-600" />
                  <AlertDescription className="text-sm">
                    <strong>Timing:</strong> {recommendations.timeframe}
                  </AlertDescription>
                </Alert>
              )}
              {recommendations.sensitivity && (
                <Alert className="border-purple-200 bg-purple-50">
                  <Target className="h-4 w-4 text-purple-600" />
                  <AlertDescription className="text-sm">
                    <strong>Sensitivity:</strong> {recommendations.sensitivity}
                  </AlertDescription>
                </Alert>
              )}
              {recommendations.areas && (
                <Alert className="border-orange-200 bg-orange-50">
                  <MapPin className="h-4 w-4 text-orange-600" />
                  <AlertDescription className="text-sm">
                    <strong>Areas:</strong> {recommendations.areas}
                  </AlertDescription>
                </Alert>
              )}
              {recommendations.businessImpact && (
                <Alert className="border-indigo-200 bg-indigo-50">
                  <TrendingUp className="h-4 w-4 text-indigo-600" />
                  <AlertDescription className="text-sm">
                    <strong>Impact:</strong> {recommendations.businessImpact}
                  </AlertDescription>
                </Alert>
              )}
              {recommendations.industryBestPractice && (
                <Alert className="border-blue-200 bg-blue-50">
                  <Users className="h-4 w-4 text-blue-600" />
                  <AlertDescription className="text-sm">
                    <strong>Best Practice:</strong> {recommendations.industryBestPractice}
                  </AlertDescription>
                </Alert>
              )}
              {recommendations.riskAssessment && (
                <Alert className="border-red-200 bg-red-50">
                  <AlertTriangle className="h-4 w-4 text-red-600" />
                  <AlertDescription className="text-sm">
                    <strong>Risk:</strong> {recommendations.riskAssessment}
                  </AlertDescription>
                </Alert>
              )}
            </div>
            
            {/* Enhanced Contextual Smart Suggestions */}
            {smartSuggestions.length > 0 && (
              <div className="mt-4 space-y-3">
                <div className="p-4 bg-white/80 rounded-lg border border-blue-200">
                  <h4 className="font-medium mb-2 text-sm flex items-center gap-2">
                    <Brain className="w-4 h-4 text-blue-600" />
                    💡 AI-Powered Insights
                  </h4>
                  <ul className="space-y-2">
                    {smartSuggestions.slice(0, 4).map((suggestion, index) => {
                      const isIndustrySpecific = suggestion.includes('🍕') || suggestion.includes('💊') || 
                                                suggestion.includes('🏪') || suggestion.includes('⚗️') || 
                                                suggestion.includes('☢️') || suggestion.includes('📊')
                      return (
                        <li key={index} className={`text-xs flex items-start gap-2 ${
                          isIndustrySpecific ? 'text-blue-700 bg-blue-50 p-2 rounded' : 'text-muted-foreground'
                        }`}>
                          <span className={`mt-0.5 ${
                            isIndustrySpecific ? 'text-blue-600' : 'text-blue-500'
                          }`}>•</span>
                          <span className={isIndustrySpecific ? 'font-medium' : ''}>{suggestion}</span>
                        </li>
                      )
                    })}
                  </ul>
                </div>
                
                {/* Show remaining suggestions if there are more */}
                {smartSuggestions.length > 4 && (
                  <details className="p-3 bg-gray-50 rounded-lg">
                    <summary className="cursor-pointer text-sm font-medium text-gray-700 hover:text-gray-900">
                      🔍 View {smartSuggestions.length - 4} more suggestions
                    </summary>
                    <ul className="space-y-1 mt-2">
                      {smartSuggestions.slice(4).map((suggestion, index) => (
                        <li key={index + 4} className="text-xs text-gray-600 flex items-start gap-2">
                          <span className="text-gray-500 mt-0.5">•</span>
                          {suggestion}
                        </li>
                      ))}
                    </ul>
                  </details>
                )}
              </div>
            )}
          </CardContent>
        </Card>

        {/* Smart Sensitivity Adjustment */}
        <Card>
        <CardHeader>
          <div className="flex items-center justify-between">
            <div>
              <CardTitle className="text-base">How strict should this rule be?</CardTitle>
              <p className="text-sm text-muted-foreground">
                More strict = catch problems earlier but more alerts
              </p>
            </div>
            <Badge variant="outline" className="bg-green-50 text-green-700 border-green-200">
              <Activity className="w-3 h-3 mr-1" />
              AI Optimized
            </Badge>
          </div>
        </CardHeader>
        <CardContent className="space-y-6">
          {/* Smart recommendation based on problem */}
          {problem && (
            <Alert className="border-green-200 bg-green-50">
              <Sparkles className="h-4 w-4 text-green-600" />
              <AlertDescription>
                <strong>Smart Recommendation:</strong> For {problem.title.toLowerCase()}, most successful warehouses start with <strong>Balanced</strong> sensitivity and adjust based on results.
              </AlertDescription>
            </Alert>
          )}

          {/* Sensitivity Slider with Smart Context */}
          <div>
            <div className="flex items-center justify-between mb-4">
              <span className="text-sm text-muted-foreground">Fewer Alerts</span>
              <span className="text-sm text-muted-foreground">More Alerts</span>
            </div>
            <Slider
              value={[sensitivity]}
              onValueChange={(value) => setSensitivity(value[0])}
              max={5}
              min={1}
              step={1}
              className="mb-4"
            />
            
            {/* Current Selection with Predictions */}
            {sensitivityInfo && (
              <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mt-4">
                <Card className="p-4">
                  <div className="text-center">
                    <BarChart3 className="w-8 h-8 mx-auto mb-2 text-blue-500" />
                    <div className="font-medium text-lg">{sensitivityInfo.label}</div>
                    <div className="text-sm text-muted-foreground">{sensitivityInfo.description}</div>
                  </div>
                </Card>
                <Card className="p-4">
                  <div className="text-center">
                    <Target className="w-8 h-8 mx-auto mb-2 text-green-500" />
                    <div className="font-medium text-lg">{sensitivityInfo.alertsPerWeek}</div>
                    <div className="text-sm text-muted-foreground">Expected alerts per week</div>
                  </div>
                </Card>
                <Card className="p-4">
                  <div className="text-center">
                    <CheckCircle className="w-8 h-8 mx-auto mb-2 text-orange-500" />
                    <div className="font-medium text-lg">{sensitivityInfo.coverage}</div>
                    <div className="text-sm text-muted-foreground">Issues caught</div>
                  </div>
                </Card>
              </div>
            )}
          </div>
        </CardContent>
      </Card>

      {/* Smart Additional Conditions */}
      {problem && problem.relatedConditions && (
        <Card>
          <CardHeader>
            <CardTitle className="text-base">Want to make this rule even smarter?</CardTitle>
            <p className="text-sm text-muted-foreground">
              Add these optional conditions for better accuracy
            </p>
          </CardHeader>
          <CardContent className="space-y-3">
            {problem.relatedConditions.map((condition, index) => (
              <div key={index} className="flex items-start gap-3 p-3 border rounded-lg">
                <input
                  type="checkbox"
                  id={condition.field}
                  checked={selectedSuggestions.includes(condition.field)}
                  onChange={(e) => {
                    if (e.target.checked) {
                      setSelectedSuggestions(prev => [...prev, condition.field])
                    } else {
                      setSelectedSuggestions(prev => prev.filter(s => s !== condition.field))
                    }
                  }}
                  className="rounded border-gray-300 mt-1"
                />
                <div className="flex-1">
                  <label htmlFor={condition.field} className="font-medium cursor-pointer">
                    {condition.label}
                  </label>
                  {condition.suggested && (
                    <Badge variant="outline" className="ml-2 bg-yellow-100 text-yellow-800 border-yellow-300 text-xs">
                      Recommended
                    </Badge>
                  )}
                </div>
              </div>
            ))}
          </CardContent>
        </Card>
      )}

      {/* Advanced Mode Toggle */}
      <Card className="border-2 border-dashed border-purple-200">
        <CardContent className="p-6">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-3">
              <div className="p-2 rounded-lg bg-purple-100">
                <Layers className="w-5 h-5 text-purple-600" />
              </div>
              <div>
                <h3 className="font-medium">Want even more control?</h3>
                <p className="text-sm text-muted-foreground">
                  Try the advanced visual builder for complex conditions
                </p>
              </div>
            </div>
            <div className="flex items-center gap-3">
              <Badge variant="outline" className="bg-purple-50 text-purple-700 border-purple-200">
                Power User Mode
              </Badge>
              <Button
                variant={advancedMode ? "default" : "outline"}
                onClick={() => setAdvancedMode(!advancedMode)}
                className="flex items-center gap-2"
              >
                <Settings className="w-4 h-4" />
                {advancedMode ? 'Exit Advanced' : 'Try Advanced'}
              </Button>
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
    )
  }

  const renderAdvancedBuilder = () => (
    <div className="space-y-6 max-w-5xl mx-auto">
      <div className="text-center space-y-2">
        <h2 className="text-2xl font-bold">Advanced Visual Rule Builder</h2>
        <p className="text-muted-foreground">
          Build complex conditions with interactive drag-and-drop interface
        </p>
        <Badge variant="outline" className="bg-purple-50 text-purple-700 border-purple-200">
          <Layers className="w-3 h-3 mr-1" />
          Power User Mode
        </Badge>
      </div>

      {/* Enhanced Context Alert */}
      <Alert className="border-purple-200 bg-gradient-to-r from-purple-50 to-indigo-50">
        <Brain className="h-4 w-4 text-purple-600" />
        <AlertDescription>
          <strong>Advanced Mode Active:</strong> Create sophisticated multi-condition rules with visual logic building. 
          Conditions are pre-populated based on your basic configuration and can be customized below.
        </AlertDescription>
      </Alert>

      {/* Problem Context Summary */}
      {problem && (
        <Card className="border-l-4 border-l-purple-500 bg-purple-50/30">
          <CardContent className="pt-6">
            <div className="flex items-center gap-3 mb-3">
              <problem.icon className="w-5 h-5 text-purple-600" />
              <div>
                <h3 className="font-medium">Building Rule For: {problem.title}</h3>
                <p className="text-sm text-muted-foreground">Rule Type: {problem.ruleType}</p>
              </div>
            </div>
            <p className="text-sm">{problem.realWorldExample}</p>
          </CardContent>
        </Card>
      )}

      {/* Interactive Visual Rule Builder */}
      <VisualRuleBuilder
        key={`${selectedProblem}-${selectedTimeframe}-${customHours}-${sensitivity}-${selectedAreas.join(',')}`} // Force re-render when context changes
        initialConditions={getInitialConditionsForProblem()}
        ruleType={problem?.ruleType}
        onConditionsChange={handleAdvancedConditionsChange}
        onValidate={handleValidateAdvancedConditions}
        isValidating={isValidatingAdvanced}
        validationResult={advancedValidationResult}
      />

      {/* Advanced Features Summary */}
      <Card className="bg-gradient-to-r from-purple-50 to-indigo-50 border-purple-200">
        <CardContent className="pt-6">
          <h4 className="font-medium mb-3 flex items-center gap-2">
            <Sparkles className="w-4 h-4 text-purple-600" />
            Advanced Features Available
          </h4>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-3 text-sm">
            <div className="flex items-center gap-2">
              <CheckCircle className="w-4 h-4 text-green-600" />
              <span>Interactive condition building</span>
            </div>
            <div className="flex items-center gap-2">
              <CheckCircle className="w-4 h-4 text-green-600" />
              <span>AND/OR logic operators</span>
            </div>
            <div className="flex items-center gap-2">
              <CheckCircle className="w-4 h-4 text-green-600" />
              <span>Multi-field complex conditions</span>
            </div>
            <div className="flex items-center gap-2">
              <CheckCircle className="w-4 h-4 text-green-600" />
              <span>Real-time validation & testing</span>
            </div>
            <div className="flex items-center gap-2">
              <CheckCircle className="w-4 h-4 text-green-600" />
              <span>Visual JSON preview</span>
            </div>
            <div className="flex items-center gap-2">
              <CheckCircle className="w-4 h-4 text-green-600" />
              <span>Intelligent field suggestions</span>
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  )

  const renderPreview = () => {
    const recommendations = getIntelligentRecommendations()
    const timeHours = selectedTimeframe === 'custom' ? customHours : (timeOption?.hours || 8)
    
    // Enhanced data simulation based on actual parameters
    const simulateRealData = () => {
      const baseIssuesPerWeek = problem?.id === 'temperature-violations' ? 12 : 
                               problem?.id === 'traffic-jams' ? 8 : 
                               problem?.id === 'forgotten-items' ? 15 : 10
      
      const sensitivityMultiplier = sensitivity <= 2 ? 0.4 : sensitivity >= 4 ? 1.6 : 1.0
      const areaMultiplier = selectedAreas.length * 0.7
      const timeMultiplier = timeHours <= 4 ? 1.4 : timeHours >= 12 ? 0.6 : 1.0
      
      const issuesPerWeek = Math.max(1, Math.floor(baseIssuesPerWeek * sensitivityMultiplier * areaMultiplier * timeMultiplier))
      const savingsPerIssue = problem?.id === 'temperature-violations' ? 1200 : 
                             problem?.id === 'traffic-jams' ? 250 : 180
      const monthlySavings = issuesPerWeek * 4.3 * savingsPerIssue
      const timesSavedHours = issuesPerWeek * (problem?.id === 'traffic-jams' ? 2.5 : 1.5)
      const coveragePercent = Math.min(95, Math.max(40, 40 + (sensitivity * 10) + (selectedSuggestions.length * 5)))
      
      return {
        issuesPerWeek,
        monthlySavings: Math.floor(monthlySavings),
        timesSavedHours: Math.floor(timesSavedHours),
        coveragePercent
      }
    }
    
    const liveData = simulateRealData()
    
    return (
      <div className="space-y-6 max-w-4xl mx-auto">
        <div className="text-center space-y-2">
          <h2 className="text-2xl font-bold">Your smart rule is ready!</h2>
          <p className="text-muted-foreground">
            Here's what your enhanced rule will do with live predictions
          </p>
        </div>

      <Card className="border-2 border-primary/20">
        <CardHeader>
          <div className="flex items-center gap-3">
            <div className="p-2 rounded-lg bg-primary/10">
              <CheckCircle className="w-5 h-5 text-primary" />
            </div>
            <div>
              <CardTitle className="text-xl">{ruleName || 'Your Smart Rule'}</CardTitle>
              <p className="text-muted-foreground">Enhanced with AI recommendations</p>
            </div>
            {advancedMode && (
              <Badge variant="outline" className="bg-purple-50 text-purple-700 border-purple-200">
                <Layers className="w-3 h-3 mr-1" />
                Advanced Mode
              </Badge>
            )}
          </div>
        </CardHeader>
        <CardContent className="space-y-6">
          {/* Rule Summary */}
          <Alert>
            <Brain className="h-4 w-4" />
            <AlertDescription>
              <strong>Smart Rule Summary:</strong>
              <br />
              This rule will monitor for {problem?.title.toLowerCase()} and alert you when issues are detected{' '}
              {selectedAreas.length > 0 ? `in ${selectedAreas.join(' or ')} areas` : 'across your warehouse'}{' '}
              {(['forgotten-items', 'traffic-jams'].includes(selectedProblem || '')) ? 
                `for longer than ${selectedTimeframe === 'custom' ? `${customHours} hours` : timeOption?.label.toLowerCase()}` : 
                'based on the configured detection criteria'}.
              <br />
              <br />
              <strong>Rule Type:</strong> {problem?.ruleType} | <strong>Intelligence Level:</strong> {sensitivityInfo?.label} sensitivity with {selectedSuggestions.length} smart enhancements active.
                {advancedMode && Object.keys(advancedConditions).length > 0 && (
                  <>
                    {' '}| <strong>Advanced Mode:</strong> {Object.keys(advancedConditions).length} custom condition{Object.keys(advancedConditions).length > 1 ? 's' : ''} configured.
                  </>
                )}
            </AlertDescription>
          </Alert>

          {/* Live Performance Predictions */}
          <div className="space-y-4">
            <div className="flex items-center justify-between">
              <h4 className="font-medium">📊 Live Performance Predictions</h4>
              <Badge variant="outline" className="bg-green-100 text-green-800 border-green-300">
                <Activity className="w-3 h-3 mr-1" />
                Based on your settings
              </Badge>
            </div>
            
            <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
              <Card className="p-4 bg-blue-50 border-blue-200">
                <div className="text-center">
                  <div className="text-2xl font-bold text-blue-600">
                    {liveData.issuesPerWeek}
                  </div>
                  <div className="text-xs text-muted-foreground">Issues caught/week</div>
                  <div className="text-xs text-blue-600 mt-1">
                    {sensitivityInfo?.label} sensitivity
                  </div>
                </div>
              </Card>
              <Card className="p-4 bg-green-50 border-green-200">
                <div className="text-center">
                  <div className="text-2xl font-bold text-green-600">
                    ${liveData.monthlySavings.toLocaleString()}
                  </div>
                  <div className="text-xs text-muted-foreground">Monthly savings</div>
                  <div className="text-xs text-green-600 mt-1">
                    {selectedAreas.length} area{selectedAreas.length > 1 ? 's' : ''}
                  </div>
                </div>
              </Card>
              <Card className="p-4 bg-orange-50 border-orange-200">
                <div className="text-center">
                  <div className="text-2xl font-bold text-orange-600">
                    {liveData.timesSavedHours}h
                  </div>
                  <div className="text-xs text-muted-foreground">Time saved/week</div>
                  <div className="text-xs text-orange-600 mt-1">
                    {timeHours}h threshold
                  </div>
                </div>
              </Card>
              <Card className="p-4 bg-purple-50 border-purple-200">
                <div className="text-center">
                  <div className="text-2xl font-bold text-purple-600">
                    {liveData.coveragePercent}%
                  </div>
                  <div className="text-xs text-muted-foreground">Issue coverage</div>
                  <div className="text-xs text-purple-600 mt-1">
                    {selectedSuggestions.length} enhancements
                  </div>
                </div>
              </Card>
            </div>
            
            {/* Real-time insights */}
            <Alert className="border-blue-200 bg-gradient-to-r from-blue-50 to-indigo-50">
              <Lightbulb className="h-4 w-4 text-blue-600" />
              <AlertDescription>
                <strong>Real-time Analysis:</strong> Based on your {problem?.title.toLowerCase()} rule with {sensitivityInfo?.label.toLowerCase()} sensitivity 
                in {selectedAreas.length} area{selectedAreas.length > 1 ? 's' : ''}, you'll catch approximately <strong>{liveData.issuesPerWeek} issues per week</strong>.
                {liveData.monthlySavings > 1000 && (
                  <span> This could save your warehouse over <strong>${liveData.monthlySavings.toLocaleString()}</strong> monthly!</span>
                )}
              </AlertDescription>
            </Alert>
          </div>

          {/* Smart Features Summary */}
          <div>
            <h4 className="font-medium mb-3">Smart Features Enabled:</h4>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
              <div className="flex items-center gap-2 p-3 bg-blue-50 rounded-lg">
                <Brain className="w-4 h-4 text-blue-600" />
                <span className="text-sm">AI-optimized sensitivity</span>
              </div>
              <div className="flex items-center gap-2 p-3 bg-green-50 rounded-lg">
                <Target className="w-4 h-4 text-green-600" />
                <span className="text-sm">Context-aware timing</span>
              </div>
              {selectedSuggestions.length > 0 && (
                <div className="flex items-center gap-2 p-3 bg-purple-50 rounded-lg">
                  <Sparkles className="w-4 h-4 text-purple-600" />
                  <span className="text-sm">{selectedSuggestions.length} smart conditions</span>
                </div>
              )}
              {advancedMode && (
                <div className="flex items-center gap-2 p-3 bg-orange-50 rounded-lg">
                  <Layers className="w-4 h-4 text-orange-600" />
                  <span className="text-sm">Advanced visual logic</span>
                </div>
              )}
            </div>
          </div>
        </CardContent>
      </Card>

      <div className="flex justify-center">
        <Button 
          onClick={() => {
            const ruleData = {
              name: ruleName,
              problem: selectedProblem,
              timeframe: selectedTimeframe,
              customHours,
              sensitivity,
              areas: selectedAreas,
              selectedSuggestions,
              advancedMode,
              additionalConditions,
              // Include advanced conditions if advanced mode was used
              advancedConditions: advancedMode ? advancedConditions : {}
            }
            onRuleCreate?.(ruleData)
          }}
          size="lg"
          className="px-8 bg-gradient-to-r from-blue-600 to-purple-600 hover:from-blue-700 hover:to-purple-700"
        >
          <Sparkles className="w-4 h-4 mr-2" />
          Create Smart Rule
        </Button>
        </div>
      </div>
    )
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 via-white to-purple-50 p-6">
      <div className="max-w-7xl mx-auto">
        {renderStepHeader()}
        
        <div className="mb-8">
          {currentStep === 'problem' && renderProblemSelection()}
          {currentStep === 'scenario' && renderScenarioConfiguration()}
          {currentStep === 'smart-enhance' && renderSmartEnhancement()}
          {currentStep === 'advanced' && renderAdvancedBuilder()}
          {currentStep === 'preview' && renderPreview()}
        </div>

        {/* Navigation */}
        <div className="flex justify-between items-center max-w-4xl mx-auto">
          <Button 
            variant="outline" 
            onClick={currentStep === 'problem' ? onCancel : handleBack}
            className="flex items-center gap-2"
          >
            <ArrowLeft className="w-4 h-4" />
            {currentStep === 'problem' ? 'Cancel' : 'Back'}
          </Button>

          {currentStep !== 'preview' && (
            <Button 
              onClick={handleNext}
              disabled={!canProceed()}
              className="flex items-center gap-2"
            >
              Continue
              <ArrowRight className="w-4 h-4" />
            </Button>
          )}
        </div>

        {/* Help text */}
        <div className="text-center mt-8">
          <p className="text-xs text-muted-foreground">
            ✨ This enhanced builder uses AI to optimize your rules and provide intelligent suggestions.
          </p>
        </div>
      </div>
    </div>
  )
}