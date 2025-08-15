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
import { useToast } from '@/hooks/use-toast';
import { 
  AlertCircle, 
  MapPin, 
  Package, 
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
  location_type: 'RECEIVING' | 'STORAGE' | 'STAGING' | 'DOCK' | 'TRANSITIONAL';
  zone: string;
  capacity: number;
  pallet_capacity: number;
  aisle_number?: number;
  rack_number?: number;
  position_number?: number;
  level?: string;
  pattern?: string;
  allowed_products: string[];
  special_requirements: Record<string, unknown>;
  is_active: boolean;
}

export function LocationForm({ location, warehouseId, onClose, onSave }: LocationFormProps) {
  const { createLocation, updateLocation, loading, error } = useLocationStore();
  const { toast } = useToast();
  const [allowedProductsText, setAllowedProductsText] = useState('');
  const [specialRequirementsText, setSpecialRequirementsText] = useState('');
  const [isStorageLocation, setIsStorageLocation] = useState(false);
  const [formErrors, setFormErrors] = useState<Record<string, string>>({});
  const [palletWarnings, setPalletWarnings] = useState<string[]>([]);

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
  const palletCapacity = watch('pallet_capacity');

  // Validate pallet capacity values
  const validatePalletCapacity = React.useCallback((capacity: number) => {
    console.log('🔍 validatePalletCapacity called with:', { capacity, locationType });
    const warnings: string[] = [];
    
    if (!capacity || capacity <= 0) {
      warnings.push('❌ Pallet capacity must be greater than 0');
    } else if (capacity > 1000) {
      warnings.push('❌ Extremely high pallet capacity detected. This value seems incorrect.');
    } else if (capacity > 100) {
      warnings.push('⚠️ Very high pallet capacity detected. Please verify this is correct.');
    } else if (capacity > 10 && locationType === 'STORAGE') {
      warnings.push('⚠️ High pallet capacity for storage location. Typical storage locations hold 1-2 pallets.');
    } else if (capacity > 50 && (locationType === 'RECEIVING' || locationType === 'STAGING')) {
      warnings.push('⚠️ Very high capacity for this location type. Please verify this is accurate.');
    } else if (capacity > 25 && locationType === 'TRANSITIONAL') {
      warnings.push('⚠️ High capacity for transitional location. Typical values are 5-15 pallets.');
    }
    
    // Check for suspicious values that might indicate typos
    const suspiciousValues = [11, 111, 123, 1234, 999, 9999];
    if (suspiciousValues.includes(capacity)) {
      warnings.push('🤔 This pallet capacity seems unusual. Did you mean to enter this value?');
    }
    
    // Validate against typical warehouse standards
    if (locationType === 'STORAGE' && capacity > 4) {
      warnings.push('💡 Most storage locations hold 1-4 pallets maximum. Double-check your entry.');
    } else if (locationType === 'DOCK' && capacity > 20) {
      warnings.push('💡 High capacity for dock location. Typical dock areas hold 5-20 pallets.');
    } else if ((locationType === 'RECEIVING' || locationType === 'STAGING') && capacity > 30) {
      warnings.push('💡 High capacity for this area type. Typical values are 5-30 pallets.');
    } else if (locationType === 'TRANSITIONAL' && capacity > 15) {
      warnings.push('💡 High capacity for transitional area. Typical values are 5-15 pallets.');
    }
    
    // Helpful suggestions
    if (capacity === 0) {
      warnings.push('💡 Tip: Even blocked locations usually have capacity 1. Use 0 only if completely unusable.');
    }
    
    console.log('🔍 Setting pallet warnings:', warnings);
    setPalletWarnings(warnings);
  }, [locationType]);

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
      
      // Trigger validation for existing location's pallet capacity
      if (location.pallet_capacity) {
        validatePalletCapacity(location.pallet_capacity);
      }
    } else {
      // Only reset non-user-controlled fields for new locations
      // Don't reset location_type to preserve user selection
      reset({
        code: '',
        location_type: locationType, // Preserve current selection
        zone: 'GENERAL',
        capacity: 1,
        pallet_capacity: 1,
        allowed_products: [],
        special_requirements: {},
        is_active: true
      });
      setAllowedProductsText('');
      setSpecialRequirementsText('{}');
      setIsStorageLocation(locationType === 'STORAGE');
      setPalletWarnings([]); // Clear warnings for new locations
    }
  }, [location, reset, validatePalletCapacity, locationType]);

  // Update storage location flag when type changes
  useEffect(() => {
    setIsStorageLocation(locationType === 'STORAGE');
  }, [locationType]);

  // Validate pallet capacity when it changes
  useEffect(() => {
    console.log('🔍 Pallet capacity validation triggered:', { palletCapacity, locationType });
    if (palletCapacity !== undefined && palletCapacity !== null && !isNaN(palletCapacity)) {
      validatePalletCapacity(palletCapacity);
    } else {
      setPalletWarnings([]);
    }
  }, [palletCapacity, validatePalletCapacity, locationType]);

  // Auto-generate code for storage locations
  const handleStructureChange = () => {
    if (isStorageLocation) {
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
    
    // Show confirmation if there are warnings about pallet capacity
    if (palletWarnings.length > 0 && palletWarnings.some(w => w.includes('❌'))) {
      const confirmed = confirm(
        `There are issues with the pallet capacity (${data.pallet_capacity}):\n\n${palletWarnings.join('\n')}\n\nDo you want to continue anyway?`
      );
      if (!confirmed) {
        return;
      }
    } else if (palletWarnings.length > 0) {
      const confirmed = confirm(
        `Please verify the pallet capacity (${data.pallet_capacity}):\n\n${palletWarnings.join('\n')}\n\nIs this value correct?`
      );
      if (!confirmed) {
        return;
      }
    }
    
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
        } catch {
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
      
      toast({
        title: location ? "Location Updated" : "Location Created",
        description: `Location ${savedLocation.code} has been ${location ? 'updated' : 'created'} successfully.`,
        variant: "success",
      });
      
      onSave(savedLocation);
    } catch (err: unknown) {
      const error = err as { response?: { data?: { error?: string } } };
      console.error('Error saving location:', error);
      
      toast({
        title: "Save Failed",
        description: error.response?.data?.error || `Failed to ${location ? 'update' : 'create'} location. Please try again.`,
        variant: "destructive",
      });
    }
  };

  return (
    <Dialog open={true} onOpenChange={onClose}>
      <DialogContent className="max-w-4xl max-h-[95vh] flex flex-col">
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

        <form onSubmit={handleSubmit(onSubmit)} className="flex-1 flex flex-col overflow-hidden">
          {error && (
            <Alert variant="destructive">
              <AlertCircle className="h-4 w-4" />
              <AlertDescription>{error}</AlertDescription>
            </Alert>
          )}

          <Tabs defaultValue="basic" className="flex-1 flex flex-col overflow-hidden">
            <TabsList className="grid w-full grid-cols-3">
              <TabsTrigger value="basic">Basic Info</TabsTrigger>
              <TabsTrigger value="structure">Structure</TabsTrigger>
              <TabsTrigger value="advanced">Advanced</TabsTrigger>
            </TabsList>

            <TabsContent value="basic" className="flex-1 overflow-y-auto space-y-6">
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
                        onValueChange={(value: LocationFormData['location_type']) => setValue('location_type', value)}
                      >
                        <SelectTrigger>
                          <SelectValue />
                        </SelectTrigger>
                        <SelectContent>
                          <SelectItem value="STORAGE">Storage</SelectItem>
                          <SelectItem value="RECEIVING">Receiving</SelectItem>
                          <SelectItem value="STAGING">Staging</SelectItem>
                          <SelectItem value="DOCK">Dock</SelectItem>
                          <SelectItem value="TRANSITIONAL">Transitional</SelectItem>
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
                          min: { value: 1, message: 'Capacity must be at least 1' },
                          onChange: (e) => {
                            const value = parseInt(e.target.value) || 0;
                            console.log('🔍 Pallet capacity input changed:', value);
                            validatePalletCapacity(value);
                          }
                        })}
                        placeholder="Number of pallets"
                      />
                      {errors.pallet_capacity && (
                        <p className="text-sm text-destructive">{errors.pallet_capacity.message}</p>
                      )}
                      <p className="text-xs text-muted-foreground">
                        {locationType === 'STORAGE' && 'Storage: 1-2 pallets typical, 4 maximum'}
                        {locationType === 'RECEIVING' && 'Receiving: 5-30 pallets typical'}
                        {locationType === 'STAGING' && 'Staging: 5-30 pallets typical'}
                        {locationType === 'DOCK' && 'Dock: 5-20 pallets typical'}
                        {locationType === 'TRANSITIONAL' && 'Transitional: 5-15 pallets typical (aisles, crossdocks)'}
                        {' • Validation active ✓'}
                      </p>
                      {palletWarnings.length > 0 && (
                        <div className="space-y-1">
                          {palletWarnings.map((warning, index) => (
                            <p key={index} className="text-sm text-amber-600 dark:text-amber-400 flex items-start gap-2">
                              {warning}
                            </p>
                          ))}
                        </div>
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

            <TabsContent value="structure" className="flex-1 overflow-y-auto space-y-6">
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
                          When you enter position number and level, the location code will be auto-generated (e.g., 01-02-015A).
                        </AlertDescription>
                      </Alert>
                    </div>
                  ) : (
                    <div className="text-center py-12 text-muted-foreground">
                      <Building2 className="h-16 w-16 mx-auto mb-4 opacity-50" />
                      <p>Structure information is only applicable to storage locations.</p>
                      <p>Special areas like receiving, staging, and dock don&apos;t need hierarchy details.</p>
                    </div>
                  )}
                </CardContent>
              </Card>
            </TabsContent>

            <TabsContent value="advanced" className="flex-1 overflow-y-auto space-y-6">
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

          <Separator className="mt-auto" />

          <div className="flex justify-end gap-2 pt-4">
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