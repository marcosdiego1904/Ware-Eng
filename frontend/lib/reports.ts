import api from './api';

export interface Report {
  id: number;
  report_name: string;
  timestamp: string;
  anomaly_count: number;
}

export interface ReportDetails {
  reportId: number;
  reportName: string;
  kpis: KPI[];
  locations: LocationSummary[];
}

export interface KPI {
  label: string;
  value: string | number;
}

export interface LocationSummary {
  name: string;
  anomaly_count: number;
  anomalies: Anomaly[];
}

export interface Anomaly {
  id: number;
  status: 'New' | 'Acknowledged' | 'In Progress' | 'Resolved' | 'Cleared';
  anomaly_type: string;
  location: string;
  priority: 'VERY HIGH' | 'HIGH' | 'MEDIUM' | 'LOW';
  pallet_id: string;
  details: string;
  history: AnomalyHistoryItem[];
  // Enhanced overcapacity detection fields
  utilization_rate?: number;
  expected_overcapacity_count?: number;
  actual_overcapacity_count?: number;
  anomaly_severity_ratio?: number;
  overcapacity_category?: 'Natural' | 'Elevated Natural' | 'Systematic';
  warehouse_total_pallets?: number;
  warehouse_total_capacity?: number;
  statistical_model?: string;
  excess_pallets?: number;
  [key: string]: unknown; // For additional anomaly details
}

export interface AnomalyHistoryItem {
  old_status: string;
  new_status: string;
  comment: string;
  user: string;
  timestamp: string;
}

export interface CreateReportRequest {
  inventory_file: File;
  rules_file?: File;
  column_mapping: Record<string, string>;
  warehouse_id?: string;  // NEW: Add warehouse_id support
  clear_previous?: boolean;  // CLEAR ANOMALIES: Support for clearing previous anomalies
}

export interface SpaceUtilization {
  warehouse_capacity: number;       // Total warehouse capacity (max pallets)
  inventory_count: number;           // Current pallets in this report
  utilization_percentage: number;    // Space utilization %
  available_space: number;           // Remaining capacity
  warehouse_name: string;            // Warehouse identifier
  warehouse_id: string;              // Warehouse ID
}

export const reportsApi = {
  async getReports(): Promise<{ reports: Report[] }> {
    const response = await api.get('/reports');
    return response.data;
  },

  async getReportDetails(reportId: number): Promise<ReportDetails> {
    const response = await api.get(`/reports/${reportId}/details`);
    return response.data;
  },

  async createReport(data: CreateReportRequest): Promise<{ message: string; report_id: number }> {
    console.log('Starting createReport...');
    
    // Check auth token
    const token = localStorage.getItem('auth_token');
    console.log('Auth token exists:', !!token);
    console.log('Auth token preview:', token ? token.substring(0, 20) + '...' : 'null');
    
    const formData = new FormData();
    formData.append('inventory_file', data.inventory_file);
    if (data.rules_file) {
      formData.append('rules_file', data.rules_file);
    }
    formData.append('column_mapping', JSON.stringify(data.column_mapping));
    
    // NEW: Include warehouse_id if provided (from applied template)
    if (data.warehouse_id) {
      formData.append('warehouse_id', data.warehouse_id);
      console.log('Including warehouse_id from applied template:', data.warehouse_id);
    }

    // CLEAR ANOMALIES: Include clear_previous parameter if provided
    if (data.clear_previous !== undefined) {
      formData.append('clear_previous', data.clear_previous.toString());
      console.log('Including clear_previous parameter:', data.clear_previous);
    }

    console.log('Sending FormData with:', {
      inventory_file: data.inventory_file.name,
      rules_file: data.rules_file?.name,
      column_mapping: data.column_mapping,
      warehouse_id: data.warehouse_id,  // NEW: Log warehouse context
      clear_previous: data.clear_previous  // CLEAR ANOMALIES: Log clear parameter
    });

    // Log FormData contents for debugging
    console.log('FormData entries:');
    for (const [key, value] of formData.entries()) {
      console.log(`  ${key}:`, value instanceof File ? `File(${value.name}, ${value.size}bytes)` : value);
    }

    try {
      console.log('Making POST request to /reports...');
      const response = await api.post('/reports', formData);
      console.log('Request successful:', response.data);
      return response.data;
    } catch (error: unknown) {
      console.error('Request failed:', error);

      // Better error handling with proper type checking
      if (error && typeof error === 'object') {
        const err = error as {
          response?: {
            status?: number;
            statusText?: string;
            data?: { message?: string; error?: string }
          };
          message?: string;
          code?: string;
          request?: unknown;
        };

        const errorDetails = {
          status: err.response?.status || 'unknown',
          statusText: err.response?.statusText || 'unknown',
          data: err.response?.data || null,
          message: err.message || 'Unknown error',
          code: err.code || 'unknown',
          hasRequest: !!err.request,
          hasResponse: !!err.response,
          // Provide a user-friendly message
          userMessage: err.response?.data?.message ||
                      err.response?.data?.error ||
                      err.message ||
                      'Failed to create report. Please check your connection and try again.'
        };

        console.error('Error details:', errorDetails);

        // Re-throw with enhanced error information
        const enhancedError = new Error(errorDetails.userMessage);
        Object.assign(enhancedError, { originalError: error, details: errorDetails });
        throw enhancedError;
      }

      // Fallback for non-object errors
      console.error('Non-object error caught:', error);
      throw new Error('An unexpected error occurred. Please try again.');
    }
  },

  async updateAnomalyStatus(
    anomalyId: number, 
    status: string, 
    comment?: string
  ): Promise<{ success: boolean; message: string; new_status: string; history_item: AnomalyHistoryItem }> {
    const response = await api.post(`/anomalies/${anomalyId}/status`, {
      status,
      comment,
    });
    return response.data;
  },

  async deleteReport(reportId: number): Promise<{ success: boolean; message: string }> {
    const response = await api.delete(`/reports/${reportId}`);
    return response.data;
  },

  async exportReport(reportId: number, format: 'excel' | 'pdf' | 'csv'): Promise<{ download_url: string; filename: string }> {
    const response = await api.get(`/reports/${reportId}/export?format=${format}`);
    return response.data;
  },

  async duplicateReport(reportId: number, newName?: string): Promise<{ success: boolean; new_report_id: number; message: string }> {
    const response = await api.post(`/reports/${reportId}/duplicate`, {
      new_name: newName
    });
    return response.data;
  },

  async getSpaceUtilization(reportId: number): Promise<SpaceUtilization> {
    const response = await api.get(`/reports/${reportId}/space-utilization`);
    return response.data;
  },
};

// Utility functions
export const getPriorityColor = (priority: string): string => {
  switch (priority) {
    case 'VERY HIGH':
      return 'bg-red-100 text-red-800 border-red-200';
    case 'HIGH':
      return 'bg-orange-100 text-orange-800 border-orange-200';
    case 'MEDIUM':
      return 'bg-yellow-100 text-yellow-800 border-yellow-200';
    case 'LOW':
      return 'bg-green-100 text-green-800 border-green-200';
    default:
      return 'bg-gray-100 text-gray-800 border-gray-200';
  }
};

export const getStatusColor = (status: string): string => {
  switch (status) {
    case 'New':
      return 'bg-blue-100 text-blue-800 border-blue-200';
    case 'Acknowledged':
      return 'bg-yellow-100 text-yellow-800 border-yellow-200';
    case 'In Progress':
      return 'bg-orange-100 text-orange-800 border-orange-200';
    case 'Resolved':
      return 'bg-green-100 text-green-800 border-green-200';
    default:
      return 'bg-gray-100 text-gray-800 border-gray-200';
  }
};

export const getOvercapacityCategoryColor = (category?: string): string => {
  switch (category) {
    case 'Natural':
      return 'bg-green-100 text-green-800 border-green-200';
    case 'Elevated Natural':
      return 'bg-yellow-100 text-yellow-800 border-yellow-200';
    case 'Systematic':
      return 'bg-red-100 text-red-800 border-red-200';
    default:
      return 'bg-gray-100 text-gray-800 border-gray-200';
  }
};