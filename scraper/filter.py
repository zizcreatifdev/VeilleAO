import unicodedata


def _normalize(text: str) -> str:
    """NFD decomposition → strip diacritics → lowercase. 'Identité' → 'identite'."""
    nfd = unicodedata.normalize("NFD", text.lower())
    return "".join(c for c in nfd if unicodedata.category(c) != "Mn")


def filter_by_keywords(
    aos: list[dict],
    keywords_fr: list[str],
    keywords_en: list[str],
) -> list[dict]:
    """Return AOs whose title+description contain at least one keyword.

    FR keywords apply to all sources.
    EN keywords apply only to AOs with language='en'.
    """
    norm_kw_fr = [_normalize(k) for k in keywords_fr]
    norm_kw_en = [_normalize(k) for k in keywords_en]

    result = []
    for ao in aos:
        text = _normalize(ao.get("title", "") + " " + ao.get("description", ""))
        keywords = norm_kw_fr + (norm_kw_en if ao.get("language") == "en" else [])
        if any(kw in text for kw in keywords):
            result.append(ao)
    return result
