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
import { userPreferencesApi } from '@/lib/api'
import { ClearAnomaliesModal } from '@/components/ui/clear-anomalies-modal'

type AnalysisStep = 'upload' | 'mapping' | 'processing' | 'complete'

export function NewAnalysisView() {
  const [currentStep, setCurrentStep] = useState<AnalysisStep>('upload')
  const [selectedFiles, setSelectedFiles] = useState<{ inventory: File | null; rules: File | null }>({
    inventory: null,
    rules: null
  })
  const [error, setError] = useState<string | null>(null)
  const [isUploading, setIsUploading] = useState(false)  // NEW: Track upload state
  const { setCurrentView } = useDashboardStore()

  // NEW: Get current warehouse configuration from applied template
  const { currentWarehouseConfig } = useLocationStore()

  // Clear Anomalies Modal State
  const [clearAnomaliesModal, setClearAnomaliesModal] = useState({
    open: false,
    anomaliesCount: 0,
    isLoading: false,
    pendingMapping: null as Record<string, string> | null
  })

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
    try {
      // Check user preferences and previous anomalies count
      const preferences = await userPreferencesApi.getPreferences()

      if (preferences.success &&
          preferences.preferences.show_clear_warning &&
          preferences.unresolved_anomaly_count > 0) {

        // Show clear anomalies modal
        setClearAnomaliesModal({
          open: true,
          anomaliesCount: preferences.unresolved_anomaly_count,
          isLoading: false,
          pendingMapping: mapping
        })

        console.log(`Found ${preferences.unresolved_anomaly_count} previous anomalies, showing modal`)
        return // Wait for user decision
      }

      // No previous anomalies or user doesn't want to see warning - proceed directly
      await submitAnalysis(mapping, false) // false = don't clear (no anomalies to clear)

    } catch (error) {
      console.error('Failed to check preferences:', error)
      // If preferences check fails, proceed without clearing
      await submitAnalysis(mapping, false)
    }
  }

  const submitAnalysis = async (mapping: Record<string, string>, clearPrevious: boolean = false) => {
    setClearAnomaliesModal(prev => ({ ...prev, open: false }))
    setIsUploading(true)  // Show loading state
    setError(null)  // Clear any previous errors

    try {
      // NEW: Include warehouse_id from applied template
      const warehouseId = currentWarehouseConfig?.warehouse_id

      console.log('Starting analysis with:', {
        inventory_file: selectedFiles.inventory?.name,
        rules_file: selectedFiles.rules?.name,
        column_mapping: mapping,
        warehouse_id: warehouseId,
        clear_previous: clearPrevious
      })

      // Submit to backend API (this waits for the response)
      console.log('⏱️ Uploading files and waiting for response...')
      const response = await reportsApi.createReport({
        inventory_file: selectedFiles.inventory!,
        rules_file: selectedFiles.rules || undefined,
        column_mapping: mapping,
        warehouse_id: warehouseId,
        clear_previous: clearPrevious  // CLEAR ANOMALIES: Pass user decision
      })

      console.log('✅ Upload complete! Analysis response:', response)

      // Store the pending report ID so overview can show processing UI
      const reportId = response.report_id
      console.log(`📝 Setting pending report ID: ${reportId}`)
      const { setPendingReportId } = useDashboardStore.getState()
      setPendingReportId(reportId)

      // Navigate immediately to overview (which will show processing UI)
      console.log('🚀 Navigating to overview to show processing state...')
      setIsUploading(false)  // Stop loading before navigation
      handleProcessingComplete()

    } catch (err: unknown) {
      console.error('Analysis failed:', err)

      // Enhanced error handling with better type checking
      let errorMessage = 'Analysis failed. Please try again.'

      if (err && typeof err === 'object') {
        const error = err as {
          response?: {
            status?: number;
            statusText?: string;
            data?: { message?: string; error?: string }
          };
          message?: string;
          details?: { userMessage?: string }
        }

        // Log detailed error information
        console.error('Error details:', {
          status: error.response?.status || 'N/A',
          statusText: error.response?.statusText || 'N/A',
          data: error.response?.data || null,
          message: error.message || 'N/A'
        })

        // Extract the best error message available
        errorMessage = error.details?.userMessage ||
                      error.response?.data?.message ||
                      error.response?.data?.error ||
                      error.message ||
                      'Analysis failed. Please check your files and try again.'
      } else {
        console.error('Unexpected error type:', typeof err, err)
      }

      setError(errorMessage)
      setIsUploading(false)  // Stop loading on error
      setCurrentStep('mapping')
    }
  }

  const handleProcessingComplete = () => {
    console.log('🎯 handleProcessingComplete called')

    // Trigger overview refresh to fetch new analysis data
    const { triggerOverviewRefresh } = useDashboardStore.getState()
    console.log('📡 Triggering overview refresh...')
    triggerOverviewRefresh()
    console.log('✅ Overview refresh triggered')

    // Small delay to ensure Zustand state update propagates before navigation
    // This prevents race condition where overview mounts before seeing the timestamp change
    console.log('⏱️ Starting 100ms delay before navigation to overview...')
    setTimeout(() => {
      console.log('🚀 Navigating to overview view')
      setCurrentView('overview')
    }, 100)
  }

  // Clear Anomalies Modal Handlers
  const handleClearAnomaliesConfirm = async (dontShowAgain: boolean) => {
    if (dontShowAgain) {
      // Update user preference to not show warning again
      try {
        await userPreferencesApi.updatePreferences({
          show_clear_warning: false
        })
        console.log('Updated user preference: show_clear_warning = false')
      } catch (error) {
        console.error('Failed to update user preference:', error)
      }
    }

    // Proceed with analysis and clear previous anomalies
    if (clearAnomaliesModal.pendingMapping) {
      await submitAnalysis(clearAnomaliesModal.pendingMapping, true) // true = clear previous
    }
  }

  const handleClearAnomaliesCancel = () => {
    // Cancel the analysis completely, go back to mapping step
    setClearAnomaliesModal(prev => ({ ...prev, open: false, pendingMapping: null }))
    console.log('User cancelled clear anomalies modal')
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
      
      {/* Progress Steps - Brand Aligned */}
      <div className="mb-8">
        <div className="flex items-center justify-between">
          {[
            { key: 'upload', label: 'Import Inventory', step: 1 },
            { key: 'mapping', label: 'Map Columns', step: 2 },
            { key: 'processing', label: 'Run Analysis', step: 3 }
          ].map(({ key, label, step }, index) => (
            <div key={key} className="flex items-center">
              <div className={`flex items-center justify-center w-8 h-8 rounded-full border-2 ${
                currentStep === key
                  ? 'border-orange-500 bg-orange-500 text-white'
                  : index < ['upload', 'mapping', 'processing'].indexOf(currentStep)
                  ? 'border-green-600 bg-green-600 text-white'
                  : 'border-slate-300 text-slate-400'
              }`}>
                {index < ['upload', 'mapping', 'processing'].indexOf(currentStep) ? '✓' : step}
              </div>
              <span className={`ml-2 text-sm font-medium ${
                currentStep === key ? 'text-orange-600' : 'text-slate-600'
              }`}>
                {label}
              </span>
              {index < 2 && (
                <div className={`mx-4 h-0.5 w-16 ${
                  index < ['upload', 'mapping', 'processing'].indexOf(currentStep)
                    ? 'bg-green-600'
                    : 'bg-slate-300'
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
          isUploading={isUploading}
        />
      )}

      {currentStep === 'processing' && (
        <ProcessingStatus
          onComplete={handleProcessingComplete}
          onError={handleProcessingError}
          onBack={handleStartOver}
        />
      )}

      {/* Clear Anomalies Modal */}
      <ClearAnomaliesModal
        open={clearAnomaliesModal.open}
        onOpenChange={(open) => setClearAnomaliesModal(prev => ({ ...prev, open }))}
        anomaliesCount={clearAnomaliesModal.anomaliesCount}
        isLoading={clearAnomaliesModal.isLoading}
        onConfirm={handleClearAnomaliesConfirm}
        onCancel={handleClearAnomaliesCancel}
      />
    </div>
  )
}