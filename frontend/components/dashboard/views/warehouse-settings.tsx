'use client';

import React, { useState, useEffect } from 'react';
import { LocationManager } from '@/components/locations/location-manager';
import { WarehouseSettingsErrorBoundary } from '@/components/error-boundary';
import { useAuth } from '@/lib/auth-context';
import { userPreferencesApi } from '@/lib/api';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Checkbox } from '@/components/ui/checkbox';
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from '@/components/ui/dialog';
import { Loader2, Settings, Database, AlertTriangle } from 'lucide-react';

export function WarehouseSettingsView() {
  const { user } = useAuth();
  const [userWarehouseId, setUserWarehouseId] = useState<string>('DEFAULT');
  const [warehouseLoading, setWarehouseLoading] = useState(true);
  const [warehouseInfo, setWarehouseInfo] = useState<any>(null);

  // User Preferences State for Clear Anomalies Feature
  const [userPreferences, setUserPreferences] = useState({
    clear_previous_anomalies: true,
    show_clear_warning: true
  });
  const [preferencesLoading, setPreferencesLoading] = useState(true);
  const [preferencesSaving, setPreferencesSaving] = useState(false);
  const [unresolvedCount, setUnresolvedCount] = useState(0);
  const [preferencesModalOpen, setPreferencesModalOpen] = useState(false);
  
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

  // Fetch user preferences for Clear Anomalies feature
  useEffect(() => {
    const fetchUserPreferences = async () => {
      if (!user) {
        setPreferencesLoading(false);
        return;
      }

      try {
        setPreferencesLoading(true);
        const response = await userPreferencesApi.getPreferences();

        if (response.success) {
          setUserPreferences(response.preferences);
          setUnresolvedCount(response.unresolved_anomaly_count);
          console.log('✅ User preferences loaded:', response.preferences);
        }
      } catch (error) {
        console.error('❌ Failed to fetch user preferences:', error);
      } finally {
        setPreferencesLoading(false);
      }
    };

    fetchUserPreferences();
  }, [user]);

  // Handle preference updates
  const updatePreference = async (key: string, value: boolean) => {
    try {
      setPreferencesSaving(true);
      const updateData = { [key]: value };
      const response = await userPreferencesApi.updatePreferences(updateData);

      if (response.success) {
        setUserPreferences(prev => ({ ...prev, [key]: value }));
        console.log(`✅ Updated ${key} to ${value}`);
      }
    } catch (error) {
      console.error(`❌ Failed to update ${key}:`, error);
    } finally {
      setPreferencesSaving(false);
    }
  };

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

      {/* Analysis Preferences Button */}
      <div className="mb-6">
        <Dialog open={preferencesModalOpen} onOpenChange={setPreferencesModalOpen}>
          <DialogTrigger asChild>
            <Button variant="outline" className="gap-2">
              <Settings className="w-4 h-4" />
              Analysis Preferences
            </Button>
          </DialogTrigger>
          <DialogContent className="max-w-2xl">
            <DialogHeader>
              <DialogTitle className="flex items-center gap-3">
                <div className="flex items-center justify-center w-10 h-10 rounded-lg bg-primary/10">
                  <Settings className="w-5 h-5 text-primary" />
                </div>
                Analysis Preferences
              </DialogTitle>
              <DialogDescription>
                Configure how new warehouse analysis uploads handle previous data
              </DialogDescription>
            </DialogHeader>

            {preferencesLoading ? (
              <div className="flex items-center gap-2 text-muted-foreground py-4">
                <Loader2 className="w-4 h-4 animate-spin" />
                <span>Loading preferences...</span>
              </div>
            ) : (
              <div className="space-y-6 py-4">
                {/* Current Status */}
                {unresolvedCount > 0 && (
                  <div className="p-4 bg-warning/10 border border-warning/20 rounded-lg">
                    <div className="flex items-start gap-3">
                      <AlertTriangle className="w-5 h-5 text-warning mt-0.5" />
                      <div>
                        <p className="font-medium text-foreground">
                          You currently have {unresolvedCount} unresolved anomalies
                        </p>
                        <p className="text-sm text-muted-foreground mt-1">
                          These will be affected by your preference settings below.
                        </p>
                      </div>
                    </div>
                  </div>
                )}

                {/* Preferences Options */}
                <div className="space-y-4">
                  <div className="flex items-start space-x-3">
                    <Checkbox
                      id="clear-previous"
                      checked={userPreferences.clear_previous_anomalies}
                      onCheckedChange={(checked) =>
                        updatePreference('clear_previous_anomalies', checked as boolean)
                      }
                      disabled={preferencesSaving}
                    />
                    <div className="grid gap-1.5 leading-none">
                      <label
                        htmlFor="clear-previous"
                        className="text-sm font-medium leading-none peer-disabled:cursor-not-allowed peer-disabled:opacity-70 cursor-pointer"
                      >
                        Clear previous anomalies on new analysis (recommended)
                      </label>
                      <p className="text-xs text-muted-foreground">
                        When uploading new inventory data, automatically clear previous unresolved anomalies.
                        This keeps your data clean and shows only current warehouse issues.
                      </p>
                    </div>
                  </div>

                  <div className="flex items-start space-x-3">
                    <Checkbox
                      id="show-warning"
                      checked={userPreferences.show_clear_warning}
                      onCheckedChange={(checked) =>
                        updatePreference('show_clear_warning', checked as boolean)
                      }
                      disabled={preferencesSaving}
                    />
                    <div className="grid gap-1.5 leading-none">
                      <label
                        htmlFor="show-warning"
                        className="text-sm font-medium leading-none peer-disabled:cursor-not-allowed peer-disabled:opacity-70 cursor-pointer"
                      >
                        Show confirmation warning before clearing
                      </label>
                      <p className="text-xs text-muted-foreground">
                        Display a confirmation dialog before clearing previous anomalies, giving you the option to cancel.
                      </p>
                    </div>
                  </div>
                </div>

                {/* Advanced Options Info */}
                <div className="p-3 bg-muted/50 rounded-lg">
                  <div className="flex items-start gap-3">
                    <Database className="w-4 h-4 text-muted-foreground mt-0.5" />
                    <div>
                      <p className="text-sm font-medium text-foreground">Advanced Mode</p>
                      <p className="text-xs text-muted-foreground">
                        To keep accumulating anomalies across multiple analyses (not recommended),
                        uncheck "Clear previous anomalies" above. This may cause data bloat and confusion.
                      </p>
                    </div>
                  </div>
                </div>

                {preferencesSaving && (
                  <div className="flex items-center gap-2 text-muted-foreground">
                    <Loader2 className="w-4 h-4 animate-spin" />
                    <span>Saving preferences...</span>
                  </div>
                )}
              </div>
            )}
          </DialogContent>
        </Dialog>
      </div>

      <WarehouseSettingsErrorBoundary>
        <LocationManager warehouseId={userWarehouseId} />
      </WarehouseSettingsErrorBoundary>
    </div>
  );
}