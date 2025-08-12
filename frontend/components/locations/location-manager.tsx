'use client';

import React, { useState, useEffect, useCallback, useRef } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Badge } from '@/components/ui/badge';
import { Label } from '@/components/ui/label';
import { Switch } from '@/components/ui/switch';
import { Alert, AlertDescription } from '@/components/ui/alert';
import { LocationList } from './location-list';
import { LocationForm } from './location-form';
import { LocationImportExport } from './location-import-export';
import { WarehouseSetupWizard } from './setup-wizard/warehouse-wizard';
import { SimplifiedReconfigureWizard } from './setup-wizard/simplified-reconfigure-wizard';
import { EnhancedTemplateManagerV2 } from './templates/enhanced-template-manager-v2';
import useLocationStore, { Location } from '@/lib/location-store';
import { useDebounce } from '@/hooks/useDebounce';
import { useToast } from '@/hooks/use-toast';
import { 
  Plus, 
  Search, 
 
  Settings, 
  Building2, 
  Package,
  AlertCircle,
  Loader2,
  Edit,
  Save,
  X
} from 'lucide-react';

interface LocationManagerProps {
  warehouseId?: string;
}

export function LocationManager({ warehouseId = 'DEFAULT' }: LocationManagerProps) {
  const {
    locations,
    currentWarehouseConfig,
    templates,
    locationsLoading,
    configLoading,
    error,
    fetchLocations,
    fetchWarehouseConfig,
    fetchTemplates,
    updateWarehouseConfig,
    setFilters,
    clearError,
    resetStore
  } = useLocationStore();

  const { toast } = useToast();
  
  // Cleanup flag to prevent state updates after unmount
  const isMountedRef = useRef(true);
  const [activeTab, setActiveTab] = useState('locations');
  const [locationSearchCode, setLocationSearchCode] = useState('');
  const debouncedSearchCode = useDebounce(locationSearchCode, 500); // 500ms debounce
  const [showLocationForm, setShowLocationForm] = useState(false);
  const [showSetupWizard, setShowSetupWizard] = useState(false);
  const [showReconfigureWizard, setShowReconfigureWizard] = useState(false);
  const [editingLocation, setEditingLocation] = useState<Location | null>(null);
  const [searchingLocation, setSearchingLocation] = useState(false);
  const [searchWarnings, setSearchWarnings] = useState<string[]>([]);
  
  // Settings form state
  const [isEditingSettings, setIsEditingSettings] = useState(false);
  const [settingsFormData, setSettingsFormData] = useState({
    warehouse_name: '',
    num_aisles: 0,
    racks_per_aisle: 0,
    positions_per_rack: 0,
    levels_per_position: 0,
    level_names: '',
    default_pallet_capacity: 0,
    bidimensional_racks: false
  });

  // Cleanup on unmount
  useEffect(() => {
    return () => {
      isMountedRef.current = false;
      clearError(); // Clear any existing errors
    };
  }, [clearError]);

  // Validate location search code for common issues
  const validateLocationSearchCode = useCallback((searchCode: string) => {
    const warnings: string[] = [];
    
    if (!searchCode.trim()) {
      setSearchWarnings([]);
      return;
    }
    
    // Check for potentially non-existent location patterns
    if (searchCode.length > 0) {
      // Check for common invalid patterns
      if (searchCode.match(/^\d+$/)) {
        // Pure numbers (likely invalid)
        if (parseInt(searchCode) > 9999) {
          warnings.push('⚠️ Location code seems too large. Typical codes are like "001A" or "01-02-015C"');
        } else if (parseInt(searchCode) > 999) {
          warnings.push('💡 Did you mean a location like "' + searchCode.slice(0,3) + 'A" instead?');
        }
      }
      
      // Check for suspicious patterns that don't match warehouse structure
      if (searchCode.match(/^[A-Z]+$/)) {
        warnings.push('💡 Location codes typically contain numbers. Try formats like "001A" or "RECEIVING"');
      }
      
      // Check for non-standard formats
      if (!searchCode.match(/^(\d{1,3}[A-Z]?|[A-Z]+|\d{2}-\d{2}-\d{3}[A-Z]|[A-Z_]+)$/i)) {
        warnings.push('🤔 Unusual format. Common formats: "001A", "01-02-015C", "RECEIVING"');
      }
      
      // Check for potentially impossible warehouse codes based on current config
      if (currentWarehouseConfig) {
        const match = searchCode.match(/^(\d+)([A-Z])?$/);
        if (match) {
          const position = parseInt(match[1]);
          const level = match[2];
          
          if (position > currentWarehouseConfig.positions_per_rack) {
            warnings.push(`⚠️ Position ${position} exceeds warehouse maximum (${currentWarehouseConfig.positions_per_rack})`);
          }
          
          if (level && !currentWarehouseConfig.level_names.includes(level)) {
            warnings.push(`⚠️ Level "${level}" not valid. Available: ${currentWarehouseConfig.level_names.split('').join(', ')}`);
          }
        }
      }
      
      // Helpful suggestions
      if (searchCode.length === 1) {
        warnings.push('💡 Try adding position number, e.g., "001A" or search for "RECEIVING"');
      }
    }
    
    setSearchWarnings(warnings);
  }, [currentWarehouseConfig]);

  // Load initial data with abort controller to prevent race conditions
  useEffect(() => {
    console.log('🚀 LocationManager useEffect triggered - loading initial data');
    console.log('🔑 Current warehouse ID:', warehouseId);
    console.log('🔑 Checking authentication...');
    const token = localStorage.getItem('token');
    const user = localStorage.getItem('user');
    console.log('🔐 Auth status:', { hasToken: !!token, hasUser: !!user });
    
    // Reset store when warehouse ID changes to prevent data contamination
    console.log('🔄 Resetting store for warehouse ID change...');
    clearError();
    
    // Clear existing locations and config to ensure fresh data for this warehouse
    if (currentWarehouseConfig?.warehouse_id !== warehouseId || locations.length > 0) {
      console.log('🗑️ Clearing stale data for new warehouse:', warehouseId);
      // Reset all store data for new warehouse to prevent contamination
      resetStore();
    }
    
    const abortController = new AbortController();
    
    const loadInitialData = async () => {
      console.log('🔄 Starting loadInitialData...');
      try {
        console.log(`📡 Fetching warehouse config for: ${warehouseId}`);
        await Promise.all([
          fetchWarehouseConfig(warehouseId),
          fetchTemplates('my')
        ]);
        
        // Force immediate location refresh to ensure special areas are loaded
        console.log('🔄 Force refreshing locations after initial load...');
        const locationFilters = { warehouse_id: warehouseId };
        await fetchLocations(locationFilters, 1, 100);
      } catch (error) {
        if (!abortController.signal.aborted && isMountedRef.current) {
          console.error('Failed to load initial data:', error);
        }
      }
    };
    
    loadInitialData();
    
    return () => {
      abortController.abort();
    };
  }, [warehouseId, fetchWarehouseConfig, fetchTemplates, fetchLocations, clearError, resetStore, currentWarehouseConfig?.warehouse_id, locations.length]);

  // Refresh locations when warehouse ID changes (but not on config loading state changes)
  useEffect(() => {
    console.log('🎯 LOCATIONS FETCH useEffect triggered for warehouse:', warehouseId);
    
    let isMounted = true;
    let timeoutId: NodeJS.Timeout;
    
    const loadLocations = async () => {
      console.log('⚡ loadLocations CALLED for warehouse:', warehouseId);
      
      // Prevent duplicate calls if already loading
      if (locationsLoading || !isMountedRef.current) {
        console.log('❌ SKIPPING FETCH - Already loading or unmounted');
        return;
      }
      
      console.log('✅ PROCEEDING with loadLocations');
      
      // Always load locations for the warehouse - this ensures special areas persist
      if (warehouseId) {
        const locationFilters = { 
          warehouse_id: warehouseId
        };
        
        console.log('🔥 CALLING fetchLocations for warehouse:', warehouseId);
        setFilters(locationFilters);
        
        try {
          await fetchLocations(locationFilters, 1, 100); // Load more to catch special locations
          console.log('✅ fetchLocations completed');
        } catch (error) {
          if (isMounted && isMountedRef.current) {
            console.error('Failed to load locations:', error);
          }
        }
      }
    };

    // Debounce to prevent rapid consecutive calls
    timeoutId = setTimeout(() => {
      if (isMounted) {
        loadLocations();
      }
    }, 100);
    
    return () => {
      isMounted = false;
      if (timeoutId) {
        clearTimeout(timeoutId);
      }
    };
  }, [warehouseId, fetchLocations, locationsLoading, setFilters]); // FIXED: Only depend on warehouseId, not configLoading

  // Note: Removed duplicate and looping useEffect to prevent race conditions

  // Populate settings form when config loads
  useEffect(() => {
    if (currentWarehouseConfig) {
      setSettingsFormData({
        warehouse_name: currentWarehouseConfig.warehouse_name || '',
        num_aisles: currentWarehouseConfig.num_aisles || 0,
        racks_per_aisle: currentWarehouseConfig.racks_per_aisle || 0,
        positions_per_rack: currentWarehouseConfig.positions_per_rack || 0,
        levels_per_position: currentWarehouseConfig.levels_per_position || 0,
        level_names: currentWarehouseConfig.level_names || '',
        default_pallet_capacity: currentWarehouseConfig.default_pallet_capacity || 0,
        bidimensional_racks: currentWarehouseConfig.bidimensional_racks || false
      });
    }
  }, [currentWarehouseConfig]);

  // Client-side filter to get only special locations
  const specialLocations = React.useMemo(() => {
    return locations.filter(location => 
      location.location_type === 'RECEIVING' || 
      location.location_type === 'STAGING' || 
      location.location_type === 'DOCK'
    );
  }, [locations]);

  // Enhanced debug logging for special areas issue
  console.log('==================================================');
  console.log('🔍 LOCATION MANAGER DEBUG');
  console.log('==================================================');
  console.log(`📊 Locations state - Total: ${locations.length}, Special: ${specialLocations.length}`);
  console.log('🏠 Current warehouse ID:', warehouseId);
  console.log('⚙️ Locations loading state:', locationsLoading);
  console.log('🔧 Config loading state:', configLoading);
  console.log('❗ Current error state:', error);
  console.log('🏢 Current warehouse config:', currentWarehouseConfig ? {
    id: currentWarehouseConfig.id,
    name: currentWarehouseConfig.warehouse_name,
    warehouse_id: currentWarehouseConfig.warehouse_id
  } : 'null');
  
  if (locations.length > 0) {
    console.log('📍 First 10 locations:', locations.slice(0, 10).map(loc => ({ 
      code: loc.code, 
      type: loc.location_type,
      warehouse_id: loc.warehouse_id,
      zone: loc.zone 
    })));
    console.log('⭐ Special locations found:', specialLocations.map(loc => ({ 
      code: loc.code, 
      type: loc.location_type, 
      zone: loc.zone,
      warehouse_id: loc.warehouse_id
    })));
    
    // Show all unique location types
    const locationTypes = [...new Set(locations.map(loc => loc.location_type))];
    console.log('📊 All location types in data:', locationTypes);
    
    // Show all unique warehouse IDs
    const warehouseIds = [...new Set(locations.map(loc => loc.warehouse_id))];
    console.log('🏢 All warehouse IDs in data:', warehouseIds);
  } else {
    console.log('❌ No locations loaded yet. Check API calls and authentication.');
  }
  
  // Debug warehouse config special areas
  if (currentWarehouseConfig) {
    console.log('Warehouse Config Debug:', {
      configId: currentWarehouseConfig.id,
      warehouseName: currentWarehouseConfig.warehouse_name,
      receivingAreas: currentWarehouseConfig.receiving_areas,
      stagingAreas: currentWarehouseConfig.staging_areas,
      dockAreas: currentWarehouseConfig.dock_areas
    });
  }

  // Search for specific location to edit (triggered by debounced search code)
  const handleLocationSearch = useCallback(async (searchCode?: string) => {
    const codeToSearch = searchCode || debouncedSearchCode;
    if (!codeToSearch.trim()) return;
    
    setSearchingLocation(true);
    try {
      // Search for the specific location by code WITHOUT replacing the main locations array
      
      console.log('🔍 Searching for location to edit:', codeToSearch);
      console.log('📊 Before search - Total locations:', locations.length, 'Special:', specialLocations.length);
      
      // Use the API directly instead of the store to avoid overwriting locations
      const { api } = await import('@/lib/api');
      const params = new URLSearchParams({
        page: '1',
        per_page: '10',
        warehouse_id: warehouseId,
        search: codeToSearch.trim()
      });
      
      console.log('🌐 Direct API search call:', `/locations?${params}`);
      const response = await api.get(`/locations?${params}`);
      const searchResults = response.data.locations || [];
      
      console.log('🔍 Search results:', searchResults.length, 'locations found');
      
      // If we find exactly one location, open it for editing immediately
      if (searchResults.length === 1) {
        const foundLocation = searchResults[0];
        console.log('Found location for editing:', foundLocation.code);
        setEditingLocation(foundLocation);
        setShowLocationForm(true);
        setLocationSearchCode(''); // Clear search
      } else if (searchResults.length === 0) {
        console.log('❌ No location found for code:', codeToSearch);
        
        // Provide helpful suggestions based on search pattern
        let suggestion = '';
        if (codeToSearch.match(/^\d+$/)) {
          suggestion = ` Try adding a level like "${codeToSearch}A" or "${codeToSearch}B".`;
        } else if (codeToSearch.match(/^[A-Z]+$/)) {
          suggestion = ' Special areas use names like "RECEIVING", "STAGING", or "DOCK".';
        } else if (codeToSearch.length < 3) {
          suggestion = ' Try a more complete code like "001A" or "01-02-015C".';
        }
        
        toast({
          title: "Location Not Found",
          description: `No location found with code: ${codeToSearch}.${suggestion}`,
          variant: "destructive",
        });
      } else {
        console.log('⚠️ Multiple locations found:', searchResults.length, 'Need more specific search');
        toast({
          title: "Multiple Locations Found",
          description: `Found ${searchResults.length} locations. Please be more specific.`,
          variant: "warning",
        });
      }
      
    } catch (error) {
      console.error('Error searching for location:', error);
    } finally {
      setSearchingLocation(false);
    }
  }, [debouncedSearchCode, warehouseId, locations.length, specialLocations.length, toast]);

  // Auto-search when debounced code changes
  useEffect(() => {
    if (debouncedSearchCode.trim()) {
      handleLocationSearch();
    }
  }, [debouncedSearchCode, handleLocationSearch]);

  // Validate search code in real-time as user types
  useEffect(() => {
    validateLocationSearchCode(locationSearchCode);
  }, [locationSearchCode, validateLocationSearchCode]);

  // Note: Removed the useEffect that watched for search results since we now handle 
  // the search results immediately in handleLocationSearch and don't overwrite the main locations array

  // Helper function to find the active template based on current warehouse config
  const findActiveTemplate = () => {
    if (!currentWarehouseConfig || !templates || templates.length === 0) {
      return null;
    }
    
    // First try to find an exact match
    const exactMatch = templates.find(template => 
      template.num_aisles === currentWarehouseConfig.num_aisles &&
      template.racks_per_aisle === currentWarehouseConfig.racks_per_aisle &&
      template.positions_per_rack === currentWarehouseConfig.positions_per_rack &&
      template.levels_per_position === currentWarehouseConfig.levels_per_position &&
      template.default_pallet_capacity === currentWarehouseConfig.default_pallet_capacity &&
      template.bidimensional_racks === currentWarehouseConfig.bidimensional_racks &&
      template.level_names === currentWarehouseConfig.level_names
    );
    
    if (exactMatch) {
      return exactMatch;
    }
    
    // If no exact match, try without level_names (they might be customized)
    const partialMatch = templates.find(template => 
      template.num_aisles === currentWarehouseConfig.num_aisles &&
      template.racks_per_aisle === currentWarehouseConfig.racks_per_aisle &&
      template.positions_per_rack === currentWarehouseConfig.positions_per_rack &&
      template.levels_per_position === currentWarehouseConfig.levels_per_position &&
      template.default_pallet_capacity === currentWarehouseConfig.default_pallet_capacity &&
      template.bidimensional_racks === currentWarehouseConfig.bidimensional_racks
    );
    
    if (partialMatch) {
      return partialMatch;
    }
    
    // Last resort: match on core structure only
    const structureMatch = templates.find(template => 
      template.num_aisles === currentWarehouseConfig.num_aisles &&
      template.racks_per_aisle === currentWarehouseConfig.racks_per_aisle &&
      template.positions_per_rack === currentWarehouseConfig.positions_per_rack &&
      template.levels_per_position === currentWarehouseConfig.levels_per_position
    );
    
    return structureMatch || null;
  };

  // Settings form handlers
  const handleEditSettings = () => {
    setIsEditingSettings(true);
  };

  const handleCancelEdit = () => {
    setIsEditingSettings(false);
    // Reset form data to current config values
    if (currentWarehouseConfig) {
      setSettingsFormData({
        warehouse_name: currentWarehouseConfig.warehouse_name || '',
        num_aisles: currentWarehouseConfig.num_aisles || 0,
        racks_per_aisle: currentWarehouseConfig.racks_per_aisle || 0,
        positions_per_rack: currentWarehouseConfig.positions_per_rack || 0,
        levels_per_position: currentWarehouseConfig.levels_per_position || 0,
        level_names: currentWarehouseConfig.level_names || '',
        default_pallet_capacity: currentWarehouseConfig.default_pallet_capacity || 0,
        bidimensional_racks: currentWarehouseConfig.bidimensional_racks || false
      });
    }
  };

  const handleSaveSettings = async () => {
    if (!currentWarehouseConfig) return;

    try {
      // Update the warehouse configuration. The store will trigger the useEffect.
      await updateWarehouseConfig(currentWarehouseConfig.id, settingsFormData);
      
      if (isMountedRef.current) {
        toast({
          title: "Configuration Updated",
          description: "Warehouse configuration updated successfully! Locations will be regenerated to match the new structure.",
          variant: "success",
        });
        setIsEditingSettings(false);
      }
      
      // Clear any existing filters that might interfere with the refresh
      const freshFilters = { warehouse_id: warehouseId };
      setFilters(freshFilters);
      
      // Fetch the updated config, which will trigger the useEffect to refresh locations.
      await fetchWarehouseConfig(warehouseId);
      await fetchTemplates('my');
      
      // Explicitly fetch first page with fresh filters for consistent behavior
      console.log('Settings updated - fetching locations with fresh filters');
      await fetchLocations(freshFilters, 1, 100);
      
    } catch (error) {
      console.error('Failed to update warehouse config:', error);
      if (isMountedRef.current) {
        toast({
          title: "Update Failed",
          description: "Failed to update warehouse configuration. Please check your input and try again.",
          variant: "destructive",
        });
      }
    }
  };

  const handleFormChange = (field: string, value: string | number | boolean) => {
    setSettingsFormData(prev => ({
      ...prev,
      [field]: value
    }));
  };

  // Check if warehouse needs setup
  const needsSetup = !currentWarehouseConfig && !configLoading;

  if (configLoading) {
    return (
      <div className="flex items-center justify-center h-64">
        <Loader2 className="h-8 w-8 animate-spin" />
        <span className="ml-2">Loading warehouse configuration...</span>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header Section */}
      <div className="flex justify-between items-start">
        <div>
          <h1 className="text-3xl font-bold tracking-tight">Warehouse Settings</h1>
          <p className="text-muted-foreground">
            Manage your warehouse locations and configuration
          </p>
        </div>
        
        {currentWarehouseConfig && (
          <div className="flex gap-2">
            <Button
              variant="outline"
              onClick={() => setShowLocationForm(true)}
              className="flex items-center gap-2"
            >
              <Plus className="h-4 w-4" />
              Add Location
            </Button>
            <Button
              variant="outline"
              onClick={() => setShowReconfigureWizard(true)}
              className="flex items-center gap-2"
            >
              <Settings className="h-4 w-4" />
              Reconfigure
            </Button>
          </div>
        )}
      </div>

      {/* Error Alert */}
      {error && (
        <Alert variant="destructive">
          <AlertCircle className="h-4 w-4" />
          <AlertDescription className="flex justify-between items-center">
            {error}
            <Button variant="ghost" size="sm" onClick={clearError}>
              Dismiss
            </Button>
          </AlertDescription>
        </Alert>
      )}

      {/* Setup Required State */}
      {needsSetup && (
        <Card className="border-dashed">
          <CardContent className="flex flex-col items-center justify-center py-12">
            <Building2 className="h-16 w-16 text-muted-foreground mb-4" />
            <h3 className="text-lg font-semibold mb-2">Warehouse Setup Required</h3>
            <p className="text-muted-foreground text-center mb-6 max-w-md">
              Before you can manage locations, you need to set up your warehouse configuration. 
              This includes defining your aisles, racks, and storage areas.
            </p>
            <Button onClick={() => setShowSetupWizard(true)} className="flex items-center gap-2">
              <Settings className="h-4 w-4" />
              Start Warehouse Setup
            </Button>
          </CardContent>
        </Card>
      )}

      {/* Warehouse Overview */}
      {currentWarehouseConfig && (() => {
        // Debug: Log the current warehouse config to identify the data issue
        console.log('📊 WAREHOUSE OVERVIEW DEBUG:', currentWarehouseConfig);
        
        // Calculate accurate metrics from current warehouse configuration
        // Handle new accounts with incomplete/empty config data
        const numAisles = currentWarehouseConfig.num_aisles || 0;
        const racksPerAisle = currentWarehouseConfig.racks_per_aisle || 0;
        const positionsPerRack = currentWarehouseConfig.positions_per_rack || 0;
        const levelsPerPosition = currentWarehouseConfig.levels_per_position || 0;
        const defaultPalletCapacity = currentWarehouseConfig.default_pallet_capacity || 0;
        
        const storageLocations = numAisles * racksPerAisle * positionsPerRack * levelsPerPosition;
        const storageCapacity = storageLocations * defaultPalletCapacity;
        
        // Add receiving/staging/dock area capacities from configuration
        let specialAreaCapacity = 0;
        let specialAreaCount = 0;
        
        try {
          if (currentWarehouseConfig.receiving_areas && Array.isArray(currentWarehouseConfig.receiving_areas)) {
            specialAreaCapacity += currentWarehouseConfig.receiving_areas.reduce((sum: number, area: { capacity?: number }) => sum + (area.capacity || 0), 0);
            specialAreaCount += currentWarehouseConfig.receiving_areas.length;
          }
          if (currentWarehouseConfig.staging_areas && Array.isArray(currentWarehouseConfig.staging_areas)) {
            specialAreaCapacity += currentWarehouseConfig.staging_areas.reduce((sum: number, area: { capacity?: number }) => sum + (area.capacity || 0), 0);
            specialAreaCount += currentWarehouseConfig.staging_areas.length;
          }
          if (currentWarehouseConfig.dock_areas && Array.isArray(currentWarehouseConfig.dock_areas)) {
            specialAreaCapacity += currentWarehouseConfig.dock_areas.reduce((sum: number, area: { capacity?: number }) => sum + (area.capacity || 0), 0);
            specialAreaCount += currentWarehouseConfig.dock_areas.length;
          }
        } catch (error) {
          // Handle JSON parsing errors gracefully
          console.warn('Error parsing special areas:', error);
        }
        
        const totalLocations = storageLocations + specialAreaCount;
        const totalCapacity = storageCapacity + specialAreaCapacity;
        
        // Check if this is an empty/new configuration
        const isEmptyConfig = numAisles === 0 && racksPerAisle === 0 && positionsPerRack === 0;
        
        // Find the active template
        const activeTemplate = findActiveTemplate();
        
        // Determine match type for better user feedback
        const getTemplateMatchInfo = () => {
          if (!activeTemplate) return { matchType: 'none', badgeColor: 'bg-gray-100 text-gray-700' };
          
          // Check for exact match
          if (
            activeTemplate.num_aisles === currentWarehouseConfig.num_aisles &&
            activeTemplate.racks_per_aisle === currentWarehouseConfig.racks_per_aisle &&
            activeTemplate.positions_per_rack === currentWarehouseConfig.positions_per_rack &&
            activeTemplate.levels_per_position === currentWarehouseConfig.levels_per_position &&
            activeTemplate.default_pallet_capacity === currentWarehouseConfig.default_pallet_capacity &&
            activeTemplate.bidimensional_racks === currentWarehouseConfig.bidimensional_racks &&
            activeTemplate.level_names === currentWarehouseConfig.level_names
          ) {
            return { matchType: 'exact', badgeColor: 'bg-green-100 text-green-700' };
          }
          
          // Check for partial match (without level names)
          if (
            activeTemplate.num_aisles === currentWarehouseConfig.num_aisles &&
            activeTemplate.racks_per_aisle === currentWarehouseConfig.racks_per_aisle &&
            activeTemplate.positions_per_rack === currentWarehouseConfig.positions_per_rack &&
            activeTemplate.levels_per_position === currentWarehouseConfig.levels_per_position &&
            activeTemplate.default_pallet_capacity === currentWarehouseConfig.default_pallet_capacity &&
            activeTemplate.bidimensional_racks === currentWarehouseConfig.bidimensional_racks
          ) {
            return { matchType: 'partial', badgeColor: 'bg-yellow-100 text-yellow-700' };
          }
          
          // Structure match only
          return { matchType: 'structure', badgeColor: 'bg-blue-100 text-blue-700' };
        };
        
        const templateMatch = getTemplateMatchInfo();
        
        return (
          <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
            <Card>
              <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                <CardTitle className="text-sm font-medium">Total Locations</CardTitle>
                <Package className="h-4 w-4 text-muted-foreground" />
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold">
                  {isEmptyConfig ? 'N/A' : totalLocations.toLocaleString()}
                </div>
                <p className="text-xs text-muted-foreground">
                  {isEmptyConfig 
                    ? 'Setup required' 
                    : `${storageLocations.toLocaleString()} storage + ${specialAreaCount} special areas`
                  }
                </p>
              </CardContent>
            </Card>

            <Card>
              <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                <CardTitle className="text-sm font-medium">Storage Capacity</CardTitle>
                <Building2 className="h-4 w-4 text-muted-foreground" />
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold">
                  {isEmptyConfig ? 'N/A' : totalCapacity.toLocaleString()}
                </div>
                <p className="text-xs text-muted-foreground">
                  {isEmptyConfig 
                    ? 'Setup required'
                    : `Total pallet capacity (${storageCapacity.toLocaleString()} storage + ${specialAreaCapacity.toLocaleString()} special)`
                  }
                </p>
              </CardContent>
            </Card>

            <Card>
              <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                <CardTitle className="text-sm font-medium">Structure</CardTitle>
                <Settings className="h-4 w-4 text-muted-foreground" />
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold">
                  {isEmptyConfig ? 'N/A' : `${numAisles}A/${racksPerAisle}R`}
                </div>
                <p className="text-xs text-muted-foreground">
                  {isEmptyConfig 
                    ? 'Setup required'
                    : `${positionsPerRack}P × ${levelsPerPosition}L per rack`
                  }
                </p>
              </CardContent>
            </Card>

            <Card>
              <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                <CardTitle className="text-sm font-medium">Active Template</CardTitle>
                {activeTemplate ? (
                  <Badge variant="secondary" className={templateMatch.badgeColor}>
                    {activeTemplate.template_code}
                  </Badge>
                ) : (
                  <Badge variant="secondary" className="bg-gray-100 text-gray-700">
                    Custom
                  </Badge>
                )}
              </CardHeader>
              <CardContent>
                <div className="text-sm font-medium">
                  {activeTemplate ? activeTemplate.name : 'Custom Configuration'}
                </div>
                <p className="text-xs text-muted-foreground">
                  {activeTemplate ? (
                    <>
                      {activeTemplate.description || 'No description'}
                      {templateMatch.matchType === 'exact' && ' • Exact match'}
                      {templateMatch.matchType === 'partial' && ' • Partial match (custom levels)'}
                      {templateMatch.matchType === 'structure' && ' • Structure match only'}
                      {' • Updated '}
                      {new Date(currentWarehouseConfig.updated_at || currentWarehouseConfig.created_at).toLocaleDateString()}
                    </>
                  ) : (
                    `${currentWarehouseConfig.default_pallet_capacity} pallet${currentWarehouseConfig.default_pallet_capacity > 1 ? 's' : ''}/level • ${currentWarehouseConfig.bidimensional_racks ? 'Bidimensional' : 'Single'} racks`
                  )}
                </p>
              </CardContent>
            </Card>
          </div>
        );
      })()}

      {/* Main Content Tabs */}
      {currentWarehouseConfig && (
        <Tabs value={activeTab} onValueChange={setActiveTab} className="w-full">
          <TabsList className="grid w-full grid-cols-3">
            <TabsTrigger value="locations">Locations</TabsTrigger>
            <TabsTrigger value="templates">Templates</TabsTrigger>
            <TabsTrigger value="settings">Settings</TabsTrigger>
          </TabsList>

          <TabsContent value="locations" className="space-y-4">
            {/* Location Management - Smart Display */}
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <Building2 className="h-5 w-5" />
                  Special Areas Management
                </CardTitle>
                <CardDescription>
                  Manage your receiving, staging, and dock areas. Changes here will be reflected in template editing.
                </CardDescription>
              </CardHeader>
              <CardContent>
                {specialLocations.length > 0 ? (
                  <LocationList
                    locations={specialLocations}
                    loading={false} // Don't show loading when we have data
                    pagination={null} // No pagination for special areas
                    onEdit={(location) => {
                      setEditingLocation(location);
                      setShowLocationForm(true);
                    }}
                    onPageChange={() => {}} // Not used
                  />
                ) : (
                  <div className="text-center py-12">
                    {locationsLoading && locations.length === 0 ? (
                      <div>
                        <Loader2 className="h-8 w-8 animate-spin mx-auto mb-4 text-muted-foreground" />
                        <p className="text-muted-foreground">Loading special areas...</p>
                      </div>
                    ) : (
                      <div>
                        <Building2 className="h-16 w-16 mx-auto mb-4 text-muted-foreground/50" />
                        <h3 className="text-lg font-semibold mb-2">No Special Areas Found</h3>
                        <p className="text-muted-foreground mb-6 max-w-md mx-auto">
                          No receiving, staging, or dock areas found for warehouse &apos;{warehouseId}&apos;. 
                          {locations.length > 0 ? 
                            `Found ${locations.length} storage locations, but no special areas.` :
                            'No locations loaded yet - check console for API errors.'
                          }
                        </p>
                        <div className="flex gap-2 justify-center">
                          <Button 
                            variant="outline"
                            onClick={() => setShowLocationForm(true)}
                            className="flex items-center gap-2"
                          >
                            <Plus className="h-4 w-4" />
                            Add Special Area
                          </Button>
                          <Button 
                            variant="outline"
                            onClick={() => setShowSetupWizard(true)}
                            className="flex items-center gap-2"
                          >
                            <Settings className="h-4 w-4" />
                            Setup Wizard
                          </Button>
                        </div>
                        <p className="text-xs text-muted-foreground mt-4">
                          Storage locations are managed through the search tool below
                        </p>
                      </div>
                    )}
                  </div>
                )}
              </CardContent>
            </Card>

            {/* Storage Location Search-to-Edit */}
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <Search className="h-5 w-5" />
                  Edit Storage Location
                </CardTitle>
                <CardDescription>
                  Find and edit a specific storage location by entering its code
                </CardDescription>
              </CardHeader>
              <CardContent className="space-y-4">
                <div className="flex gap-2">
                  <Input
                    placeholder="Enter location code (e.g., 01-02-015C)"
                    value={locationSearchCode}
                    onChange={(e) => setLocationSearchCode(e.target.value.toUpperCase())}
                    onKeyPress={(e) => e.key === 'Enter' && handleLocationSearch(locationSearchCode)}
                    className="flex-1 font-mono"
                  />
                  <Button 
                    onClick={() => handleLocationSearch(locationSearchCode)}
                    disabled={!locationSearchCode.trim() || searchingLocation}
                  >
                    {searchingLocation ? (
                      <Loader2 className="h-4 w-4 animate-spin" />
                    ) : (
                      <Edit className="h-4 w-4" />
                    )}
                    Find & Edit
                  </Button>
                </div>

                {/* Search Warnings */}
                {searchWarnings.length > 0 && (
                  <div className="space-y-2">
                    {searchWarnings.map((warning, index) => (
                      <p key={index} className="text-sm text-amber-600 dark:text-amber-400 flex items-start gap-2 bg-amber-50 dark:bg-amber-900/20 p-2 rounded-md border border-amber-200 dark:border-amber-800">
                        {warning}
                      </p>
                    ))}
                  </div>
                )}
                
                <div className="text-sm text-muted-foreground">
                  <p><strong>Examples:</strong></p>
                  <ul className="list-disc list-inside space-y-1 ml-2">
                    <li><code className="bg-muted px-1 py-0.5 rounded">A01-R01-P01-A</code> - Aisle 1, Rack 1, Position 1, Level A</li>
                    <li><code className="bg-muted px-1 py-0.5 rounded">A03-R05-P25</code> - Find all levels at this position</li>
                    <li><code className="bg-muted px-1 py-0.5 rounded">STAGING-01</code> - Special area code</li>
                  </ul>
                </div>
              </CardContent>
            </Card>

            {/* Quick Actions */}
            <Card>
              <CardHeader>
                <CardTitle>Quick Actions</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="flex gap-2">
                  <Button 
                    variant="outline" 
                    onClick={() => setShowLocationForm(true)}
                    className="flex items-center gap-2"
                  >
                    <Plus className="h-4 w-4" />
                    Add New Location
                  </Button>
                  <LocationImportExport 
                    warehouseId={warehouseId}
                    onImportComplete={(result) => {
                      if (result.created_count > 0) {
                        toast({
                          title: "Import Successful",
                          description: `Successfully imported ${result.created_count} locations!`,
                          variant: "success",
                        });
                        // Refresh locations
                        fetchLocations({ warehouse_id: warehouseId }, 1, 100);
                      }
                      if (result.errors.length > 0) {
                        console.warn('Import errors:', result.errors);
                        toast({
                          title: "Import Warning",
                          description: `Import completed with ${result.errors.length} error(s). Check console for details.`,
                          variant: "warning",
                        });
                      }
                    }}
                  />
                </div>
              </CardContent>
            </Card>
          </TabsContent>

          <TabsContent value="templates">
            <EnhancedTemplateManagerV2 warehouseId={warehouseId} />
          </TabsContent>

          <TabsContent value="settings">
            <Card>
              <CardHeader>
                <div className="flex justify-between items-start">
                  <div>
                    <CardTitle className="flex items-center gap-2">
                      Warehouse Configuration
                      {(() => {
                        const activeTemplate = findActiveTemplate();
                        return activeTemplate ? (
                          <Badge variant="secondary" className="bg-green-100 text-green-700">
                            {activeTemplate.name}
                          </Badge>
                        ) : (
                          <Badge variant="secondary" className="bg-gray-100 text-gray-700">
                            Custom
                          </Badge>
                        );
                      })()}
                    </CardTitle>
                    <CardDescription>
                      {isEditingSettings 
                        ? 'Edit your warehouse configuration - changes will regenerate all locations'
                        : 'Configure your active warehouse template settings'
                      }
                    </CardDescription>
                  </div>
                  {!isEditingSettings && (
                    <div className="flex gap-2">
                      <Button 
                        variant="outline" 
                        size="sm"
                        onClick={handleEditSettings}
                      >
                        <Edit className="h-4 w-4 mr-2" />
                        Edit Configuration
                      </Button>
                      <Button 
                        variant="outline" 
                        size="sm"
                        onClick={() => setShowReconfigureWizard(true)}
                      >
                        <Settings className="h-4 w-4 mr-2" />
                        Reconfigure
                      </Button>
                    </div>
                  )}
                </div>
              </CardHeader>
              <CardContent className="space-y-4">
                {currentWarehouseConfig && (
                  isEditingSettings ? (
                    // Edit Form
                    <form className="space-y-6">
                      <div className="grid grid-cols-2 gap-4">
                        <div className="space-y-2">
                          <Label htmlFor="warehouse_name">Warehouse Name</Label>
                          <Input
                            id="warehouse_name"
                            value={settingsFormData.warehouse_name}
                            onChange={(e) => handleFormChange('warehouse_name', e.target.value)}
                            placeholder="Enter warehouse name"
                          />
                        </div>
                        <div className="space-y-2">
                          <Label htmlFor="num_aisles">Number of Aisles</Label>
                          <Input
                            id="num_aisles"
                            type="number"
                            min="1"
                            value={settingsFormData.num_aisles}
                            onChange={(e) => handleFormChange('num_aisles', parseInt(e.target.value) || 0)}
                          />
                        </div>
                        <div className="space-y-2">
                          <Label htmlFor="racks_per_aisle">Racks per Aisle</Label>
                          <Input
                            id="racks_per_aisle"
                            type="number"
                            min="1"
                            value={settingsFormData.racks_per_aisle}
                            onChange={(e) => handleFormChange('racks_per_aisle', parseInt(e.target.value) || 0)}
                          />
                        </div>
                        <div className="space-y-2">
                          <Label htmlFor="positions_per_rack">Positions per Rack</Label>
                          <Input
                            id="positions_per_rack"
                            type="number"
                            min="1"
                            value={settingsFormData.positions_per_rack}
                            onChange={(e) => handleFormChange('positions_per_rack', parseInt(e.target.value) || 0)}
                          />
                        </div>
                        <div className="space-y-2">
                          <Label htmlFor="levels_per_position">Levels per Position</Label>
                          <Input
                            id="levels_per_position"
                            type="number"
                            min="1"
                            value={settingsFormData.levels_per_position}
                            onChange={(e) => handleFormChange('levels_per_position', parseInt(e.target.value) || 0)}
                          />
                        </div>
                        <div className="space-y-2">
                          <Label htmlFor="level_names">Level Names</Label>
                          <Input
                            id="level_names"
                            value={settingsFormData.level_names}
                            onChange={(e) => handleFormChange('level_names', e.target.value)}
                            placeholder="e.g., ABCD"
                          />
                        </div>
                        <div className="space-y-2">
                          <Label htmlFor="default_pallet_capacity">Default Pallet Capacity</Label>
                          <Input
                            id="default_pallet_capacity"
                            type="number"
                            min="1"
                            value={settingsFormData.default_pallet_capacity}
                            onChange={(e) => handleFormChange('default_pallet_capacity', parseInt(e.target.value) || 0)}
                          />
                        </div>
                        <div className="space-y-2 flex items-center gap-2">
                          <Switch
                            id="bidimensional_racks"
                            checked={settingsFormData.bidimensional_racks}
                            onCheckedChange={(checked) => handleFormChange('bidimensional_racks', checked)}
                          />
                          <Label htmlFor="bidimensional_racks" className="cursor-pointer">
                            Bidimensional Racks (2 pallets per level)
                          </Label>
                        </div>
                      </div>

                      <div className="flex justify-end gap-2 pt-4 border-t">
                        <Button 
                          type="button" 
                          variant="outline" 
                          onClick={handleCancelEdit}
                        >
                          <X className="h-4 w-4 mr-2" />
                          Cancel
                        </Button>
                        <Button 
                          type="button" 
                          onClick={handleSaveSettings}
                        >
                          <Save className="h-4 w-4 mr-2" />
                          Save Changes
                        </Button>
                      </div>
                    </form>
                  ) : (
                    // View Mode
                    <div className="grid grid-cols-2 gap-4">
                      <div>
                        <label className="text-sm font-medium">Warehouse Name</label>
                        <p className="text-sm text-muted-foreground">
                          {currentWarehouseConfig.warehouse_name}
                        </p>
                      </div>
                      <div>
                        <label className="text-sm font-medium">Warehouse ID</label>
                        <p className="text-sm text-muted-foreground">
                          {currentWarehouseConfig.warehouse_id}
                        </p>
                      </div>
                      <div>
                        <label className="text-sm font-medium">Structure</label>
                        <p className="text-sm text-muted-foreground">
                          {currentWarehouseConfig.num_aisles} aisles × {currentWarehouseConfig.racks_per_aisle} racks × {currentWarehouseConfig.positions_per_rack} positions × {currentWarehouseConfig.levels_per_position} levels
                        </p>
                      </div>
                      <div>
                        <label className="text-sm font-medium">Level Names</label>
                        <p className="text-sm text-muted-foreground">
                          {currentWarehouseConfig.level_names}
                        </p>
                      </div>
                      <div>
                        <label className="text-sm font-medium">Default Capacity</label>
                        <p className="text-sm text-muted-foreground">
                          {currentWarehouseConfig.default_pallet_capacity} pallet{currentWarehouseConfig.default_pallet_capacity > 1 ? 's' : ''} per level
                        </p>
                      </div>
                      <div>
                        <label className="text-sm font-medium">Rack Type</label>
                        <p className="text-sm text-muted-foreground">
                          {currentWarehouseConfig.bidimensional_racks ? 'Bidimensional (2 pallets/level)' : 'Single (1 pallet/level)'}
                        </p>
                      </div>
                    </div>
                  )
                )}
              </CardContent>
            </Card>
          </TabsContent>
        </Tabs>
      )}

      {/* Modals */}
      {showLocationForm && (
        <LocationForm
          location={editingLocation}
          warehouseId={warehouseId}
          onClose={() => {
            setShowLocationForm(false);
            setEditingLocation(null);
          }}
          onSave={() => {
            setShowLocationForm(false);
            setEditingLocation(null);
            // Refresh locations
            fetchLocations({ warehouse_id: warehouseId });
          }}
        />
      )}

      {showSetupWizard && (
        <WarehouseSetupWizard
          existingConfig={currentWarehouseConfig}
          warehouseId={warehouseId}
          onClose={() => setShowSetupWizard(false)}
          onComplete={async () => {
            setShowSetupWizard(false);
            
            // First, clear any existing filters that might interfere with the refresh
            const freshFilters = { warehouse_id: warehouseId };
            setFilters(freshFilters);
            
            // Refresh the config first
            await fetchWarehouseConfig(warehouseId);
            
            // Then explicitly fetch first page with fresh filters for consistent behavior
            // This ensures proper location display after reconfiguration
            console.log('Reconfiguration complete - fetching locations with fresh filters');
            await fetchLocations(freshFilters, 1, 100);
          }}
        />
      )}

      {showReconfigureWizard && currentWarehouseConfig && (
        <SimplifiedReconfigureWizard
          existingConfig={currentWarehouseConfig}
          currentTemplate={findActiveTemplate()}
          warehouseId={warehouseId}
          onClose={() => setShowReconfigureWizard(false)}
          onComplete={async () => {
            setShowReconfigureWizard(false);
            
            // Refresh data after reconfiguration
            const freshFilters = { warehouse_id: warehouseId };
            setFilters(freshFilters);
            
            await fetchWarehouseConfig(warehouseId);
            await fetchLocations(freshFilters, 1, 100);
            
            console.log('Reconfiguration complete - data refreshed');
          }}
        />
      )}
    </div>
  );
}