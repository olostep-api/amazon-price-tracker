import time

import requests

from .constants import BASE_URL, PARSER_ID


class OlostepClient:
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        }

    def scrape_single(self, url: str) -> dict:
        payload = {
            "formats": ["json"],
            "parser": {"id": PARSER_ID},
            "url_to_scrape": url,
        }

        response = requests.post(
            f"{BASE_URL}/scrapes",
            headers=self.headers,
            json=payload,
            timeout=180,
        )

        if not response.ok:
            return {
                "url": url,
                "status": response.status_code,
                "error": response.text,
            }
        return response.json()

    def scrape_urls(self, urls: list[str], delay_sec: float) -> list[dict]:
        results = []
        for index, url in enumerate(urls, start=1):
            print(f"[{index}/{len(urls)}] Scraping {url}")
            results.append(self.scrape_single(url))
            if index < len(urls) and delay_sec > 0:
                time.sleep(delay_sec)
        return results

