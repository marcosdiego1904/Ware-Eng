/**
 * Pilot Analytics API Client
 * Admin-only access to pilot program metrics and analytics
 */

import api from './api'

// ===== Type Definitions =====

export interface DateRange {
  start: string
  end: string
}

export interface DashboardFilters {
  user_id?: number
  warehouse_id?: number
  start_date?: string
  end_date?: string
}

// Usage Metrics
export interface UsageMetrics {
  total_sessions: number
  total_time_minutes: number
  avg_session_duration: number
  files_uploaded: number
  feature_usage: Record<string, number>
}

// Business Metrics
export interface BusinessMetrics {
  total_issues: number
  resolved_issues: number
  resolution_rate: number
  avg_resolution_hours: number
  issues_by_severity: Record<string, number>
  issues_by_rule: Record<string, number>
  total_cost_impact: number
  time_saved_minutes: number
  cost_savings: number
}

// Technical Metrics
export interface TechnicalMetrics {
  total_uploads: number
  successful_uploads: number
  failed_uploads: number
  success_rate: number
  avg_processing_time: number
  min_processing_time: number
  max_processing_time: number
  error_types: Record<string, number>
  browsers: Record<string, number>
  devices: Record<string, number>
}

// Dashboard Response
export interface DashboardMetrics {
  success: boolean
  date_range: DateRange
  filters: DashboardFilters
  usage: UsageMetrics
  business: BusinessMetrics
  technical: TechnicalMetrics
}

// Session
export interface Session {
  id: number
  session_id: string
  user_id: number
  warehouse_id?: number
  login_time: string
  logout_time?: string
  last_activity: string
  duration_minutes?: number
  browser?: string
  device_type?: string
}

// Event
export interface AnalyticsEvent {
  id: number
  user_id: number
  warehouse_id?: number
  session_id: string
  event_type: string
  event_category: string
  event_action: string
  event_data?: Record<string, any>
  created_at: string
}

// Anomaly
export interface AnalyticsAnomaly {
  id: number
  anomaly_id: number
  user_id: number
  warehouse_id?: number
  detected_at: string
  severity?: string
  rule_type: string
  resolved_at?: string
  time_to_resolve_hours?: number
  user_action?: string
  potential_cost_impact?: number
  impact_category?: string
}

// ===== API Functions =====

/**
 * Get comprehensive dashboard metrics
 */
export async function getDashboardMetrics(filters?: DashboardFilters): Promise<DashboardMetrics> {
  const params = new URLSearchParams()

  if (filters?.user_id) params.append('user_id', filters.user_id.toString())
  if (filters?.warehouse_id) params.append('warehouse_id', filters.warehouse_id.toString())
  if (filters?.start_date) params.append('start_date', filters.start_date)
  if (filters?.end_date) params.append('end_date', filters.end_date)

  const response = await api.get(`/pilot/dashboard?${params.toString()}`)
  return response.data
}

/**
 * Get detailed usage metrics
 */
export async function getUsageMetrics(filters?: DashboardFilters): Promise<{ success: boolean; data: UsageMetrics }> {
  const params = new URLSearchParams()

  if (filters?.user_id) params.append('user_id', filters.user_id.toString())
  if (filters?.warehouse_id) params.append('warehouse_id', filters.warehouse_id.toString())
  if (filters?.start_date) params.append('start_date', filters.start_date)
  if (filters?.end_date) params.append('end_date', filters.end_date)

  const response = await api.get(`/pilot/usage-metrics?${params.toString()}`)
  return response.data
}

/**
 * Get business impact metrics
 */
export async function getBusinessMetrics(filters?: DashboardFilters): Promise<{ success: boolean; data: BusinessMetrics }> {
  const params = new URLSearchParams()

  if (filters?.user_id) params.append('user_id', filters.user_id.toString())
  if (filters?.warehouse_id) params.append('warehouse_id', filters.warehouse_id.toString())
  if (filters?.start_date) params.append('start_date', filters.start_date)
  if (filters?.end_date) params.append('end_date', filters.end_date)

  const response = await api.get(`/pilot/business-metrics?${params.toString()}`)
  return response.data
}

/**
 * Get technical performance metrics
 */
export async function getTechnicalMetrics(filters?: DashboardFilters): Promise<{ success: boolean; data: TechnicalMetrics }> {
  const params = new URLSearchParams()

  if (filters?.user_id) params.append('user_id', filters.user_id.toString())
  if (filters?.warehouse_id) params.append('warehouse_id', filters.warehouse_id.toString())
  if (filters?.start_date) params.append('start_date', filters.start_date)
  if (filters?.end_date) params.append('end_date', filters.end_date)

  const response = await api.get(`/pilot/technical-metrics?${params.toString()}`)
  return response.data
}

/**
 * Get session history
 */
export async function getSessions(
  filters?: DashboardFilters & { limit?: number }
): Promise<{ success: boolean; count: number; data: Session[] }> {
  const params = new URLSearchParams()

  if (filters?.user_id) params.append('user_id', filters.user_id.toString())
  if (filters?.warehouse_id) params.append('warehouse_id', filters.warehouse_id.toString())
  if (filters?.start_date) params.append('start_date', filters.start_date)
  if (filters?.end_date) params.append('end_date', filters.end_date)
  if (filters?.limit) params.append('limit', filters.limit.toString())

  const response = await api.get(`/pilot/sessions?${params.toString()}`)
  return response.data
}

/**
 * Get event log
 */
export async function getEvents(
  filters?: DashboardFilters & { event_type?: string; limit?: number }
): Promise<{ success: boolean; count: number; data: AnalyticsEvent[] }> {
  const params = new URLSearchParams()

  if (filters?.user_id) params.append('user_id', filters.user_id.toString())
  if (filters?.warehouse_id) params.append('warehouse_id', filters.warehouse_id.toString())
  if (filters?.event_type) params.append('event_type', filters.event_type)
  if (filters?.start_date) params.append('start_date', filters.start_date)
  if (filters?.end_date) params.append('end_date', filters.end_date)
  if (filters?.limit) params.append('limit', filters.limit.toString())

  const response = await api.get(`/pilot/events?${params.toString()}`)
  return response.data
}

/**
 * Get anomaly history
 */
export async function getAnomalies(
  filters?: DashboardFilters & { rule_type?: string; resolved?: 'true' | 'false'; limit?: number }
): Promise<{ success: boolean; count: number; data: AnalyticsAnomaly[] }> {
  const params = new URLSearchParams()

  if (filters?.user_id) params.append('user_id', filters.user_id.toString())
  if (filters?.warehouse_id) params.append('warehouse_id', filters.warehouse_id.toString())
  if (filters?.rule_type) params.append('rule_type', filters.rule_type)
  if (filters?.resolved) params.append('resolved', filters.resolved)
  if (filters?.start_date) params.append('start_date', filters.start_date)
  if (filters?.end_date) params.append('end_date', filters.end_date)
  if (filters?.limit) params.append('limit', filters.limit.toString())

  const response = await api.get(`/pilot/anomalies?${params.toString()}`)
  return response.data
}

/**
 * Export analytics data as CSV or JSON
 */
export async function exportData(
  format: 'csv' | 'json' = 'csv',
  dataType: 'sessions' | 'events' | 'uploads' | 'anomalies' | 'time_savings' | 'all' = 'all',
  filters?: DashboardFilters
): Promise<Blob> {
  const params = new URLSearchParams()

  params.append('format', format)
  params.append('data_type', dataType)

  if (filters?.user_id) params.append('user_id', filters.user_id.toString())
  if (filters?.warehouse_id) params.append('warehouse_id', filters.warehouse_id.toString())
  if (filters?.start_date) params.append('start_date', filters.start_date)
  if (filters?.end_date) params.append('end_date', filters.end_date)

  const response = await api.get(`/pilot/export?${params.toString()}`, {
    responseType: 'blob'
  })

  return response.data
}

/**
 * Trigger download of exported data
 */
export async function downloadExport(
  format: 'csv' | 'json' = 'csv',
  dataType: 'sessions' | 'events' | 'uploads' | 'anomalies' | 'time_savings' | 'all' = 'all',
  filters?: DashboardFilters
): Promise<void> {
  const blob = await exportData(format, dataType, filters)

  // Create download link
  const url = window.URL.createObjectURL(blob)
  const link = document.createElement('a')
  link.href = url

  const timestamp = new Date().toISOString().split('T')[0]
  const extension = format === 'csv' ? 'csv' : 'json'
  link.download = `pilot_analytics_${dataType}_${timestamp}.${extension}`

  document.body.appendChild(link)
  link.click()
  document.body.removeChild(link)
  window.URL.revokeObjectURL(url)
}
