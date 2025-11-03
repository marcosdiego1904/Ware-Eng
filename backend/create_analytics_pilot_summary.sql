-- Create analytics_pilot_summary table for immutable cumulative metrics
-- Purpose: Track lifetime pilot program metrics that never decrease (perfect for marketing)

-- Create table
CREATE TABLE IF NOT EXISTS analytics_pilot_summary (
    user_id INTEGER PRIMARY KEY REFERENCES "user"(id) ON DELETE CASCADE,
    total_anomalies_found INTEGER NOT NULL DEFAULT 0,
    total_anomalies_resolved INTEGER NOT NULL DEFAULT 0,
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP,
    last_file_upload_at TIMESTAMP WITH TIME ZONE
);

-- Add comment explaining purpose
COMMENT ON TABLE analytics_pilot_summary IS 'Immutable cumulative counters for pilot program - only increase, never decrease. Perfect for marketing ROI metrics.';

COMMENT ON COLUMN analytics_pilot_summary.total_anomalies_found IS 'Lifetime cumulative count of all anomalies detected. Never decreases even if reports are deleted.';

COMMENT ON COLUMN analytics_pilot_summary.total_anomalies_resolved IS 'Lifetime cumulative count of anomalies marked as resolved. Counts each unique anomaly resolution once.';

-- Initialize row for pilot1 with current counts from existing data
-- This ensures we don't lose historical data

-- First, get the pilot user ID
DO $$
DECLARE
    pilot_user_id INTEGER;
    current_anomalies_found INTEGER;
    current_anomalies_resolved INTEGER;
BEGIN
    -- Get pilot1 user ID
    SELECT id INTO pilot_user_id FROM "user" WHERE username = 'pilot1';

    IF pilot_user_id IS NOT NULL THEN
        -- Count current anomalies found (from analytics_anomalies table)
        SELECT COUNT(*) INTO current_anomalies_found
        FROM analytics_anomalies
        WHERE user_id = pilot_user_id;

        -- Count current resolved anomalies
        SELECT COUNT(*) INTO current_anomalies_resolved
        FROM analytics_anomalies
        WHERE user_id = pilot_user_id
        AND resolved_at IS NOT NULL;

        -- Insert initial row with current counts
        INSERT INTO analytics_pilot_summary (
            user_id,
            total_anomalies_found,
            total_anomalies_resolved,
            created_at,
            updated_at
        ) VALUES (
            pilot_user_id,
            COALESCE(current_anomalies_found, 0),
            COALESCE(current_anomalies_resolved, 0),
            CURRENT_TIMESTAMP,
            CURRENT_TIMESTAMP
        )
        ON CONFLICT (user_id) DO UPDATE SET
            total_anomalies_found = GREATEST(analytics_pilot_summary.total_anomalies_found, EXCLUDED.total_anomalies_found),
            total_anomalies_resolved = GREATEST(analytics_pilot_summary.total_anomalies_resolved, EXCLUDED.total_anomalies_resolved);

        RAISE NOTICE 'Initialized pilot summary for user_id % with % anomalies found, % resolved',
            pilot_user_id, current_anomalies_found, current_anomalies_resolved;
    ELSE
        RAISE NOTICE 'pilot1 user not found, skipping initialization';
    END IF;
END $$;

-- Create index for faster queries (though with one row per user, not critical)
CREATE INDEX IF NOT EXISTS idx_analytics_pilot_summary_updated
ON analytics_pilot_summary(updated_at DESC);

-- Verify the table was created
SELECT
    user_id,
    total_anomalies_found,
    total_anomalies_resolved,
    created_at,
    updated_at
FROM analytics_pilot_summary;
