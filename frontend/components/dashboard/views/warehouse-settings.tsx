'use client';

import React from 'react';
import { LocationManager } from '@/components/locations/location-manager';

export function WarehouseSettingsView() {
  return (
    <div className="p-6">
      <LocationManager warehouseId="DEFAULT" />
    </div>
  );
}