import hashlib
import json
import os
from datetime import datetime, timedelta, timezone
from urllib.parse import urlparse, parse_qsl, urlencode, urlunparse

_TRACKING_PARAMS = frozenset({
    "utm_source", "utm_medium", "utm_campaign", "utm_content", "utm_term",
    "fbclid", "gclid", "msclkid", "ref", "_ga",
})

_EMPTY_STATE: dict = {
    "seen": {},
    "last_run": None,
    "source_failures": {},
}


def normalize_url(url: str) -> str:
    """Canonical form: https, no trailing slash, sorted params, strip trackers."""
    parsed = urlparse(url.strip())
    scheme = "https"
    netloc = parsed.netloc.lower()
    path = parsed.path.rstrip("/") or "/"
    params = sorted(
        (k, v) for k, v in parse_qsl(parsed.query)
        if k not in _TRACKING_PARAMS
    )
    query = urlencode(params)
    return urlunparse((scheme, netloc, path, "", query, ""))


def compute_hash(url: str) -> str:
    return hashlib.sha256(normalize_url(url).encode()).hexdigest()


def load_state(state_path: str) -> dict:
    if not os.path.exists(state_path):
        return dict(_EMPTY_STATE)
    try:
        with open(state_path) as f:
            data = json.load(f)
        # ensure all expected keys exist (forward-compat for older state files)
        for key, default in _EMPTY_STATE.items():
            if key not in data:
                data[key] = type(default)()
        return data
    except (json.JSONDecodeError, OSError):
        return dict(_EMPTY_STATE)


def save_state(state: dict, state_path: str) -> None:
    os.makedirs(os.path.dirname(state_path) if os.path.dirname(state_path) else ".", exist_ok=True)
    with open(state_path, "w") as f:
        json.dump(state, f, indent=2, ensure_ascii=False)


def filter_new(aos: list[dict], state: dict) -> list[dict]:
    """Return only AOs not yet in state['seen']. Update state in-place."""
    now = datetime.now(timezone.utc).isoformat()
    new = []
    for ao in aos:
        h = compute_hash(ao["url"])
        if h not in state["seen"]:
            state["seen"][h] = now
            new.append(ao)
    return new


def purge_old_entries(state: dict, max_age_days: int = 30) -> None:
    """Remove hashes older than max_age_days from state['seen']."""
    cutoff = datetime.now(timezone.utc) - timedelta(days=max_age_days)
    to_delete = []
    for h, ts in state["seen"].items():
        try:
            if datetime.fromisoformat(ts) < cutoff:
                to_delete.append(h)
        except (ValueError, TypeError):
            to_delete.append(h)  # malformed timestamp — purge it
    for h in to_delete:
        del state["seen"][h]


def mark_source_success(state: dict, source: str) -> None:
    state["source_failures"][source] = 0


def mark_source_failure(state: dict, source: str) -> None:
    current = state["source_failures"].get(source, 0)
    state["source_failures"][source] = current + 1


def sources_above_threshold(state: dict, threshold: int) -> list[str]:
    return [
        s for s, count in state["source_failures"].items()
        if count >= threshold
    ]
