'use client';

import React from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Button } from '@/components/ui/button';
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select';
import { Alert, AlertDescription } from '@/components/ui/alert';
import { Badge } from '@/components/ui/badge';
import { Separator } from '@/components/ui/separator';
import { WizardData } from './warehouse-wizard';
import { 
  MapPin, 
  Plus, 
  Trash2, 
  Package, 
  Truck,
  Building,
  Info,
  AlertCircle
} from 'lucide-react';

interface Step2SpecialAreasProps {
  data: WizardData;
  onChange: (updates: Partial<WizardData>) => void;
}

interface SpecialArea {
  code: string;
  type: string;
  capacity: number;
  zone: string;
}

export function Step2SpecialAreas({ data, onChange }: Step2SpecialAreasProps) {
  
  // Add new receiving area
  const addReceivingArea = () => {
    const newArea: SpecialArea = {
      code: `RECEIVE${data.receiving_areas.length + 1}`,
      type: 'RECEIVING',
      capacity: 10,
      zone: 'DOCK'
    };
    
    onChange({
      receiving_areas: [...data.receiving_areas, newArea]
    });
  };

  // Update receiving area
  const updateReceivingArea = (index: number, updates: Partial<SpecialArea>) => {
    const updatedAreas = data.receiving_areas.map((area, i) => 
      i === index ? { ...area, ...updates } : area
    );
    onChange({ receiving_areas: updatedAreas });
  };

  // Remove receiving area
  const removeReceivingArea = (index: number) => {
    if (data.receiving_areas.length > 1) { // Keep at least one
      const updatedAreas = data.receiving_areas.filter((_, i) => i !== index);
      onChange({ receiving_areas: updatedAreas });
    }
  };

  // Add new staging area
  const addStagingArea = () => {
    const newArea: SpecialArea = {
      code: `STAGING${data.staging_areas.length + 1}`,
      type: 'STAGING',
      capacity: 5,
      zone: 'STAGING'
    };
    
    onChange({
      staging_areas: [...data.staging_areas, newArea]
    });
  };

  // Update staging area
  const updateStagingArea = (index: number, updates: Partial<SpecialArea>) => {
    const updatedAreas = data.staging_areas.map((area, i) => 
      i === index ? { ...area, ...updates } : area
    );
    onChange({ staging_areas: updatedAreas });
  };

  // Remove staging area
  const removeStagingArea = (index: number) => {
    const updatedAreas = data.staging_areas.filter((_, i) => i !== index);
    onChange({ staging_areas: updatedAreas });
  };

  // Add new dock area
  const addDockArea = () => {
    const newArea: SpecialArea = {
      code: `DOCK${data.dock_areas.length + 1}`,
      type: 'DOCK',
      capacity: 3,
      zone: 'DOCK'
    };
    
    onChange({
      dock_areas: [...data.dock_areas, newArea]
    });
  };

  // Update dock area
  const updateDockArea = (index: number, updates: Partial<SpecialArea>) => {
    const updatedAreas = data.dock_areas.map((area, i) => 
      i === index ? { ...area, ...updates } : area
    );
    onChange({ dock_areas: updatedAreas });
  };

  // Remove dock area
  const removeDockArea = (index: number) => {
    const updatedAreas = data.dock_areas.filter((_, i) => i !== index);
    onChange({ dock_areas: updatedAreas });
  };

  // Calculate total special areas capacity
  const calculateTotalCapacity = () => {
    const receivingCapacity = data.receiving_areas.reduce((sum, area) => sum + area.capacity, 0);
    const stagingCapacity = data.staging_areas.reduce((sum, area) => sum + area.capacity, 0);
    const dockCapacity = data.dock_areas.reduce((sum, area) => sum + area.capacity, 0);
    
    return {
      receiving: receivingCapacity,
      staging: stagingCapacity,
      dock: dockCapacity,
      total: receivingCapacity + stagingCapacity + dockCapacity
    };
  };

  // Get all area codes to check for duplicates
  const getAllAreaCodes = () => {
    return [
      ...data.receiving_areas.map(a => a.code),
      ...data.staging_areas.map(a => a.code),
      ...data.dock_areas.map(a => a.code)
    ];
  };

  // Check for duplicate codes
  const getDuplicateCodes = () => {
    const allCodes = getAllAreaCodes();
    return allCodes.filter((code, index) => allCodes.indexOf(code) !== index);
  };

  const totalCapacity = calculateTotalCapacity();
  const duplicateCodes = getDuplicateCodes();

  // Render area form
  const renderAreaForm = (
    area: SpecialArea,
    index: number,
    onUpdate: (index: number, updates: Partial<SpecialArea>) => void,
    onRemove: (index: number) => void,
    canRemove: boolean = true
  ) => (
    <div key={`${area.type}-${index}`} className="p-4 border rounded-lg space-y-4">
      <div className="flex justify-between items-start">
        <div className="flex items-center gap-2">
          <MapPin className="h-4 w-4" />
          <span className="font-medium">Area {index + 1}</span>
        </div>
        {canRemove && (
          <Button
            variant="ghost"
            size="sm"
            onClick={() => onRemove(index)}
            className="text-destructive hover:text-destructive"
          >
            <Trash2 className="h-4 w-4" />
          </Button>
        )}
      </div>

      <div className="grid grid-cols-2 gap-4">
        <div className="space-y-2">
          <Label>Area Code *</Label>
          <Input
            value={area.code}
            onChange={(e) => onUpdate(index, { code: e.target.value.toUpperCase() })}
            placeholder="e.g., RECEIVING, RECEIVE1"
          />
          {duplicateCodes.includes(area.code) && (
            <p className="text-xs text-destructive">This code is already used</p>
          )}
        </div>

        <div className="space-y-2">
          <Label>Zone</Label>
          <Select
            value={area.zone}
            onValueChange={(value) => onUpdate(index, { zone: value })}
          >
            <SelectTrigger>
              <SelectValue />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="DOCK">DOCK</SelectItem>
              <SelectItem value="RECEIVING">RECEIVING</SelectItem>
              <SelectItem value="STAGING">STAGING</SelectItem>
              <SelectItem value="GENERAL">GENERAL</SelectItem>
              <SelectItem value="TEMP">TEMP</SelectItem>
            </SelectContent>
          </Select>
        </div>
      </div>

      <div className="space-y-2">
        <Label>Capacity (Pallets)</Label>
        <Input
          type="number"
          min="1"
          max="100"
          value={area.capacity}
          onChange={(e) => onUpdate(index, { capacity: parseInt(e.target.value) || 1 })}
          placeholder="Number of pallets this area can hold"
        />
      </div>
    </div>
  );

  return (
    <div className="space-y-6">
      {/* Introduction */}
      <Alert>
        <Info className="h-4 w-4" />
        <AlertDescription>
          Special areas are locations where pallets are temporarily stored before moving to permanent storage positions. 
          These include receiving docks, staging areas, and loading docks.
        </AlertDescription>
      </Alert>

      {/* Receiving Areas */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Truck className="h-5 w-5" />
            Receiving Areas *
          </CardTitle>
          <CardDescription>
            Areas where incoming pallets are temporarily stored for inspection and processing
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="space-y-4">
            {data.receiving_areas.map((area, index) => 
              renderAreaForm(
                area, 
                index, 
                updateReceivingArea, 
                removeReceivingArea,
                data.receiving_areas.length > 1
              )
            )}
          </div>

          <Button
            variant="outline"
            onClick={addReceivingArea}
            className="w-full"
          >
            <Plus className="h-4 w-4 mr-2" />
            Add Receiving Area
          </Button>

          <div className="bg-blue-50 rounded-lg p-3">
            <div className="text-sm">
              <span className="font-medium">Total Receiving Capacity:</span>
              <Badge variant="secondary" className="ml-2">
                {totalCapacity.receiving} pallets
              </Badge>
            </div>
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
          <CardDescription>
            Temporary storage areas for pallets being prepared for shipment or special handling
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          {data.staging_areas.length === 0 ? (
            <div className="text-center py-8 text-muted-foreground">
              <Package className="h-12 w-12 mx-auto mb-4 opacity-50" />
              <p>No staging areas configured</p>
              <p className="text-xs">Staging areas are optional</p>
            </div>
          ) : (
            <div className="space-y-4">
              {data.staging_areas.map((area, index) => 
                renderAreaForm(area, index, updateStagingArea, removeStagingArea)
              )}
            </div>
          )}

          <Button
            variant="outline"
            onClick={addStagingArea}
            className="w-full"
          >
            <Plus className="h-4 w-4 mr-2" />
            Add Staging Area
          </Button>

          {data.staging_areas.length > 0 && (
            <div className="bg-green-50 rounded-lg p-3">
              <div className="text-sm">
                <span className="font-medium">Total Staging Capacity:</span>
                <Badge variant="secondary" className="ml-2">
                  {totalCapacity.staging} pallets
                </Badge>
              </div>
            </div>
          )}
        </CardContent>
      </Card>

      {/* Dock Areas */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Building className="h-5 w-5" />
            Loading Dock Areas
          </CardTitle>
          <CardDescription>
            Loading bays and dock doors for outbound shipments
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          {data.dock_areas.length === 0 ? (
            <div className="text-center py-8 text-muted-foreground">
              <Building className="h-12 w-12 mx-auto mb-4 opacity-50" />
              <p>No dock areas configured</p>
              <p className="text-xs">Dock areas are optional</p>
            </div>
          ) : (
            <div className="space-y-4">
              {data.dock_areas.map((area, index) => 
                renderAreaForm(area, index, updateDockArea, removeDockArea)
              )}
            </div>
          )}

          <Button
            variant="outline"
            onClick={addDockArea}
            className="w-full"
          >
            <Plus className="h-4 w-4 mr-2" />
            Add Dock Area
          </Button>

          {data.dock_areas.length > 0 && (
            <div className="bg-orange-50 rounded-lg p-3">
              <div className="text-sm">
                <span className="font-medium">Total Dock Capacity:</span>
                <Badge variant="secondary" className="ml-2">
                  {totalCapacity.dock} pallets
                </Badge>
              </div>
            </div>
          )}
        </CardContent>
      </Card>

      {/* Summary */}
      <Card>
        <CardHeader>
          <CardTitle>Special Areas Summary</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {/* Areas Count */}
            <div className="space-y-3">
              <div className="flex justify-between items-center">
                <span className="text-sm text-muted-foreground">Receiving Areas:</span>
                <Badge>{data.receiving_areas.length}</Badge>
              </div>
              <div className="flex justify-between items-center">
                <span className="text-sm text-muted-foreground">Staging Areas:</span>
                <Badge variant="secondary">{data.staging_areas.length}</Badge>
              </div>
              <div className="flex justify-between items-center">
                <span className="text-sm text-muted-foreground">Dock Areas:</span>
                <Badge variant="outline">{data.dock_areas.length}</Badge>
              </div>
              <Separator />
              <div className="flex justify-between items-center">
                <span className="text-sm font-medium">Total Special Areas:</span>
                <Badge variant="default">
                  {data.receiving_areas.length + data.staging_areas.length + data.dock_areas.length}
                </Badge>
              </div>
            </div>

            {/* Capacity Summary */}
            <div className="space-y-3">
              <div className="flex justify-between items-center">
                <span className="text-sm text-muted-foreground">Receiving Capacity:</span>
                <Badge>{totalCapacity.receiving} pallets</Badge>
              </div>
              <div className="flex justify-between items-center">
                <span className="text-sm text-muted-foreground">Staging Capacity:</span>
                <Badge variant="secondary">{totalCapacity.staging} pallets</Badge>
              </div>
              <div className="flex justify-between items-center">
                <span className="text-sm text-muted-foreground">Dock Capacity:</span>
                <Badge variant="outline">{totalCapacity.dock} pallets</Badge>
              </div>
              <Separator />
              <div className="flex justify-between items-center">
                <span className="text-sm font-medium">Total Special Capacity:</span>
                <Badge variant="default">{totalCapacity.total} pallets</Badge>
              </div>
            </div>
          </div>

          {/* All Area Codes */}
          <div className="mt-6">
            <Label className="text-sm font-medium">All Area Codes:</Label>
            <div className="flex flex-wrap gap-2 mt-2">
              {getAllAreaCodes().map((code, index) => (
                <Badge 
                  key={index}
                  variant={duplicateCodes.includes(code) ? "destructive" : "outline"}
                >
                  {code}
                </Badge>
              ))}
            </div>
            {getAllAreaCodes().length === 0 && (
              <p className="text-xs text-muted-foreground mt-2">No areas configured yet</p>
            )}
          </div>

          {/* Validation Errors */}
          {duplicateCodes.length > 0 && (
            <Alert variant="destructive" className="mt-4">
              <AlertCircle className="h-4 w-4" />
              <AlertDescription>
                Duplicate area codes found: {duplicateCodes.join(', ')}. 
                Please use unique codes for each area.
              </AlertDescription>
            </Alert>
          )}

          {data.receiving_areas.length === 0 && (
            <Alert variant="destructive" className="mt-4">
              <AlertCircle className="h-4 w-4" />
              <AlertDescription>
                At least one receiving area is required to proceed.
              </AlertDescription>
            </Alert>
          )}
        </CardContent>
      </Card>
    </div>
  );
}