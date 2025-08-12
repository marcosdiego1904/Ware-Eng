'use client';

import React from 'react';
import { LocationManager } from '@/components/locations/location-manager';
import { WarehouseSettingsErrorBoundary } from '@/components/error-boundary';
import { useAuth } from '@/lib/auth-context';

export function WarehouseSettingsView() {
  const { user } = useAuth();
  
  // Generate user-specific warehouse ID to prevent data contamination
  // Use username-based warehouse ID instead of shared "DEFAULT"
  const userWarehouseId = user?.username ? `USER_${user.username.toUpperCase()}` : 'DEFAULT';
  
  console.log('🔑 WarehouseSettingsView - User:', user?.username, 'Warehouse ID:', userWarehouseId);
  
  return (
    <div className="p-6">
      <WarehouseSettingsErrorBoundary>
        <LocationManager warehouseId={userWarehouseId} />
      </WarehouseSettingsErrorBoundary>
    </div>
  );
}