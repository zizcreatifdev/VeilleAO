"""Scraper joffres.net."""
import requests
from bs4 import BeautifulSoup

BASE_URL = "https://www.joffres.net"
LIST_URL = f"{BASE_URL}/senegal/appels-offres"


def scrape() -> list[dict]:
    resp = requests.get(LIST_URL, timeout=(5, 10), headers={"User-Agent": "Mozilla/5.0"})
    resp.raise_for_status()
    soup = BeautifulSoup(resp.text, "lxml")

    results = []
    # TODO: vérifier le sélecteur réel sur joffres.net
    for item in soup.select("div.offre, article.offre, li.offre-item, div.job"):
        link = item.find("a", href=True)
        if not link:
            continue
        href = link["href"]
        url = href if href.startswith("http") else BASE_URL + href
        title = link.get_text(strip=True)
        deadline_el = item.select_one(".date, .deadline, time")
        deadline = deadline_el.get_text(strip=True) if deadline_el else ""
        desc_el = item.select_one(".description, .resume, p")
        description = desc_el.get_text(strip=True)[:200] if desc_el else title[:200]
        results.append({
            "title": title,
            "url": url,
            "source": "JOffres",
            "date_published": "",
            "deadline": deadline,
            "budget": "",
            "description": description,
            "language": "fr",
        })
    return results
