'use client';

import React, { useState, useEffect, useCallback } from 'react';
import { useForm } from 'react-hook-form';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Alert, AlertDescription } from '@/components/ui/alert';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select';
import { Checkbox } from '@/components/ui/checkbox';
import useLocationStore, { Location } from '@/lib/location-store';
import { useToast } from '@/hooks/use-toast';
import {
  AlertCircle,
  MapPin,
  Loader2,
  Save,
  X,
  CheckCircle,
  AlertTriangle
} from 'lucide-react';

interface BulkLocationRangeTabProps {
  warehouseId: string;
  onClose: () => void;
  onSave: (locations: Location[]) => void;
}

interface BulkRangeFormData {
  prefix: string;
  startNumber: number;
  endNumber: number;
  useLeadingZeros: boolean;
  locationType: 'RECEIVING' | 'STAGING' | 'DOCK' | 'TRANSITIONAL';
  zone: string;
  palletCapacity: number;
}

export function BulkLocationRangeTab({ warehouseId, onClose, onSave }: BulkLocationRangeTabProps) {
  const { bulkCreateLocationRange, previewLocationRange, loading } = useLocationStore();
  const { toast } = useToast();

  const [preview, setPreview] = useState<{
    location_codes: string[];
    duplicates: string[];
    warnings: string[];
    summary: any;
  } | null>(null);
  const [isLoadingPreview, setIsLoadingPreview] = useState(false);
  const [capacityWarnings, setCapacityWarnings] = useState<string[]>([]);

  const {
    register,
    handleSubmit,
    watch,
    setValue,
    formState: { errors },
  } = useForm<BulkRangeFormData>({
    defaultValues: {
      prefix: '',
      startNumber: 1,
      endNumber: 10,
      useLeadingZeros: true,
      locationType: 'TRANSITIONAL',
      zone: '',
      palletCapacity: 10,
    }
  });

  const prefix = watch('prefix');
  const startNumber = watch('startNumber');
  const endNumber = watch('endNumber');
  const useLeadingZeros = watch('useLeadingZeros');
  const locationType = watch('locationType');
  const palletCapacity = watch('palletCapacity');

  // Auto-set zone from prefix and normalize to uppercase
  useEffect(() => {
    if (prefix) {
      const cleanZone = prefix.replace('-', '').replace('_', '').trim().toUpperCase();
      setValue('zone', cleanZone);
    }
  }, [prefix, setValue]);

  // Validate capacity
  const validatePalletCapacity = useCallback((capacity: number, type: string) => {
    const warnings: string[] = [];

    if (!capacity || capacity <= 0) {
      warnings.push('❌ Pallet capacity must be greater than 0');
    } else if (capacity > 1000) {
      warnings.push('❌ Extremely high pallet capacity detected. This value seems incorrect.');
    } else if (capacity > 100) {
      warnings.push('⚠️ Very high pallet capacity detected. Please verify this is correct.');
    } else if (capacity > 50 && (type === 'RECEIVING' || type === 'STAGING')) {
      warnings.push('⚠️ Very high capacity for this location type. Please verify this is accurate.');
    } else if (capacity > 25 && type === 'TRANSITIONAL') {
      warnings.push('⚠️ High capacity for transitional location. Typical values are 5-15 pallets.');
    }

    setCapacityWarnings(warnings);
  }, []);

  useEffect(() => {
    if (palletCapacity) {
      validatePalletCapacity(palletCapacity, locationType);
    }
  }, [palletCapacity, locationType, validatePalletCapacity]);

  // Generate preview when form changes
  useEffect(() => {
    const generatePreview = async () => {
      if (!prefix || startNumber >= endNumber) {
        setPreview(null);
        return;
      }

      setIsLoadingPreview(true);
      try {
        const previewData = await previewLocationRange({
          prefix,
          start_number: startNumber,
          end_number: endNumber,
          use_leading_zeros: useLeadingZeros,
          warehouse_id: warehouseId,
          pallet_capacity: palletCapacity,
        });

        setPreview({
          ...previewData,
          summary: (previewData as any).summary || null
        });
      } catch (error: any) {
        console.error('Preview error:', error);
        setPreview(null);
      } finally {
        setIsLoadingPreview(false);
      }
    };

    const timeoutId = setTimeout(generatePreview, 500);
    return () => clearTimeout(timeoutId);
  }, [prefix, startNumber, endNumber, useLeadingZeros, warehouseId, palletCapacity, previewLocationRange]);

  const onSubmit = async (data: BulkRangeFormData) => {
    // Confirm if there are warnings
    if (capacityWarnings.length > 0 && capacityWarnings.some(w => w.includes('❌'))) {
      const confirmed = confirm(
        `There are issues with the pallet capacity (${data.palletCapacity}):\n\n${capacityWarnings.join('\n')}\n\nDo you want to continue anyway?`
      );
      if (!confirmed) return;
    }

    // Confirm if duplicates
    if (preview && preview.duplicates.length > 0) {
      const confirmed = confirm(
        `${preview.duplicates.length} location(s) already exist:\n${preview.duplicates.slice(0, 5).join(', ')}${preview.duplicates.length > 5 ? '...' : ''}\n\nPlease remove these locations first or use different codes.`
      );
      if (!confirmed) return;
    }

    try {
      const result = await bulkCreateLocationRange({
        prefix: data.prefix,
        start_number: data.startNumber,
        end_number: data.endNumber,
        use_leading_zeros: data.useLeadingZeros,
        location_type: data.locationType,
        zone: data.zone,
        pallet_capacity: data.palletCapacity,
        warehouse_id: warehouseId,
      });

      if (result.created_count > 0) {
        toast({
          title: "Locations Created Successfully",
          description: `✅ Created ${result.created_count} location(s) (${data.prefix}${data.startNumber} to ${data.prefix}${data.endNumber})`,
        });
        onSave([] as Location[]); // Trigger refresh
        onClose();
      } else if ((result as any).error_count > 0) {
        toast({
          title: "Creation Failed",
          description: `❌ ${result.errors[0] || 'Failed to create locations'}`,
          variant: "destructive",
        });
      }
    } catch (error: any) {
      console.error('Bulk range creation error:', error);

      // Handle duplicate error
      if (error.response?.status === 409) {
        const duplicates = error.response?.data?.duplicates || [];
        toast({
          title: "Duplicate Locations Found",
          description: `${duplicates.length} location(s) already exist. Please remove them first.`,
          variant: "destructive",
        });
      } else {
        toast({
          title: "Creation Failed",
          description: error.response?.data?.error || 'Failed to create location range. Please try again.',
          variant: "destructive",
        });
      }
    }
  };

  const rangeSize = endNumber - startNumber + 1;

  return (
    <form onSubmit={handleSubmit(onSubmit)} className="space-y-6">
      {/* Location Pattern Section */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <MapPin className="h-5 w-5" />
            Location Pattern
          </CardTitle>
          <CardDescription>
            Define the prefix and number range for your locations
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div className="space-y-2">
              <Label htmlFor="prefix">Prefix *</Label>
              <Input
                id="prefix"
                {...register('prefix', {
                  required: 'Prefix is required',
                  maxLength: { value: 10, message: 'Prefix must be 10 characters or less' }
                })}
                placeholder="W-, X-, RECV-, DOCK-"
              />
              {errors.prefix && (
                <p className="text-sm text-destructive">{errors.prefix.message}</p>
              )}
              <p className="text-xs text-muted-foreground">
                Common: W-, X-, RECV-, DOCK-, AISLE- (will be converted to UPPERCASE)
              </p>
            </div>

            <div className="space-y-2">
              <Label>Number Range *</Label>
              <div className="flex items-center gap-2">
                <Input
                  type="number"
                  min="1"
                  {...register('startNumber', {
                    required: true,
                    valueAsNumber: true,
                    min: { value: 1, message: 'Must be at least 1' }
                  })}
                  placeholder="1"
                  className="w-24"
                />
                <span className="text-muted-foreground">to</span>
                <Input
                  type="number"
                  min="1"
                  {...register('endNumber', {
                    required: true,
                    valueAsNumber: true,
                    validate: value => value > startNumber || 'Must be greater than start number'
                  })}
                  placeholder="15"
                  className="w-24"
                />
              </div>
              {errors.endNumber && (
                <p className="text-sm text-destructive">{errors.endNumber.message}</p>
              )}
            </div>
          </div>

          <div className="flex items-center space-x-2">
            <Checkbox
              id="useLeadingZeros"
              checked={watch('useLeadingZeros')}
              onCheckedChange={(checked) => setValue('useLeadingZeros', checked === true)}
            />
            <Label htmlFor="useLeadingZeros" className="cursor-pointer">
              Use leading zeros (01, 02, 03 instead of 1, 2, 3)
            </Label>
          </div>

          {prefix && prefix !== prefix.toUpperCase() && (
            <Alert className="border-blue-500 bg-blue-50 dark:bg-blue-950">
              <AlertCircle className="h-4 w-4 text-blue-600" />
              <AlertDescription className="text-blue-700 dark:text-blue-400">
                💡 Location codes will be normalized to uppercase: <strong>{prefix.toUpperCase()}</strong>
              </AlertDescription>
            </Alert>
          )}
        </CardContent>
      </Card>

      {/* Location Details Section */}
      <Card>
        <CardHeader>
          <CardTitle>Location Details (Applied to All)</CardTitle>
          <CardDescription>
            These settings will be applied to all generated locations
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div className="space-y-2">
              <Label htmlFor="locationType">Type *</Label>
              <Select
                value={locationType}
                onValueChange={(value: any) => setValue('locationType', value)}
              >
                <SelectTrigger>
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="RECEIVING">Receiving</SelectItem>
                  <SelectItem value="STAGING">Staging</SelectItem>
                  <SelectItem value="DOCK">Dock</SelectItem>
                  <SelectItem value="TRANSITIONAL">Transitional</SelectItem>
                </SelectContent>
              </Select>
            </div>

            <div className="space-y-2">
              <Label htmlFor="zone">Zone</Label>
              <Input
                id="zone"
                {...register('zone')}
                placeholder="Auto-filled from prefix"
              />
            </div>
          </div>

          <div className="space-y-2">
            <Label htmlFor="palletCapacity">Pallet Capacity *</Label>
            <Input
              id="palletCapacity"
              type="number"
              min="1"
              {...register('palletCapacity', {
                valueAsNumber: true,
                min: { value: 1, message: 'Capacity must be at least 1' }
              })}
              placeholder="10"
            />
            {errors.palletCapacity && (
              <p className="text-sm text-destructive">{errors.palletCapacity.message}</p>
            )}
            <p className="text-xs text-muted-foreground">
              {locationType === 'RECEIVING' && 'Receiving: 5-30 pallets typical'}
              {locationType === 'STAGING' && 'Staging: 5-30 pallets typical'}
              {locationType === 'DOCK' && 'Dock: 5-20 pallets typical'}
              {locationType === 'TRANSITIONAL' && 'Transitional: 5-15 pallets typical (aisles, crossdocks)'}
            </p>
            {capacityWarnings.length > 0 && (
              <div className="space-y-1">
                {capacityWarnings.map((warning, index) => (
                  <p key={index} className="text-sm text-amber-600 dark:text-amber-400">
                    {warning}
                  </p>
                ))}
              </div>
            )}
          </div>
        </CardContent>
      </Card>

      {/* Preview Section */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            📊 Live Preview
            {isLoadingPreview && <Loader2 className="h-4 w-4 animate-spin" />}
          </CardTitle>
          <CardDescription>
            Preview of locations that will be created
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          {preview ? (
            <>
              {preview.summary.total_locations > 100 && (
                <Alert variant="destructive">
                  <AlertCircle className="h-4 w-4" />
                  <AlertDescription>
                    ❌ Range too large ({preview.summary.total_locations} locations). Maximum: 100 locations per batch.
                  </AlertDescription>
                </Alert>
              )}

              {preview.duplicates.length > 0 && (
                <Alert variant="destructive">
                  <AlertTriangle className="h-4 w-4" />
                  <AlertDescription>
                    ⚠️ {preview.duplicates.length} location(s) already exist: {preview.duplicates.slice(0, 3).join(', ')}
                    {preview.duplicates.length > 3 && '...'}
                  </AlertDescription>
                </Alert>
              )}

              {preview.warnings.map((warning, index) => (
                <Alert key={index}>
                  <AlertCircle className="h-4 w-4" />
                  <AlertDescription>{warning}</AlertDescription>
                </Alert>
              ))}

              {preview.summary.total_locations <= 100 && preview.duplicates.length === 0 && (
                <Alert className="border-green-500 bg-green-50 dark:bg-green-950">
                  <CheckCircle className="h-4 w-4 text-green-600" />
                  <AlertDescription className="text-green-700 dark:text-green-400">
                    ✅ Ready to create {preview.summary.total_new} location(s)
                  </AlertDescription>
                </Alert>
              )}

              <div className="space-y-2">
                <div className="text-sm font-medium">Generated Codes:</div>
                <div className="p-3 bg-muted rounded-md font-mono text-sm max-h-40 overflow-y-auto">
                  {preview.location_codes.slice(0, 20).join(', ')}
                  {preview.location_codes.length > 20 && ` ... (${preview.location_codes.length - 20} more)`}
                </div>
              </div>

              <div className="grid grid-cols-2 gap-4 text-sm">
                <div>
                  <span className="text-muted-foreground">Total Locations:</span>
                  <span className="ml-2 font-semibold">{preview.summary.total_locations}</span>
                </div>
                <div>
                  <span className="text-muted-foreground">Type:</span>
                  <span className="ml-2 font-semibold">{locationType}</span>
                </div>
                <div>
                  <span className="text-muted-foreground">Capacity Each:</span>
                  <span className="ml-2 font-semibold">{palletCapacity} pallets</span>
                </div>
                <div>
                  <span className="text-muted-foreground">Total Capacity:</span>
                  <span className="ml-2 font-semibold">{preview.summary.total_capacity} pallets</span>
                </div>
              </div>
            </>
          ) : (
            <div className="text-center py-8 text-muted-foreground">
              <AlertCircle className="h-12 w-12 mx-auto mb-4 opacity-50" />
              <p>Enter a prefix and range to see preview</p>
            </div>
          )}
        </CardContent>
      </Card>

      {/* Actions */}
      <div className="flex justify-end gap-2 pt-4">
        <Button type="button" variant="outline" onClick={onClose} disabled={loading}>
          <X className="h-4 w-4 mr-2" />
          Cancel
        </Button>
        <Button
          type="submit"
          disabled={loading || !preview || preview.summary.total_locations > 100 || preview.duplicates.length > 0}
        >
          {loading && <Loader2 className="h-4 w-4 mr-2 animate-spin" />}
          <Save className="h-4 w-4 mr-2" />
          Create {rangeSize} Location{rangeSize !== 1 ? 's' : ''}
        </Button>
      </div>
    </form>
  );
}
