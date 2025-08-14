import { Report, ReportDetails } from './reports'

export interface OverviewStats {
  totalReports: number
  totalAnomalies: number
  recentActivity: number
  alertsCount: number
  resolutionRate: number
  averageAnomaliesPerReport: number
  criticalLocations: number
  systemHealth: 'excellent' | 'good' | 'warning' | 'critical'
  // Enhanced warehouse utilization metrics
  warehouseUtilization?: number
  totalPallets?: number
  totalCapacity?: number
  expectedOvercapacityCount?: number
  actualOvercapacityCount?: number
  systematicAnomaliesCount?: number
  trendsData: {
    reportsGrowth: number
    anomaliesGrowth: number
    resolutionGrowth: number
    utilizationGrowth?: number
  }
}

export interface DetailedReportData {
  reports: Report[]
  recentReports: ReportDetails[]
  priorityBreakdown: Record<string, number>
  statusBreakdown: Record<string, number>
  locationHotspots: Array<{ name: string; count: number; severity: string }>
}