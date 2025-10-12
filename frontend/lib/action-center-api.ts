import { reportsApi, Report, ReportDetails, Anomaly } from './reports'
import {
  ACTION_CATEGORIES_TEMPLATE,
  getCategoryFromAnomalyType,
  getAnomalyTypesForCategory,
  isMVPRule
} from './rule-mappings'
import { calculateProgressComparison, ProgressComparison } from './progress-comparison'

// Enhanced interfaces for Action Center
export interface ActionCategory {
  id: string
  title: string
  description: string
  icon: any
  count: number
  priority: 'critical' | 'high' | 'medium' | 'low'
  financialImpact: number
  color: string
  bgColor: string
  borderColor: string
  category: 'MVP' | 'SECONDARY'
  ruleType: string
  isTriggered: boolean
  anomalies: EnrichedActionAnomaly[]
  baseFinancialImpact: number
  urgencyMultiplier: number
}

export interface EnrichedActionAnomaly extends Anomaly {
  location_name: string
  days_idle: number
  calculated_financial_impact: number
  urgency_score: number
  assigned_to: string
  last_action: string
  category_id: string
}

export interface ActionCenterData {
  categories: ActionCategory[]
  mvpCategories: ActionCategory[]
  secondaryCategories: ActionCategory[]
  totalActiveItems: number
  totalFinancialImpact: number
  avgHoursCritical: number
  resolvedToday: number
  lastUpdated: Date
  progressComparison?: ProgressComparison
}

// Financial impact calculation constants
const FINANCIAL_CONSTANTS = {
  BASE_COST_PER_HOUR: 25,
  RECEIVING_AREA_MULTIPLIER: 3.0,
  AISLE_AREA_MULTIPLIER: 2.0,
  PRIORITY_MULTIPLIERS: {
    'VERY HIGH': 4.0,
    'HIGH': 2.5,
    'MEDIUM': 1.5,
    'LOW': 1.0
  },
  HOURS_PER_DAY: 24
}

// Helper function to determine if location is critical
function getLocationMultiplier(locationName: string): number {
  const location = locationName.toUpperCase()

  if (location.includes('RECV') || location.includes('RECEIVING')) {
    return FINANCIAL_CONSTANTS.RECEIVING_AREA_MULTIPLIER
  }

  if (location.includes('AISLE')) {
    return FINANCIAL_CONSTANTS.AISLE_AREA_MULTIPLIER
  }

  return 1.0
}

// Extract hours idle from anomaly details or timestamp
function calculateDaysIdle(anomaly: Anomaly): number {
  // Try to extract hours from details text
  if (anomaly.details) {
    const hoursMatch = anomaly.details.match(/(\d+\.?\d*)\s*h/i)
    if (hoursMatch) {
      return Math.ceil(parseFloat(hoursMatch[1]) / 24) // Convert hours to days
    }

    const daysMatch = anomaly.details.match(/(\d+)\s*day/i)
    if (daysMatch) {
      return parseInt(daysMatch[1])
    }
  }

  // Fallback: calculate from timestamp if available
  // For now, return a reasonable default
  return 1
}

// Calculate financial impact for a single anomaly
function calculateFinancialImpact(anomaly: Anomaly, locationName: string, categoryTemplate: any): number {
  const baseCost = categoryTemplate.baseFinancialImpact || FINANCIAL_CONSTANTS.BASE_COST_PER_HOUR
  const urgencyMultiplier = categoryTemplate.urgencyMultiplier || 1.0
  const locationMultiplier = getLocationMultiplier(locationName)
  const priorityMultiplier = FINANCIAL_CONSTANTS.PRIORITY_MULTIPLIERS[anomaly.priority as keyof typeof FINANCIAL_CONSTANTS.PRIORITY_MULTIPLIERS] || 1.0
  const daysIdle = calculateDaysIdle(anomaly)

  // For overcapacity anomalies, use excess_pallets if available
  if (anomaly.excess_pallets && anomaly.excess_pallets > 0) {
    return Math.round(anomaly.excess_pallets * baseCost * urgencyMultiplier * locationMultiplier * priorityMultiplier)
  }

  // For time-based anomalies (stagnant pallets)
  const dailyImpact = baseCost * urgencyMultiplier * locationMultiplier * priorityMultiplier
  return Math.round(dailyImpact * daysIdle)
}

// Generate assigned team member based on anomaly type and location
function getAssignedTeamMember(anomaly: Anomaly, locationName: string): string {
  const location = locationName.toUpperCase()

  // Team assignment logic based on location and anomaly type
  if (location.includes('RECV')) {
    return ['Mike Johnson', 'Sarah Davis', 'Tom Wilson'][Math.floor(Math.random() * 3)]
  }

  if (location.includes('AISLE')) {
    return ['Lisa Chen', 'Carlos Rodriguez', 'Mike Johnson'][Math.floor(Math.random() * 3)]
  }

  if (anomaly.anomaly_type.includes('Temperature')) {
    return 'Carlos Rodriguez' // Quality control specialist
  }

  if (anomaly.anomaly_type.includes('Data') || anomaly.anomaly_type.includes('Scan')) {
    return 'Sarah Davis' // Data specialist
  }

  return ['Mike Johnson', 'Lisa Chen', 'Tom Wilson', 'Sarah Davis', 'Carlos Rodriguez'][Math.floor(Math.random() * 5)]
}

// Generate last action description
function getLastActionDescription(anomaly: Anomaly): string {
  const actionTemplates = {
    'Stagnant Pallet': ['Received from supplier', 'Quality check pending', 'Awaiting putaway'],
    'Storage Overcapacity': ['Overflow from receiving', 'Emergency placement', 'Capacity exceeded'],
    'Special Area Capacity': ['Temperature zone full', 'Special handling required', 'Awaiting space'],
    'Location-Specific Stagnant': ['Equipment breakdown', 'Traffic congestion', 'Awaiting clearance'],
    'Uncoordinated Lots': ['Lot partially stored', 'Coordination pending', 'Awaiting lot completion'],
    'Temperature Zone Violation': ['Mis-routed during putaway', 'Urgent relocation needed', 'Cold chain breach'],
    'Invalid Location': ['Location code error', 'System mapping issue', 'Manual verification needed'],
    'Duplicate Scan': ['Scanner error detected', 'Data correction needed', 'Manual verification'],
    'Location Mapping Error': ['Mapping inconsistency', 'System update required', 'Configuration error']
  }

  const templates = actionTemplates[anomaly.anomaly_type as keyof typeof actionTemplates] || ['Action required', 'Investigation needed', 'Manual review']
  return templates[Math.floor(Math.random() * templates.length)]
}

// Transform anomaly to action item
function enrichAnomalyForAction(anomaly: Anomaly, locationName: string, categoryId: string): EnrichedActionAnomaly {
  const categoryTemplate = ACTION_CATEGORIES_TEMPLATE[categoryId as keyof typeof ACTION_CATEGORIES_TEMPLATE]

  return {
    ...anomaly,
    location_name: locationName,
    days_idle: calculateDaysIdle(anomaly),
    calculated_financial_impact: calculateFinancialImpact(anomaly, locationName, categoryTemplate),
    urgency_score: FINANCIAL_CONSTANTS.PRIORITY_MULTIPLIERS[anomaly.priority as keyof typeof FINANCIAL_CONSTANTS.PRIORITY_MULTIPLIERS] || 1.0,
    assigned_to: getAssignedTeamMember(anomaly, locationName),
    last_action: getLastActionDescription(anomaly),
    category_id: categoryId
  }
}

// Process reports data into action center format
function processReportsForActionCenter(
  reports: Report[],
  reportsDetails: ReportDetails[],
  previousReportDetails?: ReportDetails[]
): ActionCenterData {
  // Initialize categories from template
  const categories: { [key: string]: ActionCategory } = {}
  const previousCategories: { [key: string]: ActionCategory } = {}

  Object.entries(ACTION_CATEGORIES_TEMPLATE).forEach(([categoryId, template]) => {
    categories[categoryId] = {
      ...template,
      priority: template.priority as 'critical' | 'high' | 'medium' | 'low',
      category: template.category as 'MVP' | 'SECONDARY',
      count: 0,
      financialImpact: 0,
      isTriggered: false,
      anomalies: []
    }
    // Initialize previous categories too
    previousCategories[categoryId] = {
      ...template,
      priority: template.priority as 'critical' | 'high' | 'medium' | 'low',
      category: template.category as 'MVP' | 'SECONDARY',
      count: 0,
      financialImpact: 0,
      isTriggered: false,
      anomalies: []
    }
  })

  // Process all anomalies from recent reports
  let totalResolvedToday = 0
  let totalHoursForCritical = 0
  let criticalItemsCount = 0

  reportsDetails.forEach(reportDetail => {
    // Safety check: ensure locations exists and is an array
    if (!reportDetail.locations || !Array.isArray(reportDetail.locations)) {
      console.warn('Report detail missing locations array:', reportDetail)
      return
    }

    reportDetail.locations.forEach(location => {
      // Safety check: ensure anomalies exists and is an array
      if (!location.anomalies || !Array.isArray(location.anomalies)) {
        console.warn('Location missing anomalies array:', location)
        return
      }

      location.anomalies.forEach(anomaly => {
        // Count resolved items
        if (anomaly.status === 'Resolved' || anomaly.status === 'Acknowledged') {
          totalResolvedToday++
        }

        // Skip resolved and cleared items for active counts
        if (anomaly.status === 'Resolved' || anomaly.status === 'Cleared') return

        // Get category for this anomaly type
        const categoryId = getCategoryFromAnomalyType(anomaly.anomaly_type)
        if (!categoryId || !categories[categoryId]) return

        // Enrich anomaly with action data
        const enrichedAnomaly = enrichAnomalyForAction(anomaly, location.name, categoryId)

        // Add to category
        categories[categoryId].count++
        categories[categoryId].financialImpact += enrichedAnomaly.calculated_financial_impact
        categories[categoryId].isTriggered = true
        categories[categoryId].anomalies.push(enrichedAnomaly)

        // Track critical items for average calculation
        if (anomaly.priority === 'VERY HIGH' || anomaly.priority === 'HIGH') {
          totalHoursForCritical += enrichedAnomaly.days_idle * 24
          criticalItemsCount++
        }
      })
    })
  })

  // Convert to array and separate MVP vs Secondary
  const categoriesArray = Object.values(categories)
  const mvpCategories = categoriesArray.filter(cat => cat.category === 'MVP')
  const secondaryCategories = categoriesArray.filter(cat => cat.category === 'SECONDARY')

  // Calculate totals
  const totalActiveItems = categoriesArray.reduce((sum, cat) => sum + cat.count, 0)
  const totalFinancialImpact = categoriesArray.reduce((sum, cat) => sum + cat.financialImpact, 0)
  const avgHoursCritical = criticalItemsCount > 0 ? totalHoursForCritical / criticalItemsCount : 0

  // Process previous report data if available
  let previousTotalActiveItems = 0
  if (previousReportDetails && previousReportDetails.length > 0) {
    previousReportDetails.forEach(reportDetail => {
      // Safety check: ensure locations exists and is an array
      if (!reportDetail.locations || !Array.isArray(reportDetail.locations)) {
        return
      }

      reportDetail.locations.forEach(location => {
        // Safety check: ensure anomalies exists and is an array
        if (!location.anomalies || !Array.isArray(location.anomalies)) {
          return
        }

        location.anomalies.forEach(anomaly => {
          // Skip resolved and cleared items
          if (anomaly.status === 'Resolved' || anomaly.status === 'Cleared') return

          // Get category for this anomaly type
          const categoryId = getCategoryFromAnomalyType(anomaly.anomaly_type)
          if (!categoryId || !previousCategories[categoryId]) return

          // Add to previous category count
          previousCategories[categoryId].count++
        })
      })
    })

    const previousCategoriesArray = Object.values(previousCategories)
    previousTotalActiveItems = previousCategoriesArray.reduce((sum, cat) => sum + cat.count, 0)
  }

  // Calculate progress comparison if we have previous data
  let progressComparison: ProgressComparison | undefined
  if (previousReportDetails && previousReportDetails.length > 0) {
    const previousCategoriesArray = Object.values(previousCategories)
    progressComparison = calculateProgressComparison(
      categoriesArray,
      previousCategoriesArray,
      totalActiveItems,
      previousTotalActiveItems
    )
  }

  return {
    categories: categoriesArray,
    mvpCategories,
    secondaryCategories,
    totalActiveItems,
    totalFinancialImpact,
    avgHoursCritical: Math.round(avgHoursCritical * 10) / 10, // Round to 1 decimal
    resolvedToday: totalResolvedToday,
    lastUpdated: new Date(),
    progressComparison
  }
}

// Main API functions
export const actionCenterApi = {
  async getActionCenterData(): Promise<ActionCenterData> {
    try {
      // Fetch all reports
      const reportsResponse = await reportsApi.getReports()
      const reports = reportsResponse.reports || []

      // Get recent reports for detailed analysis (last 7 days)
      const recentReports = reports
        .filter(report => {
          const reportDate = new Date(report.timestamp)
          const weekAgo = new Date(Date.now() - 7 * 24 * 60 * 60 * 1000)
          return reportDate > weekAgo
        })
        .sort((a, b) => new Date(b.timestamp).getTime() - new Date(a.timestamp).getTime())
        .slice(0, 10) // Limit to 10 most recent

      // Fetch detailed data for recent reports
      const detailsPromises = recentReports.map(report =>
        reportsApi.getReportDetails(report.id).catch(() => null)
      )

      const reportsDetails = (await Promise.all(detailsPromises)).filter(Boolean) as ReportDetails[]

      // Get previous report for comparison (second most recent)
      let previousReportDetails: ReportDetails[] | undefined
      if (recentReports.length >= 2) {
        try {
          const previousReport = await reportsApi.getReportDetails(recentReports[1].id)
          previousReportDetails = [previousReport]
        } catch (error) {
          console.warn('Failed to fetch previous report for comparison:', error)
        }
      }

      // Process into action center format with comparison
      return processReportsForActionCenter(reports, reportsDetails, previousReportDetails)

    } catch (error) {
      console.error('Failed to fetch action center data:', error)
      throw new Error('Failed to load action center data')
    }
  },

  async getCategoryDetails(categoryId: string): Promise<EnrichedActionAnomaly[]> {
    try {
      const data = await this.getActionCenterData()
      const category = data.categories.find(cat => cat.id === categoryId)
      return category?.anomalies || []
    } catch (error) {
      console.error(`Failed to fetch category details for ${categoryId}:`, error)
      throw new Error(`Failed to load ${categoryId} details`)
    }
  },

  // Utility function to get financial impact summary
  getFinancialSummary(data: ActionCenterData) {
    return {
      totalRisk: data.totalFinancialImpact,
      dailyRisk: Math.round(data.totalFinancialImpact * 0.6), // Estimate daily portion
      mvpRisk: data.mvpCategories.reduce((sum, cat) => sum + cat.financialImpact, 0),
      secondaryRisk: data.secondaryCategories.reduce((sum, cat) => sum + cat.financialImpact, 0)
    }
  },

  // Resolution API functions
  async resolveAllAnomalies(): Promise<{ success: boolean; message: string; resolved_count: number }> {
    const baseURL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:5000/api/v1'
    const response = await fetch(`${baseURL}/anomalies/resolve-all`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${localStorage.getItem('auth_token')}`
      }
    })

    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`)
    }

    return await response.json()
  },

  async resolveCategoryAnomalies(anomalyType: string): Promise<{ success: boolean; message: string; resolved_count: number }> {
    const baseURL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:5000/api/v1'
    const response = await fetch(`${baseURL}/anomalies/resolve-category`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${localStorage.getItem('auth_token')}`
      },
      body: JSON.stringify({ anomaly_type: anomalyType })
    })

    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`)
    }

    return await response.json()
  },

  async resolveBulkAnomalies(anomalyIds: string[]): Promise<{ success: boolean; message: string; resolved_count: number }> {
    const baseURL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:5000/api/v1'
    const response = await fetch(`${baseURL}/anomalies/resolve-bulk`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${localStorage.getItem('auth_token')}`
      },
      body: JSON.stringify({ anomaly_ids: anomalyIds })
    })

    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`)
    }

    return await response.json()
  },

  async resolveSingleAnomaly(anomalyId: string): Promise<{ success: boolean; message: string }> {
    const baseURL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:5000/api/v1'
    const response = await fetch(`${baseURL}/anomalies/${anomalyId}/status`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${localStorage.getItem('auth_token')}`
      },
      body: JSON.stringify({ status: 'Resolved', comment: 'Marked as resolved via Action Center' })
    })

    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`)
    }

    return await response.json()
  }
}

export default actionCenterApi