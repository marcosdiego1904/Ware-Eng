'use client';

import React from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Switch } from '@/components/ui/switch';
import { Separator } from '@/components/ui/separator';
import { Alert, AlertDescription } from '@/components/ui/alert';
import { Badge } from '@/components/ui/badge';
import { WizardData } from './warehouse-wizard';
import { 
  Building2, 
  Info, 
  Calculator,
  AlertTriangle,
  CheckCircle,
  Grid3X3
} from 'lucide-react';

interface ValidationResult {
  valid: boolean;
  errors: string[];
  warnings: string[];
  calculations: {
    total_storage_locations: number;
    total_capacity: number;
    estimated_setup_time_minutes: number;
  };
}

interface Step1StructureProps {
  data: WizardData;
  onChange: (updates: Partial<WizardData>) => void;
  validationResults?: ValidationResult | null;
}

export function Step1Structure({ data, onChange, validationResults }: Step1StructureProps) {
  
  // Calculate totals in real-time
  const calculateTotals = () => {
    const storageLocations = data.num_aisles * data.racks_per_aisle * data.positions_per_rack * data.levels_per_position;
    const storageCapacity = storageLocations * data.default_pallet_capacity;
    const estimatedSetupTime = Math.max(1, Math.ceil(storageLocations / 1000));
    
    return {
      storageLocations,
      storageCapacity,
      estimatedSetupTime
    };
  };

  const totals = calculateTotals();

  // Handle input changes with validation
  const handleNumberInput = (field: keyof WizardData, value: string) => {
    const numValue = parseInt(value) || 0;
    if (numValue >= 0) {
      onChange({ [field]: numValue });
    }
  };

  return (
    <div className="space-y-6">
      {/* Warehouse Basic Info */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Building2 className="h-5 w-5" />
            Warehouse Information
          </CardTitle>
          <CardDescription>
            Basic information about your warehouse
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="grid grid-cols-1 gap-4">
            <div className="space-y-2">
              <Label htmlFor="warehouse_name">Warehouse Name *</Label>
              <Input
                id="warehouse_name"
                value={data.warehouse_name}
                onChange={(e) => onChange({ warehouse_name: e.target.value })}
                placeholder="e.g., Main Distribution Center, Warehouse A"
              />
              <p className="text-xs text-muted-foreground">
                This will be the display name for your warehouse
              </p>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Warehouse Structure */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Grid3X3 className="h-5 w-5" />
            Warehouse Structure
          </CardTitle>
          <CardDescription>
            Define the physical layout of your warehouse storage areas
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-6">
          {/* Main Structure Inputs */}
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
            <div className="space-y-2">
              <Label htmlFor="num_aisles">Aisles *</Label>
              <Input
                id="num_aisles"
                type="number"
                min="1"
                max="50"
                value={data.num_aisles}
                onChange={(e) => handleNumberInput('num_aisles', e.target.value)}
              />
              <p className="text-xs text-muted-foreground">Number of aisles</p>
            </div>

            <div className="space-y-2">
              <Label htmlFor="racks_per_aisle">Racks per Aisle *</Label>
              <Input
                id="racks_per_aisle"
                type="number"
                min="1"
                max="10"
                value={data.racks_per_aisle}
                onChange={(e) => handleNumberInput('racks_per_aisle', e.target.value)}
              />
              <p className="text-xs text-muted-foreground">Racks in each aisle</p>
            </div>

            <div className="space-y-2">
              <Label htmlFor="positions_per_rack">Positions per Rack *</Label>
              <Input
                id="positions_per_rack"
                type="number"
                min="1"
                max="500"
                value={data.positions_per_rack}
                onChange={(e) => handleNumberInput('positions_per_rack', e.target.value)}
              />
              <p className="text-xs text-muted-foreground">Storage positions</p>
            </div>

            <div className="space-y-2">
              <Label htmlFor="levels_per_position">Levels per Position *</Label>
              <Input
                id="levels_per_position"
                type="number"
                min="1"
                max="10"
                value={data.levels_per_position}
                onChange={(e) => handleNumberInput('levels_per_position', e.target.value)}
              />
              <p className="text-xs text-muted-foreground">Vertical levels</p>
            </div>
          </div>

          <Separator />

          {/* Level Configuration */}
          <div className="grid grid-cols-2 gap-4">
            <div className="space-y-2">
              <Label htmlFor="level_names">Level Names</Label>
              <Input
                id="level_names"
                value={data.level_names}
                onChange={(e) => onChange({ level_names: e.target.value.toUpperCase() })}
                placeholder="ABCD"
                maxLength={10}
              />
              <p className="text-xs text-muted-foreground">
                Letters for each level (e.g., ABCD = levels A, B, C, D)
              </p>
            </div>

            <div className="space-y-2">
              <Label htmlFor="default_zone">Default Zone</Label>
              <Input
                id="default_zone"
                value={data.default_zone}
                onChange={(e) => onChange({ default_zone: e.target.value.toUpperCase() })}
                placeholder="GENERAL"
              />
              <p className="text-xs text-muted-foreground">
                Zone name for storage locations
              </p>
            </div>
          </div>

          <Separator />

          {/* Capacity and Settings */}
          <div className="space-y-4">
            <div className="grid grid-cols-2 gap-4">
              <div className="space-y-2">
                <Label htmlFor="default_pallet_capacity">Pallets per Level *</Label>
                <Input
                  id="default_pallet_capacity"
                  type="number"
                  min="1"
                  max="4"
                  value={data.default_pallet_capacity}
                  onChange={(e) => handleNumberInput('default_pallet_capacity', e.target.value)}
                />
                <p className="text-xs text-muted-foreground">
                  How many pallets fit in each level
                </p>
              </div>

              <div className="flex items-center space-x-2 pt-7">
                <Switch
                  id="bidimensional_racks"
                  checked={data.bidimensional_racks}
                  onCheckedChange={(checked) => onChange({ bidimensional_racks: checked })}
                />
                <Label htmlFor="bidimensional_racks">Bidimensional Racks</Label>
              </div>
            </div>

            <Alert>
              <Info className="h-4 w-4" />
              <AlertDescription>
                {data.bidimensional_racks 
                  ? 'Bidimensional racks can hold 2 pallets per level (front and back)'
                  : 'Single-dimensional racks hold 1 pallet per level'
                }
              </AlertDescription>
            </Alert>

            <div className="flex items-center space-x-2">
              <Switch
                id="position_numbering_split"
                checked={data.position_numbering_split}
                onCheckedChange={(checked) => onChange({ position_numbering_split: checked })}
              />
              <Label htmlFor="position_numbering_split">Split Position Numbering</Label>
              <p className="text-xs text-muted-foreground ml-2">
                (Rack 1: positions 1-{Math.floor(data.positions_per_rack/2)}, Rack 2: positions {Math.floor(data.positions_per_rack/2)+1}-{data.positions_per_rack})
              </p>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Real-time Calculations */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Calculator className="h-5 w-5" />
            Warehouse Calculations
          </CardTitle>
          <CardDescription>
            Preview of your warehouse capacity and structure
          </CardDescription>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div className="text-center p-4 bg-blue-50 rounded-lg">
              <div className="text-2xl font-bold text-blue-700">
                {totals.storageLocations.toLocaleString()}
              </div>
              <div className="text-sm text-blue-600">Storage Locations</div>
              <div className="text-xs text-muted-foreground mt-1">
                {data.num_aisles} × {data.racks_per_aisle} × {data.positions_per_rack} × {data.levels_per_position}
              </div>
            </div>

            <div className="text-center p-4 bg-green-50 rounded-lg">
              <div className="text-2xl font-bold text-green-700">
                {totals.storageCapacity.toLocaleString()}
              </div>
              <div className="text-sm text-green-600">Pallet Capacity</div>
              <div className="text-xs text-muted-foreground mt-1">
                {data.default_pallet_capacity} pallet{data.default_pallet_capacity > 1 ? 's' : ''} per level
              </div>
            </div>

            <div className="text-center p-4 bg-orange-50 rounded-lg">
              <div className="text-2xl font-bold text-orange-700">
                ~{totals.estimatedSetupTime}
              </div>
              <div className="text-sm text-orange-600">Minutes Setup</div>
              <div className="text-xs text-muted-foreground mt-1">
                Estimated generation time
              </div>
            </div>
          </div>

          {/* Sample Location Codes */}
          <div className="mt-6">
            <Label className="text-sm font-medium">Sample Location Codes:</Label>
            <div className="flex flex-wrap gap-2 mt-2">
              {Array.from({ length: Math.min(8, data.levels_per_position) }, (_, i) => {
                const level = data.level_names[i] || `L${i+1}`;
                return (
                  <Badge key={i} variant="outline">
                    {`001${level}`}
                  </Badge>
                );
              })}
              <Badge variant="secondary">...</Badge>
              {Array.from({ length: Math.min(4, data.levels_per_position) }, (_, i) => {
                const level = data.level_names[i] || `L${i+1}`;
                const lastPos = data.positions_per_rack.toString().padStart(3, '0');
                return (
                  <Badge key={`last-${i}`} variant="outline">
                    {`${lastPos}${level}`}
                  </Badge>
                );
              })}
            </div>
            <p className="text-xs text-muted-foreground mt-2">
              Format: Position Number (001-{data.positions_per_rack.toString().padStart(3, '0')}) + Level ({data.level_names})
            </p>
          </div>
        </CardContent>
      </Card>

      {/* Validation Results */}
      {validationResults && (
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              {validationResults.valid ? (
                <CheckCircle className="h-5 w-5 text-green-600" />
              ) : (
                <AlertTriangle className="h-5 w-5 text-orange-600" />
              )}
              Validation Results
            </CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            {/* Errors */}
            {validationResults.errors && validationResults.errors.length > 0 && (
              <Alert variant="destructive">
                <AlertTriangle className="h-4 w-4" />
                <AlertDescription>
                  <ul className="list-disc list-inside space-y-1">
                    {validationResults.errors.map((error: string, index: number) => (
                      <li key={index}>{error}</li>
                    ))}
                  </ul>
                </AlertDescription>
              </Alert>
            )}

            {/* Warnings */}
            {validationResults.warnings && validationResults.warnings.length > 0 && (
              <Alert>
                <Info className="h-4 w-4" />
                <AlertDescription>
                  <ul className="list-disc list-inside space-y-1">
                    {validationResults.warnings.map((warning: string, index: number) => (
                      <li key={index}>{warning}</li>
                    ))}
                  </ul>
                </AlertDescription>
              </Alert>
            )}

            {/* Calculations from validation */}
            {validationResults.calculations && (
              <div className="bg-gray-50 rounded-lg p-4">
                <h4 className="text-sm font-medium mb-2">Validation Calculations:</h4>
                <div className="grid grid-cols-2 gap-4 text-sm">
                  <div>
                    <span className="text-muted-foreground">Total Locations:</span>
                    <span className="font-medium ml-2">
                      {validationResults.calculations.total_storage_locations?.toLocaleString()}
                    </span>
                  </div>
                  <div>
                    <span className="text-muted-foreground">Total Capacity:</span>
                    <span className="font-medium ml-2">
                      {validationResults.calculations.total_capacity?.toLocaleString()} pallets
                    </span>
                  </div>
                  <div>
                    <span className="text-muted-foreground">Setup Time:</span>
                    <span className="font-medium ml-2">
                      ~{validationResults.calculations.estimated_setup_time_minutes} minutes
                    </span>
                  </div>
                </div>
              </div>
            )}

            {validationResults.valid && (
              <Alert>
                <CheckCircle className="h-4 w-4" />
                <AlertDescription>
                  Configuration is valid and ready for the next step!
                </AlertDescription>
              </Alert>
            )}
          </CardContent>
        </Card>
      )}
    </div>
  );
}