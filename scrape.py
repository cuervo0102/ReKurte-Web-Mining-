# scraper.py
import requests
from bs4 import BeautifulSoup
import json
import time
import re

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                  "AppleWebKit/537.36 (KHTML, like Gecko) "
                  "Chrome/120.0.0.0 Safari/537.36"
}

def extract_label(soup, label: str) -> str:
    for li in soup.select("ul.featureInfo li"):
        text = li.get_text(strip=True)
        if label.lower() in text.lower():
            return text.split(":")[-1].strip()
    return None


def scrape_offer(url: str) -> dict:
    try:
        response = requests.get(url, headers=HEADERS, timeout=10)
        if response.status_code != 200:
            return {}

        soup = BeautifulSoup(response.text, "html.parser")

        titre_tag = soup.select_one("h1")
        titre = titre_tag.get_text(strip=True) if titre_tag else None

        h2_tag = soup.select_one("h2.h2italic")
        fonction_secteur = h2_tag.get_text(strip=True) if h2_tag else None

        experience  = extract_label(soup, "Experience")
        niveau      = extract_label(soup, "Niveau d'etude")
        contrat     = extract_label(soup, "Type de contrat")
        teletravail = extract_label(soup, "Teletravail")
        postes      = extract_label(soup, "Poste")
        region      = extract_label(soup, "Region")

        desc_tag = soup.select_one("div.col-md-12.info.blc.noback")
        description = desc_tag.get_text(strip=True) if desc_tag else None

        ville_match = re.search(
            r'(casablanca|rabat|marrakech|tanger|agadir|fes|meknes|oujda|kenitra|tetouan)',
            url.lower()
        )
        ville = ville_match.group(1).capitalize() if ville_match else None

        entreprise_match = re.search(r'-recrutement-(.+?)-(?:casablanca|rabat|marrakech|tanger|agadir|fes|meknes|oujda|kenitra|tetouan)', url.lower())
        entreprise = entreprise_match.group(1).replace("-", " ").title() if entreprise_match else None

        return {
            "url": url,
            "titre": titre,
            "entreprise": entreprise,
            "ville": ville,
            "fonction_secteur": fonction_secteur,
            "experience": experience,
            "niveau_etude": niveau,
            "contrat": contrat,
            "teletravail": teletravail,
            "postes": postes,
            "region": region,
            "description": description,
        }

    except Exception as e:
        print(f" Erreur : {e}")
        return {}


def scrape_all():
    with open("offer_urls.json", "r", encoding="utf-8") as f:
        urls = json.load(f)

    print(f"[*] {len(urls)} offres a scraper...")
    results = []
    errors  = []

    for i, url in enumerate(urls):
        print(f"[{i+1}/{len(urls)}] {url.split('/')[-1][:60]}")
        data = scrape_offer(url)

        if data and data.get("titre"):
            results.append(data)
        else:
            errors.append(url)

        if (i + 1) % 100 == 0:
            with open("offers_raw.json", "w", encoding="utf-8") as f:
                json.dump(results, f, ensure_ascii=False, indent=2)
            print(f"Checkpoint : {len(results)} offres sauvegardees")

        time.sleep(1.2)

    with open("offers_raw.json", "w", encoding="utf-8") as f:
        json.dump(results, f, ensure_ascii=False, indent=2)

    with open("errors.json", "w") as f:
        json.dump(errors, f, ensure_ascii=False, indent=2)

    print(f" {len(results)} offres sauvegardees dans offers_raw.json")
    print(f" {len(errors)} erreurs dans errors.json")


if __name__ == "__main__":
    scrape_all()