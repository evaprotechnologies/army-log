import os
from supabase import create_client, Client
from dotenv import load_dotenv

load_dotenv()

_client: Client | None = None


def get_client() -> Client:
    """Returns a singleton Supabase client."""
    global _client
    if _client is None:
        url = os.environ.get("SUPABASE_URL")
        key = os.environ.get("SUPABASE_ANON_KEY")
        if not url or not key:
            raise EnvironmentError(
                "Missing SUPABASE_URL or SUPABASE_ANON_KEY. "
                "Add them to your .env file or Streamlit Cloud secrets."
            )
        _client = create_client(url, key)
    return _client


def insert_log(payload: dict) -> dict:
    """Insert a daily log row. Returns the inserted record."""
    client = get_client()
    response = client.table("daily_logs").insert(payload).execute()
    return response.data


def fetch_logs(limit: int = 90) -> list[dict]:
    """Fetch the most recent `limit` log records, ordered by log_date descending.

    Falls back to ordering by created_at if log_date column does not yet exist.
    """
    client = get_client()
    try:
        response = (
            client.table("daily_logs")
            .select("*")
            .order("log_date", desc=True)
            .limit(limit)
            .execute()
        )
    except Exception:
        # Fallback: log_date column may not exist yet — order by created_at
        response = (
            client.table("daily_logs")
            .select("*")
            .order("created_at", desc=True)
            .limit(limit)
            .execute()
        )
    return response.data
