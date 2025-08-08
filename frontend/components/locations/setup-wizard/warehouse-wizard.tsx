'use client';

import React, { useState, useEffect } from 'react';
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogHeader,
  DialogTitle,
} from '@/components/ui/dialog';
import { Button } from '@/components/ui/button';
import { Progress } from '@/components/ui/progress';
import { Alert, AlertDescription } from '@/components/ui/alert';
import { Step1Structure } from './step-1-structure';
import { Step2SpecialAreas } from './step-2-special-areas';
import { Step3Preview } from './step-3-preview';
import { WizardProgress } from './wizard-progress';
import useLocationStore, { WarehouseConfig } from '@/lib/location-store';
import { 
  AlertCircle, 
  Building2, 
  ChevronLeft, 
  ChevronRight,
  Loader2,
  CheckCircle
} from 'lucide-react';

interface WarehouseSetupWizardProps {
  existingConfig?: WarehouseConfig | null;
  warehouseId: string;
  onClose: () => void;
  onComplete: (config: WarehouseConfig) => void;
}

export interface WizardData {
  // Step 1: Structure
  warehouse_name: string;
  num_aisles: number;
  racks_per_aisle: number;
  positions_per_rack: number;
  levels_per_position: number;
  level_names: string;
  default_pallet_capacity: number;
  bidimensional_racks: boolean;
  default_zone: string;
  position_numbering_split: boolean;
  
  // Step 2: Special Areas
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
  
  // Step 3: Options
  generate_locations: boolean;
  force_recreate: boolean;
  create_template: boolean;
  template_name: string;
  template_description: string;
  template_is_public: boolean;
}

const INITIAL_WIZARD_DATA: WizardData = {
  warehouse_name: '',
  num_aisles: 4,
  racks_per_aisle: 2,
  positions_per_rack: 50,
  levels_per_position: 4,
  level_names: 'ABCD',
  default_pallet_capacity: 1,
  bidimensional_racks: false,
  default_zone: 'GENERAL',
  position_numbering_split: true,
  receiving_areas: [
    { code: 'RECEIVING', type: 'RECEIVING', capacity: 10, zone: 'DOCK' }
  ],
  staging_areas: [],
  dock_areas: [],
  generate_locations: true,
  force_recreate: false,
  create_template: false,
  template_name: '',
  template_description: '',
  template_is_public: false
};

export function WarehouseSetupWizard({ 
  existingConfig, 
  warehouseId, 
  onClose, 
  onComplete 
}: WarehouseSetupWizardProps) {
  const [currentStep, setCurrentStep] = useState(1);
  const [wizardData, setWizardData] = useState<WizardData>(INITIAL_WIZARD_DATA);
  const [validationResults, setValidationResults] = useState<any>(null);
  const [previewData, setPreviewData] = useState<any>(null);
  
  const {
    setupWarehouse,
    validateWarehouseConfig,
    previewWarehouseSetup,
    loading,
    error,
    clearError
  } = useLocationStore();

  const totalSteps = 3;
  const progressPercentage = (currentStep / totalSteps) * 100;

  // Initialize wizard data from existing config
  useEffect(() => {
    if (existingConfig) {
      setWizardData({
        warehouse_name: existingConfig.warehouse_name,
        num_aisles: existingConfig.num_aisles,
        racks_per_aisle: existingConfig.racks_per_aisle,
        positions_per_rack: existingConfig.positions_per_rack,
        levels_per_position: existingConfig.levels_per_position,
        level_names: existingConfig.level_names,
        default_pallet_capacity: existingConfig.default_pallet_capacity,
        bidimensional_racks: existingConfig.bidimensional_racks,
        default_zone: existingConfig.default_zone,
        position_numbering_split: existingConfig.position_numbering_split,
        receiving_areas: existingConfig.receiving_areas,
        staging_areas: existingConfig.staging_areas || [],
        dock_areas: existingConfig.dock_areas || [],
        generate_locations: true,
        force_recreate: true, // Allow recreation if editing existing
        create_template: false,
        template_name: '',
        template_description: '',
        template_is_public: false
      });
    } else {
      // Set default warehouse name
      setWizardData(prev => ({
        ...prev,
        warehouse_name: `Warehouse ${warehouseId}`,
        template_name: `Warehouse ${warehouseId} Template`
      }));
    }
  }, [existingConfig, warehouseId]);

  // Update wizard data
  const updateWizardData = (updates: Partial<WizardData>) => {
    setWizardData(prev => ({ ...prev, ...updates }));
  };

  // Validate current step
  const validateCurrentStep = async () => {
    clearError();
    
    try {
      if (currentStep === 1) {
        // Validate warehouse structure
        const validation = await validateWarehouseConfig({
          num_aisles: wizardData.num_aisles,
          racks_per_aisle: wizardData.racks_per_aisle,
          positions_per_rack: wizardData.positions_per_rack,
          levels_per_position: wizardData.levels_per_position,
          default_pallet_capacity: wizardData.default_pallet_capacity,
          level_names: wizardData.level_names
        });
        
        setValidationResults(validation);
        return validation.valid;
      }
      
      if (currentStep === 2) {
        // Validate special areas
        const hasReceiving = wizardData.receiving_areas.length > 0;
        if (!hasReceiving) {
          throw new Error('At least one receiving area is required');
        }
        
        // Check for duplicate codes
        const allCodes = [
          ...wizardData.receiving_areas.map(a => a.code),
          ...wizardData.staging_areas.map(a => a.code),
          ...wizardData.dock_areas.map(a => a.code)
        ];
        const duplicates = allCodes.filter((code, index) => allCodes.indexOf(code) !== index);
        
        if (duplicates.length > 0) {
          throw new Error(`Duplicate area codes found: ${duplicates.join(', ')}`);
        }
        
        return true;
      }
      
      if (currentStep === 3) {
        // Generate preview
        const preview = await previewWarehouseSetup({
          ...wizardData,
          receiving_areas: wizardData.receiving_areas,
          staging_areas: wizardData.staging_areas,
          dock_areas: wizardData.dock_areas
        });
        
        setPreviewData(preview);
        return true;
      }
      
      return true;
    } catch (error: any) {
      console.error('Step validation failed:', error);
      return false;
    }
  };

  // Navigate to next step
  const handleNext = async () => {
    const isValid = await validateCurrentStep();
    if (isValid && currentStep < totalSteps) {
      setCurrentStep(currentStep + 1);
    }
  };

  // Navigate to previous step
  const handlePrevious = () => {
    if (currentStep > 1) {
      setCurrentStep(currentStep - 1);
      clearError();
    }
  };

  // Complete wizard
  const handleComplete = async () => {
    try {
      const setupData = {
        warehouse_id: warehouseId,
        configuration: {
          warehouse_name: wizardData.warehouse_name,
          num_aisles: wizardData.num_aisles,
          racks_per_aisle: wizardData.racks_per_aisle,
          positions_per_rack: wizardData.positions_per_rack,
          levels_per_position: wizardData.levels_per_position,
          level_names: wizardData.level_names,
          default_pallet_capacity: wizardData.default_pallet_capacity,
          bidimensional_racks: wizardData.bidimensional_racks,
          default_zone: wizardData.default_zone,
          position_numbering_split: wizardData.position_numbering_split
        },
        receiving_areas: wizardData.receiving_areas,
        staging_areas: wizardData.staging_areas,
        dock_areas: wizardData.dock_areas,
        generate_locations: wizardData.generate_locations,
        force_recreate: wizardData.force_recreate,
        create_template: wizardData.create_template,
        template_name: wizardData.template_name,
        template_description: wizardData.template_description,
        template_is_public: wizardData.template_is_public
      };

      const result = await setupWarehouse(setupData);
      onComplete(result.configuration);
    } catch (error) {
      console.error('Warehouse setup failed:', error);
    }
  };

  // Render current step content
  const renderStepContent = () => {
    switch (currentStep) {
      case 1:
        return (
          <Step1Structure
            data={wizardData}
            onChange={updateWizardData}
            validationResults={validationResults}
          />
        );
      case 2:
        return (
          <Step2SpecialAreas
            data={wizardData}
            onChange={updateWizardData}
          />
        );
      case 3:
        return (
          <Step3Preview
            data={wizardData}
            onChange={updateWizardData}
            previewData={previewData}
            validationResults={validationResults}
          />
        );
      default:
        return null;
    }
  };

  const getStepTitle = () => {
    switch (currentStep) {
      case 1:
        return 'Warehouse Structure';
      case 2:
        return 'Special Areas';
      case 3:
        return 'Review & Generate';
      default:
        return 'Setup';
    }
  };

  const getStepDescription = () => {
    switch (currentStep) {
      case 1:
        return 'Define your warehouse layout: aisles, racks, positions, and levels';
      case 2:
        return 'Configure receiving areas, staging zones, and dock locations';
      case 3:
        return 'Review your configuration and generate warehouse locations';
      default:
        return '';
    }
  };

  return (
    <Dialog open={true} onOpenChange={onClose}>
      <DialogContent className="max-w-5xl max-h-[90vh] overflow-y-auto">
        <DialogHeader>
          <DialogTitle className="flex items-center gap-2">
            <Building2 className="h-5 w-5" />
            {existingConfig ? 'Reconfigure Warehouse' : 'Warehouse Setup Wizard'}
          </DialogTitle>
          <DialogDescription>
            {existingConfig 
              ? 'Modify your existing warehouse configuration and regenerate locations'
              : 'Set up your warehouse structure and generate location codes automatically'
            }
          </DialogDescription>
        </DialogHeader>

        {/* Progress Bar */}
        <div className="space-y-4">
          <WizardProgress currentStep={currentStep} totalSteps={totalSteps} />
          
          <div className="text-center">
            <h3 className="text-lg font-semibold">{getStepTitle()}</h3>
            <p className="text-sm text-muted-foreground">{getStepDescription()}</p>
          </div>
        </div>

        {/* Error Alert */}
        {error && (
          <Alert variant="destructive">
            <AlertCircle className="h-4 w-4" />
            <AlertDescription>{error}</AlertDescription>
          </Alert>
        )}

        {/* Step Content */}
        <div className="min-h-[400px]">
          {renderStepContent()}
        </div>

        {/* Navigation Buttons */}
        <div className="flex justify-between items-center pt-6 border-t">
          <div>
            {currentStep > 1 && (
              <Button variant="outline" onClick={handlePrevious} disabled={loading}>
                <ChevronLeft className="h-4 w-4 mr-2" />
                Previous
              </Button>
            )}
          </div>

          <div className="flex gap-2">
            <Button variant="ghost" onClick={onClose}>
              Cancel
            </Button>
            
            {currentStep < totalSteps ? (
              <Button onClick={handleNext} disabled={loading}>
                {loading && <Loader2 className="h-4 w-4 mr-2 animate-spin" />}
                Next
                <ChevronRight className="h-4 w-4 ml-2" />
              </Button>
            ) : (
              <Button onClick={handleComplete} disabled={loading}>
                {loading ? (
                  <Loader2 className="h-4 w-4 mr-2 animate-spin" />
                ) : (
                  <CheckCircle className="h-4 w-4 mr-2" />
                )}
                {existingConfig ? 'Update Warehouse' : 'Create Warehouse'}
              </Button>
            )}
          </div>
        </div>
      </DialogContent>
    </Dialog>
  );
}