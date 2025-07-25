"use client"

import { useState, useEffect } from 'react'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Badge } from '@/components/ui/badge'
import { 
  ArrowRight, 
  CheckCircle2, 
  AlertCircle,
  FileSpreadsheet,
  Settings
} from 'lucide-react'
import * as XLSX from 'xlsx'

interface ColumnMappingProps {
  inventoryFile: File
  onMappingComplete: (mapping: Record<string, string>) => void
  onBack: () => void
}

// Required columns that need to be mapped
const REQUIRED_COLUMNS = [
  { key: 'pallet_id', label: 'Pallet ID', description: 'Unique identifier for each pallet' },
  { key: 'location', label: 'Location', description: 'Current warehouse location' },
  { key: 'description', label: 'Description', description: 'Product description or SKU' },
  { key: 'receipt_number', label: 'Receipt Number', description: 'Lot or receipt identifier' },
  { key: 'creation_date', label: 'Creation Date', description: 'Date when pallet was created' }
]

export function ColumnMapping({ inventoryFile, onMappingComplete, onBack }: ColumnMappingProps) {
  const [userColumns, setUserColumns] = useState<string[]>([])
  const [mapping, setMapping] = useState<Record<string, string>>({})
  const [isLoading, setIsLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    loadFileColumns()
  }, [inventoryFile])

  const loadFileColumns = async () => {
    try {
      setIsLoading(true)
      setError(null)

      const arrayBuffer = await inventoryFile.arrayBuffer()
      const workbook = XLSX.read(arrayBuffer, { type: 'array' })
      const firstSheetName = workbook.SheetNames[0]
      const worksheet = workbook.Sheets[firstSheetName]
      
      // Get the range of the worksheet
      const range = XLSX.utils.decode_range(worksheet['!ref'] || 'A1:A1')
      
      // Extract headers from the first row
      const headers: string[] = []
      for (let col = range.s.c; col <= range.e.c; col++) {
        const cellAddress = XLSX.utils.encode_cell({ r: 0, c: col })
        const cell = worksheet[cellAddress]
        if (cell && cell.v) {
          headers.push(String(cell.v).trim())
        }
      }

      setUserColumns(headers)
      
      // Auto-suggest mappings based on column names
      const autoMapping: Record<string, string> = {}
      REQUIRED_COLUMNS.forEach(({ key }) => {
        const suggestedColumn = findBestMatch(key, headers)
        if (suggestedColumn) {
          autoMapping[key] = suggestedColumn
        }
      })
      
      setMapping(autoMapping)
    } catch (err) {
      console.error('Failed to parse Excel file:', err)
      setError('Failed to read Excel file. Please ensure it\'s a valid .xlsx or .xls file.')
    } finally {
      setIsLoading(false)
    }
  }

  // Simple fuzzy matching for auto-suggestions
  const findBestMatch = (requiredCol: string, availableColumns: string[]): string | null => {
    const normalizedRequired = requiredCol.toLowerCase().replace(/_/g, ' ')
    
    // Exact match
    let exactMatch = availableColumns.find(col => 
      col.toLowerCase().replace(/[_\s]/g, '') === normalizedRequired.replace(/[_\s]/g, '')
    )
    if (exactMatch) return exactMatch

    // Partial match
    let partialMatch = availableColumns.find(col => 
      col.toLowerCase().includes(normalizedRequired) || 
      normalizedRequired.includes(col.toLowerCase())
    )
    if (partialMatch) return partialMatch

    // Keyword-based matching
    const keywords: Record<string, string[]> = {
      'pallet_id': ['pallet', 'id', 'identifier', 'palletid'],
      'location': ['location', 'loc', 'position', 'zone'],
      'description': ['description', 'desc', 'product', 'item', 'sku'],
      'receipt_number': ['receipt', 'lot', 'batch', 'order', 'number'],
      'creation_date': ['date', 'created', 'timestamp', 'time']
    }

    const relatedKeywords = keywords[requiredCol] || []
    for (const keyword of relatedKeywords) {
      const match = availableColumns.find(col => 
        col.toLowerCase().includes(keyword)
      )
      if (match) return match
    }

    return null
  }

  const updateMapping = (requiredColumn: string, userColumn: string) => {
    setMapping(prev => ({
      ...prev,
      [requiredColumn]: userColumn
    }))
  }

  const isComplete = () => {
    return REQUIRED_COLUMNS.every(({ key }) => mapping[key] && mapping[key] !== '')
  }

  const handleContinue = () => {
    if (isComplete()) {
      onMappingComplete(mapping)
    }
  }

  if (isLoading) {
    return (
      <Card>
        <CardContent className="p-8 text-center">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600 mx-auto mb-4"></div>
          <p className="text-gray-600">Reading Excel file columns...</p>
        </CardContent>
      </Card>
    )
  }

  if (error) {
    return (
      <Card>
        <CardContent className="p-8 text-center">
          <AlertCircle className="w-12 h-12 text-red-500 mx-auto mb-4" />
          <h3 className="text-lg font-medium mb-2">Error Reading File</h3>
          <p className="text-gray-600 mb-4">{error}</p>
          <Button onClick={onBack} variant="outline">
            Go Back
          </Button>
        </CardContent>
      </Card>
    )
  }

  return (
    <div className="space-y-6">
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Settings className="w-5 h-5" />
            Column Mapping
          </CardTitle>
          <p className="text-sm text-gray-600">
            Map your Excel columns to the required fields for analysis
          </p>
        </CardHeader>
        <CardContent>
          <div className="space-y-4">
            {REQUIRED_COLUMNS.map(({ key, label, description }) => (
              <div key={key} className="p-4 border rounded-lg">
                <div className="grid grid-cols-1 md:grid-cols-3 gap-4 items-center">
                  {/* Required Column */}
                  <div className="space-y-1">
                    <div className="flex items-center gap-2">
                      <span className="font-medium">{label}</span>
                      <Badge variant="secondary" className="text-xs">Required</Badge>
                    </div>
                    <p className="text-xs text-gray-500">{description}</p>
                  </div>

                  {/* Arrow */}
                  <div className="hidden md:flex justify-center">
                    <ArrowRight className="w-5 h-5 text-gray-400" />
                  </div>

                  {/* User Column Selection */}
                  <div className="space-y-2">
                    <select
                      value={mapping[key] || ''}
                      onChange={(e) => updateMapping(key, e.target.value)}
                      className="w-full p-2 border rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                    >
                      <option value="">Select a column...</option>
                      {userColumns.map((column) => (
                        <option key={column} value={column}>
                          {column}
                        </option>
                      ))}
                    </select>
                    
                    {mapping[key] && (
                      <div className="flex items-center gap-1 text-green-600">
                        <CheckCircle2 className="w-3 h-3" />
                        <span className="text-xs">Mapped to: {mapping[key]}</span>
                      </div>
                    )}
                  </div>
                </div>
              </div>
            ))}
          </div>
        </CardContent>
      </Card>

      {/* File Info */}
      <Card>
        <CardContent className="p-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-2">
              <FileSpreadsheet className="w-5 h-5 text-blue-600" />
              <div>
                <p className="font-medium">{inventoryFile.name}</p>
                <p className="text-sm text-gray-500">
                  {userColumns.length} columns detected
                </p>
              </div>
            </div>
            
            <div className="flex items-center gap-2">
              {isComplete() ? (
                <div className="flex items-center gap-2 text-green-600">
                  <CheckCircle2 className="w-5 h-5" />
                  <span className="text-sm font-medium">Ready to analyze</span>
                </div>
              ) : (
                <div className="flex items-center gap-2 text-orange-600">
                  <AlertCircle className="w-5 h-5" />
                  <span className="text-sm">
                    {REQUIRED_COLUMNS.length - Object.values(mapping).filter(Boolean).length} more required
                  </span>
                </div>
              )}
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Actions */}
      <div className="flex justify-between">
        <Button variant="outline" onClick={onBack}>
          Back to Files
        </Button>
        
        <Button 
          onClick={handleContinue}
          disabled={!isComplete()}
          className="min-w-32"
        >
          Start Analysis
        </Button>
      </div>
    </div>
  )
}