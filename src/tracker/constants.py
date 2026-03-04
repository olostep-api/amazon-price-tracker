BASE_URL = "https://api.olostep.com/v1"
PARSER_ID = "@olostep/amazon-it-product"
DEFAULT_DATA_DIR = "data"
DEFAULT_URLS_FILE = f"{DEFAULT_DATA_DIR}/product_urls.txt"
DEFAULT_OUTPUT_DIR = "output"
DEFAULT_CSV_PATH = f"{DEFAULT_OUTPUT_DIR}/price_tracker_history.csv"
DEFAULT_HISTORY_JSON = f"{DEFAULT_OUTPUT_DIR}/product_price_history.json"

CSV_COLUMNS = [
    "source_url",
    "scrape_status",
    "title",
    "price",
    "previous_price",
    "price_change",
    "price_change_direction",
    "currency",
    "review_stars",
    "number_reviews",
    "is_available",
    "seller_name",
    "seller_type",
    "image_url",
    "last_checked_at",
]

UPDATE_ON_SUCCESS_COLUMNS = [
    "title",
    "review_stars",
    "number_reviews",
    "is_available",
    "seller_name",
    "seller_type",
    "image_url",
]
