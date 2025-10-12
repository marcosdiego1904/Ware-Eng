# Unit-Agnostic Warehouse Intelligence: Technical Design Specification

## Document Overview

**Document Type:** Technical Design Specification
**Version:** 1.0
**Date:** September 14, 2025
**Status:** Ready for Implementation
**Author Role:** Principal Software Architect
**Prerequisites:** Unit-Agnostic Warehouse Intelligence Concept Document

### Design Principles
1. **Leverage Existing Architecture**: Reuse proven components and patterns
2. **Maintain Performance**: No degradation in current processing speeds
3. **Backwards Compatibility**: Existing installations work unchanged
4. **Progressive Enhancement**: Features can be adopted incrementally
5. **Clean Separation**: Scope logic separated from business rule logic

---

## Current Architecture Analysis

### Existing System Components

#### Backend Architecture (`backend/src/`)
```
app.py                    # Flask application and API routes
models.py                 # SQLAlchemy database models
rule_engine.py            # Core rule evaluation system
location_classification_service.py  # Location categorization
virtual_location_engine.py         # Location validation system
warehouse_api.py          # Warehouse management endpoints
user_warehouse_api.py     # User warehouse operations
```

#### Frontend Architecture (`frontend/`)
```
components/locations/
├── location-manager.tsx              # Main location management
├── templates/
│   ├── template-creation-wizard.tsx  # Warehouse setup wizard
│   └── enhanced-template-manager-v2.tsx  # Template management
└── setup-wizard/ (legacy)           # Old wizard system
```

#### Database Schema (Current)
```sql
-- Core tables that will be enhanced
location (id, code, location_type, capacity, zone, is_active, warehouse_id)
user (id, username, email, created_at)
warehouse_config (warehouse_id, config_data JSON)
rule (id, name, rule_type, conditions JSON, is_active)
```

### Current Rule Engine Flow
```python
# Current processing pipeline
1. File Upload → Column Mapping
2. Load Active Rules → Rule Engine
3. For Each Rule:
   - Load all locations from database
   - Evaluate inventory data against rule conditions
   - Generate anomalies
4. Return aggregated results
```

---

## Technical Design: Unit-Agnostic Enhancement

### 1. Database Schema Design

#### 1.1 Enhanced Location Table
```sql
-- Add new columns to existing location table
ALTER TABLE location ADD COLUMN unit_type VARCHAR(50) DEFAULT 'pallets';
ALTER TABLE location ADD COLUMN is_tracked BOOLEAN DEFAULT TRUE;
ALTER TABLE location ADD COLUMN user_defined BOOLEAN DEFAULT FALSE;
ALTER TABLE location ADD COLUMN tracking_priority INTEGER DEFAULT 1;
ALTER TABLE location ADD COLUMN custom_metadata JSON;

-- Create indexes for performance
CREATE INDEX idx_location_tracked ON location(warehouse_id, is_tracked);
CREATE INDEX idx_location_user_defined ON location(warehouse_id, user_defined);
CREATE INDEX idx_location_unit_type ON location(warehouse_id, unit_type);

-- Add constraints
ALTER TABLE location ADD CONSTRAINT chk_unit_type
    CHECK (unit_type IN ('pallets', 'boxes', 'items', 'cases', 'units', 'mixed'));
ALTER TABLE location ADD CONSTRAINT chk_tracking_priority
    CHECK (tracking_priority BETWEEN 1 AND 10);
```

#### 1.2 New Warehouse Analysis Scope Table
```sql
-- Central scope configuration per warehouse
CREATE TABLE warehouse_analysis_scope (
    id SERIAL PRIMARY KEY,
    warehouse_id INTEGER NOT NULL REFERENCES warehouse_config(warehouse_id),
    scope_name VARCHAR(100) NOT NULL DEFAULT 'Default Scope',
    location_patterns TEXT[] NOT NULL DEFAULT '{}',
    excluded_patterns TEXT[] NOT NULL DEFAULT '{}',
    unit_type_filters JSON DEFAULT '{}',
    capacity_overrides JSON DEFAULT '{}',
    is_active BOOLEAN DEFAULT TRUE,
    created_by INTEGER REFERENCES "user"(id),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT unique_warehouse_scope UNIQUE(warehouse_id, scope_name)
);

-- Example JSON structure for unit_type_filters:
-- {"STORAGE": "pallets", "PICK_AREA": "items", "RECEIVING": "mixed"}

-- Example JSON structure for capacity_overrides:
-- {"RECV-01": 50, "W-10": 30, "BULK-A-*": 5}

CREATE INDEX idx_warehouse_scope_active ON warehouse_analysis_scope(warehouse_id, is_active);
```

#### 1.3 Location Scope Mapping Table
```sql
-- Track which locations are in scope for analysis
CREATE TABLE location_scope_mapping (
    id SERIAL PRIMARY KEY,
    warehouse_id INTEGER NOT NULL REFERENCES warehouse_config(warehouse_id),
    location_code VARCHAR(50) NOT NULL,
    location_pattern VARCHAR(100),
    is_in_scope BOOLEAN DEFAULT TRUE,
    unit_type VARCHAR(50) DEFAULT 'pallets',
    capacity_override INTEGER,
    scope_reason VARCHAR(20) DEFAULT 'user_defined',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT chk_scope_reason
        CHECK (scope_reason IN ('user_defined', 'pattern_match', 'template_generated', 'auto_detected'))
);

CREATE UNIQUE INDEX idx_location_scope_unique
    ON location_scope_mapping(warehouse_id, location_code);
CREATE INDEX idx_location_scope_pattern
    ON location_scope_mapping(warehouse_id, location_pattern);
```

#### 1.4 Audit and Tracking Tables
```sql
-- Track scope changes for auditing
CREATE TABLE scope_change_log (
    id SERIAL PRIMARY KEY,
    warehouse_id INTEGER NOT NULL REFERENCES warehouse_config(warehouse_id),
    change_type VARCHAR(20) NOT NULL,
    location_code VARCHAR(50),
    old_values JSON,
    new_values JSON,
    changed_by INTEGER REFERENCES "user"(id),
    changed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT chk_change_type
        CHECK (change_type IN ('scope_added', 'scope_removed', 'capacity_changed', 'unit_type_changed'))
);

-- Track analysis performance metrics
CREATE TABLE analysis_scope_metrics (
    id SERIAL PRIMARY KEY,
    warehouse_id INTEGER NOT NULL REFERENCES warehouse_config(warehouse_id),
    analysis_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    total_records INTEGER NOT NULL,
    in_scope_records INTEGER NOT NULL,
    out_of_scope_records INTEGER NOT NULL,
    processing_time_ms INTEGER NOT NULL,
    anomalies_detected INTEGER NOT NULL,
    scope_version VARCHAR(50)
);
```

### 2. Backend API Design

#### 2.1 New API Endpoints

**Scope Management API (`/api/v1/warehouses/{warehouse_id}/scope/`)**
```python
# GET /api/v1/warehouses/{warehouse_id}/scope
# Returns current analysis scope configuration
{
    "warehouse_id": 1,
    "scope_configuration": {
        "total_locations": 1247,
        "tracked_locations": 867,
        "ignored_locations": 380,
        "unit_types": {
            "pallets": 650,
            "items": 150,
            "boxes": 67
        }
    },
    "location_patterns": [
        {"pattern": "BULK-*", "unit_type": "pallets", "capacity": 5},
        {"pattern": "W-*", "unit_type": "items", "capacity": 30}
    ],
    "excluded_patterns": ["SHELF-*", "BIN-*"]
}

# POST /api/v1/warehouses/{warehouse_id}/scope
# Updates scope configuration
{
    "location_patterns": [
        {"pattern": "BULK-*", "unit_type": "pallets", "default_capacity": 5},
        {"pattern": "W-*", "unit_type": "items", "default_capacity": 30}
    ],
    "excluded_patterns": ["SHELF-*", "BIN-*"],
    "capacity_overrides": {
        "RECV-01": 50,
        "W-10": 25
    }
}

# GET /api/v1/warehouses/{warehouse_id}/scope/preview
# Preview scope changes before applying
{
    "current_scope": {...},
    "proposed_scope": {...},
    "impact_analysis": {
        "locations_added": 15,
        "locations_removed": 3,
        "capacity_changes": 8
    }
}
```

**Location Scope API (`/api/v1/locations/scope/`)**
```python
# GET /api/v1/locations/scope/validate
# Validate location codes against scope
{
    "location_codes": ["BULK-A-001", "W-10", "SHELF-01"],
    "warehouse_id": 1
}
# Response:
{
    "validation_results": [
        {"code": "BULK-A-001", "in_scope": true, "unit_type": "pallets", "capacity": 5},
        {"code": "W-10", "in_scope": true, "unit_type": "items", "capacity": 30},
        {"code": "SHELF-01", "in_scope": false, "reason": "excluded_pattern"}
    ]
}

# POST /api/v1/locations/scope/bulk-update
# Bulk update location scope settings
{
    "warehouse_id": 1,
    "updates": [
        {"code": "W-10", "unit_type": "items", "capacity": 25},
        {"code": "W-11", "unit_type": "items", "capacity": 30}
    ]
}
```

#### 2.2 Enhanced Analysis API

**Modified Analysis Endpoint (`/api/v1/reports`)**
```python
# Enhanced POST /api/v1/reports with scope filtering
# Request includes scope information
{
    "inventory_file": <file>,
    "column_mapping": {...},
    "scope_settings": {
        "apply_scope_filter": true,
        "scope_version": "v1.0",
        "include_scope_metrics": true
    }
}

# Response includes scope analysis
{
    "report_id": 123,
    "scope_analysis": {
        "total_records": 4523,
        "in_scope_records": 1247,
        "out_of_scope_records": 3276,
        "scope_coverage": "27.6%",
        "processing_time_ms": 145
    },
    "anomalies": [...],
    "recommendations": {
        "scope_optimization": [
            "Consider adding pattern 'PICK-*' to scope (found 45 records)",
            "Pattern 'OLD-*' matched 0 records, consider removing"
        ]
    }
}
```

### 3. Backend Implementation Details

#### 3.1 Scope Service Layer

**New Service: `ScopeManagementService`**
```python
# backend/src/services/scope_management_service.py
from typing import List, Dict, Optional, Tuple
import re
import json
from models import Location, WarehouseAnalysisScope, LocationScopeMapping

class ScopeManagementService:
    def __init__(self, warehouse_id: int):
        self.warehouse_id = warehouse_id
        self._scope_cache = None

    def get_warehouse_scope(self) -> Dict:
        """Get current warehouse analysis scope configuration"""
        if self._scope_cache is None:
            self._load_scope_configuration()
        return self._scope_cache

    def apply_scope_filter(self, inventory_df) -> Tuple[pd.DataFrame, Dict]:
        """
        Filter inventory DataFrame to include only in-scope locations
        Returns: (filtered_df, scope_metrics)
        """
        scope_config = self.get_warehouse_scope()

        # Get in-scope locations
        in_scope_locations = self._get_in_scope_locations(inventory_df['location'].unique())

        # Filter DataFrame
        filtered_df = inventory_df[inventory_df['location'].isin(in_scope_locations)]

        # Calculate metrics
        scope_metrics = {
            'total_records': len(inventory_df),
            'in_scope_records': len(filtered_df),
            'out_of_scope_records': len(inventory_df) - len(filtered_df),
            'in_scope_locations': len(in_scope_locations),
            'unique_locations_total': len(inventory_df['location'].unique())
        }

        return filtered_df, scope_metrics

    def _get_in_scope_locations(self, location_codes: List[str]) -> List[str]:
        """Determine which locations are in analysis scope"""
        scope_config = self.get_warehouse_scope()
        in_scope = []

        for location in location_codes:
            if self._is_location_in_scope(location, scope_config):
                in_scope.append(location)

        return in_scope

    def _is_location_in_scope(self, location_code: str, scope_config: Dict) -> bool:
        """Check if a specific location is in analysis scope"""
        # Check excluded patterns first
        for excluded_pattern in scope_config.get('excluded_patterns', []):
            if self._matches_pattern(location_code, excluded_pattern):
                return False

        # Check included patterns
        for included_pattern in scope_config.get('location_patterns', []):
            if self._matches_pattern(location_code, included_pattern['pattern']):
                return True

        # Check direct location mappings
        direct_mappings = scope_config.get('direct_mappings', {})
        return direct_mappings.get(location_code, False)

    def _matches_pattern(self, location_code: str, pattern: str) -> bool:
        """Check if location code matches a pattern (supports wildcards)"""
        # Convert wildcard pattern to regex
        regex_pattern = pattern.replace('*', '.*').replace('?', '.')
        return bool(re.match(f'^{regex_pattern}$', location_code, re.IGNORECASE))

    def update_scope_configuration(self, new_config: Dict) -> Dict:
        """Update warehouse scope configuration"""
        # Validate configuration
        self._validate_scope_config(new_config)

        # Save to database
        scope_record = self._save_scope_config(new_config)

        # Clear cache
        self._scope_cache = None

        # Log change
        self._log_scope_change('scope_updated', new_config)

        return {"success": True, "scope_id": scope_record.id}

    def get_location_unit_type(self, location_code: str) -> str:
        """Get the unit type for a specific location"""
        scope_config = self.get_warehouse_scope()

        # Check direct overrides first
        overrides = scope_config.get('unit_type_overrides', {})
        if location_code in overrides:
            return overrides[location_code]

        # Check pattern-based unit types
        for pattern_config in scope_config.get('location_patterns', []):
            if self._matches_pattern(location_code, pattern_config['pattern']):
                return pattern_config.get('unit_type', 'pallets')

        return 'pallets'  # Default

    def get_location_capacity(self, location_code: str) -> Optional[int]:
        """Get the capacity for a specific location"""
        scope_config = self.get_warehouse_scope()

        # Check direct capacity overrides
        overrides = scope_config.get('capacity_overrides', {})
        if location_code in overrides:
            return overrides[location_code]

        # Check database location record
        location = Location.query.filter_by(
            code=location_code,
            warehouse_id=self.warehouse_id
        ).first()

        if location and location.capacity:
            return location.capacity

        # Check pattern-based default capacities
        for pattern_config in scope_config.get('location_patterns', []):
            if self._matches_pattern(location_code, pattern_config['pattern']):
                return pattern_config.get('default_capacity')

        return None
```

#### 3.2 Enhanced Rule Engine Integration

**Modified `rule_engine.py`**
```python
# backend/src/rule_engine.py - Enhanced with scope filtering

from services.scope_management_service import ScopeManagementService

class RuleEngine:
    def __init__(self, warehouse_context: dict = None):
        self.warehouse_context = warehouse_context or {}
        self.warehouse_id = warehouse_context.get('warehouse_id')
        self.scope_service = None
        if self.warehouse_id:
            self.scope_service = ScopeManagementService(self.warehouse_id)

    def evaluate_rules(self, inventory_df, rules=None, apply_scope_filter=True):
        """Enhanced rule evaluation with optional scope filtering"""

        # Apply scope filtering if enabled
        scope_metrics = {}
        if apply_scope_filter and self.scope_service:
            print(f"[RULE_ENGINE] Applying scope filter for warehouse {self.warehouse_id}")
            inventory_df, scope_metrics = self.scope_service.apply_scope_filter(inventory_df)
            print(f"[RULE_ENGINE] Scope filter: {scope_metrics['in_scope_records']}/{scope_metrics['total_records']} records in scope")

        # Load active rules
        if rules is None:
            rules = self.load_active_rules()

        # Evaluate each rule
        all_anomalies = []
        rule_performance = []

        for rule in rules:
            start_time = time.time()

            try:
                # Get rule evaluator
                evaluator = self._get_rule_evaluator(rule.rule_type)

                # Enhanced context with scope information
                enhanced_context = {
                    **self.warehouse_context,
                    'scope_service': self.scope_service,
                    'scope_metrics': scope_metrics
                }

                # Evaluate rule with enhanced context
                anomalies = evaluator.evaluate(rule, inventory_df, enhanced_context)
                all_anomalies.extend(anomalies)

                execution_time = (time.time() - start_time) * 1000
                rule_performance.append({
                    'rule_id': rule.id,
                    'rule_name': rule.name,
                    'execution_time_ms': execution_time,
                    'anomalies_found': len(anomalies),
                    'records_processed': len(inventory_df)
                })

            except Exception as e:
                print(f"[RULE_ENGINE] Error evaluating rule {rule.name}: {str(e)}")
                continue

        return {
            'anomalies': all_anomalies,
            'performance': rule_performance,
            'scope_metrics': scope_metrics
        }
```

**Enhanced Overcapacity Evaluator**
```python
# backend/src/rule_engine.py - OvercapacityEvaluator enhancement

class OvercapacityEvaluator:
    def evaluate(self, rule, inventory_df, warehouse_context=None):
        """Enhanced overcapacity evaluation with unit-agnostic logic"""

        scope_service = warehouse_context.get('scope_service') if warehouse_context else None
        anomalies = []

        # Group by location and count items (unit-agnostic)
        location_counts = inventory_df.groupby('location').size().to_dict()

        print(f"[OVERCAPACITY] Evaluating {len(location_counts)} locations")

        for location, item_count in location_counts.items():
            # Get location capacity (scope-aware)
            if scope_service:
                capacity = scope_service.get_location_capacity(location)
                unit_type = scope_service.get_location_unit_type(location)
            else:
                # Fallback to existing logic
                capacity = self._get_location_capacity_legacy(location, warehouse_context)
                unit_type = 'pallets'

            if capacity and item_count > capacity:
                # Determine anomaly details based on unit type
                anomaly_details = self._create_unit_agnostic_anomaly(
                    rule, location, item_count, capacity, unit_type, inventory_df
                )
                anomalies.extend(anomaly_details)

        print(f"[OVERCAPACITY] Found {len(anomalies)} overcapacity anomalies")
        return anomalies

    def _create_unit_agnostic_anomaly(self, rule, location, item_count, capacity, unit_type, inventory_df):
        """Create anomaly details that work for any unit type"""

        # Get items in this location for detailed reporting
        location_items = inventory_df[inventory_df['location'] == location]

        # Create appropriate anomaly description based on unit type
        unit_display = {
            'pallets': 'pallets',
            'boxes': 'boxes',
            'items': 'items',
            'cases': 'cases',
            'units': 'units',
            'mixed': 'units'
        }.get(unit_type, 'items')

        anomalies = []

        if unit_type in ['pallets', 'boxes', 'cases']:
            # Create individual anomalies for larger items
            for _, item in location_items.iterrows():
                anomalies.append({
                    'rule_id': rule.id,
                    'rule_name': rule.name,
                    'anomaly_type': 'OVERCAPACITY',
                    'priority': 'High',
                    'location': location,
                    'pallet_id': item.get('pallet_id', item.get('item_id', 'Unknown')),
                    'description': f"Location {location} over capacity: {item_count} {unit_display} > {capacity} limit",
                    'details': {
                        'current_count': item_count,
                        'capacity_limit': capacity,
                        'excess_count': item_count - capacity,
                        'unit_type': unit_type
                    }
                })
        else:
            # Create single location-level anomaly for small items
            representative_item = location_items.iloc[0] if len(location_items) > 0 else {}
            anomalies.append({
                'rule_id': rule.id,
                'rule_name': rule.name,
                'anomaly_type': 'OVERCAPACITY_LOCATION',
                'priority': 'Medium',
                'location': location,
                'pallet_id': f"LOCATION_{location}",
                'description': f"Location {location} over capacity: {item_count} {unit_display} > {capacity} limit",
                'details': {
                    'current_count': item_count,
                    'capacity_limit': capacity,
                    'excess_count': item_count - capacity,
                    'unit_type': unit_type,
                    'affected_items': len(location_items)
                }
            })

        return anomalies
```

### 4. Frontend Implementation

#### 4.1 Enhanced Template Creation Wizard

**Modified `template-creation-wizard.tsx`**
```typescript
// frontend/components/locations/templates/template-creation-wizard.tsx

interface LocationScopeDefinition {
  pattern: string;
  unitType: 'pallets' | 'boxes' | 'items' | 'cases' | 'units' | 'mixed';
  defaultCapacity: number;
  locationTypes: string[];
  isTracked: boolean;
}

interface WarehouseScopeConfig {
  scopeName: string;
  locationPatterns: LocationScopeDefinition[];
  excludedPatterns: string[];
  capacityOverrides: Record<string, number>;
  unitTypeOverrides: Record<string, string>;
}

// New step in wizard: Step 3 - Analysis Scope Definition
const Step3AnalysisScope: React.FC<{
  scopeConfig: WarehouseScopeConfig;
  onScopeChange: (config: WarehouseScopeConfig) => void;
  onNext: () => void;
  onPrev: () => void;
}> = ({ scopeConfig, onScopeChange, onNext, onPrev }) => {
  const [patterns, setPatterns] = useState<LocationScopeDefinition[]>(
    scopeConfig.locationPatterns || []
  );
  const [excludedPatterns, setExcludedPatterns] = useState<string[]>(
    scopeConfig.excludedPatterns || []
  );

  const addLocationPattern = () => {
    const newPattern: LocationScopeDefinition = {
      pattern: '',
      unitType: 'pallets',
      defaultCapacity: 5,
      locationTypes: ['STORAGE'],
      isTracked: true
    };
    setPatterns([...patterns, newPattern]);
  };

  const updatePattern = (index: number, updates: Partial<LocationScopeDefinition>) => {
    const updatedPatterns = patterns.map((pattern, i) =>
      i === index ? { ...pattern, ...updates } : pattern
    );
    setPatterns(updatedPatterns);
    onScopeChange({
      ...scopeConfig,
      locationPatterns: updatedPatterns
    });
  };

  return (
    <div className="space-y-6">
      <div className="text-center">
        <h3 className="text-2xl font-bold text-gray-900 mb-2">
          🎯 Define Analysis Scope
        </h3>
        <p className="text-gray-600 max-w-2xl mx-auto">
          Tell WareWise which locations to analyze and what type of items you track in each area.
          This ensures clean, relevant anomaly detection.
        </p>
      </div>

      {/* Location Patterns Section */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Target className="h-5 w-5 text-blue-600" />
            Locations to Analyze
          </CardTitle>
          <CardDescription>
            Define patterns for locations you want WareWise to monitor
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          {patterns.map((pattern, index) => (
            <div key={index} className="p-4 border rounded-lg space-y-3">
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <Label htmlFor={`pattern-${index}`}>Location Pattern</Label>
                  <Input
                    id={`pattern-${index}`}
                    placeholder="e.g., BULK-*, W-*, 001A-999Z"
                    value={pattern.pattern}
                    onChange={(e) => updatePattern(index, { pattern: e.target.value })}
                  />
                  <p className="text-xs text-gray-500 mt-1">
                    Use * for wildcards (e.g., BULK-* matches BULK-A-001, BULK-B-002)
                  </p>
                </div>

                <div>
                  <Label htmlFor={`unitType-${index}`}>What do you track here?</Label>
                  <Select
                    value={pattern.unitType}
                    onValueChange={(value) => updatePattern(index, { unitType: value as any })}
                  >
                    <SelectTrigger>
                      <SelectValue />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="pallets">📦 Pallets</SelectItem>
                      <SelectItem value="boxes">📫 Boxes</SelectItem>
                      <SelectItem value="items">🏷️ Individual Items</SelectItem>
                      <SelectItem value="cases">📋 Cases</SelectItem>
                      <SelectItem value="mixed">🔄 Mixed Units</SelectItem>
                    </SelectContent>
                  </Select>
                </div>
              </div>

              <div className="grid grid-cols-2 gap-4">
                <div>
                  <Label htmlFor={`capacity-${index}`}>Default Capacity</Label>
                  <Input
                    id={`capacity-${index}`}
                    type="number"
                    min="1"
                    value={pattern.defaultCapacity}
                    onChange={(e) => updatePattern(index, {
                      defaultCapacity: parseInt(e.target.value) || 1
                    })}
                  />
                  <p className="text-xs text-gray-500 mt-1">
                    Maximum {pattern.unitType} per location
                  </p>
                </div>

                <div className="flex items-end">
                  <Button
                    variant="outline"
                    size="sm"
                    onClick={() => {
                      const newPatterns = patterns.filter((_, i) => i !== index);
                      setPatterns(newPatterns);
                      onScopeChange({ ...scopeConfig, locationPatterns: newPatterns });
                    }}
                  >
                    <Trash2 className="h-4 w-4" />
                    Remove
                  </Button>
                </div>
              </div>
            </div>
          ))}

          <Button
            variant="outline"
            onClick={addLocationPattern}
            className="w-full"
          >
            <Plus className="h-4 w-4 mr-2" />
            Add Location Pattern
          </Button>
        </CardContent>
      </Card>

      {/* Excluded Patterns Section */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <X className="h-5 w-5 text-red-600" />
            Locations to Ignore
          </CardTitle>
          <CardDescription>
            Define patterns for locations that should be ignored during analysis
          </CardDescription>
        </CardHeader>
        <CardContent>
          <div className="space-y-2">
            {excludedPatterns.map((pattern, index) => (
              <div key={index} className="flex gap-2">
                <Input
                  value={pattern}
                  onChange={(e) => {
                    const newExcluded = excludedPatterns.map((p, i) =>
                      i === index ? e.target.value : p
                    );
                    setExcludedPatterns(newExcluded);
                    onScopeChange({ ...scopeConfig, excludedPatterns: newExcluded });
                  }}
                  placeholder="e.g., SHELF-*, BIN-*, TEMP-*"
                />
                <Button
                  variant="outline"
                  size="sm"
                  onClick={() => {
                    const newExcluded = excludedPatterns.filter((_, i) => i !== index);
                    setExcludedPatterns(newExcluded);
                    onScopeChange({ ...scopeConfig, excludedPatterns: newExcluded });
                  }}
                >
                  <X className="h-4 w-4" />
                </Button>
              </div>
            ))}
            <Button
              variant="outline"
              size="sm"
              onClick={() => {
                const newExcluded = [...excludedPatterns, ''];
                setExcludedPatterns(newExcluded);
                onScopeChange({ ...scopeConfig, excludedPatterns: newExcluded });
              }}
            >
              <Plus className="h-4 w-4 mr-2" />
              Add Excluded Pattern
            </Button>
          </div>
        </CardContent>
      </Card>

      {/* Scope Preview */}
      <Card className="bg-blue-50 border-blue-200">
        <CardHeader>
          <CardTitle className="text-blue-900">📊 Scope Preview</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="text-sm text-blue-800">
            <div className="mb-2">
              <strong>Will Analyze:</strong>
              <ul className="ml-4 mt-1">
                {patterns.filter(p => p.isTracked).map((pattern, i) => (
                  <li key={i}>
                    • {pattern.pattern} ({pattern.unitType}, max {pattern.defaultCapacity} each)
                  </li>
                ))}
              </ul>
            </div>
            {excludedPatterns.length > 0 && (
              <div>
                <strong>Will Ignore:</strong>
                <ul className="ml-4 mt-1">
                  {excludedPatterns.filter(p => p.trim()).map((pattern, i) => (
                    <li key={i}>• {pattern}</li>
                  ))}
                </ul>
              </div>
            )}
          </div>
        </CardContent>
      </Card>

      {/* Navigation */}
      <div className="flex justify-between pt-6">
        <Button variant="outline" onClick={onPrev}>
          <ChevronLeft className="h-4 w-4 mr-2" />
          Previous
        </Button>

        <Button
          onClick={onNext}
          disabled={patterns.length === 0}
        >
          Next: Special Areas
          <ChevronRight className="h-4 w-4 ml-2" />
        </Button>
      </div>
    </div>
  );
};
```

#### 4.2 Analysis Results Enhancement

**Enhanced Results Display**
```typescript
// frontend/components/dashboard/analysis-results.tsx

interface ScopeMetrics {
  totalRecords: number;
  inScopeRecords: number;
  outOfScopeRecords: number;
  scopeCoverage: string;
  processingTimeMs: number;
}

const AnalysisResultsHeader: React.FC<{
  scopeMetrics?: ScopeMetrics;
  anomalies: Anomaly[];
}> = ({ scopeMetrics, anomalies }) => {
  if (!scopeMetrics) return null;

  return (
    <Card className="mb-6 bg-gradient-to-r from-blue-50 to-indigo-50 border-blue-200">
      <CardHeader>
        <CardTitle className="flex items-center gap-2 text-blue-900">
          <Target className="h-5 w-5" />
          Analysis Scope Summary
        </CardTitle>
      </CardHeader>
      <CardContent>
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
          <div className="text-center">
            <div className="text-2xl font-bold text-blue-600">
              {scopeMetrics.inScopeRecords.toLocaleString()}
            </div>
            <div className="text-sm font-medium text-gray-600">Records Analyzed</div>
          </div>

          <div className="text-center">
            <div className="text-2xl font-bold text-gray-500">
              {scopeMetrics.outOfScopeRecords.toLocaleString()}
            </div>
            <div className="text-sm font-medium text-gray-600">Records Ignored</div>
          </div>

          <div className="text-center">
            <div className="text-2xl font-bold text-green-600">
              {anomalies.length}
            </div>
            <div className="text-sm font-medium text-gray-600">Anomalies Found</div>
          </div>

          <div className="text-center">
            <div className="text-2xl font-bold text-purple-600">
              {scopeMetrics.processingTimeMs}ms
            </div>
            <div className="text-sm font-medium text-gray-600">Processing Time</div>
          </div>
        </div>

        <div className="mt-4 p-3 bg-white rounded border">
          <div className="flex items-center justify-between text-sm">
            <span className="text-gray-600">
              Scope Coverage: {scopeMetrics.scopeCoverage} of uploaded data analyzed
            </span>
            <Button variant="link" size="sm" className="text-blue-600">
              <Settings className="h-4 w-4 mr-1" />
              Modify Scope
            </Button>
          </div>
        </div>
      </CardContent>
    </Card>
  );
};
```

#### 4.3 Scope Management Interface

**New Component: Scope Manager**
```typescript
// frontend/components/locations/scope-manager.tsx

const ScopeManager: React.FC<{
  warehouseId: string;
  onScopeUpdate?: (newScope: any) => void;
}> = ({ warehouseId, onScopeUpdate }) => {
  const [currentScope, setCurrentScope] = useState<any>(null);
  const [isEditing, setIsEditing] = useState(false);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadCurrentScope();
  }, [warehouseId]);

  const loadCurrentScope = async () => {
    try {
      const response = await api.get(`/warehouses/${warehouseId}/scope`);
      setCurrentScope(response.data);
    } catch (error) {
      console.error('Failed to load scope configuration:', error);
    } finally {
      setLoading(false);
    }
  };

  const updateScope = async (newScopeConfig: any) => {
    try {
      setLoading(true);
      await api.post(`/warehouses/${warehouseId}/scope`, newScopeConfig);
      await loadCurrentScope();
      onScopeUpdate?.(newScopeConfig);
      setIsEditing(false);
    } catch (error) {
      console.error('Failed to update scope:', error);
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return <div className="flex justify-center p-8"><Spinner /></div>;
  }

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <h2 className="text-2xl font-bold">Analysis Scope Configuration</h2>
        <Button
          variant={isEditing ? "outline" : "default"}
          onClick={() => setIsEditing(!isEditing)}
        >
          {isEditing ? (
            <>
              <X className="h-4 w-4 mr-2" />
              Cancel
            </>
          ) : (
            <>
              <Edit className="h-4 w-4 mr-2" />
              Edit Scope
            </>
          )}
        </Button>
      </div>

      {isEditing ? (
        <ScopeEditor
          currentScope={currentScope}
          onSave={updateScope}
          onCancel={() => setIsEditing(false)}
        />
      ) : (
        <ScopeDisplay scope={currentScope} />
      )}
    </div>
  );
};
```

### 5. Migration Strategy

#### 5.1 Phased Migration Approach

**Phase 1: Database Schema Migration (Zero Downtime)**
```sql
-- Migration Script: 001_add_unit_agnostic_support.sql

-- Step 1: Add new columns with defaults (non-breaking)
ALTER TABLE location ADD COLUMN unit_type VARCHAR(50) DEFAULT 'pallets';
ALTER TABLE location ADD COLUMN is_tracked BOOLEAN DEFAULT TRUE;
ALTER TABLE location ADD COLUMN user_defined BOOLEAN DEFAULT FALSE;
ALTER TABLE location ADD COLUMN tracking_priority INTEGER DEFAULT 1;
ALTER TABLE location ADD COLUMN custom_metadata JSON;

-- Step 2: Create new tables
CREATE TABLE warehouse_analysis_scope (
    id SERIAL PRIMARY KEY,
    warehouse_id INTEGER NOT NULL REFERENCES warehouse_config(warehouse_id),
    scope_name VARCHAR(100) NOT NULL DEFAULT 'Default Scope',
    location_patterns TEXT[] NOT NULL DEFAULT '{}',
    excluded_patterns TEXT[] NOT NULL DEFAULT '{}',
    unit_type_filters JSON DEFAULT '{}',
    capacity_overrides JSON DEFAULT '{}',
    is_active BOOLEAN DEFAULT TRUE,
    created_by INTEGER REFERENCES "user"(id),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT unique_warehouse_scope UNIQUE(warehouse_id, scope_name)
);

CREATE TABLE location_scope_mapping (
    id SERIAL PRIMARY KEY,
    warehouse_id INTEGER NOT NULL REFERENCES warehouse_config(warehouse_id),
    location_code VARCHAR(50) NOT NULL,
    location_pattern VARCHAR(100),
    is_in_scope BOOLEAN DEFAULT TRUE,
    unit_type VARCHAR(50) DEFAULT 'pallets',
    capacity_override INTEGER,
    scope_reason VARCHAR(20) DEFAULT 'user_defined',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT chk_scope_reason
        CHECK (scope_reason IN ('user_defined', 'pattern_match', 'template_generated', 'auto_detected'))
);

-- Step 3: Create indexes
CREATE INDEX idx_location_tracked ON location(warehouse_id, is_tracked);
CREATE INDEX idx_warehouse_scope_active ON warehouse_analysis_scope(warehouse_id, is_active);
CREATE UNIQUE INDEX idx_location_scope_unique ON location_scope_mapping(warehouse_id, location_code);

-- Step 4: Seed default scope configurations for existing warehouses
INSERT INTO warehouse_analysis_scope (warehouse_id, scope_name, location_patterns, is_active)
SELECT DISTINCT wc.warehouse_id, 'Default Scope', ARRAY['*'], TRUE
FROM warehouse_config wc
WHERE wc.warehouse_id NOT IN (SELECT warehouse_id FROM warehouse_analysis_scope);
```

**Phase 2: Backend Service Integration (Feature Toggle)**
```python
# backend/src/services/feature_flags.py
class FeatureFlags:
    UNIT_AGNOSTIC_SCOPE = "unit_agnostic_scope"

    @staticmethod
    def is_enabled(feature_name: str, warehouse_id: int = None) -> bool:
        # Check environment variable first
        env_flag = os.getenv(f"FEATURE_{feature_name.upper()}", "false")
        if env_flag.lower() == "true":
            return True

        # Check database configuration per warehouse
        if warehouse_id:
            return WarehouseFeatureFlag.query.filter_by(
                warehouse_id=warehouse_id,
                feature_name=feature_name,
                is_enabled=True
            ).first() is not None

        return False

# Modified rule engine with feature toggle
class RuleEngine:
    def evaluate_rules(self, inventory_df, rules=None, warehouse_context=None):
        apply_scope_filter = False

        if warehouse_context:
            warehouse_id = warehouse_context.get('warehouse_id')
            apply_scope_filter = FeatureFlags.is_enabled(
                FeatureFlags.UNIT_AGNOSTIC_SCOPE,
                warehouse_id
            )

        if apply_scope_filter and self.scope_service:
            inventory_df, scope_metrics = self.scope_service.apply_scope_filter(inventory_df)
        else:
            scope_metrics = {}

        # Continue with existing logic...
```

**Phase 3: Frontend Integration (Progressive Enhancement)**
```typescript
// frontend/lib/feature-flags.ts
export const useFeatureFlag = (flagName: string, warehouseId?: string) => {
  const [isEnabled, setIsEnabled] = useState(false);

  useEffect(() => {
    const checkFeatureFlag = async () => {
      try {
        const response = await api.get(`/feature-flags/${flagName}`, {
          params: { warehouse_id: warehouseId }
        });
        setIsEnabled(response.data.enabled);
      } catch (error) {
        setIsEnabled(false);
      }
    };

    checkFeatureFlag();
  }, [flagName, warehouseId]);

  return isEnabled;
};

// Enhanced wizard with feature toggle
const TemplateCreationWizard: React.FC = () => {
  const unitAgnosticEnabled = useFeatureFlag('unit_agnostic_scope', warehouseId);

  const steps = [
    { component: Step1TemplateInfo },
    { component: Step2WarehouseStructure },
    ...(unitAgnosticEnabled ? [{ component: Step3AnalysisScope }] : []),
    { component: Step4SpecialAreas },
    { component: Step5ReviewCreate }
  ];

  // Rest of wizard logic...
};
```

#### 5.2 Data Migration Scripts

**Migration for Existing Locations**
```python
# backend/src/migrations/migrate_existing_locations.py

def migrate_existing_locations():
    """
    Migrate existing location data to support unit-agnostic tracking
    """
    print("Starting location migration...")

    # Get all existing warehouses
    warehouses = WarehouseConfig.query.all()

    for warehouse in warehouses:
        print(f"Migrating warehouse {warehouse.warehouse_id}")

        # Create default scope configuration
        create_default_scope_config(warehouse.warehouse_id)

        # Migrate existing locations
        migrate_warehouse_locations(warehouse.warehouse_id)

    print("Location migration completed")

def create_default_scope_config(warehouse_id: int):
    """Create default scope configuration for existing warehouse"""

    # Check if scope already exists
    existing_scope = WarehouseAnalysisScope.query.filter_by(
        warehouse_id=warehouse_id
    ).first()

    if existing_scope:
        print(f"Scope already exists for warehouse {warehouse_id}")
        return

    # Create default scope that includes all current locations
    default_scope = WarehouseAnalysisScope(
        warehouse_id=warehouse_id,
        scope_name="Default Scope",
        location_patterns=["*"],  # Include all patterns
        excluded_patterns=[],     # Exclude nothing
        unit_type_filters={"default": "pallets"},
        capacity_overrides={},
        is_active=True
    )

    db.session.add(default_scope)
    db.session.commit()

    print(f"Created default scope for warehouse {warehouse_id}")

def migrate_warehouse_locations(warehouse_id: int):
    """Migrate existing location records to support unit-agnostic tracking"""

    locations = Location.query.filter_by(warehouse_id=warehouse_id).all()

    for location in locations:
        # Determine unit type based on location characteristics
        unit_type = infer_unit_type_from_location(location)

        # Update location with inferred unit type
        location.unit_type = unit_type
        location.is_tracked = True
        location.user_defined = False  # These are migrated, not user-created

        # Create scope mapping
        scope_mapping = LocationScopeMapping(
            warehouse_id=warehouse_id,
            location_code=location.code,
            is_in_scope=True,
            unit_type=unit_type,
            scope_reason='template_generated'
        )

        db.session.add(scope_mapping)

    db.session.commit()
    print(f"Migrated {len(locations)} locations for warehouse {warehouse_id}")

def infer_unit_type_from_location(location: Location) -> str:
    """Infer unit type based on location characteristics"""

    code = location.code.upper()
    location_type = location.location_type.upper() if location.location_type else ""

    # Inference rules based on common patterns
    if any(pattern in code for pattern in ['PICK', 'W-', 'BIN', 'SHELF']):
        return 'items'
    elif any(pattern in code for pattern in ['CASE', 'CARTON']):
        return 'boxes'
    elif any(pattern in location_type for pattern in ['RECEIVING', 'STAGING', 'DOCK']):
        return 'mixed'
    else:
        return 'pallets'  # Default for storage locations
```

#### 5.3 Rollback Strategy

**Database Rollback Script**
```sql
-- Rollback Script: rollback_001_unit_agnostic.sql

-- Step 1: Drop new tables
DROP TABLE IF EXISTS analysis_scope_metrics;
DROP TABLE IF EXISTS scope_change_log;
DROP TABLE IF EXISTS location_scope_mapping;
DROP TABLE IF EXISTS warehouse_analysis_scope;

-- Step 2: Remove new columns from location table
ALTER TABLE location DROP COLUMN IF EXISTS custom_metadata;
ALTER TABLE location DROP COLUMN IF EXISTS tracking_priority;
ALTER TABLE location DROP COLUMN IF EXISTS user_defined;
ALTER TABLE location DROP COLUMN IF EXISTS is_tracked;
ALTER TABLE location DROP COLUMN IF EXISTS unit_type;

-- Step 3: Drop indexes
DROP INDEX IF EXISTS idx_location_tracked;
DROP INDEX IF EXISTS idx_location_user_defined;
DROP INDEX IF EXISTS idx_location_unit_type;
```

**Application Rollback**
```python
# backend/src/rollback_unit_agnostic.py

def rollback_unit_agnostic_features():
    """Rollback unit-agnostic features"""

    # Disable feature flags
    disable_feature_flags()

    # Clear scope service caches
    clear_scope_caches()

    # Revert rule engine to original behavior
    revert_rule_engine()

    print("Unit-agnostic features rolled back successfully")

def disable_feature_flags():
    """Disable all unit-agnostic feature flags"""
    WarehouseFeatureFlag.query.filter_by(
        feature_name='unit_agnostic_scope'
    ).delete()
    db.session.commit()

def clear_scope_caches():
    """Clear all scope-related caches"""
    # Clear Redis cache if using Redis
    # Clear application-level caches
    pass

def revert_rule_engine():
    """Ensure rule engine uses original logic"""
    # Set environment variable to force disable
    os.environ['FEATURE_UNIT_AGNOSTIC_SCOPE'] = 'false'
```

### 6. Testing Strategy

#### 6.1 Unit Testing

**Backend Service Tests**
```python
# tests/services/test_scope_management_service.py

import pytest
import pandas as pd
from services.scope_management_service import ScopeManagementService
from models import WarehouseAnalysisScope, LocationScopeMapping

class TestScopeManagementService:
    def setup_method(self):
        self.warehouse_id = 1
        self.scope_service = ScopeManagementService(self.warehouse_id)

    def test_apply_scope_filter_basic(self):
        """Test basic scope filtering functionality"""
        # Setup test data
        inventory_data = pd.DataFrame({
            'location': ['BULK-A-001', 'W-10', 'SHELF-01', 'RECV-01'],
            'pallet_id': ['P001', 'P002', 'P003', 'P004'],
            'quantity': [5, 30, 100, 15]
        })

        # Mock scope configuration
        self.scope_service._scope_cache = {
            'location_patterns': [
                {'pattern': 'BULK-*', 'unit_type': 'pallets'},
                {'pattern': 'W-*', 'unit_type': 'items'},
                {'pattern': 'RECV-*', 'unit_type': 'mixed'}
            ],
            'excluded_patterns': ['SHELF-*']
        }

        filtered_df, metrics = self.scope_service.apply_scope_filter(inventory_data)

        assert len(filtered_df) == 3
        assert 'SHELF-01' not in filtered_df['location'].values
        assert metrics['in_scope_records'] == 3
        assert metrics['out_of_scope_records'] == 1

    def test_pattern_matching_wildcards(self):
        """Test wildcard pattern matching"""
        assert self.scope_service._matches_pattern('BULK-A-001', 'BULK-*')
        assert self.scope_service._matches_pattern('W-10', 'W-*')
        assert not self.scope_service._matches_pattern('SHELF-01', 'BULK-*')

    def test_get_location_unit_type(self):
        """Test unit type determination"""
        self.scope_service._scope_cache = {
            'location_patterns': [
                {'pattern': 'BULK-*', 'unit_type': 'pallets'},
                {'pattern': 'W-*', 'unit_type': 'items'}
            ],
            'unit_type_overrides': {'SPECIAL-01': 'mixed'}
        }

        assert self.scope_service.get_location_unit_type('BULK-A-001') == 'pallets'
        assert self.scope_service.get_location_unit_type('W-10') == 'items'
        assert self.scope_service.get_location_unit_type('SPECIAL-01') == 'mixed'
        assert self.scope_service.get_location_unit_type('UNKNOWN') == 'pallets'

    def test_get_location_capacity(self):
        """Test capacity determination"""
        # Test with overrides, database records, and pattern defaults
        pass

# tests/test_rule_engine_unit_agnostic.py

class TestUnitAgnosticRuleEngine:
    def test_overcapacity_pallets(self):
        """Test overcapacity detection for pallet locations"""
        inventory_data = pd.DataFrame({
            'location': ['BULK-A-001'] * 6,  # 6 pallets in 5-pallet location
            'pallet_id': ['P001', 'P002', 'P003', 'P004', 'P005', 'P006']
        })

        # Mock scope service to return pallet type and capacity 5
        mock_scope_service = Mock()
        mock_scope_service.get_location_unit_type.return_value = 'pallets'
        mock_scope_service.get_location_capacity.return_value = 5

        evaluator = OvercapacityEvaluator()
        anomalies = evaluator.evaluate(
            mock_rule,
            inventory_data,
            {'scope_service': mock_scope_service}
        )

        assert len(anomalies) == 6  # Individual pallet anomalies
        for anomaly in anomalies:
            assert anomaly['anomaly_type'] == 'OVERCAPACITY'
            assert 'pallets' in anomaly['description']

    def test_overcapacity_items(self):
        """Test overcapacity detection for item locations"""
        inventory_data = pd.DataFrame({
            'location': ['W-10'] * 35,  # 35 items in 30-item location
            'item_id': [f'I{i:03d}' for i in range(35)]
        })

        mock_scope_service = Mock()
        mock_scope_service.get_location_unit_type.return_value = 'items'
        mock_scope_service.get_location_capacity.return_value = 30

        evaluator = OvercapacityEvaluator()
        anomalies = evaluator.evaluate(
            mock_rule,
            inventory_data,
            {'scope_service': mock_scope_service}
        )

        assert len(anomalies) == 1  # Single location-level anomaly
        assert anomalies[0]['anomaly_type'] == 'OVERCAPACITY_LOCATION'
        assert 'items' in anomalies[0]['description']
        assert anomalies[0]['details']['affected_items'] == 35
```

**Frontend Component Tests**
```typescript
// tests/components/locations/test-scope-definition.test.tsx

import { render, screen, fireEvent } from '@testing-library/react';
import { Step3AnalysisScope } from '../../../components/locations/templates/template-creation-wizard';

describe('Step3AnalysisScope', () => {
  const mockScopeConfig = {
    scopeName: 'Test Scope',
    locationPatterns: [],
    excludedPatterns: [],
    capacityOverrides: {},
    unitTypeOverrides: {}
  };

  const mockProps = {
    scopeConfig: mockScopeConfig,
    onScopeChange: jest.fn(),
    onNext: jest.fn(),
    onPrev: jest.fn()
  };

  test('renders scope definition interface', () => {
    render(<Step3AnalysisScope {...mockProps} />);

    expect(screen.getByText('Define Analysis Scope')).toBeInTheDocument();
    expect(screen.getByText('Locations to Analyze')).toBeInTheDocument();
    expect(screen.getByText('Locations to Ignore')).toBeInTheDocument();
  });

  test('adds new location pattern', () => {
    render(<Step3AnalysisScope {...mockProps} />);

    const addButton = screen.getByText('Add Location Pattern');
    fireEvent.click(addButton);

    expect(screen.getByPlaceholderText('e.g., BULK-*, W-*, 001A-999Z')).toBeInTheDocument();
    expect(mockProps.onScopeChange).toHaveBeenCalled();
  });

  test('updates pattern configuration', () => {
    const propsWithPattern = {
      ...mockProps,
      scopeConfig: {
        ...mockScopeConfig,
        locationPatterns: [{
          pattern: 'BULK-*',
          unitType: 'pallets',
          defaultCapacity: 5,
          locationTypes: ['STORAGE'],
          isTracked: true
        }]
      }
    };

    render(<Step3AnalysisScope {...propsWithPattern} />);

    const patternInput = screen.getByDisplayValue('BULK-*');
    fireEvent.change(patternInput, { target: { value: 'BULK-A-*' } });

    expect(mockProps.onScopeChange).toHaveBeenCalledWith(
      expect.objectContaining({
        locationPatterns: expect.arrayContaining([
          expect.objectContaining({ pattern: 'BULK-A-*' })
        ])
      })
    );
  });

  test('prevents next step with empty patterns', () => {
    render(<Step3AnalysisScope {...mockProps} />);

    const nextButton = screen.getByText('Next: Special Areas');
    expect(nextButton).toBeDisabled();
  });

  test('enables next step with valid patterns', () => {
    const propsWithPattern = {
      ...mockProps,
      scopeConfig: {
        ...mockScopeConfig,
        locationPatterns: [{
          pattern: 'BULK-*',
          unitType: 'pallets',
          defaultCapacity: 5,
          locationTypes: ['STORAGE'],
          isTracked: true
        }]
      }
    };

    render(<Step3AnalysisScope {...propsWithPattern} />);

    const nextButton = screen.getByText('Next: Special Areas');
    expect(nextButton).not.toBeDisabled();
  });
});
```

#### 6.2 Integration Testing

**API Integration Tests**
```python
# tests/integration/test_scope_api_integration.py

class TestScopeAPIIntegration:
    def test_warehouse_scope_crud_operations(self):
        """Test complete CRUD operations for warehouse scope"""

        # Create warehouse scope
        scope_data = {
            'location_patterns': [
                {'pattern': 'BULK-*', 'unit_type': 'pallets', 'default_capacity': 5},
                {'pattern': 'W-*', 'unit_type': 'items', 'default_capacity': 30}
            ],
            'excluded_patterns': ['SHELF-*', 'BIN-*'],
            'capacity_overrides': {'RECV-01': 50}
        }

        # POST /api/v1/warehouses/1/scope
        response = self.client.post('/api/v1/warehouses/1/scope', json=scope_data)
        assert response.status_code == 201

        # GET /api/v1/warehouses/1/scope
        response = self.client.get('/api/v1/warehouses/1/scope')
        assert response.status_code == 200

        returned_scope = response.json
        assert len(returned_scope['location_patterns']) == 2
        assert 'SHELF-*' in returned_scope['excluded_patterns']

        # PUT /api/v1/warehouses/1/scope (update)
        updated_data = {**scope_data, 'excluded_patterns': ['SHELF-*', 'BIN-*', 'TEMP-*']}
        response = self.client.put('/api/v1/warehouses/1/scope', json=updated_data)
        assert response.status_code == 200

        # Verify update
        response = self.client.get('/api/v1/warehouses/1/scope')
        assert 'TEMP-*' in response.json['excluded_patterns']

    def test_location_scope_validation(self):
        """Test location validation against scope"""

        # Setup scope
        scope_data = {
            'location_patterns': [{'pattern': 'BULK-*', 'unit_type': 'pallets'}],
            'excluded_patterns': ['SHELF-*']
        }
        self.client.post('/api/v1/warehouses/1/scope', json=scope_data)

        # Validate locations
        validation_request = {
            'location_codes': ['BULK-A-001', 'W-10', 'SHELF-01'],
            'warehouse_id': 1
        }

        response = self.client.get('/api/v1/locations/scope/validate', params=validation_request)
        assert response.status_code == 200

        results = response.json['validation_results']
        bulk_result = next(r for r in results if r['code'] == 'BULK-A-001')
        shelf_result = next(r for r in results if r['code'] == 'SHELF-01')

        assert bulk_result['in_scope'] == True
        assert shelf_result['in_scope'] == False
        assert shelf_result['reason'] == 'excluded_pattern'

    def test_analysis_with_scope_filtering(self):
        """Test end-to-end analysis with scope filtering"""

        # Setup scope
        scope_data = {
            'location_patterns': [
                {'pattern': 'BULK-*', 'unit_type': 'pallets', 'default_capacity': 5}
            ],
            'excluded_patterns': ['SHELF-*']
        }
        self.client.post('/api/v1/warehouses/1/scope', json=scope_data)

        # Upload inventory file with mixed data
        inventory_file = self.create_test_inventory_file({
            'BULK-A-001': 6,  # Overcapacity (should trigger)
            'SHELF-01': 100,  # Out of scope (should be ignored)
            'BULK-B-001': 3   # Normal (should not trigger)
        })

        # Submit analysis
        response = self.client.post('/api/v1/reports',
            files={'inventory_file': inventory_file},
            data={
                'column_mapping': '{"location": "Location", "pallet_id": "Pallet ID"}',
                'scope_settings': '{"apply_scope_filter": true}'
            }
        )

        assert response.status_code == 200
        result = response.json

        # Verify scope metrics
        assert result['scope_analysis']['total_records'] == 109  # 6 + 100 + 3
        assert result['scope_analysis']['in_scope_records'] == 9  # 6 + 3
        assert result['scope_analysis']['out_of_scope_records'] == 100

        # Verify anomalies only from in-scope locations
        overcapacity_anomalies = [a for a in result['anomalies'] if a['anomaly_type'] == 'OVERCAPACITY']
        assert len(overcapacity_anomalies) == 6  # Only from BULK-A-001
        assert all('BULK-A-001' in a['location'] for a in overcapacity_anomalies)
        assert not any('SHELF-01' in str(a) for a in result['anomalies'])
```

#### 6.3 End-to-End Testing

**E2E Test Scenarios**
```typescript
// tests/e2e/unit-agnostic-warehouse-setup.spec.ts

import { test, expect } from '@playwright/test';

test.describe('Unit-Agnostic Warehouse Setup', () => {
  test('complete warehouse setup with mixed unit types', async ({ page }) => {
    // Navigate to warehouse setup
    await page.goto('/dashboard/locations');
    await page.click('[data-testid="setup-warehouse-button"]');

    // Step 1: Template Information
    await page.fill('[data-testid="template-name"]', 'Mixed Operations Warehouse');
    await page.selectOption('[data-testid="industry-select"]', 'E-commerce');
    await page.click('[data-testid="next-button"]');

    // Step 2: Warehouse Structure
    await page.fill('[data-testid="aisles-input"]', '10');
    await page.fill('[data-testid="racks-input"]', '20');
    await page.fill('[data-testid="positions-input"]', '5');
    await page.click('[data-testid="next-button"]');

    // Step 3: Analysis Scope (NEW)
    await expect(page.locator('h3')).toContainText('Define Analysis Scope');

    // Add storage pattern
    await page.click('[data-testid="add-pattern-button"]');
    await page.fill('[data-testid="pattern-input-0"]', 'STOR-*');
    await page.selectOption('[data-testid="unit-type-select-0"]', 'pallets');
    await page.fill('[data-testid="capacity-input-0"]', '5');

    // Add pick area pattern
    await page.click('[data-testid="add-pattern-button"]');
    await page.fill('[data-testid="pattern-input-1"]', 'PICK-*');
    await page.selectOption('[data-testid="unit-type-select-1"]', 'items');
    await page.fill('[data-testid="capacity-input-1"]', '50');

    // Add excluded pattern
    await page.click('[data-testid="add-excluded-pattern"]');
    await page.fill('[data-testid="excluded-pattern-0"]', 'SHELF-*');

    // Verify preview
    await expect(page.locator('[data-testid="scope-preview"]')).toContainText('STOR-* (pallets, max 5 each)');
    await expect(page.locator('[data-testid="scope-preview"]')).toContainText('PICK-* (items, max 50 each)');
    await expect(page.locator('[data-testid="scope-preview"]')).toContainText('SHELF-*');

    await page.click('[data-testid="next-button"]');

    // Continue with remaining steps...
    // Step 4: Special Areas
    await page.click('[data-testid="next-button"]');

    // Step 5: Review & Create
    await expect(page.locator('[data-testid="review-scope"]')).toContainText('2 location patterns');
    await expect(page.locator('[data-testid="review-scope"]')).toContainText('1 excluded pattern');

    await page.click('[data-testid="create-warehouse-button"]');

    // Verify success
    await expect(page.locator('[data-testid="success-message"]')).toContainText('warehouse is ready');
  });

  test('upload and analyze mixed granularity inventory', async ({ page }) => {
    // Setup: Create warehouse with scope configuration
    await setupMixedUnitWarehouse(page);

    // Navigate to analysis page
    await page.goto('/dashboard/analysis');

    // Upload mixed inventory file
    const fileInput = page.locator('[data-testid="inventory-file-input"]');
    await fileInput.setInputFiles('tests/fixtures/mixed_inventory.xlsx');

    // Verify scope analysis in upload feedback
    await expect(page.locator('[data-testid="scope-analysis"]')).toContainText('1,247 records analyzed');
    await expect(page.locator('[data-testid="scope-analysis"]')).toContainText('3,276 records ignored');

    // Submit analysis
    await page.click('[data-testid="analyze-button"]');

    // Wait for results
    await page.waitForSelector('[data-testid="analysis-results"]');

    // Verify scope summary in results
    await expect(page.locator('[data-testid="scope-summary"]')).toContainText('Records Analyzed: 1,247');
    await expect(page.locator('[data-testid="scope-summary"]')).toContainText('Records Ignored: 3,276');

    // Verify anomalies are only from in-scope locations
    const anomalyRows = page.locator('[data-testid="anomaly-row"]');
    const anomalyCount = await anomalyRows.count();

    for (let i = 0; i < anomalyCount; i++) {
      const location = await anomalyRows.nth(i).locator('[data-testid="location"]').textContent();
      expect(location).not.toMatch(/^SHELF-/); // Should not contain excluded locations
    }

    // Test scope modification
    await page.click('[data-testid="modify-scope-button"]');
    // Verify scope editor opens with current configuration
    await expect(page.locator('[data-testid="scope-editor"]')).toBeVisible();
  });
});
```

#### 6.4 Performance Testing

**Load Testing for Scope Filtering**
```python
# tests/performance/test_scope_performance.py

import pytest
import time
import pandas as pd
from services.scope_management_service import ScopeManagementService

class TestScopePerformance:
    def test_large_dataset_scope_filtering(self):
        """Test scope filtering performance with large datasets"""

        # Create large test dataset (100k records)
        large_inventory = pd.DataFrame({
            'location': [f'LOC-{i:06d}' for i in range(100000)],
            'pallet_id': [f'P{i:06d}' for i in range(100000)],
            'quantity': [1] * 100000
        })

        scope_service = ScopeManagementService(warehouse_id=1)

        # Mock scope configuration with patterns
        scope_service._scope_cache = {
            'location_patterns': [
                {'pattern': 'LOC-0*', 'unit_type': 'pallets'},  # Matches 10k locations
                {'pattern': 'LOC-1*', 'unit_type': 'items'}     # Matches 10k locations
            ],
            'excluded_patterns': ['LOC-9*']  # Excludes 10k locations
        }

        # Measure filtering performance
        start_time = time.time()
        filtered_df, metrics = scope_service.apply_scope_filter(large_inventory)
        execution_time = time.time() - start_time

        # Performance assertions
        assert execution_time < 2.0  # Should complete in under 2 seconds
        assert len(filtered_df) == 20000  # 20k records should match patterns
        assert metrics['out_of_scope_records'] == 80000

    def test_pattern_matching_performance(self):
        """Test pattern matching performance with complex patterns"""

        scope_service = ScopeManagementService(warehouse_id=1)
        test_locations = [f'TEST-{chr(65+i)}-{j:03d}' for i in range(26) for j in range(1000)]

        start_time = time.time()
        for location in test_locations:
            scope_service._matches_pattern(location, 'TEST-*-*')
        execution_time = time.time() - start_time

        assert execution_time < 1.0  # 26k pattern matches in under 1 second

    def test_rule_engine_performance_with_scope(self):
        """Test rule engine performance with scope filtering enabled"""

        # Large inventory dataset
        inventory_df = pd.DataFrame({
            'location': [f'BULK-{i:04d}' for i in range(1000)] * 10,  # 10k records
            'pallet_id': [f'P{i:05d}' for i in range(10000)],
            'quantity': [1] * 10000
        })

        # Create rule engine with scope service
        rule_engine = RuleEngine(warehouse_context={'warehouse_id': 1})

        # Measure end-to-end processing time
        start_time = time.time()
        results = rule_engine.evaluate_rules(inventory_df, apply_scope_filter=True)
        execution_time = time.time() - start_time

        # Performance requirements
        assert execution_time < 5.0  # Complete analysis in under 5 seconds
        assert 'scope_metrics' in results
        assert results['scope_metrics']['processing_time_ms'] < 500  # Scope filtering overhead < 500ms
```

#### 6.5 User Acceptance Testing

**UAT Test Scenarios**
```markdown
# Unit-Agnostic Warehouse Intelligence - UAT Test Cases

## Test Case 1: Warehouse Manager with Mixed Operations
**User**: Small e-commerce warehouse manager
**Scenario**: Setup warehouse that tracks pallets in storage and individual items in pick areas

**Steps**:
1. Access warehouse setup wizard
2. Define location patterns:
   - Storage: STOR-* (pallets, capacity 5)
   - Pick areas: PICK-* (items, capacity 100)
   - Exclude: SHELF-* patterns
3. Upload mixed inventory file (5000 records total)
4. Verify scope filtering results
5. Analyze anomalies and confirm relevance

**Expected Outcome**:
- Setup completes without confusion
- Scope filtering works transparently
- Anomalies are relevant to defined operations
- No false positives from excluded areas

## Test Case 2: Large Distribution Center
**User**: Enterprise warehouse operations manager
**Scenario**: Complex warehouse with multiple unit types and operational zones

**Steps**:
1. Setup warehouse with 5+ location patterns
2. Define capacity overrides for specific locations
3. Upload large inventory file (50k+ records)
4. Process analysis and review performance
5. Modify scope configuration and re-analyze

**Expected Outcome**:
- Performance remains acceptable with large datasets
- Scope modifications apply correctly
- Results remain consistent and accurate
- System handles enterprise scale smoothly

## Test Case 3: Migration from Existing System
**User**: Current WareWise user upgrading to unit-agnostic features
**Scenario**: Existing pallet-only warehouse wants to add item tracking

**Steps**:
1. Access existing warehouse configuration
2. Enable unit-agnostic features
3. Add new location patterns for item areas
4. Upload file with new mixed data
5. Compare results with previous pallet-only analysis

**Expected Outcome**:
- Migration is seamless and non-disruptive
- Existing configurations continue to work
- New features are additive, not replacement
- Historical data and patterns remain intact
```

#### 6.6 Monitoring and Observability Testing

**Production Monitoring Tests**
```python
# tests/monitoring/test_scope_metrics.py

class TestScopeMetrics:
    def test_scope_metrics_collection(self):
        """Test that scope metrics are properly collected and stored"""

        # Perform analysis with scope filtering
        response = self.client.post('/api/v1/reports',
            files={'inventory_file': test_file},
            data={'scope_settings': '{"apply_scope_filter": true}'}
        )

        # Verify metrics are stored in database
        metrics = AnalysisScopeMetrics.query.filter_by(
            warehouse_id=1
        ).order_by(AnalysisScopeMetrics.analysis_date.desc()).first()

        assert metrics is not None
        assert metrics.total_records > 0
        assert metrics.in_scope_records > 0
        assert metrics.processing_time_ms > 0

    def test_scope_performance_monitoring(self):
        """Test performance monitoring for scope operations"""

        # Monitor scope filtering performance over multiple requests
        performance_data = []

        for i in range(10):
            start_time = time.time()
            self.client.post('/api/v1/reports', files={'inventory_file': test_file})
            end_time = time.time()
            performance_data.append(end_time - start_time)

        # Verify performance is consistent
        avg_time = sum(performance_data) / len(performance_data)
        max_time = max(performance_data)

        assert avg_time < 3.0  # Average under 3 seconds
        assert max_time < 5.0  # No request over 5 seconds
        assert max(performance_data) / min(performance_data) < 2.0  # Consistent performance
```

---

## 7. Implementation Timeline & Deliverables

### Phase 1: Foundation (Weeks 1-2)
**Duration**: 2 weeks
**Team**: 2 Backend Developers, 1 Database Engineer

**Week 1 Deliverables:**
- ✅ Database schema migration scripts
- ✅ ScopeManagementService implementation
- ✅ Basic API endpoints for scope management
- ✅ Unit tests for core scope functionality
- ✅ Feature flag system implementation

**Week 2 Deliverables:**
- ✅ Rule engine integration with scope filtering
- ✅ Enhanced overcapacity evaluator
- ✅ API integration tests
- ✅ Performance baseline testing
- ✅ Migration scripts for existing data

### Phase 2: Frontend Integration (Weeks 2-3)
**Duration**: 2 weeks (parallel with Phase 1 Week 2)
**Team**: 2 Frontend Developers, 1 UI/UX Designer

**Week 2-3 Deliverables:**
- ✅ Enhanced template creation wizard (Step 3: Analysis Scope)
- ✅ Scope management interface components
- ✅ Analysis results enhancement with scope metrics
- ✅ Frontend unit and integration tests
- ✅ Feature flag integration for progressive rollout

### Phase 3: Testing & Validation (Week 3-4)
**Duration**: 2 weeks (parallel with Phase 2)
**Team**: 2 QA Engineers, 1 Performance Engineer

**Week 3-4 Deliverables:**
- ✅ End-to-end test suite
- ✅ Performance testing with large datasets
- ✅ User acceptance testing scenarios
- ✅ Load testing for scope filtering operations
- ✅ Security testing for new API endpoints

### Phase 4: Production Deployment (Week 4-5)
**Duration**: 2 weeks
**Team**: 1 DevOps Engineer, Full Development Team

**Week 4-5 Deliverables:**
- ✅ Production deployment scripts
- ✅ Monitoring and alerting setup
- ✅ Rollback procedures tested
- ✅ Documentation and training materials
- ✅ Feature flag controlled rollout

---

## 8. Risk Mitigation & Monitoring

### Critical Success Factors

#### 8.1 Performance Monitoring
```python
# Monitoring metrics to track
SCOPE_PERFORMANCE_METRICS = {
    'scope_filtering_time_ms': 'Time taken for scope filtering operations',
    'scope_filter_coverage_ratio': 'Percentage of records remaining after filtering',
    'scope_pattern_match_efficiency': 'Pattern matching performance',
    'rule_engine_total_time_ms': 'Total rule engine execution time with scope',
    'user_scope_modification_frequency': 'How often users modify scope settings'
}

# Alert thresholds
PERFORMANCE_ALERTS = {
    'scope_filtering_time_ms': 1000,  # Alert if >1 second
    'rule_engine_total_time_ms': 5000,  # Alert if >5 seconds
    'scope_filter_coverage_ratio': 0.05,  # Alert if <5% records in scope
}
```

#### 8.2 Business Impact Tracking
```sql
-- Business metrics to monitor
CREATE VIEW unit_agnostic_business_metrics AS
SELECT
    DATE(created_at) as date,
    COUNT(DISTINCT warehouse_id) as warehouses_using_scope,
    AVG(in_scope_records::float / total_records) as avg_scope_coverage,
    COUNT(*) as total_analyses,
    AVG(processing_time_ms) as avg_processing_time
FROM analysis_scope_metrics
WHERE created_at >= CURRENT_DATE - INTERVAL '30 days'
GROUP BY DATE(created_at);
```

#### 8.3 User Adoption Metrics
- **Scope Configuration Completion Rate**: % of users who complete scope setup
- **Scope Modification Rate**: How often users adjust their initial scope
- **Feature Utilization**: % of analyses using scope filtering
- **User Satisfaction**: Feedback scores for scope management experience

### Rollback Triggers

**Immediate Rollback Required If:**
- Scope filtering causes >20% performance degradation
- >10% of scope configurations fail to save
- Critical rule engine errors increase by >50%
- User completion rate drops below 70%

**Gradual Rollback Triggers:**
- User satisfaction scores below 3.5/5
- Support tickets related to scope functionality exceed 15% of total
- Performance metrics consistently exceed alert thresholds
- False positive anomaly rates increase significantly

---

## 9. Success Metrics & Validation

### Technical Success Criteria
- ✅ **Performance**: <10% increase in processing time with scope filtering
- ✅ **Accuracy**: 95%+ of scope filtering operations work correctly
- ✅ **Reliability**: 99.9% uptime for scope-related functionality
- ✅ **Scalability**: Handle 100k+ records with scope filtering <2 seconds

### Business Success Criteria
- ✅ **Market Expansion**: 40%+ increase in addressable warehouse types
- ✅ **User Adoption**: 85%+ of new users complete scope setup
- ✅ **False Positive Reduction**: 80%+ reduction in irrelevant anomalies
- ✅ **User Satisfaction**: 4.5+/5.0 rating on scope management features

### User Experience Success Criteria
- ✅ **Setup Simplicity**: 90%+ of users understand scope concept without training
- ✅ **Configuration Accuracy**: <20% of users need to modify scope after initial setup
- ✅ **Feature Discovery**: 70%+ of users discover scope benefits within first session
- ✅ **Workflow Integration**: Scope management feels natural to warehouse operations

---

**Document Status**: ✅ Complete - Ready for Implementation
**Technical Review**: Pending
**Architecture Approval**: Pending
**Implementation Start**: Ready to Begin

---

*This technical design provides the complete blueprint for implementing unit-agnostic warehouse intelligence in WareWise. All technical components, integration patterns, migration strategies, and testing approaches are fully specified and ready for development team execution.*

<function_calls>
<invoke name="TodoWrite">
<parameter name="todos">[{"content": "Analyze current architecture from concept document", "status": "completed", "activeForm": "Analyzing current architecture from concept document"}, {"content": "Design database schema changes for unit-agnostic tracking", "status": "completed", "activeForm": "Designing database schema changes for unit-agnostic tracking"}, {"content": "Specify backend API enhancements for scope management", "status": "completed", "activeForm": "Specifying backend API enhancements for scope management"}, {"content": "Design frontend wizard enhancements for location scope definition", "status": "completed", "activeForm": "Designing frontend wizard enhancements for location scope definition"}, {"content": "Detail rule engine modifications for scope filtering", "status": "completed", "activeForm": "Detailing rule engine modifications for scope filtering"}, {"content": "Create migration strategy for existing installations", "status": "completed", "activeForm": "Creating migration strategy for existing installations"}, {"content": "Define testing strategy for unit-agnostic functionality", "status": "completed", "activeForm": "Defining testing strategy for unit-agnostic functionality"}]

<function_calls>
<invoke name="TodoWrite">
<parameter name="todos">[{"content": "Analyze current architecture from concept document", "status": "completed", "activeForm": "Analyzing current architecture from concept document"}, {"content": "Design database schema changes for unit-agnostic tracking", "status": "completed", "activeForm": "Designing database schema changes for unit-agnostic tracking"}, {"content": "Specify backend API enhancements for scope management", "status": "completed", "activeForm": "Specifying backend API enhancements for scope management"}, {"content": "Design frontend wizard enhancements for location scope definition", "status": "completed", "activeForm": "Designing frontend wizard enhancements for location scope definition"}, {"content": "Detail rule engine modifications for scope filtering", "status": "completed", "activeForm": "Detailing rule engine modifications for scope filtering"}, {"content": "Create migration strategy for existing installations", "status": "completed", "activeForm": "Creating migration strategy for existing installations"}, {"content": "Define testing strategy for unit-agnostic functionality", "status": "in_progress", "activeForm": "Defining testing strategy for unit-agnostic functionality"}]

<function_calls>
<invoke name="TodoWrite">
<parameter name="todos">[{"content": "Analyze current architecture from concept document", "status": "completed", "activeForm": "Analyzing current architecture from concept document"}, {"content": "Design database schema changes for unit-agnostic tracking", "status": "completed", "activeForm": "Designing database schema changes for unit-agnostic tracking"}, {"content": "Specify backend API enhancements for scope management", "status": "completed", "activeForm": "Specifying backend API enhancements for scope management"}, {"content": "Design frontend wizard enhancements for location scope definition", "status": "completed", "activeForm": "Designing frontend wizard enhancements for location scope definition"}, {"content": "Detail rule engine modifications for scope filtering", "status": "completed", "activeForm": "Detailing rule engine modifications for scope filtering"}, {"content": "Create migration strategy for existing installations", "status": "in_progress", "activeForm": "Creating migration strategy for existing installations"}, {"content": "Define testing strategy for unit-agnostic functionality", "status": "pending", "activeForm": "Defining testing strategy for unit-agnostic functionality"}]

<function_calls>
<invoke name="TodoWrite">
<parameter name="todos">[{"content": "Analyze current architecture from concept document", "status": "completed", "activeForm": "Analyzing current architecture from concept document"}, {"content": "Design database schema changes for unit-agnostic tracking", "status": "in_progress", "activeForm": "Designing database schema changes for unit-agnostic tracking"}, {"content": "Specify backend API enhancements for scope management", "status": "pending", "activeForm": "Specifying backend API enhancements for scope management"}, {"content": "Design frontend wizard enhancements for location scope definition", "status": "pending", "activeForm": "Designing frontend wizard enhancements for location scope definition"}, {"content": "Detail rule engine modifications for scope filtering", "status": "pending", "activeForm": "Detailing rule engine modifications for scope filtering"}, {"content": "Create migration strategy for existing installations", "status": "pending", "activeForm": "Creating migration strategy for existing installations"}, {"content": "Define testing strategy for unit-agnostic functionality", "status": "pending", "activeForm": "Defining testing strategy for unit-agnostic functionality"}]