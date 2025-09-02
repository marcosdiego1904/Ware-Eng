-- Smart Configuration System - PostgreSQL Production Migration
-- This migration adds Smart Configuration support to PostgreSQL production database

-- Add Smart Configuration columns to warehouse_template table
ALTER TABLE warehouse_template 
ADD COLUMN IF NOT EXISTS location_format_config TEXT;

ALTER TABLE warehouse_template 
ADD COLUMN IF NOT EXISTS format_confidence FLOAT;

ALTER TABLE warehouse_template 
ADD COLUMN IF NOT EXISTS format_examples TEXT;

ALTER TABLE warehouse_template 
ADD COLUMN IF NOT EXISTS format_learned_date TIMESTAMP;

-- Create location_format_history table for evolution tracking
CREATE TABLE IF NOT EXISTS location_format_history (
    id SERIAL PRIMARY KEY,
    warehouse_template_id INTEGER NOT NULL REFERENCES warehouse_template(id) ON DELETE CASCADE,
    original_format TEXT,
    new_format TEXT,
    detected_at TIMESTAMP DEFAULT NOW(),
    confidence_score FLOAT NOT NULL,
    user_confirmed BOOLEAN DEFAULT FALSE,
    applied BOOLEAN DEFAULT FALSE,
    reviewed_by INTEGER REFERENCES "user"(id) ON DELETE SET NULL,
    reviewed_at TIMESTAMP,
    sample_locations TEXT,
    trigger_report_id INTEGER REFERENCES analysis_report(id) ON DELETE SET NULL,
    pattern_change_type VARCHAR(50),
    affected_location_count INTEGER DEFAULT 0
);

-- Create indexes for performance
CREATE INDEX IF NOT EXISTS idx_format_history_template ON location_format_history(warehouse_template_id);
CREATE INDEX IF NOT EXISTS idx_format_history_date ON location_format_history(detected_at);
CREATE INDEX IF NOT EXISTS idx_format_history_pending ON location_format_history(user_confirmed, reviewed_at) WHERE reviewed_at IS NULL;
CREATE INDEX IF NOT EXISTS idx_format_history_change_type ON location_format_history(pattern_change_type);

-- Add comments for documentation
COMMENT ON COLUMN warehouse_template.location_format_config IS 'JSON configuration from SmartFormatDetector for location format parsing';
COMMENT ON COLUMN warehouse_template.format_confidence IS 'Detection confidence score (0.0-1.0) for the location format';
COMMENT ON COLUMN warehouse_template.format_examples IS 'JSON array of original user examples used for format detection';
COMMENT ON COLUMN warehouse_template.format_learned_date IS 'When the location format was detected/learned';

COMMENT ON TABLE location_format_history IS 'Tracks location format evolution and changes over time for Smart Configuration system';
COMMENT ON COLUMN location_format_history.pattern_change_type IS 'Type of change: new_pattern, format_drift, special_locations';
COMMENT ON COLUMN location_format_history.confidence_score IS 'Confidence score of the detected evolution (0.0-1.0)';
COMMENT ON COLUMN location_format_history.sample_locations IS 'JSON array of sample locations that triggered the evolution detection';

-- Update any existing templates to have default values
UPDATE warehouse_template 
SET format_confidence = 0.0, format_learned_date = created_at 
WHERE format_confidence IS NULL;

-- Grant permissions if needed (adjust role names as needed)
-- GRANT SELECT, INSERT, UPDATE, DELETE ON location_format_history TO your_app_user;
-- GRANT USAGE, SELECT ON SEQUENCE location_format_history_id_seq TO your_app_user;

-- Verify migration
SELECT 
    'Smart Configuration PostgreSQL migration completed' as status,
    COUNT(*) as existing_templates_updated
FROM warehouse_template 
WHERE format_confidence IS NOT NULL;