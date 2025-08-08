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
  Star,
  Palette,
  Grid3X3,
  Crown,
  SlidersHorizontal
} from 'lucide-react';

interface EnhancedTemplateManagerProps {
  warehouseId: string;
}

const TEMPLATE_CATEGORIES = [
  { value: '', label: 'All Categories' },
  { value: 'MANUFACTURING', label: 'Manufacturing' },
  { value: 'RETAIL', label: 'Retail Distribution' },
  { value: 'FOOD_BEVERAGE', label: 'Food & Beverage' },
  { value: 'PHARMA', label: 'Pharmaceutical' },
  { value: 'AUTOMOTIVE', label: 'Automotive' },
  { value: 'ECOMMERCE', label: 'E-commerce' },
  { value: 'CUSTOM', label: 'Custom' }
];

export function EnhancedTemplateManagerV2({ warehouseId }: EnhancedTemplateManagerProps) {
  const {
    templates,
    currentWarehouseConfig,
    templatesLoading,
    fetchTemplates,
    applyTemplateByCode,
    createTemplateFromConfig,
    error
  } = useLocationStore();

  // UI State
  const [activeTab, setActiveTab] = useState('browse');
  const [viewMode, setViewMode] = useState<'card' | 'compact' | 'detailed'>('card');
  const [showCreateWizard, setShowCreateWizard] = useState(false);
  
  // Filter State
  const [searchTerm, setSearchTerm] = useState('');
  const [selectedCategory, setSelectedCategory] = useState('');
  const [templateScope, setTemplateScope] = useState<'all' | 'my' | 'public' | 'featured'>('all');
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
    
    // Apply category filter (TODO: Add category field to WarehouseTemplate interface)
    if (selectedCategory) {
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
  }, [templates, selectedCategory, showFeaturedOnly, sortBy]);

  const handleSearch = () => {
    const scope = templateScope === 'featured' ? 'all' : templateScope;
    fetchTemplates(scope, searchTerm);
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

  const handleApplyTemplate = async (template: { template_code?: string }) => {
    if (!template.template_code) return;
    
    try {
      await applyTemplateByCode(template.template_code, warehouseId);
    } catch (error) {
      console.error('Failed to apply template:', error);
    }
  };

  const handleViewTemplate = (template: unknown) => {
    // TODO: Open template details modal
    console.log('View template:', template);
  };

  const copyTemplateCode = (code: string) => {
    navigator.clipboard.writeText(code);
  };

  const handleTemplateCreated = (template: unknown) => {
    // Refresh templates list
    const scope = templateScope === 'featured' ? 'all' : templateScope;
    fetchTemplates(scope, searchTerm);
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
            emptyMessage={
              templateScope === 'my' 
                ? "You haven't created any templates yet. Click 'Design New Template' to get started!"
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
                Template codes are typically shared in the format: <code className="bg-muted px-1 rounded">TPL-XAXR-XXXX</code>
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
                templates={templates.filter(t => t.creator_username === 'currentuser')} // TODO: Use actual user
                variant={viewMode}
                onApply={handleApplyTemplate}
                onView={handleViewTemplate}
                onCopyCode={copyTemplateCode}
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
    </div>
  );
}