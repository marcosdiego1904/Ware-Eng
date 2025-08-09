import { create } from 'zustand';
import { devtools } from 'zustand/middleware';

// Types for the location management system
export interface Location {
  id: number;
  code: string;
  pattern?: string;
  location_type: 'RECEIVING' | 'STORAGE' | 'STAGING' | 'DOCK';
  capacity: number;
  allowed_products: string[];
  zone: string;
  warehouse_id: string;
  aisle_number?: number;
  rack_number?: number;
  position_number?: number;
  level?: string;
  pallet_capacity: number;
  location_hierarchy: Record<string, any>;
  special_requirements: Record<string, any>;
  is_storage_location: boolean;
  full_address: string;
  is_active: boolean;
  created_at: string;
  created_by?: number;
  creator_username?: string;
}

export interface WarehouseConfig {
  id: number;
  warehouse_id: string;
  warehouse_name: string;
  num_aisles: number;
  racks_per_aisle: number;
  positions_per_rack: number;
  levels_per_position: number;
  level_names: string;
  default_pallet_capacity: number;
  bidimensional_racks: boolean;
  receiving_areas: ReceivingArea[];
  staging_areas: SpecialArea[];
  dock_areas: SpecialArea[];
  default_zone: string;
  position_numbering_start: number;
  position_numbering_split: boolean;
  total_storage_locations: number;
  total_capacity: number;
  created_by: number;
  creator_username?: string;
  created_at: string;
  updated_at: string;
  is_active: boolean;
}

export interface ReceivingArea {
  code: string;
  type: string;
  capacity: number;
  zone: string;
  special_requirements?: Record<string, any>;
}

export interface SpecialArea {
  code: string;
  type: string;
  capacity: number;
  zone: string;
}

export interface WarehouseTemplate {
  id: number;
  name: string;
  description?: string;
  template_code: string;
  num_aisles: number;
  racks_per_aisle: number;
  positions_per_rack: number;
  levels_per_position: number;
  level_names: string;
  default_pallet_capacity: number;
  bidimensional_racks: boolean;
  receiving_areas_template: ReceivingArea[];
  based_on_config_id?: number;
  is_public: boolean;
  usage_count: number;
  created_by: number;
  creator_username?: string;
  created_at: string;
  updated_at: string;
  is_active: boolean;
  is_applied?: boolean;
  applied_warehouse_id?: string;
}

export interface LocationFilters {
  warehouse_id?: string;
  location_type?: string;
  zone?: string;
  is_active?: boolean;
  aisle_number?: number;
  search?: string;
}

export interface LocationsPagination {
  page: number;
  per_page: number;
  total: number;
  pages: number;
  has_next: boolean;
  has_prev: boolean;
}

export interface LocationsSummary {
  total_locations: number;
  storage_locations: number;
  total_capacity: number;
  warehouse_id: string;
}

interface LocationStore {
  // State
  locations: Location[];
  currentWarehouseConfig: WarehouseConfig | null;
  templates: WarehouseTemplate[];
  
  // Loading states
  loading: boolean;
  locationsLoading: boolean;
  configLoading: boolean;
  templatesLoading: boolean;
  
  // Pagination and filtering
  pagination: LocationsPagination | null;
  summary: LocationsSummary | null;
  filters: LocationFilters;
  
  // Error handling
  error: string | null;
  
  // Actions - Location Management
  fetchLocations: (filters?: LocationFilters, page?: number, perPage?: number) => Promise<void>;
  createLocation: (locationData: Partial<Location>) => Promise<Location>;
  updateLocation: (id: number, locationData: Partial<Location>) => Promise<Location>;
  deleteLocation: (id: number) => Promise<void>;
  bulkCreateLocations: (locationsData: Partial<Location>[]) => Promise<{ created_count: number; errors: string[] }>;
  validateLocations: (locationsData: Partial<Location>[]) => Promise<any>;
  
  // Actions - Warehouse Configuration
  fetchWarehouseConfig: (warehouseId?: string) => Promise<void>;
  createWarehouseConfig: (configData: Partial<WarehouseConfig>) => Promise<WarehouseConfig>;
  updateWarehouseConfig: (id: number, configData: Partial<WarehouseConfig>) => Promise<WarehouseConfig>;
  setupWarehouse: (setupData: any) => Promise<{ warehouse_id: string; configuration: WarehouseConfig; locations_created: number }>;
  validateWarehouseConfig: (configData: any) => Promise<any>;
  previewWarehouseSetup: (configData: any) => Promise<any>;
  generateWarehouseLocations: (configData: any) => Promise<{ created_count: number; total_capacity: number }>;
  
  // Actions - Template Management
  fetchTemplates: (scope?: 'my' | 'public' | 'all', search?: string) => Promise<void>;
  createTemplate: (templateData: Partial<WarehouseTemplate>) => Promise<WarehouseTemplate>;
  createTemplateFromConfig: (configId: number, templateName: string, description?: string, isPublic?: boolean) => Promise<WarehouseTemplate>;
  updateTemplate: (id: number, templateData: Partial<WarehouseTemplate>) => Promise<WarehouseTemplate>;
  deleteTemplate: (id: number) => Promise<void>;
  applyTemplate: (templateId: number, warehouseId?: string, warehouseName?: string, generateLocations?: boolean) => Promise<any>;
  applyTemplateByCode: (templateCode: string, warehouseId?: string, warehouseName?: string) => Promise<any>;
  previewTemplate: (templateId: number) => Promise<any>;
  
  // Utility actions
  setFilters: (filters: LocationFilters) => void;
  clearError: () => void;
  resetStore: () => void;
}

const useLocationStore = create<LocationStore>()(
  devtools(
    (set, get) => ({
      // Initial state
      locations: [],
      currentWarehouseConfig: null,
      templates: [],
      
      loading: false,
      locationsLoading: false,
      configLoading: false,
      templatesLoading: false,
      
      pagination: null,
      summary: null,
      filters: {},
      
      error: null,
      
      // Location Management Actions
      fetchLocations: async (filters = {}, page = 1, perPage = 50) => {
        console.log('fetchLocations called with:', { filters, page, perPage });
        set({ locationsLoading: true, error: null });
        
        try {
          const { api } = await import('./api');
          
          const params = new URLSearchParams({
            page: page.toString(),
            per_page: perPage.toString(),
            ...Object.entries(filters).reduce((acc, [key, value]) => {
              if (value !== undefined && value !== '') {
                acc[key] = value.toString();
              }
              return acc;
            }, {} as Record<string, string>)
          });
          
          console.log('API request URL:', `/locations?${params}`);
          const response = await api.get(`/locations?${params}`);
          console.log('API response:', response.data);
          
          set({
            locations: response.data.locations,
            pagination: response.data.pagination,
            summary: response.data.summary,
            filters,
            locationsLoading: false
          });
          
        } catch (error: any) {
          console.error('Error fetching locations:', error);
          set({ 
            error: error.response?.data?.error || 'Failed to fetch locations',
            locationsLoading: false 
          });
        }
      },
      
      createLocation: async (locationData) => {
        set({ loading: true, error: null });
        
        try {
          const { api } = await import('./api');
          const response = await api.post('/locations', locationData);
          
          const newLocation = response.data.location;
          
          // Add to current locations if we're viewing the same warehouse
          const { locations, filters } = get();
          if (!filters.warehouse_id || filters.warehouse_id === newLocation.warehouse_id) {
            set({ locations: [...locations, newLocation] });
          }
          
          set({ loading: false });
          return newLocation;
          
        } catch (error: any) {
          console.error('Error creating location:', error);
          set({ 
            error: error.response?.data?.error || 'Failed to create location',
            loading: false 
          });
          throw error;
        }
      },
      
      updateLocation: async (id, locationData) => {
        set({ loading: true, error: null });
        
        try {
          const { api } = await import('./api');
          const response = await api.put(`/locations/${id}`, locationData);
          
          const updatedLocation = response.data.location;
          
          // Update in current locations
          set(state => ({
            locations: state.locations.map(loc => 
              loc.id === id ? updatedLocation : loc
            ),
            loading: false
          }));
          
          return updatedLocation;
          
        } catch (error: any) {
          console.error('Error updating location:', error);
          set({ 
            error: error.response?.data?.error || 'Failed to update location',
            loading: false 
          });
          throw error;
        }
      },
      
      deleteLocation: async (id) => {
        set({ loading: true, error: null });
        
        try {
          const { api } = await import('./api');
          await api.delete(`/locations/${id}`);
          
          // Remove from current locations
          set(state => ({
            locations: state.locations.filter(loc => loc.id !== id),
            loading: false
          }));
          
        } catch (error: any) {
          console.error('Error deleting location:', error);
          set({ 
            error: error.response?.data?.error || 'Failed to delete location',
            loading: false 
          });
          throw error;
        }
      },
      
      bulkCreateLocations: async (locationsData) => {
        set({ loading: true, error: null });
        
        try {
          const { api } = await import('./api');
          const response = await api.post('/locations/bulk', { locations: locationsData });
          
          const { created_count, errors, created_locations } = response.data;
          
          // Add created locations to current list
          if (created_locations && created_locations.length > 0) {
            set(state => ({
              locations: [...state.locations, ...created_locations]
            }));
          }
          
          set({ loading: false });
          return { created_count, errors };
          
        } catch (error: any) {
          console.error('Error bulk creating locations:', error);
          set({ 
            error: error.response?.data?.error || 'Failed to bulk create locations',
            loading: false 
          });
          throw error;
        }
      },
      
      validateLocations: async (locationsData) => {
        try {
          const { api } = await import('./api');
          const response = await api.post('/locations/validate', { locations: locationsData });
          return response.data;
          
        } catch (error: any) {
          console.error('Error validating locations:', error);
          throw error;
        }
      },
      
      // Warehouse Configuration Actions
      fetchWarehouseConfig: async (warehouseId = 'DEFAULT') => {
        set({ configLoading: true, error: null });
        
        try {
          const { api } = await import('./api');
          const response = await api.get(`/warehouse/config?warehouse_id=${warehouseId}`);
          
          set({
            currentWarehouseConfig: response.data.config,
            configLoading: false
          });
          
        } catch (error: any) {
          console.error('Error fetching warehouse config:', error);
          if (error.response?.status === 404) {
            // No config found - this is normal for new warehouses
            set({ currentWarehouseConfig: null, configLoading: false });
          } else {
            set({ 
              error: error.response?.data?.error || 'Failed to fetch warehouse configuration',
              configLoading: false 
            });
          }
        }
      },
      
      createWarehouseConfig: async (configData) => {
        set({ loading: true, error: null });
        
        try {
          const { api } = await import('./api');
          const response = await api.post('/warehouse/config', configData);
          
          const newConfig = response.data.config;
          
          set({
            currentWarehouseConfig: newConfig,
            loading: false
          });
          
          return newConfig;
          
        } catch (error: any) {
          console.error('Error creating warehouse config:', error);
          set({ 
            error: error.response?.data?.error || 'Failed to create warehouse configuration',
            loading: false 
          });
          throw error;
        }
      },
      
      setupWarehouse: async (setupData) => {
        set({ loading: true, error: null });
        
        try {
          const { api } = await import('./api');
          const response = await api.post('/warehouse/setup', setupData);
          
          const { warehouse_id, configuration, locations_created } = response.data;
          
          set({
            currentWarehouseConfig: configuration,
            loading: false
          });
          
          // Refresh locations if they were generated
          if (locations_created > 0) {
            await get().fetchLocations({ warehouse_id });
          }
          
          return response.data;
          
        } catch (error: any) {
          console.error('Error setting up warehouse:', error);
          set({ 
            error: error.response?.data?.error || 'Failed to setup warehouse',
            loading: false 
          });
          throw error;
        }
      },
      
      validateWarehouseConfig: async (configData) => {
        try {
          const { api } = await import('./api');
          const response = await api.post('/warehouse/validate', configData);
          return response.data;
          
        } catch (error: any) {
          console.error('Error validating warehouse config:', error);
          throw error;
        }
      },
      
      previewWarehouseSetup: async (configData) => {
        try {
          const { api } = await import('./api');
          const response = await api.post('/warehouse/preview', configData);
          return response.data.preview;
          
        } catch (error: any) {
          console.error('Error previewing warehouse setup:', error);
          throw error;
        }
      },
      
      generateWarehouseLocations: async (configData) => {
        set({ loading: true, error: null });
        
        try {
          const { api } = await import('./api');
          const response = await api.post('/locations/generate', configData);
          
          // Refresh locations after generation
          if (configData.warehouse_id) {
            await get().fetchLocations({ warehouse_id: configData.warehouse_id });
          }
          
          set({ loading: false });
          return response.data;
          
        } catch (error: any) {
          console.error('Error generating warehouse locations:', error);
          set({ 
            error: error.response?.data?.error || 'Failed to generate warehouse locations',
            loading: false 
          });
          throw error;
        }
      },
      
      // Template Management Actions
      fetchTemplates: async (scope = 'all', search = '') => {
        set({ templatesLoading: true, error: null });
        
        try {
          const { api } = await import('./api');
          
          const params = new URLSearchParams({ scope });
          if (search) params.append('search', search);
          
          const response = await api.get(`/templates?${params}`);
          
          set({
            templates: response.data.templates,
            templatesLoading: false
          });
          
        } catch (error: any) {
          console.error('Error fetching templates:', error);
          set({ 
            error: error.response?.data?.error || 'Failed to fetch templates',
            templatesLoading: false 
          });
        }
      },
      
      createTemplate: async (templateData) => {
        set({ loading: true, error: null });
        
        try {
          const { api } = await import('./api');
          const response = await api.post('/templates', templateData);
          
          const newTemplate = response.data.template;
          
          set(state => ({
            templates: [...state.templates, newTemplate],
            loading: false
          }));
          
          return newTemplate;
          
        } catch (error: any) {
          console.error('Error creating template:', error);
          set({ 
            error: error.response?.data?.error || 'Failed to create template',
            loading: false 
          });
          throw error;
        }
      },
      
      createTemplateFromConfig: async (configId, templateName, description, isPublic = false) => {
        set({ loading: true, error: null });
        
        try {
          const { api } = await import('./api');
          const response = await api.post('/templates/from-config', {
            config_id: configId,
            template_name: templateName,
            template_description: description,
            is_public: isPublic
          });
          
          const newTemplate = response.data.template;
          
          set(state => ({
            templates: [...state.templates, newTemplate],
            loading: false
          }));
          
          return newTemplate;
          
        } catch (error: any) {
          console.error('Error creating template from config:', error);
          set({ 
            error: error.response?.data?.error || 'Failed to create template from configuration',
            loading: false 
          });
          throw error;
        }
      },
      
      updateTemplate: async (id, templateData) => {
        set({ loading: true, error: null });
        
        try {
          const { api } = await import('./api');
          const response = await api.put(`/templates/${id}`, templateData);
          
          const updatedTemplate = response.data.template;
          
          set(state => ({
            templates: state.templates.map(template => 
              template.id === id ? updatedTemplate : template
            ),
            loading: false
          }));
          
          return updatedTemplate;
          
        } catch (error: any) {
          console.error('Error updating template:', error);
          set({ 
            error: error.response?.data?.error || 'Failed to update template',
            loading: false 
          });
          throw error;
        }
      },
      
      deleteTemplate: async (id) => {
        set({ loading: true, error: null });
        
        try {
          const { api } = await import('./api');
          await api.delete(`/templates/${id}`);
          
          set(state => ({
            templates: state.templates.filter(template => template.id !== id),
            loading: false
          }));
          
        } catch (error: any) {
          console.error('Error deleting template:', error);
          set({ 
            error: error.response?.data?.error || 'Failed to delete template',
            loading: false 
          });
          throw error;
        }
      },
      
      applyTemplate: async (templateId, warehouseId, warehouseName, generateLocations = true) => {
        set({ loading: true, error: null });
        
        try {
          const { api } = await import('./api');
          const response = await api.post(`/templates/${templateId}/apply`, {
            warehouse_id: warehouseId,
            warehouse_name: warehouseName,
            generate_locations: generateLocations
          });
          
          const { configuration } = response.data;
          
          set({
            currentWarehouseConfig: configuration,
            loading: false
          });
          
          return response.data;
          
        } catch (error: any) {
          console.error('Error applying template:', error);
          set({ 
            error: error.response?.data?.error || 'Failed to apply template',
            loading: false 
          });
          throw error;
        }
      },
      
      applyTemplateByCode: async (templateCode, warehouseId, warehouseName) => {
        set({ loading: true, error: null });
        
        try {
          const { api } = await import('./api');
          const response = await api.post('/templates/apply-by-code', {
            template_code: templateCode,
            warehouse_id: warehouseId,
            warehouse_name: warehouseName
          });
          
          const { configuration } = response.data;
          
          set({
            currentWarehouseConfig: configuration,
            loading: false
          });
          
          return response.data;
          
        } catch (error: any) {
          console.error('Error applying template by code:', error);
          set({ 
            error: error.response?.data?.error || 'Failed to apply template',
            loading: false 
          });
          throw error;
        }
      },
      
      previewTemplate: async (templateId) => {
        try {
          const { api } = await import('./api');
          const response = await api.get(`/templates/${templateId}/preview`);
          return response.data.preview;
          
        } catch (error: any) {
          console.error('Error previewing template:', error);
          throw error;
        }
      },
      
      updateWarehouseConfig: async (id, configData) => {
        set({ loading: true, error: null });
        
        try {
          const { api } = await import('./api');
          const response = await api.put(`/warehouse/config/${id}`, configData);
          
          const updatedConfig = response.data.configuration;
          
          set({
            currentWarehouseConfig: updatedConfig,
            loading: false
          });
          
          return updatedConfig;
          
        } catch (error: any) {
          console.error('Error updating warehouse config:', error);
          set({ 
            error: error.response?.data?.error || 'Failed to update warehouse configuration',
            loading: false 
          });
          throw error;
        }
      },
      
      // Utility Actions
      setFilters: (filters) => {
        set({ filters });
      },
      
      clearError: () => {
        set({ error: null });
      },
      
      resetStore: () => {
        set({
          locations: [],
          currentWarehouseConfig: null,
          templates: [],
          loading: false,
          locationsLoading: false,
          configLoading: false,
          templatesLoading: false,
          pagination: null,
          summary: null,
          filters: {},
          error: null
        });
      }
    }),
    {
      name: 'location-store'
    }
  )
);

export default useLocationStore;