"""Tests for dedup.py — URL normalization, hashing, dedup, purge, failure tracking."""
import json
import sys
import tempfile
from datetime import datetime, timedelta, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "scraper"))
import dedup  # noqa: E402

FIXTURES = Path(__file__).parent / "fixtures"


def _ao(url: str, title: str = "Test AO") -> dict:
    return {
        "title": title, "url": url, "source": "TEST",
        "date_published": "", "deadline": "", "budget": "",
        "description": title[:200], "language": "fr",
    }


class TestUrlNormalization:
    def test_http_forced_to_https(self):
        assert dedup.normalize_url("http://example.com/ao/1") == "https://example.com/ao/1"

    def test_trailing_slash_removed(self):
        assert dedup.normalize_url("https://example.com/ao/1/") == "https://example.com/ao/1"

    def test_root_path_preserved(self):
        result = dedup.normalize_url("https://example.com/")
        assert result == "https://example.com/"

    def test_query_params_sorted(self):
        url1 = dedup.normalize_url("https://example.com/ao?z=3&a=1")
        url2 = dedup.normalize_url("https://example.com/ao?a=1&z=3")
        assert url1 == url2

    def test_utm_params_stripped(self):
        url = dedup.normalize_url("https://example.com/ao/1?id=123&utm_source=newsletter&utm_medium=email")
        assert "utm_source" not in url
        assert "utm_medium" not in url
        assert "id=123" in url

    def test_fbclid_stripped(self):
        url = dedup.normalize_url("https://example.com/ao/1?fbclid=abc123")
        assert "fbclid" not in url

    def test_same_ao_different_tracking_same_hash(self):
        h1 = dedup.compute_hash("https://dcmp.sn/ao/123?utm_source=linkedin")
        h2 = dedup.compute_hash("https://dcmp.sn/ao/123?utm_medium=email")
        assert h1 == h2

    def test_http_vs_https_same_hash(self):
        h1 = dedup.compute_hash("http://dcmp.sn/ao/123")
        h2 = dedup.compute_hash("https://dcmp.sn/ao/123")
        assert h1 == h2

    def test_trailing_slash_same_hash(self):
        h1 = dedup.compute_hash("https://dcmp.sn/ao/123/")
        h2 = dedup.compute_hash("https://dcmp.sn/ao/123")
        assert h1 == h2


class TestFilterNew:
    def test_new_ao_included_and_written_to_state(self):
        state = {"seen": {}, "last_run": None, "source_failures": {}}
        aos = [_ao("https://example.com/ao/new1")]
        result = dedup.filter_new(aos, state)
        assert len(result) == 1
        assert len(state["seen"]) == 1

    def test_already_seen_ao_excluded(self):
        url = "https://example.com/ao/existing"
        h = dedup.compute_hash(url)
        state = {
            "seen": {h: datetime.now(timezone.utc).isoformat()},
            "last_run": None, "source_failures": {},
        }
        result = dedup.filter_new([_ao(url)], state)
        assert result == []

    def test_mixed_new_and_seen(self):
        new_url = "https://example.com/ao/new"
        seen_url = "https://example.com/ao/seen"
        h_seen = dedup.compute_hash(seen_url)
        state = {
            "seen": {h_seen: datetime.now(timezone.utc).isoformat()},
            "last_run": None, "source_failures": {},
        }
        result = dedup.filter_new([_ao(new_url), _ao(seen_url)], state)
        assert len(result) == 1
        assert result[0]["url"] == new_url

    def test_http_url_deduplicated_with_https_seen(self):
        url_https = "https://example.com/ao/123"
        url_http = "http://example.com/ao/123"
        h = dedup.compute_hash(url_https)
        state = {"seen": {h: datetime.now(timezone.utc).isoformat()}, "last_run": None, "source_failures": {}}
        result = dedup.filter_new([_ao(url_http)], state)
        assert result == []


class TestStateIO:
    def test_load_creates_empty_state_if_missing(self, tmp_path):
        path = str(tmp_path / "state.json")
        state = dedup.load_state(path)
        assert state["seen"] == {}
        assert state["source_failures"] == {}

    def test_load_reads_existing_state(self):
        state = dedup.load_state(str(FIXTURES / "state_with_seen.json"))
        assert len(state["seen"]) == 5
        assert state["source_failures"]["dcmp"] == 2

    def test_load_handles_corrupted_file(self, tmp_path):
        path = tmp_path / "state.json"
        path.write_text("not valid json {{{")
        state = dedup.load_state(str(path))
        assert state == {"seen": {}, "last_run": None, "source_failures": {}}

    def test_save_and_reload(self, tmp_path):
        path = str(tmp_path / "state.json")
        state = {"seen": {"abc": "2026-05-24T00:00:00+00:00"}, "last_run": None, "source_failures": {}}
        dedup.save_state(state, path)
        reloaded = dedup.load_state(path)
        assert reloaded["seen"] == state["seen"]


class TestPurge:
    def test_old_entries_purged(self):
        state = dedup.load_state(str(FIXTURES / "state_with_seen.json"))
        initial_count = len(state["seen"])
        dedup.purge_old_entries(state, max_age_days=30)
        assert len(state["seen"]) < initial_count

    def test_recent_entries_kept(self):
        now = datetime.now(timezone.utc).isoformat()
        state = {
            "seen": {"abc": now, "def": now},
            "last_run": now, "source_failures": {},
        }
        dedup.purge_old_entries(state, max_age_days=30)
        assert len(state["seen"]) == 2

    def test_malformed_timestamp_purged(self):
        state = {
            "seen": {"bad_ts": "not-a-date"},
            "last_run": None, "source_failures": {},
        }
        dedup.purge_old_entries(state)
        assert len(state["seen"]) == 0


class TestFailureTracking:
    def test_mark_failure_increments(self):
        state = {"seen": {}, "last_run": None, "source_failures": {}}
        dedup.mark_source_failure(state, "dcmp")
        dedup.mark_source_failure(state, "dcmp")
        assert state["source_failures"]["dcmp"] == 2

    def test_mark_success_resets_to_zero(self):
        state = {"seen": {}, "last_run": None, "source_failures": {"dcmp": 5}}
        dedup.mark_source_success(state, "dcmp")
        assert state["source_failures"]["dcmp"] == 0

    def test_sources_above_threshold(self):
        state = {
            "seen": {}, "last_run": None,
            "source_failures": {"dcmp": 4, "pnud": 1, "senoffre": 3},
        }
        failing = dedup.sources_above_threshold(state, threshold=3)
        assert "dcmp" in failing
        assert "senoffre" in failing
        assert "pnud" not in failing
