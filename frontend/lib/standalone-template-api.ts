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
}

export const standaloneTemplateAPI = new StandaloneTemplateAPI();