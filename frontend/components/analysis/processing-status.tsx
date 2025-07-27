"use client"

import { useEffect, useState } from 'react'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Progress } from '@/components/ui/progress'
import { 
  CheckCircle2, 
  Loader2,
  BarChart3
} from 'lucide-react'

interface ProcessingStatusProps {
  onComplete: (reportId: number) => void
  onError: (error: string) => void
  onBack: () => void
}

export function ProcessingStatus({ onComplete, onBack }: ProcessingStatusProps) {
  const [currentStep, setCurrentStep] = useState(0)
  const [progress, setProgress] = useState(0)
  const [isProcessing, setIsProcessing] = useState(true)

  const steps = [
    { id: 1, label: 'Uploading files', description: 'Sending files to server' },
    { id: 2, label: 'Processing inventory', description: 'Reading and validating data' },
    { id: 3, label: 'Running detection algorithms', description: 'Analyzing warehouse anomalies' },
    { id: 4, label: 'Generating report', description: 'Creating analysis results' },
    { id: 5, label: 'Complete', description: 'Analysis finished successfully' }
  ]

  useEffect(() => {
    // Simulate processing steps
    const progressInterval = setInterval(() => {
      setProgress(prev => {
        const newProgress = prev + 2
        if (newProgress >= 100) {
          clearInterval(progressInterval)
          setIsProcessing(false)
          setCurrentStep(5)
          // Simulate successful completion with a report ID
          setTimeout(() => {
            onComplete(Math.floor(Math.random() * 1000) + 1)
          }, 500)
          return 100
        }
        
        // Update current step based on progress
        const stepProgress = Math.floor(newProgress / 20)
        setCurrentStep(Math.min(stepProgress, 4))
        
        return newProgress
      })
    }, 100)

    return () => clearInterval(progressInterval)
  }, [onComplete])

  return (
    <div className="space-y-6">
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            {isProcessing ? (
              <Loader2 className="w-5 h-5 animate-spin" />
            ) : (
              <CheckCircle2 className="w-5 h-5 text-green-600" />
            )}
            {isProcessing ? 'Processing Analysis...' : 'Analysis Complete!'}
          </CardTitle>
          <p className="text-sm text-gray-600">
            {isProcessing 
              ? 'Please wait while we analyze your warehouse data'
              : 'Your warehouse analysis has been completed successfully'
            }
          </p>
        </CardHeader>
        <CardContent className="space-y-6">
          {/* Progress Bar */}
          <div className="space-y-2">
            <div className="flex justify-between text-sm">
              <span>Overall Progress</span>
              <span>{progress.toFixed(0)}%</span>
            </div>
            <Progress value={progress} className="h-2" />
          </div>

          {/* Steps */}
          <div className="space-y-3">
            {steps.map((step, index) => (
              <div
                key={step.id}
                className={`flex items-center gap-3 p-3 rounded-lg transition-colors ${
                  index < currentStep
                    ? 'bg-green-50 border border-green-200'
                    : index === currentStep && isProcessing
                    ? 'bg-blue-50 border border-blue-200'
                    : index === currentStep && !isProcessing
                    ? 'bg-green-50 border border-green-200'
                    : 'bg-gray-50 border border-gray-200'
                }`}
              >
                {/* Step Icon */}
                <div className="flex-shrink-0">
                  {index < currentStep || (!isProcessing && index === currentStep) ? (
                    <CheckCircle2 className="w-5 h-5 text-green-600" />
                  ) : index === currentStep && isProcessing ? (
                    <Loader2 className="w-5 h-5 text-blue-600 animate-spin" />
                  ) : (
                    <div className="w-5 h-5 rounded-full border-2 border-gray-300"></div>
                  )}
                </div>

                {/* Step Content */}
                <div className="flex-1">
                  <p className={`font-medium ${
                    index <= currentStep ? 'text-gray-900' : 'text-gray-500'
                  }`}>
                    {step.label}
                  </p>
                  <p className={`text-sm ${
                    index <= currentStep ? 'text-gray-600' : 'text-gray-400'
                  }`}>
                    {step.description}
                  </p>
                </div>
              </div>
            ))}
          </div>

          {/* Algorithm Info */}
          {currentStep >= 2 && (
            <Card className="bg-blue-50 border-blue-200">
              <CardContent className="p-4">
                <h4 className="font-medium text-blue-900 mb-2">Detection Algorithms Running:</h4>
                <ul className="text-sm text-blue-800 space-y-1">
                  <li>• Floating Pallets Detection</li>
                  <li>• Lot Stragglers Analysis</li>
                  <li>• Stuck in Transit Detection</li>
                  <li>• Incompatibility & Overcapacity Check</li>
                  <li>• Unknown Locations Identification</li>
                  <li>• Missing Locations Detection</li>
                </ul>
              </CardContent>
            </Card>
          )}

          {/* Completion Message */}
          {!isProcessing && (
            <Card className="bg-green-50 border-green-200">
              <CardContent className="p-4 text-center">
                <CheckCircle2 className="w-12 h-12 text-green-600 mx-auto mb-3" />
                <h3 className="text-lg font-medium text-green-900 mb-1">
                  Analysis Complete!
                </h3>
                <p className="text-sm text-green-700">
                  Your warehouse intelligence report is ready to view.
                </p>
              </CardContent>
            </Card>
          )}

          {/* Action Buttons */}
          <div className="flex justify-between pt-4">
            <Button 
              variant="outline" 
              onClick={onBack}
              disabled={isProcessing}
            >
              Back to Start
            </Button>
            
            {!isProcessing && (
              <Button className="gap-2">
                <BarChart3 className="w-4 h-4" />
                View Report
              </Button>
            )}
          </div>
        </CardContent>
      </Card>
    </div>
  )
}