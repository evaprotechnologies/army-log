import datetime
import os
from typing import Any, Dict, List, Optional

from supabase import Client, create_client
from dotenv import load_dotenv

load_dotenv()

_client: Optional[Client] = None


def get_client() -> Client:
    """Returns a singleton Supabase client."""
    global _client
    if _client is None:
        url = os.environ.get("SUPABASE_URL")
        # Prefer service role when provided (bypasses RLS). Streamlit runs server-side, but
        # you must keep this key secret (env/secrets, never commit to git).
        service_role_key = os.environ.get("SUPABASE_SERVICE_ROLE_KEY")
        anon_key = os.environ.get("SUPABASE_ANON_KEY")
        key = service_role_key or anon_key

        if not url or not key:
            raise EnvironmentError(
                "Missing SUPABASE_URL or SUPABASE_ANON_KEY. "
                "Add them to your .env file or Streamlit Cloud secrets. "
                "Optionally set SUPABASE_SERVICE_ROLE_KEY to bypass RLS for writes."
            )
        _client = create_client(url, key)
    return _client


def insert_log(payload: Dict[str, Any]) -> Dict[str, Any]:
    """Insert a daily log row. Returns the inserted record."""
    client = get_client()
    response = client.table("daily_logs").insert(payload).execute()
    return response.data


def fetch_logs(limit: int = 90) -> List[Dict[str, Any]]:
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
        response = (
            client.table("daily_logs")
            .select("*")
            .order("created_at", desc=True)
            .limit(limit)
            .execute()
        )
    return response.data


def get_log_by_date(log_date: datetime.date) -> Optional[Dict[str, Any]]:
    """Return a single log for the given date, or None if not found."""
    client = get_client()
    iso_date = log_date.isoformat()
    response = (
        client.table("daily_logs")
        .select("*")
        .eq("log_date", iso_date)
        .limit(1)
        .execute()
    )
    data = response.data or []
    return data[0] if data else None


def upsert_log_fields(
    log_date: datetime.date,
    fields: Dict[str, Any],
) -> Dict[str, Any]:
    """UPSERT specific fields for the given log_date.

    If a row for `log_date` exists, only the provided fields are updated.
    If not, a new row is inserted with those fields plus log_date.
    """
    client = get_client()
    base: Dict[str, Any] = {
        "log_date": log_date.isoformat(),
        "last_updated_at": datetime.datetime.now(tz=datetime.timezone.utc).isoformat(),
    }
    base.update(fields)

    response = (
        client.table("daily_logs")
        .upsert(base, on_conflict="log_date")
        .execute()
    )
    data = response.data or []
    return data[0] if data else base
