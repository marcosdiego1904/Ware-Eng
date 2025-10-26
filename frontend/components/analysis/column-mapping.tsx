"use client"

import { useState, useEffect, useCallback } from 'react'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Badge } from '@/components/ui/badge'
import { Alert, AlertDescription, AlertTitle } from '@/components/ui/alert'
import {
  ArrowRight,
  CheckCircle2,
  AlertCircle,
  FileSpreadsheet,
  Settings,
  Sparkles,
  ChevronDown,
  ChevronUp,
  Calendar,
  AlertTriangle,
  Loader2
} from 'lucide-react'
import * as XLSX from 'xlsx'
import { ConfidenceIndicator, ConfidenceBar } from './confidence-badge'
import { cn } from '@/lib/utils'

interface ColumnMappingProps {
  inventoryFile: File
  onMappingComplete: (mapping: Record<string, string>) => void
  onBack: () => void
  isUploading?: boolean  // NEW: Loading state during upload
}

// Required columns that need to be mapped
const REQUIRED_COLUMNS = [
  { key: 'pallet_id', label: 'Pallet ID', description: 'Unique identifier for each pallet' },
  { key: 'location', label: 'Location', description: 'Current warehouse location' },
  { key: 'description', label: 'Description', description: 'Product description or SKU' },
  { key: 'receipt_number', label: 'Receipt Number', description: 'Lot or receipt identifier' },
  { key: 'creation_date', label: 'Creation Date', description: 'Date when pallet was created' }
]

interface MatchSuggestion {
  matched_column: string | null
  confidence: number
  method: string | null
  alternatives: Array<{ column: string; confidence: number }>
}

interface DateFormatInfo {
  format_type: 'EXCEL_SERIAL' | 'ISO_FORMAT' | 'US_SLASH' | 'EU_SLASH' | 'UNIX_TIMESTAMP' | 'HUMAN_READABLE' | 'MIXED' | 'UNKNOWN'
  confidence: number  // 0.0-1.0
  sample_values: string[]
  unparseable_count: number
  total_count: number
  parsing_strategy: string
}

interface MappingSuggestions {
  suggestions: Record<string, MatchSuggestion>
  user_columns: string[]
  unmapped_required: string[]
  unmapped_user: string[]
  auto_mappable: Record<string, MatchSuggestion>
  requires_review: Record<string, MatchSuggestion>
  date_format_info?: DateFormatInfo | null  // NEW: Date format detection
  statistics: {
    total_required: number
    total_user_columns: number
    matched: number
    unmapped_required: number
    unmapped_user: number
    auto_mappable_count: number
    requires_review_count: number
  }
}

export function ColumnMapping({ inventoryFile, onMappingComplete, onBack, isUploading = false }: ColumnMappingProps) {
  const [userColumns, setUserColumns] = useState<string[]>([])
  const [mapping, setMapping] = useState<Record<string, string>>({})
  const [mappingSuggestions, setMappingSuggestions] = useState<MappingSuggestions | null>(null)
  const [isLoading, setIsLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [showAlternatives, setShowAlternatives] = useState<Record<string, boolean>>({})

  const loadFileColumns = useCallback(async () => {
    try {
      setIsLoading(true)
      setError(null)

      // Call the intelligent column mapping API
      const formData = new FormData()
      formData.append('file', inventoryFile)

      // Get auth token (using 'auth_token' key to match api.ts)
      const token = localStorage.getItem('auth_token')

      if (!token) {
        throw new Error('Authentication required. Please log in again.')
      }

      // Use environment variable for API URL (production-ready)
      const apiUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:5000/api/v1'
      const response = await fetch(`${apiUrl}/suggest-column-mapping`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`
        },
        body: formData
      })

      if (!response.ok) {
        const errorData = await response.json()
        throw new Error(errorData.message || 'Failed to analyze column mapping')
      }

      const result: MappingSuggestions = await response.json()

      console.log('[COLUMN_MAPPER] Received suggestions:', result)

      // Set user columns
      setUserColumns(result.user_columns)

      // Set mapping suggestions
      setMappingSuggestions(result)

      // Auto-apply high-confidence matches (>= 85%)
      const autoMapping: Record<string, string> = {}
      for (const [reqCol, suggestion] of Object.entries(result.auto_mappable)) {
        if (suggestion.matched_column) {
          autoMapping[reqCol] = suggestion.matched_column
        }
      }

      // Also include medium-confidence matches (for review)
      for (const [reqCol, suggestion] of Object.entries(result.requires_review)) {
        if (suggestion.matched_column && suggestion.confidence >= 0.65) {
          autoMapping[reqCol] = suggestion.matched_column
        }
      }

      console.log('[COLUMN_MAPPER] Auto-applied mappings:', autoMapping)
      console.log('[COLUMN_MAPPER] Statistics:', result.statistics)

      setMapping(autoMapping)

    } catch (err: any) {
      console.error('Failed to get column mapping suggestions:', err)
      setError(err.message || 'Failed to analyze Excel file. Please try again.')
    } finally {
      setIsLoading(false)
    }
  }, [inventoryFile])
  
  useEffect(() => {
    loadFileColumns()
  }, [loadFileColumns])

  const updateMapping = (requiredColumn: string, userColumn: string) => {
    setMapping(prev => ({
      ...prev,
      [requiredColumn]: userColumn
    }))
  }

  const toggleAlternatives = (column: string) => {
    setShowAlternatives(prev => ({
      ...prev,
      [column]: !prev[column]
    }))
  }

  const selectAlternative = (requiredColumn: string, alternativeColumn: string) => {
    updateMapping(requiredColumn, alternativeColumn)
    setShowAlternatives(prev => ({
      ...prev,
      [requiredColumn]: false
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
          <Sparkles className="w-6 h-6 text-blue-500 mx-auto mb-2 animate-pulse" />
          <p className="text-gray-700 font-medium">Analyzing your file...</p>
          <p className="text-sm text-gray-500 mt-1">Using intelligent column matching</p>
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
      {/* Smart Matching Summary Banner */}
      {mappingSuggestions && (
        <Card className="bg-gradient-to-r from-blue-50 to-purple-50 border-blue-200">
          <CardContent className="p-4">
            <div className="flex items-center gap-3">
              <Sparkles className="w-6 h-6 text-blue-600" />
              <div className="flex-1">
                <h3 className="font-medium text-gray-900">Intelligent Column Matching</h3>
                <p className="text-sm text-gray-600">
                  {mappingSuggestions.statistics.auto_mappable_count} high-confidence matches •{' '}
                  {mappingSuggestions.statistics.requires_review_count} require review •{' '}
                  {mappingSuggestions.statistics.unmapped_required} unmapped
                </p>
              </div>
              {mappingSuggestions.statistics.auto_mappable_count === mappingSuggestions.statistics.total_required && (
                <Badge className="bg-green-500 text-white">Perfect Match!</Badge>
              )}
            </div>
          </CardContent>
        </Card>
      )}

      {/* Date Format Detection Section */}
      {mappingSuggestions?.date_format_info && (
        <Card className="bg-gradient-to-r from-blue-50 to-indigo-50 border-blue-200">
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Calendar className="h-5 w-5 text-blue-600" />
              Date Format Detection
            </CardTitle>
          </CardHeader>
          <CardContent className="space-y-3">
            {/* Format Type Badge */}
            <div className="flex items-center gap-2">
              <span className="text-sm font-medium text-gray-700">Detected Format:</span>
              <Badge className={cn(
                "font-mono",
                mappingSuggestions.date_format_info.format_type === 'EXCEL_SERIAL' && "bg-purple-100 text-purple-800",
                mappingSuggestions.date_format_info.format_type === 'ISO_FORMAT' && "bg-green-100 text-green-800",
                mappingSuggestions.date_format_info.format_type === 'UNIX_TIMESTAMP' && "bg-blue-100 text-blue-800",
                mappingSuggestions.date_format_info.format_type === 'US_SLASH' && "bg-indigo-100 text-indigo-800",
                mappingSuggestions.date_format_info.format_type === 'EU_SLASH' && "bg-cyan-100 text-cyan-800",
                mappingSuggestions.date_format_info.format_type === 'MIXED' && "bg-yellow-100 text-yellow-800",
                mappingSuggestions.date_format_info.format_type === 'UNKNOWN' && "bg-gray-100 text-gray-800"
              )}>
                {mappingSuggestions.date_format_info.format_type.replace(/_/g, ' ')}
              </Badge>
              <ConfidenceIndicator
                confidence={mappingSuggestions.date_format_info.confidence * 100}
                showDetails={false}
              />
            </div>

            {/* Parsing Strategy */}
            <div className="flex items-center gap-2 text-sm">
              <span className="text-gray-600">Parsing Method:</span>
              <code className="px-2 py-1 bg-gray-100 rounded text-xs">
                {mappingSuggestions.date_format_info.parsing_strategy}
              </code>
            </div>

            {/* Sample Values */}
            <div>
              <p className="text-sm text-gray-600 mb-1">Sample values:</p>
              <div className="flex flex-wrap gap-2">
                {mappingSuggestions.date_format_info.sample_values.map((sample, idx) => (
                  <code key={idx} className="px-2 py-1 bg-white rounded border text-xs">
                    {sample}
                  </code>
                ))}
              </div>
            </div>

            {/* Warning for Unparseable Dates */}
            {mappingSuggestions.date_format_info.unparseable_count > 0 && (
              <Alert className="bg-yellow-50 border-yellow-200">
                <AlertTriangle className="h-4 w-4 text-yellow-600" />
                <AlertTitle className="text-yellow-800">Parsing Issues Detected</AlertTitle>
                <AlertDescription className="text-yellow-700">
                  {mappingSuggestions.date_format_info.unparseable_count} of {mappingSuggestions.date_format_info.total_count} dates could not be parsed automatically.
                  These pallets will be excluded from time-based rules (e.g., stagnant pallet detection).
                </AlertDescription>
              </Alert>
            )}

            {/* Success Message */}
            {mappingSuggestions.date_format_info.unparseable_count === 0 && (
              <div className="flex items-center gap-2 text-sm text-green-700">
                <CheckCircle2 className="h-4 w-4" />
                <span>All dates parsed successfully!</span>
              </div>
            )}
          </CardContent>
        </Card>
      )}

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

                    {mapping[key] && mappingSuggestions?.suggestions[key] && (
                      <div className="space-y-2">
                        {/* Confidence Indicator */}
                        <ConfidenceIndicator
                          confidence={mappingSuggestions.suggestions[key].confidence}
                          method={mappingSuggestions.suggestions[key].method || undefined}
                          showDetails={true}
                        />

                        {/* Confidence Bar */}
                        <ConfidenceBar confidence={mappingSuggestions.suggestions[key].confidence} />

                        {/* Alternatives Button */}
                        {mappingSuggestions.suggestions[key].alternatives.length > 0 && (
                          <div className="space-y-2">
                            <Button
                              variant="ghost"
                              size="sm"
                              onClick={() => toggleAlternatives(key)}
                              className="text-xs h-7 px-2"
                            >
                              {showAlternatives[key] ? (
                                <>
                                  <ChevronUp className="w-3 h-3 mr-1" />
                                  Hide alternatives
                                </>
                              ) : (
                                <>
                                  <ChevronDown className="w-3 h-3 mr-1" />
                                  Show {mappingSuggestions.suggestions[key].alternatives.length} alternatives
                                </>
                              )}
                            </Button>

                            {/* Alternatives List */}
                            {showAlternatives[key] && (
                              <div className="bg-gray-50 rounded-md p-3 space-y-2">
                                <p className="text-xs font-medium text-gray-700">Alternative matches:</p>
                                {mappingSuggestions.suggestions[key].alternatives.map((alt, idx) => (
                                  <button
                                    key={idx}
                                    onClick={() => selectAlternative(key, alt.column)}
                                    className="w-full flex items-center justify-between p-2 bg-white rounded border border-gray-200 hover:border-blue-400 hover:bg-blue-50 transition-colors text-left"
                                  >
                                    <span className="text-sm">{alt.column}</span>
                                    <Badge className="bg-gray-100 text-gray-700 text-xs">
                                      {Math.round(alt.confidence * 100)}%
                                    </Badge>
                                  </button>
                                ))}
                              </div>
                            )}
                          </div>
                        )}
                      </div>
                    )}

                    {mapping[key] && !mappingSuggestions?.suggestions[key] && (
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
          disabled={!isComplete() || isUploading}
          className="min-w-32"
        >
          {isUploading ? (
            <>
              <Loader2 className="w-4 h-4 mr-2 animate-spin" />
              Uploading...
            </>
          ) : (
            'Start Analysis'
          )}
        </Button>
      </div>
    </div>
  )
}