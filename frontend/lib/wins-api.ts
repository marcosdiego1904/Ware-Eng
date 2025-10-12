/**
 * Track Your Wins API Client
 * Fetches gamification and analytics data for the wins dashboard
 */

import api from './api'

export interface HealthScore {
  score: number
  label: string
  color: string
  breakdown: {
    total_pallets: number
    total_anomalies: number
    high_priority_anomalies: number
    unresolved_anomalies: number
  }
}

export interface Achievement {
  id: number
  name: string
  icon: string
  description: string
  unlocked: boolean
  priority: number  // 1 = Highest priority (most impressive), 5 = Lowest
}

export interface Achievements {
  unlocked: number
  total: number
  details: Achievement[]
}

export interface Highlight {
  icon: string
  number: number | string
  title: string
  percentage: number | null
  context: string
}

export interface ProblemScorecardItem {
  type: string
  detected: number
  priority: string
  color: string
  bg: string
}

export interface ResolutionTrackerItem {
  category: string
  icon: string
  resolved: number
  total: number
  lastResolved: string
}

export interface ResolutionTracker {
  categories: ResolutionTrackerItem[]
  total_resolved: number
  total_to_resolve: number
  resolution_percentage: number
}

export interface SpecialLocation {
  name: string
  status: 'clean' | 'warning'
  issues: number
  description?: string
}

export interface SpecialLocationCategory {
  category: string
  locations: SpecialLocation[]
}

export interface OperationalImpactItem {
  icon: string
  title: string
  description: string
}

export interface OperationalImpact {
  analysis_completed: OperationalImpactItem
  problems_prevented: OperationalImpactItem
  issues_resolved: OperationalImpactItem
  processing_efficiency: OperationalImpactItem
}

export interface WinsData {
  report_id: number
  report_name: string
  timestamp: string
  health_score: HealthScore
  achievements: Achievements
  highlights: Highlight[]
  problem_scorecard: ProblemScorecardItem[]
  resolution_tracker: ResolutionTracker
  special_locations: SpecialLocationCategory[]
  operational_impact: OperationalImpact
  totals: {
    total_pallets: number
    total_anomalies: number
    total_issues_detected: number
    total_resolved: number
  }
}

/**
 * Get Track Your Wins data for a specific report
 */
export async function getWinsDataForReport(reportId: number): Promise<WinsData> {
  const response = await api.get<WinsData>(`/reports/${reportId}/wins`)
  return response.data
}

/**
 * Get Track Your Wins data for the user's most recent report
 */
export async function getLatestWinsData(): Promise<WinsData> {
  const response = await api.get<WinsData>('/reports/latest/wins')
  return response.data
}

/**
 * Format a timestamp into a human-readable date string
 */
export function formatWinsTimestamp(timestamp: string): string {
  const date = new Date(timestamp)
  return date.toLocaleDateString('en-US', {
    year: 'numeric',
    month: 'long',
    day: 'numeric',
    hour: '2-digit',
    minute: '2-digit'
  })
}

/**
 * Calculate percentage for progress bars
 */
export function calculatePercentage(resolved: number, total: number): number {
  if (total === 0) return 0
  return Math.round((resolved / total) * 100)
}

/**
 * Get status color for special locations
 */
export function getLocationStatusColor(status: 'clean' | 'warning'): string {
  return status === 'clean' ? '#38A169' : '#FF6B35'
}

/**
 * Format large numbers with commas
 */
export function formatNumber(num: number): string {
  return num.toLocaleString('en-US')
}
