import argparse
import os
import signal
import time

from dotenv import load_dotenv

from src.tracker.constants import DEFAULT_CSV_PATH, DEFAULT_HISTORY_JSON, DEFAULT_URLS_FILE
from src.tracker.scheduler import TrackingScheduler

load_dotenv()


def parse_args():
    parser = argparse.ArgumentParser(
        description="Run the price tracker on a fixed schedule."
    )
    parser.add_argument(
        "--csv",
        default=DEFAULT_CSV_PATH,
        help=f"CSV file path (default: {DEFAULT_CSV_PATH}).",
    )
    parser.add_argument(
        "--urls-file",
        default=DEFAULT_URLS_FILE,
        help=f"Path to product URLs text file (default: {DEFAULT_URLS_FILE}).",
    )
    parser.add_argument(
        "--sleep",
        type=float,
        default=2.0,
        help="Seconds to wait between API requests in each run.",
    )
    parser.add_argument(
        "--interval-minutes",
        type=float,
        default=30.0,
        help="How often to run the comparison.",
    )
    parser.add_argument(
        "--history-json",
        default=DEFAULT_HISTORY_JSON,
        help=f"Path to JSON history file (default: {DEFAULT_HISTORY_JSON}).",
    )
    return parser.parse_args()


def main():
    args = parse_args()
    api_key = os.getenv("OLOSTEP_API_KEY")
    if not api_key:
        raise ValueError("Missing OLOSTEP_API_KEY. Set it in .env.")

    scheduler = TrackingScheduler(
        api_key=api_key,
        csv_path=args.csv,
        urls_file=args.urls_file,
        sleep_seconds=args.sleep,
        history_json_path=args.history_json,
    )

    interval_seconds = args.interval_minutes * 60
    scheduler.start(interval_seconds)
    print(f"Scheduler started. Interval: {args.interval_minutes} minutes.")
    print("Press Ctrl+C to stop.")

    def _shutdown(_sig, _frame):
        scheduler.stop()
        print("Scheduler stopped.")
        raise SystemExit(0)

    signal.signal(signal.SIGINT, _shutdown)
    signal.signal(signal.SIGTERM, _shutdown)

    while True:
        status = scheduler.status()
        if status["last_error"]:
            print(f"Scheduler error: {status['last_error']}")
        time.sleep(5)


if __name__ == "__main__":
    main()
