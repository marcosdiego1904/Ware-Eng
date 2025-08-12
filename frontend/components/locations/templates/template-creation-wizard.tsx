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
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Textarea } from '@/components/ui/textarea';
import { Switch } from '@/components/ui/switch';
import { Badge } from '@/components/ui/badge';
import { Alert, AlertDescription } from '@/components/ui/alert';
import { Progress } from '@/components/ui/progress';
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select';
import { Separator } from '@/components/ui/separator';
import { 
  Building2, 
  Package, 
  ChevronLeft, 
  ChevronRight,
  Layers,
  Grid3X3,
  Info,
  Calculator,
  CheckCircle,
  Palette,
  Lock,
  Building,
  Globe,
  Users,
  Zap
} from 'lucide-react';
import { standaloneTemplateAPI, type StandaloneTemplateData } from '@/lib/standalone-template-api';
import { SpecialAreaEditor } from './special-area-editor';

interface TemplateCreationWizardProps {
  open: boolean;
  onClose: () => void;
  onTemplateCreated?: (template: any, shouldTest?: boolean) => void;
}

interface TemplateData {
  // Basic Information
  name: string;
  description: string;
  category: string;
  industry: string;
  tags: string[];
  
  // Privacy Settings
  visibility: 'PRIVATE' | 'COMPANY' | 'PUBLIC';
  
  // Structure Configuration
  num_aisles: number;
  racks_per_aisle: number;
  positions_per_rack: number;
  levels_per_position: number;
  level_names: string;
  default_pallet_capacity: number;
  bidimensional_racks: boolean;
  default_zone: string;
  
  // Special Areas
  receiving_areas: Array<{
    code: string;
    type: string;
    capacity: number;
    zone: string;
  }>;
  staging_areas: Array<{
    code: string;
    type: string;
    capacity: number;
    zone: string;
  }>;
  dock_areas: Array<{
    code: string;
    type: string;
    capacity: number;
    zone: string;
  }>;
}

const INITIAL_TEMPLATE_DATA: TemplateData = {
  name: '',
  description: '',
  category: 'CUSTOM',
  industry: '',
  tags: [],
  visibility: 'PRIVATE',
  num_aisles: 4,
  racks_per_aisle: 2,
  positions_per_rack: 50,
  levels_per_position: 4,
  level_names: 'ABCD',
  default_pallet_capacity: 1,
  bidimensional_racks: false,
  default_zone: 'GENERAL',
  receiving_areas: [
    { code: 'RECEIVING', type: 'RECEIVING', capacity: 10, zone: 'DOCK' }
  ],
  staging_areas: [],
  dock_areas: []
};

const TEMPLATE_CATEGORIES = [
  { value: 'MANUFACTURING', label: 'Manufacturing', description: 'Industrial production warehouses' },
  { value: 'RETAIL', label: 'Retail Distribution', description: 'Retail distribution centers' },
  { value: 'FOOD_BEVERAGE', label: 'Food & Beverage', description: 'Cold chain and food storage' },
  { value: 'PHARMA', label: 'Pharmaceutical', description: 'Controlled environment storage' },
  { value: 'AUTOMOTIVE', label: 'Automotive', description: 'Parts and assembly storage' },
  { value: 'ECOMMERCE', label: 'E-commerce', description: 'Fulfillment centers' },
  { value: 'CUSTOM', label: 'Custom', description: 'User-defined template' }
];

const STARTER_TEMPLATES = [
  {
    name: 'Small Warehouse',
    description: 'Compact layout for smaller operations',
    structure: { aisles: 2, racks: 2, positions: 25, levels: 3 },
    category: 'CUSTOM'
  },
  {
    name: 'Standard Distribution',
    description: 'Balanced layout for general distribution',
    structure: { aisles: 4, racks: 2, positions: 50, levels: 4 },
    category: 'RETAIL'
  },
  {
    name: 'High-Density Storage',
    description: 'Maximizes storage capacity',
    structure: { aisles: 6, racks: 3, positions: 60, levels: 5 },
    category: 'MANUFACTURING'
  },
  {
    name: 'E-commerce Fulfillment',
    description: 'Optimized for fast picking',
    structure: { aisles: 8, racks: 2, positions: 40, levels: 3 },
    category: 'ECOMMERCE'
  }
];

export function TemplateCreationWizard({ open, onClose, onTemplateCreated }: TemplateCreationWizardProps) {
  const [currentStep, setCurrentStep] = useState(1);
  const [templateData, setTemplateData] = useState<TemplateData>(INITIAL_TEMPLATE_DATA);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [tagInput, setTagInput] = useState('');

  const totalSteps = 4;
  const progress = (currentStep / totalSteps) * 100;

  const updateTemplateData = (updates: Partial<TemplateData>) => {
    setTemplateData(prev => ({ ...prev, ...updates }));
  };

  const calculateTotals = () => {
    const storageLocations = templateData.num_aisles * templateData.racks_per_aisle * 
                           templateData.positions_per_rack * templateData.levels_per_position;
    const storageCapacity = storageLocations * templateData.default_pallet_capacity;
    const specialCapacity = [...templateData.receiving_areas, ...templateData.staging_areas, ...templateData.dock_areas]
                          .reduce((sum, area) => sum + area.capacity, 0);
    
    return {
      storageLocations,
      storageCapacity,
      specialCapacity,
      totalCapacity: storageCapacity + specialCapacity
    };
  };

  const addTag = () => {
    if (tagInput.trim() && !templateData.tags.includes(tagInput.trim())) {
      updateTemplateData({
        tags: [...templateData.tags, tagInput.trim().toLowerCase()]
      });
      setTagInput('');
    }
  };

  const removeTag = (tagToRemove: string) => {
    updateTemplateData({
      tags: templateData.tags.filter(tag => tag !== tagToRemove)
    });
  };

  const addReceivingArea = () => {
    const newArea = {
      code: `RECV-${templateData.receiving_areas.length + 1}`,
      type: 'RECEIVING',
      capacity: 10,
      zone: 'DOCK'
    };
    updateTemplateData({
      receiving_areas: [...templateData.receiving_areas, newArea]
    });
  };

  const addStagingArea = () => {
    const newArea = {
      code: `STAGE-${templateData.staging_areas.length + 1}`,
      type: 'STAGING',
      capacity: 5,
      zone: 'STAGING'
    };
    updateTemplateData({
      staging_areas: [...templateData.staging_areas, newArea]
    });
  };

  const addDockArea = () => {
    const newArea = {
      code: `DOCK-${templateData.dock_areas.length + 1}`,
      type: 'DOCK',
      capacity: 2,
      zone: 'DOCK'
    };
    updateTemplateData({
      dock_areas: [...templateData.dock_areas, newArea]
    });
  };

  const applyStarterTemplate = (starter: typeof STARTER_TEMPLATES[0]) => {
    updateTemplateData({
      name: starter.name,
      description: starter.description,
      category: starter.category,
      num_aisles: starter.structure.aisles,
      racks_per_aisle: starter.structure.racks,
      positions_per_rack: starter.structure.positions,
      levels_per_position: starter.structure.levels
    });
  };

  const handleSubmit = async (shouldTest: boolean = false) => {
    setLoading(true);
    setError(null);
    
    try {
      // Convert to API format
      const apiData: StandaloneTemplateData = {
        name: templateData.name,
        description: templateData.description,
        category: templateData.category,
        industry: templateData.industry,
        tags: templateData.tags,
        visibility: templateData.visibility,
        num_aisles: templateData.num_aisles,
        racks_per_aisle: templateData.racks_per_aisle,
        positions_per_rack: templateData.positions_per_rack,
        levels_per_position: templateData.levels_per_position,
        level_names: templateData.level_names,
        default_pallet_capacity: templateData.default_pallet_capacity,
        bidimensional_racks: templateData.bidimensional_racks,
        receiving_areas: templateData.receiving_areas,
        staging_areas: templateData.staging_areas,
        dock_areas: templateData.dock_areas
      };
      
      const createdTemplate = await standaloneTemplateAPI.createTemplate(apiData);
      
      onTemplateCreated?.(createdTemplate, shouldTest);
      onClose();
      
    } catch (err: any) {
      setError(err?.response?.data?.error || 'Failed to create template. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  const canProceed = () => {
    switch (currentStep) {
      case 1:
        return templateData.name.trim().length > 0;
      case 2:
        return templateData.num_aisles > 0 && templateData.racks_per_aisle > 0 &&
               templateData.positions_per_rack > 0 && templateData.levels_per_position > 0;
      case 3:
        return true; // Special areas are optional
      case 4:
        return true; // Review step
      default:
        return false;
    }
  };

  const getVisibilityIcon = (visibility: string) => {
    switch (visibility) {
      case 'PRIVATE': return <Lock className="h-4 w-4" />;
      case 'COMPANY': return <Building className="h-4 w-4" />;
      case 'PUBLIC': return <Globe className="h-4 w-4" />;
      default: return <Lock className="h-4 w-4" />;
    }
  };

  const renderStep = () => {
    switch (currentStep) {
      case 1:
        return renderBasicInfoStep();
      case 2:
        return renderStructureStep();
      case 3:
        return renderSpecialAreasStep();
      case 4:
        return renderReviewStep();
      default:
        return null;
    }
  };

  const renderBasicInfoStep = () => (
    <div className="space-y-6">
      <div className="text-center mb-6">
        <Building2 className="h-12 w-12 mx-auto mb-4 text-primary" />
        <h3 className="text-lg font-semibold">Template Information</h3>
        <p className="text-sm text-muted-foreground">
          Start with a starter template or create from scratch
        </p>
      </div>

      {/* Starter Templates */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Palette className="h-5 w-5" />
            Quick Start Templates
          </CardTitle>
          <CardDescription>
            Choose a starter template to customize, or scroll down to start from scratch
          </CardDescription>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {STARTER_TEMPLATES.map((starter, index) => (
              <Card 
                key={index} 
                className="cursor-pointer hover:bg-muted/50 transition-colors"
                onClick={() => applyStarterTemplate(starter)}
              >
                <CardContent className="p-4">
                  <div className="space-y-2">
                    <div className="font-medium">{starter.name}</div>
                    <div className="text-sm text-muted-foreground">{starter.description}</div>
                    <div className="text-xs font-mono">
                      {starter.structure.aisles}A × {starter.structure.racks}R × {starter.structure.positions}P × {starter.structure.levels}L
                    </div>
                    <Badge variant="outline" className="text-xs">
                      {TEMPLATE_CATEGORIES.find(c => c.value === starter.category)?.label}
                    </Badge>
                  </div>
                </CardContent>
              </Card>
            ))}
          </div>
        </CardContent>
      </Card>

      <Separator />

      {/* Basic Information Form */}
      <div className="space-y-4">
        <div className="space-y-2">
          <Label htmlFor="name">Template Name *</Label>
          <Input
            id="name"
            value={templateData.name}
            onChange={(e) => updateTemplateData({ name: e.target.value })}
            placeholder="e.g., Manufacturing Standard Layout"
          />
        </div>

        <div className="space-y-2">
          <Label htmlFor="description">Description</Label>
          <Textarea
            id="description"
            value={templateData.description}
            onChange={(e) => updateTemplateData({ description: e.target.value })}
            placeholder="Describe the intended use case and features of this template..."
            rows={3}
          />
        </div>

        <div className="grid grid-cols-2 gap-4">
          <div className="space-y-2">
            <Label htmlFor="category">Category</Label>
            <Select value={templateData.category} onValueChange={(value) => updateTemplateData({ category: value })}>
              <SelectTrigger>
                <SelectValue placeholder="Select category" />
              </SelectTrigger>
              <SelectContent>
                {TEMPLATE_CATEGORIES.map((category) => (
                  <SelectItem key={category.value} value={category.value}>
                    <div className="space-y-1">
                      <div>{category.label}</div>
                      <div className="text-xs text-muted-foreground">{category.description}</div>
                    </div>
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>
          </div>

          <div className="space-y-2">
            <Label htmlFor="industry">Industry (Optional)</Label>
            <Input
              id="industry"
              value={templateData.industry}
              onChange={(e) => updateTemplateData({ industry: e.target.value })}
              placeholder="e.g., Automotive, Electronics"
            />
          </div>
        </div>

        <div className="space-y-2">
          <Label>Tags</Label>
          <div className="flex gap-2 mb-2">
            <Input
              value={tagInput}
              onChange={(e) => setTagInput(e.target.value)}
              placeholder="Add tags..."
              onKeyPress={(e) => e.key === 'Enter' && addTag()}
            />
            <Button type="button" variant="outline" onClick={addTag}>
              Add
            </Button>
          </div>
          <div className="flex flex-wrap gap-2">
            {templateData.tags.map((tag, index) => (
              <Badge key={index} variant="secondary" className="cursor-pointer" onClick={() => removeTag(tag)}>
                {tag} ×
              </Badge>
            ))}
          </div>
        </div>

        <div className="space-y-2">
          <Label>Privacy Setting</Label>
          <Select value={templateData.visibility} onValueChange={(value: any) => updateTemplateData({ visibility: value })}>
            <SelectTrigger>
              <SelectValue placeholder="Select visibility" />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="PRIVATE">
                <div className="flex items-center gap-2">
                  <Lock className="h-4 w-4" />
                  Private - Only you can see this
                </div>
              </SelectItem>
              <SelectItem value="COMPANY">
                <div className="flex items-center gap-2">
                  <Building className="h-4 w-4" />
                  Company - Your organization only
                </div>
              </SelectItem>
              <SelectItem value="PUBLIC">
                <div className="flex items-center gap-2">
                  <Globe className="h-4 w-4" />
                  Public - Everyone can see this
                </div>
              </SelectItem>
            </SelectContent>
          </Select>
        </div>
      </div>
    </div>
  );

  const renderStructureStep = () => (
    <div className="space-y-6">
      <div className="text-center mb-6">
        <Grid3X3 className="h-12 w-12 mx-auto mb-4 text-primary" />
        <h3 className="text-lg font-semibold">Warehouse Structure</h3>
        <p className="text-sm text-muted-foreground">
          Define the physical layout of your storage areas
        </p>
      </div>

      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        <div className="space-y-2">
          <Label htmlFor="num_aisles">Aisles *</Label>
          <Input
            id="num_aisles"
            type="number"
            min="1"
            value={templateData.num_aisles}
            onChange={(e) => updateTemplateData({ num_aisles: parseInt(e.target.value) || 0 })}
          />
        </div>
        <div className="space-y-2">
          <Label htmlFor="racks_per_aisle">Racks per Aisle *</Label>
          <Input
            id="racks_per_aisle"
            type="number"
            min="1"
            value={templateData.racks_per_aisle}
            onChange={(e) => updateTemplateData({ racks_per_aisle: parseInt(e.target.value) || 0 })}
          />
        </div>
        <div className="space-y-2">
          <Label htmlFor="positions_per_rack">Positions per Rack *</Label>
          <Input
            id="positions_per_rack"
            type="number"
            min="1"
            value={templateData.positions_per_rack}
            onChange={(e) => updateTemplateData({ positions_per_rack: parseInt(e.target.value) || 0 })}
          />
        </div>
        <div className="space-y-2">
          <Label htmlFor="levels_per_position">Levels per Position *</Label>
          <Input
            id="levels_per_position"
            type="number"
            min="1"
            value={templateData.levels_per_position}
            onChange={(e) => updateTemplateData({ levels_per_position: parseInt(e.target.value) || 0 })}
          />
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <div className="space-y-2">
          <Label htmlFor="level_names">Level Names</Label>
          <Input
            id="level_names"
            value={templateData.level_names}
            onChange={(e) => updateTemplateData({ level_names: e.target.value })}
            placeholder="e.g., ABCD or 1234"
          />
        </div>
        <div className="space-y-2">
          <Label htmlFor="default_pallet_capacity">Pallets per Level</Label>
          <Input
            id="default_pallet_capacity"
            type="number"
            min="1"
            value={templateData.default_pallet_capacity}
            onChange={(e) => updateTemplateData({ default_pallet_capacity: parseInt(e.target.value) || 1 })}
          />
        </div>
        <div className="space-y-2">
          <Label htmlFor="default_zone">Default Zone</Label>
          <Input
            id="default_zone"
            value={templateData.default_zone}
            onChange={(e) => updateTemplateData({ default_zone: e.target.value })}
            placeholder="e.g., GENERAL"
          />
        </div>
      </div>

      <div className="flex items-center space-x-2">
        <Switch
          id="bidimensional_racks"
          checked={templateData.bidimensional_racks}
          onCheckedChange={(checked) => updateTemplateData({ bidimensional_racks: checked })}
        />
        <Label htmlFor="bidimensional_racks">Bidimensional Racks (Deep Storage)</Label>
      </div>

      {/* Calculations Display */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Calculator className="h-5 w-5" />
            Template Capacity
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-3 gap-4 text-center">
            <div>
              <div className="text-2xl font-bold text-primary">{calculateTotals().storageLocations.toLocaleString()}</div>
              <div className="text-sm text-muted-foreground">Storage Locations</div>
            </div>
            <div>
              <div className="text-2xl font-bold text-primary">{calculateTotals().storageCapacity.toLocaleString()}</div>
              <div className="text-sm text-muted-foreground">Storage Capacity</div>
            </div>
            <div>
              <div className="text-2xl font-bold text-primary">{Math.ceil(calculateTotals().storageLocations / 1000)}</div>
              <div className="text-sm text-muted-foreground">Setup Time (min)</div>
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  );

  const renderSpecialAreasStep = () => (
    <div className="space-y-6">
      <div className="text-center mb-6">
        <Package className="h-12 w-12 mx-auto mb-4 text-primary" />
        <h3 className="text-lg font-semibold">Special Areas</h3>
        <p className="text-sm text-muted-foreground">
          Configure receiving, staging, and dock areas (optional)
        </p>
      </div>

      <Alert>
        <Info className="h-4 w-4" />
        <AlertDescription>
          Special areas are optional. You can skip this step and add them later when applying the template to a warehouse.
        </AlertDescription>
      </Alert>

      <div className="space-y-4">
        <SpecialAreaEditor
          title="Receiving Areas"
          description="Areas for incoming inventory"
          areas={templateData.receiving_areas}
          areaType="RECEIVING"
          onAreasChange={(areas) => updateTemplateData({ receiving_areas: areas })}
        />

        <SpecialAreaEditor
          title="Staging Areas"
          description="Temporary storage areas"
          areas={templateData.staging_areas}
          areaType="STAGING"
          onAreasChange={(areas) => updateTemplateData({ staging_areas: areas })}
        />

        <SpecialAreaEditor
          title="Dock Areas"
          description="Loading/unloading docks"
          areas={templateData.dock_areas}
          areaType="DOCK"
          onAreasChange={(areas) => updateTemplateData({ dock_areas: areas })}
        />
      </div>
    </div>
  );

  const renderReviewStep = () => {
    const totals = calculateTotals();
    
    return (
      <div className="space-y-6">
        <div className="text-center mb-6">
          <CheckCircle className="h-12 w-12 mx-auto mb-4 text-green-600" />
          <h3 className="text-lg font-semibold">Review Template</h3>
          <p className="text-sm text-muted-foreground">
            Review your template configuration before creating
          </p>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          <Card>
            <CardHeader>
              <CardTitle>Template Information</CardTitle>
            </CardHeader>
            <CardContent className="space-y-3">
              <div>
                <Label>Name</Label>
                <div className="font-medium">{templateData.name}</div>
              </div>
              <div>
                <Label>Description</Label>
                <div className="text-sm text-muted-foreground">
                  {templateData.description || 'No description provided'}
                </div>
              </div>
              <div>
                <Label>Category</Label>
                <Badge variant="outline">
                  {TEMPLATE_CATEGORIES.find(c => c.value === templateData.category)?.label}
                </Badge>
              </div>
              <div>
                <Label>Privacy</Label>
                <div className="flex items-center gap-2">
                  {getVisibilityIcon(templateData.visibility)}
                  <span className="text-sm">
                    {templateData.visibility === 'PRIVATE' && 'Private (Only You)'}
                    {templateData.visibility === 'COMPANY' && 'Company Only'}
                    {templateData.visibility === 'PUBLIC' && 'Public (Everyone)'}
                  </span>
                </div>
              </div>
              {templateData.tags.length > 0 && (
                <div>
                  <Label>Tags</Label>
                  <div className="flex flex-wrap gap-2">
                    {templateData.tags.map((tag, index) => (
                      <Badge key={index} variant="secondary">{tag}</Badge>
                    ))}
                  </div>
                </div>
              )}
            </CardContent>
          </Card>

          <Card>
            <CardHeader>
              <CardTitle>Structure Summary</CardTitle>
            </CardHeader>
            <CardContent className="space-y-3">
              <div className="grid grid-cols-2 gap-4 text-sm">
                <div>
                  <Label>Aisles</Label>
                  <div className="font-medium">{templateData.num_aisles}</div>
                </div>
                <div>
                  <Label>Racks per Aisle</Label>
                  <div className="font-medium">{templateData.racks_per_aisle}</div>
                </div>
                <div>
                  <Label>Positions per Rack</Label>
                  <div className="font-medium">{templateData.positions_per_rack}</div>
                </div>
                <div>
                  <Label>Levels per Position</Label>
                  <div className="font-medium">{templateData.levels_per_position}</div>
                </div>
              </div>
              <Separator />
              <div className="space-y-2">
                <div className="flex justify-between">
                  <span className="text-sm">Storage Locations:</span>
                  <span className="font-medium">{totals.storageLocations.toLocaleString()}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-sm">Storage Capacity:</span>
                  <span className="font-medium">{totals.storageCapacity.toLocaleString()} pallets</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-sm">Special Areas:</span>
                  <span className="font-medium">
                    {templateData.receiving_areas.length + templateData.staging_areas.length + templateData.dock_areas.length}
                  </span>
                </div>
              </div>
            </CardContent>
          </Card>
        </div>

        {error && (
          <Alert variant="destructive">
            <AlertDescription>{error}</AlertDescription>
          </Alert>
        )}
      </div>
    );
  };

  return (
    <Dialog open={open} onOpenChange={onClose}>
      <DialogContent className="max-w-4xl max-h-[90vh] overflow-y-auto">
        <DialogHeader>
          <DialogTitle>Create New Template</DialogTitle>
          <DialogDescription>
            Design a warehouse layout template from scratch that can be reused and shared
          </DialogDescription>
        </DialogHeader>

        <div className="space-y-6">
          {/* Progress Bar */}
          <div className="space-y-2">
            <div className="flex justify-between items-center text-sm">
              <span>Step {currentStep} of {totalSteps}</span>
              <span>{Math.round(progress)}% Complete</span>
            </div>
            <Progress value={progress} className="w-full" />
          </div>

          {/* Step Content */}
          {renderStep()}

          {/* Navigation */}
          <div className="flex justify-between">
            <Button
              variant="outline"
              onClick={() => setCurrentStep(Math.max(1, currentStep - 1))}
              disabled={currentStep === 1}
            >
              <ChevronLeft className="h-4 w-4 mr-2" />
              Previous
            </Button>

            <div className="flex gap-2">
              <Button variant="outline" onClick={onClose}>
                Cancel
              </Button>
              
              {currentStep < totalSteps ? (
                <Button
                  onClick={() => setCurrentStep(Math.min(totalSteps, currentStep + 1))}
                  disabled={!canProceed()}
                >
                  Next
                  <ChevronRight className="h-4 w-4 ml-2" />
                </Button>
              ) : (
                <div className="flex gap-2">
                  <Button 
                    variant="outline" 
                    onClick={() => handleSubmit(false)} 
                    disabled={!canProceed() || loading}
                  >
                    {loading ? (
                      <>
                        <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-gray-600 mr-2"></div>
                        Creating...
                      </>
                    ) : (
                      'Create Only'
                    )}
                  </Button>
                  
                  <Button 
                    onClick={() => handleSubmit(true)} 
                    disabled={!canProceed() || loading}
                    className="bg-green-600 hover:bg-green-700"
                  >
                    {loading ? (
                      <>
                        <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white mr-2"></div>
                        Creating...
                      </>
                    ) : (
                      <>
                        <Zap className="h-4 w-4 mr-2" />
                        Create & Test Now
                      </>
                    )}
                  </Button>
                </div>
              )}
            </div>
          </div>
        </div>
      </DialogContent>
    </Dialog>
  );
}