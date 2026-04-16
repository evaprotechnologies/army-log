import datetime
import os
import sys
from typing import Any, Dict, List

import streamlit as st

sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from utils.auth import ensure_authenticated, get_session_tokens  # noqa: E402
from utils.supabase_client import get_log_by_date, upsert_log_fields  # noqa: E402

st.set_page_config(
    page_title="Log Today — Army Log",
    layout="centered",
)

# ── Supabase Auth Gate ─────────────────────────────────────────────────────
ensure_authenticated()

# ── Styles (Future Tech Darkmode) ─────────────────────────────────────────────
st.markdown(
    """
    <style>
        [data-testid="stDecoration"] { display: none; }

        [data-testid="stAppViewContainer"] {
            background-color: #08080C;
            background-image: radial-gradient(circle at 50% 0%, #151522 0%, #08080C 60%);
        }

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

        hr {
            border-color: rgba(255, 255, 255, 0.05) !important;
            margin-top: 1.5rem !important;
            margin-bottom: 1.5rem !important;
        }
    </style>
    """,
    unsafe_allow_html=True,
)


def _init_session_state(today: datetime.date) -> None:
    if "log_date" not in st.session_state:
        st.session_state["log_date"] = today

    if "current_log" not in st.session_state:
        st.session_state["current_log"] = {}

    if "last_saved_at" not in st.session_state:
        st.session_state["last_saved_at"] = None

    if "tasks_list" not in st.session_state:
        st.session_state["tasks_list"] = []


def _load_log_into_state(log_date: datetime.date) -> None:
    access_token, refresh_token = get_session_tokens()
    log = (
        get_log_by_date(
            log_date,
            access_token=access_token,
            refresh_token=refresh_token,
        )
        or {}
    )
    st.session_state["current_log"] = log

    st.session_state["prayer_status"] = log.get("prayer_status", "Completed")
    st.session_state["prayer_notes"] = log.get("prayer_notes", "")
    st.session_state["skill_focus"] = log.get("skill_focus", "")
    st.session_state["apollo_tasks"] = ""
    st.session_state["apollo_backlog"] = int(log.get("apollo_backlog") or 0)
    st.session_state["evapro_progress"] = log.get("evapro_progress", "")
    st.session_state["energy_level"] = int(log.get("energy_level") or 7)
    st.session_state["daily_win"] = log.get("daily_win", "")
    st.session_state["bible_reading"] = log.get("bible_reading", "")
    st.session_state["bible_completed"] = bool(log.get("bible_completed") or False)

    existing_tasks = log.get("tasks") or []
    if isinstance(existing_tasks, list):
        st.session_state["tasks_list"] = existing_tasks
    else:
        st.session_state["tasks_list"] = []


def _save_fields(fields: Dict[str, Any]) -> None:
    log_date: datetime.date = st.session_state["log_date"]
    try:
        access_token, refresh_token = get_session_tokens()
        upsert_log_fields(
            log_date,
            fields,
            access_token=access_token,
            refresh_token=refresh_token,
        )
        st.session_state["last_saved_at"] = datetime.datetime.now()
    except Exception as exc:
        msg = str(exc)
        # Common Supabase write-block when RLS policies don't allow INSERT/UPDATE for the key in use.
        if "row-level security" in msg.lower() or "rls" in msg.lower() or "42501" in msg:
            st.error(
                "Supabase blocked this autosave due to Row Level Security (RLS).\n"
                "Fix by either:\n"
                "1) Add/adjust RLS policies for `daily_logs` to allow INSERT/UPDATE, OR\n"
                "2) Set `SUPABASE_SERVICE_ROLE_KEY` (server-side only) to bypass RLS for writes."
            )
        else:
            st.error(f"Failed to autosave: {exc}")


def _field_changed(field_name: str) -> None:
    value = st.session_state.get(field_name)
    _save_fields({field_name: value})


def _tasks_changed() -> None:
    tasks: List[Dict[str, Any]] = st.session_state.get("tasks_list", [])
    _save_fields({"tasks": tasks, "apollo_backlog": len(tasks)})


def _add_task() -> None:
    text = st.session_state.get("new_task_text", "").strip()
    if not text:
        return

    tasks: List[Dict[str, Any]] = st.session_state.get("tasks_list", [])
    next_id = (max((t.get("id", 0) for t in tasks), default=0) or 0) + 1
    tasks.append({"id": next_id, "text": text, "done": False})
    st.session_state["tasks_list"] = tasks
    st.session_state["new_task_text"] = ""
    _tasks_changed()


def _toggle_task(task_index: int) -> None:
    tasks: List[Dict[str, Any]] = st.session_state.get("tasks_list", [])
    if 0 <= task_index < len(tasks):
        tasks[task_index]["done"] = not bool(tasks[task_index].get("done"))
        st.session_state["tasks_list"] = tasks
        _tasks_changed()


today = datetime.date.today()
_init_session_state(today)

if st.session_state.get("log_date") != today:
    st.session_state["log_date"] = today

_load_log_into_state(today)

st.markdown('<div class="page-title">Daily Command Log</div>', unsafe_allow_html=True)
st.markdown(
    "<p class='page-subtitle'>Progressive saves all day · Facts only.</p>",
    unsafe_allow_html=True,
)
st.write("")

log_date = st.session_state["log_date"]
st.markdown(
    f"**Log Date:** {log_date.strftime('%A, %d %B %Y')} &nbsp;&nbsp;|&nbsp;&nbsp; "
    f"{'Autosave active' if st.session_state.get('last_saved_at') else 'Waiting for first input...'}",
)

if st.session_state.get("last_saved_at"):
    ts = st.session_state["last_saved_at"].strftime("%H:%M")
    st.caption(f"Last saved at {ts}")

st.divider()

st.markdown('<div class="section-label">4 AM Prayer Block</div>', unsafe_allow_html=True)
col_prayer, col_notes = st.columns([1, 2])
with col_prayer:
    st.selectbox(
        "Prayer Status",
        options=["Completed", "Missed"],
        key="prayer_status",
        help="Did you complete your 4 AM prayer session?",
        on_change=_field_changed,
        args=("prayer_status",),
    )
with col_notes:
    st.text_area(
        "Prayer Notes (4:30 AM)",
        key="prayer_notes",
        height=80,
        placeholder="Key scriptures, impressions, or instructions.",
        on_change=_field_changed,
        args=("prayer_notes",),
    )

st.divider()

st.markdown('<div class="section-label">5:30 AM Skill Block</div>', unsafe_allow_html=True)
st.text_input(
    "Skill / Concept Studied",
    key="skill_focus",
    placeholder="e.g. Supabase RLS, IT Audit Frameworks...",
    help="What specific skill or concept did you study this morning?",
    on_change=_field_changed,
    args=("skill_focus",),
)

st.divider()

st.markdown('<div class="section-label">Apollo Task Stack</div>', unsafe_allow_html=True)
st.text_input(
    "Add task and hit Enter",
    key="new_task_text",
    placeholder="e.g. Fix Kargo UI bug...",
    on_change=_add_task,
)

tasks: List[Dict[str, Any]] = st.session_state.get("tasks_list", [])
if tasks:
    for idx, task in enumerate(tasks):
        checked = task.get("done", False)
        label = task.get("text", "")
        st.checkbox(
            label,
            key=f"task_{task.get('id', idx)}",
            value=checked,
            on_change=_toggle_task,
            args=(idx,),
        )

st.number_input(
    "Remaining tasks in backlog",
    min_value=0,
    max_value=999,
    step=1,
    key="apollo_backlog",
    help="How many tasks are still sitting in your backlog?",
    on_change=_field_changed,
    args=("apollo_backlog",),
)

st.divider()

st.markdown('<div class="section-label">Evapro Progress</div>', unsafe_allow_html=True)
st.text_area(
    "Features built / progress made (Evapro-Kargo or Evapro-Flow)",
    key="evapro_progress",
    placeholder="e.g. Implemented manifest builder fix. Pushed to GitHub.",
    height=120,
    help="Detail what you built, fixed, or shipped for Evapro today.",
    on_change=_field_changed,
    args=("evapro_progress",),
)

st.divider()

st.markdown('<div class="section-label">Energy Level</div>', unsafe_allow_html=True)
st.slider(
    "How was your energy today? (1 = depleted, 10 = peak)",
    min_value=1,
    max_value=10,
    key="energy_level",
    help="Track fatigue trends over time.",
    on_change=_field_changed,
    args=("energy_level",),
)

st.divider()

st.markdown('<div class="section-label">Daily Win</div>', unsafe_allow_html=True)
st.text_input(
    "Your #1 win for today",
    key="daily_win",
    placeholder="e.g. Deployed army-log to Streamlit Cloud.",
    help="One clear, concrete victory — no matter how small.",
    on_change=_field_changed,
    args=("daily_win",),
)

st.divider()

st.markdown('<div class="section-label">📖 Bible Reading</div>', unsafe_allow_html=True)
col_a, col_b = st.columns([2, 1])
with col_a:
    st.text_input(
        "Current Chapters / Progress",
        key="bible_reading",
        placeholder="e.g. Genesis 1-5, Psalm 23",
        help="Which chapters did you read today?",
        on_change=_field_changed,
        args=("bible_reading",),
    )
with col_b:
    st.write("")
    st.checkbox(
        "Plan Target Met?",
        key="bible_completed",
        help="Did you complete your assigned reading for today?",
        on_change=_field_changed,
        args=("bible_completed",),
    )
