'use client';

import React, { useState, useEffect, useRef } from 'react';
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
  Users,
  Zap,
  Trophy,
  Award,
  Globe
} from 'lucide-react';
import { standaloneTemplateAPI, type StandaloneTemplateData } from '@/lib/standalone-template-api';
import { templateApi } from '@/lib/location-api';
import { SpecialAreaEditor } from './special-area-editor';
import { LocationFormatStep } from './LocationFormatStep';

interface TemplateCreationWizardProps {
  open: boolean;
  onClose: () => void;
  onTemplateCreated?: (template: any, warehouseConfig?: any) => void;
  
  // NEW: Dual-behavior props
  isFirstTimeSetup?: boolean;
  warehouseId?: string;
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
  aisle_areas: Array<{
    code: string;
    type: string;
    capacity: number;
    zone: string;
  }>;
  
  // Location Format Configuration
  format_config?: object;
  format_pattern_name?: string;
  format_examples?: string[];

  // Unit-Agnostic Configuration
  default_unit_type: 'pallets' | 'boxes' | 'items' | 'cases' | 'mixed';
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
    { code: 'RECV-01', type: 'RECEIVING', capacity: 10, zone: 'RECEIVING' }
  ],
  staging_areas: [],
  dock_areas: [],
  aisle_areas: [],
  format_config: undefined,
  format_pattern_name: undefined,
  format_examples: undefined,
  default_unit_type: 'pallets'
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

export function TemplateCreationWizard({ 
  open, 
  onClose, 
  onTemplateCreated, 
  isFirstTimeSetup = false, 
  warehouseId 
}: TemplateCreationWizardProps) {
  const [currentStep, setCurrentStep] = useState(1);
  const [templateData, setTemplateData] = useState<TemplateData>(INITIAL_TEMPLATE_DATA);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [tagInput, setTagInput] = useState('');
  const [formatApplied, setFormatApplied] = useState(false);


  // Ref for dialog content to enable scroll control
  const dialogContentRef = useRef<HTMLDivElement>(null);

  // Auto-scroll to top when step changes
  useEffect(() => {
    if (dialogContentRef.current) {
      dialogContentRef.current.scrollTo({
        top: 0,
        behavior: 'smooth'
      });
    }
  }, [currentStep]);

  const totalSteps = 5;
  const progress = (currentStep / totalSteps) * 100;

  const updateTemplateData = (updates: Partial<TemplateData>) => {
    setTemplateData(prev => ({ ...prev, ...updates }));
  };

  const calculateTotals = () => {
    const storageLocations = templateData.num_aisles * templateData.racks_per_aisle * 
                           templateData.positions_per_rack * templateData.levels_per_position;
    const storageCapacity = storageLocations * templateData.default_pallet_capacity;
    const specialCapacity = [...templateData.receiving_areas, ...templateData.staging_areas, ...templateData.dock_areas, ...templateData.aisle_areas]
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
      code: `RECV-${String(templateData.receiving_areas.length + 1).padStart(2, '0')}`,
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

  const generateAisleAreas = () => {
    const aisleAreas = [];
    for (let i = 1; i <= templateData.num_aisles; i++) {
      aisleAreas.push({
        code: `AISLE-${String(i).padStart(2, '0')}`,
        type: 'TRANSITIONAL',
        capacity: 10,
        zone: 'GENERAL'
      });
    }
    updateTemplateData({ aisle_areas: aisleAreas });
  };

  const handleFormatDetected = (formatConfig: object, patternName: string, examples: string[]) => {
    try {
      // Validate the format config before applying
      if (!formatConfig || !patternName || !examples || examples.length === 0) {
        console.warn('Invalid format detection data received:', { formatConfig, patternName, examples });
        return;
      }

      updateTemplateData({
        format_config: formatConfig,
        format_pattern_name: patternName,
        format_examples: examples
      });
      
      // Optional: Auto-advance to next step only if user explicitly clicks the button
      // This prevents automatic navigation that might cause state conflicts
      console.log('Format detected and applied:', patternName);
      
    } catch (error) {
      console.error('Error applying format detection:', error);
      setError('Failed to apply format configuration. Please try again.');
    }
  };

  const handleManualConfiguration = () => {
    // Skip to next step, allowing manual configuration later
    setCurrentStep(Math.min(totalSteps, currentStep + 1));
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

  const handleSubmit = async () => {
    setLoading(true);
    setError(null);
    
    try {
      // Convert to API format
      // Prepare location format data in the structure expected by backend
      const locationFormatData: any = {};
      if (templateData.format_config || (templateData.format_examples && templateData.format_examples.length > 0)) {
        locationFormatData.format_config = templateData.format_config;
        locationFormatData.pattern_name = templateData.format_pattern_name;
        locationFormatData.examples = templateData.format_examples || [];
        
        // Note: confidence data would be added here if available from format detection
      }

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
        dock_areas: templateData.dock_areas,
        
        // NEW: Send format data in nested structure expected by backend
        location_format: Object.keys(locationFormatData).length > 0 ? locationFormatData : undefined,
        
        // DEPRECATED: Keep flat format for backward compatibility (will be removed)
        format_config: templateData.format_config,
        format_pattern_name: templateData.format_pattern_name,
        format_examples: templateData.format_examples
      };
      
      // Step 1: Create template (existing behavior)
      const createdTemplate = await standaloneTemplateAPI.createTemplate(apiData);
      
      // Step 2: Apply template to warehouse (NEW for first-time setup)
      if (isFirstTimeSetup && warehouseId) {
        const applyResult = await templateApi.applyTemplateByCode(
          createdTemplate.template_code,
          warehouseId,
          templateData.name
        );
        
        onTemplateCreated?.(createdTemplate, applyResult.configuration);
      } else {
        // Existing template-only creation
        onTemplateCreated?.(createdTemplate);
      }
      
      onClose();
      
    } catch (err: any) {
      // Enhanced error handling for dual operation
      if (err?.message?.includes('template creation')) {
        setError('Failed to create template. Please check your configuration.');
      } else if (err?.message?.includes('apply template')) {
        setError(`Template "${templateData.name}" created but warehouse setup failed. You can apply it manually later.`);
      } else {
        setError(err?.response?.data?.error || 'Failed to create template. Please try again.');
      }
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
        return formatApplied; // CRITICAL: Format configuration must be applied to proceed
      case 4:
        return true; // Special areas are optional
      case 5:
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
        return renderLocationFormatStep();
      case 4:
        return renderSpecialAreasStep();
      case 5:
        return renderReviewStep();
      default:
        return null;
    }
  };

  const renderBasicInfoStep = () => (
    <div className="space-y-8">
      <div className="text-center mb-8">
        <div className="inline-flex items-center justify-center w-16 h-16 rounded-full bg-gradient-to-br from-slate-700 to-blue-800 shadow-xl mb-4">
          <Building2 className="h-8 w-8 text-blue-300" />
        </div>
        <h3 className="text-2xl font-bold text-gray-900 mb-2">
          {isFirstTimeSetup ? 'Set Up Your Warehouse' : 'Design Your Warehouse Layout'}
        </h3>
        <p className="text-base text-gray-600 max-w-md mx-auto">
          {isFirstTimeSetup 
            ? "Let's build your warehouse from the ground up with all the features you need" 
            : "Let's start by setting up the basics for your warehouse design"
          }
        </p>
      </div>

      {/* Main Information Form */}
      <div className="space-y-6">
        <div className="space-y-2">
          <Label htmlFor="name" className="text-base font-medium text-gray-900">
            What should we call your warehouse? *
          </Label>
          <Input
            id="name"
            value={templateData.name}
            onChange={(e) => updateTemplateData({ name: e.target.value })}
            placeholder="e.g., Main Distribution Center, North Warehouse"
            className="text-base py-3"
          />
        </div>

        <div className="space-y-2">
          <Label htmlFor="description" className="text-base font-medium text-gray-900">
            Tell us about your warehouse (optional)
          </Label>
          <Textarea
            id="description"
            value={templateData.description}
            onChange={(e) => updateTemplateData({ description: e.target.value })}
            placeholder="e.g., Main distribution center for automotive parts, handles 500 pallets daily..."
            rows={3}
            className="text-base"
          />
        </div>
      </div>

      {/* Quick Start Templates - Less Prominent */}
      <div className="relative">
        <div className="absolute inset-0 flex items-center">
          <span className="w-full border-t border-gray-200" />
        </div>
        <div className="relative flex justify-center text-sm">
          <span className="bg-white px-4 text-gray-500">Need a starting point?</span>
        </div>
      </div>

      <details className="group">
        <summary className="cursor-pointer list-none">
          <div className="flex items-center justify-center gap-2 text-sm text-gray-600 hover:text-gray-900 transition-colors py-2">
            <Palette className="h-4 w-4" />
            <span>Browse quick start templates</span>
            <ChevronRight className="h-4 w-4 transition-transform group-open:rotate-90" />
          </div>
        </summary>
        
        <div className="mt-4 p-4 bg-gray-50 rounded-lg border">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
            {STARTER_TEMPLATES.map((starter, index) => (
              <div 
                key={index} 
                className="cursor-pointer p-3 bg-white rounded border hover:border-blue-200 hover:shadow-sm transition-all duration-200"
                onClick={() => applyStarterTemplate(starter)}
              >
                <div className="space-y-2">
                  <div className="flex items-start justify-between">
                    <div className="font-medium text-gray-900 text-sm">{starter.name}</div>
                    <Badge variant="outline" className="text-xs">
                      {TEMPLATE_CATEGORIES.find(c => c.value === starter.category)?.label}
                    </Badge>
                  </div>
                  <div className="text-xs text-gray-600">{starter.description}</div>
                  <div className="flex items-center justify-between">
                    <div className="text-xs font-mono text-gray-500 bg-gray-100 px-2 py-1 rounded">
                      {starter.structure.aisles}A × {starter.structure.racks}R × {starter.structure.positions}P × {starter.structure.levels}L
                    </div>
                    <div className="text-xs text-blue-600">Use this →</div>
                  </div>
                </div>
              </div>
            ))}
          </div>
          <p className="text-xs text-gray-500 mt-3 text-center">
            Templates provide a starting point - you can customize everything in the next steps
          </p>
        </div>
      </details>
    </div>
  );

  const renderStructureStep = () => (
    <div className="space-y-5">
      <div className="text-center mb-3">
        <div className="inline-flex items-center justify-center w-10 h-10 rounded-full bg-gradient-to-br from-slate-700 to-blue-800 shadow-lg mb-2">
          <Grid3X3 className="h-5 w-5 text-blue-300" />
        </div>
        <h3 className="text-lg font-bold text-gray-900 mb-1">Design Your Storage Layout</h3>
        <p className="text-sm text-gray-600 max-w-lg mx-auto">
          Let's set up how many aisles, racks, and storage levels you need. Don't worry - you can always adjust these later!
        </p>
      </div>

      {/* Main Structure Configuration */}
      <div className="bg-gray-50 p-4 rounded-lg border">
        <h4 className="text-base font-semibold text-gray-900 mb-2">Basic Layout</h4>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
          <div className="space-y-2">
            <Label htmlFor="num_aisles" className="text-sm font-medium text-gray-900">
              How many aisles? *
            </Label>
            <Input
              id="num_aisles"
              type="number"
              min="1"
              value={templateData.num_aisles}
              onChange={(e) => updateTemplateData({ num_aisles: parseInt(e.target.value) || 0 })}
              className="text-sm py-2"
            />
            <p className="text-xs text-gray-500">Main walkways through your warehouse</p>
          </div>
          <div className="space-y-2">
            <Label htmlFor="racks_per_aisle" className="text-sm font-medium text-gray-900">
              Racks per aisle? *
            </Label>
            <Input
              id="racks_per_aisle"
              type="number"
              min="1"
              value={templateData.racks_per_aisle}
              onChange={(e) => updateTemplateData({ racks_per_aisle: parseInt(e.target.value) || 0 })}
              className="text-sm py-2"
            />
            <p className="text-xs text-gray-500">Storage racks along each aisle</p>
          </div>
          <div className="space-y-2">
            <Label htmlFor="positions_per_rack" className="text-sm font-medium text-gray-900">
              Positions per rack? *
            </Label>
            <Input
              id="positions_per_rack"
              type="number"
              min="1"
              value={templateData.positions_per_rack}
              onChange={(e) => updateTemplateData({ positions_per_rack: parseInt(e.target.value) || 0 })}
              className="text-sm py-2"
            />
            <p className="text-xs text-gray-500">Storage spots along each rack</p>
          </div>
          <div className="space-y-2">
            <Label htmlFor="levels_per_position" className="text-sm font-medium text-gray-900">
              Levels high? *
            </Label>
            <Input
              id="levels_per_position"
              type="number"
              min="1"
              value={templateData.levels_per_position}
              onChange={(e) => updateTemplateData({ levels_per_position: parseInt(e.target.value) || 0 })}
              className="text-sm py-2"
            />
            <p className="text-xs text-gray-500">How many levels to stack pallets</p>
          </div>
        </div>
      </div>

      {/* Additional Settings */}
      <div className="space-y-3">
        <h4 className="text-base font-semibold text-gray-900">Storage Details</h4>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <div className="space-y-2">
            <Label htmlFor="level_names" className="text-sm font-medium text-gray-900">
              Level naming
            </Label>
            <Input
              id="level_names"
              value={templateData.level_names}
              onChange={(e) => updateTemplateData({ level_names: e.target.value })}
              placeholder="e.g., ABCD or 1234"
              className="text-sm py-2"
            />
            <p className="text-xs text-gray-500">How to label each level (A, B, C or 1, 2, 3)</p>
          </div>
          <div className="space-y-2">
            <Label htmlFor="default_pallet_capacity" className="text-sm font-medium text-gray-900">
              Pallets per level
            </Label>
            <Input
              id="default_pallet_capacity"
              type="number"
              min="1"
              value={templateData.default_pallet_capacity}
              onChange={(e) => updateTemplateData({ default_pallet_capacity: parseInt(e.target.value) || 1 })}
              className="text-sm py-2"
            />
            <p className="text-xs text-gray-500">How many pallets fit in each level</p>
          </div>
          <div className="space-y-2">
            <Label htmlFor="default_zone" className="text-sm font-medium text-gray-900">
              Zone name
            </Label>
            <Input
              id="default_zone"
              value={templateData.default_zone}
              onChange={(e) => updateTemplateData({ default_zone: e.target.value })}
              placeholder="e.g., GENERAL"
              className="text-sm py-2"
            />
            <p className="text-xs text-gray-500">Name for your main storage area</p>
          </div>
        </div>

      </div>

      {/* Warehouse Summary */}
      <div className="bg-gradient-to-r from-slate-800 to-blue-900 p-4 rounded-lg border border-slate-700 shadow-lg">
        <div className="flex items-center gap-3 mb-3">
          <div className="inline-flex items-center justify-center w-8 h-8 rounded-full bg-blue-500/20 backdrop-blur-sm">
            <Calculator className="h-4 w-4 text-blue-300" />
          </div>
          <h4 className="text-lg font-bold text-white">Your Warehouse Capacity</h4>
        </div>
        
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div className="text-center p-3 bg-white/10 backdrop-blur-sm rounded-lg border border-white/20">
            <div className="text-2xl font-bold text-emerald-400 mb-1">
              {calculateTotals().storageLocations.toLocaleString()}
            </div>
            <div className="text-sm font-medium text-slate-200">Storage Locations</div>
            <div className="text-xs text-slate-300">Individual storage spots</div>
          </div>
          <div className="text-center p-3 bg-white/10 backdrop-blur-sm rounded-lg border border-white/20">
            <div className="text-2xl font-bold text-blue-400 mb-1">
              {calculateTotals().storageCapacity.toLocaleString()}
            </div>
            <div className="text-sm font-medium text-slate-200">Pallet Capacity</div>
            <div className="text-xs text-slate-300">Total pallets you can store</div>
          </div>
        </div>
        
        <div className="mt-3 text-center">
          <p className="text-sm text-slate-200">
            🎉 <strong className="text-white">Great choice!</strong> This layout will give you plenty of storage capacity and flexibility.
          </p>
        </div>
      </div>
    </div>
  );

  const renderLocationFormatStep = () => (
    <LocationFormatStep
      onFormatDetected={handleFormatDetected}
      onManualConfiguration={handleManualConfiguration}
      onFormatApplied={setFormatApplied}
      initialExamples=""
    />
  );

  const renderSpecialAreasStep = () => (
    <div className="space-y-8">
      <div className="text-center mb-8">
        <div className="inline-flex items-center justify-center w-16 h-16 rounded-full bg-gradient-to-br from-slate-700 to-indigo-800 shadow-xl mb-4">
          <Package className="h-8 w-8 text-indigo-300" />
        </div>
        <h3 className="text-2xl font-bold text-gray-900 mb-2">Set Up Work Areas</h3>
        <p className="text-base text-gray-600 max-w-lg mx-auto">
          Add areas where you receive deliveries, prepare shipments, and handle day-to-day operations
        </p>
      </div>

      <div className="bg-gradient-to-r from-slate-50 to-blue-50 border border-slate-200 rounded-lg p-4 shadow-sm">
        <div className="flex items-start gap-3">
          <div className="inline-flex items-center justify-center w-8 h-8 rounded-full bg-gradient-to-br from-slate-600 to-blue-700 shadow-lg">
            <Info className="h-4 w-4 text-blue-200" />
          </div>
          <div>
            <div className="font-semibold text-blue-900">This step is optional</div>
            <div className="text-sm text-blue-700 mt-1">
              You can skip this for now and add work areas later, or set up the basic ones you know you'll need.
            </div>
          </div>
        </div>
      </div>

      <div className="space-y-6">
        <SpecialAreaEditor
          title="📦 Receiving Areas"
          description="Where trucks deliver and you check in new inventory"
          areas={templateData.receiving_areas}
          areaType="RECEIVING"
          onAreasChange={(areas) => updateTemplateData({ receiving_areas: areas })}
        />

        <SpecialAreaEditor
          title="📋 Staging Areas"
          description="Temporary spots for organizing pallets before putting them away"
          areas={templateData.staging_areas}
          areaType="STAGING"
          onAreasChange={(areas) => updateTemplateData({ staging_areas: areas })}
        />

        <SpecialAreaEditor
          title="🚛 Dock Areas"
          description="Loading docks where trucks pick up outgoing shipments"
          areas={templateData.dock_areas}
          areaType="DOCK"
          onAreasChange={(areas) => updateTemplateData({ dock_areas: areas })}
        />
        <SpecialAreaEditor
          title="🚶 Aisle Areas"
          description="Walkway spaces for moving pallets between storage and work areas"
          areas={templateData.aisle_areas}
          areaType="TRANSITIONAL"
          onAreasChange={(areas) => updateTemplateData({ aisle_areas: areas })}
        />
        
        {templateData.aisle_areas.length === 0 && (
          <div className="bg-gradient-to-r from-emerald-50 to-slate-50 border border-emerald-200 rounded-lg p-4 shadow-sm">
            <div className="flex items-center justify-between">
              <div className="flex items-start gap-3">
                <div className="inline-flex items-center justify-center w-8 h-8 rounded-full bg-gradient-to-br from-emerald-600 to-slate-700 shadow-lg">
                  <Zap className="h-4 w-4 text-emerald-200" />
                </div>
                <div>
                  <div className="font-semibold text-slate-800">Quick setup available</div>
                  <div className="text-sm text-slate-600 mt-1">
                    We can automatically create walkway areas for all {templateData.num_aisles} of your aisles
                  </div>
                </div>
              </div>
              <Button 
                variant="outline" 
                size="sm" 
                onClick={generateAisleAreas}
                className="bg-white hover:bg-emerald-50 border-emerald-300 text-emerald-700 shadow-sm"
              >
                ✨ Auto-Generate
              </Button>
            </div>
          </div>
        )}
      </div>
    </div>
  );


  const renderReviewStep = () => {
    const totals = calculateTotals();
    
    return (
      <div className="space-y-8">
        <div className="text-center mb-8">
          <div className="inline-flex items-center justify-center w-20 h-20 rounded-full bg-gradient-to-br from-slate-700 to-blue-800 shadow-xl mb-6">
            <Trophy className="h-10 w-10 text-blue-300" />
          </div>
          <h3 className="text-3xl font-bold text-gray-900 mb-3">
            {isFirstTimeSetup ? '🎉 Your Warehouse is Ready!' : '🎉 Your Warehouse Design is Ready!'}
          </h3>
          <p className="text-lg text-gray-600 max-w-2xl mx-auto">
            {isFirstTimeSetup 
              ? <>Excellent! You've built a complete warehouse that will handle <strong>{totals.storageCapacity.toLocaleString()} pallets</strong> across <strong>{totals.storageLocations.toLocaleString()} storage locations</strong>. Plus, we've created a reusable template for future use.</>
              : <>Amazing work! You've designed a complete warehouse layout that will handle <strong>{totals.storageCapacity.toLocaleString()} pallets</strong> across <strong>{totals.storageLocations.toLocaleString()} storage locations</strong>.</>
            }
          </p>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
          <Card className="border-2 border-slate-300 bg-gradient-to-br from-white to-slate-100 shadow-xl">
            <CardHeader>
              <CardTitle className="text-xl font-bold text-gray-900 flex items-center gap-2">
                🏢 Your Warehouse: {templateData.name}
              </CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              {templateData.description && (
                <div className="bg-white p-3 rounded-lg border">
                  <p className="text-sm text-gray-700 italic">"{templateData.description}"</p>
                </div>
              )}
              
              <div className="space-y-3">
                <div className="flex items-center justify-between">
                  <span className="text-sm font-medium text-gray-600">Business Type:</span>
                  <Badge variant="outline" className="bg-white">
                    {TEMPLATE_CATEGORIES.find(c => c.value === templateData.category)?.label || 'Custom'}
                  </Badge>
                </div>
                
                {templateData.format_pattern_name && (
                  <div className="flex items-center justify-between">
                    <span className="text-sm font-medium text-gray-600">Location System:</span>
                    <Badge variant="outline" className="text-green-700 bg-green-50 border-green-200">
                      {templateData.format_pattern_name}
                    </Badge>
                  </div>
                )}
                
                <div className="flex items-center justify-between">
                  <span className="text-sm font-medium text-gray-600">Sharing:</span>
                  <div className="flex items-center gap-2">
                    {getVisibilityIcon(templateData.visibility)}
                    <span className="text-sm">
                      {templateData.visibility === 'PRIVATE' && 'Private (Only You)'}
                      {templateData.visibility === 'COMPANY' && 'Company Team'}
                      {templateData.visibility === 'PUBLIC' && 'Public'}
                    </span>
                  </div>
                </div>
              </div>
              
              {templateData.tags.length > 0 && (
                <div>
                  <div className="text-sm font-medium text-gray-600 mb-2">Tags:</div>
                  <div className="flex flex-wrap gap-2">
                    {templateData.tags.map((tag, index) => (
                      <Badge key={index} variant="secondary" className="bg-blue-100 text-blue-800">{tag}</Badge>
                    ))}
                  </div>
                </div>
              )}
            </CardContent>
          </Card>

          <Card className="border-2 border-slate-400 bg-gradient-to-br from-slate-800 to-blue-900 shadow-2xl">
            <CardHeader>
              <CardTitle className="text-xl font-bold text-white flex items-center gap-2">
                📊 Warehouse Capacity & Layout
              </CardTitle>
            </CardHeader>
            <CardContent className="space-y-6">
              {/* Main Capacity Highlights */}
              <div className="grid grid-cols-2 gap-4">
                <div className="bg-white/10 backdrop-blur-sm p-4 rounded-lg border border-white/20 shadow-sm text-center">
                  <div className="text-2xl font-bold text-emerald-400">{totals.storageLocations.toLocaleString()}</div>
                  <div className="text-sm font-medium text-slate-200">Storage Spots</div>
                </div>
                <div className="bg-white/10 backdrop-blur-sm p-4 rounded-lg border border-white/20 shadow-sm text-center">
                  <div className="text-2xl font-bold text-blue-400">{totals.storageCapacity.toLocaleString()}</div>
                  <div className="text-sm font-medium text-slate-200">Total Pallets</div>
                </div>
              </div>
              
              {/* Layout Details */}
              <div className="bg-white/10 backdrop-blur-sm p-4 rounded-lg border border-white/20">
                <h4 className="text-sm font-semibold text-slate-200 mb-3">Layout Structure</h4>
                <div className="grid grid-cols-2 gap-3 text-sm">
                  <div className="flex justify-between">
                    <span className="text-slate-300">Aisles:</span>
                    <span className="font-medium text-white">{templateData.num_aisles}</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-slate-300">Racks per Aisle:</span>
                    <span className="font-medium text-white">{templateData.racks_per_aisle}</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-slate-300">Positions per Rack:</span>
                    <span className="font-medium text-white">{templateData.positions_per_rack}</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-slate-300">Levels High:</span>
                    <span className="font-medium text-white">{templateData.levels_per_position}</span>
                  </div>
                </div>
              </div>
              
              {/* Work Areas */}
              {(templateData.receiving_areas.length + templateData.staging_areas.length + templateData.dock_areas.length + templateData.aisle_areas.length) > 0 && (
                <div className="bg-white/10 backdrop-blur-sm p-4 rounded-lg border border-white/20">
                  <h4 className="text-sm font-semibold text-slate-200 mb-3">Work Areas Configured</h4>
                  <div className="space-y-2 text-sm">
                    {templateData.receiving_areas.length > 0 && (
                      <div className="flex items-center justify-between">
                        <span className="text-slate-300 flex items-center gap-1">📦 Receiving Areas:</span>
                        <span className="font-medium text-white">{templateData.receiving_areas.length}</span>
                      </div>
                    )}
                    {templateData.staging_areas.length > 0 && (
                      <div className="flex items-center justify-between">
                        <span className="text-slate-300 flex items-center gap-1">📋 Staging Areas:</span>
                        <span className="font-medium text-white">{templateData.staging_areas.length}</span>
                      </div>
                    )}
                    {templateData.dock_areas.length > 0 && (
                      <div className="flex items-center justify-between">
                        <span className="text-slate-300 flex items-center gap-1">🚛 Dock Areas:</span>
                        <span className="font-medium text-white">{templateData.dock_areas.length}</span>
                      </div>
                    )}
                    {templateData.aisle_areas.length > 0 && (
                      <div className="flex items-center justify-between">
                        <span className="text-slate-300 flex items-center gap-1">🚶 Aisle Areas:</span>
                        <span className="font-medium text-white">{templateData.aisle_areas.length}</span>
                      </div>
                    )}
                  </div>
                </div>
              )}
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
      <DialogContent ref={dialogContentRef} className="max-w-4xl max-h-[90vh] overflow-y-auto">
        {currentStep === 1 && (
          <DialogHeader className="text-center pb-2">
            <DialogTitle className="text-2xl font-bold text-gray-900">
              {isFirstTimeSetup ? 'Set Up Your Warehouse' : 'Design Your Warehouse Layout'}
            </DialogTitle>
            <DialogDescription className="text-base text-gray-600 mt-2">
              {isFirstTimeSetup 
                ? "We'll set up your complete warehouse system with all the features and templates you need"
                : "We'll walk you through creating a warehouse layout that works perfectly for your business"
              }
            </DialogDescription>
          </DialogHeader>
        )}

        <div className="space-y-6">
          {/* Progress Bar */}
          <div className="space-y-3">
            <div className="flex justify-between items-center pr-8">
              <span className="text-sm font-medium text-gray-700">Step {currentStep} of {totalSteps}</span>
              <span className="text-sm font-medium text-blue-600">{Math.round(progress)}% Complete</span>
            </div>
            <Progress value={progress} className="w-full h-2" />
            <div className="text-center">
              <span className="text-sm text-gray-500">
                {progress < 25 && "Let's start with the basics"}
                {progress >= 25 && progress < 50 && "Great! Now let's design your layout"}
                {progress >= 50 && progress < 75 && "Perfect! Setting up your location system"}
                {progress >= 75 && progress < 100 && "Almost there! Adding special areas"}
                {progress === 100 && "🎉 Your warehouse design is ready!"}
              </span>
            </div>
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
                <div className="flex flex-col items-end gap-2">
                  <Button
                    onClick={() => setCurrentStep(Math.min(totalSteps, currentStep + 1))}
                    disabled={!canProceed()}
                  >
                    Next
                    <ChevronRight className="h-4 w-4 ml-2" />
                  </Button>
                  {currentStep === 3 && !formatApplied && (
                    <div className="text-xs text-amber-600 flex items-center gap-1">
                      <Info className="h-3 w-3" />
                      Apply format configuration to continue
                    </div>
                  )}
                </div>
              ) : (
                <Button 
                  onClick={handleSubmit} 
                  disabled={!canProceed() || loading}
                  className="bg-gradient-to-r from-slate-800 to-slate-900 hover:from-slate-900 hover:to-black text-white shadow-2xl px-8 py-3 border border-slate-700 hover:border-slate-600 transition-all duration-200"
                  size="lg"
                >
                  {loading ? (
                    <>
                      <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white mr-2"></div>
                      {isFirstTimeSetup ? 'Setting Up Your Warehouse...' : 'Creating Template...'}
                    </>
                  ) : (
                    <>
                      <Building2 className="h-5 w-5 mr-2" />
                      {isFirstTimeSetup ? 'Build My Warehouse! 🚀' : 'Create Template'}
                    </>
                  )}
                </Button>
              )}
            </div>
          </div>
        </div>
      </DialogContent>
    </Dialog>
  );
}