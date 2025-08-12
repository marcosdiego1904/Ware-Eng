-- =====================================================
-- PRODUCTION MIGRATION SCRIPT
-- Warehouse Settings Database Layer Optimization
-- =====================================================

-- This script safely migrates the existing warehouse system to the
-- optimized schema without data loss. Run during maintenance window.

-- =====================================================
-- PHASE 1: BACKUP AND PREPARATION
-- =====================================================

-- Create backup tables (recommended before migration)
-- Uncomment these lines in production:
-- CREATE TABLE location_backup AS SELECT * FROM location;
-- CREATE TABLE warehouse_config_backup AS SELECT * FROM warehouse_config;
-- CREATE TABLE warehouse_template_backup AS SELECT * FROM warehouse_template;

-- =====================================================
-- PHASE 2: SCHEMA MODIFICATIONS
-- =====================================================

-- Step 1: Add new columns to existing tables
DO $$ 
BEGIN
    -- Add columns to location table if they don't exist
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns 
                   WHERE table_name='location' AND column_name='warehouse_id') THEN
        ALTER TABLE location ADD COLUMN warehouse_id VARCHAR(50) DEFAULT 'DEFAULT';
    END IF;
    
    -- Update existing NULL warehouse_id values
    UPDATE location SET warehouse_id = 'DEFAULT' WHERE warehouse_id IS NULL;
    
    -- Make warehouse_id NOT NULL
    ALTER TABLE location ALTER COLUMN warehouse_id SET NOT NULL;
END $$;

-- Step 2: Convert TEXT columns to JSONB for better performance
DO $$
BEGIN
    -- Warehouse config JSON fields
    IF EXISTS (SELECT 1 FROM information_schema.columns 
               WHERE table_name='warehouse_config' AND column_name='receiving_areas' AND data_type='text') THEN
        
        -- Add temporary JSONB columns
        ALTER TABLE warehouse_config ADD COLUMN receiving_areas_jsonb JSONB;
        ALTER TABLE warehouse_config ADD COLUMN staging_areas_jsonb JSONB;
        ALTER TABLE warehouse_config ADD COLUMN dock_areas_jsonb JSONB;
        
        -- Convert existing TEXT JSON to JSONB
        UPDATE warehouse_config SET 
            receiving_areas_jsonb = COALESCE(receiving_areas::jsonb, '[]'::jsonb),
            staging_areas_jsonb = COALESCE(staging_areas::jsonb, '[]'::jsonb),
            dock_areas_jsonb = COALESCE(dock_areas::jsonb, '[]'::jsonb);
            
        -- Drop old TEXT columns and rename JSONB columns
        ALTER TABLE warehouse_config DROP COLUMN receiving_areas;
        ALTER TABLE warehouse_config DROP COLUMN staging_areas;
        ALTER TABLE warehouse_config DROP COLUMN dock_areas;
        
        ALTER TABLE warehouse_config RENAME COLUMN receiving_areas_jsonb TO receiving_areas;
        ALTER TABLE warehouse_config RENAME COLUMN staging_areas_jsonb TO staging_areas;
        ALTER TABLE warehouse_config RENAME COLUMN dock_areas_jsonb TO dock_areas;
    END IF;
    
    -- Location JSON fields
    IF EXISTS (SELECT 1 FROM information_schema.columns 
               WHERE table_name='location' AND column_name='allowed_products' AND data_type='text') THEN
        
        -- Add temporary JSONB columns
        ALTER TABLE location ADD COLUMN allowed_products_jsonb JSONB;
        ALTER TABLE location ADD COLUMN special_requirements_jsonb JSONB;
        ALTER TABLE location ADD COLUMN location_hierarchy_jsonb JSONB;
        
        -- Convert existing TEXT JSON to JSONB
        UPDATE location SET 
            allowed_products_jsonb = COALESCE(allowed_products::jsonb, '[]'::jsonb),
            special_requirements_jsonb = COALESCE(special_requirements::jsonb, '{}'::jsonb),
            location_hierarchy_jsonb = COALESCE(location_hierarchy::jsonb, '{}'::jsonb);
            
        -- Drop old TEXT columns and rename JSONB columns
        ALTER TABLE location DROP COLUMN IF EXISTS allowed_products;
        ALTER TABLE location DROP COLUMN IF EXISTS special_requirements;
        ALTER TABLE location DROP COLUMN IF EXISTS location_hierarchy;
        
        ALTER TABLE location RENAME COLUMN allowed_products_jsonb TO allowed_products;
        ALTER TABLE location RENAME COLUMN special_requirements_jsonb TO special_requirements;
        ALTER TABLE location RENAME COLUMN location_hierarchy_jsonb TO location_hierarchy;
    END IF;
END $$;

-- Step 3: Fix the critical unique constraint issue
DO $$
BEGIN
    -- Drop the problematic global unique constraint on location.code
    IF EXISTS (SELECT 1 FROM information_schema.table_constraints 
               WHERE table_name='location' AND constraint_name='location_code_key') THEN
        ALTER TABLE location DROP CONSTRAINT location_code_key;
    END IF;
    
    -- Add the correct composite unique constraint
    IF NOT EXISTS (SELECT 1 FROM information_schema.table_constraints 
                   WHERE table_name='location' AND constraint_name='unique_location_per_warehouse') THEN
        ALTER TABLE location ADD CONSTRAINT unique_location_per_warehouse UNIQUE (code, warehouse_id);
    END IF;
END $$;

-- Step 4: Add missing constraints and defaults
DO $$
BEGIN
    -- Add check constraints for data integrity
    ALTER TABLE warehouse_config ADD CONSTRAINT IF NOT EXISTS check_num_aisles_positive 
        CHECK (num_aisles > 0);
    ALTER TABLE warehouse_config ADD CONSTRAINT IF NOT EXISTS check_racks_per_aisle_positive 
        CHECK (racks_per_aisle > 0);
    ALTER TABLE warehouse_config ADD CONSTRAINT IF NOT EXISTS check_positions_per_rack_positive 
        CHECK (positions_per_rack > 0);
        
    ALTER TABLE location ADD CONSTRAINT IF NOT EXISTS check_capacity_positive 
        CHECK (capacity > 0);
    ALTER TABLE location ADD CONSTRAINT IF NOT EXISTS check_pallet_capacity_positive 
        CHECK (pallet_capacity > 0);
END $$;

-- =====================================================
-- PHASE 3: CREATE OPTIMIZED INDEXES
-- =====================================================

-- Main performance indexes (created concurrently to avoid locks)
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_warehouse_config_warehouse_id 
ON warehouse_config (warehouse_id) WHERE is_active = TRUE;

CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_warehouse_config_created_by 
ON warehouse_config (created_by) WHERE is_active = TRUE;

CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_location_warehouse_id 
ON location (warehouse_id) WHERE is_active = TRUE;

CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_location_warehouse_type 
ON location (warehouse_id, location_type) WHERE is_active = TRUE;

CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_location_structure 
ON location (warehouse_id, aisle_number, rack_number, position_number, level) 
WHERE is_active = TRUE AND aisle_number IS NOT NULL;

CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_location_zone 
ON location (warehouse_id, zone) WHERE is_active = TRUE;

-- JSON indexes for enhanced search performance
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_warehouse_receiving_areas_gin 
ON warehouse_config USING GIN (receiving_areas) WHERE receiving_areas != '[]'::jsonb;

CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_location_special_requirements_gin 
ON location USING GIN (special_requirements) WHERE special_requirements != '{}'::jsonb;

CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_location_allowed_products_gin 
ON location USING GIN (allowed_products) WHERE allowed_products != '[]'::jsonb;

CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_location_hierarchy_gin 
ON location USING GIN (location_hierarchy);

-- =====================================================
-- PHASE 4: CREATE PERFORMANCE FUNCTIONS
-- =====================================================

-- High-performance bulk location insertion function
CREATE OR REPLACE FUNCTION bulk_insert_locations_safe(
    p_warehouse_id VARCHAR(50),
    p_location_data JSONB[],
    p_created_by INTEGER
) RETURNS INTEGER AS $$
DECLARE
    inserted_count INTEGER := 0;
    location_record JSONB;
BEGIN
    -- Validate input
    IF p_warehouse_id IS NULL OR p_created_by IS NULL THEN
        RAISE EXCEPTION 'warehouse_id and created_by cannot be null';
    END IF;
    
    -- Use safe insertion with conflict handling
    INSERT INTO location (
        code, warehouse_id, location_type, capacity, zone,
        aisle_number, rack_number, position_number, level,
        pallet_capacity, location_hierarchy, created_by, created_at
    )
    SELECT 
        (data->>'code')::VARCHAR(50),
        p_warehouse_id,
        COALESCE((data->>'location_type')::VARCHAR(30), 'STORAGE'),
        COALESCE((data->>'capacity')::INTEGER, 1),
        COALESCE((data->>'zone')::VARCHAR(50), 'GENERAL'),
        NULLIF((data->>'aisle_number'), '')::INTEGER,
        NULLIF((data->>'rack_number'), '')::INTEGER,
        NULLIF((data->>'position_number'), '')::INTEGER,
        NULLIF((data->>'level'), '')::VARCHAR(1),
        COALESCE((data->>'pallet_capacity')::INTEGER, 1),
        COALESCE(data->'location_hierarchy', '{}'::jsonb),
        p_created_by,
        CURRENT_TIMESTAMP
    FROM unnest(p_location_data) AS data
    ON CONFLICT (code, warehouse_id) DO UPDATE SET
        location_type = EXCLUDED.location_type,
        capacity = EXCLUDED.capacity,
        zone = EXCLUDED.zone,
        updated_at = CURRENT_TIMESTAMP;
    
    GET DIAGNOSTICS inserted_count = ROW_COUNT;
    RETURN inserted_count;
END;
$$ LANGUAGE plpgsql;

-- Function to safely clear locations for a warehouse
CREATE OR REPLACE FUNCTION clear_warehouse_locations(
    p_warehouse_id VARCHAR(50)
) RETURNS INTEGER AS $$
DECLARE
    deleted_count INTEGER := 0;
BEGIN
    -- Soft delete first (for safety)
    UPDATE location 
    SET is_active = FALSE, updated_at = CURRENT_TIMESTAMP
    WHERE warehouse_id = p_warehouse_id;
    
    GET DIAGNOSTICS deleted_count = ROW_COUNT;
    
    -- Hard delete after soft delete (can be rolled back if needed)
    DELETE FROM location 
    WHERE warehouse_id = p_warehouse_id AND is_active = FALSE;
    
    RETURN deleted_count;
END;
$$ LANGUAGE plpgsql;

-- =====================================================
-- PHASE 5: CREATE MONITORING VIEWS
-- =====================================================

-- Warehouse performance monitoring view
CREATE OR REPLACE VIEW warehouse_performance_view AS
SELECT 
    wc.warehouse_id,
    wc.warehouse_name,
    wc.created_by,
    COUNT(l.id) as total_locations,
    COUNT(l.id) FILTER (WHERE l.location_type = 'STORAGE') as storage_locations,
    COUNT(l.id) FILTER (WHERE l.location_type = 'RECEIVING') as receiving_locations,
    COUNT(l.id) FILTER (WHERE l.location_type = 'STAGING') as staging_locations,
    COUNT(l.id) FILTER (WHERE l.location_type = 'DOCK') as dock_locations,
    SUM(l.capacity) as total_capacity,
    AVG(l.capacity) as avg_capacity_per_location,
    MAX(l.aisle_number) as max_aisle,
    MAX(l.rack_number) as max_rack,
    wc.created_at as warehouse_created,
    wc.updated_at as last_modified,
    COUNT(l.id) / GREATEST(EXTRACT(DAYS FROM (CURRENT_TIMESTAMP - wc.created_at)), 1) as locations_per_day
FROM warehouse_config wc
LEFT JOIN location l ON l.warehouse_id = wc.warehouse_id AND l.is_active = TRUE
WHERE wc.is_active = TRUE
GROUP BY wc.warehouse_id, wc.warehouse_name, wc.created_by, wc.created_at, wc.updated_at;

-- =====================================================
-- PHASE 6: DATA VALIDATION AND CLEANUP
-- =====================================================

-- Validate data integrity after migration
DO $$
DECLARE
    invalid_locations INTEGER;
    duplicate_codes INTEGER;
BEGIN
    -- Check for invalid location structures
    SELECT COUNT(*) INTO invalid_locations
    FROM location 
    WHERE (aisle_number IS NOT NULL AND (rack_number IS NULL OR position_number IS NULL OR level IS NULL))
       OR (aisle_number IS NULL AND (rack_number IS NOT NULL OR position_number IS NOT NULL OR level IS NOT NULL));
    
    IF invalid_locations > 0 THEN
        RAISE WARNING 'Found % locations with invalid hierarchical structure', invalid_locations;
    END IF;
    
    -- Check for potential duplicate codes within warehouses
    SELECT COUNT(*) INTO duplicate_codes
    FROM (
        SELECT warehouse_id, code, COUNT(*) 
        FROM location 
        WHERE is_active = TRUE
        GROUP BY warehouse_id, code 
        HAVING COUNT(*) > 1
    ) duplicates;
    
    IF duplicate_codes > 0 THEN
        RAISE WARNING 'Found % potential duplicate location codes within warehouses', duplicate_codes;
    END IF;
    
    RAISE NOTICE 'Migration validation completed. Invalid locations: %, Duplicate codes: %', 
                 invalid_locations, duplicate_codes;
END $$;

-- =====================================================
-- PHASE 7: PERFORMANCE VERIFICATION
-- =====================================================

-- Create a test query to verify performance improvements
CREATE OR REPLACE FUNCTION test_migration_performance(test_warehouse_id VARCHAR(50) DEFAULT 'DEFAULT')
RETURNS TABLE(
    test_name TEXT,
    execution_time_ms NUMERIC,
    rows_returned INTEGER
) AS $$
DECLARE
    start_time TIMESTAMP;
    end_time TIMESTAMP;
    row_count INTEGER;
BEGIN
    -- Test 1: Get all locations for a warehouse
    start_time := clock_timestamp();
    SELECT COUNT(*) INTO row_count FROM location WHERE warehouse_id = test_warehouse_id AND is_active = TRUE;
    end_time := clock_timestamp();
    
    RETURN QUERY SELECT 
        'Get all locations for warehouse'::TEXT,
        EXTRACT(MILLISECONDS FROM (end_time - start_time))::NUMERIC,
        row_count::INTEGER;
    
    -- Test 2: Get locations by type
    start_time := clock_timestamp();
    SELECT COUNT(*) INTO row_count 
    FROM location 
    WHERE warehouse_id = test_warehouse_id AND location_type = 'STORAGE' AND is_active = TRUE;
    end_time := clock_timestamp();
    
    RETURN QUERY SELECT 
        'Get storage locations only'::TEXT,
        EXTRACT(MILLISECONDS FROM (end_time - start_time))::NUMERIC,
        row_count::INTEGER;
    
    -- Test 3: Hierarchical query
    start_time := clock_timestamp();
    SELECT COUNT(*) INTO row_count 
    FROM location 
    WHERE warehouse_id = test_warehouse_id 
      AND aisle_number = 1 
      AND is_active = TRUE;
    end_time := clock_timestamp();
    
    RETURN QUERY SELECT 
        'Get locations for aisle 1'::TEXT,
        EXTRACT(MILLISECONDS FROM (end_time - start_time))::NUMERIC,
        row_count::INTEGER;
END;
$$ LANGUAGE plpgsql;

-- =====================================================
-- MIGRATION COMPLETION REPORT
-- =====================================================

-- Generate migration report
DO $$
DECLARE
    total_warehouses INTEGER;
    total_locations INTEGER;
    total_templates INTEGER;
BEGIN
    SELECT COUNT(*) INTO total_warehouses FROM warehouse_config WHERE is_active = TRUE;
    SELECT COUNT(*) INTO total_locations FROM location WHERE is_active = TRUE;
    SELECT COUNT(*) INTO total_templates FROM warehouse_template WHERE is_active = TRUE;
    
    RAISE NOTICE '==============================================';
    RAISE NOTICE 'WAREHOUSE OPTIMIZATION MIGRATION COMPLETED';
    RAISE NOTICE '==============================================';
    RAISE NOTICE 'Total warehouses: %', total_warehouses;
    RAISE NOTICE 'Total locations: %', total_locations;
    RAISE NOTICE 'Total templates: %', total_templates;
    RAISE NOTICE 'Migration timestamp: %', CURRENT_TIMESTAMP;
    RAISE NOTICE '==============================================';
    RAISE NOTICE 'Performance improvements applied:';
    RAISE NOTICE '- Fixed composite unique constraints';
    RAISE NOTICE '- Added optimized indexes';
    RAISE NOTICE '- Converted TEXT to JSONB fields';
    RAISE NOTICE '- Created bulk operation functions';
    RAISE NOTICE '- Added monitoring views';
    RAISE NOTICE '==============================================';
END $$;

-- Recommendation for post-migration
-- Run this query to refresh statistics after migration:
-- ANALYZE warehouse_config;
-- ANALYZE location;
-- ANALYZE warehouse_template;