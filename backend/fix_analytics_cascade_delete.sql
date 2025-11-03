-- Fix foreign key constraint to allow cascade delete
-- This allows anomalies to be deleted without violating the analytics_anomalies reference

-- Drop the existing constraint
ALTER TABLE analytics_anomalies
DROP CONSTRAINT IF EXISTS analytics_anomalies_anomaly_id_fkey;

-- Recreate it with CASCADE delete
ALTER TABLE analytics_anomalies
ADD CONSTRAINT analytics_anomalies_anomaly_id_fkey
FOREIGN KEY (anomaly_id)
REFERENCES anomaly(id)
ON DELETE CASCADE;

-- Verify the constraint was created
SELECT conname, conrelid::regclass AS table_name, confrelid::regclass AS referenced_table, confdeltype
FROM pg_constraint
WHERE conname = 'analytics_anomalies_anomaly_id_fkey';
