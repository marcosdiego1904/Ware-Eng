'use client';

import React from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Label } from '@/components/ui/label';
import { Input } from '@/components/ui/input';
import { Textarea } from '@/components/ui/textarea';
import { Switch } from '@/components/ui/switch';
import { Alert, AlertDescription } from '@/components/ui/alert';
import { Badge } from '@/components/ui/badge';
import { Separator } from '@/components/ui/separator';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { WizardData } from './warehouse-wizard';
import { 
  CheckCircle, 
  AlertTriangle,
  Building2, 
  Package, 
  MapPin,
  Clock,
  Database,
  Share2,
  Info,
  Eye,
  Settings
} from 'lucide-react';

interface PreviewData {
  sample_locations: {
    code: string;
    full_address: string;
  }[];
  totals: {
    storage_locations: number;
    receiving_areas: number;
    staging_areas: number;
    total_locations: number;
  };
}

interface ValidationResult {
  valid: boolean;
  errors: string[];
  warnings: string[];
}

interface Step3PreviewProps {
  data: WizardData;
  onChange: (updates: Partial<WizardData>) => void;
  previewData?: PreviewData | null;
  validationResults?: ValidationResult | null;
}

export function Step3Preview({ data, onChange, previewData, validationResults }: Step3PreviewProps) {
  
  // Calculate final totals
  const calculateFinalTotals = () => {
    const storageLocations = data.num_aisles * data.racks_per_aisle * data.positions_per_rack * data.levels_per_position;
    const storageCapacity = storageLocations * data.default_pallet_capacity;
    
    const specialAreasCount = data.receiving_areas.length + data.staging_areas.length + data.dock_areas.length;
    const specialCapacity = 
      data.receiving_areas.reduce((sum, area) => sum + area.capacity, 0) +
      data.staging_areas.reduce((sum, area) => sum + area.capacity, 0) +
      data.dock_areas.reduce((sum, area) => sum + area.capacity, 0);
    
    const totalLocations = storageLocations + specialAreasCount;
    const totalCapacity = storageCapacity + specialCapacity;
    
    return {
      storageLocations,
      storageCapacity,
      specialAreasCount,
      specialCapacity,
      totalLocations,
      totalCapacity
    };
  };

  const totals = calculateFinalTotals();

  return (
    <div className="space-y-6">
      {/* Configuration Summary */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Eye className="h-5 w-5" />
            Configuration Preview
          </CardTitle>
          <CardDescription>
            Review your warehouse configuration before generating locations
          </CardDescription>
        </CardHeader>
        <CardContent>
          <Tabs defaultValue="structure" className="w-full">
            <TabsList className="grid w-full grid-cols-3">
              <TabsTrigger value="structure">Structure</TabsTrigger>
              <TabsTrigger value="areas">Special Areas</TabsTrigger>
              <TabsTrigger value="summary">Summary</TabsTrigger>
            </TabsList>

            <TabsContent value="structure" className="space-y-4">
              <div className="grid grid-cols-2 gap-4">
                <div className="space-y-3">
                  <div className="flex justify-between">
                    <span className="text-sm text-muted-foreground">Warehouse Name:</span>
                    <span className="text-sm font-medium">{data.warehouse_name}</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-sm text-muted-foreground">Aisles:</span>
                    <Badge>{data.num_aisles}</Badge>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-sm text-muted-foreground">Racks per Aisle:</span>
                    <Badge>{data.racks_per_aisle}</Badge>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-sm text-muted-foreground">Positions per Rack:</span>
                    <Badge>{data.positions_per_rack}</Badge>
                  </div>
                </div>
                <div className="space-y-3">
                  <div className="flex justify-between">
                    <span className="text-sm text-muted-foreground">Levels per Position:</span>
                    <Badge>{data.levels_per_position}</Badge>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-sm text-muted-foreground">Level Names:</span>
                    <Badge variant="outline">{data.level_names}</Badge>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-sm text-muted-foreground">Pallets per Level:</span>
                    <Badge>{data.default_pallet_capacity}</Badge>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-sm text-muted-foreground">Rack Type:</span>
                    <Badge variant="secondary">
                      {data.bidimensional_racks ? 'Bidimensional' : 'Single'}
                    </Badge>
                  </div>
                </div>
              </div>

              {/* Sample Locations Preview */}
              {previewData && (
                <div className="mt-6">
                  <Label className="text-sm font-medium">Sample Location Codes:</Label>
                  <div className="grid grid-cols-4 gap-2 mt-3">
                    {previewData.sample_locations?.slice(0, 8).map((location: any, index: number) => (
                      <div key={index} className="text-center p-2 bg-blue-50 rounded border">
                        <div className="font-mono text-sm font-medium">{location.code}</div>
                        <div className="text-xs text-muted-foreground">{location.full_address}</div>
                      </div>
                    ))}
                  </div>
                  <p className="text-xs text-muted-foreground mt-2">
                    Showing first 8 sample locations from Aisle 1, Rack 1
                  </p>
                </div>
              )}
            </TabsContent>

            <TabsContent value="areas" className="space-y-4">
              {/* Receiving Areas */}
              <div>
                <h4 className="text-sm font-medium mb-2 flex items-center gap-2">
                  <MapPin className="h-4 w-4" />
                  Receiving Areas ({data.receiving_areas.length})
                </h4>
                <div className="space-y-2">
                  {data.receiving_areas.map((area, index) => (
                    <div key={index} className="flex justify-between items-center p-2 bg-blue-50 rounded">
                      <span className="font-medium">{area.code}</span>
                      <div className="flex gap-2">
                        <Badge variant="outline">{area.zone}</Badge>
                        <Badge>{area.capacity} pallets</Badge>
                      </div>
                    </div>
                  ))}
                </div>
              </div>

              {/* Staging Areas */}
              {data.staging_areas.length > 0 && (
                <div>
                  <h4 className="text-sm font-medium mb-2 flex items-center gap-2">
                    <Package className="h-4 w-4" />
                    Staging Areas ({data.staging_areas.length})
                  </h4>
                  <div className="space-y-2">
                    {data.staging_areas.map((area, index) => (
                      <div key={index} className="flex justify-between items-center p-2 bg-green-50 rounded">
                        <span className="font-medium">{area.code}</span>
                        <div className="flex gap-2">
                          <Badge variant="outline">{area.zone}</Badge>
                          <Badge>{area.capacity} pallets</Badge>
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              )}

              {/* Dock Areas */}
              {data.dock_areas.length > 0 && (
                <div>
                  <h4 className="text-sm font-medium mb-2 flex items-center gap-2">
                    <Building2 className="h-4 w-4" />
                    Dock Areas ({data.dock_areas.length})
                  </h4>
                  <div className="space-y-2">
                    {data.dock_areas.map((area, index) => (
                      <div key={index} className="flex justify-between items-center p-2 bg-orange-50 rounded">
                        <span className="font-medium">{area.code}</span>
                        <div className="flex gap-2">
                          <Badge variant="outline">{area.zone}</Badge>
                          <Badge>{area.capacity} pallets</Badge>
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              )}
            </TabsContent>

            <TabsContent value="summary">
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                {/* Storage Summary */}
                <div className="space-y-4">
                  <h4 className="text-sm font-medium">Storage Locations</h4>
                  <div className="text-center p-6 bg-blue-50 rounded-lg">
                    <div className="text-3xl font-bold text-blue-700">
                      {totals.storageLocations.toLocaleString()}
                    </div>
                    <div className="text-sm text-blue-600">Storage Positions</div>
                    <div className="text-xs text-muted-foreground mt-2">
                      {totals.storageCapacity.toLocaleString()} pallet capacity
                    </div>
                  </div>
                </div>

                {/* Special Areas Summary */}
                <div className="space-y-4">
                  <h4 className="text-sm font-medium">Special Areas</h4>
                  <div className="text-center p-6 bg-green-50 rounded-lg">
                    <div className="text-3xl font-bold text-green-700">
                      {totals.specialAreasCount}
                    </div>
                    <div className="text-sm text-green-600">Special Areas</div>
                    <div className="text-xs text-muted-foreground mt-2">
                      {totals.specialCapacity} pallet capacity
                    </div>
                  </div>
                </div>

                {/* Total Summary */}
                <div className="md:col-span-2">
                  <div className="text-center p-6 bg-gray-100 rounded-lg">
                    <div className="text-4xl font-bold text-gray-700">
                      {totals.totalLocations.toLocaleString()}
                    </div>
                    <div className="text-lg text-gray-600">Total Locations</div>
                    <div className="text-sm text-muted-foreground mt-2">
                      {totals.totalCapacity.toLocaleString()} total pallet capacity
                    </div>
                  </div>
                </div>
              </div>

              {/* Preview Data from API */}
              {previewData && (
                <Alert className="mt-4">
                  <Info className="h-4 w-4" />
                  <AlertDescription>
                    <div className="space-y-2">
                      <div className="font-medium">API Preview Confirmation:</div>
                      <div className="text-sm">
                        • Storage Locations: {previewData.totals?.storage_locations?.toLocaleString()}
                      </div>
                      <div className="text-sm">
                        • Special Areas: {previewData.totals?.receiving_areas + previewData.totals?.staging_areas}
                      </div>
                      <div className="text-sm">
                        • Total Locations: {previewData.totals?.total_locations?.toLocaleString()}
                      </div>
                    </div>
                  </AlertDescription>
                </Alert>
              )}
            </TabsContent>
          </Tabs>
        </CardContent>
      </Card>

      {/* Generation Options */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Settings className="h-5 w-5" />
            Generation Options
          </CardTitle>
          <CardDescription>
            Configure how your warehouse will be generated
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-6">
          {/* Basic Options */}
          <div className="space-y-4">
            <div className="flex items-center justify-between">
              <div className="space-y-1">
                <Label htmlFor="generate_locations">Generate Locations</Label>
                <p className="text-xs text-muted-foreground">
                  Create all location records in the database
                </p>
              </div>
              <Switch
                id="generate_locations"
                checked={data.generate_locations}
                onCheckedChange={(checked) => onChange({ generate_locations: checked })}
              />
            </div>

            <div className="flex items-center justify-between">
              <div className="space-y-1">
                <Label htmlFor="force_recreate">Force Recreate</Label>
                <p className="text-xs text-muted-foreground">
                  Replace existing locations (if any) with new configuration
                </p>
              </div>
              <Switch
                id="force_recreate"
                checked={data.force_recreate}
                onCheckedChange={(checked) => onChange({ force_recreate: checked })}
              />
            </div>
          </div>

          <Separator />

          {/* Template Creation */}
          <div className="space-y-4">
            <div className="flex items-center justify-between">
              <div className="space-y-1">
                <Label htmlFor="create_template">Create Template</Label>
                <p className="text-xs text-muted-foreground">
                  Save this configuration as a reusable template
                </p>
              </div>
              <Switch
                id="create_template"
                checked={data.create_template}
                onCheckedChange={(checked) => onChange({ create_template: checked })}
              />
            </div>

            {data.create_template && (
              <div className="space-y-4 pl-6 border-l-2 border-blue-200">
                <div className="space-y-2">
                  <Label htmlFor="template_name">Template Name *</Label>
                  <Input
                    id="template_name"
                    value={data.template_name}
                    onChange={(e) => onChange({ template_name: e.target.value })}
                    placeholder="e.g., Standard 4-Aisle Layout"
                  />
                </div>

                <div className="space-y-2">
                  <Label htmlFor="template_description">Template Description</Label>
                  <Textarea
                    id="template_description"
                    value={data.template_description}
                    onChange={(e) => onChange({ template_description: e.target.value })}
                    placeholder="Describe this template for other users..."
                    rows={3}
                  />
                </div>

                <div className="flex items-center justify-between">
                  <div className="space-y-1">
                    <Label htmlFor="template_is_public">Make Template Public</Label>
                    <p className="text-xs text-muted-foreground">
                      Allow other users to use this template
                    </p>
                  </div>
                  <Switch
                    id="template_is_public"
                    checked={data.template_is_public}
                    onCheckedChange={(checked) => onChange({ template_is_public: checked })}
                  />
                </div>

                <Alert>
                  <Share2 className="h-4 w-4" />
                  <AlertDescription>
                    {data.template_is_public 
                      ? 'This template will be available to all users and will receive a shareable code.'
                      : 'This template will only be available to you.'
                    }
                  </AlertDescription>
                </Alert>
              </div>
            )}
          </div>
        </CardContent>
      </Card>

      {/* Validation and Warnings */}
      {validationResults && (
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              {validationResults.valid ? (
                <CheckCircle className="h-5 w-5 text-green-600" />
              ) : (
                <AlertTriangle className="h-5 w-5 text-orange-600" />
              )}
              Final Validation
            </CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
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

            {validationResults.valid && (
              <Alert>
                <CheckCircle className="h-4 w-4" />
                <AlertDescription>
                  Configuration is valid and ready for generation!
                </AlertDescription>
              </Alert>
            )}
          </CardContent>
        </Card>
      )}

      {/* Estimated Generation Time */}
      {data.generate_locations && (
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Clock className="h-5 w-5" />
              Estimated Generation Time
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-center p-4 bg-orange-50 rounded-lg">
              <div className="text-2xl font-bold text-orange-700">
                ~{Math.max(1, Math.ceil(totals.totalLocations / 1000))} minutes
              </div>
              <div className="text-sm text-orange-600">Generation Time</div>
              <div className="text-xs text-muted-foreground mt-2">
                Creating {totals.totalLocations.toLocaleString()} location records
              </div>
            </div>
            
            <Alert className="mt-4">
              <Database className="h-4 w-4" />
              <AlertDescription>
                The system will create {totals.totalLocations.toLocaleString()} location records in your database. 
                Large warehouses may take several minutes to generate.
              </AlertDescription>
            </Alert>
          </CardContent>
        </Card>
      )}
    </div>
  );
}