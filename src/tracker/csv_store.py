import csv
import os

from .utils import parse_float, to_csv_value


def ensure_csv_schema(csv_path: str, columns: list[str]) -> bool:
    if not os.path.exists(csv_path) or os.path.getsize(csv_path) == 0:
        return False

    with open(csv_path, "r", encoding="utf-8", newline="") as file:
        reader = csv.DictReader(file)
        existing_rows = list(reader)
        fieldnames = reader.fieldnames or []

    if fieldnames == columns:
        return False

    projected_rows = []
    for row in existing_rows:
        projected_rows.append({column: row.get(column, "") for column in columns})

    write_csv_rows(csv_path, projected_rows, columns)
    return True


def read_csv_rows(csv_path: str, columns: list[str]) -> list[dict]:
    if not os.path.exists(csv_path) or os.path.getsize(csv_path) == 0:
        return []

    with open(csv_path, "r", encoding="utf-8", newline="") as file:
        reader = csv.DictReader(file)
        return [{column: row.get(column, "") for column in columns} for row in reader]


def write_csv_rows(csv_path: str, rows: list[dict], columns: list[str]) -> None:
    csv_dir = os.path.dirname(csv_path)
    if csv_dir:
        os.makedirs(csv_dir, exist_ok=True)
    with open(csv_path, "w", encoding="utf-8", newline="") as file:
        writer = csv.DictWriter(file, fieldnames=columns)
        writer.writeheader()
        for row in rows:
            writer.writerow({key: to_csv_value(row.get(key)) for key in columns})


def upsert_rows(
    csv_path: str,
    records: list[dict],
    columns: list[str],
    update_on_success_columns: list[str],
) -> dict:
    rows = read_csv_rows(csv_path, columns)
    row_index_by_url = {}

    for index, row in enumerate(rows):
        source_url = (row.get("source_url") or "").strip()
        if source_url:
            row_index_by_url[source_url] = index

    appended = 0
    updated = 0
    skipped = 0
    changed = 0
    higher = 0
    lower = 0
    same = 0

    for record in records:
        source_url = (record.get("source_url") or "").strip()
        if not source_url:
            skipped += 1
            continue

        if source_url not in row_index_by_url:
            rows.append(record)
            row_index_by_url[source_url] = len(rows) - 1
            rows[-1]["price_change_direction"] = "new"
            appended += 1
            continue

        if record.get("scrape_status") != "success":
            skipped += 1
            continue

        row = rows[row_index_by_url[source_url]]
        old_price = parse_float(row.get("price"))
        new_price = record.get("price")
        row["last_checked_at"] = record.get("last_checked_at", row.get("last_checked_at", ""))

        if new_price is not None:
            row["previous_price"] = old_price if old_price is not None else ""
            row["price"] = new_price
            row["currency"] = record.get("currency") or row.get("currency", "")

            if old_price is None:
                row["price_change"] = ""
                row["price_change_direction"] = "new"
            else:
                price_change = new_price - old_price
                row["price_change"] = price_change
                if price_change > 0:
                    row["price_change_direction"] = "higher"
                    changed += 1
                    higher += 1
                elif price_change < 0:
                    row["price_change_direction"] = "lower"
                    changed += 1
                    lower += 1
                else:
                    row["price_change_direction"] = "same"
                    same += 1
        else:
            row["price_change"] = ""
            row["price_change_direction"] = "unknown"

        row["scrape_status"] = record.get("scrape_status", row.get("scrape_status", ""))

        for column in update_on_success_columns:
            value = record.get(column)
            if value is not None and value != "":
                row[column] = value

        updated += 1

    write_csv_rows(csv_path, rows, columns)
    return {
        "appended": appended,
        "updated": updated,
        "skipped": skipped,
        "changed": changed,
        "higher": higher,
        "lower": lower,
        "same": same,
    }
