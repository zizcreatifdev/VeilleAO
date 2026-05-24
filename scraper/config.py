import os

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
