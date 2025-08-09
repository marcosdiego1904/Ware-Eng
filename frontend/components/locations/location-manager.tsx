'use client';

import React, { useState, useEffect } from 'react';
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
import { WarehouseSetupWizard } from './setup-wizard/warehouse-wizard';
import { EnhancedTemplateManagerV2 } from './templates/enhanced-template-manager-v2';
import useLocationStore, { Location } from '@/lib/location-store';
import { 
  Plus, 
  Search, 
  Download, 
  Upload, 
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
    pagination,
    filters,
    fetchLocations,
    fetchWarehouseConfig,
    fetchTemplates,
    updateWarehouseConfig,
    setFilters,
    clearError
  } = useLocationStore();

  const [activeTab, setActiveTab] = useState('locations');
  const [searchTerm, setSearchTerm] = useState('');
  const [showLocationForm, setShowLocationForm] = useState(false);
  const [showSetupWizard, setShowSetupWizard] = useState(false);
  const [editingLocation, setEditingLocation] = useState<Location | null>(null);
  
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

  // Load initial data
  useEffect(() => {
    fetchWarehouseConfig(warehouseId);
    fetchTemplates('all'); // Load templates to identify active one
  }, [warehouseId]);

  // Refresh locations when warehouse config changes or initially loads
  useEffect(() => {
    console.log('LocationManager useEffect triggered:', {
      configId: currentWarehouseConfig?.id,
      updatedAt: currentWarehouseConfig?.updated_at,
      warehouseId,
      configLoading
    });
    
    if (currentWarehouseConfig?.id) {
      // Clear any existing filters that might hide new locations
      const freshFilters = { warehouse_id: warehouseId };
      setFilters(freshFilters);
      // Fetch with increased pagination to show all locations
      console.log('Fetching locations from LocationManager with filters:', freshFilters);
      fetchLocations(freshFilters, 1, 500); // Increased from default 50 to 500
    } else if (!configLoading && warehouseId) {
      // Initial load when no config exists yet
      console.log('Fetching locations from LocationManager (no config):', { warehouse_id: warehouseId });
      fetchLocations({ warehouse_id: warehouseId }, 1, 500);
    }
  }, [currentWarehouseConfig?.id, currentWarehouseConfig?.updated_at, warehouseId]);

  // Separate useEffect for initial config loading to avoid conflicts
  useEffect(() => {
    if (!currentWarehouseConfig && !configLoading && warehouseId) {
      fetchLocations({ warehouse_id: warehouseId }, 1, 500);
    }
  }, [configLoading, warehouseId]);

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

  // Handle search
  const handleSearch = () => {
    const newFilters = {
      ...filters,
      warehouse_id: warehouseId,
      search: searchTerm
    };
    setFilters(newFilters);
    fetchLocations(newFilters, 1, 500); // Use increased pagination for search results
  };

  // Handle filter changes
  const handleFilterChange = (filterKey: string, value: string) => {
    const newFilters = {
      ...filters,
      warehouse_id: warehouseId,
      [filterKey]: value
    };
    setFilters(newFilters);
    fetchLocations(newFilters, 1, 500); // Use increased pagination for filtered results
  };

  // Helper function to find the active template based on current warehouse config
  const findActiveTemplate = () => {
    if (!currentWarehouseConfig || !templates || templates.length === 0) {
      return null;
    }
    
    return templates.find(template => 
      template.num_aisles === currentWarehouseConfig.num_aisles &&
      template.racks_per_aisle === currentWarehouseConfig.racks_per_aisle &&
      template.positions_per_rack === currentWarehouseConfig.positions_per_rack &&
      template.levels_per_position === currentWarehouseConfig.levels_per_position &&
      template.default_pallet_capacity === currentWarehouseConfig.default_pallet_capacity &&
      template.bidimensional_racks === currentWarehouseConfig.bidimensional_racks
    ) || null;
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
      
      alert('Warehouse configuration updated successfully! Locations will be regenerated to match the new structure.');
      setIsEditingSettings(false);
      
      // Fetch the updated config, which will trigger the useEffect to refresh locations.
      await fetchWarehouseConfig(warehouseId);
      await fetchTemplates('all');
      
    } catch (error) {
      console.error('Failed to update warehouse config:', error);
      alert('Failed to update warehouse configuration. Please try again.');
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
              onClick={() => setShowSetupWizard(true)}
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
        // Calculate accurate metrics from current warehouse configuration
        const storageLocations = currentWarehouseConfig.num_aisles * 
          currentWarehouseConfig.racks_per_aisle * 
          currentWarehouseConfig.positions_per_rack * 
          currentWarehouseConfig.levels_per_position;
        
        const storageCapacity = storageLocations * currentWarehouseConfig.default_pallet_capacity;
        
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
        
        // Find the active template
        const activeTemplate = findActiveTemplate();
        
        return (
          <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
            <Card>
              <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                <CardTitle className="text-sm font-medium">Total Locations</CardTitle>
                <Package className="h-4 w-4 text-muted-foreground" />
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold">
                  {totalLocations.toLocaleString()}
                </div>
                <p className="text-xs text-muted-foreground">
                  {storageLocations.toLocaleString()} storage + {specialAreaCount} special areas
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
                  {totalCapacity.toLocaleString()}
                </div>
                <p className="text-xs text-muted-foreground">
                  Total pallet capacity ({storageCapacity.toLocaleString()} storage + {specialAreaCapacity.toLocaleString()} special)
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
                  {currentWarehouseConfig.num_aisles}A/{currentWarehouseConfig.racks_per_aisle}R
                </div>
                <p className="text-xs text-muted-foreground">
                  {currentWarehouseConfig.positions_per_rack}P × {currentWarehouseConfig.levels_per_position}L per rack
                </p>
              </CardContent>
            </Card>

            <Card>
              <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                <CardTitle className="text-sm font-medium">Active Template</CardTitle>
                {activeTemplate ? (
                  <Badge variant="secondary" className="bg-green-100 text-green-700">
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
                    `${activeTemplate.description || 'No description'} • Updated ${new Date(currentWarehouseConfig.updated_at || currentWarehouseConfig.created_at).toLocaleDateString()}`
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
            {/* Search and Filters */}
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <Search className="h-5 w-5" />
                  Location Management
                </CardTitle>
                <CardDescription>
                  Search, filter, and manage your warehouse locations
                </CardDescription>
              </CardHeader>
              <CardContent className="space-y-4">
                {/* Search Bar */}
                <div className="flex gap-2">
                  <Input
                    placeholder="Search locations by code, zone, or type..."
                    value={searchTerm}
                    onChange={(e) => setSearchTerm(e.target.value)}
                    onKeyPress={(e) => e.key === 'Enter' && handleSearch()}
                    className="flex-1"
                  />
                  <Button onClick={handleSearch} variant="outline">
                    <Search className="h-4 w-4" />
                  </Button>
                </div>

                {/* Quick Filters */}
                <div className="flex flex-wrap gap-2">
                  <Button
                    variant={filters.location_type === 'STORAGE' ? 'default' : 'outline'}
                    size="sm"
                    onClick={() => handleFilterChange('location_type', 
                      filters.location_type === 'STORAGE' ? '' : 'STORAGE')}
                  >
                    Storage Locations
                  </Button>
                  <Button
                    variant={filters.location_type === 'RECEIVING' ? 'default' : 'outline'}
                    size="sm"
                    onClick={() => handleFilterChange('location_type', 
                      filters.location_type === 'RECEIVING' ? '' : 'RECEIVING')}
                  >
                    Receiving Areas
                  </Button>
                  <Button
                    variant={filters.location_type === 'STAGING' ? 'default' : 'outline'}
                    size="sm"
                    onClick={() => handleFilterChange('location_type', 
                      filters.location_type === 'STAGING' ? '' : 'STAGING')}
                  >
                    Staging Areas
                  </Button>
                </div>

                {/* Action Buttons */}
                <div className="flex justify-between items-center pt-4 border-t">
                  <div className="flex gap-2">
                    <Button variant="outline" size="sm">
                      <Download className="h-4 w-4 mr-2" />
                      Export
                    </Button>
                    <Button variant="outline" size="sm">
                      <Upload className="h-4 w-4 mr-2" />
                      Import
                    </Button>
                    <Button 
                      variant="outline" 
                      size="sm"
                      onClick={() => {
                        setSearchTerm('');
                        const freshFilters = { warehouse_id: warehouseId };
                        setFilters(freshFilters);
                        fetchLocations(freshFilters, 1, 500);
                      }}
                    >
                      Show All Locations
                    </Button>
                  </div>
                  
                  {pagination && (
                    <Badge variant="secondary">
                      {pagination.total} total locations
                    </Badge>
                  )}
                </div>
              </CardContent>
            </Card>

            {/* Locations List */}
            <LocationList
              locations={locations}
              loading={locationsLoading}
              pagination={pagination}
              onEdit={(location) => {
                setEditingLocation(location);
                setShowLocationForm(true);
              }}
              onPageChange={(page) => {
                fetchLocations({ ...filters, warehouse_id: warehouseId }, page, 500);
              }}
            />
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
                        onClick={() => setShowSetupWizard(true)}
                      >
                        <Settings className="h-4 w-4 mr-2" />
                        Setup Wizard
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
            // Refresh the config. The useEffect hook will react to this and fetch the new locations.
            await fetchWarehouseConfig(warehouseId);
          }}
        />
      )}
    </div>
  );
}