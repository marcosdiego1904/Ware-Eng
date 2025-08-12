'use client';

import React from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { 
  Table, 
  TableBody, 
  TableCell, 
  TableHead, 
  TableHeader, 
  TableRow 
} from '@/components/ui/table';
import { Skeleton } from '@/components/ui/skeleton';
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuTrigger,
} from '@/components/ui/dropdown-menu';
import { Location, LocationsPagination } from '@/lib/location-store';
import { 
  MoreHorizontal, 
  Edit, 
  Trash2, 
  MapPin, 
  Package,
  ChevronLeft,
  ChevronRight,
  Loader2
} from 'lucide-react';

interface LocationListProps {
  locations: Location[];
  loading: boolean;
  pagination: LocationsPagination | null;
  onEdit: (location: Location) => void;
  onDelete?: (location: Location) => void;
  onPageChange: (page: number) => void;
}

export function LocationList({ 
  locations, 
  loading, 
  pagination, 
  onEdit, 
  onDelete, 
  onPageChange 
}: LocationListProps) {
  
  // Get location type badge variant
  const getLocationTypeBadge = (type: string) => {
    switch (type) {
      case 'STORAGE':
        return <Badge variant="default">{type}</Badge>;
      case 'RECEIVING':
        return <Badge variant="secondary">{type}</Badge>;
      case 'STAGING':
        return <Badge variant="outline">{type}</Badge>;
      case 'DOCK':
        return <Badge variant="destructive">{type}</Badge>;
      default:
        return <Badge variant="outline">{type}</Badge>;
    }
  };

  // Get capacity indicator
  const getCapacityIndicator = (capacity: number, palletCapacity: number) => {
    const effectiveCapacity = palletCapacity || capacity;
    if (effectiveCapacity >= 10) {
      return <Badge variant="destructive">{effectiveCapacity}</Badge>;
    } else if (effectiveCapacity >= 5) {
      return <Badge variant="default">{effectiveCapacity}</Badge>;
    } else if (effectiveCapacity >= 2) {
      return <Badge variant="secondary">{effectiveCapacity}</Badge>;
    } else {
      return <Badge variant="outline">{effectiveCapacity}</Badge>;
    }
  };

  // Format location display
  const formatLocationDisplay = (location: Location) => {
    if (location.is_storage_location) {
      return (
        <div className="space-y-1 min-w-0">
          <div className="font-medium font-mono text-sm truncate" title={location.code}>
            {location.code}
          </div>
          <div className="text-xs text-muted-foreground truncate" title={location.full_address}>
            {location.full_address}
          </div>
        </div>
      );
    } else {
      return (
        <div className="space-y-1 min-w-0">
          <div className="font-medium font-mono text-sm truncate" title={location.code}>
            {location.code}
          </div>
          <div className="text-xs text-muted-foreground">
            Special Area
          </div>
        </div>
      );
    }
  };

  if (loading && locations.length === 0) {
    return (
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Loader2 className="h-5 w-5 animate-spin" />
            Loading Locations...
          </CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          {Array.from({ length: 10 }).map((_, i) => (
            <div key={i} className="flex items-center space-x-4">
              <Skeleton className="h-12 w-12 rounded" />
              <div className="space-y-2 flex-1">
                <Skeleton className="h-4 w-[200px]" />
                <Skeleton className="h-4 w-[150px]" />
              </div>
              <Skeleton className="h-8 w-20" />
              <Skeleton className="h-8 w-8" />
            </div>
          ))}
        </CardContent>
      </Card>
    );
  }

  if (locations.length === 0) {
    return (
      <Card>
        <CardContent className="flex flex-col items-center justify-center py-12">
          <Package className="h-16 w-16 text-muted-foreground mb-4" />
          <h3 className="text-lg font-semibold mb-2">No Locations Found</h3>
          <p className="text-muted-foreground text-center mb-4">
            No locations match your current filters. Try adjusting your search criteria.
          </p>
        </CardContent>
      </Card>
    );
  }

  return (
    <Card>
      <CardHeader>
        <CardTitle className="flex items-center justify-between">
          <div className="flex items-center gap-2">
            <MapPin className="h-5 w-5" />
            Warehouse Locations
          </div>
          {loading && (
            <Loader2 className="h-4 w-4 animate-spin" />
          )}
        </CardTitle>
      </CardHeader>
      <CardContent>
        <div className="rounded-md border overflow-x-auto">
          <Table className="min-w-full">
            <TableHeader>
              <TableRow>
                <TableHead className="min-w-[180px]">Location</TableHead>
                <TableHead className="min-w-[100px]">Type</TableHead>
                <TableHead className="min-w-[80px]">Zone</TableHead>
                <TableHead className="min-w-[80px]">Capacity</TableHead>
                <TableHead className="min-w-[120px]">Structure</TableHead>
                <TableHead className="min-w-[80px]">Status</TableHead>
                <TableHead className="w-[50px]"></TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {locations.map((location) => (
                <TableRow key={location.id}>
                  <TableCell>
                    {formatLocationDisplay(location)}
                  </TableCell>
                  <TableCell>
                    {getLocationTypeBadge(location.location_type)}
                  </TableCell>
                  <TableCell>
                    <Badge variant="outline">{location.zone}</Badge>
                  </TableCell>
                  <TableCell>
                    {getCapacityIndicator(location.capacity, location.pallet_capacity)}
                  </TableCell>
                  <TableCell>
                    {location.is_storage_location ? (
                      <div className="text-sm text-muted-foreground">
                        A{location.aisle_number}/R{location.rack_number}/P{location.position_number}{location.level}
                      </div>
                    ) : (
                      <div className="text-sm text-muted-foreground">
                        —
                      </div>
                    )}
                  </TableCell>
                  <TableCell>
                    <Badge 
                      variant={location.is_active ? "default" : "secondary"}
                    >
                      {location.is_active ? "Active" : "Inactive"}
                    </Badge>
                  </TableCell>
                  <TableCell>
                    <DropdownMenu>
                      <DropdownMenuTrigger asChild>
                        <Button variant="ghost" className="h-8 w-8 p-0">
                          <MoreHorizontal className="h-4 w-4" />
                        </Button>
                      </DropdownMenuTrigger>
                      <DropdownMenuContent align="end">
                        <DropdownMenuItem onClick={() => onEdit(location)}>
                          <Edit className="mr-2 h-4 w-4" />
                          Edit
                        </DropdownMenuItem>
                        {onDelete && (
                          <DropdownMenuItem 
                            onClick={() => onDelete(location)}
                            className="text-destructive"
                          >
                            <Trash2 className="mr-2 h-4 w-4" />
                            Delete
                          </DropdownMenuItem>
                        )}
                      </DropdownMenuContent>
                    </DropdownMenu>
                  </TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        </div>

        {/* Pagination */}
        {pagination && pagination.pages > 1 && (
          <div className="flex items-center justify-between space-x-2 py-4">
            <div className="text-sm text-muted-foreground">
              Showing {((pagination.page - 1) * pagination.per_page) + 1} to{' '}
              {Math.min(pagination.page * pagination.per_page, pagination.total)} of{' '}
              {pagination.total} locations
            </div>
            
            <div className="flex items-center space-x-2">
              <Button
                variant="outline"
                size="sm"
                onClick={() => onPageChange(pagination.page - 1)}
                disabled={!pagination.has_prev}
              >
                <ChevronLeft className="h-4 w-4" />
              </Button>
              
              <div className="flex items-center space-x-1">
                {Array.from({ length: Math.min(5, pagination.pages) }, (_, i) => {
                  let pageNum: number;
                  
                  if (pagination.pages <= 5) {
                    pageNum = i + 1;
                  } else {
                    const start = Math.max(1, pagination.page - 2);
                    const end = Math.min(pagination.pages, start + 4);
                    pageNum = start + i;
                    
                    if (pageNum > end) return null;
                  }
                  
                  return (
                    <Button
                      key={pageNum}
                      variant={pageNum === pagination.page ? "default" : "outline"}
                      size="sm"
                      onClick={() => onPageChange(pageNum)}
                      className="w-8 h-8 p-0"
                    >
                      {pageNum}
                    </Button>
                  );
                })}
              </div>
              
              <Button
                variant="outline"
                size="sm"
                onClick={() => onPageChange(pagination.page + 1)}
                disabled={!pagination.has_next}
              >
                <ChevronRight className="h-4 w-4" />
              </Button>
            </div>
          </div>
        )}
      </CardContent>
    </Card>
  );
}