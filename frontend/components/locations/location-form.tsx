'use client';

import React, { useState, useEffect } from 'react';
import { useForm } from 'react-hook-form';
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
import { Textarea } from '@/components/ui/textarea';
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select';
import { Switch } from '@/components/ui/switch';
import { Alert, AlertDescription } from '@/components/ui/alert';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Separator } from '@/components/ui/separator';
import useLocationStore, { Location } from '@/lib/location-store';
import { 
  AlertCircle, 
  MapPin, 
  Package, 
  Settings, 
  Building2,
  Loader2,
  Save,
  X
} from 'lucide-react';

interface LocationFormProps {
  location?: Location | null;
  warehouseId: string;
  onClose: () => void;
  onSave: (location: Location) => void;
}

interface LocationFormData {
  code: string;
  location_type: 'RECEIVING' | 'STORAGE' | 'STAGING' | 'DOCK';
  zone: string;
  capacity: number;
  pallet_capacity: number;
  aisle_number?: number;
  rack_number?: number;
  position_number?: number;
  level?: string;
  pattern?: string;
  allowed_products: string[];
  special_requirements: Record<string, any>;
  is_active: boolean;
}

export function LocationForm({ location, warehouseId, onClose, onSave }: LocationFormProps) {
  const { createLocation, updateLocation, loading, error } = useLocationStore();
  const [allowedProductsText, setAllowedProductsText] = useState('');
  const [specialRequirementsText, setSpecialRequirementsText] = useState('');
  const [isStorageLocation, setIsStorageLocation] = useState(false);
  const [formErrors, setFormErrors] = useState<Record<string, string>>({});

  const {
    register,
    handleSubmit,
    watch,
    setValue,
    formState: { errors },
    reset
  } = useForm<LocationFormData>({
    defaultValues: {
      code: '',
      location_type: 'STORAGE',
      zone: 'GENERAL',
      capacity: 1,
      pallet_capacity: 1,
      allowed_products: [],
      special_requirements: {},
      is_active: true
    }
  });

  const locationType = watch('location_type');

  // Initialize form when location prop changes
  useEffect(() => {
    if (location) {
      reset({
        code: location.code,
        location_type: location.location_type,
        zone: location.zone,
        capacity: location.capacity,
        pallet_capacity: location.pallet_capacity,
        aisle_number: location.aisle_number,
        rack_number: location.rack_number,
        position_number: location.position_number,
        level: location.level,
        pattern: location.pattern,
        allowed_products: location.allowed_products,
        special_requirements: location.special_requirements,
        is_active: location.is_active
      });
      
      setAllowedProductsText(location.allowed_products.join(', '));
      setSpecialRequirementsText(JSON.stringify(location.special_requirements, null, 2));
      setIsStorageLocation(location.is_storage_location);
    } else {
      reset();
      setAllowedProductsText('');
      setSpecialRequirementsText('{}');
      setIsStorageLocation(locationType === 'STORAGE');
    }
  }, [location, reset]);

  // Update storage location flag when type changes
  useEffect(() => {
    setIsStorageLocation(locationType === 'STORAGE');
  }, [locationType]);

  // Auto-generate code for storage locations
  const handleStructureChange = () => {
    if (isStorageLocation) {
      const aisleNum = watch('aisle_number');
      const rackNum = watch('rack_number');
      const posNum = watch('position_number');
      const level = watch('level');
      
      if (posNum && level) {
        const code = `${posNum.toString().padStart(3, '0')}${level}`;
        setValue('code', code);
      }
    }
  };

  const onSubmit = async (data: LocationFormData) => {
    setFormErrors({});
    
    try {
      // Parse allowed products
      const allowedProducts = allowedProductsText
        .split(',')
        .map(p => p.trim())
        .filter(p => p.length > 0);
      
      // Parse special requirements
      let specialRequirements = {};
      if (specialRequirementsText.trim()) {
        try {
          specialRequirements = JSON.parse(specialRequirementsText);
        } catch (e) {
          setFormErrors({ special_requirements: 'Invalid JSON format' });
          return;
        }
      }

      const locationData = {
        ...data,
        warehouse_id: warehouseId,
        allowed_products: allowedProducts,
        special_requirements: specialRequirements,
        // Clear structure fields for non-storage locations
        aisle_number: isStorageLocation ? data.aisle_number : undefined,
        rack_number: isStorageLocation ? data.rack_number : undefined,
        position_number: isStorageLocation ? data.position_number : undefined,
        level: isStorageLocation ? data.level : undefined,
      };

      let savedLocation;
      if (location) {
        savedLocation = await updateLocation(location.id, locationData);
      } else {
        savedLocation = await createLocation(locationData);
      }
      
      onSave(savedLocation);
    } catch (error) {
      console.error('Error saving location:', error);
    }
  };

  return (
    <Dialog open={true} onOpenChange={onClose}>
      <DialogContent className="max-w-4xl max-h-[90vh] overflow-y-auto">
        <DialogHeader>
          <DialogTitle className="flex items-center gap-2">
            <MapPin className="h-5 w-5" />
            {location ? 'Edit Location' : 'Add New Location'}
          </DialogTitle>
          <DialogDescription>
            {location 
              ? `Modify the details for location ${location.code}`
              : 'Create a new location in your warehouse'
            }
          </DialogDescription>
        </DialogHeader>

        <form onSubmit={handleSubmit(onSubmit)} className="space-y-6">
          {error && (
            <Alert variant="destructive">
              <AlertCircle className="h-4 w-4" />
              <AlertDescription>{error}</AlertDescription>
            </Alert>
          )}

          <Tabs defaultValue="basic" className="w-full">
            <TabsList className="grid w-full grid-cols-3">
              <TabsTrigger value="basic">Basic Info</TabsTrigger>
              <TabsTrigger value="structure">Structure</TabsTrigger>
              <TabsTrigger value="advanced">Advanced</TabsTrigger>
            </TabsList>

            <TabsContent value="basic" className="space-y-6">
              <Card>
                <CardHeader>
                  <CardTitle className="flex items-center gap-2">
                    <Package className="h-4 w-4" />
                    Location Details
                  </CardTitle>
                  <CardDescription>
                    Basic information about this location
                  </CardDescription>
                </CardHeader>
                <CardContent className="space-y-4">
                  <div className="grid grid-cols-2 gap-4">
                    <div className="space-y-2">
                      <Label htmlFor="code">Location Code *</Label>
                      <Input
                        id="code"
                        {...register('code', { 
                          required: 'Location code is required',
                          minLength: { value: 1, message: 'Code must be at least 1 character' }
                        })}
                        placeholder="e.g., 001A, RECEIVING"
                      />
                      {errors.code && (
                        <p className="text-sm text-destructive">{errors.code.message}</p>
                      )}
                    </div>

                    <div className="space-y-2">
                      <Label htmlFor="location_type">Location Type *</Label>
                      <Select
                        value={locationType}
                        onValueChange={(value) => setValue('location_type', value as any)}
                      >
                        <SelectTrigger>
                          <SelectValue />
                        </SelectTrigger>
                        <SelectContent>
                          <SelectItem value="STORAGE">Storage</SelectItem>
                          <SelectItem value="RECEIVING">Receiving</SelectItem>
                          <SelectItem value="STAGING">Staging</SelectItem>
                          <SelectItem value="DOCK">Dock</SelectItem>
                        </SelectContent>
                      </Select>
                    </div>
                  </div>

                  <div className="grid grid-cols-2 gap-4">
                    <div className="space-y-2">
                      <Label htmlFor="zone">Zone</Label>
                      <Input
                        id="zone"
                        {...register('zone')}
                        placeholder="e.g., GENERAL, FREEZER, HAZMAT"
                      />
                    </div>

                    <div className="space-y-2">
                      <Label htmlFor="pallet_capacity">Pallet Capacity</Label>
                      <Input
                        id="pallet_capacity"
                        type="number"
                        min="1"
                        {...register('pallet_capacity', { 
                          valueAsNumber: true,
                          min: { value: 1, message: 'Capacity must be at least 1' }
                        })}
                        placeholder="Number of pallets"
                      />
                      {errors.pallet_capacity && (
                        <p className="text-sm text-destructive">{errors.pallet_capacity.message}</p>
                      )}
                    </div>
                  </div>

                  <div className="space-y-2">
                    <Label htmlFor="pattern">Location Pattern (Optional)</Label>
                    <Input
                      id="pattern"
                      {...register('pattern')}
                      placeholder="e.g., AISLE-*, 00[1-9][A-D]"
                    />
                    <p className="text-xs text-muted-foreground">
                      Regex pattern for matching multiple locations (optional)
                    </p>
                  </div>

                  <div className="flex items-center space-x-2">
                    <Switch
                      id="is_active"
                      checked={watch('is_active')}
                      onCheckedChange={(checked) => setValue('is_active', checked)}
                    />
                    <Label htmlFor="is_active">Location is active</Label>
                  </div>
                </CardContent>
              </Card>
            </TabsContent>

            <TabsContent value="structure" className="space-y-6">
              <Card>
                <CardHeader>
                  <CardTitle className="flex items-center gap-2">
                    <Building2 className="h-4 w-4" />
                    Physical Structure
                  </CardTitle>
                  <CardDescription>
                    {isStorageLocation 
                      ? 'Define the physical location within your warehouse hierarchy'
                      : 'Storage locations only - structure fields are not needed for special areas'
                    }
                  </CardDescription>
                </CardHeader>
                <CardContent>
                  {isStorageLocation ? (
                    <div className="space-y-4">
                      <div className="grid grid-cols-2 gap-4">
                        <div className="space-y-2">
                          <Label htmlFor="aisle_number">Aisle Number</Label>
                          <Input
                            id="aisle_number"
                            type="number"
                            min="1"
                            {...register('aisle_number', { 
                              valueAsNumber: true,
                              onChange: handleStructureChange
                            })}
                            placeholder="1, 2, 3..."
                          />
                        </div>

                        <div className="space-y-2">
                          <Label htmlFor="rack_number">Rack Number</Label>
                          <Input
                            id="rack_number"
                            type="number"
                            min="1"
                            {...register('rack_number', { 
                              valueAsNumber: true,
                              onChange: handleStructureChange
                            })}
                            placeholder="1, 2..."
                          />
                        </div>
                      </div>

                      <div className="grid grid-cols-2 gap-4">
                        <div className="space-y-2">
                          <Label htmlFor="position_number">Position Number</Label>
                          <Input
                            id="position_number"
                            type="number"
                            min="1"
                            {...register('position_number', { 
                              valueAsNumber: true,
                              onChange: handleStructureChange
                            })}
                            placeholder="1, 2, 3... 50, 100..."
                          />
                        </div>

                        <div className="space-y-2">
                          <Label htmlFor="level">Level</Label>
                          <Input
                            id="level"
                            {...register('level', {
                              onChange: handleStructureChange
                            })}
                            placeholder="A, B, C, D..."
                            maxLength={2}
                          />
                        </div>
                      </div>

                      <Alert>
                        <AlertCircle className="h-4 w-4" />
                        <AlertDescription>
                          When you enter position number and level, the location code will be auto-generated (e.g., 001A).
                        </AlertDescription>
                      </Alert>
                    </div>
                  ) : (
                    <div className="text-center py-12 text-muted-foreground">
                      <Building2 className="h-16 w-16 mx-auto mb-4 opacity-50" />
                      <p>Structure information is only applicable to storage locations.</p>
                      <p>Special areas like receiving, staging, and dock don't need hierarchy details.</p>
                    </div>
                  )}
                </CardContent>
              </Card>
            </TabsContent>

            <TabsContent value="advanced" className="space-y-6">
              <div className="grid gap-6">
                <Card>
                  <CardHeader>
                    <CardTitle>Allowed Products</CardTitle>
                    <CardDescription>
                      Specify which product patterns are allowed in this location
                    </CardDescription>
                  </CardHeader>
                  <CardContent>
                    <div className="space-y-2">
                      <Textarea
                        value={allowedProductsText}
                        onChange={(e) => setAllowedProductsText(e.target.value)}
                        placeholder="Enter product patterns separated by commas, e.g., FROZEN*, *HAZMAT*, PRODUCT-123"
                        rows={3}
                      />
                      <p className="text-xs text-muted-foreground">
                        Use asterisks (*) for wildcards. Leave empty to allow all products.
                      </p>
                    </div>
                  </CardContent>
                </Card>

                <Card>
                  <CardHeader>
                    <CardTitle>Special Requirements</CardTitle>
                    <CardDescription>
                      Additional requirements or metadata for this location (JSON format)
                    </CardDescription>
                  </CardHeader>
                  <CardContent>
                    <div className="space-y-2">
                      <Textarea
                        value={specialRequirementsText}
                        onChange={(e) => setSpecialRequirementsText(e.target.value)}
                        placeholder='{"temperature": "freezer", "hazmat_approved": true, "max_height": 10}'
                        rows={4}
                      />
                      {formErrors.special_requirements && (
                        <p className="text-sm text-destructive">{formErrors.special_requirements}</p>
                      )}
                      <p className="text-xs text-muted-foreground">
                        Valid JSON format required. Use empty object {} if no special requirements.
                      </p>
                    </div>
                  </CardContent>
                </Card>
              </div>
            </TabsContent>
          </Tabs>

          <Separator />

          <div className="flex justify-end gap-2">
            <Button type="button" variant="outline" onClick={onClose}>
              <X className="h-4 w-4 mr-2" />
              Cancel
            </Button>
            <Button type="submit" disabled={loading}>
              {loading && <Loader2 className="h-4 w-4 mr-2 animate-spin" />}
              <Save className="h-4 w-4 mr-2" />
              {location ? 'Update Location' : 'Create Location'}
            </Button>
          </div>
        </form>
      </DialogContent>
    </Dialog>
  );
}