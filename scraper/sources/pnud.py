"""Scraper PNUD Sénégal via API procurement-notices.undp.org.

NOTE: Tester l'endpoint manuellement si des changements de structure surviennent.
L'API peut être instable — tout changement de structure retourne [] sans crash.
"""
import requests

API_URL = "https://procurement-notices.undp.org/view_negotiation.cfm"
# Fallback HTML si l'API JSON n'est pas disponible
HTML_URL = "https://procurement-notices.undp.org/view_notices.cfm?filter_country=SN"


def scrape() -> list[dict]:
    resp = requests.get(
        HTML_URL,
        timeout=(5, 10),
        headers={"User-Agent": "Mozilla/5.0"},
    )
    resp.raise_for_status()

    from bs4 import BeautifulSoup
    soup = BeautifulSoup(resp.text, "lxml")

    results = []
    # TODO: vérifier le sélecteur réel sur procurement-notices.undp.org
    for row in soup.select("table.table tbody tr, tr.negTableRow"):
        cells = row.find_all("td")
        if not cells:
            continue
        link = row.find("a", href=True)
        if not link:
            continue
        href = link["href"]
        url = href if href.startswith("http") else "https://procurement-notices.undp.org/" + href
        results.append({
            "title": link.get_text(strip=True),
            "url": url,
            "source": "PNUD",
            "date_published": cells[0].get_text(strip=True) if cells else "",
            "deadline": cells[-1].get_text(strip=True) if len(cells) > 2 else "",
            "budget": "",
            "description": link.get_text(strip=True)[:200],
            "language": "en",
        })
    return results
