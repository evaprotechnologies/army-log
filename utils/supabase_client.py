import datetime
import os
from typing import Any, Dict, List, Optional

from dotenv import load_dotenv
from supabase import Client, create_client

load_dotenv()


def _require_env(name: str) -> str:
    value = os.environ.get(name)
    if not value:
        raise EnvironmentError(f"Missing required env var `{name}`.")
    return value


def get_client(
    *,
    access_token: Optional[str] = None,
    refresh_token: Optional[str] = None,
) -> Client:
    """Create a Supabase client using the anon key.

    If `access_token` + `refresh_token` are provided, the client is bound to that user session
    (so RLS policies can evaluate as that user).
    """
    url = _require_env("SUPABASE_URL")
    anon_key = _require_env("SUPABASE_ANON_KEY")

    client = create_client(url, anon_key)

    if access_token:
        if not refresh_token:
            raise EnvironmentError(
                "refresh_token is required when access_token is provided."
            )
        # Attach JWT to the client so table operations are performed as the logged-in user.
        client.auth.set_session(access_token, refresh_token)

    return client


def insert_log(
    payload: Dict[str, Any],
    *,
    access_token: Optional[str] = None,
    refresh_token: Optional[str] = None,
) -> Dict[str, Any]:
    """Insert a daily log row. Returns the inserted record."""
    client = get_client(access_token=access_token, refresh_token=refresh_token)
    response = client.table("daily_logs").insert(payload).execute()
    return response.data


def fetch_logs(
    limit: int = 90,
    *,
    access_token: Optional[str] = None,
    refresh_token: Optional[str] = None,
) -> List[Dict[str, Any]]:
    """Fetch the most recent `limit` log records, ordered by log_date descending.

    Falls back to ordering by created_at if log_date column does not yet exist.
    """
    client = get_client(access_token=access_token, refresh_token=refresh_token)
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


def get_log_by_date(
    log_date: datetime.date,
    *,
    access_token: Optional[str] = None,
    refresh_token: Optional[str] = None,
) -> Optional[Dict[str, Any]]:
    """Return a single log for the given date, or None if not found."""
    client = get_client(access_token=access_token, refresh_token=refresh_token)
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
    *,
    access_token: Optional[str] = None,
    refresh_token: Optional[str] = None,
) -> Dict[str, Any]:
    """UPSERT specific fields for the given log_date.

    If a row for `log_date` exists, only the provided fields are updated.
    If not, a new row is inserted with those fields plus log_date.
    """
    client = get_client(access_token=access_token, refresh_token=refresh_token)
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
