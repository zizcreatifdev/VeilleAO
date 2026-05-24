# TODOS

## Pending

### SendGrid migration (if Gmail fails in prod)
**What:** Replace Gmail SMTP with SendGrid free tier (100 emails/day) in `email_digest.py`.
**Why:** Gmail App Passwords can be silently blocked by Google from shared cloud IPs (GitHub Actions egress). If the first days in prod show zero email delivery, this is the fix.
**Pros:** API REST, no IP-based blocking, free up to 100/day, simple 5-line API call replaces smtplib.
**Cons:** New dependency (sendgrid), new API key to manage in GH Actions Secrets.
**Context:** Decision D9 during /plan-eng-review. Gmail + retry + GH Actions logging is the V1 approach. This TODO is the prepared Plan B. Files to change: `scraper/email_digest.py` (replace `smtplib` block with `sendgrid.SendGridAPIClient`), `requirements.txt` (add `sendgrid`), `.github/workflows/veille-ao.yml` (add `SENDGRID_API_KEY` secret).
**Depends on:** Test Gmail for 3-7 days in prod first.

### Filter precision improvement (after week 1 evaluation)
**What:** Add an exclusion keyword list and title-first weighting to `filter.py`.
**Why:** "communication" matches AOs for telecom equipment, medical procurement, and IT systems that mention "communication strategy" in boilerplate. The <30% false positive success criterion may not be met with pure keyword presence matching.
**Pros:** Reduces email noise, higher signal:noise ratio, more useful daily digest.
**Cons:** Risk of excluding valid AOs if exclusion list is too aggressive. Requires 1 week of real data to calibrate.
**Context:** Surfaced during outside voice review (D finding #4). Start by evaluating week 1 results manually: tag each item as TP/FP. If FP rate >30%, implement: (1) NEGATIVE_KEYWORDS list in config.py, (2) title-match weighted 2x over description match.
**Depends on:** 7 days of prod data.
