import argparse
import os

from dotenv import load_dotenv

from src.tracker.constants import DEFAULT_CSV_PATH, DEFAULT_HISTORY_JSON, DEFAULT_URLS_FILE
from src.tracker.service import run_tracking

load_dotenv()

OLOSTEP_API_KEY = os.getenv("OLOSTEP_API_KEY")


def parse_args():
    parser = argparse.ArgumentParser(
        description="Track products, compare prices, and update CSV records."
    )
    parser.add_argument(
        "--csv",
        default=DEFAULT_CSV_PATH,
        help=f"CSV file path (default: {DEFAULT_CSV_PATH}).",
    )
    parser.add_argument(
        "--sleep",
        type=float,
        default=2,
        help="Seconds to wait between API requests (default: 2).",
    )
    parser.add_argument(
        "--urls-file",
        default=DEFAULT_URLS_FILE,
        help=f"Path to product URLs text file (default: {DEFAULT_URLS_FILE}).",
    )
    parser.add_argument(
        "--history-json",
        default=DEFAULT_HISTORY_JSON,
        help=f"Path to JSON history file (default: {DEFAULT_HISTORY_JSON}).",
    )
    return parser.parse_args()


def main():
    args = parse_args()
    result = run_tracking(
        api_key=OLOSTEP_API_KEY,
        csv_path=args.csv,
        urls_file=args.urls_file,
        sleep_seconds=args.sleep,
        history_json_path=args.history_json,
    )

    if result["schema_changed"]:
        print(f"CSV schema updated to requested columns: {args.csv}")
    print(f"Checked at: {result['checked_at']}")
    print(f"CSV updated: {args.csv}")
    print(f"History JSON updated: {result['history_json_path']}")
    print(
        f"Rows appended (new products): {result['appended']} | "
        f"Rows updated (successful existing products): {result['updated']} | "
        f"Rows skipped: {result['skipped']}"
    )
    print(
        f"Price changes: {result['changed']} | "
        f"Higher: {result['higher']} | Lower: {result['lower']} | Same: {result['same']}"
    )


if __name__ == "__main__":
    main()
