# TRACK YOUR WINS - DEVELOPER SPECIFICATION

## Document Overview

This document provides complete specifications for implementing the "Track Your Wins" section of the Warehouse Intelligence Engine. This interface celebrates operational achievements from the most recent report analysis, providing positive reinforcement and motivation for warehouse operators.

**Version:** 1.0
**Last Updated:** 2025-10-02
**Target Implementation:** Next.js 15 (React 19) + TypeScript

---

## Design Philosophy

### Purpose
Combat "dashboard depression" by celebrating successes and showing operational value after each report analysis. This section focuses exclusively on **single-report achievements** - no historical data required.

### Brand Alignment
- **Tone:** Professional warehouse peer-to-peer (not gamified)
- **Language:** Direct, warehouse-native terminology
- **Visual:** Industrial aesthetics with Safety Orange accents
- **Psychology:** Positive reinforcement without patronizing

### User Experience Goals
1. Immediate positive feedback after report processing
2. Clear visibility of what was accomplished
3. Motivation to continue using the system
4. Professional presentation suitable for warehouse operations

---

## Component Architecture

### Page Structure
```
/frontend/components/dashboard/views/track-your-wins.tsx
```

### Layout Grid
7 core elements arranged in a scannable, prioritized layout:

```
┌───────────────────────────────────────────────────────────┐
│  TRACK YOUR WINS                                          │
├───────────────────────────────────────────────────────────┤
│                                                            │
│  ┌────────────────┐  ┌──────────────────────────────┐   │
│  │ 1. HEALTH      │  │ 2. ACHIEVEMENTS UNLOCKED     │   │
│  │    SCORE       │  │    (Badge Grid)              │   │
│  └────────────────┘  └──────────────────────────────┘   │
│                                                            │
│  ┌─────────────────────────────────────────────────────┐ │
│  │ 3. REPORT HIGHLIGHTS (3-column cards)               │ │
│  └─────────────────────────────────────────────────────┘ │
│                                                            │
│  ┌────────────────┐  ┌──────────────────────────────┐   │
│  │ 4. PROBLEM     │  │ 5. ANOMALIES RESOLVED        │   │
│  │    RESOLUTION  │  │    (Category Progress Bars)  │   │
│  │    SCORECARD   │  └──────────────────────────────┘   │
│  └────────────────┘                                       │
│                                                            │
│  ┌─────────────────────────────────────────────────────┐ │
│  │ 6. SPECIAL LOCATION PERFORMANCE SPOTLIGHT           │ │
│  └─────────────────────────────────────────────────────┘ │
│                                                            │
│  ┌─────────────────────────────────────────────────────┐ │
│  │ 7. TODAY'S OPERATIONAL IMPACT                       │ │
│  └─────────────────────────────────────────────────────┘ │
│                                                            │
└───────────────────────────────────────────────────────────┘
```

---

## ELEMENT 1: WAREHOUSE HEALTH SCORE

### Visual Design
**Component Type:** Large circular gauge (speedometer-style)

**Layout:**
```
┌─────────────────────────────┐
│                             │
│         ╭───────╮           │
│        ╱         ╲          │
│       │    87    │          │
│        ╲         ╱          │
│         ╰───────╯           │
│                             │
│   Warehouse Health Score    │
│   Based on 700 pallets      │
│                             │
└─────────────────────────────┘
```

### Data Requirements

**Input Data:**
```typescript
interface HealthScoreData {
  score: number;              // 0-100
  totalPallets: number;       // e.g., 700
  metrics: {
    spaceUtilization: number;     // percentage
    anomalyRate: number;           // anomalies per 100 pallets
    dataQuality: number;           // percentage
    locationValidation: number;    // percentage
  };
}
```

**Score Calculation:**
```typescript
function calculateHealthScore(data: AnalysisResult): number {
  const weights = {
    spaceUtilization: 0.25,    // 25% weight
    anomalyRate: 0.35,         // 35% weight
    dataQuality: 0.25,         // 25% weight
    locationValidation: 0.15   // 15% weight
  };

  // Space utilization score (optimal: 70-85%)
  const spaceScore = calculateSpaceScore(data.spaceUtilization);

  // Anomaly rate score (lower is better, optimal: <10%)
  const anomalyScore = 100 - (data.anomalyRate * 10);

  // Data quality score (higher is better)
  const qualityScore = data.dataQuality;

  // Location validation score (higher is better)
  const validationScore = data.locationValidation;

  const totalScore =
    (spaceScore * weights.spaceUtilization) +
    (anomalyScore * weights.anomalyRate) +
    (qualityScore * weights.dataQuality) +
    (validationScore * weights.locationValidation);

  return Math.round(totalScore);
}
```

### Color Coding
```typescript
function getHealthScoreColor(score: number): string {
  if (score >= 85) return '#38A169';      // Warehouse Green
  if (score >= 70) return '#F7DC6F';      // Hi-Vis Yellow
  if (score >= 50) return '#FF6B35';      // Safety Orange
  return '#E53E3E';                       // Industrial Red
}

function getHealthScoreLabel(score: number): string {
  if (score >= 85) return 'Excellent Operations';
  if (score >= 70) return 'Good Performance';
  if (score >= 50) return 'Needs Attention';
  return 'Critical Focus';
}
```

### Visual Specifications
- **Container:** `w-full max-w-xs p-6 bg-white rounded-lg border border-gray-200`
- **Gauge Size:** 200px diameter
- **Score Number:** `text-6xl font-bold` in Roboto Bold
- **Label Text:** `text-lg text-gray-600` in Roboto Regular
- **Context Text:** `text-sm text-gray-500` in Roboto Regular

### Implementation Notes
- Use Recharts `RadialBarChart` or similar gauge component
- Animate gauge fill on component mount (0 → score over 1 second)
- Display score number in center with color matching gauge
- Update color dynamically based on score thresholds

---

## ELEMENT 2: REPORT ACHIEVEMENTS UNLOCKED

### Visual Design
**Component Type:** Badge grid with achievement cards

**Layout:**
```
┌──────────────────────────────────────────┐
│  ACHIEVEMENTS UNLOCKED                   │
│  7/11 earned in this report              │
│                                          │
│  ┌──────┐ ┌──────┐ ┌──────┐ ┌──────┐  │
│  │ 📦✅ │ │ 🚛✅ │ │ ⚖️✅ │ │ 📋   │  │
│  │Clean │ │Clear │ │Perfect│ │Zero │  │
│  │Recv  │ │AISLE │ │Capacity│Stragg│  │
│  └──────┘ └──────┘ └──────┘ └──────┘  │
│                                          │
│  ┌──────┐ ┌──────┐ ┌──────┐ ┌──────┐  │
│  │ 🎯✅ │ │ 🔍   │ │ ✓    │ │ 🛡️  │  │
│  │Data  │ │Perfect│ │Format│ │Zero │  │
│  │Champ │ │ Scan │ │Master│ │Invalid│ │
│  └──────┘ └──────┘ └──────┘ └──────┘  │
│                                          │
│  ┌──────┐ ┌──────┐ ┌──────┐           │
│  │ ⚡✅ │ │ 🚀✅ │ │ 📊   │           │
│  │Lightning│Rapid │ │Efficient│        │
│  │ Fast │ │Process│ │ Space │          │
│  └──────┘ └──────┘ └──────┘           │
└──────────────────────────────────────────┘
```

### Achievement Definitions

```typescript
interface Achievement {
  id: string;
  name: string;
  icon: string;
  description: string;
  criteria: (data: AnalysisResult) => boolean;
}

const ACHIEVEMENTS: Achievement[] = [
  // Performance Badges
  {
    id: 'clean_receiving',
    name: 'Clean Receiving',
    icon: '📦✅',
    description: 'Zero forgotten pallets detected',
    criteria: (data) => data.anomalies.forgottenPallets === 0
  },
  {
    id: 'clear_aisle',
    name: 'Clear AISLE Flow',
    icon: '🚛✅',
    description: 'Zero stuck pallets in transitional areas',
    criteria: (data) => data.anomalies.stuckPallets === 0
  },
  {
    id: 'perfect_capacity',
    name: 'Perfect Capacity',
    icon: '⚖️✅',
    description: 'No overcapacity violations',
    criteria: (data) => data.anomalies.overcapacity === 0
  },
  {
    id: 'zero_stragglers',
    name: 'Zero Stragglers',
    icon: '📋✅',
    description: 'No incomplete lots detected',
    criteria: (data) => data.anomalies.incompleteLots === 0
  },
  {
    id: 'data_champion',
    name: 'Data Champion',
    icon: '🎯',
    description: '100% location validation rate',
    criteria: (data) => data.locationValidationRate === 100
  },
  {
    id: 'efficient_space',
    name: 'Efficient Space',
    icon: '📊',
    description: 'Utilization in optimal 70-85% range',
    criteria: (data) => data.spaceUtilization >= 70 && data.spaceUtilization <= 85
  },

  // Quality Badges
  {
    id: 'perfect_scan',
    name: 'Perfect Scan',
    icon: '🔍',
    description: 'No duplicate scans detected',
    criteria: (data) => data.anomalies.duplicateScans === 0
  },
  {
    id: 'format_master',
    name: 'Format Master',
    icon: '✓',
    description: '100% location format compliance',
    criteria: (data) => data.formatComplianceRate === 100
  },
  {
    id: 'zero_invalid',
    name: 'Zero Invalid',
    icon: '🛡️',
    description: 'No invalid location errors',
    criteria: (data) => data.anomalies.invalidLocations === 0
  },

  // Speed Badges
  {
    id: 'lightning_fast',
    name: 'Lightning Fast',
    icon: '⚡',
    description: 'Analysis completed in under 2 seconds',
    criteria: (data) => data.processingTime < 2000
  },
  {
    id: 'rapid_processing',
    name: 'Rapid Processing',
    icon: '🚀',
    description: 'Processed 500+ records efficiently',
    criteria: (data) => data.totalRecords >= 500
  }
];
```

### Visual Specifications

**Badge Card (Unlocked):**
```css
.achievement-badge-unlocked {
  width: 120px;
  height: 120px;
  padding: 12px;
  background: white;
  border: 2px solid #38A169;
  border-radius: 8px;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  box-shadow: 0 2px 4px rgba(0,0,0,0.1);
}

.achievement-icon {
  font-size: 32px;
  margin-bottom: 8px;
}

.achievement-name {
  font-family: 'Roboto', sans-serif;
  font-weight: 600;
  font-size: 12px;
  text-align: center;
  color: #2D3748;
}
```

**Badge Card (Locked):**
```css
.achievement-badge-locked {
  /* Same as unlocked but: */
  border: 2px solid #E2E8F0;
  opacity: 0.5;
  filter: grayscale(100%);
}
```

### Implementation Notes
- Display badges in 4-column grid on desktop, 3-column on tablet, 2-column on mobile
- Show tooltip with description on hover
- Animate badge unlock with scale effect
- Display counter at top: "X/Y earned in this report"

---

## ELEMENT 3: REPORT HIGHLIGHTS

### Visual Design
**Component Type:** Three-column card layout with positive metrics

**Layout:**
```
┌───────────────────────────────────────────────────────┐
│  REPORT HIGHLIGHTS                                    │
├───────────────────────────────────────────────────────┤
│                                                        │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐          │
│  │    ✅    │  │    🎯    │  │    🏪    │          │
│  │          │  │          │  │          │          │
│  │   497    │  │   475    │  │  20.7%   │          │
│  │  Pallets │  │  Valid   │  │ Capacity │          │
│  │ Properly │  │ Locations│  │ Utilized │          │
│  │  Placed  │  │          │  │          │          │
│  │          │  │          │  │          │          │
│  │ 71% of   │  │ 96%      │  │ Optimal  │          │
│  │inventory │  │validation│  │operating │          │
│  │          │  │ success  │  │  range   │          │
│  └──────────┘  └──────────┘  └──────────┘          │
│                                                        │
└───────────────────────────────────────────────────────┘
```

### Data Structure

```typescript
interface ReportHighlight {
  icon: string;
  mainMetric: string | number;
  title: string;
  percentage?: string;
  context: string;
  color: string;
}

function generateHighlights(data: AnalysisResult): ReportHighlight[] {
  const totalPallets = data.totalPallets;
  const properlyPlaced = totalPallets - data.totalAnomalies;
  const validLocations = data.validLocations;
  const totalLocations = data.totalLocations;
  const capacityUtilization = data.spaceUtilization;
  const availableLocations = data.availableLocations;

  return [
    {
      icon: '✅',
      mainMetric: properlyPlaced,
      title: 'Pallets Properly Placed',
      percentage: `${Math.round((properlyPlaced / totalPallets) * 100)}%`,
      context: 'Most inventory is exactly where it should be',
      color: '#38A169'
    },
    {
      icon: '🎯',
      mainMetric: validLocations,
      title: 'Valid Locations',
      percentage: `${Math.round((validLocations / totalLocations) * 100)}%`,
      context: 'High scanning accuracy maintained',
      color: '#38A169'
    },
    {
      icon: '🏪',
      mainMetric: `${capacityUtilization}%`,
      title: 'Capacity Utilized',
      percentage: '',
      context: `${availableLocations} locations available for growth`,
      color: '#4A5568'
    }
  ];
}
```

### Visual Specifications

**Highlight Card:**
```css
.highlight-card {
  padding: 24px;
  background: white;
  border: 1px solid #E2E8F0;
  border-radius: 8px;
  text-align: center;
  transition: transform 0.2s;
}

.highlight-card:hover {
  transform: translateY(-4px);
  box-shadow: 0 4px 12px rgba(0,0,0,0.1);
}

.highlight-icon {
  font-size: 48px;
  margin-bottom: 16px;
}

.highlight-metric {
  font-family: 'Roboto', sans-serif;
  font-weight: bold;
  font-size: 48px;
  color: #2D3748;
  margin-bottom: 8px;
}

.highlight-title {
  font-family: 'Roboto', sans-serif;
  font-weight: 500;
  font-size: 16px;
  color: #4A5568;
  margin-bottom: 12px;
}

.highlight-percentage {
  font-family: 'Roboto', sans-serif;
  font-weight: bold;
  font-size: 20px;
  color: #38A169;
  margin-bottom: 8px;
}

.highlight-context {
  font-family: 'Roboto', sans-serif;
  font-size: 14px;
  color: #718096;
}
```

### Implementation Notes
- Use CSS Grid: `grid-template-columns: repeat(3, 1fr)`
- On mobile: Stack vertically (`grid-template-columns: 1fr`)
- Animate numbers counting up from 0 on component mount
- Use green accent for percentage indicators

---

## ELEMENT 4: PROBLEM RESOLUTION SCORECARD

### Visual Design
**Component Type:** Table showing detected anomalies ready for resolution

**Layout:**
```
┌────────────────────────────────────────────┐
│  PREVENTION SCORECARD                      │
│  Problems detected proactively             │
├────────────────────────────────────────────┤
│                                            │
│  Anomaly Type     │ Detected │ Priority   │
│  ─────────────────┼──────────┼──────────  │
│  Forgotten Pallets│    58    │  🔴 HIGH   │
│  Stuck in AISLE   │    37    │  🔴 HIGH   │
│  Overcapacity     │    51    │  🟠 MEDIUM │
│  Invalid Locations│    22    │  🔴 HIGH   │
│  Duplicate Scans  │    14    │  🟡 LOW    │
│                                            │
│  ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━  │
│                                            │
│  ✨ 182 issues caught before they         │
│     became problems                        │
│                                            │
│  [ Go to Action Hub → ]                   │
│                                            │
└────────────────────────────────────────────┘
```

### Data Structure

```typescript
interface AnomalyCategory {
  type: string;
  detected: number;
  priority: 'VERY_HIGH' | 'HIGH' | 'MEDIUM' | 'LOW';
  icon: string;
  color: string;
}

function generateScorecard(data: AnalysisResult): AnomalyCategory[] {
  const categories: AnomalyCategory[] = [];

  if (data.anomalies.forgottenPallets > 0) {
    categories.push({
      type: 'Forgotten Pallets',
      detected: data.anomalies.forgottenPallets,
      priority: 'HIGH',
      icon: '📦',
      color: '#E53E3E'
    });
  }

  if (data.anomalies.stuckPallets > 0) {
    categories.push({
      type: 'Stuck in AISLE',
      detected: data.anomalies.stuckPallets,
      priority: 'HIGH',
      icon: '🚛',
      color: '#E53E3E'
    });
  }

  if (data.anomalies.overcapacity > 0) {
    categories.push({
      type: 'Overcapacity',
      detected: data.anomalies.overcapacity,
      priority: 'MEDIUM',
      icon: '⚖️',
      color: '#FF6B35'
    });
  }

  if (data.anomalies.invalidLocations > 0) {
    categories.push({
      type: 'Invalid Locations',
      detected: data.anomalies.invalidLocations,
      priority: 'HIGH',
      icon: '🛡️',
      color: '#E53E3E'
    });
  }

  if (data.anomalies.duplicateScans > 0) {
    categories.push({
      type: 'Duplicate Scans',
      detected: data.anomalies.duplicateScans,
      priority: 'LOW',
      icon: '🔍',
      color: '#F7DC6F'
    });
  }

  return categories;
}
```

### Priority Color Mapping

```typescript
const PRIORITY_COLORS = {
  VERY_HIGH: { bg: '#FED7D7', text: '#C53030', label: 'CRITICAL' },
  HIGH: { bg: '#FEEBC8', text: '#C05621', label: 'HIGH' },
  MEDIUM: { bg: '#FFFBEB', text: '#B7791F', label: 'MEDIUM' },
  LOW: { bg: '#F0FFF4', text: '#276749', label: 'LOW' }
};
```

### Visual Specifications

```css
.scorecard-container {
  padding: 24px;
  background: white;
  border: 1px solid #E2E8F0;
  border-radius: 8px;
}

.scorecard-header {
  font-family: 'Roboto', sans-serif;
  font-weight: bold;
  font-size: 20px;
  color: #2D3748;
  margin-bottom: 4px;
}

.scorecard-subtitle {
  font-family: 'Roboto', sans-serif;
  font-size: 14px;
  color: #718096;
  margin-bottom: 16px;
}

.scorecard-table {
  width: 100%;
  border-collapse: collapse;
}

.scorecard-row {
  border-bottom: 1px solid #E2E8F0;
  padding: 12px 0;
}

.scorecard-type {
  font-family: 'Roboto', sans-serif;
  font-size: 14px;
  color: #2D3748;
}

.scorecard-detected {
  font-family: 'Roboto', sans-serif;
  font-weight: bold;
  font-size: 18px;
  color: #2D3748;
  text-align: center;
}

.scorecard-priority {
  display: inline-block;
  padding: 4px 12px;
  border-radius: 4px;
  font-family: 'Roboto', sans-serif;
  font-weight: 500;
  font-size: 12px;
}

.scorecard-summary {
  margin-top: 16px;
  padding-top: 16px;
  border-top: 2px solid #E2E8F0;
  font-family: 'Roboto', sans-serif;
  font-size: 16px;
  color: #4A5568;
  text-align: center;
}

.scorecard-button {
  margin-top: 16px;
  width: 100%;
  padding: 12px;
  background: #FF6B35;
  color: white;
  border: none;
  border-radius: 6px;
  font-family: 'Roboto', sans-serif;
  font-weight: 600;
  font-size: 14px;
  cursor: pointer;
  transition: background 0.2s;
}

.scorecard-button:hover {
  background: #E55A2B;
}
```

### Implementation Notes
- Show only categories with detected anomalies (hide zero counts)
- Link button navigates to Action Hub filtered view
- Use Radix UI Table component for accessibility
- Mobile: Consider card layout instead of table

---

## ELEMENT 5: ANOMALIES RESOLVED TRACKER

### Visual Design
**Component Type:** Category-specific progress bars with resolution tracking

**Layout:**
```
┌─────────────────────────────────────────────────┐
│  PROBLEM RESOLUTION STATUS                       │
├─────────────────────────────────────────────────┤
│                                                  │
│  📦 Forgotten Pallets                           │
│  [████████░░░░░░░░░░░░] 12/58 resolved (21%)    │
│  Last resolved: 5 minutes ago                   │
│                                                  │
│  🚛 Stuck in AISLE                              │
│  [█████████████░░░░░░░] 18/37 resolved (49%)    │
│  Last resolved: 12 minutes ago                  │
│                                                  │
│  ⚖️ Overcapacity Issues                         │
│  [██████░░░░░░░░░░░░░░] 10/51 resolved (20%)    │
│  Last resolved: 1 hour ago                      │
│                                                  │
│  🛡️ Invalid Locations                           │
│  [███████░░░░░░░░░░░░░] 5/22 resolved (23%)     │
│  Last resolved: 2 hours ago                     │
│                                                  │
│  ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━  │
│                                                  │
│  ✨ TOTAL: 45/168 issues resolved (27%)         │
│                                                  │
│  [ Go to Action Hub → ]                         │
│                                                  │
└─────────────────────────────────────────────────┘
```

### Data Structure

```typescript
interface ResolutionStatus {
  category: string;
  icon: string;
  resolved: number;
  total: number;
  percentage: number;
  lastResolvedTimestamp: Date | null;
  color: string;
}

interface ResolutionTracker {
  categories: ResolutionStatus[];
  totalResolved: number;
  totalIssues: number;
  overallPercentage: number;
}

// Sample data structure
const resolutionData: ResolutionTracker = {
  categories: [
    {
      category: 'Forgotten Pallets',
      icon: '📦',
      resolved: 12,
      total: 58,
      percentage: 21,
      lastResolvedTimestamp: new Date(Date.now() - 5 * 60 * 1000), // 5 min ago
      color: '#FF6B35'
    },
    {
      category: 'Stuck in AISLE',
      icon: '🚛',
      resolved: 18,
      total: 37,
      percentage: 49,
      lastResolvedTimestamp: new Date(Date.now() - 12 * 60 * 1000),
      color: '#FF6B35'
    },
    {
      category: 'Overcapacity Issues',
      icon: '⚖️',
      resolved: 10,
      total: 51,
      percentage: 20,
      lastResolvedTimestamp: new Date(Date.now() - 60 * 60 * 1000),
      color: '#F7DC6F'
    },
    {
      category: 'Invalid Locations',
      icon: '🛡️',
      resolved: 5,
      total: 22,
      percentage: 23,
      lastResolvedTimestamp: new Date(Date.now() - 2 * 60 * 60 * 1000),
      color: '#E53E3E'
    }
  ],
  totalResolved: 45,
  totalIssues: 168,
  overallPercentage: 27
};
```

### Visual Specifications

```css
.resolution-container {
  padding: 24px;
  background: white;
  border: 1px solid #E2E8F0;
  border-radius: 8px;
}

.resolution-header {
  font-family: 'Roboto', sans-serif;
  font-weight: bold;
  font-size: 20px;
  color: #2D3748;
  margin-bottom: 20px;
}

.resolution-category {
  margin-bottom: 24px;
}

.resolution-category-header {
  display: flex;
  align-items: center;
  margin-bottom: 8px;
}

.resolution-icon {
  font-size: 24px;
  margin-right: 12px;
}

.resolution-category-name {
  font-family: 'Roboto', sans-serif;
  font-weight: 600;
  font-size: 16px;
  color: #2D3748;
}

.resolution-progress-bar {
  width: 100%;
  height: 24px;
  background: #E2E8F0;
  border-radius: 12px;
  overflow: hidden;
  margin-bottom: 8px;
}

.resolution-progress-fill {
  height: 100%;
  background: linear-gradient(90deg, #38A169 0%, #48BB78 100%);
  transition: width 1s ease-out;
  display: flex;
  align-items: center;
  padding-left: 12px;
}

.resolution-progress-text {
  font-family: 'Roboto', sans-serif;
  font-weight: 600;
  font-size: 12px;
  color: white;
}

.resolution-stats {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.resolution-count {
  font-family: 'Roboto', sans-serif;
  font-size: 14px;
  color: #4A5568;
}

.resolution-timestamp {
  font-family: 'Roboto', sans-serif;
  font-size: 12px;
  color: #A0AEC0;
}

.resolution-summary {
  margin-top: 20px;
  padding-top: 20px;
  border-top: 2px solid #E2E8F0;
  text-align: center;
}

.resolution-total {
  font-family: 'Roboto', sans-serif;
  font-weight: bold;
  font-size: 24px;
  color: #2D3748;
  margin-bottom: 16px;
}
```

### Time Formatting Function

```typescript
function formatTimeSince(timestamp: Date): string {
  const now = new Date();
  const diffMs = now.getTime() - timestamp.getTime();
  const diffMins = Math.floor(diffMs / 60000);

  if (diffMins < 1) return 'Just now';
  if (diffMins < 60) return `${diffMins} minute${diffMins > 1 ? 's' : ''} ago`;

  const diffHours = Math.floor(diffMins / 60);
  if (diffHours < 24) return `${diffHours} hour${diffHours > 1 ? 's' : ''} ago`;

  const diffDays = Math.floor(diffHours / 24);
  return `${diffDays} day${diffDays > 1 ? 's' : ''} ago`;
}
```

### Implementation Notes
- Progress bars animate on component mount
- Show only categories with detected anomalies
- Update "Last resolved" timestamps in real-time
- Link to Action Hub with category filter applied
- **Important:** Requires backend API to track resolution status per anomaly

### Backend API Requirements

```typescript
// POST endpoint to mark anomalies as resolved
POST /api/v1/anomalies/resolve
{
  reportId: string;
  anomalyIds: string[];
  resolvedBy: string;
  timestamp: Date;
}

// GET endpoint to fetch resolution status
GET /api/v1/reports/{reportId}/resolution-status
Response: {
  categories: ResolutionStatus[];
  totalResolved: number;
  totalIssues: number;
}
```

---

## ELEMENT 6: SPECIAL LOCATION PERFORMANCE SPOTLIGHT

### Visual Design
**Component Type:** Categorized location status list

**Layout:**
```
┌─────────────────────────────────────────────────┐
│  SPECIAL LOCATION PERFORMANCE                    │
├─────────────────────────────────────────────────┤
│                                                  │
│  🏪 RECEIVING AREAS                             │
│  ├─ RECV-01: ✅ Clean (0 issues)                │
│  ├─ RECV-02: ⚠️ 23 forgotten pallets            │
│  └─ RECV-03: ⚠️ 35 forgotten pallets            │
│                                                  │
│  🚛 AISLE/TRANSITIONAL                          │
│  ├─ AISLE-01: ⚠️ 15 stuck pallets               │
│  ├─ AISLE-02: ⚠️ 22 stuck pallets               │
│  └─ AISLE-03: ✅ Clean (0 issues)               │
│                                                  │
│  📦 DOCK AREAS                                   │
│  ├─ DOCK-01: ✅ Clean (0 issues)                │
│  └─ DOCK-02: ✅ Clean (0 issues)                │
│                                                  │
│  🎯 STAGING ZONES                                │
│  └─ STAGING-01: ✅ Clean (0 issues)             │
│                                                  │
│  ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━  │
│                                                  │
│  Summary: 5/9 special locations operating       │
│           perfectly this report                 │
│                                                  │
└─────────────────────────────────────────────────┘
```

### Data Structure

```typescript
interface SpecialLocation {
  id: string;
  name: string;
  type: 'RECEIVING' | 'AISLE' | 'DOCK' | 'STAGING' | 'TRANSITIONAL';
  status: 'clean' | 'issues';
  issueCount: number;
  issueDescription: string;
}

interface SpecialLocationCategory {
  type: string;
  icon: string;
  locations: SpecialLocation[];
}

// Function to generate location performance data
function generateSpecialLocationPerformance(
  data: AnalysisResult
): SpecialLocationCategory[] {
  const categories: SpecialLocationCategory[] = [];

  // Group special locations by type
  const locationsByType = groupLocationsByType(data.locations);

  // RECEIVING AREAS
  if (locationsByType.RECEIVING && locationsByType.RECEIVING.length > 0) {
    categories.push({
      type: 'RECEIVING AREAS',
      icon: '🏪',
      locations: locationsByType.RECEIVING.map(loc => ({
        id: loc.id,
        name: loc.name,
        type: 'RECEIVING',
        status: loc.anomalyCount === 0 ? 'clean' : 'issues',
        issueCount: loc.anomalyCount,
        issueDescription: `${loc.anomalyCount} forgotten pallet${loc.anomalyCount > 1 ? 's' : ''}`
      }))
    });
  }

  // AISLE/TRANSITIONAL
  if (locationsByType.AISLE && locationsByType.AISLE.length > 0) {
    categories.push({
      type: 'AISLE/TRANSITIONAL',
      icon: '🚛',
      locations: locationsByType.AISLE.map(loc => ({
        id: loc.id,
        name: loc.name,
        type: 'AISLE',
        status: loc.anomalyCount === 0 ? 'clean' : 'issues',
        issueCount: loc.anomalyCount,
        issueDescription: `${loc.anomalyCount} stuck pallet${loc.anomalyCount > 1 ? 's' : ''}`
      }))
    });
  }

  // DOCK AREAS
  if (locationsByType.DOCK && locationsByType.DOCK.length > 0) {
    categories.push({
      type: 'DOCK AREAS',
      icon: '📦',
      locations: locationsByType.DOCK.map(loc => ({
        id: loc.id,
        name: loc.name,
        type: 'DOCK',
        status: loc.anomalyCount === 0 ? 'clean' : 'issues',
        issueCount: loc.anomalyCount,
        issueDescription: `${loc.anomalyCount} issue${loc.anomalyCount > 1 ? 's' : ''}`
      }))
    });
  }

  // STAGING ZONES
  if (locationsByType.STAGING && locationsByType.STAGING.length > 0) {
    categories.push({
      type: 'STAGING ZONES',
      icon: '🎯',
      locations: locationsByType.STAGING.map(loc => ({
        id: loc.id,
        name: loc.name,
        type: 'STAGING',
        status: loc.anomalyCount === 0 ? 'clean' : 'issues',
        issueCount: loc.anomalyCount,
        issueDescription: `${loc.anomalyCount} issue${loc.anomalyCount > 1 ? 's' : ''}`
      }))
    });
  }

  return categories;
}
```

### Visual Specifications

```css
.special-locations-container {
  padding: 24px;
  background: white;
  border: 1px solid #E2E8F0;
  border-radius: 8px;
}

.special-locations-header {
  font-family: 'Roboto', sans-serif;
  font-weight: bold;
  font-size: 20px;
  color: #2D3748;
  margin-bottom: 20px;
}

.location-category {
  margin-bottom: 20px;
}

.location-category-header {
  display: flex;
  align-items: center;
  margin-bottom: 12px;
  padding-bottom: 8px;
  border-bottom: 1px solid #E2E8F0;
}

.location-category-icon {
  font-size: 24px;
  margin-right: 12px;
}

.location-category-title {
  font-family: 'Roboto', sans-serif;
  font-weight: 600;
  font-size: 16px;
  color: #2D3748;
}

.location-item {
  display: flex;
  align-items: center;
  padding: 8px 0 8px 36px; /* Indent under category */
  border-left: 2px solid transparent;
}

.location-item.clean {
  border-left-color: #38A169;
}

.location-item.issues {
  border-left-color: #FF6B35;
}

.location-status-icon {
  margin-right: 8px;
  font-size: 18px;
}

.location-name {
  font-family: 'Roboto', sans-serif;
  font-weight: 600;
  font-size: 14px;
  color: #2D3748;
  margin-right: 12px;
}

.location-status-clean {
  font-family: 'Roboto', sans-serif;
  font-size: 14px;
  color: #38A169;
}

.location-status-issues {
  font-family: 'Roboto', sans-serif;
  font-size: 14px;
  color: #E55A2B;
}

.special-locations-summary {
  margin-top: 20px;
  padding-top: 20px;
  border-top: 2px solid #E2E8F0;
  font-family: 'Roboto', sans-serif;
  font-size: 14px;
  color: #4A5568;
  text-align: center;
}
```

### Implementation Notes
- Group locations by classification type
- Show clean locations with green checkmark
- Show problematic locations with orange warning
- Calculate summary: clean locations / total special locations
- Make location names clickable to filter Action Hub view
- If no special locations exist, show empty state message

---

## ELEMENT 7: TODAY'S OPERATIONAL IMPACT

### Visual Design
**Component Type:** Summary card with key operational metrics

**Layout:**
```
┌─────────────────────────────────────────────────┐
│  TODAY'S OPERATIONAL IMPACT                      │
├─────────────────────────────────────────────────┤
│                                                  │
│  📊 Analysis Completed                          │
│     700 pallets processed in 1.01 seconds       │
│                                                  │
│  🎯 Problems Prevented                          │
│     168 issues caught before becoming urgent    │
│                                                  │
│  ✅ Issues Resolved                             │
│     45 problems fixed and cleared               │
│                                                  │
│  ⚡ Processing Efficiency                        │
│     693 records per second (Excellent)          │
│                                                  │
│  ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━  │
│                                                  │
│  Your warehouse intelligence system is          │
│  working effectively.                           │
│                                                  │
└─────────────────────────────────────────────────┘
```

### Data Structure

```typescript
interface OperationalImpact {
  analysisCompleted: {
    totalPallets: number;
    processingTime: number; // in seconds
  };
  problemsPrevented: {
    totalIssues: number;
    description: string;
  };
  issuesResolved: {
    resolvedCount: number;
    description: string;
  };
  processingEfficiency: {
    recordsPerSecond: number;
    rating: 'Excellent' | 'Good' | 'Average' | 'Needs Improvement';
  };
}

function generateOperationalImpact(
  data: AnalysisResult,
  resolutionData: ResolutionTracker
): OperationalImpact {
  const recordsPerSecond = Math.round(data.totalPallets / data.processingTime);

  return {
    analysisCompleted: {
      totalPallets: data.totalPallets,
      processingTime: data.processingTime
    },
    problemsPrevented: {
      totalIssues: data.totalAnomalies,
      description: 'issues caught before becoming urgent'
    },
    issuesResolved: {
      resolvedCount: resolutionData.totalResolved,
      description: 'problems fixed and cleared'
    },
    processingEfficiency: {
      recordsPerSecond,
      rating: getEfficiencyRating(recordsPerSecond)
    }
  };
}

function getEfficiencyRating(recordsPerSecond: number): string {
  if (recordsPerSecond >= 500) return 'Excellent';
  if (recordsPerSecond >= 300) return 'Good';
  if (recordsPerSecond >= 100) return 'Average';
  return 'Needs Improvement';
}
```

### Visual Specifications

```css
.impact-container {
  padding: 24px;
  background: white;
  border: 1px solid #E2E8F0;
  border-radius: 8px;
}

.impact-header {
  font-family: 'Roboto', sans-serif;
  font-weight: bold;
  font-size: 20px;
  color: #2D3748;
  margin-bottom: 20px;
}

.impact-metric {
  display: flex;
  align-items: flex-start;
  margin-bottom: 20px;
  padding: 12px;
  background: #F7FAFC;
  border-radius: 6px;
  transition: background 0.2s;
}

.impact-metric:hover {
  background: #EDF2F7;
}

.impact-icon {
  font-size: 32px;
  margin-right: 16px;
  flex-shrink: 0;
}

.impact-content {
  flex: 1;
}

.impact-label {
  font-family: 'Roboto', sans-serif;
  font-weight: 600;
  font-size: 14px;
  color: #2D3748;
  margin-bottom: 4px;
}

.impact-value {
  font-family: 'Roboto', sans-serif;
  font-size: 16px;
  color: #4A5568;
}

.impact-summary {
  margin-top: 20px;
  padding-top: 20px;
  border-top: 2px solid #E2E8F0;
  text-align: center;
}

.impact-summary-text {
  font-family: 'Roboto', sans-serif;
  font-size: 16px;
  color: #4A5568;
  line-height: 1.6;
}
```

### Impact Metrics Configuration

```typescript
const IMPACT_METRICS = [
  {
    icon: '📊',
    label: 'Analysis Completed',
    getValue: (data: OperationalImpact) =>
      `${data.analysisCompleted.totalPallets} pallets processed in ${data.analysisCompleted.processingTime.toFixed(2)} seconds`
  },
  {
    icon: '🎯',
    label: 'Problems Prevented',
    getValue: (data: OperationalImpact) =>
      `${data.problemsPrevented.totalIssues} ${data.problemsPrevented.description}`
  },
  {
    icon: '✅',
    label: 'Issues Resolved',
    getValue: (data: OperationalImpact) =>
      `${data.issuesResolved.resolvedCount} ${data.issuesResolved.description}`
  },
  {
    icon: '⚡',
    label: 'Processing Efficiency',
    getValue: (data: OperationalImpact) =>
      `${data.processingEfficiency.recordsPerSecond} records per second (${data.processingEfficiency.rating})`
  }
];
```

### Implementation Notes
- Display metrics in vertical list format
- Use light background for each metric row
- Add hover effect for subtle interactivity
- Summary text should be concise and professional
- Update efficiency rating color based on performance level

---

## RESPONSIVE DESIGN SPECIFICATIONS

### Desktop (≥1024px)
```css
.track-your-wins-container {
  display: grid;
  grid-template-columns: 1fr 2fr; /* Left: Health Score, Right: Achievements */
  gap: 24px;
  padding: 24px;
}

.highlights-row {
  grid-column: 1 / -1;
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 16px;
}

.middle-section {
  grid-column: 1 / -1;
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 24px;
}

.full-width-sections {
  grid-column: 1 / -1;
}
```

### Tablet (768px - 1023px)
```css
.track-your-wins-container {
  grid-template-columns: 1fr;
}

.highlights-row {
  grid-template-columns: repeat(2, 1fr);
}

.middle-section {
  grid-template-columns: 1fr;
}
```

### Mobile (<768px)
```css
.track-your-wins-container {
  padding: 16px;
  gap: 16px;
}

.highlights-row {
  grid-template-columns: 1fr;
}

.achievement-badge-grid {
  grid-template-columns: repeat(2, 1fr);
}
```

---

## BRAND COLOR PALETTE

### Primary Colors
```css
:root {
  /* Safety Orange - Primary Action */
  --color-primary: #FF6B35;
  --color-primary-hover: #E55A2B;

  /* Steel Gray - Authority */
  --color-secondary: #4A5568;
  --color-text-primary: #2D3748;
  --color-text-secondary: #718096;

  /* Warehouse Green - Success */
  --color-success: #38A169;
  --color-success-light: #F0FFF4;

  /* Hi-Vis Yellow - Warning */
  --color-warning: #F7DC6F;
  --color-warning-light: #FFFBEB;

  /* Industrial Red - Danger */
  --color-danger: #E53E3E;
  --color-danger-light: #FED7D7;

  /* Neutral Colors */
  --color-white: #FFFFFF;
  --color-gray-50: #F7FAFC;
  --color-gray-100: #EDF2F7;
  --color-gray-200: #E2E8F0;
  --color-gray-300: #CBD5E0;
  --color-gray-400: #A0AEC0;
}
```

---

## TYPOGRAPHY SYSTEM

### Font Family
```css
:root {
  --font-primary: 'Roboto', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
}

body {
  font-family: var(--font-primary);
}
```

### Type Scale
```css
/* Headers */
.text-h1 {
  font-size: 32px;
  font-weight: 700;
  line-height: 1.2;
}

.text-h2 {
  font-size: 24px;
  font-weight: 700;
  line-height: 1.3;
}

.text-h3 {
  font-size: 18px;
  font-weight: 600;
  line-height: 1.4;
}

/* Body */
.text-body-large {
  font-size: 16px;
  font-weight: 400;
  line-height: 1.5;
}

.text-body {
  font-size: 14px;
  font-weight: 400;
  line-height: 1.5;
}

/* Labels */
.text-label {
  font-size: 12px;
  font-weight: 500;
  line-height: 1.4;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

/* Action Text */
.text-action {
  font-size: 14px;
  font-weight: 600;
  line-height: 1.4;
}
```

---

## DATA API REQUIREMENTS

### Analysis Result Data Structure

```typescript
interface AnalysisResult {
  // Metadata
  reportId: string;
  timestamp: Date;
  warehouseId: string;

  // Processing Metrics
  processingTime: number;        // seconds
  totalPallets: number;
  totalRecords: number;

  // Space Analytics
  spaceUtilization: number;      // percentage
  totalLocations: number;
  availableLocations: number;
  validLocations: number;

  // Data Quality
  locationValidationRate: number;  // percentage
  formatComplianceRate: number;    // percentage

  // Anomaly Summary
  totalAnomalies: number;
  anomalies: {
    forgottenPallets: number;
    stuckPallets: number;
    overcapacity: number;
    invalidLocations: number;
    duplicateScans: number;
    incompleteLots: number;
  };

  // Location Data
  locations: LocationData[];

  // Rule Performance
  rulePerformance: {
    totalRules: number;
    successfulRules: number;
    executionTimes: Record<string, number>;
  };
}

interface LocationData {
  id: string;
  name: string;
  type: 'RECEIVING' | 'AISLE' | 'DOCK' | 'STAGING' | 'STORAGE' | 'TRANSITIONAL';
  classification: 'special' | 'standard';
  anomalyCount: number;
  capacity: number;
  currentOccupancy: number;
}
```

### API Endpoints Required

```typescript
// Get analysis results for Track Your Wins display
GET /api/v1/reports/{reportId}/wins
Response: AnalysisResult

// Get resolution status
GET /api/v1/reports/{reportId}/resolution-status
Response: ResolutionTracker

// Mark anomalies as resolved
POST /api/v1/anomalies/resolve
Body: {
  reportId: string;
  anomalyIds: string[];
  resolvedBy: string;
}
Response: { success: boolean; updated: number; }
```

---

## STATE MANAGEMENT

### Zustand Store Structure

```typescript
// /frontend/lib/track-wins-store.ts

import { create } from 'zustand';

interface TrackWinsState {
  // Data
  analysisResult: AnalysisResult | null;
  resolutionStatus: ResolutionTracker | null;

  // Loading States
  isLoading: boolean;
  error: string | null;

  // Actions
  loadWinsData: (reportId: string) => Promise<void>;
  loadResolutionStatus: (reportId: string) => Promise<void>;
  markAnomaliesResolved: (anomalyIds: string[]) => Promise<void>;
  reset: () => void;
}

export const useTrackWinsStore = create<TrackWinsState>((set, get) => ({
  analysisResult: null,
  resolutionStatus: null,
  isLoading: false,
  error: null,

  loadWinsData: async (reportId: string) => {
    set({ isLoading: true, error: null });
    try {
      const response = await fetch(`/api/v1/reports/${reportId}/wins`);
      const data = await response.json();
      set({ analysisResult: data, isLoading: false });
    } catch (error) {
      set({ error: error.message, isLoading: false });
    }
  },

  loadResolutionStatus: async (reportId: string) => {
    try {
      const response = await fetch(`/api/v1/reports/${reportId}/resolution-status`);
      const data = await response.json();
      set({ resolutionStatus: data });
    } catch (error) {
      console.error('Failed to load resolution status:', error);
    }
  },

  markAnomaliesResolved: async (anomalyIds: string[]) => {
    const state = get();
    if (!state.analysisResult) return;

    try {
      await fetch('/api/v1/anomalies/resolve', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          reportId: state.analysisResult.reportId,
          anomalyIds
        })
      });

      // Reload resolution status
      await state.loadResolutionStatus(state.analysisResult.reportId);
    } catch (error) {
      console.error('Failed to mark anomalies as resolved:', error);
    }
  },

  reset: () => set({
    analysisResult: null,
    resolutionStatus: null,
    isLoading: false,
    error: null
  })
}));
```

---

## COMPONENT FILE STRUCTURE

```
/frontend/components/dashboard/views/track-your-wins/
├── index.tsx                          # Main container component
├── HealthScoreGauge.tsx              # Element 1
├── AchievementBadges.tsx             # Element 2
├── ReportHighlights.tsx              # Element 3
├── ProblemResolutionScorecard.tsx    # Element 4
├── AnomaliesResolvedTracker.tsx      # Element 5
├── SpecialLocationSpotlight.tsx      # Element 6
└── OperationalImpact.tsx             # Element 7
```

### Main Container Component

```typescript
// /frontend/components/dashboard/views/track-your-wins/index.tsx

import React, { useEffect } from 'react';
import { useTrackWinsStore } from '@/lib/track-wins-store';
import HealthScoreGauge from './HealthScoreGauge';
import AchievementBadges from './AchievementBadges';
import ReportHighlights from './ReportHighlights';
import ProblemResolutionScorecard from './ProblemResolutionScorecard';
import AnomaliesResolvedTracker from './AnomaliesResolvedTracker';
import SpecialLocationSpotlight from './SpecialLocationSpotlight';
import OperationalImpact from './OperationalImpact';

interface TrackYourWinsProps {
  reportId: string;
}

export default function TrackYourWins({ reportId }: TrackYourWinsProps) {
  const {
    analysisResult,
    resolutionStatus,
    isLoading,
    error,
    loadWinsData,
    loadResolutionStatus
  } = useTrackWinsStore();

  useEffect(() => {
    if (reportId) {
      loadWinsData(reportId);
      loadResolutionStatus(reportId);
    }
  }, [reportId]);

  if (isLoading) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="text-lg text-gray-600">Loading your wins...</div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="text-lg text-red-600">Error: {error}</div>
      </div>
    );
  }

  if (!analysisResult) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="text-lg text-gray-600">No data available</div>
      </div>
    );
  }

  return (
    <div className="track-your-wins-container p-6 bg-gray-50 min-h-screen">
      <h1 className="text-3xl font-bold text-gray-800 mb-6">
        Track Your Wins
      </h1>

      {/* Top Section: Health Score + Achievements */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 mb-6">
        <div className="lg:col-span-1">
          <HealthScoreGauge data={analysisResult} />
        </div>
        <div className="lg:col-span-2">
          <AchievementBadges data={analysisResult} />
        </div>
      </div>

      {/* Report Highlights */}
      <div className="mb-6">
        <ReportHighlights data={analysisResult} />
      </div>

      {/* Middle Section: Scorecard + Resolution Tracker */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-6">
        <ProblemResolutionScorecard data={analysisResult} />
        <AnomaliesResolvedTracker
          data={analysisResult}
          resolutionStatus={resolutionStatus}
        />
      </div>

      {/* Special Location Spotlight */}
      <div className="mb-6">
        <SpecialLocationSpotlight data={analysisResult} />
      </div>

      {/* Operational Impact Summary */}
      <div>
        <OperationalImpact
          data={analysisResult}
          resolutionStatus={resolutionStatus}
        />
      </div>
    </div>
  );
}
```

---

## TESTING REQUIREMENTS

### Unit Tests
- Test health score calculation with various input values
- Test achievement criteria evaluation
- Test time formatting functions
- Test data transformation utilities

### Integration Tests
- Test API data fetching and error handling
- Test resolution status updates
- Test navigation to Action Hub with filters

### Visual Regression Tests
- Test responsive layouts at different breakpoints
- Test color schemes and brand consistency
- Test animation behaviors

---

## PERFORMANCE CONSIDERATIONS

### Optimization Strategies
1. **Lazy Loading:** Load Track Your Wins data only when navigating to the section
2. **Memoization:** Use React.memo for expensive components
3. **Debouncing:** Debounce resolution status updates
4. **Caching:** Cache wins data for quick re-renders

### Example Memoization

```typescript
import { memo } from 'react';

const HealthScoreGauge = memo(({ data }: { data: AnalysisResult }) => {
  // Component implementation
}, (prevProps, nextProps) => {
  // Custom comparison: only re-render if score changed
  return prevProps.data.reportId === nextProps.data.reportId;
});
```

---

## ACCESSIBILITY REQUIREMENTS

### ARIA Labels
- Add `aria-label` to all interactive elements
- Use semantic HTML (`<button>`, `<nav>`, etc.)
- Provide screen reader announcements for dynamic updates

### Keyboard Navigation
- Ensure all interactive elements are keyboard-accessible
- Provide focus indicators
- Support tab navigation through badges and buttons

### Color Contrast
- Ensure text meets WCAG AA standards (4.5:1 ratio)
- Provide text alternatives to color-only indicators

---

## FUTURE ENHANCEMENTS

### Phase 2 Features
1. **Historical Comparison:** "20% better than last report"
2. **Streak Tracking:** "5 consecutive reports with 85+ health score"
3. **Team Leaderboards:** "Top performing shift this week"
4. **Export Functionality:** Download wins summary as PDF
5. **Sharing:** Share achievements via email or print

---

## IMPLEMENTATION CHECKLIST

### Backend Requirements
- [ ] Create `/api/v1/reports/{reportId}/wins` endpoint
- [ ] Create `/api/v1/reports/{reportId}/resolution-status` endpoint
- [ ] Create `/api/v1/anomalies/resolve` endpoint
- [ ] Implement resolution tracking in database
- [ ] Add timestamp tracking for resolved anomalies

### Frontend Requirements
- [ ] Create Zustand store for Track Your Wins state
- [ ] Implement 7 component files
- [ ] Add responsive CSS Grid layouts
- [ ] Integrate with existing dashboard navigation
- [ ] Add loading and error states
- [ ] Implement animations and transitions
- [ ] Add Radix UI components for accessibility
- [ ] Write unit tests for calculations
- [ ] Test responsive layouts
- [ ] Verify brand color usage

### Design Requirements
- [ ] Verify Roboto font is loaded
- [ ] Confirm color palette matches brand guidelines
- [ ] Test iconography consistency
- [ ] Review warehouse-native language in all copy
- [ ] Validate professional tone throughout

---

## GLOSSARY

- **Health Score:** Calculated metric (0-100) representing overall warehouse operational excellence
- **Achievement Badge:** Visual indicator of specific performance milestone reached
- **Resolution Status:** Tracking of which detected anomalies have been addressed
- **Special Location:** Non-standard warehouse areas (RECEIVING, AISLE, DOCK, STAGING)
- **Anomaly:** Detected operational issue requiring attention
- **Warehouse-Native:** Language and visual patterns familiar to warehouse operators

---

## CONTACT & SUPPORT

For questions during implementation:
- Review WAREHOUSE_INTELLIGENCE_UX_STRATEGY.md for UX context
- Review BRAND_FOUNDATION_DOCUMENT.md for brand guidelines
- Review WAREHOUSE_ANALYTICS_DATA_CATALOG.md for data sources

---

**Document Version:** 1.0
**Last Updated:** 2025-10-02
**Status:** Ready for Development
