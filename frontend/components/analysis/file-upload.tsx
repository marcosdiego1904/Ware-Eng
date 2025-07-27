"use client"

import { useCallback } from 'react'
import { useDropzone } from 'react-dropzone'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Badge } from '@/components/ui/badge'
import { 
  Upload, 
  FileSpreadsheet, 
  X, 
  CheckCircle2, 
  AlertCircle,
  Download
} from 'lucide-react'

interface FileUploadProps {
  onFilesSelected: (files: { inventory: File | null; rules: File | null }) => void
  selectedFiles: { inventory: File | null; rules: File | null }
  allowRulesOptional?: boolean
}

export function FileUpload({ onFilesSelected, selectedFiles, allowRulesOptional = true }: FileUploadProps) {

  const onDropInventory = useCallback((acceptedFiles: File[]) => {
    if (acceptedFiles.length > 0) {
      const file = acceptedFiles[0]
      onFilesSelected({ ...selectedFiles, inventory: file })
    }
  }, [selectedFiles, onFilesSelected])

  const onDropRules = useCallback((acceptedFiles: File[]) => {
    if (acceptedFiles.length > 0) {
      const file = acceptedFiles[0]
      onFilesSelected({ ...selectedFiles, rules: file })
    }
  }, [selectedFiles, onFilesSelected])

  const {
    getRootProps: getInventoryRootProps,
    getInputProps: getInventoryInputProps,
    isDragActive: isInventoryDragActive
  } = useDropzone({
    onDrop: onDropInventory,
    accept: {
      'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet': ['.xlsx'],
      'application/vnd.ms-excel': ['.xls']
    },
    maxFiles: 1
  })

  const {
    getRootProps: getRulesRootProps,
    getInputProps: getRulesInputProps,
    isDragActive: isRulesDragActive
  } = useDropzone({
    onDrop: onDropRules,
    accept: {
      'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet': ['.xlsx'],
      'application/vnd.ms-excel': ['.xls']
    },
    maxFiles: 1
  })

  const removeFile = (type: 'inventory' | 'rules') => {
    onFilesSelected({
      ...selectedFiles,
      [type]: null
    })
  }

  const downloadSampleRules = () => {
    // This would download your sample warehouse_rules.xlsx file
    window.open('http://localhost:5001/download/warehouse_rules.xlsx', '_blank')
  }

  const downloadSampleInventory = () => {
    // This would download your sample inventory_report.xlsx file
    window.open('http://localhost:5001/download/inventory_report.xlsx', '_blank')
  }

  return (
    <div className="space-y-6">
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Inventory File Upload */}
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <FileSpreadsheet className="w-5 h-5" />
              Inventory Report
              <Badge variant="destructive" className="text-xs">Required</Badge>
            </CardTitle>
          </CardHeader>
          <CardContent>
            {selectedFiles.inventory ? (
              <div className="p-4 border rounded-lg bg-green-50 border-green-200">
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-2">
                    <CheckCircle2 className="w-5 h-5 text-green-600" />
                    <div>
                      <p className="font-medium text-green-800">{selectedFiles.inventory.name}</p>
                      <p className="text-xs text-green-600">
                        {(selectedFiles.inventory.size / 1024 / 1024).toFixed(2)} MB
                      </p>
                    </div>
                  </div>
                  <Button
                    variant="ghost"
                    size="sm"
                    onClick={() => removeFile('inventory')}
                  >
                    <X className="w-4 h-4" />
                  </Button>
                </div>
              </div>
            ) : (
              <div
                {...getInventoryRootProps()}
                className={`border-2 border-dashed rounded-lg p-6 text-center cursor-pointer transition-colors ${
                  isInventoryDragActive
                    ? 'border-blue-400 bg-blue-50'
                    : 'border-gray-300 hover:border-gray-400'
                }`}
              >
                <input {...getInventoryInputProps()} />
                <Upload className="w-8 h-8 text-gray-400 mx-auto mb-2" />
                <p className="text-sm text-gray-600 mb-2">
                  Drag & drop your inventory Excel file here, or click to browse
                </p>
                <p className="text-xs text-gray-500">Supports .xlsx and .xls files</p>
              </div>
            )}
            
            <div className="mt-3 flex items-center gap-2">
              <Button
                variant="outline"
                size="sm"
                onClick={downloadSampleInventory}
                className="gap-1"
              >
                <Download className="w-3 h-3" />
                Download Sample
              </Button>
            </div>
          </CardContent>
        </Card>

        {/* Rules File Upload */}
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <FileSpreadsheet className="w-5 h-5" />
              Warehouse Rules
              {allowRulesOptional && (
                <Badge variant="secondary" className="text-xs">Optional</Badge>
              )}
            </CardTitle>
          </CardHeader>
          <CardContent>
            {selectedFiles.rules ? (
              <div className="p-4 border rounded-lg bg-green-50 border-green-200">
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-2">
                    <CheckCircle2 className="w-5 h-5 text-green-600" />
                    <div>
                      <p className="font-medium text-green-800">{selectedFiles.rules.name}</p>
                      <p className="text-xs text-green-600">
                        {(selectedFiles.rules.size / 1024 / 1024).toFixed(2)} MB
                      </p>
                    </div>
                  </div>
                  <Button
                    variant="ghost"
                    size="sm"
                    onClick={() => removeFile('rules')}
                  >
                    <X className="w-4 h-4" />
                  </Button>
                </div>
              </div>
            ) : (
              <div
                {...getRulesRootProps()}
                className={`border-2 border-dashed rounded-lg p-6 text-center cursor-pointer transition-colors ${
                  isRulesDragActive
                    ? 'border-blue-400 bg-blue-50'
                    : 'border-gray-300 hover:border-gray-400'
                }`}
              >
                <input {...getRulesInputProps()} />
                <Upload className="w-8 h-8 text-gray-400 mx-auto mb-2" />
                <p className="text-sm text-gray-600 mb-2">
                  Drag & drop your rules Excel file here, or click to browse
                </p>
                <p className="text-xs text-gray-500">
                  {allowRulesOptional ? 'Will use default rules if not provided' : 'Required file'}
                </p>
              </div>
            )}
            
            <div className="mt-3 flex items-center gap-2">
              <Button
                variant="outline"
                size="sm"
                onClick={downloadSampleRules}
                className="gap-1"
              >
                <Download className="w-3 h-3" />
                Download Sample
              </Button>
            </div>
          </CardContent>
        </Card>
      </div>

      {/* File Validation Messages */}
      <div className="space-y-2">
        {!selectedFiles.inventory && (
          <div className="flex items-center gap-2 text-red-600">
            <AlertCircle className="w-4 h-4" />
            <span className="text-sm">Inventory report is required to proceed</span>
          </div>
        )}
        
        {selectedFiles.inventory && (
          <div className="flex items-center gap-2 text-green-600">
            <CheckCircle2 className="w-4 h-4" />
            <span className="text-sm">Ready to proceed with column mapping</span>
          </div>
        )}
      </div>
    </div>
  )
}