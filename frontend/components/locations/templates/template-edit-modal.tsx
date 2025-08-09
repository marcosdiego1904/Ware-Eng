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
import useLocationStore, { WarehouseTemplate } from '@/lib/location-store';
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
  RefreshCw
} from 'lucide-react';

interface TemplateEditModalProps {
  template: WarehouseTemplate | null;
  open: boolean;
  onClose: () => void;
  onTemplateUpdated?: (template: WarehouseTemplate) => void;
}

export function TemplateEditModal({ 
  template, 
  open, 
  onClose, 
  onTemplateUpdated 
}: TemplateEditModalProps) {
  const { updateTemplate, loading, error } = useLocationStore();
  
  // Form state
  const [formData, setFormData] = useState({
    name: '',
    description: '',
    num_aisles: 0,
    racks_per_aisle: 0,
    positions_per_rack: 0,
    levels_per_position: 0,
    level_names: '',
    default_pallet_capacity: 0,
    bidimensional_racks: false,
    is_public: false
  });
  
  const [originalData, setOriginalData] = useState(formData);
  const [hasChanges, setHasChanges] = useState(false);

  // Populate form when template changes
  useEffect(() => {
    if (template) {
      const templateFormData = {
        name: template.name || '',
        description: template.description || '',
        num_aisles: template.num_aisles || 0,
        racks_per_aisle: template.racks_per_aisle || 0,
        positions_per_rack: template.positions_per_rack || 0,
        levels_per_position: template.levels_per_position || 0,
        level_names: template.level_names || '',
        default_pallet_capacity: template.default_pallet_capacity || 0,
        bidimensional_racks: template.bidimensional_racks || false,
        is_public: template.is_public || false
      };
      setFormData(templateFormData);
      setOriginalData(templateFormData);
    }
  }, [template]);

  // Check for changes
  useEffect(() => {
    const changed = JSON.stringify(formData) !== JSON.stringify(originalData);
    setHasChanges(changed);
  }, [formData, originalData]);

  const handleInputChange = (field: string, value: string | number | boolean) => {
    setFormData(prev => ({
      ...prev,
      [field]: value
    }));
  };

  const handleSave = async () => {
    if (!template || !hasChanges) return;

    try {
      const updatedTemplate = await updateTemplate(template.id, formData);
      
      // Show success message
      alert('Template updated successfully!');
      
      // Reset form state
      setOriginalData(formData);
      
      // Notify parent component
      if (onTemplateUpdated) {
        onTemplateUpdated(updatedTemplate);
      }
      
      onClose();
    } catch (error) {
      console.error('Failed to update template:', error);
      // Error is handled by the store and displayed in the UI
    }
  };

  const handleCancel = () => {
    // Reset form to original values
    if (template) {
      setFormData(originalData);
    }
    onClose();
  };

  const calculateTotals = () => {
    const storageLocations = formData.num_aisles * formData.racks_per_aisle * 
                            formData.positions_per_rack * formData.levels_per_position;
    const storageCapacity = storageLocations * formData.default_pallet_capacity;
    
    return { storageLocations, storageCapacity };
  };

  const { storageLocations, storageCapacity } = calculateTotals();

  if (!template) return null;

  return (
    <Dialog open={open} onOpenChange={onClose}>
      <DialogContent className="max-w-4xl max-h-[90vh] overflow-y-auto">
        <DialogHeader>
          <DialogTitle className="flex items-center gap-2">
            <Building2 className="h-5 w-5" />
            Edit Template: {template.name}
          </DialogTitle>
          <DialogDescription>
            Modify template settings. Changes will affect future applications of this template.
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

        <div className="space-y-6">
          {/* Basic Information */}
          <Card>
            <CardHeader>
              <CardTitle className="text-lg">Template Information</CardTitle>
              <CardDescription>Basic template details and visibility settings</CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="grid grid-cols-1 gap-4">
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
                    placeholder="Describe this template's purpose and characteristics"
                    rows={3}
                  />
                </div>
                <div className="flex items-center space-x-2">
                  <Switch
                    id="is_public"
                    checked={formData.is_public}
                    onCheckedChange={(checked) => handleInputChange('is_public', checked)}
                  />
                  <Label htmlFor="is_public" className="cursor-pointer">
                    Make this template public (visible to all users)
                  </Label>
                </div>
              </div>
            </CardContent>
          </Card>

          {/* Warehouse Structure */}
          <Card>
            <CardHeader>
              <CardTitle className="text-lg">Warehouse Structure</CardTitle>
              <CardDescription>Define the physical layout and capacity of the warehouse</CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
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
              </div>

              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div className="space-y-2">
                  <Label htmlFor="level_names">Level Names</Label>
                  <Input
                    id="level_names"
                    value={formData.level_names}
                    onChange={(e) => handleInputChange('level_names', e.target.value)}
                    placeholder="e.g., ABCD"
                  />
                  <p className="text-xs text-muted-foreground">
                    Characters representing each level (e.g., A, B, C, D)
                  </p>
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
                  <p className="text-xs text-muted-foreground">
                    Number of pallets per level
                  </p>
                </div>
              </div>

              <div className="flex items-center space-x-2">
                <Switch
                  id="bidimensional_racks"
                  checked={formData.bidimensional_racks}
                  onCheckedChange={(checked) => handleInputChange('bidimensional_racks', checked)}
                />
                <Label htmlFor="bidimensional_racks" className="cursor-pointer">
                  Bidimensional racks (2 pallets per level instead of 1)
                </Label>
              </div>
            </CardContent>
          </Card>

          {/* Live Preview */}
          <Card>
            <CardHeader>
              <CardTitle className="text-lg flex items-center gap-2">
                <Grid3X3 className="h-5 w-5" />
                Live Preview
              </CardTitle>
              <CardDescription>Real-time calculation of warehouse capacity</CardDescription>
            </CardHeader>
            <CardContent>
              <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                <div className="space-y-2">
                  <div className="flex items-center gap-2 text-sm font-medium text-muted-foreground">
                    <Building2 className="h-4 w-4" />
                    Structure
                  </div>
                  <div className="text-2xl font-bold">
                    {formData.num_aisles}A × {formData.racks_per_aisle}R × {formData.positions_per_rack}P × {formData.levels_per_position}L
                  </div>
                </div>
                <div className="space-y-2">
                  <div className="flex items-center gap-2 text-sm font-medium text-muted-foreground">
                    <Package className="h-4 w-4" />
                    Storage Locations
                  </div>
                  <div className="text-2xl font-bold text-primary">
                    {storageLocations.toLocaleString()}
                  </div>
                </div>
                <div className="space-y-2">
                  <div className="flex items-center gap-2 text-sm font-medium text-muted-foreground">
                    <Package className="h-4 w-4" />
                    Pallet Capacity
                  </div>
                  <div className="text-2xl font-bold text-primary">
                    {storageCapacity.toLocaleString()}
                  </div>
                </div>
              </div>
            </CardContent>
          </Card>
        </div>

        {/* Footer Actions */}
        <div className="flex justify-between items-center pt-4 border-t">
          <div className="text-sm text-muted-foreground">
            {hasChanges ? (
              <span className="flex items-center gap-1 text-amber-600">
                <RefreshCw className="h-3 w-3" />
                You have unsaved changes
              </span>
            ) : (
              'No changes made'
            )}
          </div>
          <div className="flex gap-2">
            <Button 
              variant="outline" 
              onClick={handleCancel}
              disabled={loading}
            >
              <X className="h-4 w-4 mr-2" />
              Cancel
            </Button>
            <Button 
              onClick={handleSave} 
              disabled={!hasChanges || loading}
            >
              {loading ? (
                <Loader2 className="h-4 w-4 mr-2 animate-spin" />
              ) : (
                <Save className="h-4 w-4 mr-2" />
              )}
              Save Changes
            </Button>
          </div>
        </div>
      </DialogContent>
    </Dialog>
  );
}