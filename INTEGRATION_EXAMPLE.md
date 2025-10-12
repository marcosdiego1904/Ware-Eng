# Action Center Event-Driven Updates - Integration Guide

## Overview
The Action Center now uses **event-driven updates** instead of auto-refresh timers. It only updates when anomalies are actually resolved or when manually refreshed.

## Integration Methods

### Method 1: Component Reference (Recommended)
```typescript
// In your parent component (enhanced overview)
import { useRef } from 'react'
import { ActionCenterView, ActionCenterRef } from './action-center'

const actionCenterRef = useRef<ActionCenterRef>(null)

// In your anomaly resolution callback
const handleAnomalyResolved = () => {
  // This will immediately update Action Center metrics
  actionCenterRef.current?.notifyAnomalyResolved()

  // Show success feedback
  toast.success("Anomaly resolved! Action Center updated.")
}

<ActionCenterView
  ref={actionCenterRef}
  onAnomalyResolved={() => console.log('Anomaly resolved event')}
  onDataRefresh={() => console.log('Data refreshed event')}
/>
```

### Method 2: Callback Props
```typescript
// When anomaly is resolved in BusinessIntelligenceReport component
onAnomalyResolved={(anomalyId: string) => {
  // Your existing resolution logic
  setResolvedAnomalies(prev => prev.add(anomalyId))

  // Notify Action Center (passed via props)
  onActionCenterUpdate?.()
}}
```

### Method 3: Event Bus Pattern (Future Enhancement)
```typescript
// Global event system for dashboard updates
eventBus.emit('anomaly:resolved', {
  anomalyId,
  location,
  type: 'Stagnant Pallet'
})

// Action Center listens for these events
useEffect(() => {
  const handleAnomalyResolved = () => loadData()
  eventBus.on('anomaly:resolved', handleAnomalyResolved)
  return () => eventBus.off('anomaly:resolved', handleAnomalyResolved)
}, [])
```

## What's Changed

### ❌ Removed (Old Auto-Refresh System):
- 30-second automatic polling
- Constant API requests
- Battery drain on mobile
- Disruption during analysis

### ✅ Added (New Event-Driven System):
- **Smart refresh button** - highlights when updates are available
- **"Updates available" indicator** - shows when data has changed
- **Event callbacks** - integrates with existing resolution workflow
- **Manual refresh** - user controls when to update
- **Ref-based API** - allows external components to trigger updates

## User Experience

### Before:
- Page refreshed every 30 seconds regardless of activity
- Jarring interruptions during detailed analysis
- Wasted bandwidth and battery

### After:
- **Immediate feedback** when user resolves anomalies
- **Stable experience** - no unexpected refreshes
- **Smart indicators** - button glows blue when updates are ready
- **User control** - refresh only when needed

## Integration in Your Reports Component

You can connect this to your existing anomaly resolution in `BusinessIntelligenceReport`:

```typescript
// In business-intelligence-report.tsx
onAnomalyResolved={(anomalyId: string) => {
  // Your existing logic
  setResolvedAnomalies(prev => prev.add(anomalyId))

  // NEW: Notify Action Center
  if (onActionCenterUpdate) {
    onActionCenterUpdate()
  }
}}
```

This creates a responsive, efficient dashboard that updates exactly when needed - when your team actually resolves issues!