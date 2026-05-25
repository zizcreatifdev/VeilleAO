# TODOS

## Pending

### SendGrid migration (if Gmail fails in prod)
**What:** Replace Gmail SMTP with SendGrid free tier (100 emails/day) in `email_digest.py`.
**Why:** Gmail App Passwords can be silently blocked by Google from shared cloud IPs (GitHub Actions egress). If the first days in prod show zero email delivery, this is the fix.
**Pros:** API REST, no IP-based blocking, free up to 100/day, simple 5-line API call replaces smtplib.
**Cons:** New dependency (sendgrid), new API key to manage in GH Actions Secrets.
**Context:** Decision D9 during /plan-eng-review. Gmail + retry + GH Actions logging is the V1 approach. This TODO is the prepared Plan B. Files to change: `scraper/email_digest.py` (replace `smtplib` block with `sendgrid.SendGridAPIClient`), `requirements.txt` (add `sendgrid`), `.github/workflows/veille-ao.yml` (add `SENDGRID_API_KEY` secret).
**Depends on:** Test Gmail for 3-7 days in prod first.

### Resend quota upgrade (quand > 80 agences actives)
**What:** Passer du plan Resend gratuit (100 emails/jour) au plan payant ($20/mois, 50 000 emails/jour).
**Why:** À 80 agences actives, le digest quotidien (80 emails) + les emails transactionnels dépassent la limite gratuite. Emails non-livrés = clients non-nourris = churn.
**Pros:** $20/mois est négligeable avec 80 clients à 25k FCFA/mois. L'upgrade prend 2 minutes dans le dashboard Resend.
**Cons:** Aucun — coût très faible, upgrade triviale.
**Context:** Le seuil de déclenchement est 80 agences actives. En dessous, le plan gratuit suffit. À surveiller dans le dashboard Resend (quota visible).
**Depends on:** Aucun prérequis. Upgrade à chaud sans downtime.

### Supabase write key restriction (post-10 clients actifs)
**What:** Créer un rôle PostgreSQL restreint pour le scraper (`GRANT INSERT ON appels_offres ONLY`) au lieu d'utiliser la SUPABASE_SERVICE_KEY.
**Why:** La service_role key donne accès complet à la DB. Si le repo devient public, vecteur d'injection de données malveillantes dans le feed de toutes les agences.
**Pros:** Principe du moindre privilège. La clé scraper ne peut qu'insérer des AOs, pas modifier des paiements ou des agencies.
**Cons:** Supabase ne supporte pas nativement les clés API scoped par rôle — nécessite un workaround (anon key + RLS policy ou JWT custom).
**Context:** En V1 avec un repo privé, le risque est faible. À implémenter avant d'ouvrir le repo en open-source.
**Depends on:** Décision d'open-sourcer le repo.

### Filter precision improvement (after week 1 evaluation)
**What:** Add an exclusion keyword list and title-first weighting to `filter.py`.
**Why:** "communication" matches AOs for telecom equipment, medical procurement, and IT systems that mention "communication strategy" in boilerplate. The <30% false positive success criterion may not be met with pure keyword presence matching.
**Pros:** Reduces email noise, higher signal:noise ratio, more useful daily digest.
**Cons:** Risk of excluding valid AOs if exclusion list is too aggressive. Requires 1 week of real data to calibrate.
**Context:** Surfaced during outside voice review (D finding #4). Start by evaluating week 1 results manually: tag each item as TP/FP. If FP rate >30%, implement: (1) NEGATIVE_KEYWORDS list in config.py, (2) title-match weighted 2x over description match.
**Depends on:** 7 days of prod data.
