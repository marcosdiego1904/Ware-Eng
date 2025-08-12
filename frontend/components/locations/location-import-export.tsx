'use client';

import React, { useState, useRef, useEffect } from 'react';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Alert, AlertDescription } from '@/components/ui/alert';
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from '@/components/ui/dialog';
import { Progress } from '@/components/ui/progress';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Separator } from '@/components/ui/separator';
import useLocationStore from '@/lib/location-store';
import { locationApi } from '@/lib/location-api';
import { 
  Download, 
  Upload, 
  FileText, 
  AlertCircle, 
  CheckCircle,
  Loader2,
  X
} from 'lucide-react';

interface CsvRow {
  code: string;
  location_type: string;
  zone: string;
  capacity: number;
  pallet_capacity: number;
  aisle_number?: number;
  rack_number?: number;
  position_number?: number;
  level?: string;
  allowed_products: string[];
  special_requirements: Record<string, unknown>;
  is_active: boolean;
  warehouse_id: string;
}

interface LocationImportExportProps {
  warehouseId: string;
  onImportComplete?: (result: { created_count: number; errors: string[] }) => void;
}

export function LocationImportExport({ warehouseId, onImportComplete }: LocationImportExportProps) {
  const { locations, fetchLocations } = useLocationStore();
  const fileInputRef = useRef<HTMLInputElement>(null);
  const isMountedRef = useRef(true);
  
  // Export states
  const [exporting, setExporting] = useState(false);
  const [exportFormat, setExportFormat] = useState<'json' | 'csv'>('csv');
  
  // Import states
  const [importing, setImporting] = useState(false);
  const [importFile, setImportFile] = useState<File | null>(null);
  const [importProgress, setImportProgress] = useState(0);
  const [importResult, setImportResult] = useState<{
    created_count: number;
    errors: string[];
  } | null>(null);
  const [showImportDialog, setShowImportDialog] = useState(false);

  // Cleanup on unmount
  useEffect(() => {
    return () => {
      isMountedRef.current = false;
    };
  }, []);

  // Handle export
  const handleExport = async () => {
    setExporting(true);
    try {
      const data = await locationApi.exportLocations(warehouseId, exportFormat);
      
      if (exportFormat === 'csv') {
        // Handle blob download for CSV
        const url = window.URL.createObjectURL(data);
        const link = document.createElement('a');
        link.href = url;
        link.download = `warehouse-${warehouseId}-locations.csv`;
        document.body.appendChild(link);
        link.click();
        document.body.removeChild(link);
        window.URL.revokeObjectURL(url);
      } else {
        // Handle JSON download
        const jsonStr = JSON.stringify(data, null, 2);
        const blob = new Blob([jsonStr], { type: 'application/json' });
        const url = window.URL.createObjectURL(blob);
        const link = document.createElement('a');
        link.href = url;
        link.download = `warehouse-${warehouseId}-locations.json`;
        document.body.appendChild(link);
        link.click();
        document.body.removeChild(link);
        window.URL.revokeObjectURL(url);
      }
    } catch (error) {
      console.error('Export failed:', error);
      alert('Failed to export locations. Please try again.');
    } finally {
      setExporting(false);
    }
  };

  // Handle file selection
  const handleFileSelect = (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    if (file) {
      setImportFile(file);
      setImportResult(null);
    }
  };

  // Parse CSV file
  const parseCSV = (text: string): CsvRow[] => {
    const lines = text.split('\n');
    const headers = lines[0].split(',').map(h => h.trim().replace(/"/g, ''));
    
    const data = [];
    for (let i = 1; i < lines.length; i++) {
      const line = lines[i].trim();
      if (!line) continue;
      
      const values = line.split(',').map(v => v.trim().replace(/"/g, ''));
      const row: Partial<CsvRow> = {};
      
      headers.forEach((header, index) => {
        const value = values[index] || '';
        
        // Type conversion based on field name
        if (header.includes('capacity') || header.includes('number')) {
          (row as any)[header] = value ? parseInt(value, 10) : 0;
        } else if (header === 'is_active' || header === 'is_storage_location') {
          (row as any)[header] = value.toLowerCase() === 'true';
        } else if (header === 'allowed_products') {
          (row as any)[header] = value ? value.split(';').map(p => p.trim()) : [];
        } else if (header === 'special_requirements') {
          try {
            (row as any)[header] = value ? JSON.parse(value) : {};
          } catch {
            (row as any)[header] = {};
          }
        } else {
          (row as any)[header] = value;
        }
      });
      
      // Ensure warehouse_id is set
      row.warehouse_id = warehouseId;
      
      data.push(row as CsvRow);
    }
    
    return data;
  };

  // Handle import
  const handleImport = async () => {
    if (!importFile) return;
    
    setImporting(true);
    setImportProgress(0);
    
    try {
      const text = await importFile.text();
      let locationsData: CsvRow[];
      
      if (importFile.name.endsWith('.json')) {
        locationsData = JSON.parse(text);
        if (!Array.isArray(locationsData)) {
          throw new Error('JSON file must contain an array of locations');
        }
      } else if (importFile.name.endsWith('.csv')) {
        locationsData = parseCSV(text);
      } else {
        throw new Error('Unsupported file format. Please use CSV or JSON.');
      }
      
      setImportProgress(50);
      
      // Validate and import locations
      const result = await locationApi.bulkCreateLocations(locationsData as any);
      
      setImportProgress(100);
      setImportResult(result);
      
      // Refresh locations list
      await fetchLocations({ warehouse_id: warehouseId });
      
      if (onImportComplete) {
        onImportComplete(result);
      }
      
    } catch (err: unknown) {
      const error = err as Error;
      console.error('Import failed:', error);
      setImportResult({
        created_count: 0,
        errors: [error.message || 'Import failed']
      });
    } finally {
      setImporting(false);
    }
  };

  // Download template
  const downloadTemplate = () => {
    const template = [
      {
        code: 'EXAMPLE-001',
        location_type: 'STORAGE',
        zone: 'GENERAL',
        capacity: 1,
        pallet_capacity: 1,
        aisle_number: 1,
        rack_number: 1,
        position_number: 1,
        level: 'A',
        allowed_products: [],
        special_requirements: {},
        is_active: true
      },
      {
        code: 'RECEIVING-01',
        location_type: 'RECEIVING',
        zone: 'DOCK',
        capacity: 10,
        pallet_capacity: 10,
        allowed_products: [],
        special_requirements: {},
        is_active: true
      }
    ];
    
    const jsonStr = JSON.stringify(template, null, 2);
    const blob = new Blob([jsonStr], { type: 'application/json' });
    const url = window.URL.createObjectURL(blob);
    const link = document.createElement('a');
    link.href = url;
    link.download = 'location-template.json';
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    window.URL.revokeObjectURL(url);
  };

  return (
    <div className="flex gap-2">
      {/* Export Button */}
      <Dialog>
        <DialogTrigger asChild>
          <Button variant="outline" size="sm">
            <Download className="h-4 w-4 mr-2" />
            Export Locations
          </Button>
        </DialogTrigger>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>Export Locations</DialogTitle>
            <DialogDescription>
              Download all locations for warehouse {warehouseId}
            </DialogDescription>
          </DialogHeader>
          <div className="space-y-4">
            <div className="space-y-2">
              <Label>Export Format</Label>
              <div className="flex gap-2">
                <Button
                  variant={exportFormat === 'csv' ? 'default' : 'outline'}
                  size="sm"
                  onClick={() => setExportFormat('csv')}
                >
                  CSV
                </Button>
                <Button
                  variant={exportFormat === 'json' ? 'default' : 'outline'}
                  size="sm"
                  onClick={() => setExportFormat('json')}
                >
                  JSON
                </Button>
              </div>
            </div>
            <div className="flex justify-end gap-2">
              <Button onClick={handleExport} disabled={exporting}>
                {exporting && <Loader2 className="h-4 w-4 mr-2 animate-spin" />}
                <Download className="h-4 w-4 mr-2" />
                Export {locations.length} locations
              </Button>
            </div>
          </div>
        </DialogContent>
      </Dialog>

      {/* Import Button */}
      <Dialog open={showImportDialog} onOpenChange={setShowImportDialog}>
        <DialogTrigger asChild>
          <Button variant="outline" size="sm">
            <Upload className="h-4 w-4 mr-2" />
            Import Locations
          </Button>
        </DialogTrigger>
        <DialogContent className="max-w-2xl">
          <DialogHeader>
            <DialogTitle>Import Locations</DialogTitle>
            <DialogDescription>
              Upload a CSV or JSON file to import locations
            </DialogDescription>
          </DialogHeader>
          
          <div className="space-y-6">
            {/* Template Download */}
            <Card>
              <CardHeader>
                <CardTitle className="text-sm">Need a template?</CardTitle>
                <CardDescription>
                  Download a sample file to see the expected format
                </CardDescription>
              </CardHeader>
              <CardContent>
                <Button variant="outline" size="sm" onClick={downloadTemplate}>
                  <FileText className="h-4 w-4 mr-2" />
                  Download Template
                </Button>
              </CardContent>
            </Card>

            <Separator />

            {/* File Upload */}
            <div className="space-y-4">
              <div className="space-y-2">
                <Label htmlFor="import-file">Select File</Label>
                <Input
                  id="import-file"
                  ref={fileInputRef}
                  type="file"
                  accept=".csv,.json"
                  onChange={handleFileSelect}
                  disabled={importing}
                />
              </div>

              {importFile && (
                <div className="text-sm text-muted-foreground">
                  Selected: {importFile.name} ({(importFile.size / 1024).toFixed(1)} KB)
                </div>
              )}

              {importing && (
                <div className="space-y-2">
                  <Label>Import Progress</Label>
                  <Progress value={importProgress} />
                </div>
              )}

              {importResult && (
                <Alert variant={importResult.errors.length > 0 ? "destructive" : "default"}>
                  {importResult.errors.length > 0 ? (
                    <AlertCircle className="h-4 w-4" />
                  ) : (
                    <CheckCircle className="h-4 w-4" />
                  )}
                  <AlertDescription>
                    <div className="space-y-2">
                      <div>
                        Import completed: {importResult.created_count} locations created
                      </div>
                      {importResult.errors.length > 0 && (
                        <div>
                          <div className="font-semibold">Errors:</div>
                          <ul className="list-disc list-inside text-sm">
                            {importResult.errors.slice(0, 5).map((error, i) => (
                              <li key={i}>{error}</li>
                            ))}
                            {importResult.errors.length > 5 && (
                              <li>... and {importResult.errors.length - 5} more errors</li>
                            )}
                          </ul>
                        </div>
                      )}
                    </div>
                  </AlertDescription>
                </Alert>
              )}
            </div>

            <div className="flex justify-end gap-2">
              <Button
                variant="outline"
                onClick={() => {
                  setShowImportDialog(false);
                  setImportFile(null);
                  setImportResult(null);
                  setImportProgress(0);
                }}
              >
                <X className="h-4 w-4 mr-2" />
                Cancel
              </Button>
              <Button
                onClick={handleImport}
                disabled={!importFile || importing}
              >
                {importing && <Loader2 className="h-4 w-4 mr-2 animate-spin" />}
                <Upload className="h-4 w-4 mr-2" />
                Import Locations
              </Button>
            </div>
          </div>
        </DialogContent>
      </Dialog>
    </div>
  );
}