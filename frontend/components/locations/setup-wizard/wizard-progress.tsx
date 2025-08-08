'use client';

import React from 'react';
import { Progress } from '@/components/ui/progress';
import { Badge } from '@/components/ui/badge';
import { cn } from '@/lib/utils';
import { 
  Building2, 
  MapPin, 
  CheckCircle, 
  Circle,
  Clock
} from 'lucide-react';

interface WizardProgressProps {
  currentStep: number;
  totalSteps: number;
}

export function WizardProgress({ currentStep, totalSteps }: WizardProgressProps) {
  const progressPercentage = (currentStep / totalSteps) * 100;

  const steps = [
    {
      number: 1,
      title: 'Structure',
      description: 'Warehouse layout',
      icon: Building2
    },
    {
      number: 2,
      title: 'Special Areas',
      description: 'Receiving & staging',
      icon: MapPin
    },
    {
      number: 3,
      title: 'Generate',
      description: 'Review & create',
      icon: CheckCircle
    }
  ];

  const getStepStatus = (stepNumber: number) => {
    if (stepNumber < currentStep) return 'completed';
    if (stepNumber === currentStep) return 'current';
    return 'upcoming';
  };

  const getStepIcon = (step: any, status: string) => {
    const IconComponent = step.icon;
    
    if (status === 'completed') {
      return <CheckCircle className="h-5 w-5 text-green-600" />;
    }
    
    if (status === 'current') {
      return <Clock className="h-5 w-5 text-blue-600" />;
    }
    
    return <Circle className="h-5 w-5 text-gray-400" />;
  };

  return (
    <div className="space-y-4">
      {/* Progress Bar */}
      <div className="space-y-2">
        <div className="flex justify-between text-sm text-muted-foreground">
          <span>Step {currentStep} of {totalSteps}</span>
          <span>{Math.round(progressPercentage)}% complete</span>
        </div>
        <Progress value={progressPercentage} className="h-2" />
      </div>

      {/* Step Indicators */}
      <div className="flex justify-between items-center">
        {steps.map((step, index) => {
          const status = getStepStatus(step.number);
          const isLast = index === steps.length - 1;
          
          return (
            <div key={step.number} className="flex items-center flex-1">
              {/* Step Circle */}
              <div className="flex flex-col items-center">
                <div
                  className={cn(
                    "flex items-center justify-center w-10 h-10 rounded-full border-2 transition-colors",
                    status === 'completed' && "bg-green-50 border-green-200",
                    status === 'current' && "bg-blue-50 border-blue-200",
                    status === 'upcoming' && "bg-gray-50 border-gray-200"
                  )}
                >
                  {getStepIcon(step, status)}
                </div>
                
                {/* Step Info */}
                <div className="mt-2 text-center">
                  <div
                    className={cn(
                      "text-sm font-medium",
                      status === 'completed' && "text-green-700",
                      status === 'current' && "text-blue-700",
                      status === 'upcoming' && "text-gray-500"
                    )}
                  >
                    {step.title}
                  </div>
                  <div className="text-xs text-muted-foreground mt-1">
                    {step.description}
                  </div>
                </div>
              </div>

              {/* Connector Line */}
              {!isLast && (
                <div className="flex-1 h-px mx-4 mt-5">
                  <div
                    className={cn(
                      "h-full transition-colors",
                      status === 'completed' ? "bg-green-200" : "bg-gray-200"
                    )}
                  />
                </div>
              )}
            </div>
          );
        })}
      </div>

      {/* Current Step Badge */}
      <div className="text-center">
        <Badge 
          variant={currentStep === totalSteps ? "default" : "secondary"}
          className="px-3 py-1"
        >
          {currentStep === totalSteps ? 'Ready to Generate' : `Step ${currentStep}: ${steps[currentStep - 1]?.title}`}
        </Badge>
      </div>
    </div>
  );
}