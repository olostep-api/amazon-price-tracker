from datetime import datetime, timezone

from .constants import CSV_COLUMNS, DEFAULT_HISTORY_JSON, UPDATE_ON_SUCCESS_COLUMNS
from .csv_store import ensure_csv_schema, read_csv_rows, upsert_rows
from .json_history import get_product_stats_map, update_price_history
from .normalizer import normalize_scrape_result
from .olostep_client import OlostepClient
from .url_loader import load_product_urls


def run_tracking(
    api_key: str,
    csv_path: str,
    urls_file: str,
    sleep_seconds: float,
    history_json_path: str = DEFAULT_HISTORY_JSON,
) -> dict:
    if not api_key:
        raise ValueError("Missing OLOSTEP_API_KEY. Set it in .env.")

    urls = load_product_urls(urls_file)
    if not urls:
        raise ValueError(f"No product URLs found in {urls_file}.")

    schema_changed = ensure_csv_schema(csv_path, CSV_COLUMNS)
    client = OlostepClient(api_key)
    scrape_results = client.scrape_urls(urls, sleep_seconds)
    checked_at = datetime.now(timezone.utc).replace(microsecond=0).isoformat()
    records = [normalize_scrape_result(item, checked_at) for item in scrape_results]
    update_stats = upsert_rows(
        csv_path,
        records,
        CSV_COLUMNS,
        UPDATE_ON_SUCCESS_COLUMNS,
    )
    product_stats_map = update_price_history(history_json_path, records, checked_at)
    csv_rows = read_csv_rows(csv_path, CSV_COLUMNS)
    csv_rows_with_average = []
    for row in csv_rows:
        source_url = row.get("source_url", "")
        stats = product_stats_map.get(source_url, {})
        row_copy = dict(row)
        row_copy["average_price_from_json"] = stats.get("average_price")
        row_copy["price_samples_from_json"] = stats.get("samples", 0)
        csv_rows_with_average.append(row_copy)

    return {
        "schema_changed": schema_changed,
        "checked_at": checked_at,
        "history_json_path": history_json_path,
        "appended": update_stats["appended"],
        "updated": update_stats["updated"],
        "skipped": update_stats["skipped"],
        "changed": update_stats["changed"],
        "higher": update_stats["higher"],
        "lower": update_stats["lower"],
        "same": update_stats["same"],
        "total_urls": len(urls),
        "csv_rows": csv_rows_with_average,
        "product_stats_map": product_stats_map,
    }


def get_tracking_view(csv_path: str, history_json_path: str = DEFAULT_HISTORY_JSON) -> list[dict]:
    csv_rows = read_csv_rows(csv_path, CSV_COLUMNS)
    stats_map = get_product_stats_map(history_json_path)
    view_rows = []
    for row in csv_rows:
        source_url = row.get("source_url", "")
        stats = stats_map.get(source_url, {})
        row_copy = dict(row)
        row_copy["average_price_from_json"] = stats.get("average_price")
        row_copy["price_samples_from_json"] = stats.get("samples", 0)
        view_rows.append(row_copy)
    return view_rows
