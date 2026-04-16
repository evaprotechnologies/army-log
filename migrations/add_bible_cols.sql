-- Army Log — Migration: Add Bible Reading Columns
-- Run this in the Supabase SQL Editor

ALTER TABLE daily_logs ADD COLUMN IF NOT EXISTS bible_reading TEXT;
ALTER TABLE daily_logs ADD COLUMN IF NOT EXISTS bible_completed BOOLEAN DEFAULT false;

-- Reload PostgREST schema cache
NOTIFY pgrst, 'reload schema';

-- Verify columns
SELECT column_name, data_type, is_nullable
FROM information_schema.columns
WHERE table_name = 'daily_logs' AND column_name IN ('bible_reading', 'bible_completed');
