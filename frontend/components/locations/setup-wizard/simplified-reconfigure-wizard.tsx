'use client';

import React, { useState } from 'react';
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogHeader,
  DialogTitle,
} from '@/components/ui/dialog';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Switch } from '@/components/ui/switch';
import { Alert, AlertDescription } from '@/components/ui/alert';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Separator } from '@/components/ui/separator';
import useLocationStore, { WarehouseConfig, WarehouseTemplate } from '@/lib/location-store';
import { 
  AlertTriangle,
  Building2, 
  RefreshCw,
  CheckCircle,
  Info,
  Loader2,
  Zap
} from 'lucide-react';

interface SimplifiedReconfigureWizardProps {
  existingConfig: WarehouseConfig | null;
  currentTemplate: WarehouseTemplate | null;
  warehouseId: string;
  onClose: () => void;
  onComplete: (config: WarehouseConfig) => void;
}

interface ReconfigureData {
  warehouse_name: string;
  force_recreate: boolean;
  clear_existing_data: boolean;
}

export function SimplifiedReconfigureWizard({ 
  existingConfig,
  currentTemplate,
  warehouseId,
  onClose, 
  onComplete 
}: SimplifiedReconfigureWizardProps) {
  const { setupWarehouse, loading, error } = useLocationStore();
  
  const [reconfigureData, setReconfigureData] = useState<ReconfigureData>({
    warehouse_name: existingConfig?.warehouse_name || '',
    force_recreate: false,
    clear_existing_data: false
  });

  const [step, setStep] = useState(1);
  const [, setIsProcessing] = useState(false);
  
  const handleInputChange = (field: keyof ReconfigureData, value: string | boolean) => {
    setReconfigureData(prev => ({
      ...prev,
      [field]: value
    }));
  };

  const handleReconfigure = async () => {
    if (!existingConfig || !currentTemplate) return;
    
    setIsProcessing(true);
    setStep(2);
    
    try {
      // Use existing template structure but apply with new settings
      const setupData = {
        warehouse_id: warehouseId,
        warehouse_name: reconfigureData.warehouse_name,
        
        // Use template structure (no changes to dimensions)
        num_aisles: currentTemplate.num_aisles,
        racks_per_aisle: currentTemplate.racks_per_aisle,
        positions_per_rack: currentTemplate.positions_per_rack,
        levels_per_position: currentTemplate.levels_per_position,
        level_names: currentTemplate.level_names,
        default_pallet_capacity: currentTemplate.default_pallet_capacity,
        bidimensional_racks: currentTemplate.bidimensional_racks,
        default_zone: existingConfig.default_zone,
        
        // Use template special areas
        receiving_areas: currentTemplate.receiving_areas_template || [],
        staging_areas: currentTemplate.staging_areas_template || [],
        dock_areas: currentTemplate.dock_areas_template || [],
        
        // Application settings
        generate_locations: true,
        force_recreate: reconfigureData.force_recreate,
        
        // Don't create new template - we're applying existing one
        create_template: false,
        template_name: '',
        template_description: '',
        template_is_public: false
      };
      
      const result = await setupWarehouse(setupData);
      
      setTimeout(() => {
        setStep(3);
        setTimeout(() => {
          onComplete(result.configuration);
          onClose();
        }, 1500);
      }, 2000);
      
    } catch (error) {
      console.error('Reconfiguration failed:', error);
      setIsProcessing(false);
      setStep(1);
    }
  };

  const calculatePreviewStats = () => {
    if (!currentTemplate) return { locations: 0, capacity: 0, specialAreas: 0 };
    
    const locations = currentTemplate.num_aisles * 
                     currentTemplate.racks_per_aisle * 
                     currentTemplate.positions_per_rack * 
                     currentTemplate.levels_per_position;
    
    const capacity = locations * currentTemplate.default_pallet_capacity;
    
    const specialAreas = (currentTemplate.receiving_areas_template?.length || 0) +
                        (currentTemplate.staging_areas_template?.length || 0) +
                        (currentTemplate.dock_areas_template?.length || 0);
    
    return { locations, capacity, specialAreas };
  };

  const { locations, capacity, specialAreas } = calculatePreviewStats();

  if (!existingConfig || !currentTemplate) {
    return null;
  }

  return (
    <Dialog open={true} onOpenChange={onClose}>
      <DialogContent className="max-w-2xl">
        <DialogHeader>
          <DialogTitle className="flex items-center gap-2">
            <RefreshCw className="h-5 w-5" />
            Reconfigure Warehouse
          </DialogTitle>
          <DialogDescription>
            Apply the current template structure to regenerate warehouse locations
          </DialogDescription>
        </DialogHeader>

        {error && (
          <Alert variant="destructive">
            <AlertTriangle className="h-4 w-4" />
            <AlertDescription>{error}</AlertDescription>
          </Alert>
        )}

        <div className="space-y-6">
          {step === 1 && (
            <>
              {/* Current Configuration */}
              <Card>
                <CardHeader>
                  <CardTitle className="flex items-center gap-2 text-lg">
                    <Building2 className="h-5 w-5" />
                    Current Configuration
                  </CardTitle>
                  <CardDescription>
                    Using template: <strong>{currentTemplate.name}</strong>
                  </CardDescription>
                </CardHeader>
                <CardContent className="space-y-4">
                  <div className="grid grid-cols-3 gap-4">
                    <div className="text-center p-3 bg-muted rounded">
                      <div className="text-xl font-bold">{locations.toLocaleString()}</div>
                      <div className="text-sm text-muted-foreground">Storage Locations</div>
                    </div>
                    <div className="text-center p-3 bg-muted rounded">
                      <div className="text-xl font-bold">{specialAreas}</div>
                      <div className="text-sm text-muted-foreground">Special Areas</div>
                    </div>
                    <div className="text-center p-3 bg-muted rounded">
                      <div className="text-xl font-bold">{capacity.toLocaleString()}</div>
                      <div className="text-sm text-muted-foreground">Total Capacity</div>
                    </div>
                  </div>
                  
                  <div className="text-sm text-muted-foreground">
                    <strong>Structure:</strong> {currentTemplate.num_aisles} aisles × {currentTemplate.racks_per_aisle} racks × {currentTemplate.positions_per_rack} positions × {currentTemplate.levels_per_position} levels
                  </div>

                  <Alert>
                    <Info className="h-4 w-4" />
                    <AlertDescription>
                      To modify the warehouse structure (dimensions, special areas), edit the template in the Templates tab instead.
                    </AlertDescription>
                  </Alert>
                </CardContent>
              </Card>

              {/* Application Settings */}
              <Card>
                <CardHeader>
                  <CardTitle className="text-lg">Application Settings</CardTitle>
                  <CardDescription>Configure how the template should be applied</CardDescription>
                </CardHeader>
                <CardContent className="space-y-4">
                  <div className="space-y-2">
                    <Label htmlFor="warehouse_name">Warehouse Instance Name</Label>
                    <Input
                      id="warehouse_name"
                      value={reconfigureData.warehouse_name}
                      onChange={(e) => handleInputChange('warehouse_name', e.target.value)}
                      placeholder="Enter warehouse name"
                    />
                  </div>

                  <Separator />

                  <div className="space-y-4">
                    <div className="flex items-center justify-between">
                      <div className="space-y-1">
                        <Label htmlFor="force_recreate" className="cursor-pointer">
                          Force Complete Regeneration
                        </Label>
                        <p className="text-sm text-muted-foreground">
                          Delete all existing locations and create fresh ones
                        </p>
                      </div>
                      <Switch
                        id="force_recreate"
                        checked={reconfigureData.force_recreate}
                        onCheckedChange={(checked) => handleInputChange('force_recreate', checked)}
                      />
                    </div>

                    {reconfigureData.force_recreate && (
                      <Alert variant="destructive">
                        <AlertTriangle className="h-4 w-4" />
                        <AlertDescription>
                          <strong>Warning:</strong> This will permanently delete all existing location data, 
                          including any custom locations you&apos;ve added. This action cannot be undone.
                        </AlertDescription>
                      </Alert>
                    )}
                  </div>
                </CardContent>
              </Card>

              {/* Action Buttons */}
              <div className="flex justify-end gap-2">
                <Button variant="outline" onClick={onClose}>
                  Cancel
                </Button>
                <Button 
                  onClick={handleReconfigure}
                  disabled={!reconfigureData.warehouse_name.trim() || loading}
                  className="flex items-center gap-2"
                >
                  <Zap className="h-4 w-4" />
                  Apply Configuration
                </Button>
              </div>
            </>
          )}

          {step === 2 && (
            <div className="text-center space-y-6 py-8">
              <div className="flex justify-center">
                <Loader2 className="h-12 w-12 animate-spin text-primary" />
              </div>
              <div>
                <h3 className="text-lg font-medium">Applying Configuration...</h3>
                <p className="text-muted-foreground">
                  {reconfigureData.force_recreate 
                    ? 'Regenerating all warehouse locations...' 
                    : 'Updating warehouse configuration...'
                  }
                </p>
              </div>
            </div>
          )}

          {step === 3 && (
            <div className="text-center space-y-6 py-8">
              <div className="flex justify-center">
                <CheckCircle className="h-12 w-12 text-green-500" />
              </div>
              <div>
                <h3 className="text-lg font-medium">Configuration Applied Successfully!</h3>
                <p className="text-muted-foreground">
                  Your warehouse has been reconfigured with the updated settings.
                </p>
              </div>
            </div>
          )}
        </div>
      </DialogContent>
    </Dialog>
  );
}