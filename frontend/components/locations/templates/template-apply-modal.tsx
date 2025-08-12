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
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Alert, AlertDescription } from '@/components/ui/alert';
import { Separator } from '@/components/ui/separator';
import { Progress } from '@/components/ui/progress';
import { 
  CheckCircle, 
  Building2, 
  Package, 
  Users, 
  AlertCircle,
  Loader2,
  ArrowRight,
  MapPin
} from 'lucide-react';

interface TemplateApplyModalProps {
  open: boolean;
  onClose: () => void;
  template: {
    name: string;
    template_code?: string;
    description?: string;
    num_aisles: number;
    racks_per_aisle: number;
    positions_per_rack: number;
    levels_per_position: number;
    default_pallet_capacity: number;
    receiving_areas?: any[];
    staging_areas?: any[];
    dock_areas?: any[];
  } | null;
  warehouseName?: string;
  warehouseId?: string;
  onApply?: () => Promise<any>;
  applyResult?: {
    success: boolean;
    locations_created?: number;
    storage_locations?: number;
    special_areas?: number;
    error?: string;
  } | null;
}

export function TemplateApplyModal({
  open,
  onClose,
  template,
  warehouseName,
  warehouseId,
  onApply,
  applyResult
}: TemplateApplyModalProps) {
  const [isApplying, setIsApplying] = useState(false);
  const [progress, setProgress] = useState(0);

  if (!template) return null;

  const handleApply = async () => {
    if (!onApply) return;
    
    setIsApplying(true);
    setProgress(0);
    
    try {
      // Simulate progress for better UX
      const progressInterval = setInterval(() => {
        setProgress(prev => Math.min(prev + 10, 90));
      }, 200);
      
      await onApply();
      
      clearInterval(progressInterval);
      setProgress(100);
      
    } catch (error) {
      console.error('Failed to apply template:', error);
    } finally {
      setIsApplying(false);
    }
  };

  const calculateTotals = () => {
    const storageLocations = template.num_aisles * template.racks_per_aisle * 
      template.positions_per_rack * template.levels_per_position;
    const storageCapacity = storageLocations * template.default_pallet_capacity;
    const specialAreas = (template.receiving_areas?.length || 0) + 
      (template.staging_areas?.length || 0) + (template.dock_areas?.length || 0);
    
    return { storageLocations, storageCapacity, specialAreas };
  };

  const totals = calculateTotals();

  // Show success state
  if (applyResult?.success) {
    return (
      <Dialog open={open} onOpenChange={onClose}>
        <DialogContent className="max-w-2xl">
          <DialogHeader>
            <DialogTitle className="flex items-center gap-2 text-green-600">
              <CheckCircle className="h-6 w-6" />
              Template Applied Successfully!
            </DialogTitle>
            <DialogDescription>
              Your warehouse has been configured with the {template.name} template
            </DialogDescription>
          </DialogHeader>

          <div className="space-y-6">
            <Card>
              <CardHeader>
                <CardTitle className="text-lg">Application Summary</CardTitle>
              </CardHeader>
              <CardContent className="space-y-4">
                <div className="grid grid-cols-2 gap-4 text-sm">
                  <div>
                    <div className="font-medium">Warehouse</div>
                    <div className="text-muted-foreground">
                      {warehouseName} ({warehouseId})
                    </div>
                  </div>
                  <div>
                    <div className="font-medium">Template</div>
                    <div className="text-muted-foreground">
                      {template.name} {template.template_code && `(${template.template_code})`}
                    </div>
                  </div>
                </div>

                <Separator />

                <div className="grid grid-cols-3 gap-4 text-center">
                  <div>
                    <div className="text-2xl font-bold text-blue-600">
                      {applyResult.locations_created?.toLocaleString() || totals.storageLocations.toLocaleString()}
                    </div>
                    <div className="text-sm text-muted-foreground">Total Locations</div>
                  </div>
                  <div>
                    <div className="text-2xl font-bold text-green-600">
                      {applyResult.storage_locations?.toLocaleString() || totals.storageLocations.toLocaleString()}
                    </div>
                    <div className="text-sm text-muted-foreground">Storage Locations</div>
                  </div>
                  <div>
                    <div className="text-2xl font-bold text-purple-600">
                      {applyResult.special_areas || totals.specialAreas}
                    </div>
                    <div className="text-sm text-muted-foreground">Special Areas</div>
                  </div>
                </div>
              </CardContent>
            </Card>

            <Alert>
              <MapPin className="h-4 w-4" />
              <AlertDescription>
                Your warehouse locations have been generated! Switch to the <strong>Locations tab</strong> to view and manage them.
              </AlertDescription>
            </Alert>
          </div>

          <div className="flex justify-end gap-2">
            <Button onClick={onClose}>
              <CheckCircle className="h-4 w-4 mr-2" />
              Done
            </Button>
          </div>
        </DialogContent>
      </Dialog>
    );
  }

  // Show error state
  if (applyResult && !applyResult.success) {
    return (
      <Dialog open={open} onOpenChange={onClose}>
        <DialogContent className="max-w-2xl">
          <DialogHeader>
            <DialogTitle className="flex items-center gap-2 text-red-600">
              <AlertCircle className="h-6 w-6" />
              Application Failed
            </DialogTitle>
            <DialogDescription>
              There was an error applying the template to your warehouse
            </DialogDescription>
          </DialogHeader>

          <Alert variant="destructive">
            <AlertCircle className="h-4 w-4" />
            <AlertDescription>
              {applyResult.error || 'An unexpected error occurred while applying the template. Please try again.'}
            </AlertDescription>
          </Alert>

          <div className="flex justify-end gap-2">
            <Button variant="outline" onClick={onClose}>
              Cancel
            </Button>
            <Button onClick={handleApply} disabled={isApplying}>
              Try Again
            </Button>
          </div>
        </DialogContent>
      </Dialog>
    );
  }

  // Show application state (loading or confirmation)
  return (
    <Dialog open={open} onOpenChange={onClose}>
      <DialogContent className="max-w-3xl">
        <DialogHeader>
          <DialogTitle className="flex items-center gap-2">
            <Building2 className="h-6 w-6" />
            Apply Template
          </DialogTitle>
          <DialogDescription>
            Review and apply the {template.name} template to your warehouse
          </DialogDescription>
        </DialogHeader>

        <div className="space-y-6">
          {isApplying && (
            <div className="space-y-3">
              <div className="flex items-center gap-2">
                <Loader2 className="h-4 w-4 animate-spin" />
                <span className="text-sm font-medium">Applying template...</span>
              </div>
              <Progress value={progress} className="w-full" />
              <p className="text-sm text-muted-foreground">
                This may take a moment. We're generating your warehouse locations.
              </p>
            </div>
          )}

          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <Package className="h-5 w-5" />
                  Template Details
                </CardTitle>
              </CardHeader>
              <CardContent className="space-y-3">
                <div>
                  <div className="font-medium">{template.name}</div>
                  {template.template_code && (
                    <Badge variant="outline" className="mt-1">
                      {template.template_code}
                    </Badge>
                  )}
                </div>
                {template.description && (
                  <p className="text-sm text-muted-foreground">
                    {template.description}
                  </p>
                )}
                <Separator />
                <div className="grid grid-cols-2 gap-2 text-sm">
                  <div>
                    <span className="text-muted-foreground">Aisles:</span>
                    <span className="font-medium ml-2">{template.num_aisles}</span>
                  </div>
                  <div>
                    <span className="text-muted-foreground">Racks:</span>
                    <span className="font-medium ml-2">{template.racks_per_aisle}</span>
                  </div>
                  <div>
                    <span className="text-muted-foreground">Positions:</span>
                    <span className="font-medium ml-2">{template.positions_per_rack}</span>
                  </div>
                  <div>
                    <span className="text-muted-foreground">Levels:</span>
                    <span className="font-medium ml-2">{template.levels_per_position}</span>
                  </div>
                </div>
              </CardContent>
            </Card>

            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <Users className="h-5 w-5" />
                  Warehouse Target
                </CardTitle>
              </CardHeader>
              <CardContent className="space-y-3">
                <div>
                  <div className="font-medium">
                    {warehouseName || `Warehouse ${warehouseId}`}
                  </div>
                  <div className="text-sm text-muted-foreground">
                    ID: {warehouseId}
                  </div>
                </div>
                <Separator />
                <div className="text-sm space-y-1">
                  <div className="flex justify-between">
                    <span className="text-muted-foreground">Storage Locations:</span>
                    <span className="font-medium">{totals.storageLocations.toLocaleString()}</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-muted-foreground">Storage Capacity:</span>
                    <span className="font-medium">{totals.storageCapacity.toLocaleString()}</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-muted-foreground">Special Areas:</span>
                    <span className="font-medium">{totals.specialAreas}</span>
                  </div>
                </div>
              </CardContent>
            </Card>
          </div>

          <Alert>
            <AlertCircle className="h-4 w-4" />
            <AlertDescription>
              <strong>Warning:</strong> This will replace your current warehouse configuration and regenerate all locations. 
              Any existing location customizations will be lost.
            </AlertDescription>
          </Alert>
        </div>

        <div className="flex justify-end gap-2">
          <Button variant="outline" onClick={onClose} disabled={isApplying}>
            Cancel
          </Button>
          <Button onClick={handleApply} disabled={isApplying}>
            {isApplying ? (
              <>
                <Loader2 className="h-4 w-4 mr-2 animate-spin" />
                Applying...
              </>
            ) : (
              <>
                Apply Template
                <ArrowRight className="h-4 w-4 ml-2" />
              </>
            )}
          </Button>
        </div>
      </DialogContent>
    </Dialog>
  );
}