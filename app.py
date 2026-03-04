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


def is_valid_url(url: str) -> bool:
    return (url or "").strip().startswith(("http://", "https://"))


def render_csv_table(csv_path: str, history_json_path: str) -> None:
    rows = get_tracking_view(csv_path, history_json_path)
    if not rows:
        st.info("CSV is empty.")
        return

    st.subheader("Tracked Products")
    st.dataframe(rows, use_container_width=True, hide_index=True)


def main() -> None:
    st.set_page_config(page_title="Price Tracker", layout="wide")
    st.title("Product Price Tracker")

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

    left_col, right_col = st.columns([1, 1])

    with left_col:
        st.subheader("Product URLs (JSON)")
        try:
            urls = load_product_urls(urls_file)
        except FileNotFoundError:
            urls = []

        st.json({"urls": urls})

        new_url = st.text_input("Add new URL", placeholder="https://www.amazon.com/dp/...")
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

        st.subheader("Edit or Remove URL")
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
        st.subheader("Run Tracker")
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
            c1, c2, c3, c4 = st.columns(4)
            c1.metric("Changed", last_run["changed"])
            c2.metric("Higher", last_run["higher"])
            c3.metric("Lower", last_run["lower"])
            c4.metric("Same", last_run["same"])
            st.caption(f"History JSON: {last_run['history_json_path']}")
            if last_run["schema_changed"]:
                st.info("CSV schema was aligned to the tracker columns.")

        st.subheader("Scheduler")
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
        scheduler_status = (
            scheduler.status()
            if scheduler is not None
            else {
                "running": False,
                "interval_seconds": 0,
                "last_run_at": None,
                "next_run_at": None,
                "last_result": None,
                "last_error": None,
            }
        )

        st.write(f"Scheduler running: {scheduler_status['running']}")
        st.write(f"Last run (UTC): {scheduler_status['last_run_at'] or '-'}")
        st.write(f"Next run (UTC): {scheduler_status['next_run_at'] or '-'}")
        if scheduler_status["last_error"]:
            st.error(f"Scheduler error: {scheduler_status['last_error']}")

        if scheduler_status["last_result"]:
            sr = scheduler_status["last_result"]
            s1, s2, s3, s4 = st.columns(4)
            s1.metric("Sched Changed", sr["changed"])
            s2.metric("Sched Higher", sr["higher"])
            s3.metric("Sched Lower", sr["lower"])
            s4.metric("Sched Same", sr["same"])

    st.divider()
    render_csv_table(csv_path, history_json_path)


if __name__ == "__main__":
    main()
