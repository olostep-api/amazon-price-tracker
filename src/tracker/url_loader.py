from pathlib import Path


def load_product_urls(path: str) -> list[str]:
    urls = []
    with open(path, "r", encoding="utf-8") as file:
        for raw_line in file:
            line = raw_line.strip()
            if not line or line.startswith("#"):
                continue
            urls.append(line)
    return urls


def save_product_urls(path: str, urls: list[str]) -> int:
    cleaned_urls = []
    seen = set()
    for raw_url in urls:
        url = (raw_url or "").strip()
        if not url or url in seen:
            continue
        seen.add(url)
        cleaned_urls.append(url)

    file_path = Path(path)
    if file_path.parent and str(file_path.parent) != ".":
        file_path.parent.mkdir(parents=True, exist_ok=True)

    content = "\n".join(cleaned_urls)
    if cleaned_urls:
        content += "\n"
    file_path.write_text(content, encoding="utf-8")
    return len(cleaned_urls)


def add_product_url(path: str, url: str) -> bool:
    candidate = (url or "").strip()
    if not candidate:
        return False

    try:
        existing_urls = load_product_urls(path)
    except FileNotFoundError:
        existing_urls = []

    if candidate in existing_urls:
        return False

    existing_urls.append(candidate)
    save_product_urls(path, existing_urls)
    return True


def remove_product_url(path: str, url: str) -> bool:
    candidate = (url or "").strip()
    if not candidate:
        return False

    try:
        existing_urls = load_product_urls(path)
    except FileNotFoundError:
        return False

    if candidate not in existing_urls:
        return False

    existing_urls.remove(candidate)
    save_product_urls(path, existing_urls)
    return True


def update_product_url(path: str, old_url: str, new_url: str) -> bool:
    old_candidate = (old_url or "").strip()
    new_candidate = (new_url or "").strip()

    if not old_candidate or not new_candidate:
        return False

    try:
        existing_urls = load_product_urls(path)
    except FileNotFoundError:
        return False

    if old_candidate not in existing_urls:
        return False

    if new_candidate != old_candidate and new_candidate in existing_urls:
        return False

    index = existing_urls.index(old_candidate)
    existing_urls[index] = new_candidate
    save_product_urls(path, existing_urls)
    return True
