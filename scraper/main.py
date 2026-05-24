"""Orchestrateur principal — veille AO communication/branding Sénégal.

Politique d'erreur :
- Erreur par source → log + continue + incrémente source_failures
- Toutes sources en échec → email dégradé envoyé quand même
- Crash global (config manquante, import error) → email système envoyé puis re-raise
"""
import os
import sys
from datetime import datetime, timezone
from pathlib import Path

import config
import dedup
import email_digest
import filter as ao_filter
from sources import dcmp, joffres, marches_sn, pnud, senoffre

STATE_PATH = Path(__file__).parent / "state.json"

SCRAPERS = {
    "dcmp": dcmp.scrape,
    "pnud": pnud.scrape,
    "marches_sn": marches_sn.scrape,
    "senoffre": senoffre.scrape,
    "joffres": joffres.scrape,
}


def _send_system_error(error_msg: str) -> None:
    """Last-resort email when the script itself crashes. Never raises."""
    try:
        subject = f"[Veille AO] ERREUR SYSTÈME — {datetime.now(timezone.utc).date()}"
        body = f"<html><body><p>Le script a planté :<br><pre>{error_msg}</pre></p></body></html>"
        email_digest.send(subject, body, config.RECIPIENTS, config.GMAIL_USER, config.GMAIL_APP_PASSWORD)
    except Exception as exc:
        print(f"[main] Impossible d'envoyer l'email système : {exc}", file=sys.stderr)


def run() -> None:
    state = dedup.load_state(str(STATE_PATH))
    source_errors: dict[str, str] = {}
    all_aos: list[dict] = []

    for name, scrape_fn in SCRAPERS.items():
        try:
            raw = scrape_fn()
            filtered = ao_filter.filter_by_keywords(raw, config.KEYWORDS_FR, config.KEYWORDS_EN)
            all_aos.extend(filtered)
            dedup.mark_source_success(state, name)
            print(f"[{name}] {len(raw)} AOs bruts → {len(filtered)} après filtrage")
        except Exception as exc:
            dedup.mark_source_failure(state, name)
            source_errors[name] = str(exc)
            print(f"[{name}] ERREUR : {exc}", file=sys.stderr)

    new_aos = dedup.filter_new(all_aos, state)
    dedup.purge_old_entries(state)
    state["last_run"] = datetime.now(timezone.utc).isoformat()

    failing = dedup.sources_above_threshold(state, config.SOURCE_FAIL_THRESHOLD)
    subject, body = email_digest.compose(new_aos, source_errors, failing, config.ARMP_FALLBACK_URL)
    email_digest.send(subject, body, config.RECIPIENTS, config.GMAIL_USER, config.GMAIL_APP_PASSWORD)

    dedup.save_state(state, str(STATE_PATH))
    print(f"[main] {len(new_aos)} nouveaux AOs envoyés. State sauvegardé.")


if __name__ == "__main__":
    try:
        if not config.GMAIL_USER or not config.GMAIL_APP_PASSWORD:
            raise EnvironmentError(
                "GMAIL_USER et GMAIL_APP_PASSWORD doivent être définis en variables d'environnement"
            )
        run()
    except Exception as exc:
        _send_system_error(str(exc))
        sys.exit(1)
