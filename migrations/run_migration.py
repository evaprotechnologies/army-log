"""
Army Log — Database Migration Script
=====================================
Adds the `log_date` DATE column to daily_logs and reloads
the Supabase PostgREST schema cache.

Usage:
    python migrations/run_migration.py

Requires DATABASE_URL in your .env file.
Get it from: Supabase Dashboard → Settings → Database → URI
"""

import os
import sys
from urllib.parse import urlparse, unquote

try:
    import psycopg2
except ImportError:
    print("❌ psycopg2 not installed. Run: pip install psycopg2-binary")
    sys.exit(1)

from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.environ.get("DATABASE_URL")

if not DATABASE_URL:
    print(
        "\n❌ DATABASE_URL not found in .env\n\n"
        "  1. Go to: Supabase Dashboard → Settings → Database\n"
        "  2. Scroll to 'Connection string' and select the URI tab\n"
        "  3. Copy the URI (it starts with postgresql://postgres:...)\n"
        "  4. Add it to your .env file as:\n"
        "     DATABASE_URL=postgresql://postgres:[YOUR-PASSWORD]@db.[ref].supabase.co:5432/postgres\n"
    )
    sys.exit(1)

# Strip surrounding brackets Supabase sometimes shows in their UI: [password]
DATABASE_URL = DATABASE_URL.strip()
# Remove square brackets from password section if user copied them literally
# e.g. postgresql://postgres:[abc123]@host → postgresql://postgres:abc123@host
import re
DATABASE_URL = re.sub(r'://([^:]+):\[([^\]]+)\]@', r'://\1:\2@', DATABASE_URL)

# Safely parse URL and decode each component to handle special chars in password
parsed = urlparse(DATABASE_URL)
db_params = {
    "host":     parsed.hostname,
    "port":     parsed.port or 5432,
    "dbname":   parsed.path.lstrip("/") or "postgres",
    "user":     unquote(parsed.username or "postgres"),
    "password": unquote(parsed.password or ""),
}

MIGRATIONS = [
    {
        "name": "Add log_date column",
        "check": "SELECT column_name FROM information_schema.columns WHERE table_name='daily_logs' AND column_name='log_date';",
        "sql": "ALTER TABLE daily_logs ADD COLUMN log_date DATE NOT NULL DEFAULT CURRENT_DATE;",
    },
    {
        "name": "Add unique constraint on log_date",
        "check": "SELECT constraint_name FROM information_schema.table_constraints WHERE table_name='daily_logs' AND constraint_name='daily_logs_log_date_unique';",
        "sql": "ALTER TABLE daily_logs ADD CONSTRAINT daily_logs_log_date_unique UNIQUE (log_date);",
    },
    {
        "name": "Reload PostgREST schema cache",
        "check": None,  # always run
        "sql": "NOTIFY pgrst, 'reload schema';",
    },
]


def run():
    print("\nArmy Log — Running migrations...\n")

    try:
        conn = psycopg2.connect(**db_params)
        conn.autocommit = True
        cursor = conn.cursor()
        print("Connected to Supabase Postgres\n")
    except Exception as e:
        print(f"Connection failed: {e}")
        sys.exit(1)

    for step in MIGRATIONS:
        name = step["name"]
        already_done = False

        # Check if migration already applied
        if step["check"]:
            cursor.execute(step["check"])
            result = cursor.fetchone()
            if result:
                print(f"  Skipped  : {name} (already applied)")
                already_done = True

        if not already_done:
            try:
                cursor.execute(step["sql"])
                print(f"  Applied  : {name}")
            except Exception as e:
                print(f"  Failed   : {name}\n     Error: {e}")
                cursor.close()
                conn.close()
                sys.exit(1)

    cursor.close()
    conn.close()

    print("\nAll migrations complete. Supabase is ready.\n")
    print("   Now run:  streamlit run app.py\n")


if __name__ == "__main__":
    run()
