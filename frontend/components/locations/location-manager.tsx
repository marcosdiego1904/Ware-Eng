'use client';

import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Badge } from '@/components/ui/badge';
import { Alert, AlertDescription } from '@/components/ui/alert';
import { LocationList } from './location-list';
import { LocationForm } from './location-form';
import { WarehouseSetupWizard } from './setup-wizard/warehouse-wizard';
import { TemplateManager } from './templates/template-manager';
import useLocationStore, { Location } from '@/lib/location-store';
import { 
  Plus, 
  Search, 
  Filter, 
  Download, 
  Upload, 
  Settings, 
  Building2, 
  Package,
  AlertCircle,
  Loader2
} from 'lucide-react';

interface LocationManagerProps {
  warehouseId?: string;
}

export function LocationManager({ warehouseId = 'DEFAULT' }: LocationManagerProps) {
  const {
    locations,
    currentWarehouseConfig,
    loading,
    locationsLoading,
    configLoading,
    error,
    summary,
    pagination,
    filters,
    fetchLocations,
    fetchWarehouseConfig,
    setFilters,
    clearError
  } = useLocationStore();

  const [activeTab, setActiveTab] = useState('locations');
  const [searchTerm, setSearchTerm] = useState('');
  const [showLocationForm, setShowLocationForm] = useState(false);
  const [showSetupWizard, setShowSetupWizard] = useState(false);
  const [editingLocation, setEditingLocation] = useState<Location | null>(null);

  // Load initial data
  useEffect(() => {
    fetchWarehouseConfig(warehouseId);
    fetchLocations({ warehouse_id: warehouseId });
  }, [warehouseId]);

  // Handle search
  const handleSearch = () => {
    const newFilters = {
      ...filters,
      warehouse_id: warehouseId,
      search: searchTerm
    };
    setFilters(newFilters);
    fetchLocations(newFilters);
  };

  // Handle filter changes
  const handleFilterChange = (filterKey: string, value: string) => {
    const newFilters = {
      ...filters,
      warehouse_id: warehouseId,
      [filterKey]: value
    };
    setFilters(newFilters);
    fetchLocations(newFilters);
  };

  // Check if warehouse needs setup
  const needsSetup = !currentWarehouseConfig && !configLoading;
  const hasLocations = locations.length > 0;

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
      {currentWarehouseConfig && (
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">Total Locations</CardTitle>
              <Package className="h-4 w-4 text-muted-foreground" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">
                {summary?.total_locations || 0}
              </div>
              <p className="text-xs text-muted-foreground">
                Active locations in warehouse
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
                {summary?.total_capacity || 0}
              </div>
              <p className="text-xs text-muted-foreground">
                Total pallet capacity
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
                Aisles / Racks per aisle
              </p>
            </CardContent>
          </Card>

          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">Warehouse</CardTitle>
              <Badge variant="secondary">{currentWarehouseConfig.warehouse_id}</Badge>
            </CardHeader>
            <CardContent>
              <div className="text-sm font-medium">
                {currentWarehouseConfig.warehouse_name}
              </div>
              <p className="text-xs text-muted-foreground">
                Created {new Date(currentWarehouseConfig.created_at).toLocaleDateString()}
              </p>
            </CardContent>
          </Card>
        </div>
      )}

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
              onEdit={setEditingLocation}
              onPageChange={(page) => {
                fetchLocations({ ...filters, warehouse_id: warehouseId }, page);
              }}
            />
          </TabsContent>

          <TabsContent value="templates">
            <TemplateManager warehouseId={warehouseId} />
          </TabsContent>

          <TabsContent value="settings">
            <Card>
              <CardHeader>
                <CardTitle>Warehouse Configuration</CardTitle>
                <CardDescription>
                  View and modify your warehouse settings
                </CardDescription>
              </CardHeader>
              <CardContent className="space-y-4">
                {currentWarehouseConfig && (
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
                )}
                
                <div className="pt-4 border-t">
                  <Button onClick={() => setShowSetupWizard(true)}>
                    <Settings className="h-4 w-4 mr-2" />
                    Reconfigure Warehouse
                  </Button>
                </div>
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
          onSave={(location) => {
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
          onComplete={(config) => {
            setShowSetupWizard(false);
            // Refresh data
            fetchWarehouseConfig(warehouseId);
            fetchLocations({ warehouse_id: warehouseId });
          }}
        />
      )}
    </div>
  );
}