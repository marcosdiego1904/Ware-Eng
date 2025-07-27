/**
 * API integration layer for the Warehouse Rules System
 * Follows existing patterns from lib/api.ts
 */

import { api } from './api';
import type {
  RuleHistory,
  RulesResponse,
  RuleResponse,
  CategoriesResponse,
  TemplatesResponse,
  CreateRuleRequest,
  UpdateRuleRequest,
  RuleValidationRequest,
  ValidationResult,
  RulePreviewRequest,
  PreviewResult,
  RuleTestRequest,
  TestResult,
  DebugRequest,
  DebugResult,
  PerformanceMetrics,
  AnalyticsData,
  RuleFilters,
  ApiError,
  TemplateInstance
} from './rules-types';

// ==================== RULES CRUD API ====================

export const rulesApi = {
  /**
   * Get all rules with optional filtering
   */
  async getRules(filters?: RuleFilters): Promise<RulesResponse> {
    const params = new URLSearchParams();
    
    if (filters?.category) params.append('category', filters.category);
    if (filters?.priority) params.append('priority', filters.priority);
    if (filters?.status && filters.status !== 'all') {
      params.append('active_only', (filters.status === 'active').toString());
    }
    if (filters?.rule_type) params.append('rule_type', filters.rule_type);
    if (filters?.search) params.append('search', filters.search);
    
    const queryString = params.toString();
    const url = `/rules${queryString ? `?${queryString}` : ''}`;
    
    const response = await api.get<RulesResponse>(url);
    return response.data;
  },

  /**
   * Get a specific rule by ID with history
   */
  async getRule(ruleId: number): Promise<RuleResponse> {
    const response = await api.get<RuleResponse>(`/rules/${ruleId}`);
    return response.data;
  },

  /**
   * Create a new rule
   */
  async createRule(data: CreateRuleRequest): Promise<RuleResponse> {
    const response = await api.post<RuleResponse>('/rules', data);
    return response.data;
  },

  /**
   * Update an existing rule
   */
  async updateRule(ruleId: number, data: UpdateRuleRequest): Promise<RuleResponse> {
    const response = await api.put<RuleResponse>(`/rules/${ruleId}`, data);
    return response.data;
  },

  /**
   * Delete a rule
   */
  async deleteRule(ruleId: number): Promise<{ success: boolean; message: string }> {
    const response = await api.delete<{ success: boolean; message: string }>(`/rules/${ruleId}`);
    return response.data;
  },

  /**
   * Activate or deactivate a rule
   */
  async toggleRuleActivation(ruleId: number, isActive: boolean): Promise<RuleResponse> {
    const response = await api.post<RuleResponse>(`/rules/${ruleId}/activate`, { is_active: isActive });
    return response.data;
  },

  /**
   * Duplicate a rule
   */
  async duplicateRule(ruleId: number, newName: string): Promise<RuleResponse> {
    const originalRule = await this.getRule(ruleId);
    
    const duplicateData: CreateRuleRequest = {
      name: newName,
      description: `Copy of ${originalRule.rule.description}`,
      category_id: originalRule.rule.category_id,
      rule_type: originalRule.rule.rule_type,
      conditions: originalRule.rule.conditions,
      parameters: originalRule.rule.parameters,
      priority: originalRule.rule.priority,
      is_active: false // Start inactive for safety
    };
    
    return this.createRule(duplicateData);
  }
};

// ==================== CATEGORIES API ====================

export const categoriesApi = {
  /**
   * Get all rule categories
   */
  async getCategories(): Promise<CategoriesResponse> {
    const response = await api.get<CategoriesResponse>('/categories');
    return response.data;
  }
};

// ==================== RULE TESTING & VALIDATION API ====================

export const ruleTestingApi = {
  /**
   * Validate rule conditions
   */
  async validateRule(data: RuleValidationRequest): Promise<ValidationResult> {
    const response = await api.post<ValidationResult>('/rules/validate', data);
    return response.data;
  },

  /**
   * Preview rule results without saving
   */
  async previewRule(data: RulePreviewRequest): Promise<PreviewResult> {
    const response = await api.post<PreviewResult>('/rules/preview', data);
    return response.data;
  },

  /**
   * Test rules against uploaded data
   */
  async testRules(data: RuleTestRequest): Promise<TestResult> {
    const formData = new FormData();
    formData.append('test_file', data.test_file);
    
    if (data.rule_ids) {
      formData.append('rule_ids', JSON.stringify(data.rule_ids));
    }
    
    const response = await api.post<TestResult>('/rules/test', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });
    return response.data;
  },

  /**
   * Debug rule execution
   */
  async debugRule(ruleId: number, data?: DebugRequest): Promise<DebugResult> {
    const response = await api.post<DebugResult>(`/rules/${ruleId}/debug`, data || {});
    return response.data;
  }
};

// ==================== TEMPLATES API ====================

export const templatesApi = {
  /**
   * Get all rule templates
   */
  async getTemplates(): Promise<TemplatesResponse> {
    const response = await api.get<TemplatesResponse>('/rule-templates');
    return response.data;
  },

  /**
   * Get public templates from community
   */
  async getPublicTemplates(): Promise<TemplatesResponse> {
    const response = await api.get<TemplatesResponse>('/rule-templates/public');
    return response.data;
  },

  /**
   * Create a rule from a template
   */
  async createFromTemplate(templateId: number, instance: TemplateInstance): Promise<RuleResponse> {
    const response = await api.post<RuleResponse>(`/rule-templates/${templateId}/create`, {
      parameters: instance.parameters,
      rule_name: instance.rule_name,
      rule_description: instance.rule_description
    });
    return response.data;
  },

  /**
   * Create a new template
   */
  async createTemplate(data: {
    name: string;
    description: string;
    category_id: number;
    template_conditions: Record<string, any>;
    parameters_schema: Record<string, any>;
    is_public?: boolean;
  }): Promise<{ success: boolean; template_id: number }> {
    const response = await api.post<{ success: boolean; template_id: number }>('/rule-templates', data);
    return response.data;
  },

  /**
   * Get template usage statistics
   */
  async getTemplateUsage(templateId: number): Promise<{ usage_count: number; recent_uses: Array<Record<string, unknown>> }> {
    const response = await api.get<{ usage_count: number; recent_uses: Array<Record<string, unknown>> }>(`/rule-templates/${templateId}/usage`);
    return response.data;
  }
};

// ==================== PERFORMANCE & ANALYTICS API ====================

export const performanceApi = {
  /**
   * Get performance metrics for a specific rule
   */
  async getRulePerformance(ruleId: number): Promise<PerformanceMetrics> {
    const response = await api.get<PerformanceMetrics>(`/rules/${ruleId}/performance`);
    return response.data;
  },

  /**
   * Get overall rules analytics
   */
  async getAnalytics(): Promise<AnalyticsData> {
    const response = await api.get<AnalyticsData>('/rules/analytics');
    return response.data;
  },

  /**
   * Estimate rule performance
   */
  async estimatePerformance(ruleId: number, historicalData?: Array<Record<string, unknown>>): Promise<{
    estimated_anomalies: number;
    confidence_level: number;
    performance_prediction: string;
  }> {
    const response = await api.post<{
      estimated_anomalies: number;
      confidence_level: number;
      performance_prediction: string;
    }>(`/rules/${ruleId}/estimate`, { historical_data: historicalData });
    return response.data;
  }
};

// ==================== RULE HISTORY API ====================

export const historyApi = {
  /**
   * Get rule change history
   */
  async getRuleHistory(ruleId: number): Promise<{ success: boolean; history: RuleHistory[] }> {
    const response = await api.get<{ success: boolean; history: RuleHistory[] }>(`/rules/${ruleId}/history`);
    return response.data;
  },

  /**
   * Revert rule to a previous version
   */
  async revertRule(ruleId: number, version: number): Promise<RuleResponse> {
    const response = await api.post<RuleResponse>(`/rules/${ruleId}/revert/${version}`);
    return response.data;
  }
};

// ==================== BULK OPERATIONS API ====================

export const bulkApi = {
  /**
   * Import rules from file
   */
  async importRules(file: File): Promise<{
    success: boolean;
    imported_count: number;
    skipped_count: number;
    errors: string[];
  }> {
    const formData = new FormData();
    formData.append('rules_file', file);
    
    const response = await api.post<{
      success: boolean;
      imported_count: number;
      skipped_count: number;
      errors: string[];
    }>('/rules/import', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });
    return response.data;
  },

  /**
   * Export rules to file
   */
  async exportRules(ruleIds?: number[]): Promise<Blob> {
    const params = ruleIds ? { rule_ids: ruleIds.join(',') } : {};
    
    const response = await api.get('/rules/export', {
      params,
      responseType: 'blob',
    });
    
    return response.data;
  },

  /**
   * Bulk activate/deactivate rules
   */
  async bulkToggleRules(ruleIds: number[], isActive: boolean): Promise<{
    success: boolean;
    updated_count: number;
    errors: string[];
  }> {
    const response = await api.post<{
      success: boolean;
      updated_count: number;
      errors: string[];
    }>('/rules/bulk-toggle', {
      rule_ids: ruleIds,
      is_active: isActive
    });
    return response.data;
  },

  /**
   * Bulk delete rules
   */
  async bulkDeleteRules(ruleIds: number[]): Promise<{
    success: boolean;
    deleted_count: number;
    errors: string[];
  }> {
    const response = await api.post<{
      success: boolean;
      deleted_count: number;
      errors: string[];
    }>('/rules/bulk-delete', {
      rule_ids: ruleIds
    });
    return response.data;
  }
};

// ==================== UTILITY FUNCTIONS ====================

/**
 * Check if an error response is an API error
 */
export function isApiError(error: unknown): error is ApiError {
  if (error && typeof error === 'object' && 'success' in error) {
    return (error as ApiError).success === false;
  }
  return false;
}

/**
 * Extract error message from API response
 */
export function getErrorMessage(error: unknown): string {
  if (isApiError(error)) {
    return error.message;
  }
  
  if (error instanceof Error) {
    return error.message;
  }
  
  return 'An unexpected error occurred';
}

/**
 * Format validation errors for display
 */
export function formatValidationErrors(errors: Record<string, string[]>): Record<string, string> {
  const formatted: Record<string, string> = {};
  
  for (const [field, messages] of Object.entries(errors)) {
    formatted[field] = messages.join(', ');
  }
  
  return formatted;
}

/**
 * Retry API call with exponential backoff
 */
export async function retryApiCall<T>(
  apiCall: () => Promise<T>,
  maxRetries: number = 3,
  baseDelay: number = 1000
): Promise<T> {
  for (let attempt = 1; attempt <= maxRetries; attempt++) {
    try {
      return await apiCall();
    } catch (error) {
      if (attempt === maxRetries) {
        throw error;
      }
      
      const delay = baseDelay * Math.pow(2, attempt - 1);
      await new Promise(resolve => setTimeout(resolve, delay));
    }
  }
  
  throw new Error('Max retries exceeded');
}

// ==================== COMBINED API OBJECT ====================

/**
 * Main API object that combines all rule-related API functions
 * Following the pattern from your existing api.ts
 */
export const ruleManagementApi = {
  rules: rulesApi,
  categories: categoriesApi,
  testing: ruleTestingApi,
  templates: templatesApi,
  performance: performanceApi,
  history: historyApi,
  bulk: bulkApi,
  
  // Utility functions
  isApiError,
  getErrorMessage,
  formatValidationErrors,
  retryApiCall
};

// Default export for convenience
export default ruleManagementApi;