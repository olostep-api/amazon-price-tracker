from .utils import parse_float, parse_json_string


def normalize_scrape_result(item: dict, checked_at: str) -> dict:
    source_url = item.get("url", "")
    details = parse_json_string((item.get("result") or {}).get("json_content"))

    scrape_status = "success" if details and not item.get("error") else "error"
    current_price = parse_float(details.get("priceUpdated"))

    return {
        "source_url": source_url,
        "scrape_status": scrape_status,
        "title": details.get("title"),
        "price": current_price,
        "previous_price": None,
        "price_change": None,
        "price_change_direction": "unknown",
        "currency": "USD" if current_price is not None else "",
        "review_stars": details.get("reviewStars"),
        "number_reviews": details.get("numberReviews"),
        "is_available": details.get("is_available"),
        "seller_name": details.get("sellerNameUpdated"),
        "seller_type": details.get("sellerTypeUpdated"),
        "image_url": details.get("image"),
        "last_checked_at": checked_at,
    }
