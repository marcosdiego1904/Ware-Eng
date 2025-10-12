# Template Creation Interface - Complete Foundation Document

## Overview
This document provides a comprehensive foundation for designing a new template creation interface. It covers all UI/UX elements, backend capabilities, data structures, and design patterns from the existing system.

---

## 📋 Table of Contents
1. [System Architecture](#system-architecture)
2. [Data Models & Structures](#data-models--structures)
3. [Backend API Endpoints](#backend-api-endpoints)
4. [Frontend Components](#frontend-components)
5. [UI/UX Patterns](#uiux-patterns)
6. [Form Elements & Validation](#form-elements--validation)
7. [Smart Features](#smart-features)
8. [User Flows](#user-flows)
9. [Design Tokens & Styling](#design-tokens--styling)
10. [Best Practices](#best-practices)

---

## 1. System Architecture

### High-Level Flow
```
User Input → Template Creation Wizard → Backend Processing → Virtual/Physical Locations → Warehouse Ready
```

### Core Components
- **Template Creation Wizard** - 5-step progressive disclosure flow
- **Smart Format Detector** - ML-powered location pattern recognition
- **Virtual Template Manager** - Handles template application with virtual locations
- **Template Library** - Browse, search, and apply existing templates

### Dual-Mode Operation
Templates can be created in two modes:
1. **Standalone Mode** - Create reusable template for future use
2. **First-Time Setup Mode** - Create template AND immediately apply to warehouse

---

## 2. Data Models & Structures

### WarehouseTemplate Model (Backend)

**File:** `backend/src/models.py` (lines 636-786)

```python
class WarehouseTemplate(db.Model):
    # Basic Information
    id: Integer (Primary Key)
    name: String(120)                    # Required
    description: Text                    # Optional
    template_code: String(20) UNIQUE     # Auto-generated (e.g., "WAR-4A2R-X7Z")

    # Structure Configuration
    num_aisles: Integer                  # Required, min: 1
    racks_per_aisle: Integer             # Required, min: 1
    positions_per_rack: Integer          # Required, min: 1
    levels_per_position: Integer         # Default: 4
    level_names: String(20)              # Default: "ABCD"
    default_pallet_capacity: Integer     # Default: 1
    bidimensional_racks: Boolean         # Default: False

    # Special Areas (stored as JSON Text)
    receiving_areas_template: Text       # JSON array of area objects
    staging_areas_template: Text         # JSON array of area objects
    dock_areas_template: Text            # JSON array of area objects

    # Smart Location Format (AI-Detected)
    location_format_config: Text         # JSON config from SmartFormatDetector
    format_confidence: Float             # 0.0-1.0 confidence score
    format_examples: Text                # JSON array of user examples
    format_learned_date: DateTime        # When format was detected

    # Enterprise Features
    max_position_digits: Integer         # Default: 6 (supports up to 999,999 positions)

    # Metadata
    based_on_config_id: Integer FK       # If created from existing warehouse
    is_public: Boolean                   # Public/Private sharing
    usage_count: Integer                 # Track popularity

    # System Fields
    created_by: Integer FK (User)
    created_at: DateTime
    updated_at: DateTime
    is_active: Boolean                   # Soft delete flag
```

### Special Area Structure

Each special area (receiving/staging/dock/aisle) follows this structure:

```typescript
interface SpecialArea {
  code: string;        // e.g., "RECV-01", "DOCK-A", "AISLE-12"
  type: string;        // "RECEIVING" | "STAGING" | "DOCK" | "TRANSITIONAL"
  capacity: number;    // Pallet capacity
  zone: string;        // Zone identifier (e.g., "RECEIVING", "GENERAL")
}
```

**Default Capacities:**
- RECEIVING: 10 pallets
- STAGING: 5 pallets
- DOCK: 2 pallets
- TRANSITIONAL (Aisles): 10 pallets

### Location Format Configuration

The Smart Format Detector returns this structure:

```typescript
interface FormatDetectionResult {
  detected: boolean;
  format_config: {
    pattern_type: string;          // e.g., "position_level", "aisle_rack_position"
    canonical_format: string;      // Standardized format definition
    conversion_rules: object;      // Rules for converting to canonical
    validation_rules: object;      // Rules for validating location codes
    examples: string[];            // Canonical examples
    confidence: number;            // 0-100
  };
  confidence: number;              // 0-100
  pattern_name: string;            // Human-readable pattern name
  canonical_examples: string[];   // Converted examples
}
```

### Template Categories

```typescript
const TEMPLATE_CATEGORIES = [
  { value: 'MANUFACTURING', label: 'Manufacturing', description: 'Industrial production warehouses' },
  { value: 'RETAIL', label: 'Retail Distribution', description: 'Retail distribution centers' },
  { value: 'FOOD_BEVERAGE', label: 'Food & Beverage', description: 'Cold chain and food storage' },
  { value: 'PHARMA', label: 'Pharmaceutical', description: 'Controlled environment storage' },
  { value: 'AUTOMOTIVE', label: 'Automotive', description: 'Parts and assembly storage' },
  { value: 'ECOMMERCE', label: 'E-commerce', description: 'Fulfillment centers' },
  { value: 'CUSTOM', label: 'Custom', description: 'User-defined template' }
];
```

### Visibility/Sharing Options

```typescript
type TemplateVisibility = 'PRIVATE' | 'COMPANY' | 'PUBLIC';

// PRIVATE: Only creator can see/use
// COMPANY: Entire company team can access
// PUBLIC: Available in public template library
```

---

## 3. Backend API Endpoints

**Base URL:** `/api/v1/templates`

### Template CRUD Operations

#### 1. List Templates
```
GET /api/v1/templates
Query Parameters:
  - scope: 'my' | 'public' | 'all' (default: 'all')
  - page: integer (default: 1)
  - per_page: integer (default: 20, max: 50)
  - search: string (searches name, description, template_code)

Response:
{
  "templates": [Template[]],
  "pagination": {
    "page": 1,
    "per_page": 20,
    "total": 50,
    "pages": 3,
    "has_next": true,
    "has_prev": false
  },
  "summary": {
    "my_templates": 5,
    "public_templates": 45,
    "scope": "all"
  }
}
```

#### 2. Get Template by ID
```
GET /api/v1/templates/{template_id}

Response:
{
  "template": {
    "id": 1,
    "name": "Main Distribution Center",
    "description": "...",
    "template_code": "WAR-4A2R-X7Z",
    "num_aisles": 4,
    "racks_per_aisle": 2,
    "positions_per_rack": 50,
    "levels_per_position": 4,
    "level_names": "ABCD",
    "default_pallet_capacity": 1,
    "bidimensional_racks": false,
    "receiving_areas": [...],
    "staging_areas": [...],
    "dock_areas": [...],
    "location_format_config": {...},
    "format_confidence": 0.95,
    "format_examples": ["010A", "325B", "245D"],
    "is_public": false,
    "usage_count": 12,
    "created_by": 1,
    "creator_username": "john.doe",
    "created_at": "2025-01-15T10:30:00",
    "updated_at": "2025-01-15T10:30:00",
    "total_storage_locations": 1600,
    "total_capacity": 1600
  }
}
```

#### 3. Create Template
```
POST /api/v1/templates
Body:
{
  "name": "Main Distribution Center",
  "description": "Primary warehouse for automotive parts",
  "num_aisles": 4,
  "racks_per_aisle": 2,
  "positions_per_rack": 50,
  "levels_per_position": 4,
  "level_names": "ABCD",
  "default_pallet_capacity": 1,
  "bidimensional_racks": false,
  "is_public": false,

  // Optional: Special areas
  "receiving_areas": [
    { "code": "RECV-01", "type": "RECEIVING", "capacity": 10, "zone": "RECEIVING" }
  ],
  "staging_areas": [],
  "dock_areas": [],

  // Optional: Location format (nested structure)
  "location_format": {
    "format_config": {...},
    "confidence": 0.95,
    "examples": ["010A", "325B"]
  }
}

Response: 201 Created
{
  "message": "Template created successfully",
  "template": {Template object}
}
```

#### 4. Update Template
```
PUT /api/v1/templates/{template_id}
Body: Same as Create (all fields optional)

Response: 200 OK
{
  "message": "Template updated successfully",
  "template": {Template object}
}
```

#### 5. Delete Template (Soft Delete)
```
DELETE /api/v1/templates/{template_id}

Response: 200 OK
{
  "message": "Template deleted successfully"
}
```

### Template Application

#### 6. Apply Template by ID
```
POST /api/v1/templates/{template_id}/apply
Body:
{
  "warehouse_id": "WAREHOUSE_123",      // Optional, auto-generated if not provided
  "warehouse_name": "North Facility",
  "use_virtual_locations": true,        // Default: true (NEW: Virtual locations feature)
  "customizations": {                   // Optional
    "default_pallet_capacity": 2
  }
}

Response: 201 Created
{
  "message": "Template applied successfully using virtual_locations",
  "warehouse_id": "WAREHOUSE_123",
  "configuration": {WarehouseConfig object},
  "template_code": "WAR-4A2R-X7Z",
  "locations_created": 0,               // Physical locations created
  "virtual_locations_available": 1600,  // Virtual locations available
  "storage_locations": 1600,
  "special_areas": 4,
  "virtual_location_summary": {
    "total_virtual": 1600,
    "generation_method": "lazy",
    "benefits": ["instant_setup", "zero_storage", "dynamic_generation"]
  },
  "creation_method": "virtual_locations"
}
```

#### 7. Apply Template by Code
```
POST /api/v1/templates/apply-by-code
Body:
{
  "template_code": "WAR-4A2R-X7Z",
  "warehouse_id": "WAREHOUSE_123",
  "warehouse_name": "North Facility",
  "use_virtual_locations": true
}

Response: Same as Apply by ID
```

#### 8. Get Template by Code
```
GET /api/v1/templates/by-code/{template_code}

Response: Same as Get by ID
```

### Smart Format Detection

#### 9. Detect Location Format
```
POST /api/v1/templates/detect-format
Body:
{
  "examples": ["010A", "325B", "245D", "1230A", "5678C"],
  "warehouse_context": {                 // Optional
    "name": "Main Warehouse",
    "description": "Distribution center"
  }
}

Response: 200 OK
{
  "success": true,
  "detection_result": {
    "detected_pattern": {
      "pattern_type": "position_level",
      "components": {
        "position": { "type": "numeric", "digits": "variable", "range": "1-99999" },
        "level": { "type": "alpha", "values": ["A", "B", "C", "D"] }
      },
      "format": "PPPPPL",
      "examples": ["010A", "325B", "245D"]
    },
    "confidence": 0.95,
    "canonical_examples": ["010A", "325B", "245D", "1230A", "5678C"],
    "analysis_summary": "Detected position-level format with variable-length numeric positions (1-5 digits) followed by single letter level identifier.",
    "recommendations": [
      "This format supports up to 99,999 positions per rack",
      "Level identifiers should be uppercase letters (A-D standard)",
      "Consider using leading zeros for consistency (e.g., 010A vs 10A)"
    ]
  },
  "format_config": {
    "pattern_type": "position_level",
    "canonical_format": "PPPPPL",
    "conversion_rules": {...},
    "validation_rules": {...}
  },
  "validation": {
    "valid": true,
    "errors": [],
    "warnings": []
  },
  "input_summary": {
    "original_example_count": 5,
    "cleaned_example_count": 5,
    "examples_used": ["010A", "325B", "245D", "1230A", "5678C"]
  },
  "metadata": {
    "detector_version": "1.0.0",
    "processing_timestamp": "2025-01-15T10:30:00",
    "user_id": 1,
    "patterns_analyzed": 3
  }
}
```

#### 10. Validate Format Configuration
```
POST /api/v1/templates/validate-format
Body:
{
  "format_config": {Format config object}
}

Response: 200 OK
{
  "success": true,
  "validation": {
    "valid": true,
    "errors": [],
    "warnings": ["Position range exceeds typical warehouse size"]
  },
  "compatibility_check": {
    "canonical_service_available": true,
    "pattern_type": "position_level",
    "can_convert_to_canonical": true,
    "sample_conversions": [
      { "original": "010A", "canonical": "010A", "success": true },
      { "original": "325B", "canonical": "325B", "success": true }
    ]
  }
}
```

### Additional Endpoints

#### 11. Preview Template
```
GET /api/v1/templates/{template_id}/preview

Response: 200 OK
{
  "preview": {
    "template": {Template object},
    "calculations": {
      "total_storage_locations": 1600,
      "total_storage_capacity": 1600,
      "receiving_capacity": 40,
      "total_capacity": 1640
    },
    "sample_locations": [
      { "code": "001A", "full_address": "Aisle 1, Rack 1, Position 001A" },
      { "code": "001B", "full_address": "Aisle 1, Rack 1, Position 001B" }
    ],
    "special_areas": {
      "receiving": [...]
    }
  }
}
```

#### 12. Get Popular Templates
```
GET /api/v1/templates/popular?limit=10

Response: 200 OK
{
  "templates": [Template[]],
  "count": 10
}
```

#### 13. Create Template from Existing Config
```
POST /api/v1/templates/from-config
Body:
{
  "config_id": 5,
  "template_name": "My Warehouse Template",
  "template_description": "Based on North Facility",
  "is_public": false
}

Response: 201 Created
{
  "message": "Template created from configuration successfully",
  "template": {Template object}
}
```

---

## 4. Frontend Components

### Main Components

#### 1. TemplateCreationWizard
**File:** `frontend/components/locations/templates/template-creation-wizard.tsx`

**Purpose:** 5-step wizard for creating new templates

**Props:**
```typescript
interface TemplateCreationWizardProps {
  open: boolean;
  onClose: () => void;
  onTemplateCreated?: (template: any, warehouseConfig?: any) => void;
  isFirstTimeSetup?: boolean;    // NEW: Dual-behavior mode
  warehouseId?: string;           // NEW: For first-time setup
}
```

**Steps:**
1. **Step 1: Basic Information** (lines 457-555)
   - Template name (required)
   - Description (optional)
   - Category selection
   - Industry
   - Tags
   - Visibility (Private/Company/Public)
   - Quick Start Templates (collapsible section)

2. **Step 2: Structure Configuration** (lines 557-713)
   - Number of aisles
   - Racks per aisle
   - Positions per rack
   - Levels per position
   - Level naming convention
   - Default pallet capacity
   - Default zone
   - Real-time capacity calculator

3. **Step 3: Location Format** (lines 715-722)
   - Smart format detection
   - Example input (textarea)
   - Auto-detection with debounce (800ms)
   - Format confidence display
   - Accept/Apply button
   - Manual configuration option

4. **Step 4: Special Areas** (lines 724-808)
   - Receiving areas editor
   - Staging areas editor
   - Dock areas editor
   - Aisle areas editor
   - Auto-generate aisle areas button

5. **Step 5: Review & Create** (lines 812-974)
   - Complete summary
   - Capacity highlights
   - Layout structure
   - Work areas configured
   - Create/Build button

**Key Features:**
- Auto-scroll to top on step change (lines 201-208)
- Progress bar with percentage (lines 995-1010)
- Step validation with `canProceed()` (lines 413-429)
- Dual-mode submission (lines 337-411)
- Format detection callback handling (lines 296-318)

#### 2. LocationFormatStep
**File:** `frontend/components/locations/templates/LocationFormatStep.tsx`

**Purpose:** Smart location format detection step

**Props:**
```typescript
interface LocationFormatStepProps {
  onFormatDetected: (formatConfig: object, patternName: string, examples: string[]) => void;
  onManualConfiguration?: () => void;
  initialExamples?: string;
  onFormatApplied?: (applied: boolean) => void;
}
```

**Features:**
- Debounced input (800ms) to avoid excessive API calls
- Real-time format detection
- Example suggestions (4 preset formats)
- Visual confidence scoring
- Applied state tracking
- Error handling

**Example Suggestions:**
1. Position + Level Format: `010A, 325B, 245D`
2. Enterprise Scale Positions: `1000A, 2500B, 7890C`
3. Aisle-Rack-Position: `01-A-1000A, 02-B-2500C`
4. Zone + Sequential: `ZONE-A-001, ZONE-B-125`

#### 3. FormatDetectionDisplay
**File:** `frontend/components/locations/templates/FormatDetectionDisplay.tsx`

**Purpose:** Displays format detection results with confidence

**Props:**
```typescript
interface FormatDetectionDisplayProps {
  result: FormatDetectionResult | null;
  loading: boolean;
  error: string | null;
  originalExamples: string[];
  onAcceptFormat: () => void;
  onManualConfiguration: () => void;
  isApplied?: boolean;
}
```

**UI States:**
- Loading: Animated spinner with "Analyzing patterns..."
- Error: Destructive alert with error message
- Success: Card with confidence badge and examples
- Applied: Green checkmark with success message

**Confidence Badge Colors:**
- ≥80%: Green (high confidence)
- ≥60%: Yellow (medium confidence)
- <60%: Red (low confidence)

#### 4. SpecialAreaEditor
**File:** `frontend/components/locations/templates/special-area-editor.tsx`

**Purpose:** Reusable editor for special area configuration

**Props:**
```typescript
interface SpecialAreaEditorProps {
  title: string;
  description: string;
  areas: SpecialArea[];
  areaType: 'RECEIVING' | 'STAGING' | 'DOCK' | 'TRANSITIONAL';
  onAreasChange: (areas: SpecialArea[]) => void;
  icon?: React.ReactNode;
}
```

**Features:**
- Add/Edit/Delete operations
- Auto-generated default codes
- Capacity and zone configuration
- Type-specific defaults
- Modal dialog for editing

#### 5. EnhancedTemplateManagerV2
**File:** `frontend/components/locations/templates/enhanced-template-manager-v2.tsx`

**Purpose:** Browse, search, and apply existing templates

**Features:**
- Tab-based navigation (Browse/My Templates/Featured)
- Search with debouncing
- Category filtering
- Sort options (Recent/Popular/Rating/Name)
- View modes (Card/Compact/Detailed)
- Quick apply by template code
- Template preview
- Delete templates (soft delete)
- Create template from existing warehouse

**Template Card Display:**
- Template name and description
- Structure summary (4A × 2R × 50P × 4L)
- Total capacity
- Template code
- Usage count
- Creator
- Public/Private badge
- Apply button
- Applied status indicator

---

## 5. UI/UX Patterns

### Progressive Disclosure
Steps are revealed one at a time, reducing cognitive load:
- Each step has clear title and description
- Progress bar shows completion percentage
- "Next" button disabled until step requirements met
- Previous button to go back

### Validation Gates
Each step requires validation before proceeding:
```typescript
const canProceed = () => {
  switch (currentStep) {
    case 1: return templateData.name.trim().length > 0;
    case 2: return templateData.num_aisles > 0 && templateData.racks_per_aisle > 0 &&
                   templateData.positions_per_rack > 0 && templateData.levels_per_position > 0;
    case 3: return formatApplied;  // Must apply format to proceed
    case 4: return true;  // Special areas optional
    case 5: return true;  // Review step
    default: return false;
  }
};
```

### Real-Time Feedback
- **Capacity Calculator:** Updates live as structure values change
- **Format Detection:** Debounced auto-detection (800ms delay)
- **Example Counter:** Shows progress (e.g., "Add 2-4 more examples")
- **Progress Messages:** Contextual messages at each completion level

### Visual Hierarchy

**Color Coding:**
- Primary actions: Gradient slate to blue (`from-slate-700 to-blue-800`)
- Success states: Emerald (`from-emerald-50 to-slate-50`)
- Info alerts: Blue (`from-blue-50 to-slate-50`)
- Warnings: Yellow (`from-yellow-50`)
- Errors: Red (destructive variant)

**Typography:**
- Step titles: `text-2xl font-bold`
- Section headers: `text-lg font-semibold`
- Labels: `text-base font-medium`
- Helper text: `text-sm text-gray-600`
- Values: `font-mono` for codes and numbers

**Spacing:**
- Step content: `space-y-8` (generous breathing room)
- Form sections: `space-y-6`
- Form fields: `space-y-4`
- Cards: `p-6` padding

### Micro-interactions
- Hover effects on cards and buttons
- Loading spinners during async operations
- Smooth scrolling to top on step change
- Badge animations for confidence scores
- Progress bar transitions

### Empty States
Well-designed empty states with:
- Icon representing the content type
- Clear message ("No receiving areas configured")
- Call-to-action button

---

## 6. Form Elements & Validation

### Input Fields

#### Text Input
```tsx
<Input
  id="name"
  value={templateData.name}
  onChange={(e) => updateTemplateData({ name: e.target.value })}
  placeholder="e.g., Main Distribution Center"
  className="text-base py-3"
/>
```

#### Number Input
```tsx
<Input
  id="num_aisles"
  type="number"
  min="1"
  value={templateData.num_aisles}
  onChange={(e) => updateTemplateData({ num_aisles: parseInt(e.target.value) || 0 })}
  className="text-sm py-2"
/>
```

#### Textarea
```tsx
<Textarea
  id="description"
  value={templateData.description}
  onChange={(e) => updateTemplateData({ description: e.target.value })}
  placeholder="Describe your warehouse..."
  rows={3}
  className="text-base"
/>
```

#### Select/Dropdown
```tsx
<Select
  value={templateData.category}
  onValueChange={(value) => updateTemplateData({ category: value })}
>
  <SelectTrigger>
    <SelectValue placeholder="Select category" />
  </SelectTrigger>
  <SelectContent>
    {TEMPLATE_CATEGORIES.map(cat => (
      <SelectItem key={cat.value} value={cat.value}>
        {cat.label}
      </SelectItem>
    ))}
  </SelectContent>
</Select>
```

#### Switch/Toggle
```tsx
<div className="flex items-center space-x-2">
  <Switch
    id="bidimensional_racks"
    checked={templateData.bidimensional_racks}
    onCheckedChange={(checked) => updateTemplateData({ bidimensional_racks: checked })}
  />
  <Label htmlFor="bidimensional_racks">Bidimensional racks</Label>
</div>
```

### Validation Rules

**Required Fields:**
- Template name (Step 1)
- num_aisles, racks_per_aisle, positions_per_rack, levels_per_position (Step 2)
- Format configuration must be applied (Step 3)

**Numeric Constraints:**
- All structure values must be ≥ 1
- Capacity values must be ≥ 1
- max_position_digits: 1-6

**String Constraints:**
- name: max 120 characters
- level_names: max 20 characters
- template_code: max 20 characters (auto-generated)

**Format Validation:**
- Minimum 2 examples required for detection
- Examples trimmed and filtered (empty strings removed)
- Debounced detection to avoid excessive API calls

---

## 7. Smart Features

### 1. Smart Format Detection

**How it works:**
1. User provides 3-5 location code examples
2. System analyzes patterns using ML (SmartFormatDetector)
3. Returns detected pattern with confidence score
4. Shows canonical (standardized) format
5. User reviews and applies configuration

**Supported Pattern Types:**
- `position_level` - Position number + level letter (e.g., 010A)
- `aisle_rack_position` - Multi-segment (e.g., 01-A-1000A)
- `zone_sequential` - Zone with sequence (e.g., ZONE-A-001)
- `enterprise_scale` - Large position numbers (e.g., 15000A)

**Confidence Thresholds:**
- ≥80%: High confidence (auto-suggest apply)
- 60-79%: Medium confidence (user review recommended)
- <60%: Low confidence (manual configuration suggested)

### 2. Auto-Generate Features

**Aisle Areas Auto-Generation:**
```typescript
const generateAisleAreas = () => {
  const aisleAreas = [];
  for (let i = 1; i <= templateData.num_aisles; i++) {
    aisleAreas.push({
      code: `AISLE-${String(i).padStart(2, '0')}`,
      type: 'TRANSITIONAL',
      capacity: 10,
      zone: 'GENERAL'
    });
  }
  updateTemplateData({ aisle_areas: aisleAreas });
};
```

**Template Code Generation:**
```python
# Format: WAR-{aisles}A{racks}R-{random}
# Example: WAR-4A2R-X7Z
def generate_template_code(self):
    random_suffix = ''.join(random.choices(string.ascii_uppercase + string.digits, k=3))
    code = f"WAR-{self.num_aisles}A{self.racks_per_aisle}R-{random_suffix}"

    # Ensure uniqueness
    while WarehouseTemplate.query.filter_by(template_code=code).first():
        random_suffix = ''.join(random.choices(string.ascii_uppercase + string.digits, k=3))
        code = f"WAR-{self.num_aisles}A{self.racks_per_aisle}R-{random_suffix}"

    return code
```

### 3. Quick Start Templates

Predefined templates for common warehouse types:

```typescript
const STARTER_TEMPLATES = [
  {
    name: 'Small Warehouse',
    description: 'Compact layout for smaller operations',
    structure: { aisles: 2, racks: 2, positions: 25, levels: 3 },
    category: 'CUSTOM'
  },
  {
    name: 'Standard Distribution',
    description: 'Balanced layout for general distribution',
    structure: { aisles: 4, racks: 2, positions: 50, levels: 4 },
    category: 'RETAIL'
  },
  {
    name: 'High-Density Storage',
    description: 'Maximizes storage capacity',
    structure: { aisles: 6, racks: 3, positions: 60, levels: 5 },
    category: 'MANUFACTURING'
  },
  {
    name: 'E-commerce Fulfillment',
    description: 'Optimized for fast picking',
    structure: { aisles: 8, racks: 2, positions: 40, levels: 3 },
    category: 'ECOMMERCE'
  }
];
```

### 4. Real-Time Capacity Calculator

```typescript
const calculateTotals = () => {
  const storageLocations = templateData.num_aisles * templateData.racks_per_aisle *
                         templateData.positions_per_rack * templateData.levels_per_position;
  const storageCapacity = storageLocations * templateData.default_pallet_capacity;
  const specialCapacity = [...templateData.receiving_areas, ...templateData.staging_areas,
                          ...templateData.dock_areas, ...templateData.aisle_areas]
                        .reduce((sum, area) => sum + area.capacity, 0);

  return {
    storageLocations,
    storageCapacity,
    specialCapacity,
    totalCapacity: storageCapacity + specialCapacity
  };
};
```

### 5. Virtual Locations (Backend)

**NEW Feature:** Templates can be applied with virtual locations instead of creating physical database records.

**Benefits:**
- Instant setup (no database writes)
- Zero storage overhead
- Dynamic generation on-demand
- Supports millions of locations

**Implementation:**
```python
# Backend: template_api.py (lines 574-604)
use_virtual_locations = data.get('use_virtual_locations', True)

if use_virtual_locations:
    result = virtual_manager.apply_template_with_virtual_locations(
        template, warehouse_id, warehouse_name, current_user,
        customizations=data.get('customizations')
    )
else:
    result = virtual_manager.apply_template_legacy_mode(
        template, warehouse_id, warehouse_name, current_user,
        customizations=data.get('customizations')
    )
```

---

## 8. User Flows

### Flow 1: Create Standalone Template

```
1. User clicks "Create New Template"
2. Step 1: Basic Info
   - Enter name: "Main Distribution Center"
   - Enter description (optional)
   - Select category: "Manufacturing"
   - Set visibility: "Private"
   - Click "Next"

3. Step 2: Structure
   - Aisles: 4
   - Racks per aisle: 2
   - Positions per rack: 50
   - Levels: 4
   - View calculated capacity: 1,600 locations
   - Click "Next"

4. Step 3: Location Format
   - Enter examples: "010A", "325B", "245D", "1230A", "5678C"
   - System auto-detects: "position_level" (95% confidence)
   - Review canonical format
   - Click "Apply Format Configuration"
   - Click "Next"

5. Step 4: Special Areas
   - Add receiving area: RECV-01 (10 pallets)
   - Add staging area: STAGE-01 (5 pallets)
   - Click "Auto-Generate" for aisle areas
   - Click "Next"

6. Step 5: Review
   - Review all configuration
   - Total capacity: 1,640 pallets
   - Click "Create Template"

7. Success
   - Template created with code: WAR-4A2R-X7Z
   - Can now be shared or applied to warehouses
```

### Flow 2: First-Time Warehouse Setup

```
1. New user logs in (no warehouse configured)
2. System shows "Set Up Your Warehouse" wizard
3. Same 5-step flow as Flow 1, but with different messaging:
   - "Build Your Warehouse" instead of "Create Template"
   - Final button: "Build My Warehouse! 🚀"

4. On submit:
   - Template created AND saved to library
   - Template immediately applied to warehouse
   - Locations generated (virtual or physical)
   - User taken to warehouse dashboard

5. Result:
   - Warehouse ready to use
   - Template saved for future use
   - Can create additional warehouses from same template
```

### Flow 3: Apply Existing Template

```
1. User browses Template Library
2. Filters by category or searches by name
3. Clicks on template to preview
4. Reviews:
   - Structure (4A × 2R × 50P × 4L)
   - Total capacity (1,640 pallets)
   - Special areas configured
   - Location format pattern

5. Clicks "Apply Template"
6. Modal opens with options:
   - Warehouse name (editable)
   - Use virtual locations: Yes/No
   - Customizations (optional)

7. Clicks "Apply to My Warehouse"
8. Success:
   - Warehouse created
   - Template usage_count incremented
   - Redirect to warehouse dashboard
```

### Flow 4: Apply by Template Code

```
1. User receives template code from colleague: "WAR-4A2R-X7Z"
2. In Template Manager, clicks "Quick Apply" tab
3. Enters template code: WAR-4A2R-X7Z
4. Clicks "Apply"
5. Same modal as Flow 3
6. Template applied to warehouse
```

---

## 9. Design Tokens & Styling

### Colors (Tailwind)

**Primary Palette:**
```
Slate: slate-50, slate-100, slate-200, slate-600, slate-700, slate-800, slate-900
Blue: blue-50, blue-100, blue-200, blue-600, blue-700, blue-800, blue-900
```

**State Colors:**
```
Success: emerald-50, emerald-200, emerald-400, emerald-600, emerald-700
Info: blue-50, blue-200, blue-600, blue-700
Warning: yellow-50, yellow-100, yellow-200, yellow-600, yellow-700
Error: red-50, red-200, red-600, red-700
```

**Gradients:**
```
Primary: from-slate-700 to-blue-800
Success: from-emerald-50 to-slate-50
Info: from-blue-50 to-slate-50
Dark cards: from-slate-800 to-blue-900
```

### Typography

**Font Families:**
- Default: System font stack
- Monospace: `font-mono` (for codes, numbers, examples)

**Sizes:**
- Step titles: `text-2xl` (24px)
- Section headers: `text-lg` (18px)
- Labels: `text-base` (16px)
- Body: `text-sm` (14px)
- Helper text: `text-xs` (12px)

**Weights:**
- Titles: `font-bold` (700)
- Headers: `font-semibold` (600)
- Labels: `font-medium` (500)
- Body: `font-normal` (400)

### Spacing

**Container Padding:**
- Cards: `p-6` (24px)
- Sections: `p-4` (16px)
- Compact: `p-3` (12px)

**Vertical Spacing:**
- Step sections: `space-y-8` (32px)
- Form groups: `space-y-6` (24px)
- Form fields: `space-y-4` (16px)
- Labels: `space-y-2` (8px)

**Horizontal Spacing:**
- Buttons: `gap-2` (8px)
- Icons: `gap-3` (12px)
- Cards: `gap-4` (16px)

### Border Radius

```
Default: rounded-lg (8px)
Cards: rounded-lg
Buttons: rounded (4px)
Badges: rounded (4px)
Full: rounded-full (pill shape for icons)
```

### Shadows

```
Small: shadow-sm
Default: shadow
Large: shadow-lg
Extra large: shadow-xl
Extra extra large: shadow-2xl
```

### Icons

**Library:** Lucide React

**Common Icons:**
- Building2: Warehouse/Template
- Package: Receiving/Special areas
- Grid3X3: Structure/Layout
- MapPin: Location format
- Sparkles: Smart features
- CheckCircle: Success/Applied
- AlertTriangle: Warnings
- Info: Information
- Zap: Quick actions
- Trophy: Completion
- Plus: Add
- Edit: Edit
- Trash2: Delete
- Eye: View/Preview
- Copy: Duplicate
- Share2: Share
- Search: Search
- Filter: Filter

**Icon Sizes:**
- Large: `h-8 w-8` (32px)
- Medium: `h-5 w-5` (20px)
- Small: `h-4 w-4` (16px)
- Extra small: `h-3 w-3` (12px)

---

## 10. Best Practices

### State Management

**Use Zustand for global state:**
```typescript
// location-store.ts
export const useLocationStore = create<LocationStore>((set, get) => ({
  templates: [],
  templatesLoading: false,
  fetchTemplates: async (scope, search) => {
    set({ templatesLoading: true });
    const response = await templateApi.listTemplates(scope, search);
    set({ templates: response.templates, templatesLoading: false });
  }
}));
```

**Use local state for form data:**
```typescript
const [templateData, setTemplateData] = useState<TemplateData>(INITIAL_TEMPLATE_DATA);
const updateTemplateData = (updates: Partial<TemplateData>) => {
  setTemplateData(prev => ({ ...prev, ...updates }));
};
```

### Error Handling

**User-Friendly Error Messages:**
```typescript
try {
  await createTemplate(data);
} catch (err: any) {
  if (err?.message?.includes('duplicate')) {
    setError('A template with this name already exists. Please choose a different name.');
  } else if (err?.response?.data?.error) {
    setError(err.response.data.error);
  } else {
    setError('Failed to create template. Please try again.');
  }
}
```

**Backend Error Handling:**
```python
# Provide context-specific error messages
if 'duplicate key' in error_message:
    return jsonify({
        'error': 'Template Application Conflict',
        'error_type': 'duplicate_locations',
        'message': 'Template contains locations that already exist',
        'solutions': [
            {'option': 'replace', 'title': 'Replace Existing Locations'},
            {'option': 'rename', 'title': 'Rename Template Locations'},
            {'option': 'cancel', 'title': 'Cancel Application'}
        ],
        'user_friendly': True
    }), 409
```

### Performance Optimization

**Debouncing:**
```typescript
// Debounce format detection to avoid excessive API calls
const useDebounce = (value: string, delay: number) => {
  const [debouncedValue, setDebouncedValue] = useState(value);

  useEffect(() => {
    const handler = setTimeout(() => {
      setDebouncedValue(value);
    }, delay);

    return () => clearTimeout(handler);
  }, [value, delay]);

  return debouncedValue;
};

const debouncedExamples = useDebounce(examples, 800);
```

**Lazy Loading:**
```typescript
// Import heavy components dynamically
const { templateApi } = await import('./location-api');
```

**Pagination:**
```typescript
// Backend: Limit results per page
per_page = min(int(request.args.get('per_page', 20)), 50)
pagination = query.paginate(page=page, per_page=per_page, error_out=False)
```

**Database Indexes:**
```python
# Add indexes for common queries
__table_args__ = (
    db.Index('idx_template_public_active', 'is_public', 'is_active'),
    db.Index('idx_template_usage_created', 'usage_count', 'created_at'),
    db.Index('idx_template_creator_active', 'created_by', 'is_active'),
)
```

### Accessibility

**Keyboard Navigation:**
- All interactive elements focusable
- Tab order follows visual flow
- Enter/Space to activate buttons
- Escape to close dialogs

**Screen Reader Support:**
- Semantic HTML (`<button>`, `<label>`, `<input>`)
- ARIA labels for icon-only buttons
- Form labels associated with inputs
- Alert regions for dynamic content

**Visual Accessibility:**
- Sufficient color contrast (WCAG AA)
- Focus indicators on all interactive elements
- Error messages in red + text
- Success states in green + checkmark icon

### Testing Considerations

**Unit Tests:**
- Test form validation logic
- Test calculation functions (capacity calculator)
- Test format detection parsing
- Test state updates

**Integration Tests:**
- Test API endpoints with mock data
- Test wizard flow completion
- Test template application
- Test error scenarios

**E2E Tests:**
- Complete wizard flow
- Template search and filter
- Apply template from library
- Apply template by code

### Security

**Input Validation:**
- Sanitize all user inputs
- Validate data types and ranges
- Check for SQL injection attempts
- Limit string lengths

**Authentication:**
- JWT token required for all API calls
- Token validation on every request
- User ownership checks for updates/deletes

**Authorization:**
- Only creator can edit/delete templates
- Public templates readable by all
- Private templates only for creator
- Company templates for team members

**Rate Limiting:**
- Limit format detection calls per user
- Limit template creation per user
- Prevent API abuse

---

## Summary

This foundation document provides everything needed to design a new template creation interface:

✅ **Complete data models** with all fields and constraints
✅ **Full API documentation** with request/response examples
✅ **Existing UI components** with props and features
✅ **Design patterns** and best practices
✅ **User flows** for all template scenarios
✅ **Design tokens** for consistent styling
✅ **Smart features** like format detection and auto-generation
✅ **Performance optimizations** and security considerations

### Next Steps for Your Interface Design:

1. **Review this document** to understand existing patterns
2. **Identify improvements** or new features you want to add
3. **Sketch wireframes** using the UI patterns described
4. **Design mockups** following the design tokens
5. **Share with me** for implementation

**Key Files to Reference:**
- Backend API: `backend/src/template_api.py`
- Models: `backend/src/models.py`
- Wizard: `frontend/components/locations/templates/template-creation-wizard.tsx`
- Manager: `frontend/components/locations/templates/enhanced-template-manager-v2.tsx`
- Format Step: `frontend/components/locations/templates/LocationFormatStep.tsx`

Good luck with your new interface design! 🚀
