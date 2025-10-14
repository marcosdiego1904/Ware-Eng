import { create } from 'zustand';
import { devtools } from 'zustand/middleware';

// Types for the location management system
export interface Location {
  id: number;
  code: string;
  pattern?: string;
  location_type: 'RECEIVING' | 'STORAGE' | 'STAGING' | 'DOCK' | 'TRANSITIONAL';
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
  staging_areas_template: SpecialArea[];
  dock_areas_template: SpecialArea[];
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

  // Actions
  setLoading: (loading: boolean) => void;
  setError: (error: string | null) => void;
  
  // Actions - Location Management
  fetchLocations: (filters?: LocationFilters, page?: number, perPage?: number) => Promise<void>;
  createLocation: (locationData: Partial<Location>) => Promise<Location>;
  updateLocation: (id: number, locationData: Partial<Location>) => Promise<Location>;
  deleteLocation: (id: number) => Promise<void>;
  bulkCreateLocations: (locationsData: Partial<Location>[]) => Promise<{ created_count: number; errors: string[] }>;
  validateLocations: (locationsData: Partial<Location>[]) => Promise<any>;
  bulkCreateLocationRange: (rangeData: any) => Promise<{ created_count: number; errors: string[]; warnings: string[] }>;
  previewLocationRange: (rangeData: any) => Promise<{ location_codes: string[]; duplicates: string[]; warnings: string[] }>;
  
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

      // Actions
      setLoading: (loading) => set({ loading }),
      setError: (error) => set({ error }),
      
      // Location Management Actions
      fetchLocations: async (filters = {}, page = 1, perPage = 100) => {
        console.log('🚀 fetchLocations called with:', { filters, page, perPage });
        
        // Enhanced race condition protection with parameter checking
        const currentState = get();
        const requestKey = JSON.stringify({ filters, page, perPage });
        
        if (currentState.locationsLoading) {
          console.log('⏸️ Skipping fetchLocations - already loading');
          return;
        }
        
        // Store the request key to prevent duplicate requests
        const lastRequestKey = (currentState as any)._lastRequestKey;
        if (lastRequestKey === requestKey) {
          console.log('⏸️ Skipping fetchLocations - same request already processed');
          return;
        }
        
        console.log('📊 Current store state:', {
          locationsCount: currentState.locations.length,
          loading: currentState.locationsLoading,
          error: currentState.error
        });
        
        set({ locationsLoading: true, error: null, _lastRequestKey: requestKey } as any);
        
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
          
          console.log('🌐 API request URL:', `/locations?${params}`);
          console.log('🔑 Auth token exists:', !!localStorage.getItem('token'));
          
          const response = await api.get(`/locations?${params}`);
          
          console.log('✅ API response received:', {
            status: response.status,
            dataKeys: Object.keys(response.data),
            locationsCount: response.data.locations?.length || 0
          });
          
          const locations = response.data.locations || [];
          const pagination = response.data.pagination || null;
          const summary = response.data.summary || null;

          const specialLocations = locations.filter((loc: any) => 
            ['RECEIVING', 'STAGING', 'DOCK', 'TRANSITIONAL'].includes(loc.location_type)
          );
          
          console.log('🏢 Locations analysis:', {
            totalLocations: locations.length,
            specialLocations: specialLocations.length,
            specialDetails: specialLocations.map((loc: any) => ({
              code: loc.code,
              type: loc.location_type,
              zone: loc.zone
            }))
          });
          
          set({
            locations,
            pagination,
            summary,
            filters,
            locationsLoading: false,
            _lastRequestKey: undefined
          } as any);
          
        } catch (error: any) {
          console.error('Error fetching locations:', error);
          set({ 
            error: error.response?.data?.error || 'Failed to fetch locations',
            locationsLoading: false,
            _lastRequestKey: undefined
          } as any);
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
          
          // Enhanced debugging for the 404 issue
          console.log('🔧 updateLocation called with:', { id, locationData });
          console.log('🌐 Making API call to:', `PUT /locations/${id}`);
          
          const response = await api.put(`/locations/${id}`, locationData);
          console.log('✅ API call successful:', response.data);
          
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
          console.error('❌ Location update failed:', error);
          console.error('   Error details:', {
            status: error.response?.status,
            statusText: error.response?.statusText,
            url: error.config?.url,
            method: error.config?.method,
            headers: error.config?.headers,
            data: error.response?.data
          });
          
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

      bulkCreateLocationRange: async (rangeData) => {
        set({ loading: true, error: null });

        try {
          const { locationApi } = await import('./location-api');
          const response = await locationApi.bulkCreateLocationRange(rangeData);

          const { created_count, errors, warnings, created_locations } = response;

          // Add created locations to current list
          if (created_locations && created_locations.length > 0) {
            set(state => ({
              locations: [...state.locations, ...created_locations]
            }));
          }

          set({ loading: false });
          return { created_count, errors, warnings };

        } catch (error: any) {
          console.error('Error bulk creating location range:', error);
          set({
            error: error.response?.data?.error || 'Failed to bulk create location range',
            loading: false
          });
          throw error;
        }
      },

      previewLocationRange: async (rangeData) => {
        try {
          const { locationApi } = await import('./location-api');
          const response = await locationApi.previewLocationRange(rangeData);
          return response;

        } catch (error: any) {
          console.error('Error previewing location range:', error);
          throw error;
        }
      },
      
      // Warehouse Configuration Actions
      fetchWarehouseConfig: async (warehouseId = 'DEFAULT') => {
        console.log('[STORE] fetchWarehouseConfig called for:', warehouseId);
        set({ configLoading: true, error: null });

        try {
          const { api } = await import('./api');
          const response = await api.get(`/warehouse/config?warehouse_id=${warehouseId}`);

          console.log('[STORE] fetchWarehouseConfig response:', response.data);

          set({
            currentWarehouseConfig: response.data.config,
            configLoading: false
          });

          console.log('[STORE] currentWarehouseConfig updated:', response.data.config);

        } catch (error: any) {
          console.error('[STORE] Error fetching warehouse config:', error);
          if (error.response?.status === 404) {
            // No config found - this is normal for new warehouses
            console.log('[STORE] Config not found (404), setting to null');
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
      fetchTemplates: async (scope = 'my', search = '') => {
        console.log('[STORE] fetchTemplates called:', { scope, search });
        set({ templatesLoading: true, error: null });

        try {
          const { api } = await import('./api');

          const params = new URLSearchParams({ scope });
          if (search) params.append('search', search);

          console.log('[STORE] Fetching templates from:', `/templates?${params}`);
          const response = await api.get(`/templates?${params}`);

          console.log('[STORE] Templates response:', response.data);
          console.log('[STORE] Number of templates returned:', response.data.templates?.length || 0);

          set({
            templates: response.data.templates,
            templatesLoading: false
          });

        } catch (error: any) {
          console.error('[STORE] Error fetching templates:', error);
          console.error('[STORE] Error details:', error.response?.data);
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
          
          // Reload locations after template is applied (ALWAYS, not just when generating)
          console.log('🔄 Template applied, reloading locations...');
          if (warehouseId) {
            // Clear existing locations to force fresh load
            set({ locations: [] });
            const filters = { warehouse_id: warehouseId };
            await get().fetchLocations(filters, 1, 100);
          }
          
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
        console.log('[STORE] applyTemplateByCode called:', { templateCode, warehouseId, warehouseName });
        set({ loading: true, error: null });

        try {
          const { api } = await import('./api');
          const response = await api.post('/templates/apply-by-code', {
            template_code: templateCode,
            warehouse_id: warehouseId,
            warehouse_name: warehouseName
          });

          console.log('[STORE] applyTemplateByCode response:', response.data);
          const { configuration } = response.data;
          console.log('[STORE] Extracted configuration:', configuration);

          set({
            currentWarehouseConfig: configuration,
            loading: false
          });

          console.log('[STORE] currentWarehouseConfig updated in state');

          // Reload locations after template is applied by code
          console.log('🔄 Template applied by code, reloading locations...');
          if (warehouseId) {
            // Clear existing locations to force fresh load
            set({ locations: [] });
            const filters = { warehouse_id: warehouseId };
            await get().fetchLocations(filters, 1, 100);
          }

          console.log('[STORE] Returning response.data with configuration');
          return response.data;

        } catch (error: any) {
          console.error('[STORE] Error applying template by code:', error);
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
          const locationsRegenerated = response.data.locations_regenerated;
          
          set({
            currentWarehouseConfig: updatedConfig,
            loading: false
          });

          // If locations were regenerated, refresh the locations list with reasonable pagination
          if (locationsRegenerated) {
            await get().fetchLocations({ warehouse_id: updatedConfig.warehouse_id }, 1, 100);
          }
          
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