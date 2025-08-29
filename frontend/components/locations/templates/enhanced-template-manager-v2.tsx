'use client';

import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Badge } from '@/components/ui/badge';
import { Alert, AlertDescription } from '@/components/ui/alert';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Skeleton } from '@/components/ui/skeleton';
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select';
import { Switch } from '@/components/ui/switch';
import { Label } from '@/components/ui/label';
import { TemplateCreationWizard } from './template-creation-wizard';
import { TemplateGrid } from './template-preview';
import { EnhancedTemplateEditModal } from './enhanced-template-edit-modal';
import { TemplateApplyModal } from './template-apply-modal';
import useLocationStore, { WarehouseTemplate } from '@/lib/location-store';
import { useAuth } from '@/lib/auth-context';
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
  Star,
  Palette,
  Grid3X3,
  Crown,
  SlidersHorizontal,
  CheckCircle
} from 'lucide-react';

interface EnhancedTemplateManagerProps {
  warehouseId: string;
}

const TEMPLATE_CATEGORIES = [
  { value: 'all', label: 'All Categories' },
  { value: 'MANUFACTURING', label: 'Manufacturing' },
  { value: 'RETAIL', label: 'Retail Distribution' },
  { value: 'FOOD_BEVERAGE', label: 'Food & Beverage' },
  { value: 'PHARMA', label: 'Pharmaceutical' },
  { value: 'AUTOMOTIVE', label: 'Automotive' },
  { value: 'ECOMMERCE', label: 'E-commerce' },
  { value: 'CUSTOM', label: 'Custom' }
];

// Helper function to check if a template is currently active
const isTemplateActive = (template: any, config: any) => {
  if (!template || !config) return false;
  
  // Compare key template characteristics with current warehouse config
  return (
    template.num_aisles === config.num_aisles &&
    template.racks_per_aisle === config.racks_per_aisle &&
    template.positions_per_rack === config.positions_per_rack &&
    template.levels_per_position === config.levels_per_position &&
    template.default_pallet_capacity === config.default_pallet_capacity &&
    template.bidimensional_racks === config.bidimensional_racks
  );
};

export function EnhancedTemplateManagerV2({ warehouseId }: EnhancedTemplateManagerProps) {
  const { user } = useAuth();
  const {
    templates,
    currentWarehouseConfig,
    templatesLoading,
    fetchTemplates,
    applyTemplate,
    applyTemplateByCode,
    createTemplateFromConfig,
    deleteTemplate,
    fetchWarehouseConfig,
    fetchLocations,
    error
  } = useLocationStore();

  // UI State
  const [activeTab, setActiveTab] = useState('browse');
  const [viewMode, setViewMode] = useState<'card' | 'compact' | 'detailed'>('card');
  const [showCreateWizard, setShowCreateWizard] = useState(false);
  const [editingTemplate, setEditingTemplate] = useState<WarehouseTemplate | null>(null);
  const [showEditModal, setShowEditModal] = useState(false);
  
  // Template Apply Modal State
  const [showApplyModal, setShowApplyModal] = useState(false);
  const [templateToApply, setTemplateToApply] = useState<any>(null);
  const [applyResult, setApplyResult] = useState<any>(null);
  
  // Filter State
  const [searchTerm, setSearchTerm] = useState('');
  const [selectedCategory, setSelectedCategory] = useState('all');
  const [templateScope, setTemplateScope] = useState<'all' | 'my' | 'public' | 'featured'>('my');
  const [showFeaturedOnly, setShowFeaturedOnly] = useState(false);
  const [sortBy, setSortBy] = useState<'recent' | 'popular' | 'rating' | 'name'>('recent');
  
  // Quick Apply State
  const [shareCode, setShareCode] = useState('');

  useEffect(() => {
    const scope = templateScope === 'featured' ? 'all' : templateScope;
    fetchTemplates(scope, searchTerm);
  }, [templateScope, searchTerm, fetchTemplates]);

  // Filter and sort templates
  const filteredAndSortedTemplates = React.useMemo(() => {
    let filtered = [...templates];
    
    // Mark active template based on current warehouse config
    if (currentWarehouseConfig) {
      filtered = filtered.map(template => ({
        ...template,
        is_applied: isTemplateActive(template, currentWarehouseConfig),
        applied_warehouse_id: isTemplateActive(template, currentWarehouseConfig) ? currentWarehouseConfig.warehouse_id : undefined
      }));
    }
    
    // Apply category filter (TODO: Add category field to WarehouseTemplate interface)
    if (selectedCategory && selectedCategory !== 'all') {
      filtered = filtered.filter(t => (t as any).category === selectedCategory);
    }
    
    // Apply featured filter (TODO: Add featured field to WarehouseTemplate interface)
    if (showFeaturedOnly) {
      filtered = filtered.filter(t => (t as any).featured);
    }
    
    // Apply sorting
    filtered.sort((a, b) => {
      switch (sortBy) {
        case 'popular':
          return (b.usage_count || 0) - (a.usage_count || 0);
        case 'rating':
          return ((b as any).rating || 0) - ((a as any).rating || 0);
        case 'name':
          return a.name.localeCompare(b.name);
        case 'recent':
        default:
          return new Date(b.created_at || 0).getTime() - new Date(a.created_at || 0).getTime();
      }
    });
    
    return filtered;
  }, [templates, selectedCategory, showFeaturedOnly, sortBy, currentWarehouseConfig]);

  const handleSearch = () => {
    const scope = templateScope === 'featured' ? 'all' : templateScope;
    fetchTemplates(scope, searchTerm);
  };

  const handleApplyByCode = async () => {
    if (shareCode.trim()) {
      try {
        // Create mock template for the modal
        const mockTemplate = {
          name: `Template ${shareCode.trim()}`,
          template_code: shareCode.trim(),
          description: 'Template applied by code',
          num_aisles: 0,
          racks_per_aisle: 0,
          positions_per_rack: 0,
          levels_per_position: 0,
          default_pallet_capacity: 1
        };
        
        setTemplateToApply(mockTemplate);
        setApplyResult(null);
        setShowApplyModal(true);
      } catch (error: any) {
        console.error('Failed to prepare template application:', error);
      }
    }
  };

  const handleCreateFromConfig = async () => {
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

  const handleApplyTemplate = async (template: { template_code?: string; name?: string }) => {
    if (!template.template_code) return;
    
    // Set up the modal with template data
    setTemplateToApply(template);
    setApplyResult(null);
    setShowApplyModal(true);
  };

  const handleViewTemplate = (template: any) => {
    // Create a detailed alert/modal showing template information
    const details = [
      `Name: ${template.name}`,
      `Description: ${template.description || 'No description'}`,
      `Structure: ${template.num_aisles}A × ${template.racks_per_aisle}R × ${template.positions_per_rack}P × ${template.levels_per_position}L`,
      `Capacity: ${template.num_aisles * template.racks_per_aisle * template.positions_per_rack * template.levels_per_position * (template.default_pallet_capacity || 1)} pallets`,
      `Template Code: ${template.template_code}`,
      `Created by: ${template.creator_username || 'Unknown'}`,
      `Created: ${template.created_at ? new Date(template.created_at).toLocaleDateString() : 'Unknown'}`
    ].join('\n');
    
    alert(`Template Details:\n\n${details}`);
  };

  // Modal handlers
  const handleModalApply = async () => {
    if (!templateToApply?.template_code) return;
    
    try {
      const targetWarehouseId = warehouseId || 'DEFAULT';
      const templateName = templateToApply.name || 'Applied Template';
      const warehouseName = currentWarehouseConfig?.warehouse_name || `Warehouse ${targetWarehouseId}`;
      
      console.log(`Applying template: ${templateToApply.template_code} to warehouse: ${targetWarehouseId}`);
      
      const result = await applyTemplateByCode(
        templateToApply.template_code, 
        targetWarehouseId, 
        warehouseName
      );
      
      console.log('Template application result:', result);
      
      // Set success result
      setApplyResult({
        success: true,
        locations_created: result?.locations_created,
        storage_locations: result?.storage_locations,
        special_areas: result?.special_areas
      });
      
      // Clear share code if it was used
      setShareCode('');
      
      // Optimized refresh: Only refresh templates, no need for extra delays
      // The applyTemplateByCode store method already handles config and location refresh
      console.log(`Template applied successfully to warehouse: ${targetWarehouseId}`);
      
      // Refresh templates to show updated status (cached refresh)
      const scope = templateScope === 'featured' ? 'all' : templateScope;
      await fetchTemplates(scope, searchTerm);
      
    } catch (error: any) {
      console.error('Failed to apply template:', error);
      
      // Set error result
      setApplyResult({
        success: false,
        error: error?.response?.data?.error || 'Failed to apply template. Please try again.'
      });
    }
  };

  const handleCloseApplyModal = () => {
    setShowApplyModal(false);
    setTemplateToApply(null);
    setApplyResult(null);
  };

  const copyTemplateCode = (code: string) => {
    navigator.clipboard.writeText(code);
  };

  const handleTemplateCreated = async (template: any) => {
    // Refresh templates list to show the newly created template
    const scope = templateScope === 'featured' ? 'all' : templateScope;
    fetchTemplates(scope, searchTerm);
  };

  const handleEditTemplate = (template: WarehouseTemplate) => {
    setEditingTemplate(template);
    setShowEditModal(true);
  };

  const handleCloseEditModal = () => {
    setEditingTemplate(null);
    setShowEditModal(false);
  };

  const handleTemplateUpdated = (updatedTemplate: WarehouseTemplate) => {
    // Refresh templates list to show updated information
    const scope = templateScope === 'featured' ? 'all' : templateScope;
    fetchTemplates(scope, searchTerm);
  };

  const handleDeleteTemplate = async (template: WarehouseTemplate) => {
    const confirmed = window.confirm(
      `Are you sure you want to delete the template "${template.name}"? This action cannot be undone.`
    );
    
    if (!confirmed) return;
    
    try {
      await deleteTemplate(template.id);
      
      // Refresh templates list to show updated information
      const scope = templateScope === 'featured' ? 'all' : templateScope;
      await fetchTemplates(scope, searchTerm);
      
      console.log(`Template "${template.name}" deleted successfully`);
    } catch (error: any) {
      console.error('Failed to delete template:', error);
      alert(`Failed to delete template: ${error.response?.data?.error || error.message || 'Unknown error'}`);
    }
  };

  const getScopeDescription = () => {
    switch (templateScope) {
      case 'my':
        return 'Templates you have created';
      case 'public':
        return 'Community templates available to everyone';
      case 'featured':
        return 'Curated high-quality templates';
      case 'all':
      default:
        return 'All templates you have access to';
    }
  };

  const getTemplateStats = () => {
    return {
      total: templates.length,
      my: templates.filter(t => t.creator_username === 'currentuser').length, // TODO: Use actual user
      public: templates.filter(t => t.is_public).length,
      featured: templates.filter(t => (t as any).featured).length
    };
  };

  const stats = getTemplateStats();

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
              {Array.from({ length: 6 }).map((_, i) => (
                <Skeleton key={i} className="h-32 w-full rounded" />
              ))}
            </div>
          </CardContent>
        </Card>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex justify-between items-start">
        <div>
          <h3 className="text-2xl font-bold tracking-tight">Template Library</h3>
          <p className="text-muted-foreground">
            Create, browse, and apply warehouse layout templates
          </p>
          {/* Active Template Indicator */}
          {(() => {
            const activeTemplate = filteredAndSortedTemplates.find(t => t.is_applied);
            return activeTemplate ? (
              <div className="mt-2 flex items-center gap-2">
                <Badge variant="secondary" className="flex items-center gap-1 bg-green-100 text-green-700">
                  <CheckCircle className="h-3 w-3" />
                  Active: {activeTemplate.name}
                </Badge>
                <span className="text-xs text-muted-foreground">
                  Currently applied to {currentWarehouseConfig?.warehouse_name || warehouseId}
                </span>
              </div>
            ) : null;
          })()}
        </div>
        
        <div className="flex items-center gap-2">
          {currentWarehouseConfig && (
            <Button onClick={handleCreateFromConfig} variant="outline">
              <Building2 className="h-4 w-4 mr-2" />
              Save Current Layout
            </Button>
          )}
          <Button onClick={() => setShowCreateWizard(true)}>
            <Palette className="h-4 w-4 mr-2" />
            Design New Template
          </Button>
        </div>
      </div>

      {error && (
        <Alert variant="destructive">
          <AlertDescription>{error}</AlertDescription>
        </Alert>
      )}

      <Tabs value={activeTab} onValueChange={setActiveTab} className="w-full">
        <TabsList className="grid w-full grid-cols-3">
          <TabsTrigger value="browse" className="flex items-center gap-2">
            <Grid3X3 className="h-4 w-4" />
            Browse Templates ({stats.total})
          </TabsTrigger>
          <TabsTrigger value="quick-apply" className="flex items-center gap-2">
            <Share2 className="h-4 w-4" />
            Quick Apply
          </TabsTrigger>
          <TabsTrigger value="my-templates" className="flex items-center gap-2">
            <Users className="h-4 w-4" />
            My Templates ({stats.my})
          </TabsTrigger>
        </TabsList>

        {/* Browse Templates Tab */}
        <TabsContent value="browse" className="space-y-6">
          {/* Filters and Search */}
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <SlidersHorizontal className="h-5 w-5" />
                Search & Filter Templates
              </CardTitle>
              <CardDescription>{getScopeDescription()}</CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              {/* Scope Selection */}
              <div className="flex gap-2 flex-wrap">
                {[
                  { key: 'all', label: 'All Templates', count: stats.total },
                  { key: 'featured', label: 'Featured', count: stats.featured, icon: Crown },
                  { key: 'public', label: 'Public', count: stats.public },
                  { key: 'my', label: 'My Templates', count: stats.my }
                ].map(({ key, label, count, icon: Icon }) => (
                  <Button
                    key={key}
                    variant={templateScope === key ? 'default' : 'outline'}
                    size="sm"
                    onClick={() => setTemplateScope(key as any)}
                    className="flex items-center gap-2"
                  >
                    {Icon && <Icon className="h-3 w-3" />}
                    {label} ({count})
                  </Button>
                ))}
              </div>

              {/* Search and Filters */}
              <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
                <div className="md:col-span-2">
                  <div className="flex gap-2">
                    <Input
                      placeholder="Search templates by name, description, or tags..."
                      value={searchTerm}
                      onChange={(e) => setSearchTerm(e.target.value)}
                      onKeyPress={(e) => e.key === 'Enter' && handleSearch()}
                      className="flex-1"
                    />
                    <Button onClick={handleSearch} variant="outline">
                      <Search className="h-4 w-4" />
                    </Button>
                  </div>
                </div>

                <Select value={selectedCategory} onValueChange={setSelectedCategory}>
                  <SelectTrigger>
                    <SelectValue placeholder="Category" />
                  </SelectTrigger>
                  <SelectContent>
                    {TEMPLATE_CATEGORIES.map((category) => (
                      <SelectItem key={category.value} value={category.value}>
                        {category.label}
                      </SelectItem>
                    ))}
                  </SelectContent>
                </Select>

                <Select value={sortBy} onValueChange={(value: 'recent' | 'popular' | 'rating' | 'name') => setSortBy(value)}>
                  <SelectTrigger>
                    <SelectValue placeholder="Sort by" />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="recent">Most Recent</SelectItem>
                    <SelectItem value="popular">Most Popular</SelectItem>
                    <SelectItem value="rating">Highest Rated</SelectItem>
                    <SelectItem value="name">Name A-Z</SelectItem>
                  </SelectContent>
                </Select>
              </div>

              {/* Advanced Filters */}
              <div className="flex items-center justify-between">
                <div className="flex items-center space-x-2">
                  <Switch
                    id="featured-only"
                    checked={showFeaturedOnly}
                    onCheckedChange={setShowFeaturedOnly}
                  />
                  <Label htmlFor="featured-only" className="flex items-center gap-2">
                    <Crown className="h-4 w-4 text-yellow-500" />
                    Featured templates only
                  </Label>
                </div>

                <div className="flex items-center gap-2">
                  <Label className="text-sm">View:</Label>
                  <div className="flex items-center gap-1">
                    {[
                      { key: 'card', icon: Grid3X3 },
                      { key: 'compact', icon: Filter },
                      { key: 'detailed', icon: Eye }
                    ].map(({ key, icon: Icon }) => (
                      <Button
                        key={key}
                        variant={viewMode === key ? 'default' : 'ghost'}
                        size="sm"
                        onClick={() => setViewMode(key as any)}
                      >
                        <Icon className="h-4 w-4" />
                      </Button>
                    ))}
                  </div>
                </div>
              </div>
            </CardContent>
          </Card>

          {/* Templates Display */}
          <TemplateGrid
            templates={filteredAndSortedTemplates}
            variant={viewMode}
            onApply={handleApplyTemplate}
            onView={handleViewTemplate}
            onCopyCode={copyTemplateCode}
            onEdit={handleEditTemplate}
            onDelete={handleDeleteTemplate}
            currentUsername={user?.username}
            emptyMessage={
              templateScope === 'my' 
                ? "Welcome! You haven't created any templates yet. Get started: Click 'Design New Template' or use 'Import Template Code' to import a shared template."
                : "No templates match your search criteria. Try adjusting your filters."
            }
          />
        </TabsContent>

        {/* Quick Apply Tab */}
        <TabsContent value="quick-apply" className="space-y-6">
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Share2 className="h-5 w-5" />
                Apply Template by Code
              </CardTitle>
              <CardDescription>
                Quickly apply a template using its unique code shared by another user
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="flex gap-2">
                <Input
                  placeholder="Enter template code (e.g., TPL-4A2R-ABC1)"
                  value={shareCode}
                  onChange={(e) => setShareCode(e.target.value.toUpperCase())}
                  className="font-mono"
                />
                <Button onClick={handleApplyByCode} disabled={!shareCode.trim()}>
                  <Download className="h-4 w-4 mr-2" />
                  Apply Template
                </Button>
              </div>
              <div className="text-sm text-muted-foreground">
                Get template codes from colleagues to import their warehouse setups. Template codes look like: <code className="bg-muted px-1 rounded">TPL-XAXR-XXXX</code>
              </div>
            </CardContent>
          </Card>

          {/* Recent Templates */}
          <Card>
            <CardHeader>
              <CardTitle>Recently Applied Templates</CardTitle>
              <CardDescription>
                Quick access to templates you've used recently
              </CardDescription>
            </CardHeader>
            <CardContent>
              <TemplateGrid
                templates={templates.slice(0, 6)} // Show recent templates
                variant="compact"
                onApply={handleApplyTemplate}
                onView={handleViewTemplate}
                onCopyCode={copyTemplateCode}
                onEdit={handleEditTemplate}
                onDelete={handleDeleteTemplate}
                currentUsername={user?.username}
                emptyMessage="No recently used templates"
              />
            </CardContent>
          </Card>
        </TabsContent>

        {/* My Templates Tab */}
        <TabsContent value="my-templates" className="space-y-6">
          <Card>
            <CardHeader>
              <div className="flex justify-between items-start">
                <div>
                  <CardTitle>My Templates</CardTitle>
                  <CardDescription>
                    Templates you have created and can manage
                  </CardDescription>
                </div>
                <div className="flex gap-2">
                  {currentWarehouseConfig && (
                    <Button onClick={handleCreateFromConfig} variant="outline" size="sm">
                      <Building2 className="h-4 w-4 mr-2" />
                      From Current
                    </Button>
                  )}
                  <Button onClick={() => setShowCreateWizard(true)} size="sm">
                    <Plus className="h-4 w-4 mr-2" />
                    New Template
                  </Button>
                </div>
              </div>
            </CardHeader>
            <CardContent>
              <TemplateGrid
                templates={templates.filter(t => t.creator_username === user?.username)}
                variant={viewMode}
                onApply={handleApplyTemplate}
                onView={handleViewTemplate}
                onCopyCode={copyTemplateCode}
                onEdit={handleEditTemplate}
                onDelete={handleDeleteTemplate}
                currentUsername={user?.username}
                emptyMessage="You haven't created any templates yet. Design your first template to get started!"
              />
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>

      {/* Template Creation Wizard */}
      <TemplateCreationWizard
        open={showCreateWizard}
        onClose={() => setShowCreateWizard(false)}
        onTemplateCreated={handleTemplateCreated}
      />

      {/* Template Edit Modal */}
      <EnhancedTemplateEditModal
        template={editingTemplate}
        open={showEditModal}
        onClose={handleCloseEditModal}
        onTemplateUpdated={handleTemplateUpdated}
        warehouseId={warehouseId}
      />

      {/* Template Apply Modal */}
      <TemplateApplyModal
        open={showApplyModal}
        onClose={handleCloseApplyModal}
        template={templateToApply}
        warehouseName={currentWarehouseConfig?.warehouse_name}
        warehouseId={warehouseId}
        onApply={handleModalApply}
        applyResult={applyResult}
      />
    </div>
  );
}