import streamlit as st
import datetime
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from utils.supabase_client import insert_log, fetch_logs

st.set_page_config(
    page_title="Log Today — Army Log",
    layout="centered",
)

# ── Styles (Future Tech Darkmode) ─────────────────────────────────────────────
st.markdown(
    """
    <style>
        /* Hide default Streamlit decoration */
        [data-testid="stDecoration"] { display: none; }
        
        /* Deep background gradient for the whole app */
        [data-testid="stAppViewContainer"] {
            background-color: #08080C;
            background-image: radial-gradient(circle at 50% 0%, #151522 0%, #08080C 60%);
        }

        /* Typography */
        .page-title {
            font-size: 2.2rem;
            font-weight: 900;
            background: linear-gradient(135deg, #00FF94, #00D4FF);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
            letter-spacing: 1.5px;
            text-transform: uppercase;
        }
        
        .page-subtitle {
            color: #6B7280; 
            font-size: 0.9rem;
            margin-top: -0.5rem;
            letter-spacing: 0.5px;
        }

        .section-label {
            font-size: 0.75rem;
            font-weight: 700;
            letter-spacing: 2px;
            color: #00D4FF;
            text-transform: uppercase;
            margin-bottom: -0.5rem;
            opacity: 0.9;
        }

        /* Form Container - Glassmorphism */
        div[data-testid="stForm"] {
            background: rgba(18, 18, 26, 0.4);
            border: 1px solid rgba(0, 212, 255, 0.15);
            border-radius: 16px;
            padding: 2rem;
            box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.3);
            backdrop-filter: blur(8px);
            -webkit-backdrop-filter: blur(8px);
        }

        /* Input Fields Normal State */
        div[data-baseweb="input"] > div, 
        div[data-baseweb="select"] > div, 
        div[data-baseweb="textarea"] > div {
            background-color: #0F0F16 !important;
            border: 1px solid #1E1E2E !important;
            border-radius: 8px !important;
            transition: all 0.3s ease;
        }

        /* Input Fields Focus State (Neon Glow) */
        div[data-baseweb="input"] > div:focus-within, 
        div[data-baseweb="select"] > div:focus-within, 
        div[data-baseweb="textarea"] > div:focus-within {
            border: 1px solid #00FF94 !important;
            box-shadow: 0 0 10px rgba(0, 255, 148, 0.2) !important;
            background-color: #12121A !important;
        }

        /* Text inside inputs */
        input, textarea, div[data-baseweb="select"] {
            color: #E2E8F0 !important;
        }

        /* Custom Dividers */
        hr {
            border-color: rgba(255, 255, 255, 0.05) !important;
            margin-top: 1.5rem !important;
            margin-bottom: 1.5rem !important;
        }

        /* Primary Submit Button styling */
        div[data-testid="stFormSubmitButton"] > button {
            background: linear-gradient(135deg, #00D4FF 0%, #00FF94 100%);
            color: #08080C !important;
            font-weight: 800 !important;
            letter-spacing: 1px;
            border: none !important;
            border-radius: 8px !important;
            transition: all 0.3s ease !important;
            text-transform: uppercase;
        }

        /* Button Hover State */
        div[data-testid="stFormSubmitButton"] > button:hover {
            box-shadow: 0 0 20px rgba(0, 255, 148, 0.4) !important;
            transform: translateY(-2px);
        }
        
        /* Adjust help text tooltips slightly */
        .stTooltipIcon {
            color: #00D4FF !important;
        }
    </style>
    """,
    unsafe_allow_html=True,
)

st.markdown('<div class="page-title">Daily Debrief</div>', unsafe_allow_html=True)
st.markdown(
    "<p class='page-subtitle'>9 PM CHECK-IN · REPORT FACTS ALONE.</p>",
    unsafe_allow_html=True,
)
st.write("") # Small spacer

# ── Check for duplicate log_date ──────────────────────────────────────────────
@st.cache_data(ttl=60)
def get_logged_dates():
    """Returns a set of dates already logged (as date objects)."""
    rows = fetch_logs(limit=365)
    dates = set()
    for r in rows:
        raw = r.get("log_date")
        if raw:
            try:
                dates.add(datetime.date.fromisoformat(str(raw)[:10]))
            except ValueError:
                pass
    return dates

# ── Form ──────────────────────────────────────────────────────────────────────
with st.form("daily_log_form", clear_on_submit=True):

    # --- Meta block ---
    st.markdown('<div class="section-label">Log Date</div>', unsafe_allow_html=True)
    log_date = st.date_input(
        "Which day are you reporting on?",
        value=datetime.date.today(),
        max_value=datetime.date.today(),
        label_visibility="collapsed",
    )

    st.divider()

    # --- 4 AM Prayer block ---
    st.markdown('<div class="section-label">4 AM Prayer Block</div>', unsafe_allow_html=True)
    prayer_status = st.selectbox(
        "Prayer Status",
        options=["Completed", "Missed"],
        index=0,
        help="Did you complete your 4 AM prayer session?",
    )

    st.divider()

    # --- 5:30 AM Skill block ---
    st.markdown('<div class="section-label">5:30 AM Skill Block</div>', unsafe_allow_html=True)
    skill_focus = st.text_input(
        "Skill / Concept Studied",
        placeholder="e.g. Supabase RLS, IT Audit Frameworks...",
        help="What specific skill or concept did you study this morning?",
    )

    st.divider()

    # --- Apollo Workload ---
    st.markdown('<div class="section-label">Apollo Backlog</div>', unsafe_allow_html=True)
    apollo_backlog = st.number_input(
        "Remaining tasks in your backlog today",
        min_value=0,
        max_value=999,
        step=1,
        value=0,
        help="How many tasks are still sitting in your backlog?",
    )

    st.divider()

    # --- Evapro Progress ---
    st.markdown('<div class="section-label">Evapro Progress</div>', unsafe_allow_html=True)
    evapro_progress = st.text_area(
        "Features built / progress made (Evapro-Kargo or Evapro-Flow)",
        placeholder="e.g. Implemented manifest builder fix. Pushed to GitHub.",
        height=120,
        help="Detail what you built, fixed, or shipped for Evapro today.",
    )

    st.divider()

    # --- Body & Energy ---
    st.markdown('<div class="section-label">Energy Level</div>', unsafe_allow_html=True)
    energy_level = st.slider(
        "How was your energy today? (1 = depleted, 10 = peak)",
        min_value=1,
        max_value=10,
        value=7,
        help="Track fatigue trends over time.",
    )

    st.divider()

    # --- Daily Win ---
    st.markdown('<div class="section-label">Daily Win</div>', unsafe_allow_html=True)
    daily_win = st.text_input(
        "Your #1 win for today",
        placeholder="e.g. Deployed army-log to Streamlit Cloud.",
        help="One clear, concrete victory — no matter how small.",
    )

    st.divider()

    # --- Bible Reading block ---
    st.markdown('<div class="section-label">📖 Bible Reading</div>', unsafe_allow_html=True)
    col_a, col_b = st.columns([2, 1])
    with col_a:
        bible_reading = st.text_input(
            "Current Chapters / Progress",
            placeholder="e.g. Genesis 1-5, Psalm 23",
            help="Which chapters did you read today?",
        )
    with col_b:
        st.write("") # Shim for alignment
        bible_completed = st.checkbox(
            "Plan Target Met?",
            value=False,
            help="Did you complete your assigned reading for today?",
        )

    st.divider()

    submitted = st.form_submit_button(
        "Transmit Report",
        use_container_width=True,
        type="primary",
    )

# ── Submission handler ────────────────────────────────────────────────────────
if submitted:
    # Basic validation
    errors = []
    if not skill_focus.strip():
        errors.append("Skill Focus cannot be empty.")
    if not daily_win.strip():
        errors.append("Daily Win cannot be empty.")

    # Duplicate date check
    logged_dates = get_logged_dates()
    if log_date in logged_dates:
        errors.append(
            f"A log for **{log_date.strftime('%A, %d %B %Y')}** already exists. "
            "Edit it directly in Supabase or choose a different date."
        )

    if errors:
        for err in errors:
            st.error(err)
    else:
        payload = {
            "log_date": log_date.isoformat(),
            "prayer_status": prayer_status,
            "skill_focus": skill_focus.strip(),
            "apollo_backlog": int(apollo_backlog),
            "evapro_progress": evapro_progress.strip(),
            "energy_level": int(energy_level),
            "daily_win": daily_win.strip(),
            "bible_reading": bible_reading.strip(),
            "bible_completed": bool(bible_completed),
        }

        try:
            with st.spinner("Encrypting and saving to Supabase..."):
                insert_log(payload)
            # Clear cache so dashboard reflects new entry immediately
            get_logged_dates.clear()
            st.success(
                f"Log for **{log_date.strftime('%A, %d %B %Y')}** secured. "
                "Soldier, carry on."
            )
            st.balloons()
        except Exception as e:
            st.error(f"Failed to save: {e}")
