'use client';

import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Badge } from '@/components/ui/badge';
import { Alert, AlertDescription } from '@/components/ui/alert';
import { Skeleton } from '@/components/ui/skeleton';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select';
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from '@/components/ui/dialog';
import { Label } from '@/components/ui/label';
import { Textarea } from '@/components/ui/textarea';
import { Switch } from '@/components/ui/switch';
import { 
  Table, 
  TableBody, 
  TableCell, 
  TableHead, 
  TableHeader, 
  TableRow 
} from '@/components/ui/table';
import { 
  Share2, 
  Plus, 
  Eye, 
  Download, 
  Users,
  User,
  Search,
  Filter,
  Loader2,
  Building2,
  Copy,
  Star,
  Lock,
  Globe,
  Building,
  Crown,
  Settings,
  MessageSquare,
  Heart,
  Tag
} from 'lucide-react';

interface Template {
  id: number;
  name: string;
  description: string;
  template_code: string;
  visibility: 'PRIVATE' | 'COMPANY' | 'PUBLIC';
  visibility_display: string;
  template_category: string;
  featured: boolean;
  rating: number;
  usage_count: number;
  downloads_count: number;
  tags: string[];
  creator_username: string;
  creator_organization?: string;
  review_count: number;
  created_at: string;
  num_aisles: number;
  racks_per_aisle: number;
  positions_per_rack: number;
  levels_per_position: number;
}

interface TemplateCategory {
  id: number;
  category_name: string;
  display_name: string;
  description: string;
}

interface EnhancedTemplateManagerProps {
  warehouseId: string;
}

export function EnhancedTemplateManager({ warehouseId }: EnhancedTemplateManagerProps) {
  // State management
  const [templates, setTemplates] = useState<Template[]>([]);
  const [categories, setCategories] = useState<TemplateCategory[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  
  // Filter states
  const [activeScope, setActiveScope] = useState<'accessible' | 'my' | 'company' | 'public'>('accessible');
  const [selectedCategory, setSelectedCategory] = useState<string>('');
  const [searchTerm, setSearchTerm] = useState('');
  const [showFeaturedOnly, setShowFeaturedOnly] = useState(false);
  
  // Create template dialog state
  const [showCreateDialog, setShowCreateDialog] = useState(false);
  const [createTemplateData, setCreateTemplateData] = useState({
    name: '',
    description: '',
    visibility: 'PRIVATE' as 'PRIVATE' | 'COMPANY' | 'PUBLIC',
    template_category: 'CUSTOM',
    industry_category: '',
    tags: [] as string[]
  });

  // Mock data for demonstration
  useEffect(() => {
    fetchTemplates();
    fetchCategories();
  }, [activeScope, selectedCategory, searchTerm, showFeaturedOnly]);

  const fetchTemplates = async () => {
    setLoading(true);
    try {
      // Mock API call - replace with actual API
      const mockTemplates: Template[] = [
        {
          id: 1,
          name: "Standard Manufacturing Layout",
          description: "4-aisle manufacturing warehouse with receiving and staging areas",
          template_code: "WAR-4A2R-MFG",
          visibility: 'PUBLIC',
          visibility_display: "Public (Everyone)",
          template_category: 'MANUFACTURING',
          featured: true,
          rating: 4.8,
          usage_count: 156,
          downloads_count: 89,
          tags: ['manufacturing', 'standard', 'popular'],
          creator_username: 'admin',
          creator_organization: 'WareWise Solutions',
          review_count: 23,
          created_at: '2024-01-15T10:30:00Z',
          num_aisles: 4,
          racks_per_aisle: 2,
          positions_per_rack: 50,
          levels_per_position: 4
        },
        {
          id: 2,
          name: "My Custom Retail Layout",
          description: "Personal retail distribution center template",
          template_code: "WAR-6A3R-RTL",
          visibility: 'PRIVATE',
          visibility_display: "Private (Only You)",
          template_category: 'RETAIL',
          featured: false,
          rating: 0.0,
          usage_count: 2,
          downloads_count: 0,
          tags: ['retail', 'custom'],
          creator_username: 'currentuser',
          creator_organization: 'Your Company',
          review_count: 0,
          created_at: '2024-01-20T14:15:00Z',
          num_aisles: 6,
          racks_per_aisle: 3,
          positions_per_rack: 40,
          levels_per_position: 5
        },
        {
          id: 3,
          name: "Company Standard Layout",
          description: "Our company's standardized warehouse configuration",
          template_code: "WAR-5A2R-STD",
          visibility: 'COMPANY',
          visibility_display: "Company Only",
          template_category: 'CUSTOM',
          featured: false,
          rating: 4.2,
          usage_count: 12,
          downloads_count: 8,
          tags: ['company', 'standard'],
          creator_username: 'manager',
          creator_organization: 'Your Company',
          review_count: 5,
          created_at: '2024-01-18T09:45:00Z',
          num_aisles: 5,
          racks_per_aisle: 2,
          positions_per_rack: 60,
          levels_per_position: 4
        }
      ];
      
      // Filter based on scope
      let filteredTemplates = mockTemplates;
      if (activeScope === 'my') {
        filteredTemplates = mockTemplates.filter(t => t.creator_username === 'currentuser');
      } else if (activeScope === 'company') {
        filteredTemplates = mockTemplates.filter(t => t.visibility === 'COMPANY' || t.creator_organization === 'Your Company');
      } else if (activeScope === 'public') {
        filteredTemplates = mockTemplates.filter(t => t.visibility === 'PUBLIC');
      }
      
      // Apply other filters
      if (selectedCategory) {
        filteredTemplates = filteredTemplates.filter(t => t.template_category === selectedCategory);
      }
      if (searchTerm) {
        filteredTemplates = filteredTemplates.filter(t => 
          t.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
          t.description.toLowerCase().includes(searchTerm.toLowerCase()) ||
          t.tags.some(tag => tag.toLowerCase().includes(searchTerm.toLowerCase()))
        );
      }
      if (showFeaturedOnly) {
        filteredTemplates = filteredTemplates.filter(t => t.featured);
      }
      
      setTemplates(filteredTemplates);
    } catch (err) {
      setError('Failed to load templates');
    } finally {
      setLoading(false);
    }
  };

  const fetchCategories = async () => {
    // Mock categories
    const mockCategories: TemplateCategory[] = [
      { id: 1, category_name: 'MANUFACTURING', display_name: 'Manufacturing', description: 'Manufacturing warehouse templates' },
      { id: 2, category_name: 'RETAIL', display_name: 'Retail Distribution', description: 'Retail distribution center templates' },
      { id: 3, category_name: 'FOOD_BEVERAGE', display_name: 'Food & Beverage', description: 'Cold chain and food storage templates' },
      { id: 4, category_name: 'CUSTOM', display_name: 'Custom', description: 'User-created custom templates' }
    ];
    setCategories(mockCategories);
  };

  const getVisibilityIcon = (visibility: string) => {
    switch (visibility) {
      case 'PRIVATE': return <Lock className="h-4 w-4 text-gray-600" />;
      case 'COMPANY': return <Building className="h-4 w-4 text-blue-600" />;
      case 'PUBLIC': return <Globe className="h-4 w-4 text-green-600" />;
      default: return <Lock className="h-4 w-4 text-gray-600" />;
    }
  };

  const getVisibilityBadge = (template: Template) => {
    const variants = {
      'PRIVATE': 'secondary' as const,
      'COMPANY': 'default' as const, 
      'PUBLIC': 'outline' as const
    };
    
    return (
      <Badge variant={variants[template.visibility]} className="flex items-center gap-1">
        {getVisibilityIcon(template.visibility)}
        {template.visibility_display}
      </Badge>
    );
  };

  const handleCreateTemplate = async () => {
    try {
      // Mock template creation - replace with actual API
      console.log('Creating template:', createTemplateData);
      setShowCreateDialog(false);
      fetchTemplates(); // Refresh the list
    } catch (err) {
      setError('Failed to create template');
    }
  };

  const copyTemplateCode = (code: string) => {
    navigator.clipboard.writeText(code);
    // Add toast notification here
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex justify-between items-start">
        <div>
          <h2 className="text-2xl font-bold tracking-tight">Template Library</h2>
          <p className="text-muted-foreground">
            Browse, create, and share warehouse layout templates
          </p>
        </div>
        
        <Dialog open={showCreateDialog} onOpenChange={setShowCreateDialog}>
          <DialogTrigger asChild>
            <Button className="flex items-center gap-2">
              <Plus className="h-4 w-4" />
              Create Template
            </Button>
          </DialogTrigger>
          <DialogContent className="max-w-md">
            <DialogHeader>
              <DialogTitle>Create New Template</DialogTitle>
              <DialogDescription>
                Save your current warehouse configuration as a reusable template
              </DialogDescription>
            </DialogHeader>
            
            <div className="space-y-4">
              <div className="space-y-2">
                <Label htmlFor="template-name">Template Name</Label>
                <Input
                  id="template-name"
                  placeholder="My Warehouse Template"
                  value={createTemplateData.name}
                  onChange={(e) => setCreateTemplateData(prev => ({
                    ...prev,
                    name: e.target.value
                  }))}
                />
              </div>
              
              <div className="space-y-2">
                <Label htmlFor="template-description">Description</Label>
                <Textarea
                  id="template-description"
                  placeholder="Describe your warehouse layout..."
                  value={createTemplateData.description}
                  onChange={(e) => setCreateTemplateData(prev => ({
                    ...prev,
                    description: e.target.value
                  }))}
                />
              </div>
              
              <div className="space-y-2">
                <Label htmlFor="template-visibility">Privacy Setting</Label>
                <Select
                  value={createTemplateData.visibility}
                  onValueChange={(value: 'PRIVATE' | 'COMPANY' | 'PUBLIC') => 
                    setCreateTemplateData(prev => ({ ...prev, visibility: value }))
                  }
                >
                  <SelectTrigger>
                    <SelectValue placeholder="Select visibility" />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="PRIVATE">
                      <div className="flex items-center gap-2">
                        <Lock className="h-4 w-4" />
                        Private - Only you can see this
                      </div>
                    </SelectItem>
                    <SelectItem value="COMPANY">
                      <div className="flex items-center gap-2">
                        <Building className="h-4 w-4" />
                        Company - Your organization only
                      </div>
                    </SelectItem>
                    <SelectItem value="PUBLIC">
                      <div className="flex items-center gap-2">
                        <Globe className="h-4 w-4" />
                        Public - Everyone can see this
                      </div>
                    </SelectItem>
                  </SelectContent>
                </Select>
              </div>
              
              <div className="space-y-2">
                <Label htmlFor="template-category">Category</Label>
                <Select
                  value={createTemplateData.template_category}
                  onValueChange={(value) => 
                    setCreateTemplateData(prev => ({ ...prev, template_category: value }))
                  }
                >
                  <SelectTrigger>
                    <SelectValue placeholder="Select category" />
                  </SelectTrigger>
                  <SelectContent>
                    {categories.map((category) => (
                      <SelectItem key={category.id} value={category.category_name}>
                        {category.display_name}
                      </SelectItem>
                    ))}
                  </SelectContent>
                </Select>
              </div>
              
              <div className="flex justify-end gap-2 pt-4">
                <Button variant="outline" onClick={() => setShowCreateDialog(false)}>
                  Cancel
                </Button>
                <Button onClick={handleCreateTemplate}>
                  Create Template
                </Button>
              </div>
            </div>
          </DialogContent>
        </Dialog>
      </div>

      {/* Filters */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Filter className="h-5 w-5" />
            Filter Templates
          </CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          {/* Scope Tabs */}
          <Tabs value={activeScope} onValueChange={(value: any) => setActiveScope(value)}>
            <TabsList className="grid w-full grid-cols-4">
              <TabsTrigger value="accessible" className="flex items-center gap-2">
                <Eye className="h-4 w-4" />
                Accessible
              </TabsTrigger>
              <TabsTrigger value="my" className="flex items-center gap-2">
                <User className="h-4 w-4" />
                My Templates
              </TabsTrigger>
              <TabsTrigger value="company" className="flex items-center gap-2">
                <Building className="h-4 w-4" />
                Company
              </TabsTrigger>
              <TabsTrigger value="public" className="flex items-center gap-2">
                <Globe className="h-4 w-4" />
                Public
              </TabsTrigger>
            </TabsList>
          </Tabs>
          
          {/* Search and Category */}
          <div className="flex gap-4">
            <div className="flex-1">
              <Input
                placeholder="Search templates..."
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                className="w-full"
              />
            </div>
            <Select value={selectedCategory} onValueChange={setSelectedCategory}>
              <SelectTrigger className="w-48">
                <SelectValue placeholder="All Categories" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="">All Categories</SelectItem>
                {categories.map((category) => (
                  <SelectItem key={category.id} value={category.category_name}>
                    {category.display_name}
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>
          </div>
          
          {/* Featured Toggle */}
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
        </CardContent>
      </Card>

      {/* Templates List */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center justify-between">
            <span>Templates ({templates.length})</span>
            {loading && <Loader2 className="h-4 w-4 animate-spin" />}
          </CardTitle>
        </CardHeader>
        <CardContent>
          {error && (
            <Alert className="mb-4">
              <AlertDescription>{error}</AlertDescription>
            </Alert>
          )}
          
          <div className="rounded-md border">
            <Table>
              <TableHeader>
                <TableRow>
                  <TableHead>Template</TableHead>
                  <TableHead>Privacy</TableHead>
                  <TableHead>Category</TableHead>
                  <TableHead>Rating</TableHead>
                  <TableHead>Usage</TableHead>
                  <TableHead>Creator</TableHead>
                  <TableHead>Actions</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {templates.map((template) => (
                  <TableRow key={template.id}>
                    <TableCell>
                      <div className="space-y-1">
                        <div className="flex items-center gap-2">
                          <span className="font-medium">{template.name}</span>
                          {template.featured && (
                            <Crown className="h-4 w-4 text-yellow-500" />
                          )}
                        </div>
                        <p className="text-sm text-muted-foreground">
                          {template.description}
                        </p>
                        <div className="flex items-center gap-2 text-xs text-muted-foreground">
                          <span>{template.num_aisles}A × {template.racks_per_aisle}R × {template.positions_per_rack}P</span>
                          {template.tags.map((tag, index) => (
                            <Badge key={index} variant="outline" className="text-xs">
                              {tag}
                            </Badge>
                          ))}
                        </div>
                      </div>
                    </TableCell>
                    <TableCell>
                      {getVisibilityBadge(template)}
                    </TableCell>
                    <TableCell>
                      <Badge variant="secondary">
                        {categories.find(c => c.category_name === template.template_category)?.display_name || template.template_category}
                      </Badge>
                    </TableCell>
                    <TableCell>
                      <div className="flex items-center gap-2">
                        <div className="flex items-center gap-1">
                          <Star className="h-4 w-4 text-yellow-500 fill-current" />
                          <span className="text-sm">{template.rating.toFixed(1)}</span>
                        </div>
                        <span className="text-xs text-muted-foreground">
                          ({template.review_count})
                        </span>
                      </div>
                    </TableCell>
                    <TableCell>
                      <div className="text-sm">
                        <div>{template.downloads_count} downloads</div>
                        <div className="text-muted-foreground">{template.usage_count} uses</div>
                      </div>
                    </TableCell>
                    <TableCell>
                      <div className="text-sm">
                        <div className="font-medium">{template.creator_username}</div>
                        {template.creator_organization && (
                          <div className="text-muted-foreground">{template.creator_organization}</div>
                        )}
                      </div>
                    </TableCell>
                    <TableCell>
                      <div className="flex items-center gap-2">
                        <Button size="sm" variant="outline">
                          <Download className="h-4 w-4" />
                        </Button>
                        <Button 
                          size="sm" 
                          variant="outline"
                          onClick={() => copyTemplateCode(template.template_code)}
                        >
                          <Copy className="h-4 w-4" />
                        </Button>
                        {template.creator_username === 'currentuser' && (
                          <Button size="sm" variant="outline">
                            <Settings className="h-4 w-4" />
                          </Button>
                        )}
                      </div>
                    </TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          </div>
          
          {templates.length === 0 && !loading && (
            <div className="flex flex-col items-center justify-center py-12">
              <Building2 className="h-16 w-16 text-muted-foreground mb-4" />
              <h3 className="text-lg font-semibold mb-2">No Templates Found</h3>
              <p className="text-muted-foreground text-center mb-4">
                No templates match your current filters. Try adjusting your search criteria.
              </p>
            </div>
          )}
        </CardContent>
      </Card>
    </div>
  );
}