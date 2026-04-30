# crawler.py
import requests
from bs4 import BeautifulSoup
import time
import json

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                  "AppleWebKit/537.36 (KHTML, like Gecko) "
                  "Chrome/120.0.0.0 Safari/537.36"
}

BASE_URL = "https://www.rekrute.com/offres.html"

def get_offer_urls(page: int) -> list[str]:
    # ✅ Paramètres corrects extraits du HTML
    params = {
        "p": page,
        "s": 1,
        "o": 1
    }
    response = requests.get(BASE_URL, headers=HEADERS, params=params, timeout=10)

    if response.status_code != 200:
        print(f"[!] Page {page} inaccessible : {response.status_code}")
        return []

    soup = BeautifulSoup(response.text, "html.parser")

    urls = []
    for a_tag in soup.select("a.titreJob"):
        href = a_tag.get("href", "")
        if href:
            urls.append("https://www.rekrute.com" + href)

    return urls  # pas de set() ici, dédup à la fin


def crawl_all_pages(max_pages: int = 180) -> list[str]:
    all_urls = []

    for page in range(1, max_pages + 1):
        print(f"[*] Crawling page {page}/{max_pages}...")
        urls = get_offer_urls(page)

        if not urls:
            print(f"[✓] Fin détectée à la page {page}")
            break

        all_urls.extend(urls)
        print(f"    → {len(urls)} offres | Total : {len(all_urls)}")

        time.sleep(1.5)

    # Déduplication finale
    all_urls = list(set(all_urls))

    with open("offer_urls.json", "w", encoding="utf-8") as f:
        json.dump(all_urls, f, ensure_ascii=False, indent=2)

    print(f"\n[✓] {len(all_urls)} URLs uniques sauvegardées")
    return all_urls


if __name__ == "__main__":
    crawl_all_pages(max_pages=180)