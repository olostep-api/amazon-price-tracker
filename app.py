import html
import os

import streamlit as st
from dotenv import load_dotenv

from src.tracker.constants import DEFAULT_CSV_PATH, DEFAULT_HISTORY_JSON, DEFAULT_URLS_FILE
from src.tracker.scheduler import TrackingScheduler
from src.tracker.service import get_tracking_view, run_tracking
from src.tracker.url_loader import (
    add_product_url,
    load_product_urls,
    remove_product_url,
    update_product_url,
)

load_dotenv()

DEFAULT_HISTORY_JSON_PATH = DEFAULT_HISTORY_JSON

APP_CSS = """
:root {
  --olostep-primary: #635bff;
  --olostep-primary-hover: #534ae6;
  --olostep-bg: #f9fafb;
  --olostep-surface: #ffffff;
  --olostep-surface-alt: #f4f6ff;
  --olostep-text: #13152b;
  --olostep-muted: #5c6370;
  --olostep-border: #dce0f0;
  --olostep-secondary: #eceffd;
  --olostep-secondary-hover: #e2e6ff;
  --olostep-soft-1: #eef0ff;
  --olostep-soft-2: #eef1ff;
  --olostep-soft-3: #f1f3ff;
  --olostep-success: #0f8f5f;
  --olostep-error: #c2362b;
}

.stApp {
  color: var(--olostep-text);
  font-family: "Segoe UI", "SF Pro Text", "Helvetica Neue", Helvetica, Arial, sans-serif;
  background:
    radial-gradient(circle at 6% 0%, rgba(99, 91, 255, 0.11), rgba(99, 91, 255, 0) 35%),
    var(--olostep-bg);
}

header[data-testid="stHeader"] {
  display: none !important;
}

div[data-testid="stDecoration"] {
  display: none !important;
}

div[data-testid="stAppViewContainer"] > .main .block-container {
  max-width: 1320px;
  padding: 0.5rem 1rem 1rem;
}

div[data-testid="stVerticalBlock"] {
  gap: 0.55rem;
}

div[data-testid="stHorizontalBlock"] {
  gap: 0.6rem;
}

h1, h2, h3 {
  color: var(--olostep-text);
}

p, label, span, li, div[data-testid="stMarkdownContainer"] {
  color: var(--olostep-text);
}

div[data-testid="stCaptionContainer"] p {
  color: var(--olostep-muted) !important;
  font-size: 0.82rem;
}

section[data-testid="stSidebar"] {
  border-right: 1px solid var(--olostep-border);
  background: linear-gradient(180deg, #f4f6ff 0%, #f9fafb 100%);
}

section[data-testid="stSidebar"] [data-testid="stSidebarContent"] {
  padding-top: 0.65rem;
}

section[data-testid="stSidebar"] label {
  font-size: 0.88rem;
}

[data-testid="stVerticalBlockBorderWrapper"] {
  border: 1px solid var(--olostep-border) !important;
  border-radius: 14px !important;
  background: rgba(255, 255, 255, 0.96);
  box-shadow: 0 8px 16px rgba(19, 21, 43, 0.05);
}

[data-testid="stVerticalBlockBorderWrapper"] > div[data-testid="stVerticalBlock"] {
  gap: 0.42rem;
}

.ol-hero {
  border: 1px solid rgba(99, 91, 255, 0.35);
  border-radius: 14px;
  padding: 0.78rem 0.95rem;
  margin-bottom: 0.45rem;
  background: linear-gradient(145deg, rgba(99, 91, 255, 0.2), rgba(255, 255, 255, 0.95));
  box-shadow: 0 10px 22px rgba(19, 21, 43, 0.08);
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 0.9rem;
}

.ol-hero h1 {
  margin: 0;
  font-size: 1.54rem;
  line-height: 1.2;
}

.ol-hero p {
  margin: 0.2rem 0 0;
  color: #2d3560;
  font-size: 0.93rem;
}

.ol-badge {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  font-weight: 600;
  font-size: 0.76rem;
  line-height: 1;
  border-radius: 999px;
  padding: 0.33rem 0.58rem;
  white-space: nowrap;
}

.ol-badge.is-success {
  color: var(--olostep-success);
  background: rgba(15, 143, 95, 0.12);
  border: 1px solid rgba(15, 143, 95, 0.3);
}

.ol-badge.is-error {
  color: var(--olostep-error);
  background: rgba(194, 54, 43, 0.12);
  border: 1px solid rgba(194, 54, 43, 0.3);
}

.ol-hero-meta {
  margin-top: 0.45rem;
  display: flex;
  flex-wrap: wrap;
  gap: 0.36rem;
}

.ol-chip {
  display: inline-flex;
  align-items: center;
  gap: 0.26rem;
  font-size: 0.74rem;
  font-weight: 600;
  border-radius: 999px;
  border: 1px solid #d8ddf6;
  background: #f1f3ff;
  color: #303962;
  padding: 0.22rem 0.5rem;
}

.ol-card-title {
  margin: 0;
  font-size: 0.98rem;
  font-weight: 700;
  letter-spacing: 0.01em;
}

.ol-card-subtitle {
  margin: 0.08rem 0 0.5rem;
  color: #4f5773;
  font-size: 0.84rem;
}

.ol-section-label {
  margin: 0.15rem 0 0.05rem;
  font-size: 0.84rem;
  font-weight: 700;
  color: #2a335d;
}

div[data-baseweb="input"] > div,
div[data-baseweb="select"] > div,
div[data-testid="stNumberInput"] > div > div {
  background: var(--olostep-surface) !important;
  border: 1px solid var(--olostep-border) !important;
  border-radius: 9px !important;
}

div[data-baseweb="input"] > div:focus-within,
div[data-baseweb="select"] > div:focus-within,
div[data-testid="stNumberInput"] > div > div:focus-within {
  border-color: var(--olostep-primary) !important;
  box-shadow: 0 0 0 2px rgba(99, 91, 255, 0.17);
}

div[data-baseweb="input"] input,
div[data-baseweb="select"] input,
div[data-testid="stNumberInput"] input,
textarea {
  color: var(--olostep-text) !important;
  font-size: 0.9rem !important;
}

div[data-testid="stButton"] > button {
  border-radius: 9px;
  border: 1px solid #cfd5f4;
  background: var(--olostep-secondary);
  color: #1f2751;
  font-weight: 600;
  min-height: 2.24rem;
  padding: 0.36rem 0.55rem;
  font-size: 0.92rem;
}

div[data-testid="stButton"] > button:hover {
  border-color: #c3cbed;
  background: var(--olostep-secondary-hover);
  color: #141b42;
}

div[data-testid="stButton"] > button[kind="primary"] {
  border-color: var(--olostep-primary);
  background: var(--olostep-primary);
  color: #ffffff;
  box-shadow: 0 8px 18px rgba(99, 91, 255, 0.24);
}

div[data-testid="stButton"] > button[kind="primary"]:hover {
  border-color: var(--olostep-primary-hover) !important;
  background: var(--olostep-primary-hover) !important;
  color: #ffffff !important;
}

div[data-testid="stButton"] > button:focus {
  box-shadow: 0 0 0 2px rgba(99, 91, 255, 0.2);
}

div[data-testid="stMetric"] {
  border: 1px solid var(--olostep-border);
  border-radius: 10px;
  padding: 0.42rem 0.55rem;
  background: var(--olostep-surface-alt);
}

div[data-testid="stMetricLabel"] {
  color: var(--olostep-muted) !important;
  text-transform: uppercase;
  letter-spacing: 0.04em;
  font-size: 0.68rem;
}

div[data-testid="stMetricValue"] {
  color: var(--olostep-text);
  font-size: 1.22rem;
}

div[data-testid="stJson"] {
  border: 1px solid var(--olostep-border);
  border-radius: 9px;
  background: var(--olostep-soft-3);
}

div[data-testid="stDataFrame"] {
  border: 1px solid var(--olostep-border);
  border-radius: 10px;
  background: var(--olostep-surface);
}

div[data-testid="stDataFrame"] [role="columnheader"] {
  background: var(--olostep-soft-2) !important;
}

div[data-testid="stTabs"] button[role="tab"] {
  height: 2.02rem;
  border: 1px solid #d6dbf4;
  border-radius: 9px;
  background: var(--olostep-soft-1);
  color: #3d466e;
  font-size: 0.86rem;
  font-weight: 600;
}

div[data-testid="stTabs"] button[role="tab"][aria-selected="true"] {
  border-color: var(--olostep-primary);
  background: rgba(99, 91, 255, 0.12);
  color: #242d59;
}

div[data-testid="stExpander"] details {
  border: 1px solid #d8def2;
  border-radius: 9px;
  background: var(--olostep-surface-alt);
}

div[data-testid="stExpander"] summary {
  color: #27305d !important;
  font-size: 0.86rem;
  font-weight: 600;
}

div[data-testid="stAlert"] {
  border-radius: 10px;
  border: 1px solid var(--olostep-border);
  background: var(--olostep-soft-3);
}

div[data-testid="stAlert"][kind="success"] {
  border-color: rgba(15, 143, 95, 0.32);
  background: rgba(15, 143, 95, 0.09);
}

div[data-testid="stAlert"][kind="error"] {
  border-color: rgba(194, 54, 43, 0.32);
  background: rgba(194, 54, 43, 0.09);
}

.ol-status-row {
  border: 1px solid var(--olostep-border);
  border-radius: 9px;
  background: var(--olostep-soft-2);
  padding: 0.42rem 0.54rem;
  margin-bottom: 0.32rem;
  display: flex;
  justify-content: space-between;
  gap: 0.75rem;
}

.ol-status-row strong {
  color: #1a2149;
  font-size: 0.82rem;
}

.ol-status-row span {
  color: #2f365f;
  font-size: 0.82rem;
}
"""


def inject_app_css() -> None:
    st.markdown(f"<style>{APP_CSS}</style>", unsafe_allow_html=True)


def render_hero(
    api_key: str,
    urls_count: int,
    scheduler_running: bool,
    sleep_seconds: float,
) -> None:
    status_class = "is-success" if api_key else "is-error"
    status_text = "API key configured" if api_key else "API key missing"
    scheduler_text = "Scheduler on" if scheduler_running else "Scheduler off"
    scheduler_class = "is-success" if scheduler_running else "is-error"
    st.markdown(
        f"""
        <section class="ol-hero">
          <div>
            <h1>Product Price Tracker</h1>
            <p>Compact dashboard for URL management, live runs, and scheduled price checks.</p>
            <div class="ol-hero-meta">
              <span class="ol-chip">URLs: {urls_count}</span>
              <span class="ol-chip">Delay: {sleep_seconds:g}s</span>
              <span class="ol-badge {scheduler_class}">{scheduler_text}</span>
            </div>
          </div>
          <span class="ol-badge {status_class}">{status_text}</span>
        </section>
        """,
        unsafe_allow_html=True,
    )


def render_card_header(title: str, subtitle: str) -> None:
    title_html = html.escape(title)
    subtitle_html = html.escape(subtitle)
    st.markdown(
        f"""
        <h3 class="ol-card-title">{title_html}</h3>
        <p class="ol-card-subtitle">{subtitle_html}</p>
        """,
        unsafe_allow_html=True,
    )


def render_status_row(label: str, value: str) -> None:
    label_html = html.escape(label)
    value_html = html.escape(value)
    st.markdown(
        f"""
        <div class="ol-status-row">
          <strong>{label_html}</strong>
          <span>{value_html}</span>
        </div>
        """,
        unsafe_allow_html=True,
    )


def get_scheduler_status(scheduler: TrackingScheduler | None) -> dict:
    if scheduler is None:
        return {
            "running": False,
            "interval_seconds": 0,
            "last_run_at": None,
            "next_run_at": None,
            "last_result": None,
            "last_error": None,
        }
    return scheduler.status()


def render_overview_strip(
    urls_count: int,
    scheduler_status: dict,
    last_run: dict | None,
) -> None:
    with st.container(border=True):
        m1, m2, m3, m4 = st.columns(4)
        m1.metric("URLs Queued", urls_count)
        m2.metric("Scheduler", "Running" if scheduler_status["running"] else "Stopped")
        if last_run:
            m3.metric("Last Changed", last_run["changed"])
            m4.metric("Last URLs", last_run["total_urls"])
        else:
            m3.metric("Last Changed", "-")
            m4.metric("Last URLs", "-")


def is_valid_url(url: str) -> bool:
    return (url or "").strip().startswith(("http://", "https://"))


def render_csv_table(
    csv_path: str,
    history_json_path: str,
    search_query: str = "",
    direction_filter: str = "All",
) -> None:
    rows = get_tracking_view(csv_path, history_json_path)
    total_rows = len(rows)
    if total_rows == 0:
        st.info("CSV is empty.")
        return

    query = (search_query or "").strip().lower()
    if query:
        rows = [
            row
            for row in rows
            if query in str(row.get("title", "")).lower()
            or query in str(row.get("source_url", "")).lower()
        ]

    if direction_filter != "All":
        rows = [
            row
            for row in rows
            if str(row.get("price_change_direction", "")).lower() == direction_filter.lower()
        ]

    if not rows:
        st.info("No products match the current filters.")
        return

    st.caption(f"Showing {len(rows)} of {total_rows} tracked product(s)")
    st.dataframe(rows, use_container_width=True, hide_index=True, height=360)


def main() -> None:
    st.set_page_config(page_title="Price Tracker", layout="wide")
    inject_app_css()

    api_key = os.getenv("OLOSTEP_API_KEY", "")
    if "tracker_scheduler" not in st.session_state:
        st.session_state["tracker_scheduler"] = None

    with st.sidebar:
        st.header("Settings")
        csv_path = st.text_input("CSV file", value=DEFAULT_CSV_PATH)
        urls_file = st.text_input("URLs file", value=DEFAULT_URLS_FILE)
        history_json_path = st.text_input(
            "History JSON file",
            value=DEFAULT_HISTORY_JSON_PATH,
        )
        sleep_seconds = st.number_input(
            "Delay between requests (sec)",
            min_value=0.0,
            value=2.0,
            step=0.5,
        )
        st.caption(
            "API key status: configured"
            if api_key
            else "API key status: missing (set OLOSTEP_API_KEY in .env)"
        )

    try:
        urls = load_product_urls(urls_file)
    except FileNotFoundError:
        urls = []

    scheduler = st.session_state.get("tracker_scheduler")
    scheduler_status = get_scheduler_status(scheduler)
    last_run = st.session_state.get("last_run_result")

    render_hero(api_key, len(urls), scheduler_status["running"], float(sleep_seconds))
    render_overview_strip(len(urls), scheduler_status, last_run)

    dashboard_tab, data_tab = st.tabs(["Dashboard", "Tracked Data"])

    with dashboard_tab:
        left_col, right_col = st.columns([1, 1], gap="small")

        with left_col:
            with st.container(border=True):
                render_card_header(
                    "URL Workspace",
                    "Preview, add, edit, and remove tracked product links.",
                )
                tab_add, tab_edit = st.tabs(["Preview & Add", "Edit / Remove"])
                with tab_add:
                    st.caption(f"Source: {urls_file} | Loaded: {len(urls)} URL(s)")
                    with st.expander("URL JSON preview", expanded=False):
                        st.json({"urls": urls}, expanded=False)

                    new_url = st.text_input(
                        "Add new URL",
                        placeholder="https://www.amazon.com/dp/...",
                    )
                    add_col, reload_col = st.columns(2)
                    with add_col:
                        if st.button("Add URL", use_container_width=True):
                            if not new_url.strip():
                                st.warning("Please enter a URL.")
                            elif not is_valid_url(new_url):
                                st.warning("URL must start with http:// or https://.")
                            else:
                                added = add_product_url(urls_file, new_url)
                                if added:
                                    st.success(f"URL added to {urls_file}.")
                                    st.rerun()
                                else:
                                    st.info("URL already exists or is invalid.")
                    with reload_col:
                        if st.button("Reload URLs", use_container_width=True):
                            st.rerun()

                with tab_edit:
                    if not urls:
                        st.info("No URLs found. Add a URL first.")
                    else:
                        selected_url = st.selectbox("Select URL", options=urls)
                        edited_url = st.text_input("Edited URL", value=selected_url)

                        edit_col, remove_col = st.columns(2)
                        with edit_col:
                            if st.button("Save Edit", use_container_width=True):
                                if not edited_url.strip():
                                    st.warning("Edited URL cannot be empty.")
                                elif not is_valid_url(edited_url):
                                    st.warning("Edited URL must start with http:// or https://.")
                                else:
                                    updated = update_product_url(urls_file, selected_url, edited_url)
                                    if updated:
                                        st.success("URL updated.")
                                        st.rerun()
                                    else:
                                        st.info("Could not update URL (duplicate or not found).")

                        with remove_col:
                            if st.button("Remove URL", use_container_width=True):
                                removed = remove_product_url(urls_file, selected_url)
                                if removed:
                                    st.success("URL removed.")
                                    st.rerun()
                                else:
                                    st.info("Could not remove URL.")

        with right_col:
            with st.container(border=True):
                render_card_header(
                    "Tracking Control",
                    "Run manual checks or manage scheduled comparisons.",
                )
                run_tab, scheduler_tab = st.tabs(["Manual Run", "Scheduler"])

                with run_tab:
                    if not api_key:
                        st.warning("Missing OLOSTEP_API_KEY in .env.")

                    if st.button("Start Tracking", type="primary", use_container_width=True):
                        try:
                            with st.spinner("Running scrape and updating CSV..."):
                                result = run_tracking(
                                    api_key=api_key,
                                    csv_path=csv_path,
                                    urls_file=urls_file,
                                    sleep_seconds=float(sleep_seconds),
                                    history_json_path=history_json_path,
                                )
                            st.session_state["last_run_result"] = result
                            st.success("Tracking completed.")
                        except Exception as exc:
                            st.error(str(exc))

                    last_run = st.session_state.get("last_run_result")
                    if last_run:
                        m1, m2, m3, m4 = st.columns(4)
                        m1.metric("Appended", last_run["appended"])
                        m2.metric("Updated", last_run["updated"])
                        m3.metric("Skipped", last_run["skipped"])
                        m4.metric("URLs", last_run["total_urls"])
                        with st.expander("Price movement details", expanded=False):
                            c1, c2, c3, c4 = st.columns(4)
                            c1.metric("Changed", last_run["changed"])
                            c2.metric("Higher", last_run["higher"])
                            c3.metric("Lower", last_run["lower"])
                            c4.metric("Same", last_run["same"])
                        st.caption(f"History JSON: {last_run['history_json_path']}")
                        if last_run["schema_changed"]:
                            st.info("CSV schema was aligned to the tracker columns.")

                with scheduler_tab:
                    interval_minutes = st.number_input(
                        "Run comparison every N minutes",
                        min_value=1,
                        value=30,
                        step=1,
                    )

                    scheduler = st.session_state.get("tracker_scheduler")
                    start_col, stop_col, refresh_col = st.columns(3)
                    with start_col:
                        if st.button("Start Scheduler", use_container_width=True):
                            try:
                                if scheduler is None or not scheduler.is_running():
                                    scheduler = TrackingScheduler(
                                        api_key=api_key,
                                        csv_path=csv_path,
                                        urls_file=urls_file,
                                        sleep_seconds=float(sleep_seconds),
                                        history_json_path=history_json_path,
                                    )
                                    st.session_state["tracker_scheduler"] = scheduler
                                started = scheduler.start(interval_minutes * 60)
                                if started:
                                    st.success("Scheduler started.")
                                else:
                                    st.info("Scheduler is already running.")
                            except Exception as exc:
                                st.error(str(exc))

                    with stop_col:
                        if st.button("Stop Scheduler", use_container_width=True):
                            if scheduler and scheduler.stop():
                                st.success("Scheduler stopped.")
                            else:
                                st.info("Scheduler is not running.")

                    with refresh_col:
                        if st.button("Refresh Status", use_container_width=True):
                            st.rerun()

                    scheduler = st.session_state.get("tracker_scheduler")
                    scheduler_status = get_scheduler_status(scheduler)
                    render_status_row(
                        "Scheduler running",
                        "Yes" if scheduler_status["running"] else "No",
                    )
                    render_status_row("Last run (UTC)", scheduler_status["last_run_at"] or "-")
                    render_status_row("Next run (UTC)", scheduler_status["next_run_at"] or "-")
                    if scheduler_status["last_error"]:
                        st.error(f"Scheduler error: {scheduler_status['last_error']}")

                    if scheduler_status["last_result"]:
                        with st.expander("Latest scheduler metrics", expanded=False):
                            sr = scheduler_status["last_result"]
                            s1, s2, s3, s4 = st.columns(4)
                            s1.metric("Sched Changed", sr["changed"])
                            s2.metric("Sched Higher", sr["higher"])
                            s3.metric("Sched Lower", sr["lower"])
                            s4.metric("Sched Same", sr["same"])

    with data_tab:
        with st.container(border=True):
            render_card_header(
                "Tracked Products",
                "Latest CSV view with JSON-derived average and sample counts.",
            )
            filter_col, direction_col = st.columns([2, 1])
            with filter_col:
                search_query = st.text_input(
                    "Search by title or URL",
                    placeholder="Search title or source URL...",
                    key="table_search",
                )
            with direction_col:
                direction_filter = st.selectbox(
                    "Direction",
                    options=["All", "higher", "lower", "same", "new", "unknown", "error"],
                    index=0,
                    key="table_direction",
                )
            render_csv_table(
                csv_path=csv_path,
                history_json_path=history_json_path,
                search_query=search_query,
                direction_filter=direction_filter,
            )



if __name__ == "__main__":
    main()
