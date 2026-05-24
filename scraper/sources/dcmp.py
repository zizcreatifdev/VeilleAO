"""Scraper DCMP Sénégal (dcmp.sn).

NOTE: Vérifier manuellement avant déploiement que le sélecteur CSS est correct.
Si Cloudflare bloque, fallback vers armp.sn (voir config.ARMP_FALLBACK_URL).
"""
import requests
from bs4 import BeautifulSoup

BASE_URL = "https://www.dcmp.sn"
LIST_URL = f"{BASE_URL}/avis-et-appels-offres"


def scrape() -> list[dict]:
    resp = requests.get(LIST_URL, timeout=(5, 10), headers={"User-Agent": "Mozilla/5.0"})
    resp.raise_for_status()
    soup = BeautifulSoup(resp.text, "lxml")

    results = []
    # TODO: vérifier le sélecteur réel sur dcmp.sn après le premier run
    for row in soup.select("table.table tbody tr"):
        cells = row.find_all("td")
        if len(cells) < 3:
            continue
        link = row.find("a", href=True)
        if not link:
            continue
        href = link["href"]
        url = href if href.startswith("http") else BASE_URL + href
        results.append({
            "title": link.get_text(strip=True),
            "url": url,
            "source": "DCMP",
            "date_published": cells[0].get_text(strip=True) if cells else "",
            "deadline": cells[-1].get_text(strip=True) if len(cells) > 1 else "",
            "budget": "",
            "description": link.get_text(strip=True)[:200],
            "language": "fr",
        })
    return results
