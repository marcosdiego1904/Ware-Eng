'use client';

import React from 'react';
import { cn } from '@/lib/utils';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Skeleton } from '@/components/ui/skeleton';

// Basic skeleton wrapper
export function SkeletonWrapper({ 
  children, 
  isLoading, 
  height = 'h-4',
  width = 'w-full',
  className = '' 
}: {
  children: React.ReactNode;
  isLoading: boolean;
  height?: string;
  width?: string;
  className?: string;
}) {
  if (isLoading) {
    return <Skeleton className={cn(height, width, className)} />;
  }
  return <>{children}</>;
}

// Skeleton for warehouse overview cards
export function WarehouseOverviewSkeleton() {
  return (
    <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
      {Array.from({ length: 4 }).map((_, index) => (
        <Card key={index}>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <Skeleton className="h-4 w-20" />
            <Skeleton className="h-4 w-4 rounded-full" />
          </CardHeader>
          <CardContent>
            <Skeleton className="h-8 w-16 mb-2" />
            <Skeleton className="h-3 w-full" />
          </CardContent>
        </Card>
      ))}
    </div>
  );
}

// Skeleton for location list
export function LocationListSkeleton({ count = 5 }: { count?: number }) {
  return (
    <div className="space-y-3">
      {Array.from({ length: count }).map((_, index) => (
        <div key={index} className="flex items-center justify-between p-4 border rounded-lg">
          <div className="flex items-center space-x-4">
            <Skeleton className="h-10 w-10 rounded-full" />
            <div className="space-y-2">
              <Skeleton className="h-4 w-20" />
              <Skeleton className="h-3 w-32" />
            </div>
          </div>
          <div className="flex items-center space-x-2">
            <Skeleton className="h-6 w-16 rounded-full" />
            <Skeleton className="h-8 w-8" />
            <Skeleton className="h-8 w-8" />
          </div>
        </div>
      ))}
    </div>
  );
}

// Skeleton for location form
export function LocationFormSkeleton() {
  return (
    <div className="space-y-6">
      <div className="grid grid-cols-2 gap-4">
        <div className="space-y-2">
          <Skeleton className="h-4 w-24" />
          <Skeleton className="h-10 w-full" />
        </div>
        <div className="space-y-2">
          <Skeleton className="h-4 w-20" />
          <Skeleton className="h-10 w-full" />
        </div>
      </div>
      
      <div className="grid grid-cols-2 gap-4">
        <div className="space-y-2">
          <Skeleton className="h-4 w-16" />
          <Skeleton className="h-10 w-full" />
        </div>
        <div className="space-y-2">
          <Skeleton className="h-4 w-28" />
          <Skeleton className="h-10 w-full" />
        </div>
      </div>
      
      <div className="space-y-2">
        <Skeleton className="h-4 w-32" />
        <Skeleton className="h-20 w-full" />
      </div>
      
      <div className="flex justify-end gap-2">
        <Skeleton className="h-10 w-20" />
        <Skeleton className="h-10 w-24" />
      </div>
    </div>
  );
}

// Skeleton for template cards
export function TemplateCardSkeleton({ count = 6 }: { count?: number }) {
  return (
    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
      {Array.from({ length: count }).map((_, index) => (
        <Card key={index}>
          <CardHeader>
            <div className="flex justify-between items-start">
              <div className="space-y-2">
                <Skeleton className="h-5 w-32" />
                <Skeleton className="h-3 w-24" />
              </div>
              <Skeleton className="h-6 w-16 rounded-full" />
            </div>
          </CardHeader>
          <CardContent>
            <div className="space-y-3">
              <div className="grid grid-cols-2 gap-2 text-sm">
                <div className="space-y-1">
                  <Skeleton className="h-3 w-12" />
                  <Skeleton className="h-4 w-8" />
                </div>
                <div className="space-y-1">
                  <Skeleton className="h-3 w-16" />
                  <Skeleton className="h-4 w-10" />
                </div>
              </div>
              
              <div className="space-y-2">
                <Skeleton className="h-3 w-20" />
                <div className="grid grid-cols-3 gap-1">
                  <Skeleton className="h-6 w-full" />
                  <Skeleton className="h-6 w-full" />
                  <Skeleton className="h-6 w-full" />
                </div>
              </div>
              
              <div className="flex justify-between items-center pt-2">
                <Skeleton className="h-3 w-16" />
                <div className="flex gap-1">
                  <Skeleton className="h-8 w-8" />
                  <Skeleton className="h-8 w-8" />
                  <Skeleton className="h-8 w-8" />
                </div>
              </div>
            </div>
          </CardContent>
        </Card>
      ))}
    </div>
  );
}

// Skeleton for warehouse settings form
export function WarehouseSettingsFormSkeleton() {
  return (
    <Card>
      <CardHeader>
        <div className="flex justify-between items-start">
          <div className="space-y-2">
            <Skeleton className="h-6 w-48" />
            <Skeleton className="h-4 w-64" />
          </div>
          <Skeleton className="h-9 w-32" />
        </div>
      </CardHeader>
      <CardContent className="space-y-4">
        <div className="grid grid-cols-2 gap-4">
          {Array.from({ length: 6 }).map((_, index) => (
            <div key={index} className="space-y-2">
              <Skeleton className="h-4 w-24" />
              <Skeleton className="h-10 w-full" />
            </div>
          ))}
        </div>
        
        <div className="flex items-center space-x-2">
          <Skeleton className="h-5 w-5 rounded" />
          <Skeleton className="h-4 w-40" />
        </div>
        
        <div className="flex justify-end gap-2 pt-4 border-t">
          <Skeleton className="h-10 w-20" />
          <Skeleton className="h-10 w-24" />
        </div>
      </CardContent>
    </Card>
  );
}

// Skeleton for data table
export function DataTableSkeleton({ 
  rows = 5, 
  columns = 4 
}: { 
  rows?: number; 
  columns?: number; 
}) {
  return (
    <div className="space-y-3">
      {/* Header */}
      <div className="flex items-center space-x-4 pb-2 border-b">
        {Array.from({ length: columns }).map((_, index) => (
          <Skeleton key={index} className="h-4 w-20 flex-1" />
        ))}
      </div>
      
      {/* Rows */}
      {Array.from({ length: rows }).map((_, rowIndex) => (
        <div key={rowIndex} className="flex items-center space-x-4 py-2">
          {Array.from({ length: columns }).map((_, colIndex) => (
            <Skeleton key={colIndex} className="h-4 flex-1" />
          ))}
        </div>
      ))}
    </div>
  );
}

// Skeleton for dashboard stats
export function DashboardStatsSkeleton() {
  return (
    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
      {Array.from({ length: 4 }).map((_, index) => (
        <Card key={index}>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <Skeleton className="h-4 w-20" />
            <Skeleton className="h-4 w-4 rounded-full" />
          </CardHeader>
          <CardContent>
            <Skeleton className="h-8 w-16 mb-2" />
            <Skeleton className="h-3 w-24" />
          </CardContent>
        </Card>
      ))}
    </div>
  );
}

// Skeleton for navigation breadcrumbs
export function BreadcrumbSkeleton() {
  return (
    <div className="flex items-center space-x-2">
      <Skeleton className="h-4 w-16" />
      <Skeleton className="h-4 w-1" />
      <Skeleton className="h-4 w-20" />
      <Skeleton className="h-4 w-1" />
      <Skeleton className="h-4 w-24" />
    </div>
  );
}

// Generic content skeleton
export function ContentSkeleton({ 
  lines = 3, 
  showImage = false 
}: { 
  lines?: number; 
  showImage?: boolean; 
}) {
  return (
    <div className="space-y-3">
      {showImage && <Skeleton className="h-48 w-full rounded-lg" />}
      <div className="space-y-2">
        {Array.from({ length: lines }).map((_, index) => (
          <Skeleton 
            key={index} 
            className={cn(
              "h-4",
              index === lines - 1 ? "w-3/4" : "w-full"
            )} 
          />
        ))}
      </div>
    </div>
  );
}

// Skeleton for tab content
export function TabContentSkeleton() {
  return (
    <div className="space-y-6">
      <div className="space-y-4">
        <Skeleton className="h-6 w-32" />
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <ContentSkeleton lines={3} />
          <ContentSkeleton lines={3} />
        </div>
      </div>
      
      <div className="space-y-4">
        <Skeleton className="h-6 w-40" />
        <DataTableSkeleton rows={3} columns={3} />
      </div>
    </div>
  );
}

// Skeleton for modal content
export function ModalSkeleton() {
  return (
    <div className="space-y-6 p-6">
      <div className="space-y-2">
        <Skeleton className="h-6 w-48" />
        <Skeleton className="h-4 w-64" />
      </div>
      
      <div className="space-y-4">
        <div className="grid grid-cols-2 gap-4">
          <div className="space-y-2">
            <Skeleton className="h-4 w-20" />
            <Skeleton className="h-10 w-full" />
          </div>
          <div className="space-y-2">
            <Skeleton className="h-4 w-24" />
            <Skeleton className="h-10 w-full" />
          </div>
        </div>
        
        <div className="space-y-2">
          <Skeleton className="h-4 w-28" />
          <Skeleton className="h-20 w-full" />
        </div>
      </div>
      
      <div className="flex justify-end gap-2">
        <Skeleton className="h-10 w-20" />
        <Skeleton className="h-10 w-24" />
      </div>
    </div>
  );
}

// Responsive skeleton that adapts to screen size
export function ResponsiveSkeleton({ 
  mobile, 
  desktop, 
  className = "" 
}: {
  mobile: React.ReactNode;
  desktop: React.ReactNode;
  className?: string;
}) {
  return (
    <div className={className}>
      <div className="md:hidden">{mobile}</div>
      <div className="hidden md:block">{desktop}</div>
    </div>
  );
}