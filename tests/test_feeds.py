from unittest.mock import MagicMock, patch

from rssagent.feeds import fetch_rss_feed, process_journal


def test_fetch_rss_rejects_html_landing_page() -> None:
    mock_resp = MagicMock()
    mock_resp.raise_for_status = MagicMock()
    mock_resp.headers = {"Content-Type": "text/html; charset=utf-8"}
    mock_resp.content = b"<html><body>RSS feeds</body></html>"

    with patch("rssagent.feeds.requests.get", return_value=mock_resp):
        result = fetch_rss_feed("https://example.com/rss-feeds")

    assert not result.ok
    assert "HTML" in result.reason


def test_process_journal_falls_back_when_rss_empty() -> None:
    mock_resp = MagicMock()
    mock_resp.raise_for_status = MagicMock()
    mock_resp.headers = {"Content-Type": "application/rss+xml"}
    mock_resp.content = b'<?xml version="1.0"?><rss><channel></channel></rss>'

    with patch("rssagent.feeds.requests.get", return_value=mock_resp):
        with patch("rssagent.feeds.fallback_scraper", return_value=2) as fallback:
            total = process_journal(
                "Test Journal",
                "https://example.com/feed",
                "https://example.com",
            )

    fallback.assert_called_once()
    assert total == 2
