'use client';

import React from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { 
  Building2, 
  Grid3X3, 
  Package, 
  Users,
  Crown,
  Star,
  Download,
  Eye,
  Copy,
  Lock,
  Globe,
  Building,
  CheckCircle
} from 'lucide-react';

interface TemplateData {
  id?: number;
  name: string;
  description?: string;
  category?: string;
  visibility?: 'PRIVATE' | 'COMPANY' | 'PUBLIC';
  num_aisles: number;
  racks_per_aisle: number;
  positions_per_rack: number;
  levels_per_position: number;
  default_pallet_capacity?: number;
  tags?: string[];
  featured?: boolean;
  rating?: number;
  usage_count?: number;
  downloads_count?: number;
  creator_username?: string;
  creator_organization?: string;
  review_count?: number;
  template_code?: string;
  created_at?: string;
  is_applied?: boolean;
  applied_warehouse_id?: string;
}

interface TemplatePreviewProps {
  template: TemplateData;
  variant?: 'card' | 'compact' | 'detailed';
  onApply?: (template: TemplateData) => void;
  onView?: (template: TemplateData) => void;
  onCopyCode?: (code: string) => void;
  className?: string;
}

export function TemplatePreview({ 
  template, 
  variant = 'card',
  onApply,
  onView,
  onCopyCode,
  className = '' 
}: TemplatePreviewProps) {
  
  // Calculate totals
  const storageLocations = template.num_aisles * template.racks_per_aisle * 
                          template.positions_per_rack * template.levels_per_position;
  const storageCapacity = storageLocations * (template.default_pallet_capacity || 1);

  const getVisibilityIcon = (visibility?: string) => {
    switch (visibility) {
      case 'PRIVATE': return <Lock className="h-3 w-3 text-gray-600" />;
      case 'COMPANY': return <Building className="h-3 w-3 text-blue-600" />;
      case 'PUBLIC': return <Globe className="h-3 w-3 text-green-600" />;
      default: return <Lock className="h-3 w-3 text-gray-600" />;
    }
  };

  const getVisibilityLabel = (visibility?: string) => {
    switch (visibility) {
      case 'PRIVATE': return 'Private';
      case 'COMPANY': return 'Company';
      case 'PUBLIC': return 'Public';
      default: return 'Private';
    }
  };

  // Render warehouse layout visualization
  const renderWarehouseLayout = () => {
    const maxAisles = 8; // Limit visual representation
    const displayAisles = Math.min(template.num_aisles, maxAisles);
    const maxRacks = 4;
    const displayRacks = Math.min(template.racks_per_aisle, maxRacks);

    return (
      <div className="w-full h-32 bg-muted/30 rounded-md p-2 flex items-center justify-center relative overflow-hidden">
        <div className="flex gap-1">
          {Array.from({ length: displayAisles }).map((_, aisleIndex) => (
            <div key={aisleIndex} className="flex flex-col gap-1">
              {Array.from({ length: displayRacks }).map((_, rackIndex) => (
                <div
                  key={rackIndex}
                  className="w-3 h-6 bg-primary/60 rounded-sm"
                  style={{
                    backgroundColor: `hsl(${210 + (aisleIndex * 20)}, 60%, ${50 + (rackIndex * 10)}%)`
                  }}
                />
              ))}
            </div>
          ))}
        </div>
        
        {/* Overflow indicator */}
        {template.num_aisles > maxAisles && (
          <div className="absolute right-2 top-1/2 -translate-y-1/2 text-xs text-muted-foreground">
            +{template.num_aisles - maxAisles} more
          </div>
        )}

        {/* Layout info overlay */}
        <div className="absolute bottom-1 right-1 text-xs font-mono bg-background/80 px-1 rounded">
          {template.num_aisles}A×{template.racks_per_aisle}R
        </div>
      </div>
    );
  };

  if (variant === 'compact') {
    return (
      <div className={`flex items-center gap-3 p-3 border rounded-lg hover:bg-muted/50 transition-colors ${className}`}>
        <div className="w-16 h-12 bg-muted rounded flex items-center justify-center">
          <Grid3X3 className="h-4 w-4 text-muted-foreground" />
        </div>
        <div className="flex-1 min-w-0">
          <div className="flex items-center gap-2">
            <h4 className="font-medium truncate">{template.name}</h4>
            {template.featured && <Crown className="h-3 w-3 text-yellow-500" />}
            {template.is_applied && (
              <div className="flex items-center gap-1 text-green-600" title="Template is currently applied">
                <CheckCircle className="h-3 w-3" />
                <span className="text-xs">Applied</span>
              </div>
            )}
            {template.visibility && (
              <div className="flex items-center gap-1">
                {getVisibilityIcon(template.visibility)}
              </div>
            )}
          </div>
          <div className="text-xs text-muted-foreground">
            {storageLocations.toLocaleString()} locations • {storageCapacity.toLocaleString()} capacity
          </div>
          {template.creator_username && (
            <div className="text-xs text-muted-foreground">by {template.creator_username}</div>
          )}
        </div>
        {template.rating !== undefined && template.rating > 0 && (
          <div className="flex items-center gap-1">
            <Star className="h-3 w-3 text-yellow-500 fill-current" />
            <span className="text-xs">{template.rating.toFixed(1)}</span>
          </div>
        )}
        <div className="flex items-center gap-1">
          {onView && (
            <Button variant="ghost" size="sm" onClick={() => onView(template)}>
              <Eye className="h-3 w-3" />
            </Button>
          )}
          {onApply && (
            <Button variant="outline" size="sm" onClick={() => onApply(template)}>
              <Download className="h-3 w-3" />
            </Button>
          )}
        </div>
      </div>
    );
  }

  if (variant === 'detailed') {
    return (
      <Card className={`overflow-hidden ${className}`}>
        <CardHeader className="pb-4">
          <div className="flex items-start justify-between">
            <div className="space-y-1">
              <div className="flex items-center gap-2">
                <CardTitle className="text-lg">{template.name}</CardTitle>
                {template.featured && <Crown className="h-4 w-4 text-yellow-500" />}
                {template.is_applied && (
                  <Badge variant="secondary" className="flex items-center gap-1 bg-green-100 text-green-700">
                    <CheckCircle className="h-3 w-3" />
                    Applied
                  </Badge>
                )}
              </div>
              {template.description && (
                <CardDescription>{template.description}</CardDescription>
              )}
            </div>
            {template.visibility && (
              <Badge variant="outline" className="flex items-center gap-1">
                {getVisibilityIcon(template.visibility)}
                {getVisibilityLabel(template.visibility)}
              </Badge>
            )}
          </div>
          
          {/* Tags and Category */}
          <div className="flex flex-wrap gap-2">
            {template.category && (
              <Badge variant="secondary">{template.category}</Badge>
            )}
            {template.tags?.map((tag, index) => (
              <Badge key={index} variant="outline" className="text-xs">
                {tag}
              </Badge>
            ))}
          </div>
        </CardHeader>
        
        <CardContent className="space-y-4">
          {/* Visual Layout */}
          <div className="space-y-2">
            <div className="flex items-center gap-2 text-sm font-medium">
              <Building2 className="h-4 w-4" />
              Warehouse Layout
            </div>
            {renderWarehouseLayout()}
          </div>

          {/* Structure Details */}
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4 text-sm">
            <div className="text-center p-2 bg-muted/50 rounded">
              <div className="font-semibold">{template.num_aisles}</div>
              <div className="text-xs text-muted-foreground">Aisles</div>
            </div>
            <div className="text-center p-2 bg-muted/50 rounded">
              <div className="font-semibold">{template.racks_per_aisle}</div>
              <div className="text-xs text-muted-foreground">Racks/Aisle</div>
            </div>
            <div className="text-center p-2 bg-muted/50 rounded">
              <div className="font-semibold">{template.positions_per_rack}</div>
              <div className="text-xs text-muted-foreground">Positions/Rack</div>
            </div>
            <div className="text-center p-2 bg-muted/50 rounded">
              <div className="font-semibold">{template.levels_per_position}</div>
              <div className="text-xs text-muted-foreground">Levels/Position</div>
            </div>
          </div>

          {/* Capacity Summary */}
          <div className="grid grid-cols-2 gap-4 p-3 bg-primary/5 rounded-lg">
            <div>
              <div className="text-lg font-bold text-primary">{storageLocations.toLocaleString()}</div>
              <div className="text-sm text-muted-foreground">Storage Locations</div>
            </div>
            <div>
              <div className="text-lg font-bold text-primary">{storageCapacity.toLocaleString()}</div>
              <div className="text-sm text-muted-foreground">Pallet Capacity</div>
            </div>
          </div>

          {/* Stats and Creator Info */}
          <div className="flex items-center justify-between text-sm">
            <div className="space-y-1">
              {template.creator_username && (
                <div className="flex items-center gap-1 text-muted-foreground">
                  <Users className="h-3 w-3" />
                  {template.creator_username}
                  {template.creator_organization && ` • ${template.creator_organization}`}
                </div>
              )}
              {template.created_at && (
                <div className="text-xs text-muted-foreground">
                  Created {new Date(template.created_at).toLocaleDateString()}
                </div>
              )}
            </div>
            
            <div className="flex items-center gap-4 text-sm">
              {template.rating !== undefined && template.rating > 0 && (
                <div className="flex items-center gap-1">
                  <Star className="h-3 w-3 text-yellow-500 fill-current" />
                  <span>{template.rating.toFixed(1)}</span>
                  <span className="text-muted-foreground">({template.review_count || 0})</span>
                </div>
              )}
              {template.downloads_count !== undefined && (
                <div className="text-muted-foreground">
                  {template.downloads_count} downloads
                </div>
              )}
            </div>
          </div>

          {/* Actions */}
          <div className="flex items-center gap-2 pt-2">
            {onView && (
              <Button variant="outline" size="sm" onClick={() => onView(template)}>
                <Eye className="h-4 w-4 mr-2" />
                View Details
              </Button>
            )}
            {onApply && (
              <Button size="sm" onClick={() => onApply(template)}>
                <Download className="h-4 w-4 mr-2" />
                Apply Template
              </Button>
            )}
            {template.template_code && onCopyCode && (
              <Button 
                variant="ghost" 
                size="sm" 
                onClick={() => onCopyCode(template.template_code!)}
              >
                <Copy className="h-4 w-4 mr-2" />
                {template.template_code}
              </Button>
            )}
          </div>
        </CardContent>
      </Card>
    );
  }

  // Default 'card' variant
  return (
    <Card className={`overflow-hidden hover:shadow-md transition-shadow cursor-pointer ${className}`}>
      <CardContent className="p-4">
        <div className="space-y-3">
          {/* Header */}
          <div className="flex items-start justify-between">
            <div className="space-y-1 min-w-0 flex-1">
              <div className="flex items-center gap-2">
                <h4 className="font-medium truncate">{template.name}</h4>
                {template.featured && <Crown className="h-3 w-3 text-yellow-500 flex-shrink-0" />}
                {template.is_applied && (
                  <div className="flex items-center gap-1 text-green-600" title="Template is currently applied">
                    <CheckCircle className="h-3 w-3" />
                    <span className="text-xs font-medium">Applied</span>
                  </div>
                )}
              </div>
              {template.description && (
                <p className="text-sm text-muted-foreground line-clamp-2">
                  {template.description}
                </p>
              )}
            </div>
            {template.visibility && (
              <Badge variant="outline" className="flex items-center gap-1 ml-2 flex-shrink-0">
                {getVisibilityIcon(template.visibility)}
              </Badge>
            )}
          </div>

          {/* Visual Layout Preview */}
          {renderWarehouseLayout()}

          {/* Structure Info */}
          <div className="flex justify-between text-sm">
            <div className="text-muted-foreground">
              {template.num_aisles}A × {template.racks_per_aisle}R × {template.positions_per_rack}P
            </div>
            <div className="font-medium">
              {storageLocations.toLocaleString()} locations
            </div>
          </div>

          {/* Stats */}
          <div className="flex items-center justify-between text-sm">
            <div className="flex items-center gap-3">
              {template.rating !== undefined && template.rating > 0 && (
                <div className="flex items-center gap-1">
                  <Star className="h-3 w-3 text-yellow-500 fill-current" />
                  <span>{template.rating.toFixed(1)}</span>
                </div>
              )}
              {template.downloads_count !== undefined && (
                <div className="text-muted-foreground">
                  {template.downloads_count} uses
                </div>
              )}
            </div>
            {template.creator_username && (
              <div className="text-muted-foreground truncate">
                by {template.creator_username}
              </div>
            )}
          </div>

          {/* Tags */}
          {template.tags && template.tags.length > 0 && (
            <div className="flex flex-wrap gap-1">
              {template.tags.slice(0, 3).map((tag, index) => (
                <Badge key={index} variant="outline" className="text-xs">
                  {tag}
                </Badge>
              ))}
              {template.tags.length > 3 && (
                <Badge variant="outline" className="text-xs">
                  +{template.tags.length - 3} more
                </Badge>
              )}
            </div>
          )}

          {/* Actions */}
          <div className="flex items-center gap-2">
            {onView && (
              <Button variant="ghost" size="sm" onClick={() => onView(template)} className="flex-1">
                <Eye className="h-3 w-3 mr-1" />
                View
              </Button>
            )}
            {onApply && (
              <Button size="sm" onClick={() => onApply(template)} className="flex-1">
                <Download className="h-3 w-3 mr-1" />
                Apply
              </Button>
            )}
          </div>
        </div>
      </CardContent>
    </Card>
  );
}

// Template Grid Component for displaying multiple templates
interface TemplateGridProps {
  templates: TemplateData[];
  variant?: 'card' | 'compact' | 'detailed';
  onApply?: (template: TemplateData) => void;
  onView?: (template: TemplateData) => void;
  onCopyCode?: (code: string) => void;
  emptyMessage?: string;
  className?: string;
}

export function TemplateGrid({ 
  templates, 
  variant = 'card',
  onApply,
  onView,
  onCopyCode,
  emptyMessage = 'No templates found',
  className = '' 
}: TemplateGridProps) {
  if (templates.length === 0) {
    return (
      <div className={`text-center py-12 ${className}`}>
        <Building2 className="h-16 w-16 mx-auto mb-4 text-muted-foreground opacity-50" />
        <h3 className="text-lg font-semibold mb-2">No Templates Found</h3>
        <p className="text-muted-foreground">{emptyMessage}</p>
      </div>
    );
  }

  if (variant === 'compact') {
    return (
      <div className={`space-y-2 ${className}`}>
        {templates.map((template) => (
          <TemplatePreview
            key={template.id || template.name}
            template={template}
            variant="compact"
            onApply={onApply}
            onView={onView}
            onCopyCode={onCopyCode}
          />
        ))}
      </div>
    );
  }

  return (
    <div className={`grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4 ${className}`}>
      {templates.map((template) => (
        <TemplatePreview
          key={template.id || template.name}
          template={template}
          variant={variant}
          onApply={onApply}
          onView={onView}
          onCopyCode={onCopyCode}
        />
      ))}
    </div>
  );
}