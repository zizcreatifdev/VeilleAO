"""Email digest composition and delivery.

Retry policy: 1 retry on SMTP failure.
On both failures: log to stdout (visible in GH Actions) and raise.
"""
import smtplib
import sys
from datetime import date
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText


def _build_subject(new_aos: list[dict]) -> str:
    today = date.today().strftime("%d %B %Y")
    if new_aos:
        return f"[Veille AO] {len(new_aos)} nouvelle(s) opportunité(s) — {today}"
    return f"[Veille AO] Aucune nouvelle opportunité — {today}"


def _build_html(
    new_aos: list[dict],
    source_errors: dict[str, str],
    failing_sources: list[str],
    armp_url: str,
) -> str:
    lines = ["<html><body>"]
    lines.append("<h2>NOUVELLES OPPORTUNITÉS COMMUNICATION / BRANDING</h2>")
    lines.append("<hr>")

    if new_aos:
        for i, ao in enumerate(new_aos, 1):
            lines.append(f"<p><strong>{i}. [{ao['source']}] {ao['title']}</strong><br>")
            if ao.get("deadline"):
                lines.append(f"Date limite : {ao['deadline']}<br>")
            if ao.get("budget"):
                lines.append(f"Budget estimé : {ao['budget']}<br>")
            if ao.get("description"):
                lines.append(f"{ao['description'][:200]}<br>")
            lines.append(f"<a href=\"{ao['url']}\">Voir l'appel d'offres</a></p>")
    else:
        lines.append("<p>Aucune nouvelle opportunité aujourd'hui.</p>")

    if source_errors:
        lines.append("<hr><h3>Sources en erreur</h3><ul>")
        for src, err in source_errors.items():
            lines.append(f"<li><strong>{src}</strong> : {err}</li>")
        lines.append("</ul>")

    if failing_sources:
        lines.append("<hr>")
        lines.append(
            f"<p style='color:red'><strong>⚠ ALERTE :</strong> "
            f"Les sources suivantes sont en échec depuis plusieurs jours : "
            f"{', '.join(failing_sources)}.<br>"
            f"Vérification manuelle recommandée : "
            f"<a href='{armp_url}'>{armp_url}</a></p>"
        )

    sources_ok = [s for s in ["DCMP", "PNUD", "MarchesSN", "SenOffre", "JOffres"]
                  if s not in source_errors]
    sources_ko = list(source_errors.keys())
    status_parts = [f"{s} ✓" for s in sources_ok] + [f"{s} ✗" for s in sources_ko]
    lines.append(f"<hr><small>Sources : {' | '.join(status_parts)}</small>")
    lines.append("</body></html>")
    return "\n".join(lines)


def compose(
    new_aos: list[dict],
    source_errors: dict[str, str],
    failing_sources: list[str],
    armp_url: str,
) -> tuple[str, str]:
    """Return (subject, html_body). Pure function — no side effects."""
    return _build_subject(new_aos), _build_html(new_aos, source_errors, failing_sources, armp_url)


def send(
    subject: str,
    html_body: str,
    recipients: list[str],
    gmail_user: str,
    gmail_password: str,
) -> None:
    """Send email via Gmail SMTP. Retries once on failure."""
    msg = MIMEMultipart("alternative")
    msg["Subject"] = subject
    msg["From"] = gmail_user
    msg["To"] = ", ".join(recipients)
    msg.attach(MIMEText(html_body, "html", "utf-8"))

    last_exc: Exception | None = None
    for attempt in range(2):
        try:
            with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
                server.login(gmail_user, gmail_password)
                server.sendmail(gmail_user, recipients, msg.as_string())
            print(f"[email_digest] Email envoyé à {recipients} (tentative {attempt + 1})")
            return
        except Exception as exc:
            last_exc = exc
            print(
                f"[email_digest] SMTP échec tentative {attempt + 1}: {exc}",
                file=sys.stderr,
            )

    print(
        f"[email_digest] ÉCHEC DÉFINITIF — email non livré. Vérifier Gmail App Password "
        f"ou envisager migration SendGrid (voir TODOS.md).",
        file=sys.stderr,
    )
    raise RuntimeError(f"Email non livré après 2 tentatives: {last_exc}") from last_exc
