import streamlit as st
import os
from dotenv import load_dotenv

load_dotenv()

st.set_page_config(
    page_title="Army Log — Daily Ops",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Security Layer ────────────────────────────────────────────────────────────
def check_password():
    """Returns True if the user had the correct password."""

    def password_entered():
        """Checks whether a password entered by the user is correct."""
        # 1. Try Streamlit Secrets
        try:
            target_password = st.secrets.get("APP_PASSWORD")
        except Exception:
            target_password = None

        # 2. Fallback to Environment Variable or Default
        if not target_password:
            target_password = os.environ.get("APP_PASSWORD", "army-log-default")

        if st.session_state["password"].strip() == str(target_password).strip():
            st.session_state["password_correct"] = True
            del st.session_state["password"]  # don't store password
        else:
            st.session_state["password_correct"] = False

    if "password_correct" not in st.session_state:
        # First run, show input for password.
        st.markdown(
            """
            <div style='text-align:center; padding: 2rem;'>
                <h1 style='color:#00FF94; letter-spacing:3px;'>SECURE ACCESS REQUIRED</h1>
                <p style='color:#666;'>Enter your Command Entry Password to proceed.</p>
            </div>
            """,
            unsafe_allow_html=True
        )
        st.text_input(
            "Command Password", type="password", on_change=password_entered, key="password"
        )
        return False
    elif not st.session_state["password_correct"]:
        # Password incorrect, show input + error.
        st.text_input(
            "Command Password", type="password", on_change=password_entered, key="password"
        )
        st.error("❌ Access Denied: Invalid Credentials")
        return False
    else:
        # Password correct.
        return True

if not check_password():
    st.stop()

# ── Sidebar brand ────────────────────────────────────────────────────────────
st.sidebar.markdown(
    """
    <div style='text-align:center; padding: 1rem 0 0.5rem 0;'>
        <span style='font-size:1.3rem; font-weight:800; letter-spacing:2px;
                     color:#00FF94;'>ARMY LOG</span><br/>
        <span style='font-size:0.75rem; color:#666; letter-spacing:1px;'>
            DAILY OPS TRACKER
        </span>
    </div>
    <hr style='border-color:#1e1e2e; margin:0.5rem 0;'/>
    """,
    unsafe_allow_html=True,
)

# ── Home page content ─────────────────────────────────────────────────────────
st.markdown(
    """
    <style>
        /* Hide default streamlit header decoration */
        [data-testid="stDecoration"] { display: none; }

        .hero-title {
            font-size: 3rem;
            font-weight: 900;
            letter-spacing: 3px;
            background: linear-gradient(135deg, #00FF94 0%, #00D4FF 100%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
        }
        .hero-sub {
            font-size: 1.1rem;
            color: #888;
            margin-top: -0.5rem;
            letter-spacing: 1px;
        }
        .card {
            background: #12121A;
            border: 1px solid #1e1e2e;
            border-radius: 12px;
            padding: 1.5rem;
            margin-bottom: 1rem;
        }
        .card h3 { color: #00FF94; margin-bottom: 0.25rem; }
        .card p  { color: #999; font-size: 0.9rem; }
    </style>

    <div class="hero-title">ARMY LOG</div>
    <div class="hero-sub">YOUR DAILY DISCIPLINE COMMAND CENTER</div>
    <br/>
    """,
    unsafe_allow_html=True,
)

col1, col2 = st.columns(2)

with col1:
    st.markdown(
        """
        <div class="card">
            <h3>Log Today</h3>
            <p>Fill in your daily 9 PM debrief — prayer, skill focus,
            backlog, Evapro progress, energy level, and your win of the day.</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

with col2:
    st.markdown(
        """
        <div class="card">
            <h3>Dashboard</h3>
            <p>Track trends over time — energy levels, backlog counts,
            prayer streaks, and a full searchable history of your logs.</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

st.markdown(
    """
    <br/>
    <div style='color:#444; font-size:0.8rem; text-align:center;'>
        Use the sidebar to navigate · Built for Apollo · Powered by Supabase
    </div>
    """,
    unsafe_allow_html=True,
)

