"""Tests for all scrapers — mocked HTTP responses via responses library."""
import sys
from pathlib import Path

import pytest
import responses as resp_mock
import requests

sys.path.insert(0, str(Path(__file__).parent.parent / "scraper"))
from sources import dcmp, marches_sn, senoffre, joffres, pnud  # noqa: E402

FIXTURES = Path(__file__).parent / "fixtures"

AO_KEYS = {"title", "url", "source", "date_published", "deadline", "budget", "description", "language"}


def _fixture(name: str) -> str:
    return (FIXTURES / name).read_text()


# ── DCMP ─────────────────────────────────────────────────────────────────────

class TestDcmp:
    @resp_mock.activate
    def test_happy_path_returns_ao_list(self):
        resp_mock.add(resp_mock.GET, dcmp.LIST_URL, body=_fixture("dcmp_sample.html"), status=200)
        result = dcmp.scrape()
        assert isinstance(result, list)
        assert len(result) >= 1
        for ao in result:
            assert AO_KEYS.issubset(ao.keys()), f"Missing keys in AO: {ao}"
            assert ao["source"] == "DCMP"
            assert ao["url"].startswith("http")
            assert ao["language"] == "fr"

    @resp_mock.activate
    def test_403_raises_exception(self):
        resp_mock.add(resp_mock.GET, dcmp.LIST_URL, status=403)
        with pytest.raises(Exception):
            dcmp.scrape()

    @resp_mock.activate
    def test_429_raises_exception(self):
        resp_mock.add(resp_mock.GET, dcmp.LIST_URL, status=429)
        with pytest.raises(Exception):
            dcmp.scrape()

    @resp_mock.activate
    def test_503_raises_exception(self):
        resp_mock.add(resp_mock.GET, dcmp.LIST_URL, status=503)
        with pytest.raises(Exception):
            dcmp.scrape()

    @resp_mock.activate
    def test_timeout_raises_exception(self):
        resp_mock.add(resp_mock.GET, dcmp.LIST_URL, body=requests.exceptions.Timeout())
        with pytest.raises(Exception):
            dcmp.scrape()

    @resp_mock.activate
    def test_empty_html_returns_empty_list(self):
        resp_mock.add(resp_mock.GET, dcmp.LIST_URL, body="<html><body></body></html>", status=200)
        result = dcmp.scrape()
        assert result == []


# ── PNUD ─────────────────────────────────────────────────────────────────────

class TestPnud:
    @resp_mock.activate
    def test_happy_path_returns_ao_list(self):
        resp_mock.add(resp_mock.GET, pnud.HTML_URL, body=_fixture("pnud_sample.html"), status=200)
        result = pnud.scrape()
        assert isinstance(result, list)
        assert len(result) >= 1
        for ao in result:
            assert AO_KEYS.issubset(ao.keys())
            assert ao["source"] == "PNUD"
            assert ao["language"] == "en"

    @resp_mock.activate
    def test_403_raises_exception(self):
        resp_mock.add(resp_mock.GET, pnud.HTML_URL, status=403)
        with pytest.raises(Exception):
            pnud.scrape()

    @resp_mock.activate
    def test_timeout_raises_exception(self):
        resp_mock.add(resp_mock.GET, pnud.HTML_URL, body=requests.exceptions.Timeout())
        with pytest.raises(Exception):
            pnud.scrape()

    @resp_mock.activate
    def test_empty_html_returns_empty_list(self):
        resp_mock.add(resp_mock.GET, pnud.HTML_URL, body="<html><body></body></html>", status=200)
        result = pnud.scrape()
        assert result == []


# ── MarchesSN ────────────────────────────────────────────────────────────────

class TestMarchesSn:
    @resp_mock.activate
    def test_happy_path_returns_ao_list(self):
        resp_mock.add(resp_mock.GET, marches_sn.LIST_URL, body=_fixture("marches_sn_sample.html"), status=200)
        result = marches_sn.scrape()
        assert isinstance(result, list)
        assert len(result) >= 1
        for ao in result:
            assert AO_KEYS.issubset(ao.keys())
            assert ao["source"] == "MarchesSN"
            assert ao["language"] == "fr"

    @resp_mock.activate
    def test_403_raises_exception(self):
        resp_mock.add(resp_mock.GET, marches_sn.LIST_URL, status=403)
        with pytest.raises(Exception):
            marches_sn.scrape()

    @resp_mock.activate
    def test_timeout_raises_exception(self):
        resp_mock.add(resp_mock.GET, marches_sn.LIST_URL, body=requests.exceptions.Timeout())
        with pytest.raises(Exception):
            marches_sn.scrape()

    @resp_mock.activate
    def test_empty_html_returns_empty_list(self):
        resp_mock.add(resp_mock.GET, marches_sn.LIST_URL, body="<html><body></body></html>", status=200)
        result = marches_sn.scrape()
        assert result == []


# ── SenOffre ─────────────────────────────────────────────────────────────────

class TestSenOffre:
    @resp_mock.activate
    def test_happy_path_returns_ao_list(self):
        resp_mock.add(resp_mock.GET, senoffre.LIST_URL, body=_fixture("senoffre_sample.html"), status=200)
        result = senoffre.scrape()
        assert isinstance(result, list)
        assert len(result) >= 1
        for ao in result:
            assert AO_KEYS.issubset(ao.keys())
            assert ao["source"] == "SenOffre"

    @resp_mock.activate
    def test_403_raises_exception(self):
        resp_mock.add(resp_mock.GET, senoffre.LIST_URL, status=403)
        with pytest.raises(Exception):
            senoffre.scrape()

    @resp_mock.activate
    def test_timeout_raises_exception(self):
        resp_mock.add(resp_mock.GET, senoffre.LIST_URL, body=requests.exceptions.Timeout())
        with pytest.raises(Exception):
            senoffre.scrape()


# ── JOffres ──────────────────────────────────────────────────────────────────

class TestJOffres:
    @resp_mock.activate
    def test_happy_path_returns_ao_list(self):
        resp_mock.add(resp_mock.GET, joffres.LIST_URL, body=_fixture("joffres_sample.html"), status=200)
        result = joffres.scrape()
        assert isinstance(result, list)
        assert len(result) >= 1
        for ao in result:
            assert AO_KEYS.issubset(ao.keys())
            assert ao["source"] == "JOffres"

    @resp_mock.activate
    def test_403_raises_exception(self):
        resp_mock.add(resp_mock.GET, joffres.LIST_URL, status=403)
        with pytest.raises(Exception):
            joffres.scrape()

    @resp_mock.activate
    def test_timeout_raises_exception(self):
        resp_mock.add(resp_mock.GET, joffres.LIST_URL, body=requests.exceptions.Timeout())
        with pytest.raises(Exception):
            joffres.scrape()

    @resp_mock.activate
    def test_empty_html_returns_empty_list(self):
        resp_mock.add(resp_mock.GET, joffres.LIST_URL, body="<html><body></body></html>", status=200)
        result = joffres.scrape()
        assert result == []
