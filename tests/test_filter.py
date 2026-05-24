"""Tests for filter.py — keyword matching with accent and case normalization."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "scraper"))
import filter as ao_filter  # noqa: E402

KW_FR = ["communication", "branding", "identité visuelle", "logo", "charte graphique", "réseaux sociaux", "stratégie digitale"]
KW_EN = ["branding", "logo design", "website"]


def _ao(title="", description="", language="fr", url="https://example.com/ao/1") -> dict:
    return {
        "title": title, "description": description, "language": language,
        "url": url, "source": "TEST", "date_published": "", "deadline": "", "budget": "",
    }


class TestNormalization:
    def test_accent_in_keyword_matches_plain_text(self):
        aos = [_ao(title="conception identite visuelle ministere")]
        result = ao_filter.filter_by_keywords(aos, KW_FR, KW_EN)
        assert len(result) == 1

    def test_accented_text_matches_plain_keyword(self):
        # keyword is "logo", text has no accents issue but tests normalization path
        aos = [_ao(title="LOGO et charte graphique — startup")]
        result = ao_filter.filter_by_keywords(aos, KW_FR, KW_EN)
        assert len(result) == 1

    def test_uppercase_title_matches(self):
        aos = [_ao(title="COMMUNICATION VISUELLE CAMPAGNE")]
        result = ao_filter.filter_by_keywords(aos, KW_FR, KW_EN)
        assert len(result) == 1

    def test_mixed_case_and_accents(self):
        aos = [_ao(title="Identité Visuelle — Projet PAPNBG")]
        result = ao_filter.filter_by_keywords(aos, KW_FR, KW_EN)
        assert len(result) == 1

    def test_keyword_in_description_matched(self):
        aos = [_ao(title="Prestation de service", description="conception logo et branding")]
        result = ao_filter.filter_by_keywords(aos, KW_FR, KW_EN)
        assert len(result) == 1

    def test_no_match_returns_empty(self):
        aos = [_ao(title="Fourniture matériel informatique"), _ao(title="Travaux BTP route")]
        result = ao_filter.filter_by_keywords(aos, KW_FR, KW_EN)
        assert result == []

    def test_partial_match_returns_only_matching(self):
        aos = [
            _ao(title="Logo startup Dakar", url="https://example.com/ao/1"),
            _ao(title="Audit comptable exercice 2025", url="https://example.com/ao/2"),
            _ao(title="Stratégie digitale réseaux sociaux", url="https://example.com/ao/3"),
        ]
        result = ao_filter.filter_by_keywords(aos, KW_FR, KW_EN)
        assert len(result) == 2
        titles = {r["title"] for r in result}
        assert "Audit comptable exercice 2025" not in titles


class TestLanguageFiltering:
    def test_en_keywords_applied_to_en_source(self):
        aos = [_ao(title="Website development for NGO", language="en")]
        result = ao_filter.filter_by_keywords(aos, KW_FR, KW_EN)
        assert len(result) == 1

    def test_en_keywords_not_applied_to_fr_source(self):
        # "website" is EN only; FR source should not match on EN-only keyword
        # unless the word also appears in KW_FR (it doesn't here)
        kw_fr_no_web = ["communication", "branding", "identité visuelle", "logo"]
        kw_en = ["website development"]
        aos = [_ao(title="website développement", language="fr")]
        result = ao_filter.filter_by_keywords(aos, kw_fr_no_web, kw_en)
        assert result == []

    def test_fr_keywords_always_applied(self):
        aos = [_ao(title="Design branding campaign", language="en")]
        result = ao_filter.filter_by_keywords(aos, KW_FR, KW_EN)
        assert len(result) == 1  # "branding" is in both FR and EN lists
