import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import datetime
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from utils.auth import ensure_authenticated, get_session_tokens  # noqa: E402
from utils.supabase_client import fetch_logs

st.set_page_config(
    page_title="Dashboard — Army Log",
    layout="wide",
)

# ── Supabase Auth Gate ─────────────────────────────────────────────────────
ensure_authenticated()

# ── Styles ────────────────────────────────────────────────────────────────────
st.markdown(
    """
    <style>
        [data-testid="stDecoration"] { display: none; }
        .page-title {
            font-size: 2rem;
            font-weight: 800;
            background: linear-gradient(135deg, #00FF94, #00D4FF);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
            letter-spacing: 2px;
        }
        .metric-card {
            background: #12121A;
            border: 1px solid #1e1e2e;
            border-radius: 12px;
            padding: 1.2rem 1rem;
            text-align: center;
        }
        .metric-val {
            font-size: 2.2rem;
            font-weight: 900;
            color: #00FF94;
        }
        .metric-lbl {
            font-size: 0.75rem;
            color: #666;
            letter-spacing: 1.5px;
            text-transform: uppercase;
        }
    </style>
    """,
    unsafe_allow_html=True,
)

st.markdown('<div class="page-title">Operations Dashboard</div>', unsafe_allow_html=True)
st.markdown(
    "<p style='color:#666; margin-top:-0.25rem;'>Your last 90 days at a glance.</p>",
    unsafe_allow_html=True,
)
st.divider()

# ── Data load ─────────────────────────────────────────────────────────────────
def load_data():
    access_token, refresh_token = get_session_tokens()
    rows = fetch_logs(
        limit=90, access_token=access_token, refresh_token=refresh_token
    )
    if not rows:
        return pd.DataFrame()
    df = pd.DataFrame(rows)
    df["log_date"] = pd.to_datetime(df["log_date"])

    if "last_updated_at" in df.columns:
        df["last_updated_at"] = pd.to_datetime(df["last_updated_at"], errors="coerce")

    # Derive task-level stats from JSONB `tasks` if present
    if "tasks" in df.columns:
        def _task_counts(tasks):
            try:
                if not isinstance(tasks, list):
                    return 0, 0
                total = len(tasks)
                done = sum(1 for t in tasks if t.get("done"))
                return total, done
            except Exception:
                return 0, 0

        totals, dones = zip(*df["tasks"].map(_task_counts)) if len(df) else ([], [])
        df["tasks_total"] = totals if len(df) else 0
        df["tasks_done"] = dones if len(df) else 0

    df = df.sort_values("log_date")
    return df


with st.spinner("Loading your logs..."):
    df = load_data()

if df.empty:
    st.info("No logs found yet. Submit your first daily log to get started!")
    st.stop()

# ── KPI Cards ─────────────────────────────────────────────────────────────────
total_logs = len(df)
prayer_rate = (
    (df["prayer_status"] == "Completed").sum() / total_logs * 100
    if total_logs and "prayer_status" in df.columns else 0
)
bible_rate = (
    (df["bible_completed"] == True).sum() / total_logs * 100  # noqa: E712
    if total_logs and "bible_completed" in df.columns else 0
)
avg_energy = df["energy_level"].mean() if "energy_level" in df.columns else 0

avg_backlog = df["apollo_backlog"].mean() if "apollo_backlog" in df.columns else 0

task_completion = 0
if "tasks_total" in df.columns and "tasks_done" in df.columns:
    total_tasks = df["tasks_total"].sum()
    done_tasks = df["tasks_done"].sum()
    task_completion = (done_tasks / total_tasks * 100) if total_tasks else 0

last_updated_str = "N/A"
if "last_updated_at" in df.columns and df["last_updated_at"].notna().any():
    last_ts = df["last_updated_at"].max()
    last_updated_str = last_ts.strftime("%d %b %Y · %H:%M") if not pd.isna(last_ts) else "N/A"

c1, c2, c3, c4 = st.columns(4)


def kpi(col, value, label):
    col.markdown(
        f"""
        <div class="metric-card">
            <div class="metric-val">{value}</div>
            <div class="metric-lbl">{label}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


kpi(c1, f"{prayer_rate:.0f}%", "Prayer Rate")
kpi(c2, f"{bible_rate:.0f}%", "Bible Plan Rate")
kpi(c3, f"{avg_energy:.1f}/10", "Avg Energy")
kpi(c4, f"{task_completion:.0f}%", "Tasks Done")

st.caption(f"Last progressive update: {last_updated_str} · Avg backlog: {avg_backlog:.1f} tasks")

st.divider()

# ── Charts Row 1 ──────────────────────────────────────────────────────────────
col_left, col_right = st.columns(2)

with col_left:
    st.markdown("#### Energy Over Time")
    fig_energy = px.area(
        df,
        x="log_date",
        y="energy_level",
        color_discrete_sequence=["#00FF94"],
        template="plotly_dark",
    )
    fig_energy.update_traces(fill="tozeroy", line_width=2)
    fig_energy.update_layout(
        paper_bgcolor="#0A0A0F",
        plot_bgcolor="#0A0A0F",
        yaxis=dict(range=[0, 10], gridcolor="#1e1e2e"),
        xaxis=dict(gridcolor="#1e1e2e"),
        margin=dict(l=0, r=0, t=10, b=0),
    )
    st.plotly_chart(fig_energy, use_container_width=True)

with col_right:
    st.markdown("#### Bible Reading Consistency")
    if "bible_completed" in df.columns:
        # Create a consistency bar chart (1 for met, 0 for not)
        df["bible_numeric"] = df["bible_completed"].astype(int)
        fig_bible = px.bar(
            df,
            x="log_date",
            y="bible_numeric",
            color="bible_completed",
            color_discrete_map={True: "#00FF94", False: "#FF4B4B"},
            template="plotly_dark",
        )
        fig_bible.update_layout(
            paper_bgcolor="#0A0A0F",
            plot_bgcolor="#0A0A0F",
            showlegend=False,
            yaxis=dict(tickvals=[0, 1], ticktext=["Missed", "Met"], gridcolor="#1e1e2e"),
            xaxis=dict(gridcolor="#1e1e2e"),
            margin=dict(l=0, r=0, t=10, b=0),
        )
        st.plotly_chart(fig_bible, use_container_width=True)
    else:
        st.info("No Bible reading data available yet.")

# ── Charts Row 2 ──────────────────────────────────────────────────────────────
col_a, col_b = st.columns([1, 2])

with col_a:
    st.markdown("#### Prayer Streak")
    prayer_counts = df["prayer_status"].value_counts().reset_index()
    prayer_counts.columns = ["status", "count"]
    fig_prayer = px.pie(
        prayer_counts,
        names="status",
        values="count",
        color="status",
        color_discrete_map={"Completed": "#00FF94", "Missed": "#FF4B4B"},
        template="plotly_dark",
        hole=0.55,
    )
    fig_prayer.update_layout(
        paper_bgcolor="#0A0A0F",
        margin=dict(l=0, r=0, t=10, b=0),
        legend=dict(font=dict(color="#888")),
    )
    st.plotly_chart(fig_prayer, use_container_width=True)

with col_b:
    st.markdown("#### Apollo Backlog & Tasks")
    fig_backlog = px.bar(
        df,
        x="log_date",
        y="apollo_backlog",
        color_discrete_sequence=["#00D4FF"],
        template="plotly_dark",
    )
    if "tasks_done" in df.columns:
        fig_backlog.add_trace(
            go.Scatter(
                x=df["log_date"],
                y=df["tasks_done"],
                mode="lines+markers",
                name="Tasks Done",
                line=dict(color="#00FF94", width=2),
            )
        )
    fig_backlog.update_layout(
        paper_bgcolor="#0A0A0F",
        plot_bgcolor="#0A0A0F",
        yaxis=dict(gridcolor="#1e1e2e"),
        xaxis=dict(gridcolor="#1e1e2e"),
        margin=dict(l=0, r=0, t=10, b=0),
    )
    st.plotly_chart(fig_backlog, use_container_width=True)

st.divider()

# ── Log History Table ─────────────────────────────────────────────────────────
st.markdown("#### Full Log History")

display_df = df.copy()
display_df["log_date"] = display_df["log_date"].dt.strftime("%a, %d %b %Y")

if "last_updated_at" in display_df.columns:
    display_df["last_updated_at"] = display_df["last_updated_at"].dt.strftime(
        "%d %b %Y %H:%M"
    )

# Reorder and rename columns for display
column_map = {
    "log_date": "Date",
    "prayer_status": "Prayer",
    "bible_reading": "Reading",
    "skill_focus": "Skill Focus",
    "apollo_backlog": "Backlog",
    "tasks_done": "Tasks Done",
    "energy_level": "Energy",
    "daily_win": "Daily Win",
    "last_updated_at": "Last Updated",
}

display_cols = [c for c in column_map if c in display_df.columns]
display_df = display_df[display_cols].rename(columns=column_map)
display_df = display_df.iloc[::-1].reset_index(drop=True)  # newest first

st.dataframe(
    display_df,
    use_container_width=True,
    hide_index=True,
    column_config={
        "Prayer": st.column_config.TextColumn(width="small"),
        "Energy": st.column_config.ProgressColumn(
            min_value=0, max_value=10, format="%d/10"
        ),
        "Backlog": st.column_config.NumberColumn(format="%d tasks"),
        "Tasks Done": st.column_config.NumberColumn(format="%d"),
    },
)

# ── Refresh Button ────────────────────────────────────────────────────────────
st.divider()
if st.button("Refresh Data", use_container_width=False):
    st.rerun()

