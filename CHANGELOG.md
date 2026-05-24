# Changelog

## [1.0.0] — 2026-05-24

### Added
- **5 scrapers** (DCMP, PNUD Sénégal, marchesdusenegal.com, senoffre.com, joffres.net) with `timeout=(5, 10)` on all HTTP calls
- **Keyword filter** (`filter.py`) — French keywords applied to all sources, English keywords to `language="en"` sources only; NFD accent normalization + case folding
- **URL deduplication** (`dedup.py`) — SHA256 on normalized URL (https upgrade, trailing-slash strip, query sort, utm_* removal); 30-day retention via `purge_old_entries()`
- **state.json persistence** — `seen` hashes + `source_failures` counter + `last_run` timestamp in a single file; committed after each run via GitHub Actions `[skip ci]`
- **Email digest** (`email_digest.py`) — HTML digest with SMTP retry (×1) and explicit GH Actions stderr log on failure; alert section when a source exceeds `SOURCE_FAIL_THRESHOLD` (3 consecutive failures) with ARMP fallback link
- **GitHub Actions workflow** (`.github/workflows/veille-ao.yml`) — daily cron `0 7 * * *` (7h UTC / Dakar), `permissions: contents: write`, `workflow_dispatch` for manual runs
- **67 tests** across 4 suites (`test_filter`, `test_dedup`, `test_sources`, `test_email_digest`) with mocked HTTP via `responses` library; 78% overall coverage
- **TODOS.md** — tracked plan-B items: SendGrid fallback + filter precision improvement after week-1 data
