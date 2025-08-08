'use client';

import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Badge } from '@/components/ui/badge';
import { Alert, AlertDescription } from '@/components/ui/alert';
import { Skeleton } from '@/components/ui/skeleton';
import { 
  Table, 
  TableBody, 
  TableCell, 
  TableHead, 
  TableHeader, 
  TableRow 
} from '@/components/ui/table';
import useLocationStore from '@/lib/location-store';
import { 
  Share2, 
  Plus, 
  Eye, 
  Download, 
  Users,
  Search,
  Filter,
  Loader2,
  Building2,
  Copy,
  Star
} from 'lucide-react';

interface TemplateManagerProps {
  warehouseId: string;
}

export function TemplateManager({ warehouseId }: TemplateManagerProps) {
  const {
    templates,
    currentWarehouseConfig,
    templatesLoading,
    fetchTemplates,
    applyTemplateByCode,
    createTemplateFromConfig,
    error
  } = useLocationStore();

  const [searchTerm, setSearchTerm] = useState('');
  const [templateScope, setTemplateScope] = useState<'all' | 'my' | 'public'>('all');
  const [shareCode, setShareCode] = useState('');

  useEffect(() => {
    fetchTemplates(templateScope, searchTerm);
  }, [templateScope, searchTerm, fetchTemplates]);

  const handleSearch = () => {
    fetchTemplates(templateScope, searchTerm);
  };

  const handleApplyByCode = async () => {
    if (shareCode.trim()) {
      try {
        await applyTemplateByCode(shareCode.trim(), warehouseId);
        setShareCode('');
      } catch (error) {
        console.error('Failed to apply template:', error);
      }
    }
  };

  const handleCreateTemplate = async () => {
    if (currentWarehouseConfig) {
      try {
        await createTemplateFromConfig(
          currentWarehouseConfig.id,
          `${currentWarehouseConfig.warehouse_name} Template`,
          `Template based on ${currentWarehouseConfig.warehouse_name}`,
          false
        );
      } catch (error) {
        console.error('Failed to create template:', error);
      }
    }
  };

  const copyTemplateCode = (code: string) => {
    navigator.clipboard.writeText(code);
    // You could add a toast notification here
  };

  if (templatesLoading) {
    return (
      <div className="space-y-4">
        <Card>
          <CardHeader>
            <Skeleton className="h-6 w-48" />
            <Skeleton className="h-4 w-72" />
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              {Array.from({ length: 5 }).map((_, i) => (
                <div key={i} className="flex items-center space-x-4">
                  <Skeleton className="h-12 w-12 rounded" />
                  <div className="space-y-2 flex-1">
                    <Skeleton className="h-4 w-[250px]" />
                    <Skeleton className="h-4 w-[200px]" />
                  </div>
                  <Skeleton className="h-8 w-20" />
                </div>
              ))}
            </div>
          </CardContent>
        </Card>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header Actions */}
      <div className="flex justify-between items-start">
        <div>
          <h3 className="text-lg font-semibold">Warehouse Templates</h3>
          <p className="text-sm text-muted-foreground">
            Save and share warehouse configurations
          </p>
        </div>
        
        {currentWarehouseConfig && (
          <Button onClick={handleCreateTemplate} className="flex items-center gap-2">
            <Plus className="h-4 w-4" />
            Create Template
          </Button>
        )}
      </div>

      {error && (
        <Alert variant="destructive">
          <AlertDescription>{error}</AlertDescription>
        </Alert>
      )}

      {/* Apply Template by Code */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Share2 className="h-5 w-5" />
            Apply Template by Code
          </CardTitle>
          <CardDescription>
            Use a template code shared by another warehouse manager
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="flex gap-2">
            <Input
              placeholder="Enter template code (e.g., WAR-4A2R-ABC)"
              value={shareCode}
              onChange={(e) => setShareCode(e.target.value.toUpperCase())}
            />
            <Button onClick={handleApplyByCode} disabled={!shareCode.trim()}>
              Apply Template
            </Button>
          </div>
        </CardContent>
      </Card>

      {/* Templates List */}
      <Card>
        <CardHeader>
          <CardTitle>Available Templates</CardTitle>
          <CardDescription>
            Browse and use templates from yourself and other users
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          {/* Search and Filter */}
          <div className="flex gap-2">
            <Input
              placeholder="Search templates..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              onKeyPress={(e) => e.key === 'Enter' && handleSearch()}
              className="flex-1"
            />
            <Button onClick={handleSearch} variant="outline">
              <Search className="h-4 w-4" />
            </Button>
          </div>

          <div className="flex gap-2">
            <Button
              variant={templateScope === 'all' ? 'default' : 'outline'}
              size="sm"
              onClick={() => setTemplateScope('all')}
            >
              All Templates
            </Button>
            <Button
              variant={templateScope === 'my' ? 'default' : 'outline'}
              size="sm"
              onClick={() => setTemplateScope('my')}
            >
              My Templates
            </Button>
            <Button
              variant={templateScope === 'public' ? 'default' : 'outline'}
              size="sm"
              onClick={() => setTemplateScope('public')}
            >
              Public Templates
            </Button>
          </div>

          {/* Templates Table */}
          {templates.length === 0 ? (
            <div className="text-center py-12">
              <Building2 className="h-16 w-16 mx-auto mb-4 text-muted-foreground opacity-50" />
              <h3 className="text-lg font-semibold mb-2">No Templates Found</h3>
              <p className="text-muted-foreground mb-4">
                {templateScope === 'my' 
                  ? "You haven't created any templates yet."
                  : "No templates match your search criteria."
                }
              </p>
              {currentWarehouseConfig && templateScope === 'my' && (
                <Button onClick={handleCreateTemplate}>
                  <Plus className="h-4 w-4 mr-2" />
                  Create Your First Template
                </Button>
              )}
            </div>
          ) : (
            <div className="rounded-md border">
              <Table>
                <TableHeader>
                  <TableRow>
                    <TableHead>Template</TableHead>
                    <TableHead>Structure</TableHead>
                    <TableHead>Visibility</TableHead>
                    <TableHead>Usage</TableHead>
                    <TableHead>Code</TableHead>
                    <TableHead className="w-[100px]">Actions</TableHead>
                  </TableRow>
                </TableHeader>
                <TableBody>
                  {templates.map((template) => (
                    <TableRow key={template.id}>
                      <TableCell>
                        <div className="space-y-1">
                          <div className="font-medium">{template.name}</div>
                          {template.description && (
                            <div className="text-sm text-muted-foreground">
                              {template.description}
                            </div>
                          )}
                          <div className="text-xs text-muted-foreground">
                            by {template.creator_username || 'Unknown'}
                          </div>
                        </div>
                      </TableCell>
                      <TableCell>
                        <div className="text-sm">
                          {template.num_aisles}A × {template.racks_per_aisle}R × {template.positions_per_rack}P × {template.levels_per_position}L
                        </div>
                        <div className="text-xs text-muted-foreground">
                          {template.default_pallet_capacity} pallet{template.default_pallet_capacity > 1 ? 's' : ''}/level
                        </div>
                      </TableCell>
                      <TableCell>
                        <Badge variant={template.is_public ? 'default' : 'secondary'}>
                          {template.is_public ? (
                            <>
                              <Users className="h-3 w-3 mr-1" />
                              Public
                            </>
                          ) : (
                            'Private'
                          )}
                        </Badge>
                      </TableCell>
                      <TableCell>
                        <div className="flex items-center gap-1">
                          <Star className="h-3 w-3 text-yellow-500" />
                          <span className="text-sm">{template.usage_count}</span>
                        </div>
                      </TableCell>
                      <TableCell>
                        <Button
                          variant="ghost"
                          size="sm"
                          onClick={() => copyTemplateCode(template.template_code)}
                          className="font-mono text-xs"
                        >
                          {template.template_code}
                          <Copy className="h-3 w-3 ml-1" />
                        </Button>
                      </TableCell>
                      <TableCell>
                        <div className="flex gap-1">
                          <Button variant="ghost" size="sm">
                            <Eye className="h-4 w-4" />
                          </Button>
                          <Button variant="ghost" size="sm">
                            <Download className="h-4 w-4" />
                          </Button>
                        </div>
                      </TableCell>
                    </TableRow>
                  ))}
                </TableBody>
              </Table>
            </div>
          )}
        </CardContent>
      </Card>
    </div>
  );
}