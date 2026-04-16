# Army Log — Daily Ops Tracker

A personal discipline tracking app built with **Streamlit** + **Supabase**. Logs your 9 PM daily debrief and visualises trends over time.

## Features
- **Log Today** — Daily form covering prayer status, skill focus, Apollo backlog, Evapro progress, energy level, and daily win
- **Dashboard** — Energy trends, backlog charts, prayer streak donut, and a correlation scatter with trendline
- **Duplicate guard** — Prevents logging the same date twice
- **Manual log date** — Backfill missed days accurately

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
# → Open .env and paste your SUPABASE_URL and SUPABASE_ANON_KEY

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
| `log_date` | DATE | The day being reported (manual) |
| `prayer_status` | TEXT | "Completed" / "Missed" |
| `skill_focus` | TEXT | Morning study topic |
| `apollo_backlog` | INTEGER | Tasks remaining |
| `evapro_progress` | TEXT | Features built |
| `energy_level` | INTEGER | 1–10 self-rating |
| `daily_win` | TEXT | Primary victory |
