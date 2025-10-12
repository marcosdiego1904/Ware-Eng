'use client';

import React, { useState } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogHeader,
  DialogTitle,
} from '@/components/ui/dialog';
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select';
import { Badge } from '@/components/ui/badge';
import { Plus, Edit, Trash2, Package, Building2, Truck, ArrowRightLeft } from 'lucide-react';

interface SpecialArea {
  code: string;
  type: string;
  capacity: number;
  zone: string;
}

interface SpecialAreaEditorProps {
  title: string;
  description: string;
  areas: SpecialArea[];
  areaType: 'RECEIVING' | 'STAGING' | 'DOCK' | 'TRANSITIONAL';
  onAreasChange: (areas: SpecialArea[]) => void;
  icon?: React.ReactNode;
}

export function SpecialAreaEditor({ 
  title, 
  description, 
  areas, 
  areaType, 
  onAreasChange, 
  icon 
}: SpecialAreaEditorProps) {
  const [editingIndex, setEditingIndex] = useState<number | null>(null);
  const [showAddDialog, setShowAddDialog] = useState(false);
  const [editForm, setEditForm] = useState<SpecialArea>({
    code: '',
    type: areaType,
    capacity: 1,
    zone: getDefaultZone(areaType)
  });

  function getDefaultZone(type: string) {
    switch (type) {
      case 'RECEIVING': return 'RECEIVING';
      case 'STAGING': return 'STAGING';
      case 'DOCK': return 'DOCK';
      case 'TRANSITIONAL': return 'GENERAL';
      default: return 'GENERAL';
    }
  }

  function getDefaultCode(type: string, count: number) {
    const prefix = type === 'RECEIVING' ? 'RECV' : 
                   type === 'STAGING' ? 'STAGE' : 
                   type === 'DOCK' ? 'DOCK' : 
                   type === 'TRANSITIONAL' ? 'AISLE' : 'AREA';
    return `${prefix}-${String(count + 1).padStart(2, '0')}`;
  }

  const handleAdd = () => {
    setEditForm({
      code: getDefaultCode(areaType, areas.length),
      type: areaType,
      capacity: areaType === 'RECEIVING' ? 10 : 
                areaType === 'STAGING' ? 5 : 
                areaType === 'DOCK' ? 2 :
                areaType === 'TRANSITIONAL' ? 10 : 5,
      zone: getDefaultZone(areaType)
    });
    setEditingIndex(null);
    setShowAddDialog(true);
  };

  const handleEdit = (index: number) => {
    setEditForm({ ...areas[index] });
    setEditingIndex(index);
    setShowAddDialog(true);
  };

  const handleSave = () => {
    const newAreas = [...areas];
    if (editingIndex !== null) {
      newAreas[editingIndex] = editForm;
    } else {
      newAreas.push(editForm);
    }
    onAreasChange(newAreas);
    setShowAddDialog(false);
    setEditingIndex(null);
  };

  const handleDelete = (index: number) => {
    const newAreas = areas.filter((_, i) => i !== index);
    onAreasChange(newAreas);
  };

  const getTypeColor = (type: string) => {
    switch (type) {
      case 'RECEIVING': return 'bg-blue-100 text-blue-700';
      case 'STAGING': return 'bg-yellow-100 text-yellow-700';
      case 'DOCK': return 'bg-green-100 text-green-700';
      case 'TRANSITIONAL': return 'bg-purple-100 text-purple-700';
      default: return 'bg-gray-100 text-gray-700';
    }
  };

  const getIcon = () => {
    if (icon) return icon;
    switch (areaType) {
      case 'RECEIVING': return <Package className="h-4 w-4" />;
      case 'STAGING': return <Building2 className="h-4 w-4" />;
      case 'DOCK': return <Truck className="h-4 w-4" />;
      case 'TRANSITIONAL': return <ArrowRightLeft className="h-4 w-4" />;
      default: return <Package className="h-4 w-4" />;
    }
  };

  return (
    <>
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            {getIcon()}
            {title}
          </CardTitle>
          <CardDescription>{description}</CardDescription>
        </CardHeader>
        <CardContent>
          <div className="space-y-3">
            {areas.length > 0 ? (
              areas.map((area, index) => (
                <div key={index} className="flex items-center gap-3 p-3 border rounded-lg">
                  <div className="flex-1">
                    <div className="flex items-center gap-2 mb-1">
                      <span className="font-medium font-mono">{area.code}</span>
                      <Badge variant="secondary" className={getTypeColor(area.type)}>
                        {area.type}
                      </Badge>
                    </div>
                    <div className="text-sm text-muted-foreground">
                      Capacity: {area.capacity} pallets • Zone: {area.zone}
                    </div>
                  </div>
                  <div className="flex items-center gap-1">
                    <Button
                      variant="ghost"
                      size="sm"
                      onClick={() => handleEdit(index)}
                    >
                      <Edit className="h-4 w-4" />
                    </Button>
                    <Button
                      variant="ghost"
                      size="sm"
                      onClick={() => handleDelete(index)}
                    >
                      <Trash2 className="h-4 w-4" />
                    </Button>
                  </div>
                </div>
              ))
            ) : (
              <div className="text-center py-8 text-muted-foreground">
                <div className="mb-2">{getIcon()}</div>
                <p>No {title.toLowerCase()} configured</p>
              </div>
            )}
            
            <Button 
              variant="outline" 
              size="sm" 
              onClick={handleAdd}
              className="w-full"
            >
              <Plus className="h-4 w-4 mr-2" />
              Add {areaType === 'RECEIVING' ? 'Receiving' : 
                   areaType === 'STAGING' ? 'Staging' : 
                   areaType === 'DOCK' ? 'Dock' :
                   areaType === 'TRANSITIONAL' ? 'Aisle' : 'Area'} Area
            </Button>
          </div>
        </CardContent>
      </Card>

      <Dialog open={showAddDialog} onOpenChange={setShowAddDialog}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>
              {editingIndex !== null ? 'Edit' : 'Add'} {areaType === 'RECEIVING' ? 'Receiving' : 
                                                          areaType === 'STAGING' ? 'Staging' : 
                                                          areaType === 'DOCK' ? 'Dock' :
                                                          areaType === 'TRANSITIONAL' ? 'Aisle' : 'Area'} Area
            </DialogTitle>
            <DialogDescription>
              Configure the details for this special area
            </DialogDescription>
          </DialogHeader>
          
          <div className="space-y-4">
            <div className="space-y-2">
              <Label htmlFor="code">Area Code</Label>
              <Input
                id="code"
                value={editForm.code}
                onChange={(e) => setEditForm({ ...editForm, code: e.target.value.toUpperCase() })}
                placeholder="e.g., RECV-01"
                className="font-mono"
              />
            </div>

            <div className="space-y-2">
              <Label htmlFor="capacity">Pallet Capacity</Label>
              <Input
                id="capacity"
                type="number"
                min="1"
                value={editForm.capacity}
                onChange={(e) => setEditForm({ ...editForm, capacity: parseInt(e.target.value) || 1 })}
              />
            </div>

            <div className="space-y-2">
              <Label htmlFor="zone">Zone</Label>
              <Select
                value={editForm.zone}
                onValueChange={(value) => setEditForm({ ...editForm, zone: value })}
              >
                <SelectTrigger>
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="DOCK">Dock</SelectItem>
                  <SelectItem value="STAGING">Staging</SelectItem>
                  <SelectItem value="RECEIVING">Receiving</SelectItem>
                  <SelectItem value="GENERAL">General</SelectItem>
                  <SelectItem value="HAZMAT">Hazmat</SelectItem>
                  <SelectItem value="COLD">Cold Storage</SelectItem>
                  <SelectItem value="AMBIENT">Ambient</SelectItem>
                </SelectContent>
              </Select>
            </div>
          </div>

          <div className="flex justify-end gap-2 mt-6">
            <Button variant="outline" onClick={() => setShowAddDialog(false)}>
              Cancel
            </Button>
            <Button 
              onClick={handleSave}
              disabled={!editForm.code.trim() || editForm.capacity < 1}
            >
              {editingIndex !== null ? 'Update' : 'Add'} Area
            </Button>
          </div>
        </DialogContent>
      </Dialog>
    </>
  );
}