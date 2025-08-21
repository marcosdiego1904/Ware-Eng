"use client"

import { useState } from 'react'
import { FileUpload } from '@/components/analysis/file-upload'
import { ColumnMapping } from '@/components/analysis/column-mapping'
import { ProcessingStatus } from '@/components/analysis/processing-status'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { Building2 } from 'lucide-react'
import { reportsApi } from '@/lib/reports'
import { useDashboardStore } from '@/lib/store'
import useLocationStore from '@/lib/location-store'

type AnalysisStep = 'upload' | 'mapping' | 'processing' | 'complete'

export function NewAnalysisView() {
  const [currentStep, setCurrentStep] = useState<AnalysisStep>('upload')
  const [selectedFiles, setSelectedFiles] = useState<{ inventory: File | null; rules: File | null }>({
    inventory: null,
    rules: null
  })
  const [error, setError] = useState<string | null>(null)
  const { setCurrentView } = useDashboardStore()
  
  // NEW: Get current warehouse configuration from applied template
  const { currentWarehouseConfig } = useLocationStore()

  const handleFilesSelected = (files: { inventory: File | null; rules: File | null }) => {
    setSelectedFiles(files)
    setError(null)
  }

  const handleProceedToMapping = () => {
    if (selectedFiles.inventory) {
      setCurrentStep('mapping')
    }
  }

  const handleMappingComplete = async (mapping: Record<string, string>) => {
    setCurrentStep('processing')

    try {
      // NEW: Include warehouse_id from applied template
      const warehouseId = currentWarehouseConfig?.warehouse_id
      
      console.log('Starting analysis with:', {
        inventory_file: selectedFiles.inventory?.name,
        rules_file: selectedFiles.rules?.name,
        column_mapping: mapping,
        warehouse_id: warehouseId  // NEW: Show warehouse context
      })

      // Submit to backend API
      const response = await reportsApi.createReport({
        inventory_file: selectedFiles.inventory!,
        rules_file: selectedFiles.rules || undefined,
        column_mapping: mapping,
        warehouse_id: warehouseId  // NEW: Pass warehouse context from applied template
      })

      console.log('Analysis response:', response)

      // Simulate processing time (the real API call handles this)
      setTimeout(() => {
        handleProcessingComplete()
      }, 5000) // 5 second delay to show the processing animation

    } catch (err: unknown) {
      const error = err as { response?: { status?: number; data?: { message?: string } }; message?: string }
      console.error('Analysis failed:', err)
      console.error('Error details:', {
        status: error.response?.status,
        data: error.response?.data,
        message: error.message
      })
      setError(error.response?.data?.message || `Analysis failed: ${error.message}`)
      setCurrentStep('mapping')
    }
  }

  const handleProcessingComplete = () => {
    // Redirect to the reports view to show the new report
    setCurrentView('reports')
    // Or you could navigate to a specific report view
    // router.push(`/report/${reportId}`)
  }

  const handleProcessingError = (errorMessage: string) => {
    setError(errorMessage)
    setCurrentStep('mapping')
  }

  const handleBackToFiles = () => {
    setCurrentStep('upload')
    setError(null)
  }

  const handleStartOver = () => {
    setCurrentStep('upload')
    setSelectedFiles({ inventory: null, rules: null })
    setError(null)
  }

  return (
    <div className="p-6 max-w-6xl mx-auto">
      {/* NEW: Warehouse Context Display */}
      {currentWarehouseConfig && (
        <Card className="mb-6 border-blue-200 bg-blue-50">
          <CardHeader className="pb-3">
            <CardTitle className="flex items-center gap-2 text-blue-700">
              <Building2 className="h-5 w-5" />
              Analysis Warehouse Configuration
            </CardTitle>
            <CardDescription className="text-blue-600">
              Analysis will use the currently applied warehouse template
            </CardDescription>
          </CardHeader>
          <CardContent className="pt-0">
            <div className="flex items-center gap-3">
              <Badge variant="secondary" className="bg-blue-100 text-blue-700">
                {currentWarehouseConfig.warehouse_name}
              </Badge>
              <span className="text-sm text-gray-600">
                ID: {currentWarehouseConfig.warehouse_id}
              </span>
              <span className="text-sm text-gray-600">
                • {currentWarehouseConfig.total_storage_locations?.toLocaleString() || 'N/A'} locations
              </span>
            </div>
          </CardContent>
        </Card>
      )}
      
      {/* Progress Steps */}
      <div className="mb-8">
        <div className="flex items-center justify-between">
          {[
            { key: 'upload', label: 'Upload Files', step: 1 },
            { key: 'mapping', label: 'Column Mapping', step: 2 },
            { key: 'processing', label: 'Processing', step: 3 }
          ].map(({ key, label, step }, index) => (
            <div key={key} className="flex items-center">
              <div className={`flex items-center justify-center w-8 h-8 rounded-full border-2 ${
                currentStep === key
                  ? 'border-blue-500 bg-blue-500 text-white'
                  : index < ['upload', 'mapping', 'processing'].indexOf(currentStep)
                  ? 'border-green-500 bg-green-500 text-white'
                  : 'border-gray-300 text-gray-400'
              }`}>
                {index < ['upload', 'mapping', 'processing'].indexOf(currentStep) ? '✓' : step}
              </div>
              <span className={`ml-2 text-sm font-medium ${
                currentStep === key ? 'text-blue-600' : 'text-gray-500'
              }`}>
                {label}
              </span>
              {index < 2 && (
                <div className={`mx-4 h-0.5 w-16 ${
                  index < ['upload', 'mapping', 'processing'].indexOf(currentStep)
                    ? 'bg-green-500'
                    : 'bg-gray-300'
                }`} />
              )}
            </div>
          ))}
        </div>
      </div>

      {/* Error Display */}
      {error && (
        <div className="mb-6 p-4 bg-red-50 border border-red-200 rounded-lg">
          <p className="text-red-800 font-medium">Analysis Failed</p>
          <p className="text-red-600 text-sm mt-1">{error}</p>
        </div>
      )}

      {/* Step Content */}
      {currentStep === 'upload' && (
        <div className="space-y-6">
          <FileUpload
            onFilesSelected={handleFilesSelected}
            selectedFiles={selectedFiles}
          />
          
          {selectedFiles.inventory && (
            <div className="flex justify-end">
              <button
                onClick={handleProceedToMapping}
                className="px-6 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
              >
                Continue to Mapping
              </button>
            </div>
          )}
        </div>
      )}

      {currentStep === 'mapping' && selectedFiles.inventory && (
        <ColumnMapping
          inventoryFile={selectedFiles.inventory}
          onMappingComplete={handleMappingComplete}
          onBack={handleBackToFiles}
        />
      )}

      {currentStep === 'processing' && (
        <ProcessingStatus
          onComplete={handleProcessingComplete}
          onError={handleProcessingError}
          onBack={handleStartOver}
        />
      )}
    </div>
  )
}