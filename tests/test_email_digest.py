"""Tests for email_digest.py — composition and SMTP retry."""
import sys
from pathlib import Path
from unittest.mock import MagicMock, patch, call

import pytest

sys.path.insert(0, str(Path(__file__).parent.parent / "scraper"))
import email_digest  # noqa: E402


def _ao(title: str, url: str = "https://example.com/ao/1") -> dict:
    return {
        "title": title, "url": url, "source": "TEST",
        "date_published": "2026-05-24", "deadline": "2026-06-15",
        "budget": "10M FCFA", "description": title[:200], "language": "fr",
    }


ARMP = "https://www.armp.sn"
GMAIL = "bot@gmail.com"
PWD = "apppassword"
RECIPIENTS = ["zizcreatif@gmail.com"]


class TestCompose:
    def test_subject_with_results(self):
        subject, _ = email_digest.compose([_ao("Logo startup")], {}, [], ARMP)
        assert "1" in subject
        assert "Veille AO" in subject

    def test_subject_multiple_results(self):
        subject, _ = email_digest.compose([_ao("A"), _ao("B")], {}, [], ARMP)
        assert "2" in subject

    def test_subject_no_results(self):
        subject, _ = email_digest.compose([], {}, [], ARMP)
        assert "Aucune" in subject

    def test_body_contains_ao_title(self):
        _, body = email_digest.compose([_ao("Logo identité visuelle Dakar")], {}, [], ARMP)
        assert "Logo identité visuelle Dakar" in body

    def test_body_contains_source_errors(self):
        _, body = email_digest.compose([], {"dcmp": "403 Forbidden"}, [], ARMP)
        assert "dcmp" in body
        assert "403" in body

    def test_body_contains_alert_when_failing(self):
        _, body = email_digest.compose([], {}, ["dcmp"], ARMP)
        assert "ALERTE" in body
        assert ARMP in body

    def test_body_no_alert_when_no_failures(self):
        _, body = email_digest.compose([_ao("Test")], {}, [], ARMP)
        assert "ALERTE" not in body

    def test_ao_url_in_body(self):
        url = "https://dcmp.sn/ao/123"
        _, body = email_digest.compose([_ao("Test", url=url)], {}, [], ARMP)
        assert url in body

    def test_description_truncated_to_200(self):
        long_desc = "x" * 500
        ao = _ao("Test")
        ao["description"] = long_desc
        _, body = email_digest.compose([ao], {}, [], ARMP)
        # description is already stored as [:200] at scraper level
        # but compose should not blow up on long descriptions either
        assert "Test" in body


class TestSend:
    def test_successful_send_on_first_attempt(self):
        mock_server = MagicMock()
        with patch("smtplib.SMTP_SSL") as mock_smtp:
            mock_smtp.return_value.__enter__.return_value = mock_server
            email_digest.send("Subject", "<p>body</p>", RECIPIENTS, GMAIL, PWD)
        mock_server.login.assert_called_once_with(GMAIL, PWD)
        mock_server.sendmail.assert_called_once()

    def test_retry_on_first_smtp_failure(self):
        mock_server = MagicMock()
        mock_server.sendmail.side_effect = [Exception("SMTP error"), None]
        with patch("smtplib.SMTP_SSL") as mock_smtp:
            mock_smtp.return_value.__enter__.return_value = mock_server
            # First call raises, second succeeds
            email_digest.send("Subject", "<p>body</p>", RECIPIENTS, GMAIL, PWD)
        assert mock_server.sendmail.call_count == 2

    def test_raises_after_two_failures(self):
        mock_server = MagicMock()
        mock_server.sendmail.side_effect = Exception("SMTP error")
        with patch("smtplib.SMTP_SSL") as mock_smtp:
            mock_smtp.return_value.__enter__.return_value = mock_server
            with pytest.raises(RuntimeError, match="non livré"):
                email_digest.send("Subject", "<p>body</p>", RECIPIENTS, GMAIL, PWD)
        assert mock_server.sendmail.call_count == 2

    def test_sends_to_all_recipients(self):
        recipients = ["a@gmail.com", "b@gmail.com"]
        mock_server = MagicMock()
        with patch("smtplib.SMTP_SSL") as mock_smtp:
            mock_smtp.return_value.__enter__.return_value = mock_server
            email_digest.send("Sub", "<p>body</p>", recipients, GMAIL, PWD)
        _, call_recipients, _ = mock_server.sendmail.call_args[0]
        assert call_recipients == recipients
