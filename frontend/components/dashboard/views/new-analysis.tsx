"use client"

import { useState } from 'react'
import { useRouter } from 'next/navigation'
import { FileUpload } from '@/components/analysis/file-upload'
import { ColumnMapping } from '@/components/analysis/column-mapping'
import { ProcessingStatus } from '@/components/analysis/processing-status'
import { reportsApi } from '@/lib/reports'
import { useDashboardStore } from '@/lib/store'

type AnalysisStep = 'upload' | 'mapping' | 'processing' | 'complete'

export function NewAnalysisView() {
  const [currentStep, setCurrentStep] = useState<AnalysisStep>('upload')
  const [selectedFiles, setSelectedFiles] = useState<{ inventory: File | null; rules: File | null }>({
    inventory: null,
    rules: null
  })
  const [columnMapping, setColumnMapping] = useState<Record<string, string>>({})
  const [error, setError] = useState<string | null>(null)
  const [isSubmitting, setIsSubmitting] = useState(false)
  const { setCurrentView } = useDashboardStore()
  const router = useRouter()

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
    setColumnMapping(mapping)
    setCurrentStep('processing')
    setIsSubmitting(true)

    try {
      console.log('Starting analysis with:', {
        inventory_file: selectedFiles.inventory?.name,
        rules_file: selectedFiles.rules?.name,
        column_mapping: mapping
      })

      // Submit to backend API
      const response = await reportsApi.createReport({
        inventory_file: selectedFiles.inventory!,
        rules_file: selectedFiles.rules || undefined,
        column_mapping: mapping
      })

      console.log('Analysis response:', response)

      // Simulate processing time (the real API call handles this)
      setTimeout(() => {
        handleProcessingComplete(response.report_id)
      }, 5000) // 5 second delay to show the processing animation

    } catch (err: any) {
      console.error('Analysis failed:', err)
      console.error('Error details:', {
        status: err.response?.status,
        data: err.response?.data,
        message: err.message
      })
      setError(err.response?.data?.message || `Analysis failed: ${err.message}`)
      setCurrentStep('mapping')
      setIsSubmitting(false)
    }
  }

  const handleProcessingComplete = (reportId: number) => {
    setIsSubmitting(false)
    // Redirect to the reports view to show the new report
    setCurrentView('reports')
    // Or you could navigate to a specific report view
    // router.push(`/report/${reportId}`)
  }

  const handleProcessingError = (errorMessage: string) => {
    setError(errorMessage)
    setCurrentStep('mapping')
    setIsSubmitting(false)
  }

  const handleBackToFiles = () => {
    setCurrentStep('upload')
    setColumnMapping({})
    setError(null)
  }

  const handleStartOver = () => {
    setCurrentStep('upload')
    setSelectedFiles({ inventory: null, rules: null })
    setColumnMapping({})
    setError(null)
  }

  return (
    <div className="p-6 max-w-6xl mx-auto">
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