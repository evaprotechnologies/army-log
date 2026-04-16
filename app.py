import streamlit as st
import os
import sys
from dotenv import load_dotenv

load_dotenv()

sys.path.append(os.path.dirname(__file__))

from utils.auth import ensure_authenticated  # noqa: E402

st.set_page_config(
    page_title="Army Log — Daily Ops",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Supabase Auth Gate ──────────────────────────────────────────────────────
ensure_authenticated()

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

