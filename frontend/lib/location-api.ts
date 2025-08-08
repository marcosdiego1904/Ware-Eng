import { api } from './api';
import type { Location, WarehouseConfig, WarehouseTemplate, LocationFilters } from './location-store';

export interface LocationsResponse {
  locations: Location[];
  pagination: {
    page: number;
    per_page: number;
    total: number;
    pages: number;
    has_next: boolean;
    has_prev: boolean;
  };
  summary: {
    total_locations: number;
    storage_locations: number;
    total_capacity: number;
    warehouse_id: string;
  };
}

export interface BulkCreateResponse {
  created_count: number;
  error_count: number;
  errors: string[];
  created_locations: Location[];
}

export interface ValidationResponse {
  validation_results: Array<{
    index: number;
    valid: boolean;
    errors: string[];
    warnings: string[];
  }>;
  summary: {
    total_locations: number;
    valid_locations: number;
    invalid_locations: number;
    overall_valid: boolean;
  };
}

export interface WarehouseSetupData {
  warehouse_id?: string;
  configuration: {
    warehouse_name: string;
    num_aisles: number;
    racks_per_aisle: number;
    positions_per_rack: number;
    levels_per_position?: number;
    level_names?: string;
    default_pallet_capacity?: number;
    bidimensional_racks?: boolean;
    default_zone?: string;
  };
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
  generate_locations?: boolean;
  force_recreate?: boolean;
  create_template?: boolean;
  template_name?: string;
  template_description?: string;
  template_is_public?: boolean;
}

export interface WarehouseSetupResponse {
  message: string;
  warehouse_id: string;
  configuration: WarehouseConfig;
  locations_created: number;
  total_capacity: number;
  template?: WarehouseTemplate;
}

// Location Management API
export const locationApi = {
  // Get locations with filtering and pagination
  async getLocations(
    filters: LocationFilters = {},
    page: number = 1,
    perPage: number = 50
  ): Promise<LocationsResponse> {
    const params = new URLSearchParams({
      page: page.toString(),
      per_page: perPage.toString(),
    });

    Object.entries(filters).forEach(([key, value]) => {
      if (value !== undefined && value !== '') {
        params.append(key, value.toString());
      }
    });

    const response = await api.get(`/locations?${params.toString()}`);
    return response.data;
  },

  // Get single location
  async getLocation(id: number): Promise<Location> {
    const response = await api.get(`/locations/${id}`);
    return response.data.location;
  },

  // Create location
  async createLocation(locationData: Partial<Location>): Promise<Location> {
    const response = await api.post('/locations', locationData);
    return response.data.location;
  },

  // Update location
  async updateLocation(id: number, locationData: Partial<Location>): Promise<Location> {
    const response = await api.put(`/locations/${id}`, locationData);
    return response.data.location;
  },

  // Delete location
  async deleteLocation(id: number): Promise<void> {
    await api.delete(`/locations/${id}`);
  },

  // Bulk create locations
  async bulkCreateLocations(locationsData: Partial<Location>[]): Promise<BulkCreateResponse> {
    const response = await api.post('/locations/bulk', { locations: locationsData });
    return response.data;
  },

  // Validate locations before creation
  async validateLocations(locationsData: Partial<Location>[]): Promise<ValidationResponse> {
    const response = await api.post('/locations/validate', { locations: locationsData });
    return response.data;
  },

  // Generate warehouse locations from configuration
  async generateWarehouseLocations(configData: any): Promise<{
    created_count: number;
    storage_locations: number;
    total_capacity: number;
    error_count: number;
    errors: string[];
  }> {
    const response = await api.post('/locations/generate', configData);
    return response.data;
  },

  // Export locations
  async exportLocations(warehouseId: string = 'DEFAULT', format: 'json' | 'csv' = 'json'): Promise<any> {
    const params = new URLSearchParams({
      warehouse_id: warehouseId,
      format
    });

    if (format === 'csv') {
      const response = await api.get(`/locations/export?${params.toString()}`, {
        responseType: 'blob'
      });
      return response.data;
    } else {
      const response = await api.get(`/locations/export?${params.toString()}`);
      return response.data;
    }
  }
};

// Warehouse Configuration API
export const warehouseApi = {
  // Get warehouse configuration
  async getWarehouseConfig(warehouseId: string = 'DEFAULT'): Promise<WarehouseConfig> {
    const response = await api.get(`/warehouse/config?warehouse_id=${warehouseId}`);
    return response.data.config;
  },

  // Create warehouse configuration
  async createWarehouseConfig(configData: Partial<WarehouseConfig>): Promise<WarehouseConfig> {
    const response = await api.post('/warehouse/config', configData);
    return response.data.config;
  },

  // Update warehouse configuration
  async updateWarehouseConfig(id: number, configData: Partial<WarehouseConfig>): Promise<WarehouseConfig> {
    const response = await api.put(`/warehouse/config/${id}`, configData);
    return response.data.config;
  },

  // Complete warehouse setup (wizard)
  async setupWarehouse(setupData: WarehouseSetupData): Promise<WarehouseSetupResponse> {
    const response = await api.post('/warehouse/setup', setupData);
    return response.data;
  },

  // Validate warehouse configuration
  async validateWarehouseConfig(configData: any): Promise<{
    valid: boolean;
    errors: string[];
    warnings: string[];
    calculations: {
      total_storage_locations: number;
      total_storage_capacity: number;
      receiving_capacity: number;
      total_capacity: number;
      estimated_setup_time_minutes: number;
    };
  }> {
    const response = await api.post('/warehouse/validate', configData);
    return response.data;
  },

  // Preview warehouse setup
  async previewWarehouseSetup(configData: any): Promise<{
    warehouse_structure: {
      num_aisles: number;
      racks_per_aisle: number;
      positions_per_rack: number;
      levels_per_position: number;
      level_names: string;
    };
    sample_locations: Array<{
      code: string;
      full_address: string;
      aisle: number;
      rack: number;
      position: number;
      level: string;
    }>;
    totals: {
      storage_locations: number;
      receiving_areas: number;
      staging_areas: number;
      total_locations: number;
    };
    special_areas: {
      receiving: any[];
      staging: any[];
    };
  }> {
    const response = await api.post('/warehouse/preview', configData);
    return response.data.preview;
  },

  // List user's warehouses
  async listWarehouses(): Promise<{
    warehouses: Array<WarehouseConfig & { location_count: number }>;
    total_count: number;
  }> {
    const response = await api.get('/warehouse/list');
    return response.data;
  }
};

// Template Management API
export const templateApi = {
  // Get templates
  async getTemplates(
    scope: 'my' | 'public' | 'all' = 'all',
    search: string = '',
    page: number = 1,
    perPage: number = 20
  ): Promise<{
    templates: WarehouseTemplate[];
    pagination: {
      page: number;
      per_page: number;
      total: number;
      pages: number;
      has_next: boolean;
      has_prev: boolean;
    };
    summary: {
      my_templates: number;
      public_templates: number;
      scope: string;
    };
  }> {
    const params = new URLSearchParams({
      scope,
      page: page.toString(),
      per_page: perPage.toString(),
    });

    if (search) params.append('search', search);

    const response = await api.get(`/templates?${params.toString()}`);
    return response.data;
  },

  // Get single template
  async getTemplate(id: number): Promise<WarehouseTemplate> {
    const response = await api.get(`/templates/${id}`);
    return response.data.template;
  },

  // Get template by shareable code
  async getTemplateByCode(templateCode: string): Promise<WarehouseTemplate> {
    const response = await api.get(`/templates/by-code/${templateCode}`);
    return response.data.template;
  },

  // Create template
  async createTemplate(templateData: Partial<WarehouseTemplate>): Promise<WarehouseTemplate> {
    const response = await api.post('/templates', templateData);
    return response.data.template;
  },

  // Create template from existing warehouse configuration
  async createTemplateFromConfig(
    configId: number,
    templateName: string,
    description?: string,
    isPublic: boolean = false
  ): Promise<WarehouseTemplate> {
    const response = await api.post('/templates/from-config', {
      config_id: configId,
      template_name: templateName,
      template_description: description,
      is_public: isPublic
    });
    return response.data.template;
  },

  // Update template
  async updateTemplate(id: number, templateData: Partial<WarehouseTemplate>): Promise<WarehouseTemplate> {
    const response = await api.put(`/templates/${id}`, templateData);
    return response.data.template;
  },

  // Delete template
  async deleteTemplate(id: number): Promise<void> {
    await api.delete(`/templates/${id}`);
  },

  // Apply template
  async applyTemplate(
    templateId: number,
    warehouseId?: string,
    warehouseName?: string,
    generateLocations: boolean = true
  ): Promise<{
    message: string;
    warehouse_id: string;
    configuration: WarehouseConfig;
    template_code: string;
    locations_to_generate: boolean;
  }> {
    const response = await api.post(`/templates/${templateId}/apply`, {
      warehouse_id: warehouseId,
      warehouse_name: warehouseName,
      generate_locations: generateLocations
    });
    return response.data;
  },

  // Apply template by code
  async applyTemplateByCode(
    templateCode: string,
    warehouseId?: string,
    warehouseName?: string
  ): Promise<{
    message: string;
    warehouse_id: string;
    configuration: WarehouseConfig;
    template: WarehouseTemplate;
  }> {
    const response = await api.post('/templates/apply-by-code', {
      template_code: templateCode,
      warehouse_id: warehouseId,
      warehouse_name: warehouseName
    });
    return response.data;
  },

  // Preview template
  async previewTemplate(templateId: number): Promise<{
    template: WarehouseTemplate;
    calculations: {
      total_storage_locations: number;
      total_storage_capacity: number;
      receiving_capacity: number;
      total_capacity: number;
    };
    sample_locations: Array<{
      code: string;
      full_address: string;
    }>;
    special_areas: {
      receiving: any[];
    };
  }> {
    const response = await api.get(`/templates/${templateId}/preview`);
    return response.data.preview;
  },

  // Get popular public templates
  async getPopularTemplates(limit: number = 10): Promise<{
    templates: WarehouseTemplate[];
    count: number;
  }> {
    const params = new URLSearchParams({
      limit: limit.toString()
    });

    const response = await api.get(`/templates/popular?${params.toString()}`);
    return response.data;
  }
};

// Export all APIs as a combined object
export const locationApis = {
  ...locationApi,
  warehouse: warehouseApi,
  templates: templateApi
};