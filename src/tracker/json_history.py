import json
from pathlib import Path

from .utils import parse_float


def _default_history() -> dict:
    return {"updated_at": None, "products": {}}


def _load_history(path: str) -> dict:
    history_path = Path(path)
    if not history_path.exists():
        return _default_history()

    try:
        data = json.loads(history_path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return _default_history()

    if not isinstance(data, dict):
        return _default_history()
    data.setdefault("updated_at", None)
    data.setdefault("products", {})
    if not isinstance(data.get("products"), dict):
        data["products"] = {}
    return data


def _save_history(path: str, data: dict) -> None:
    history_path = Path(path)
    if history_path.parent and str(history_path.parent) != ".":
        history_path.parent.mkdir(parents=True, exist_ok=True)
    history_path.write_text(
        json.dumps(data, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )


def update_price_history(path: str, records: list[dict], checked_at: str) -> dict:
    data = _load_history(path)
    products = data["products"]

    for record in records:
        source_url = (record.get("source_url") or "").strip()
        if not source_url:
            continue

        product = products.setdefault(
            source_url,
            {
                "source_url": source_url,
                "title": "",
                "currency": "",
                "price_history": [],
                "average_price": None,
                "last_price": None,
                "last_fetched_at": None,
            },
        )

        title = record.get("title")
        currency = record.get("currency")
        if title:
            product["title"] = title
        if currency:
            product["currency"] = currency

        price = parse_float(record.get("price"))
        if price is None:
            continue

        history_points = product.setdefault("price_history", [])
        history_points.append({"fetched_at": checked_at, "price": price})

        prices = [point["price"] for point in history_points if parse_float(point.get("price")) is not None]
        if prices:
            product["average_price"] = sum(prices) / len(prices)
            product["last_price"] = prices[-1]
            product["last_fetched_at"] = checked_at

    data["updated_at"] = checked_at
    _save_history(path, data)

    return get_product_stats_map(path)


def get_product_stats_map(path: str) -> dict:
    data = _load_history(path)
    products = data.get("products", {})
    stats = {}

    for source_url, product in products.items():
        history_points = product.get("price_history", []) or []
        prices = []
        for point in history_points:
            parsed = parse_float(point.get("price"))
            if parsed is not None:
                prices.append(parsed)

        average_price = (sum(prices) / len(prices)) if prices else None
        last_fetched_at = history_points[-1].get("fetched_at") if history_points else None

        stats[source_url] = {
            "average_price": average_price,
            "samples": len(prices),
            "last_fetched_at": last_fetched_at,
        }

    return stats

