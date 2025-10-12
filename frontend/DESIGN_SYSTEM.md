# WAREHOUSE INTELLIGENCE DESIGN SYSTEM

**Last Updated:** January 2025
**Status:** Active Implementation
**Based on:** BRAND_FOUNDATION_DOCUMENT.md

---

## Overview

This design system translates the Warehouse Intelligence brand foundation into a cohesive, implementable UI system. Built for warehouse professionals, it prioritizes **clarity, action-readiness, and operational focus**.

---

## Color System

### Light Mode: "Safety-First Professional" (Default)

#### Primary Actions - Safety Orange Family
```css
--primary: #FF6B35           /* Main CTAs, urgent alerts */
--primary-hover: #FF5A24      /* Hover state */
--secondary-action: #FF8A5B   /* Less critical actions */
--action-bg: #FFF4F2          /* Subtle action zone backgrounds */
```

**When to use:**
- Primary buttons (Save, Submit, Create)
- Urgent alerts requiring immediate attention
- Call-to-action elements
- Focus states on interactive elements

#### Structure - Steel Gray Family
```css
--text-primary: #2D3748       /* Headings, critical information */
--text-secondary: #4A5568     /* Body text, descriptions */
--secondary: #4A5568          /* Secondary buttons, outlines */
--border: #E2E8F0             /* Subtle dividers, form outlines */
```

**When to use:**
- All body text and headings
- Secondary actions (Cancel, Close)
- Borders and dividers
- Non-urgent UI structure

#### Success - Warehouse Green Family
```css
--success: #38A169            /* Completed tasks, confirmations */
--success-light: #F0FFF4      /* Success backgrounds */
--success-growth: #68D391     /* Positive trends, improvements */
```

**When to use:**
- Successful operations
- Positive metrics and trends
- Completion confirmations
- "All clear" status indicators

#### Warning - Hi-Vis Yellow Family
```css
--warning: #F7DC6F            /* Capacity alerts, attention needed */
--warning-light: #FFFBEB      /* Warning backgrounds */
--warning-caution: #ECC94B    /* Medium priority items */
```

**When to use:**
- Capacity warnings
- Items needing attention (not critical)
- Medium priority alerts
- "Review recommended" status

#### Danger - Industrial Red Family
```css
--destructive: #E53E3E        /* Critical alerts, system errors */
--danger-light: #FED7D7       /* Error backgrounds */
--danger-emergency: #C53030   /* Urgent action required */
```

**When to use:**
- Critical errors
- Delete/destructive actions
- System failures
- Urgent pallet loss situations

### Dark Mode: "Industrial Authority"

Automatically applied when `.dark` class is present.

#### Primary Colors Swap
```css
--primary: #F7DC6F            /* Hi-Vis Yellow (high contrast) */
--secondary-action: #FF6B35   /* Safety Orange (accent) */
```

**Rationale:** Yellow has better visibility in low-light warehouse environments.

---

## Typography

### Font Stack
```css
--font-sans: "Inter", system-ui, -apple-system, sans-serif;
```

### Hierarchy

| Element | Style | Size | Weight | Usage |
|---------|-------|------|--------|-------|
| **H1** | Inter | 32px | Bold (700) | Page titles, major sections |
| **H2** | Inter | 24px | Bold (700) | Zone headers, alert categories |
| **H3** | Inter | 18px | Medium (500) | Subsections, rule names |
| **Body Large** | Inter | 16px | Regular (400) | Primary content, descriptions |
| **Body** | Inter | 14px | Regular (400) | Secondary info, details |
| **Label** | Inter | 12px | Medium (500) | Field labels, timestamps, locations |
| **Action** | Inter | 14px | Bold (700) | Button text, links, CTAs |

### Text Color Usage

```css
/* Light mode */
.text-primary-text  /* #2D3748 - Headings, critical data */
.text-secondary-text /* #4A5568 - Body text */

/* Semantic colors */
.text-success       /* Positive confirmations */
.text-warning       /* Caution/attention */
.text-destructive   /* Errors/dangers */
```

---

## Component Styles

### Buttons - "Action-Ready Design"

#### Primary Button (Warehouse CTA)
```tsx
<button className="btn-warehouse-primary">
  Analyze Inventory
</button>
```

**Specs:**
- Height: 48px (warehouse safety button standard)
- Padding: 0 24px
- Border radius: 6px
- Background: Safety Orange (#FF6B35)
- Font: Inter Bold, 14px
- Hover: Slightly darker orange (#FF5A24)

**Usage:** Main actions (Submit, Save, Start Analysis)

#### Secondary Button (Alternative Actions)
```tsx
<button className="btn-warehouse-secondary">
  Cancel
</button>
```

**Specs:**
- Height: 48px
- Padding: 0 24px
- Border: 2px solid Steel Gray (#4A5568)
- Background: Transparent
- Font: Inter Medium, 14px
- Hover: Filled with Steel Gray

**Usage:** Cancel, Close, Back, Secondary actions

### Cards - "Pallet Stack Organization"

#### Alert Card
```tsx
<div className="alert-urgent"> {/* or alert-high, alert-medium, alert-low */}
  <h3>3 Pallets Need Attention</h3>
  <p>Zone B - Stagnant inventory detected</p>
</div>
```

**Specs:**
- Clean edges (6px border radius)
- Subtle shadow: `0 1px 3px rgba(0,0,0,0.1)`
- Left border: 4px colored priority indicator
- Zone/location prominent at top
- Expandable details on click

**Priority Colors:**
- `.alert-urgent` - Emergency Red (#C53030)
- `.alert-high` - Hi-Vis Yellow (#F7DC6F)
- `.alert-medium` - Caution Yellow (#ECC94B)
- `.alert-low` - Warehouse Green (#38A169)

### Forms - "Digital Clipboard Style"

#### Input Fields
```tsx
<input
  className="border border-input rounded-md px-4 py-3 text-foreground"
  placeholder="Enter location code"
/>
```

**Specs:**
- Clear 1px borders (#E2E8F0)
- Ample padding: 12px vertical, 16px horizontal
- Always-visible labels (never floating)
- Focus: Safety Orange ring
- Validation: Immediate feedback with warehouse-clear language

**Good validation message:** "Location B-12 not found in warehouse"
**Bad validation message:** "Invalid input detected in field_location_code"

### Tables - "Inventory List Mastery"

```tsx
<table className="warehouse-data-table">
  <thead>
    <tr>
      <th>Location</th>
      <th>Pallet ID</th>
      <th>Status</th>
      <th className="text-right">Actions</th>
    </tr>
  </thead>
  <tbody>
    <tr className="alert-high">
      <td>B-12-3</td>
      <td>PLT-1234</td>
      <td><span className="text-warning">Needs Attention</span></td>
      <td className="text-right">View • Resolve</td>
    </tr>
  </tbody>
</table>
```

**Specs:**
- Excel-familiar layout
- Hover states for row scanning
- Left border priority indicators (like alert cards)
- Actions right-aligned with icon+text
- Sticky headers on scroll

---

## Utility Classes

### Background Colors
```css
.bg-action          /* Subtle orange background (#FFF4F2) */
.bg-success-light   /* Light green background (#F0FFF4) */
.bg-warning-light   /* Light yellow background (#FFFBEB) */
.bg-danger-light    /* Light red background (#FED7D7) */
```

### Text Colors
```css
.text-success       /* Warehouse Green */
.text-success-growth /* Growth Green */
.text-warning       /* Hi-Vis Yellow */
.text-warning-caution /* Caution Yellow */
.text-destructive   /* Industrial Red */
.text-danger-emergency /* Emergency Red */
```

### Border Radius
```css
.rounded-sm  /* 4px - Subtle rounding */
.rounded-md  /* 6px - Standard warehouse components */
.rounded-lg  /* 8px - Cards, containers */
.rounded-xl  /* 12px - Large feature areas */
```

---

## Spacing System

Following 8px base grid for operational consistency:

```css
--spacing-1: 0.5rem   /* 8px */
--spacing-2: 1rem     /* 16px */
--spacing-3: 1.5rem   /* 24px */
--spacing-4: 2rem     /* 32px */
--spacing-6: 3rem     /* 48px */
--spacing-8: 4rem     /* 64px */
```

**Usage:**
- Padding inside cards: 24px
- Gap between cards: 16px
- Section spacing: 32px
- Major layout spacing: 48px

---

## Icon System

**Style:** Outlined (2px stroke) for better visibility
**Grid:** 24px base
**Library:** Lucide React (already installed)

### Core Warehouse Icons

| Icon | Component | Usage |
|------|-----------|-------|
| 📦 | `<Package />` | Pallets, inventory items |
| 🏪 | `<Grid3x3 />` | Zones, warehouse layout |
| 🚛 | `<Truck />` | Receiving, shipping |
| ⚠️ | `<AlertTriangle />` | Warnings, attention needed |
| 🔍 | `<Search />` | Search functionality |
| 📊 | `<BarChart3 />` | Analytics, capacity |
| 🔥 | `<Flame />` | Urgent/critical items |
| ⏰ | `<Clock />` | Time-based alerts |
| ✅ | `<CheckCircle />` | Success, completion |
| ❌ | `<XCircle />` | Problems, errors |
| 📍 | `<MapPin />` | Specific locations |

---

## Voice & Tone Guidelines

### Do's ✅
- Use warehouse terminology naturally
- Lead with solutions: "3 pallets need attention in Zone B"
- Be direct: "Found 5 stagnant pallets" not "Potential stagnancy detected"
- Speak peer-to-peer: "Here's what we found"

### Don'ts ❌
- Corporate buzzwords: "synergy," "leverage," "solutions"
- Over-explaining: "The system has detected..."
- Technical jargon for users: "NULL value in field_loc"
- Dramatic language: "CRITICAL ERROR!!!"

### Example Transformations

| ❌ Bad | ✅ Good |
|--------|---------|
| "Potential inventory discrepancies have been identified" | "Found 3 pallets that may be lost" |
| "System analysis complete. Click to view results." | "Analysis done. View 12 items needing attention" |
| "Location validation failed: invalid_location_format" | "Location B-12-A doesn't match your warehouse format" |

---

## Implementation Checklist

### Phase 1: Foundation ✅
- [x] Color system in globals.css
- [x] Typography hierarchy defined
- [x] Utility classes created
- [ ] Inter font properly loaded

### Phase 2: Core Components
- [ ] Button variants updated
- [ ] Card components aligned
- [ ] Form inputs styled
- [ ] Table layouts refined

### Phase 3: Application
- [ ] Dashboard updated
- [ ] Reports section styled
- [ ] Settings pages aligned
- [ ] Location management refined

### Phase 4: Polish
- [ ] Dark mode tested
- [ ] Accessibility audit
- [ ] Animation/transitions added
- [ ] Design system documentation site

---

## Accessibility Standards

1. **Color Contrast:** All text meets WCAG AA (4.5:1 for normal text)
2. **Focus States:** Safety Orange ring visible on all interactive elements
3. **Icon Labels:** All icons have aria-label or accompanying text
4. **Keyboard Navigation:** Full keyboard support for all actions
5. **Screen Readers:** Semantic HTML and proper ARIA attributes

---

## Design Tokens Reference

All design tokens are available as CSS variables in `globals.css`:

```css
var(--primary)              /* Safety Orange */
var(--text-primary)         /* Headings */
var(--success)              /* Warehouse Green */
var(--warning)              /* Hi-Vis Yellow */
var(--destructive)          /* Industrial Red */
var(--radius-md)            /* 6px standard */
var(--button-height)        /* 48px */
```

---

## Questions & Support

For design decisions or implementation questions, refer to:
- **Brand Strategy:** `BRAND_FOUNDATION_DOCUMENT.md`
- **Component Examples:** `/frontend/components/ui/`
- **Color System:** `/frontend/app/globals.css`
