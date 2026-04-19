# Army Log — Living Command Center

A personal discipline tracking app built with **Streamlit** + **Supabase**. Instead of a single end-of-day submission, it progressively saves your inputs through the day and visualises trends over time.

## Features
- **Progressive autosave** — every field upserts to Supabase as you edit (no `st.form` submit step)
- **Supabase Auth login** — sign in with a **pre-provisioned** Supabase user (the app does not offer public sign-up)
- **4 AM Prayer Block** — prayer status + `prayer_notes`
- **Skill Focus** — autosaved on change
- **Apollo Task Stack** — `tasks` stored as JSONB; add/tick tasks updates `apollo_backlog`
- **Evapro Progress + Energy + Daily Win** — autosaved on change
- **Dashboard updates** — includes last progressive save time + task completion stats

## Security Notice
Do not commit `.env`. If it was ever pushed (even once), rotate your Supabase keys immediately (at least `SUPABASE_ANON_KEY` and any service keys).

For account creation, use **Supabase Dashboard → Authentication → Users** (admin-provisioned users only). In Supabase, also disable **public email sign-ups** so accounts cannot be created outside your controlled flow.

## Tech Stack
| Layer | Tool |
|---|---|
| Frontend | Streamlit |
| Database | Supabase (PostgreSQL) |
| Charts | Plotly Express |
| Language | Python 3.11+ |

## Local Setup

```bash
# 1. Clone the repo
git clone https://github.com/evaprotechnologies/army-log.git
cd army-log

# 2. Install dependencies
pip install -r requirements.txt

# 3. Add your secrets
cp .env.example .env
# → Open `.env` and paste:
#   - `SUPABASE_URL`
#   - `SUPABASE_ANON_KEY`
#   - Ensure your Supabase RLS allows `SELECT/INSERT/UPDATE` for the logged-in user.

# 4. Run
streamlit run app.py
```

## Streamlit Cloud Deployment

1. Push this repo to GitHub
2. Go to [share.streamlit.io](https://share.streamlit.io) → New App → select this repo
3. Add secrets under **App Settings → Secrets**:
   ```toml
   SUPABASE_URL = "https://your-project-ref.supabase.co"
   SUPABASE_ANON_KEY = "your-anon-key"
   ```
4. Deploy

## Database Schema (`daily_logs`)

| Column | Type | Purpose |
|---|---|---|
| `id` | UUID | Primary key |
| `created_at` | TIMESTAMPTZ | Auto-set insert timestamp |
| `log_date` | DATE | The day being reported (one row per day) |
| `prayer_status` | TEXT | "Completed" / "Missed" |
| `prayer_notes` | TEXT | Notes for the 4:30 AM block |
| `bible_reading` | TEXT | Chapters read (e.g. "Genesis 1-3") |
| `bible_completed` | BOOLEAN | Met the day's plan target |
| `skill_focus` | TEXT | Morning study topic |
| `apollo_backlog` | INTEGER | Tasks remaining (derived from `tasks` length) |
| `tasks` | JSONB | Apollo tasks array (e.g. `[{"id":1,"text":"...","done":false}]`) |
| `evapro_progress` | TEXT | Features built |
| `energy_level` | INTEGER | 1–10 self-rating |
| `daily_win` | TEXT | Primary victory |
| `last_updated_at` | TIMESTAMPTZ | Timestamp of the latest progressive autosave (UTC default) |

## Database Migration (Supabase SQL Editor)

Run this once to support progressive logging (unique per-day row + new columns).

```sql
-- 1) Enforce 1 log row per day (required for upsert on log_date)
DO $$
BEGIN
  IF NOT EXISTS (
    SELECT 1
    FROM information_schema.table_constraints
    WHERE table_name='daily_logs'
      AND constraint_type='UNIQUE'
      AND constraint_name='unique_log_date'
  ) THEN
    ALTER TABLE daily_logs ADD CONSTRAINT unique_log_date UNIQUE (log_date);
  END IF;
END $$;

-- 2) Progressive fields
ALTER TABLE daily_logs
  ADD COLUMN IF NOT EXISTS prayer_notes TEXT,
  ADD COLUMN IF NOT EXISTS tasks JSONB DEFAULT '[]'::jsonb,
  ADD COLUMN IF NOT EXISTS last_updated_at TIMESTAMPTZ DEFAULT timezone('utc'::text, now());
```

## Notes on RLS (autosave permissions)

- Autosave and reads now run as the logged-in Supabase user (using their JWT), so `daily_logs` must allow `SELECT`, `INSERT`, and `UPDATE` for whatever RLS policies you enable.
