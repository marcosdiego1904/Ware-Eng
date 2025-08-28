'use client';

import React, { useState, useEffect } from 'react';
import { LocationManager } from '@/components/locations/location-manager';
import { WarehouseSettingsErrorBoundary } from '@/components/error-boundary';
import { useAuth } from '@/lib/auth-context';
import { Loader2 } from 'lucide-react';

export function WarehouseSettingsView() {
  const { user } = useAuth();
  const [userWarehouseId, setUserWarehouseId] = useState<string>('DEFAULT');
  const [warehouseLoading, setWarehouseLoading] = useState(true);
  const [warehouseInfo, setWarehouseInfo] = useState<any>(null);
  
  // Fetch user's primary warehouse dynamically
  useEffect(() => {
    const fetchUserWarehouse = async () => {
      if (!user) {
        setUserWarehouseId('DEFAULT');
        setWarehouseLoading(false);
        return;
      }

      try {
        setWarehouseLoading(true);
        const { api } = await import('@/lib/api');
        const response = await api.get('/user/warehouse');
        
        if (response.data.success && response.data.primary_warehouse) {
          const primaryWarehouse = response.data.primary_warehouse;
          setUserWarehouseId(primaryWarehouse);
          setWarehouseInfo(response.data);
          
          console.log('🏢 Dynamic warehouse detected:', {
            user: user.username,
            warehouse: primaryWarehouse,
            name: response.data.primary_warehouse_name,
            specialAreas: response.data.special_areas_count,
            method: response.data.detection_method
          });
        } else {
          // Fallback to username-based warehouse ID
          const fallbackWarehouse = `USER_${user.username.toUpperCase()}`;
          setUserWarehouseId(fallbackWarehouse);
          console.log('⚠️ No dynamic warehouse found, using fallback:', fallbackWarehouse);
        }
      } catch (error) {
        console.error('❌ Failed to fetch user warehouse:', error);
        // Final fallback to DEFAULT
        setUserWarehouseId('DEFAULT');
      } finally {
        setWarehouseLoading(false);
      }
    };

    fetchUserWarehouse();
  }, [user]);

  console.log('🔑 WarehouseSettingsView - User:', user?.username, 'Warehouse ID:', userWarehouseId);

  if (warehouseLoading) {
    return (
      <div className="p-6 flex items-center justify-center h-64">
        <div className="flex items-center gap-3">
          <Loader2 className="h-6 w-6 animate-spin" />
          <span>Detecting your warehouse...</span>
        </div>
      </div>
    );
  }
  
  return (
    <div className="p-6">
      {warehouseInfo && warehouseInfo.detection_method !== 'fallback_default' && (
        <div className="mb-4 p-3 bg-blue-50 border border-blue-200 rounded-md">
          <p className="text-sm text-blue-700">
            📋 Using warehouse: <strong>{warehouseInfo.primary_warehouse_name}</strong> 
            ({warehouseInfo.special_areas_count} special areas configured)
          </p>
        </div>
      )}
      
      <WarehouseSettingsErrorBoundary>
        <LocationManager warehouseId={userWarehouseId} />
      </WarehouseSettingsErrorBoundary>
    </div>
  );
}