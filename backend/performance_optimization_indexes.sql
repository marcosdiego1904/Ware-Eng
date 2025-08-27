-- CRITICAL PERFORMANCE OPTIMIZATION: Database Indexes
-- This script adds indexes to dramatically improve warehouse query performance
-- Run this on both development (SQLite) and production (PostgreSQL) databases

-- Index 1: Primary warehouse filtering index
-- Used by: Location.query.filter(Location.warehouse_id == warehouse_id)
-- Expected improvement: 10-100x faster warehouse location queries
CREATE INDEX IF NOT EXISTS idx_location_warehouse_id ON location(warehouse_id);

-- Index 2: Compound index for warehouse + active filtering
-- Used by: Location.query.filter(Location.warehouse_id == warehouse_id, Location.is_active == True)  
-- Expected improvement: 50-200x faster filtered queries
CREATE INDEX IF NOT EXISTS idx_location_active_warehouse ON location(warehouse_id, is_active);

-- Index 3: Compound index for warehouse + location code lookups
-- Used by: Location lookups during inventory validation
-- Expected improvement: 20-100x faster location code searches
CREATE INDEX IF NOT EXISTS idx_location_code_warehouse ON location(warehouse_id, code);

-- Index 4: Location code index for general lookups
-- Used by: _find_location_by_code() methods
-- Expected improvement: 10-50x faster location code searches  
CREATE INDEX IF NOT EXISTS idx_location_code ON location(code);

-- Index 5: Location type index for rule evaluation
-- Used by: Location type filtering in rule evaluators
-- Expected improvement: 5-20x faster location type queries
CREATE INDEX IF NOT EXISTS idx_location_type ON location(location_type);

-- Verify indexes were created (PostgreSQL syntax - adjust for SQLite if needed)
-- SELECT indexname, tablename FROM pg_indexes WHERE tablename = 'location' ORDER BY indexname;

-- Performance monitoring query - run this after creating indexes to verify improvement
-- SELECT 
--     warehouse_id, 
--     COUNT(*) as location_count,
--     COUNT(CASE WHEN is_active = true OR is_active IS NULL THEN 1 END) as active_count
-- FROM location 
-- GROUP BY warehouse_id 
-- ORDER BY location_count DESC;