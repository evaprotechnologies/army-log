import streamlit as st
from supabase import create_client
from dotenv import load_dotenv
import os
from typing import Optional, Tuple

load_dotenv()


def _require_env(name: str) -> str:
    value = os.environ.get(name)
    if not value:
        raise EnvironmentError(f"Missing required env var `{name}`.")
    return value


def _auth_client():
    url = _require_env("SUPABASE_URL")
    anon_key = _require_env("SUPABASE_ANON_KEY")
    return create_client(url, anon_key)


def login(email: str, password: str) -> Tuple[bool, Optional[str]]:
    """Signs the user in via Supabase Auth (email/password)."""
    client = _auth_client()

    try:
        res = client.auth.sign_in_with_password(
            {"email": email, "password": password}
        )
    except Exception as exc:  # Supabase Auth errors (invalid creds, unconfirmed email, etc.)
        return False, str(exc)
    # supabase-py may return either a response object or dict-like response.
    session = getattr(res, "session", None) or (res.get("session") if hasattr(res, "get") else None)
    user = getattr(res, "user", None) or (res.get("user") if hasattr(res, "get") else None)

    if not session or not getattr(session, "access_token", None) and not (
        isinstance(session, dict) and session.get("access_token")
    ):
        # Try to extract error if present.
        error_msg = None
        if hasattr(res, "error") and getattr(res, "error"):
            error_msg = str(getattr(res, "error"))
        elif hasattr(res, "get"):
            error_msg = res.get("message") or res.get("error_description") or res.get("error")
        return False, error_msg or "Login failed."

    access_token = getattr(session, "access_token", None) or session["access_token"]
    refresh_token = getattr(session, "refresh_token", None) or session["refresh_token"]

    st.session_state["supabase_access_token"] = access_token
    st.session_state["supabase_refresh_token"] = refresh_token

    st.session_state["supabase_user_id"] = getattr(user, "id", None) or (
        user.get("id") if isinstance(user, dict) else None
    )
    st.session_state["supabase_user_email"] = getattr(user, "email", None) or (
        user.get("email") if isinstance(user, dict) else email
    )
    return True, None


def logout() -> None:
    st.session_state.pop("supabase_access_token", None)
    st.session_state.pop("supabase_refresh_token", None)
    st.session_state.pop("supabase_user_id", None)
    st.session_state.pop("supabase_user_email", None)


def get_session_tokens() -> Tuple[Optional[str], Optional[str]]:
    return (
        st.session_state.get("supabase_access_token"),
        st.session_state.get("supabase_refresh_token"),
    )


def ensure_authenticated() -> None:
    """Blocks the page until the user is logged into Supabase Auth."""
    if st.session_state.get("supabase_access_token") and st.session_state.get(
        "supabase_refresh_token"
    ):
        with st.sidebar:
            st.markdown("### Session")
            st.caption(f"Signed in as: {st.session_state.get('supabase_user_email')}")
            if st.button("Logout"):
                logout()
                st.rerun()
        return

    st.markdown(
        """
        <div style='text-align:center; padding: 2rem;'>
            <h1 style='color:#00FF94; letter-spacing:3px;'>SIGN IN REQUIRED</h1>
            <p style='color:#666;'>Log in using your Supabase account.</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    with st.form("supabase_login_form", clear_on_submit=False):
        email = st.text_input("Email")
        password = st.text_input("Password", type="password")

        submitted = st.form_submit_button("Sign in")

        if submitted:
            if not email.strip() or not password:
                st.error("Email and password are required.")
            else:
                ok, err = login(email.strip(), password)
                if ok:
                    st.success("Signed in.")
                    st.rerun()
                else:
                    st.error(f"Login failed: {err or 'Unknown error'}")

    st.stop()

