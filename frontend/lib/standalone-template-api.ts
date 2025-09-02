import { api } from './api';

export interface StandaloneTemplateData {
  // Basic Information
  name: string;
  description?: string;
  category?: string;
  industry?: string;
  tags?: string[];
  
  // Privacy Settings
  visibility?: 'PRIVATE' | 'COMPANY' | 'PUBLIC';
  
  // Structure Configuration
  num_aisles: number;
  racks_per_aisle: number;
  positions_per_rack: number;
  levels_per_position: number;
  level_names?: string;
  default_pallet_capacity?: number;
  bidimensional_racks?: boolean;
  
  // Special Areas
  receiving_areas?: Array<{
    code: string;
    type: string;
    capacity: number;
    zone: string;
  }>;
  staging_areas?: Array<{
    code: string;
    type: string;
    capacity: number;
    zone: string;
  }>;
  dock_areas?: Array<{
    code: string;
    type: string;
    capacity: number;
    zone: string;
  }>;
  
  // Location Format Configuration
  format_config?: object;
  format_pattern_name?: string;
  format_examples?: string[];
}

export interface CreatedTemplate extends StandaloneTemplateData {
  id: number;
  template_code: string;
  created_by: number;
  creator_username: string;
  created_at: string;
  updated_at: string;
  usage_count: number;
  total_storage_locations: number;
  total_capacity: number;
}

export interface ValidationResult {
  valid: boolean;
  errors: string[];
  warnings: string[];
  calculated_totals: {
    storage_locations: number;
    storage_capacity: number;
    estimated_setup_time_minutes: number;
  };
}

export interface TemplateCodePreview {
  template_code: string;
  already_exists: boolean;
  format_explanation: {
    prefix: string;
    structure: string;
    suffix: string;
  };
}

export interface TemplateCategories {
  categories: Array<{
    value: string;
    label: string;
    description: string;
  }>;
  industries: string[];
}

export interface FormatDetectionResult {
  detected: boolean;
  format_config?: object;
  confidence: number;
  pattern_name: string;
  canonical_examples: string[];
}

class StandaloneTemplateAPI {
  /**
   * Create a new template from scratch
   */
  async createTemplate(data: StandaloneTemplateData): Promise<CreatedTemplate> {
    const response = await api.post('/standalone-templates/create', data);
    return response.data.template;
  }

  /**
   * Validate template data without creating it
   */
  async validateTemplate(data: StandaloneTemplateData): Promise<ValidationResult> {
    const response = await api.post('/standalone-templates/validate', data);
    return response.data;
  }

  /**
   * Generate a preview of the template code
   */
  async generateCodePreview(name: string, num_aisles: number, racks_per_aisle: number): Promise<TemplateCodePreview> {
    const response = await api.post('/standalone-templates/generate-code', {
      name,
      num_aisles,
      racks_per_aisle
    });
    return response.data;
  }

  /**
   * Get available template categories and industries
   */
  async getCategories(): Promise<TemplateCategories> {
    const response = await api.get('/standalone-templates/categories');
    return response.data;
  }

  /**
   * Detect location format from examples
   */
  async detectLocationFormat(examples: string[]): Promise<FormatDetectionResult> {
    const response = await api.post('/templates/detect-format', {
      examples: examples.filter(ex => ex.trim().length > 0)
    });
    
    const backendData = response.data;
    
    // Debug logging to help troubleshoot
    console.log('Smart Configuration API Response:', {
      success: backendData.success,
      hasDetectionResult: !!backendData.detection_result,
      hasDetectedPattern: !!backendData.detection_result?.detected_pattern,
      patternType: backendData.detection_result?.detected_pattern?.pattern_type,
      confidence: backendData.detection_result?.confidence
    });
    
    // Transform backend response to frontend interface
    const detectionResult = backendData.detection_result || {};
    const detectedPattern = detectionResult.detected_pattern;
    
    return {
      detected: backendData.success && !!detectedPattern,
      format_config: backendData.format_config,
      confidence: detectionResult.confidence || 0,
      pattern_name: detectedPattern?.pattern_type || 'unknown',
      canonical_examples: detectionResult.canonical_examples || []
    };
  }
}

export const standaloneTemplateAPI = new StandaloneTemplateAPI();