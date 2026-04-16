-- Army Log — Migration: Add log_date column
-- Run with: psql -h db.bujyipyjrtjhdobxvgqh.supabase.co -p 5432 -d postgres -U postgres -f migrations/migrate.sql

-- Step 1: Add log_date column (safe — skips if already exists)
DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns
        WHERE table_name = 'daily_logs' AND column_name = 'log_date'
    ) THEN
        ALTER TABLE daily_logs ADD COLUMN log_date DATE NOT NULL DEFAULT CURRENT_DATE;
        RAISE NOTICE 'log_date column added.';
    ELSE
        RAISE NOTICE 'log_date column already exists — skipped.';
    END IF;
END $$;

-- Step 2: Add unique constraint (safe — skips if already exists)
DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.table_constraints
        WHERE table_name = 'daily_logs'
        AND constraint_name = 'daily_logs_log_date_unique'
    ) THEN
        ALTER TABLE daily_logs ADD CONSTRAINT daily_logs_log_date_unique UNIQUE (log_date);
        RAISE NOTICE 'Unique constraint added.';
    ELSE
        RAISE NOTICE 'Unique constraint already exists — skipped.';
    END IF;
END $$;

-- Step 3: Reload PostgREST schema cache
NOTIFY pgrst, 'reload schema';

-- Confirm final schema
SELECT column_name, data_type, is_nullable
FROM information_schema.columns
WHERE table_name = 'daily_logs'
ORDER BY ordinal_position;
