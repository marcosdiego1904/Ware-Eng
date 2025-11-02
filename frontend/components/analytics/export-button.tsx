"use client"

import { useState } from "react"
import { Button } from "@/components/ui/button"
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuLabel,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu"
import { Download, FileSpreadsheet, FileJson, Loader2 } from "lucide-react"
import { downloadExport, DashboardFilters } from "@/lib/pilot-analytics-api"
import { useToast } from "@/hooks/use-toast"

interface ExportButtonProps {
  filters?: DashboardFilters
  dataType?: 'sessions' | 'events' | 'uploads' | 'anomalies' | 'time_savings' | 'all'
  variant?: 'default' | 'outline' | 'secondary' | 'ghost'
  size?: 'default' | 'sm' | 'lg' | 'icon'
  className?: string
}

export function ExportButton({
  filters,
  dataType = 'all',
  variant = 'outline',
  size = 'default',
  className
}: ExportButtonProps) {
  const [isExporting, setIsExporting] = useState(false)
  const { toast } = useToast()

  const handleExport = async (format: 'csv' | 'json', type: typeof dataType) => {
    setIsExporting(true)

    try {
      await downloadExport(format, type, filters)

      toast({
        title: "Export successful",
        description: `Data exported as ${format.toUpperCase()} file.`,
      })
    } catch (error) {
      console.error('Export error:', error)
      toast({
        title: "Export failed",
        description: "Failed to export data. Please try again.",
        variant: "destructive"
      })
    } finally {
      setIsExporting(false)
    }
  }

  return (
    <DropdownMenu>
      <DropdownMenuTrigger asChild>
        <Button
          variant={variant}
          size={size}
          className={className}
          disabled={isExporting}
        >
          {isExporting ? (
            <>
              <Loader2 className="mr-2 h-4 w-4 animate-spin" />
              Exporting...
            </>
          ) : (
            <>
              <Download className="mr-2 h-4 w-4" />
              Export Data
            </>
          )}
        </Button>
      </DropdownMenuTrigger>

      <DropdownMenuContent align="end" className="w-56">
        <DropdownMenuLabel>Export Format</DropdownMenuLabel>
        <DropdownMenuSeparator />

        <DropdownMenuItem
          onClick={() => handleExport('csv', dataType)}
          disabled={isExporting}
        >
          <FileSpreadsheet className="mr-2 h-4 w-4" />
          <span>Export as CSV</span>
        </DropdownMenuItem>

        <DropdownMenuItem
          onClick={() => handleExport('json', dataType)}
          disabled={isExporting}
        >
          <FileJson className="mr-2 h-4 w-4" />
          <span>Export as JSON</span>
        </DropdownMenuItem>

        {dataType === 'all' && (
          <>
            <DropdownMenuSeparator />
            <DropdownMenuLabel>Export Specific Data</DropdownMenuLabel>

            <DropdownMenuItem
              onClick={() => handleExport('csv', 'sessions')}
              disabled={isExporting}
            >
              <FileSpreadsheet className="mr-2 h-4 w-4" />
              <span>Sessions Only</span>
            </DropdownMenuItem>

            <DropdownMenuItem
              onClick={() => handleExport('csv', 'events')}
              disabled={isExporting}
            >
              <FileSpreadsheet className="mr-2 h-4 w-4" />
              <span>Events Only</span>
            </DropdownMenuItem>

            <DropdownMenuItem
              onClick={() => handleExport('csv', 'anomalies')}
              disabled={isExporting}
            >
              <FileSpreadsheet className="mr-2 h-4 w-4" />
              <span>Anomalies Only</span>
            </DropdownMenuItem>

            <DropdownMenuItem
              onClick={() => handleExport('csv', 'time_savings')}
              disabled={isExporting}
            >
              <FileSpreadsheet className="mr-2 h-4 w-4" />
              <span>Time Savings Only</span>
            </DropdownMenuItem>
          </>
        )}
      </DropdownMenuContent>
    </DropdownMenu>
  )
}

// Simpler version with just icon button
interface ExportIconButtonProps {
  filters?: DashboardFilters
  dataType?: 'sessions' | 'events' | 'uploads' | 'anomalies' | 'time_savings' | 'all'
  format?: 'csv' | 'json'
}

export function ExportIconButton({
  filters,
  dataType = 'all',
  format = 'csv'
}: ExportIconButtonProps) {
  const [isExporting, setIsExporting] = useState(false)
  const { toast } = useToast()

  const handleExport = async () => {
    setIsExporting(true)

    try {
      await downloadExport(format, dataType, filters)

      toast({
        title: "Export successful",
        description: `Data exported as ${format.toUpperCase()} file.`,
      })
    } catch (error) {
      console.error('Export error:', error)
      toast({
        title: "Export failed",
        description: "Failed to export data. Please try again.",
        variant: "destructive"
      })
    } finally {
      setIsExporting(false)
    }
  }

  return (
    <Button
      variant="outline"
      size="icon"
      onClick={handleExport}
      disabled={isExporting}
      title={`Export as ${format.toUpperCase()}`}
    >
      {isExporting ? (
        <Loader2 className="h-4 w-4 animate-spin" />
      ) : (
        <Download className="h-4 w-4" />
      )}
    </Button>
  )
}
