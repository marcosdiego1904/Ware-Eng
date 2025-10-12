# VIEW ANALYTICS - DESIGN SPECIFICATION
## Smart Landing Hub Analytics Section

**Document Version:** 2.0
**Last Updated:** 2025-09-30
**Status:** Planning Phase - All Tiers Approved

---

## DESIGN PHILOSOPHY

### Core Principles
1. **CLARITY OVER COMPLEXITY** - Show only what matters, cut through data noise
2. **PREVENTION OVER REACTION** - Focus on actionable risks, not historical reports
3. **WAREHOUSE-FIRST LANGUAGE** - Speak to inventory supervisors in their terms
4. **30-SECOND MORNING BRIEFING** - User should grasp warehouse status immediately

### User Context
**Primary User:** Inventory Supervisor
**Use Case:** Arrives at work, needs to know "What needs my attention RIGHT NOW?"
**Goal:** Eliminate manual Excel analysis, provide instant risk assessment

---

## TIER 1: IMMEDIATE ACTION INTELLIGENCE ✅ APPROVED

### Overview
**Purpose:** Answer "What do I need to handle TODAY?"
**Priority:** Top of View Analytics section
**Interaction Model:** Clickable categories + global action link
**Enhancement:** Includes Critical Locations identification for targeted attention

---

### COMPONENT: Pallet Loss Risk Assessment

#### Visual Design - Enhanced with Critical Locations

```
┌─────────────────────────────────────────────────────┐
│  🔥 PALLET LOSS RISK ASSESSMENT                     │
├─────────────────────────────────────────────────────┤
│                                                     │
│         ┌──────────────────┐                       │
│         │       167        │                       │
│         │  PALLETS AT RISK │                       │
│         └──────────────────┘                       │
│                                                     │
│  📍 5 HIGH-MAINTENANCE LOCATIONS                   │
│  RECV-03, AISLE-02, 13.45A, DOCK-01, STAGING-05   │
│                                                     │
│  ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━  │
│                                                     │
│  RISK BREAKDOWN:                                   │
│                                                     │
│  🚨 ████████████████████████████ 58 RECEIVING   →  │
│  ⏱️  ███████████████████ 37 AISLE                →  │
│  ⚠️  ███████████████████ 51 CAPACITY             →  │
│  🔍 ██████ 22 ERRORS                            →  │
│                                                     │
│  [View Complete Analysis →]                        │
└─────────────────────────────────────────────────────┘
```

---

### Data Architecture

#### Risk Consolidation Logic

**Total Risk Score Calculation:**
```
Total At-Risk Pallets =
  Stagnant RECEIVING (Rule: Stagnant Pallets) +
  Stuck AISLE Transit (Rule: Stagnant Pallets) +
  Overcapacity Locations (Rule: Overcapacity Detection) +
  Invalid Location Scans (Rule: Invalid Location Detection)
```

**Note:** Risk of double-counting exists if pallets meet multiple criteria. Initial implementation will sum all categories. Future enhancement could deduplicate based on pallet ID.

#### Data Source Mapping

| Risk Category | Data Source (from WAREHOUSE_ANALYTICS_DATA_CATALOG.md) | Rule Type |
|--------------|-------------------------------------------------------|-----------|
| **RECEIVING** | Module 2: Forgotten Pallets Alert | Stagnant in RECEIVING areas (>10h threshold) |
| **AISLE** | Module 2: AISLE Stuck Pallets | Stagnant in transitional areas (>4h threshold) |
| **CAPACITY** | Module 4: Overcapacity Violations | Locations exceeding defined capacity |
| **ERRORS** | Module 4: Invalid Location Scans | Locations failing pattern validation |

#### Risk Category Details

##### 🚨 RECEIVING (High Priority)
- **Icon:** 🚨 (red alert)
- **Label:** "RECEIVING"
- **Metric:** Count of pallets stagnant in RECEIVING areas
- **Threshold:** >10 hours
- **Why It's a Risk:** Forgotten pallets become lost pallets; oldest inventory most likely to be misplaced

##### ⏱️ AISLE (High Priority)
- **Icon:** ⏱️ (clock)
- **Label:** "AISLE"
- **Metric:** Count of pallets stuck in AISLE/transitional areas
- **Threshold:** >4 hours
- **Why It's a Risk:** Blocks workflow, indicates putaway failures, easily misplaced during chaos

##### ⚠️ CAPACITY (Medium Priority)
- **Icon:** ⚠️ (warning triangle)
- **Label:** "CAPACITY"
- **Metric:** Count of locations exceeding capacity limits
- **Threshold:** >100% of defined capacity
- **Why It's a Risk:** Either scanning errors (pallets in wrong places) or physical impossibilities (data integrity issues)

##### 🔍 ERRORS (Medium Priority)
- **Icon:** 🔍 (magnifying glass)
- **Label:** "ERRORS"
- **Metric:** Count of invalid location scans
- **Threshold:** Pattern validation failure
- **Why It's a Risk:** Pallets scanned to non-existent locations are effectively lost until found manually

#### Critical Locations Feature

##### 📍 HIGH-MAINTENANCE LOCATIONS
- **Purpose:** Identify specific locations causing repeated problems
- **Display:** Shows top 5 critical location IDs (e.g., "RECV-03, AISLE-02, 13.45A, DOCK-01, STAGING-05")
- **Definition:** Locations with ≥3 anomalies/issues in current analysis
- **Sorting:** Ranked by issue count (highest to lowest)
- **Visual Position:** Between main risk number and breakdown section
- **Value:** Provides immediate actionability - user knows exactly where to focus physical attention

---

### Interaction Design

#### Default State
- Component displays with all data visible
- Visual bars indicate relative risk magnitude
- Subtle hover states indicate interactivity
- Clean, scannable layout (3-second comprehension goal)

#### Clickable Category Behavior
**When user clicks a risk category bar:**
- Navigate to Reports view
- Apply filter for that specific risk type
- Examples:
  - Click "RECEIVING" → `/reports?filter=stagnant_receiving`
  - Click "AISLE" → `/reports?filter=stagnant_aisle`
  - Click "CAPACITY" → `/reports?filter=overcapacity`
  - Click "ERRORS" → `/reports?filter=invalid_location`

**Visual Feedback:**
- Hover state: Subtle background color change + cursor pointer
- Arrow icon (→) becomes more prominent on hover
- Optional: Tooltip showing threshold violation details (e.g., "Average 417h past 10h limit")

#### Global Action Button
**"View Complete Analysis" button:**
- Navigate to Reports view with no filters applied
- Shows all anomalies across all categories
- Fallback option for users who want full context

#### Total Risk Number
- **Not clickable** - serves as informational metric only
- Large, prominent display for immediate impact recognition
- Color-coded based on severity (future enhancement):
  - Green: 0-50 pallets
  - Yellow: 51-150 pallets
  - Orange: 151-300 pallets
  - Red: 300+ pallets

---

### Visual Bar Calculation

**Bar Length Algorithm:**
```javascript
// Find max value across all categories
const maxValue = Math.max(receiving, aisle, capacity, errors);

// Calculate percentage for each bar
const barPercentage = (categoryValue / maxValue) * 100;

// Render bar with proportional width
<ProgressBar width={`${barPercentage}%`} />
```

**Example:**
- RECEIVING: 58 pallets → 100% bar length (highest)
- AISLE: 37 pallets → 64% bar length
- CAPACITY: 51 pallets → 88% bar length
- ERRORS: 22 pallets → 38% bar length

---

### Color Palette (from BRAND_FOUNDATION_DOCUMENT.md)

#### Light Mode (Default)
- **Primary Action:** #FF6B35 (Safety Orange) - Used for icons, bars, hover states
- **Text Primary:** #2D3748 (Charcoal) - Main text, numbers
- **Text Secondary:** #4A5568 (Steel Gray) - Labels, descriptions
- **Background:** #FFFFFF (White)
- **Borders:** #E2E8F0 (Light Gray)

#### Risk Category Colors
- **🚨 RECEIVING (High):** #FF6B35 (Safety Orange)
- **⏱️ AISLE (High):** #FF6B35 (Safety Orange)
- **⚠️ CAPACITY (Medium):** #F7DC6F (Hi-Vis Yellow)
- **🔍 ERRORS (Medium):** #F7DC6F (Hi-Vis Yellow)

---

### Typography (from BRAND_FOUNDATION_DOCUMENT.md)

- **Section Header:** Roboto Bold, 24px - "PALLET LOSS RISK ASSESSMENT"
- **Risk Number:** Roboto Bold, 48px - "167"
- **Risk Label:** Roboto Medium, 16px - "PALLETS AT RISK"
- **Breakdown Label:** Roboto Medium, 14px - "RISK BREAKDOWN:"
- **Category Text:** Roboto Regular, 14px - "58 RECEIVING"
- **Button Text:** Roboto Bold, 14px - "View Complete Analysis"

---

### Spacing & Layout

```
Component Dimensions:
- Total height: ~380px (increased for critical locations)
- Inner padding: 24px
- Risk number container: 120px × 120px
- Critical locations section: 40px height
- Divider line: 1px with 16px margins
- Bar height: 32px each
- Gap between bars: 12px
- Button height: 48px
- Bottom margin: 32px (separation from Tier 2)
```

---

### Edge Cases & Special States

#### Zero Risk State
```
┌─────────────────────────────────────────────────────┐
│  🔥 PALLET LOSS RISK ASSESSMENT                     │
├─────────────────────────────────────────────────────┤
│                                                     │
│         ┌──────────────────┐                       │
│         │        0         │                       │
│         │  PALLETS AT RISK │                       │
│         └──────────────────┘                       │
│                                                     │
│  ✅ NO RISKS DETECTED                              │
│                                                     │
│  All pallets within expected thresholds.           │
│  Great work keeping operations smooth!             │
│                                                     │
│  [View Reports →]                                  │
└─────────────────────────────────────────────────────┘
```

#### Loading State
```
┌─────────────────────────────────────────────────────┐
│  🔥 PALLET LOSS RISK ASSESSMENT                     │
├─────────────────────────────────────────────────────┤
│                                                     │
│         ┌──────────────────┐                       │
│         │       ...        │                       │
│         │   LOADING DATA   │                       │
│         └──────────────────┘                       │
│                                                     │
│  RISK BREAKDOWN:                                   │
│                                                     │
│  ████████████████░░░░░░░░░░░░ Loading...           │
│  ████████████████░░░░░░░░░░░░ Loading...           │
│  ████████████████░░░░░░░░░░░░ Loading...           │
│  ████████████████░░░░░░░░░░░░ Loading...           │
│                                                     │
└─────────────────────────────────────────────────────┘
```

#### Error State
```
┌─────────────────────────────────────────────────────┐
│  🔥 PALLET LOSS RISK ASSESSMENT                     │
├─────────────────────────────────────────────────────┤
│                                                     │
│  ⚠️  Unable to load risk data                      │
│                                                     │
│  Check your connection or try refreshing.          │
│                                                     │
│  [Retry] [View Last Report →]                      │
│                                                     │
└─────────────────────────────────────────────────────┘
```

---




## TIER 2: WAREHOUSE HEALTH AT-A-GLANCE ✅ APPROVED

### Overview
**Purpose:** Provide operational context - "How healthy is my warehouse overall?"
**Priority:** Supporting metrics below Tier 1
**Layout:** Horizontal side-by-side cards
**Interaction Model:** Non-interactive (informational only)
**Detail Level:** Moderate (number + one line of context)

---

### COMPONENT: Space Utilization & Data Quality

#### Visual Design - Horizontal Cards

```
┌──────────────────────────────┐  ┌──────────────────────────────┐
│ 📊 SPACE UTILIZATION         │  │ ✓ DATA QUALITY               │
│                              │  │                              │
│ [████░░░░░░░░░░] 20.7% Full  │  │      98% Clean Data          │
│                              │  │                              │
│ 1,903 locations available    │  │ 14 duplicate scans detected  │
└──────────────────────────────┘  └──────────────────────────────┘
```

---

### Metrics Specifications

#### 📊 SPACE UTILIZATION
- **Purpose:** Shows warehouse capacity at a glance
- **Primary Metric:** Percentage of occupied locations (e.g., "20.7% Full")
- **Visual Element:** Progress bar indicating utilization level
- **Supporting Context:** Count of available locations (e.g., "1,903 locations available")
- **Data Source:** Module 1 - Total Capacity Overview
- **Why It Matters:** Helps operators understand space availability for incoming inventory

#### ✓ DATA QUALITY
- **Purpose:** Confidence in the analysis and scanning accuracy
- **Primary Metric:** Percentage of clean data (e.g., "98% Clean Data")
- **Supporting Context:** Count of specific issues detected (e.g., "14 duplicate scans detected")
- **Data Source:** Module 6 - Scanning Quality Metrics
- **Why It Matters:** Ensures operators trust the risk assessment and can act with confidence

---

### Color Palette

**Space Utilization:**
- Progress bar fill: #FF6B35 (Safety Orange) for occupied space
- Progress bar background: #E2E8F0 (Light Gray)
- Text: #2D3748 (Charcoal)

**Data Quality:**
- High quality (>95%): #38A169 (Success Green)
- Medium quality (85-95%): #F7DC6F (Warning Yellow)
- Low quality (<85%): #E53E3E (Danger Red)
- Text: #2D3748 (Charcoal)

---

### Typography

- **Card Header:** Roboto Bold, 14px - "SPACE UTILIZATION" / "DATA QUALITY"
- **Primary Metric:** Roboto Bold, 28px - "20.7%" / "98%"
- **Supporting Text:** Roboto Regular, 12px - Context line

---

### Spacing & Layout

```
Card Dimensions:
- Each card width: 48% of container (with 4% gap between)
- Card height: 120px
- Inner padding: 20px
- Gap between cards: 4% of container width
- Progress bar height: 8px
- Vertical spacing between elements: 8px
- Bottom margin: 24px (separation from Tier 3)
```

---

### Edge Cases & Special States

#### Zero Utilization State
```
┌──────────────────────────────┐
│ 📊 SPACE UTILIZATION         │
│                              │
│ [░░░░░░░░░░░░] 0% Full       │
│                              │
│ All locations available      │
└──────────────────────────────┘
```

#### Full Capacity State
```
┌──────────────────────────────┐
│ 📊 SPACE UTILIZATION         │
│                              │
│ [████████████] 100% Full     │
│                              │
│ No locations available       │
└──────────────────────────────┘
```

#### Perfect Data Quality
```
┌──────────────────────────────┐
│ ✓ DATA QUALITY               │
│                              │
│      100% Clean Data         │
│                              │
│ No issues detected           │
└──────────────────────────────┘
```

---

## TIER 3: MOTIVATIONAL CONTEXT ✅ APPROVED

### Overview
**Purpose:** Maintain morale and demonstrate system awareness - "The system is watching your good work"
**Priority:** Subtle encouragement at bottom
**Display Logic:** Only appears when there's genuine progress to celebrate
**Tone:** Professional with warmth, factual acknowledgment
**Content Policy:** Only positive information (problems handled in Tier 1)

---

### COMPONENT: Progress Recognition Banner

#### Visual Design - Two-Line Banner

```
┌─────────────────────────────────────────────────────┐
│ ✨ NICE WORK!                                       │
│ You resolved 10 RECEIVING anomalies since yesterday │
└─────────────────────────────────────────────────────┘
```

---

### Celebration Trigger Types

#### 1. Resolution Acknowledgment (Highest Priority)
**When:** Anomalies disappear between analyses

**Examples:**
- `✨ Nice work! You resolved 10 anomalies in RECEIVING since yesterday`
- `✨ Strong progress: 8 stuck pallets cleared from AISLE-02 this morning`
- `✨ RECEIVING zone is now clear - all 15 stagnant pallets resolved`

#### 2. Prevention Recognition
**When:** User maintains good performance over time

**Examples:**
- `✨ 3-day streak: RECEIVING staying under 20 pallets`
- `✨ Zero invalid location scans today - excellent scanning accuracy`
- `✨ 7 days without overcapacity issues`

#### 3. Speed Acknowledgment
**When:** Problems resolved faster than usual

**Examples:**
- `✨ Fast response: AISLE bottleneck cleared in under 2 hours (avg: 4h)`
- `✨ Quick action: Yesterday's 22 capacity issues all verified within one shift`

#### 4. Milestone Recognition
**When:** User hits significant improvements

**Examples:**
- `✨ Milestone: Warehouse risk count lowest in 30 days (42 pallets at risk)`
- `✨ Achievement: First week with zero lost pallets`
- `✨ Record performance: Data quality hit 99% - best this month`

#### 5. Location-Specific Wins
**When:** Problem locations improve significantly

**Examples:**
- `✨ RECV-03 improvement: From 15 issues down to 2`
- `✨ Great focus: 3 of your 5 critical locations now resolved`

---

### Message Selection Priority

**System evaluates in this order:**
1. **Major wins** - Resolved >50% of total anomalies
2. **Category-specific resolutions** - Resolved ≥5 anomalies in one category
3. **Critical location improvements** - Previously critical location now clean
4. **Active streaks** - Multi-day performance maintenance
5. **Any improvement** - Fewer issues than previous analysis
6. **Good baseline performance** - Total anomalies <50

**If none apply:** Hide Tier 3 entirely (no message shown)

---

### Message Tone Guidelines

**✅ DO:**
- Use specific numbers ("10 anomalies resolved")
- Reference actual locations/categories ("RECEIVING", "AISLE-02")
- Keep it factual with warmth ("Nice work! 10 resolved")
- Use warehouse terminology naturally
- Acknowledge effort and results

**❌ DON'T:**
- Over-celebrate small things ("AMAZING! 1 anomaly resolved!")
- Use corporate buzzwords ("Synergistic optimization!")
- Sound robotic ("System detected improvement")
- Be patronizing ("Good job, champ!")
- Show neutral messages when there's nothing to celebrate

**Approved Tone Examples:**
```
✅ Nice work! 10 RECEIVING anomalies resolved since yesterday
✅ Strong progress: AISLE-02 cleared from 12 issues to 2
✅ 5-day streak: RECEIVING staying under 20 pallets
```

---

### Color Palette

- **Background:** #F0FFF4 (Success Light Green)
- **Text Header:** #2D3748 (Charcoal)
- **Text Body:** #4A5568 (Steel Gray)
- **Icon:** #38A169 (Success Green)

---

### Typography

- **Header:** Roboto Bold, 14px - "NICE WORK!" / "STRONG PROGRESS!" etc.
- **Body:** Roboto Regular, 14px - Celebration message details

---

### Spacing & Layout

```
Banner Dimensions:
- Height: 60px
- Inner padding: 16px vertical, 24px horizontal
- Line height: 1.5
- Bottom margin: 0 (final element)
```

---

### When to Hide Tier 3

**Hide completely when:**
- No previous analysis exists (first-time user)
- Performance worsened (more anomalies than before)
- No meaningful change (±5 anomalies, within statistical noise)
- Data quality issues prevent accurate comparison
- System cannot determine valid comparison

**Never show:**
- Generic encouragement ("Keep up the good work!")
- Empty praise without specific achievements
- Neutral status updates without positive context

---

## COMPLETE LAYOUT PREVIEW

```
┌─────────────────────────────────────────────────────┐
│  🔥 PALLET LOSS RISK ASSESSMENT                     │
├─────────────────────────────────────────────────────┤
│         ┌──────────────────┐                       │
│         │       167        │                       │
│         │  PALLETS AT RISK │                       │
│         └──────────────────┘                       │
│                                                     │
│  📍 5 HIGH-MAINTENANCE LOCATIONS                   │
│  RECV-03, AISLE-02, 13.45A, DOCK-01, STAGING-05   │
│                                                     │
│  ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━  │
│                                                     │
│  RISK BREAKDOWN:                                   │
│  🚨 ████████████████████████████ 58 RECEIVING   →  │
│  ⏱️  ███████████████████ 37 AISLE                →  │
│  ⚠️  ███████████████████ 51 CAPACITY             →  │
│  🔍 ██████ 22 ERRORS                            →  │
│                                                     │
│  [View Complete Analysis →]                        │
└─────────────────────────────────────────────────────┘

┌──────────────────────────────┐  ┌──────────────────────────────┐
│ 📊 SPACE UTILIZATION         │  │ ✓ DATA QUALITY               │
│                              │  │                              │
│ [████░░░░░░░░░░] 20.7% Full  │  │      98% Clean Data          │
│                              │  │                              │
│ 1,903 locations available    │  │ 14 duplicate scans detected  │
└──────────────────────────────┘  └──────────────────────────────┘

┌─────────────────────────────────────────────────────┐
│ ✨ NICE WORK!                                       │
│ You resolved 10 RECEIVING anomalies since yesterday │
└─────────────────────────────────────────────────────┘
```

---

