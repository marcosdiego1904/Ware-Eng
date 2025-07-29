# Automatic Database Migration System

## Overview
Your application now includes an **automatic database migration system** that ensures your production database is always properly initialized with rules and tables.

## How It Works

### 1. Automatic Initialization
- **On every app startup**, the system automatically:
  - ✅ Creates all required database tables
  - ✅ Seeds default rules if none exist
  - ✅ Creates basic location mappings
  - ✅ Handles both SQLite (dev) and PostgreSQL (prod)

### 2. Smart Detection
- **Checks if rules exist** before seeding
- **Only creates missing components** (no duplicates)
- **Safe to run multiple times** (idempotent)

### 3. Zero Configuration Required
- **No manual intervention needed**
- **Works on first deployment**
- **Works on every subsequent deployment**

## Files Added

### `src/auto_migrate.py`
The core auto-migration system that:
- Creates database tables
- Seeds 8 default rules across 3 categories
- Creates basic location mappings
- Handles errors gracefully

### `deploy.py`
Optional deployment script for manual migration if needed.

## Health Check Endpoint

Check your database status anytime:
```
GET /api/v1/health
```

Response:
```json
{
  "status": "healthy",
  "database": "connected", 
  "rules": {
    "active_rules": 8,
    "categories": 3,
    "locations": 4
  },
  "enhanced_engine": true,
  "timestamp": "2025-07-29T16:30:00.000Z"
}
```

## What This Solves

### Before (Manual):
❌ Had to visit `/init-db/` URL after each deployment  
❌ Production database missing tables  
❌ Analysis returning 0 anomalies  
❌ Manual intervention required  

### After (Automatic):
✅ Database initialized on every startup  
✅ Rules automatically seeded  
✅ Analysis works immediately  
✅ Zero manual intervention  

## Default Rules Created

The system automatically creates these 8 rules:

**FLOW & TIME Rules (Priority: Maximum)**
1. Forgotten Pallets Alert (VERY_HIGH)
2. Incomplete Lots Alert (VERY_HIGH)  
3. AISLE Stuck Pallets (HIGH)

**SPACE Rules (Priority: High)**
4. Overcapacity Alert (HIGH)
5. Invalid Locations Alert (HIGH)
6. Scanner Error Detection (MEDIUM)
7. Location Type Mismatches (HIGH)

**PRODUCT Rules (Priority: Medium)**
8. Cold Chain Violations (VERY_HIGH)

## Deployment Process

### Vercel Deployment
1. **Push to repository**
2. **Vercel auto-deploys**
3. **App starts up**
4. **Auto-migration runs**
5. **Database ready**
6. **Analysis works immediately**

### Manual Migration (if needed)
```bash
python deploy.py
```

## Monitoring

- **Check health**: `GET /api/v1/health`
- **View logs**: Vercel dashboard function logs
- **Auto-migration logs**: Shown during startup

## Error Handling

If auto-migration fails:
- **App still starts** (doesn't crash)
- **Error logged** to console
- **Falls back to legacy engine** if available
- **Health check shows status**

Your application is now **fully automated** and will work correctly on every deployment without any manual intervention!