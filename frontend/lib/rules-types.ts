/**
 * TypeScript type definitions for the Warehouse Rules System
 * Matches backend models and API responses
 */

// ==================== CORE RULE TYPES ====================

export interface Rule {
  id: number;
  name: string;
  description: string;
  category_id: number;
  category_name: string;
  rule_type: string;
  conditions: Record<string, any>;
  parameters: Record<string, any>;
  priority: 'VERY_HIGH' | 'HIGH' | 'MEDIUM' | 'LOW';
  is_active: boolean;
  is_default: boolean;
  created_by: number;
  creator_username: string;
  created_at: string;
  updated_at: string;
}

export interface RuleCategory {
  id: number;
  name: string;
  display_name: string;
  priority: number;
  description: string;
  is_active: boolean;
  rule_count: number;
}

export interface RuleTemplate {
  id: number;
  name: string;
  description: string;
  category_id: number;
  category_name: string;
  template_conditions: Record<string, any>;
  parameters_schema: Record<string, any>;
  is_public: boolean;
  usage_count: number;
  created_by: number;
  creator_username: string;
  created_at: string;
  updated_at: string;
}

export interface RuleHistory {
  id: number;
  rule_id: number;
  version: number;
  changes: Record<string, any>;
  changed_by: number;
  user_username: string;
  timestamp: string;
}

export interface RulePerformance {
  id: number;
  rule_id: number;
  rule_name: string;
  report_id: number;
  anomalies_detected: number;
  false_positives: number;
  execution_time_ms: number;
  timestamp: string;
}

// ==================== API REQUEST/RESPONSE TYPES ====================

export interface RulesResponse {
  success: boolean;
  rules: Rule[];
  total: number;
}

export interface RuleResponse {
  success: boolean;
  rule: Rule;
  message?: string;
}

export interface CategoriesResponse {
  success: boolean;
  categories: RuleCategory[];
}

export interface TemplatesResponse {
  success: boolean;
  templates: RuleTemplate[];
}

export interface CreateRuleRequest {
  name: string;
  description: string;
  category_id: number;
  rule_type: string;
  conditions: Record<string, any>;
  parameters?: Record<string, any>;
  priority: Rule['priority'];
  is_active?: boolean;
}

export interface UpdateRuleRequest extends Partial<CreateRuleRequest> {}

export interface RuleValidationRequest {
  conditions: string; // JSON string
  rule_type?: string;
  sample_data?: any[];
}

export interface ValidationResult {
  success: boolean;
  validation_result: {
    is_valid: boolean;
    error_message?: string;
    warnings: string[];
    suggestions: string[];
  };
}

export interface RulePreviewRequest {
  name?: string;
  rule_type: string;
  conditions: Record<string, any>;
  parameters?: Record<string, any>;
  priority?: Rule['priority'];
  sample_data?: any[];
}

export interface PreviewResult {
  success: boolean;
  preview_results: {
    anomalies_found: number;
    execution_time_ms: number;
    sample_anomalies: any[];
    success: boolean;
    error_message?: string;
  };
  performance_estimate: {
    estimated_anomalies: number;
    confidence_level: number;
    execution_time_ms: number;
    detection_rate: number;
    performance_prediction: string;
  };
}

export interface RuleTestRequest {
  test_file: File;
  rule_ids?: number[];
}

export interface TestResult {
  success: boolean;
  test_results: {
    rule_id: number;
    success: boolean;
    anomalies_found: number;
    execution_time_ms: number;
    error_message?: string;
    sample_anomalies: any[];
  }[];
  data_info: {
    rows: number;
    columns: string[];
  };
}

export interface DebugRequest {
  sample_data?: any[];
}

export interface DebugResult {
  success: boolean;
  debug_result: {
    rule_id: number;
    rule_status: string;
    data_compatibility: Record<string, any>;
    condition_analysis: Record<string, any>;
    execution_trace: string[];
    suggestions: string[];
    performance_metrics: Record<string, any>;
  };
}

export interface PerformanceMetrics {
  success: boolean;
  performance_metrics: {
    rule_id: number;
    rule_name: string;
    total_executions: number;
    total_detections: number;
    total_false_positives: number;
    false_positive_rate: number;
    average_execution_time_ms: number;
    recent_records: RulePerformance[];
  };
}

export interface AnalyticsData {
  success: boolean;
  analytics: {
    overview: {
      total_rules: number;
      active_rules: number;
      default_rules: number;
      custom_rules: number;
    };
    categories: {
      category_name: string;
      display_name: string;
      active_rules: number;
      total_rules: number;
      priority: number;
    }[];
    recent_performance: RulePerformance[];
  };
}

// ==================== UI-SPECIFIC TYPES ====================

export interface RuleFilters {
  category?: string;
  priority?: Rule['priority'];
  status?: 'active' | 'inactive' | 'all';
  search?: string;
  rule_type?: string;
}

export interface RuleFormData {
  name: string;
  description: string;
  category_id: number;
  rule_type: string;
  conditions: Record<string, any>;
  parameters: Record<string, any>;
  priority: Rule['priority'];
  is_active: boolean;
}

export interface RulesViewState {
  currentSubView: 'overview' | 'create' | 'edit' | 'templates' | 'analytics';
  selectedRuleId: number | null;
  isCreating: boolean;
  isEditing: boolean;
}

// ==================== RULE TYPE DEFINITIONS ====================

export const RULE_TYPES: Record<string, { label: string; description: string }> = {
  STAGNANT_PALLETS: { 
    label: 'Stagnant Pallets', 
    description: 'Detect pallets that have been stationary for too long' 
  },
  UNCOORDINATED_LOTS: { 
    label: 'Uncoordinated Lots', 
    description: 'Identify lots that are not properly coordinated' 
  },
  OVERCAPACITY: { 
    label: 'Overcapacity', 
    description: 'Monitor areas exceeding capacity limits' 
  },
  INVALID_LOCATION: { 
    label: 'Invalid Location', 
    description: 'Find items in unauthorized locations' 
  },
  LOCATION_SPECIFIC_STAGNANT: { 
    label: 'Location-Specific Stagnant', 
    description: 'Detect stagnation in specific locations' 
  },
  TEMPERATURE_ZONE_MISMATCH: { 
    label: 'Temperature Zone Mismatch', 
    description: 'Items stored in wrong temperature zones' 
  },
  DATA_INTEGRITY: { 
    label: 'Data Integrity', 
    description: 'Identify data inconsistencies and errors' 
  },
  LOCATION_MAPPING_ERROR: { 
    label: 'Location Mapping Error', 
    description: 'Errors in location mapping systems' 
  },
  MISSING_LOCATION: { 
    label: 'Missing Location', 
    description: 'Items with missing location information' 
  },
  PRODUCT_INCOMPATIBILITY: { 
    label: 'Product Incompatibility', 
    description: 'Products stored with incompatible items' 
  }
} as const;

export const PRIORITY_LEVELS: Record<Rule['priority'], { label: string; color: string; weight: number }> = {
  VERY_HIGH: { label: 'Very High', color: 'destructive', weight: 4 },
  HIGH: { label: 'High', color: 'destructive', weight: 3 },
  MEDIUM: { label: 'Medium', color: 'default', weight: 2 },
  LOW: { label: 'Low', color: 'secondary', weight: 1 }
};

export const RULE_CATEGORIES = {
  FLOW_TIME: {
    name: 'FLOW_TIME',
    display_name: 'Flow & Time Rules',
    description: 'Rules that detect stagnant pallets, uncoordinated lots, and time-based issues',
    priority: 1,
    color: 'red'
  },
  SPACE: {
    name: 'SPACE',
    display_name: 'Space Management Rules',
    description: 'Rules that manage warehouse space, capacity, and location compliance',
    priority: 2,
    color: 'orange'
  },
  PRODUCT: {
    name: 'PRODUCT',
    display_name: 'Product Compatibility Rules',
    description: 'Rules that ensure products are stored in appropriate locations',
    priority: 3,
    color: 'blue'
  }
} as const;

// ==================== UTILITY TYPES ====================

export type RuleTypeKey = keyof typeof RULE_TYPES;
export type CategoryKey = keyof typeof RULE_CATEGORIES;

export interface RuleCondition {
  field: string;
  operator: 'equals' | 'not_equals' | 'contains' | 'not_contains' | 'greater_than' | 'less_than' | 'in_list' | 'regex_match';
  value: string | number | string[];
  logical_operator?: 'AND' | 'OR';
}

export interface RuleParameter {
  name: string;
  type: 'string' | 'number' | 'boolean' | 'select' | 'multi-select';
  value: any;
  options?: { value: string; label: string }[];
  min?: number;
  max?: number;
  required?: boolean;
  description?: string;
}

// ==================== ERROR TYPES ====================

export interface ApiError {
  success: false;
  message: string;
  errors?: Record<string, string[]>;
}

export interface FormValidationError {
  field: string;
  message: string;
}

// ==================== STEP TYPES FOR WORKFLOWS ====================

export type RuleCreationStep = 'basic' | 'conditions' | 'parameters' | 'preview';
export type AnalysisStep = 'upload' | 'mapping' | 'rules' | 'processing' | 'complete';

export interface StepProps {
  onNext: () => void;
  onBack: () => void;
}

export interface RuleCreationStepProps extends StepProps {
  onSave?: () => void;
  onCancel?: () => void;
}

// ==================== TEMPLATE TYPES ====================

export interface RuleTemplateParameter {
  name: string;
  type: 'string' | 'number' | 'select' | 'boolean';
  label: string;
  description?: string;
  default?: any;
  options?: { value: any; label: string }[];
  min?: number;
  max?: number;
  required?: boolean;
}

export interface TemplateInstance {
  template_id: number;
  template_name: string;
  parameters: Record<string, any>;
  rule_name: string;
  rule_description?: string;
}

// ==================== DASHBOARD INTEGRATION TYPES ====================

export interface RulesDashboardData {
  stats: {
    total_rules: number;
    active_rules: number;
    recent_changes: number;
    categories_count: number;
  };
  recent_rules: Rule[];
  top_performing_rules: (Rule & { performance_score: number })[];
  category_distribution: {
    category: string;
    count: number;
    percentage: number;
  }[];
}

export interface RuleQuickAction {
  id: string;
  label: string;
  icon: string;
  action: 'create' | 'import' | 'template' | 'analytics';
  description: string;
}

// ==================== EXPORT TYPES ====================

export interface RuleExportData {
  rules: Rule[];
  categories: RuleCategory[];
  export_date: string;
  version: string;
}

export interface RuleImportResult {
  success: boolean;
  imported_count: number;
  skipped_count: number;
  errors: string[];
  imported_rules: Rule[];
}