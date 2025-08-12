'use client';

import React, { useState, useEffect } from 'react';
import { Dialog, DialogContent, DialogDescription, DialogHeader, DialogTitle } from '@/components/ui/dialog';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Textarea } from '@/components/ui/textarea';
import { Switch } from '@/components/ui/switch';
import { Alert, AlertDescription } from '@/components/ui/alert';
import { Badge } from '@/components/ui/badge';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import useLocationStore, { WarehouseTemplate, SpecialArea } from '@/lib/location-store';
import { 
  Save, 
  X, 
  Building2, 
  Grid3X3, 
  Package, 
  Globe,
  Lock,
  AlertCircle,
  Loader2,
  Plus,
  Trash2,
  MapPin,
  Truck,
  Calculator,
  Info,
  Zap
} from 'lucide-react';

interface TemplateEditModalProps {
  template: WarehouseTemplate | null;
  open: boolean;
  onClose: () => void;
  onTemplateUpdated?: (template: WarehouseTemplate) => void;
  warehouseId?: string;
}

interface ExtendedFormData {
  name: string;
  description: string;
  num_aisles: number;
  racks_per_aisle: number;
  positions_per_rack: number;
  levels_per_position: number;
  level_names: string;
  default_pallet_capacity: number;
  bidimensional_racks: boolean;
  is_public: boolean;
  receiving_areas_template: SpecialArea[];
  staging_areas_template: SpecialArea[];
  dock_areas_template: SpecialArea[];
}

export function EnhancedTemplateEditModal({ 
  template, 
  open, 
  onClose, 
  onTemplateUpdated,
  warehouseId 
}: TemplateEditModalProps) {
  const { 
    updateTemplate, 
    applyTemplate, 
    currentWarehouseConfig, 
    locations, 
    fetchLocations,
    loading, 
    error,
    setLoading,
    setError
  } = useLocationStore();
  
  // Form state
  const [formData, setFormData] = useState<ExtendedFormData>({
    name: '',
    description: '',
    num_aisles: 0,
    racks_per_aisle: 0,
    positions_per_rack: 0,
    levels_per_position: 0,
    level_names: '',
    default_pallet_capacity: 0,
    bidimensional_racks: false,
    is_public: false,
    receiving_areas_template: [],
    staging_areas_template: [],
    dock_areas_template: []
  });
  
  const [originalData, setOriginalData] = useState<ExtendedFormData>(formData);
  const [hasChanges, setHasChanges] = useState(false);
  const currentWarehouseId = warehouseId || 'DEFAULT';

  // Helper function to extract special areas from current warehouse locations
  const extractSpecialAreasFromLocations = (locations: any[]): {
    receiving_areas: SpecialArea[],
    staging_areas: SpecialArea[],
    dock_areas: SpecialArea[]
  } => {
    const receiving_areas: SpecialArea[] = [];
    const staging_areas: SpecialArea[] = [];
    const dock_areas: SpecialArea[] = [];

    locations.forEach(location => {
      if (location.location_type === 'RECEIVING') {
        receiving_areas.push({
          code: location.code,
          type: 'RECEIVING',
          capacity: location.capacity || location.pallet_capacity || 1,
          zone: location.zone || 'GENERAL'
        });
      } else if (location.location_type === 'STAGING') {
        staging_areas.push({
          code: location.code,
          type: 'STAGING',
          capacity: location.capacity || location.pallet_capacity || 1,
          zone: location.zone || 'GENERAL'
        });
      } else if (location.location_type === 'DOCK') {
        dock_areas.push({
          code: location.code,
          type: 'DOCK',
          capacity: location.capacity || location.pallet_capacity || 1,
          zone: location.zone || 'GENERAL'
        });
      }
    });

    return { receiving_areas, staging_areas, dock_areas };
  };

  // Load current warehouse special areas when modal opens
  useEffect(() => {
    if (open && currentWarehouseId) {
      console.log('🔄 Loading current warehouse locations to sync with template...', currentWarehouseId);
      const filters = { warehouse_id: currentWarehouseId };
      fetchLocations(filters, 1, 100);
    }
  }, [open, currentWarehouseId, fetchLocations]);

  // Populate form when template changes or locations are loaded (but not when user is editing)
  useEffect(() => {
    if (template) {
      // Only reset form data if there are no unsaved changes (prevents overriding user input)
      if (!hasChanges) {
        // Extract current warehouse special areas from locations
        const warehouseSpecialAreas = extractSpecialAreasFromLocations(locations || []);
        
        const templateFormData: ExtendedFormData = {
          name: template.name || '',
          description: template.description || '',
          num_aisles: template.num_aisles || 0,
          racks_per_aisle: template.racks_per_aisle || 0,
          positions_per_rack: template.positions_per_rack || 0,
          levels_per_position: template.levels_per_position || 0,
          level_names: template.level_names || '',
          default_pallet_capacity: template.default_pallet_capacity || 0,
          bidimensional_racks: template.bidimensional_racks || false,
          is_public: template.is_public || false,
          // Use current warehouse special areas instead of template stored ones
          receiving_areas_template: warehouseSpecialAreas.receiving_areas,
          staging_areas_template: warehouseSpecialAreas.staging_areas,
          dock_areas_template: warehouseSpecialAreas.dock_areas
        };
        
        console.log('🏗️ Template form populated with current warehouse special areas:', warehouseSpecialAreas);
        setFormData(templateFormData);
        setOriginalData(templateFormData);
      } else {
        console.log('🚫 Skipping form reset - user has unsaved changes');
      }
    }
  }, [template, locations, hasChanges]);

  // Check for changes
  useEffect(() => {
    const changed = JSON.stringify(formData) !== JSON.stringify(originalData);
    setHasChanges(changed);
  }, [formData, originalData]);

  const handleInputChange = (field: keyof ExtendedFormData, value: any) => {
    setFormData(prev => ({
      ...prev,
      [field]: value
    }));
  };

  // Special areas handlers
  const addSpecialArea = (type: 'receiving_areas_template' | 'staging_areas_template' | 'dock_areas_template') => {
    const areaType = type.replace('_areas_template', '').toUpperCase();
    const newArea: SpecialArea = {
      code: `${areaType}-${formData[type].length + 1}`,
      type: areaType,
      capacity: areaType === 'RECEIVING' ? 10 : areaType === 'STAGING' ? 5 : 2,
      zone: areaType === 'RECEIVING' || areaType === 'DOCK' ? 'DOCK' : 'STAGING'
    };
    
    handleInputChange(type, [...formData[type], newArea]);
  };

  const updateSpecialArea = (
    type: 'receiving_areas_template' | 'staging_areas_template' | 'dock_areas_template', 
    index: number, 
    field: keyof SpecialArea, 
    value: any
  ) => {
    const areas = [...formData[type]];
    areas[index] = { ...areas[index], [field]: value };
    handleInputChange(type, areas);
  };

  const removeSpecialArea = (type: 'receiving_areas_template' | 'staging_areas_template' | 'dock_areas_template', index: number) => {
    const areas = formData[type].filter((_, i) => i !== index);
    handleInputChange(type, areas);
  };

  // Sync warehouse special areas with template
  const syncWithWarehouseSpecialAreas = () => {
    if (!currentWarehouseConfig) return;
    
    try {
      // Parse warehouse special areas (they may be stored as JSON strings)
      const getAreas = (areasField: any): SpecialArea[] => {
        if (!areasField) return [];
        if (typeof areasField === 'string') {
          try {
            return JSON.parse(areasField) || [];
          } catch {
            return [];
          }
        }
        return Array.isArray(areasField) ? areasField : [];
      };

      const receivingAreas = getAreas(currentWarehouseConfig.receiving_areas);
      const stagingAreas = getAreas(currentWarehouseConfig.staging_areas);
      const dockAreas = getAreas(currentWarehouseConfig.dock_areas);

      // Update form data with current warehouse special areas
      setFormData(prev => ({
        ...prev,
        receiving_areas_template: receivingAreas,
        staging_areas_template: stagingAreas,
        dock_areas_template: dockAreas
      }));
      
    } catch (error) {
      console.error('Error syncing warehouse special areas:', error);
    }
  };

  const handleSave = async () => {
    if (!template || !hasChanges) return;

    setLoading(true);
    setError(null);

    try {
      // Create clean, validated data to prevent conflicts
      const updateData = {
        name: String(formData.name).trim(),
        description: String(formData.description).trim(),
        num_aisles: Math.max(1, parseInt(String(formData.num_aisles)) || 1),
        racks_per_aisle: Math.max(1, parseInt(String(formData.racks_per_aisle)) || 1),
        positions_per_rack: Math.max(1, parseInt(String(formData.positions_per_rack)) || 1),
        levels_per_position: Math.max(1, parseInt(String(formData.levels_per_position)) || 1),
        level_names: String(formData.level_names).trim(),
        default_pallet_capacity: Math.max(1, parseInt(String(formData.default_pallet_capacity)) || 1),
        bidimensional_racks: Boolean(formData.bidimensional_racks),
        is_public: Boolean(formData.is_public),
        // Deep clone to prevent reference conflicts
        receiving_areas_template: JSON.parse(JSON.stringify(formData.receiving_areas_template || [])),
        staging_areas_template: JSON.parse(JSON.stringify(formData.staging_areas_template || [])),
        dock_areas_template: JSON.parse(JSON.stringify(formData.dock_areas_template || []))
      };

      console.log(`Updating template ${template.id} with isolated data:`, updateData);

      const updatedTemplate = await updateTemplate(template.id, updateData);
      
      console.log(`Template ${template.id} updated successfully, no side effects expected`);
      
      // Update local state to reflect successful save
      setOriginalData(formData);
      
      if (onTemplateUpdated) {
        onTemplateUpdated(updatedTemplate);
      }
      
      onClose();
    } catch (error: any) {
      console.error('Failed to update template:', error);
      setError(error?.response?.data?.error || 'Failed to update template. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  const handleSaveAndTest = async () => {
    if (!template || !hasChanges) return;

    setLoading(true);
    setError(null);

    try {
      // First save the template with clean, validated data
      const updateData = {
        name: String(formData.name).trim(),
        description: String(formData.description).trim(),
        num_aisles: Math.max(1, parseInt(String(formData.num_aisles)) || 1),
        racks_per_aisle: Math.max(1, parseInt(String(formData.racks_per_aisle)) || 1),
        positions_per_rack: Math.max(1, parseInt(String(formData.positions_per_rack)) || 1),
        levels_per_position: Math.max(1, parseInt(String(formData.levels_per_position)) || 1),
        level_names: String(formData.level_names).trim(),
        default_pallet_capacity: Math.max(1, parseInt(String(formData.default_pallet_capacity)) || 1),
        bidimensional_racks: Boolean(formData.bidimensional_racks),
        is_public: Boolean(formData.is_public),
        // Deep clone to prevent reference conflicts
        receiving_areas_template: JSON.parse(JSON.stringify(formData.receiving_areas_template || [])),
        staging_areas_template: JSON.parse(JSON.stringify(formData.staging_areas_template || [])),
        dock_areas_template: JSON.parse(JSON.stringify(formData.dock_areas_template || []))
      };

      console.log(`Updating and testing template ${template.id} with isolated data:`, updateData);

      const updatedTemplate = await updateTemplate(template.id, updateData);
      
      // Wait a moment for the update to propagate to prevent race conditions
      await new Promise(resolve => setTimeout(resolve, 500));
      
      // Then apply it to DEFAULT warehouse for testing (isolated operation)
      await applyTemplate(template.id, 'DEFAULT', `Testing ${formData.name}`, true);
      
      console.log(`Template ${template.id} updated and applied successfully, operations isolated`);
      
      // Update local state to reflect successful save
      setOriginalData(formData);
      
      if (onTemplateUpdated) {
        onTemplateUpdated(updatedTemplate);
      }
      
      onClose();
    } catch (error: any) {
      console.error('Failed to save and test template:', error);
      setError(error?.response?.data?.error || 'Failed to update and test template. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  const handleCancel = () => {
    if (template) {
      setFormData(originalData);
    }
    onClose();
  };

  const calculateTotals = () => {
    const storageLocations = formData.num_aisles * formData.racks_per_aisle * 
                            formData.positions_per_rack * formData.levels_per_position;
    const storageCapacity = storageLocations * formData.default_pallet_capacity;
    
    const specialCapacity = [
      ...formData.receiving_areas_template,
      ...formData.staging_areas_template,
      ...formData.dock_areas_template
    ].reduce((sum, area) => sum + area.capacity, 0);
    
    return { 
      storageLocations, 
      storageCapacity, 
      specialAreas: formData.receiving_areas_template.length + 
                   formData.staging_areas_template.length + 
                   formData.dock_areas_template.length,
      specialCapacity,
      totalCapacity: storageCapacity + specialCapacity
    };
  };

  const { storageLocations, storageCapacity, specialAreas, specialCapacity, totalCapacity } = calculateTotals();

  if (!template) return null;

  return (
    <Dialog open={open} onOpenChange={onClose}>
      <DialogContent className="max-w-6xl max-h-[90vh] overflow-y-auto">
        <DialogHeader>
          <DialogTitle className="flex items-center gap-2">
            <Building2 className="h-5 w-5" />
            Edit Template: {template.name}
          </DialogTitle>
          <DialogDescription>
            Modify the complete template structure including dimensions and special areas. Changes affect future applications.
          </DialogDescription>
          <div className="flex items-center gap-2 mt-2">
            <Badge variant="outline" className="text-xs">
              Code: {template.template_code}
            </Badge>
            <Badge variant={template.is_public ? 'default' : 'secondary'} className="text-xs">
              {template.is_public ? (
                <>
                  <Globe className="h-3 w-3 mr-1" />
                  Public
                </>
              ) : (
                <>
                  <Lock className="h-3 w-3 mr-1" />
                  Private
                </>
              )}
            </Badge>
            <Badge variant="outline" className="text-xs">
              Used {template.usage_count || 0} times
            </Badge>
          </div>
        </DialogHeader>

        {error && (
          <Alert variant="destructive">
            <AlertCircle className="h-4 w-4" />
            <AlertDescription>{error}</AlertDescription>
          </Alert>
        )}

        <Tabs defaultValue="structure" className="w-full">
          <TabsList className="grid w-full grid-cols-4">
            <TabsTrigger value="structure">Structure</TabsTrigger>
            <TabsTrigger value="special-areas">Special Areas</TabsTrigger>
            <TabsTrigger value="settings">Settings</TabsTrigger>
            <TabsTrigger value="preview">Preview</TabsTrigger>
          </TabsList>

          <TabsContent value="structure" className="space-y-4">
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <Grid3X3 className="h-5 w-5" />
                  Warehouse Structure
                </CardTitle>
                <CardDescription>
                  Define the physical layout dimensions of the warehouse
                </CardDescription>
              </CardHeader>
              <CardContent className="space-y-4">
                <div className="grid grid-cols-2 gap-4">
                  <div className="space-y-2">
                    <Label htmlFor="num_aisles">Number of Aisles</Label>
                    <Input
                      id="num_aisles"
                      type="number"
                      min="1"
                      value={formData.num_aisles}
                      onChange={(e) => handleInputChange('num_aisles', parseInt(e.target.value) || 0)}
                    />
                  </div>
                  <div className="space-y-2">
                    <Label htmlFor="racks_per_aisle">Racks per Aisle</Label>
                    <Input
                      id="racks_per_aisle"
                      type="number"
                      min="1"
                      value={formData.racks_per_aisle}
                      onChange={(e) => handleInputChange('racks_per_aisle', parseInt(e.target.value) || 0)}
                    />
                  </div>
                  <div className="space-y-2">
                    <Label htmlFor="positions_per_rack">Positions per Rack</Label>
                    <Input
                      id="positions_per_rack"
                      type="number"
                      min="1"
                      value={formData.positions_per_rack}
                      onChange={(e) => handleInputChange('positions_per_rack', parseInt(e.target.value) || 0)}
                    />
                  </div>
                  <div className="space-y-2">
                    <Label htmlFor="levels_per_position">Levels per Position</Label>
                    <Input
                      id="levels_per_position"
                      type="number"
                      min="1"
                      value={formData.levels_per_position}
                      onChange={(e) => handleInputChange('levels_per_position', parseInt(e.target.value) || 0)}
                    />
                  </div>
                  <div className="space-y-2">
                    <Label htmlFor="level_names">Level Names</Label>
                    <Input
                      id="level_names"
                      value={formData.level_names}
                      onChange={(e) => handleInputChange('level_names', e.target.value)}
                      placeholder="e.g., ABCD"
                    />
                  </div>
                  <div className="space-y-2">
                    <Label htmlFor="default_pallet_capacity">Default Pallet Capacity</Label>
                    <Input
                      id="default_pallet_capacity"
                      type="number"
                      min="1"
                      value={formData.default_pallet_capacity}
                      onChange={(e) => handleInputChange('default_pallet_capacity', parseInt(e.target.value) || 0)}
                    />
                  </div>
                </div>
                
                <div className="flex items-center space-x-2">
                  <Switch
                    id="bidimensional_racks"
                    checked={formData.bidimensional_racks}
                    onCheckedChange={(checked) => handleInputChange('bidimensional_racks', checked)}
                  />
                  <Label htmlFor="bidimensional_racks" className="cursor-pointer">
                    Bidimensional Racks (2 pallets per level)
                  </Label>
                </div>
              </CardContent>
            </Card>
          </TabsContent>

          <TabsContent value="special-areas" className="space-y-4">
            {/* Information about Location as Source of Truth */}
            <Alert>
              <Info className="h-4 w-4" />
              <AlertDescription>
                <strong>Special Areas Editing:</strong> These special areas reflect your current warehouse configuration. 
                Edit special areas in the <strong>Locations tab</strong> to make changes. Template editing captures the current state when saved.
                {locations && locations.length > 0 && (
                  <div className="mt-2 text-xs text-muted-foreground">
                    Currently showing {locations.filter(l => ['RECEIVING', 'STAGING', 'DOCK'].includes(l.location_type)).length} special area locations from your warehouse.
                  </div>
                )}
              </AlertDescription>
            </Alert>

            {/* Receiving Areas */}
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <Truck className="h-5 w-5" />
                  Receiving Areas
                </CardTitle>
                <CardDescription>Areas for incoming inventory and deliveries</CardDescription>
              </CardHeader>
              <CardContent>
                <div className="space-y-2">
                  {formData.receiving_areas_template.map((area, index) => (
                    <div key={index} className="flex items-center gap-2 p-3 bg-gray-50 border rounded">
                      <div className="flex-1 grid grid-cols-3 gap-2">
                        <div className="p-2 text-sm">
                          <span className="font-medium">{area.code || 'Unnamed'}</span>
                        </div>
                        <div className="p-2 text-sm text-muted-foreground">
                          Capacity: {area.capacity}
                        </div>
                        <div className="p-2 text-sm text-muted-foreground">
                          Zone: {area.zone}
                        </div>
                      </div>
                      <div className="text-xs text-muted-foreground px-2">
                        Read-only
                      </div>
                    </div>
                  ))}
                  {formData.receiving_areas_template.length === 0 && (
                    <div className="text-center py-4 text-muted-foreground">
                      No receiving areas defined in your warehouse. Create them in the <strong>Locations tab</strong>.
                    </div>
                  )}
                </div>
              </CardContent>
            </Card>

            {/* Staging Areas */}
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <Package className="h-5 w-5" />
                  Staging Areas
                </CardTitle>
                <CardDescription>Temporary holding areas for order preparation</CardDescription>
              </CardHeader>
              <CardContent>
                <div className="space-y-2">
                  {formData.staging_areas_template.map((area, index) => (
                    <div key={index} className="flex items-center gap-2 p-3 bg-gray-50 border rounded">
                      <div className="flex-1 grid grid-cols-3 gap-2">
                        <div className="p-2 text-sm">
                          <span className="font-medium">{area.code || 'Unnamed'}</span>
                        </div>
                        <div className="p-2 text-sm text-muted-foreground">
                          Capacity: {area.capacity}
                        </div>
                        <div className="p-2 text-sm text-muted-foreground">
                          Zone: {area.zone}
                        </div>
                      </div>
                      <div className="text-xs text-muted-foreground px-2">
                        Read-only
                      </div>
                    </div>
                  ))}
                  {formData.staging_areas_template.length === 0 && (
                    <div className="text-center py-4 text-muted-foreground">
                      No staging areas defined in your warehouse. Create them in the <strong>Locations tab</strong>.
                    </div>
                  )}
                </div>
              </CardContent>
            </Card>

            {/* Dock Areas */}
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <MapPin className="h-5 w-5" />
                  Dock Areas
                </CardTitle>
                <CardDescription>Loading and shipping dock locations</CardDescription>
              </CardHeader>
              <CardContent>
                <div className="space-y-2">
                  {formData.dock_areas_template.map((area, index) => (
                    <div key={index} className="flex items-center gap-2 p-3 bg-gray-50 border rounded">
                      <div className="flex-1 grid grid-cols-3 gap-2">
                        <div className="p-2 text-sm">
                          <span className="font-medium">{area.code || 'Unnamed'}</span>
                        </div>
                        <div className="p-2 text-sm text-muted-foreground">
                          Capacity: {area.capacity}
                        </div>
                        <div className="p-2 text-sm text-muted-foreground">
                          Zone: {area.zone}
                        </div>
                      </div>
                      <div className="text-xs text-muted-foreground px-2">
                        Read-only
                      </div>
                    </div>
                  ))}
                  {formData.dock_areas_template.length === 0 && (
                    <div className="text-center py-4 text-muted-foreground">
                      No dock areas defined in your warehouse. Create them in the <strong>Locations tab</strong>.
                    </div>
                  )}
                </div>
              </CardContent>
            </Card>
          </TabsContent>

          <TabsContent value="settings" className="space-y-4">
            <Card>
              <CardHeader>
                <CardTitle className="text-lg">Template Information</CardTitle>
                <CardDescription>Basic template details and visibility settings</CardDescription>
              </CardHeader>
              <CardContent className="space-y-4">
                <div className="space-y-2">
                  <Label htmlFor="name">Template Name</Label>
                  <Input
                    id="name"
                    value={formData.name}
                    onChange={(e) => handleInputChange('name', e.target.value)}
                    placeholder="Enter template name"
                  />
                </div>
                <div className="space-y-2">
                  <Label htmlFor="description">Description</Label>
                  <Textarea
                    id="description"
                    value={formData.description}
                    onChange={(e) => handleInputChange('description', e.target.value)}
                    placeholder="Describe this template..."
                    rows={3}
                  />
                </div>
                <div className="flex items-center space-x-2">
                  <Switch
                    id="is_public"
                    checked={formData.is_public}
                    onCheckedChange={(checked) => handleInputChange('is_public', checked)}
                  />
                  <Label htmlFor="is_public" className="cursor-pointer flex items-center gap-2">
                    {formData.is_public ? <Globe className="h-4 w-4" /> : <Lock className="h-4 w-4" />}
                    Make template public (visible to all users)
                  </Label>
                </div>
              </CardContent>
            </Card>
          </TabsContent>

          <TabsContent value="preview" className="space-y-4">
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <Calculator className="h-5 w-5" />
                  Template Summary
                </CardTitle>
                <CardDescription>
                  Preview of the template configuration and calculated totals
                </CardDescription>
              </CardHeader>
              <CardContent className="space-y-4">
                <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                  <div className="text-center p-4 border rounded">
                    <div className="text-2xl font-bold">{storageLocations.toLocaleString()}</div>
                    <div className="text-sm text-muted-foreground">Storage Locations</div>
                  </div>
                  <div className="text-center p-4 border rounded">
                    <div className="text-2xl font-bold">{specialAreas}</div>
                    <div className="text-sm text-muted-foreground">Special Areas</div>
                  </div>
                  <div className="text-center p-4 border rounded">
                    <div className="text-2xl font-bold">{storageCapacity.toLocaleString()}</div>
                    <div className="text-sm text-muted-foreground">Storage Capacity</div>
                  </div>
                  <div className="text-center p-4 border rounded">
                    <div className="text-2xl font-bold">{totalCapacity.toLocaleString()}</div>
                    <div className="text-sm text-muted-foreground">Total Capacity</div>
                  </div>
                </div>

                <div className="space-y-2">
                  <h4 className="font-medium">Structure:</h4>
                  <p className="text-sm text-muted-foreground">
                    {formData.num_aisles} aisles × {formData.racks_per_aisle} racks × {formData.positions_per_rack} positions × {formData.levels_per_position} levels
                  </p>
                  
                  <h4 className="font-medium">Special Areas:</h4>
                  <div className="text-sm text-muted-foreground space-y-1">
                    <div>• {formData.receiving_areas_template.length} receiving areas (capacity: {formData.receiving_areas_template.reduce((sum, area) => sum + area.capacity, 0)})</div>
                    <div>• {formData.staging_areas_template.length} staging areas (capacity: {formData.staging_areas_template.reduce((sum, area) => sum + area.capacity, 0)})</div>
                    <div>• {formData.dock_areas_template.length} dock areas (capacity: {formData.dock_areas_template.reduce((sum, area) => sum + area.capacity, 0)})</div>
                  </div>
                </div>
                
                {hasChanges && (
                  <Alert>
                    <Info className="h-4 w-4" />
                    <AlertDescription>
                      You have unsaved changes. Click "Save Changes" to update the template.
                    </AlertDescription>
                  </Alert>
                )}
              </CardContent>
            </Card>
          </TabsContent>
        </Tabs>

        {/* Action buttons */}
        <div className="flex justify-between pt-4 border-t">
          <Button variant="outline" onClick={handleCancel} disabled={loading}>
            <X className="h-4 w-4 mr-2" />
            Cancel
          </Button>
          
          <div className="flex gap-2">
            <Button 
              onClick={handleSave} 
              disabled={!hasChanges || loading}
              variant="outline"
              className="flex items-center gap-2"
            >
              {loading ? (
                <Loader2 className="h-4 w-4 animate-spin" />
              ) : (
                <Save className="h-4 w-4" />
              )}
              Save Only
            </Button>
            
            <Button 
              onClick={handleSaveAndTest} 
              disabled={!hasChanges || loading}
              className="flex items-center gap-2 bg-green-600 hover:bg-green-700"
            >
              {loading ? (
                <Loader2 className="h-4 w-4 animate-spin" />
              ) : (
                <Zap className="h-4 w-4" />
              )}
              Save & Test Now
            </Button>
          </div>
        </div>
      </DialogContent>
    </Dialog>
  );
}