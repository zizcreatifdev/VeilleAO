import os
import json
from pathlib import Path

# SYNC keywords with web/app/page.tsx theme definitions
KEYWORDS_FR = [
    "communication", "branding", "identite visuelle", "identité visuelle",
    "charte graphique", "design packaging", "packaging design",
    "creation site web", "création site web", "developpement web", "développement web",
    "refonte site", "logo", "identite de marque", "identité de marque",
    "agence de communication", "campagne de sensibilisation",
    "publicite", "publicité", "strategie digitale", "stratégie digitale",
    "reseaux sociaux", "réseaux sociaux", "communication visuelle",
]

KEYWORDS_EN = [
    "communication", "branding", "logo design", "brand identity",
    "website development", "web development", "packaging design",
    "digital strategy", "social media", "awareness campaign",
    "visual identity", "graphic design",
]

RECIPIENTS = ["zizcreatif@gmail.com"]

SOURCE_FAIL_THRESHOLD = 3   # alert email after N consecutive failures
ARMP_FALLBACK_URL = "https://www.armp.sn"

GMAIL_USER = os.environ.get("GMAIL_USER", "")
GMAIL_APP_PASSWORD = os.environ.get("GMAIL_APP_PASSWORD", "")

SOURCES = ["dcmp", "pnud", "marches_sn", "senoffre", "joffres"]


def load_config():
    """Load config.json from repo root; return None if not found."""
    config_path = Path(__file__).parent.parent / "config.json"
    if not config_path.exists():
        return None
    try:
        with open(config_path, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return None


def get_active_sources():
    """Return list of active source ids from config.json, falling back to SOURCES."""
    cfg = load_config()
    if cfg and "sources" in cfg:
        return [s["id"] for s in cfg["sources"] if s.get("active", True)]
    return SOURCES


def get_source_url(source_id):
    """Return configured URL for a source id, or None if not in config.json."""
    cfg = load_config()
    if cfg and "sources" in cfg:
        for s in cfg["sources"]:
            if s["id"] == source_id:
                return s.get("url")
    return None


def get_keywords():
    """Return merged keyword lists from active themes in config.json, falling back to defaults."""
    cfg = load_config()
    if not cfg or "themes" not in cfg:
        return KEYWORDS_FR, KEYWORDS_EN

    kw_fr, kw_en = [], []
    for theme in cfg["themes"]:
        if theme.get("active", False):
            kw_fr.extend(theme.get("keywords_fr", []))
            kw_en.extend(theme.get("keywords_en", []))

    if not kw_fr and not kw_en:
        return KEYWORDS_FR, KEYWORDS_EN

    return list(dict.fromkeys(kw_fr)), list(dict.fromkeys(kw_en))


def get_recipients():
    """Return recipients from config.json, falling back to RECIPIENTS."""
    cfg = load_config()
    if cfg and cfg.get("recipients"):
        return cfg["recipients"]
    return RECIPIENTS
