"""RSS parsing and fallback website scraping."""

from __future__ import annotations

import logging
from dataclasses import dataclass

import feedparser
import requests
from bs4 import BeautifulSoup

from rssagent import config
from rssagent.db import is_article_seen, save_article
from rssagent.notify import notify_new_article
from rssagent.urls import is_valid_http_url, normalize_http_url

logger = logging.getLogger(__name__)

DEFAULT_HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (compatible; RSSAgent/0.1; "
        "+https://github.com/Kemosabe0x/research-radar)"
    ),
    "Accept": "application/rss+xml, application/atom+xml, application/xml, text/xml, */*",
}


@dataclass(frozen=True)
class RssFetchResult:
    """Outcome of attempting to load an RSS/Atom feed."""

    ok: bool
    feed: feedparser.FeedParserDict | None = None
    reason: str = ""


def fetch_rss_feed(rss_url: str) -> RssFetchResult:
    """Fetch and parse a feed; does not process entries."""
    normalized = normalize_http_url(rss_url)
    if not normalized:
        return RssFetchResult(ok=False, reason="missing or invalid RSS URL")
    if not is_valid_http_url(normalized):
        return RssFetchResult(ok=False, reason=f"invalid URL: {rss_url!r}")

    try:
        response = requests.get(
            normalized,
            headers=DEFAULT_HEADERS,
            timeout=config.REQUEST_TIMEOUT,
            allow_redirects=True,
        )
        response.raise_for_status()
    except requests.RequestException as e:
        return RssFetchResult(ok=False, reason=f"HTTP error: {e}")

    content_type = (response.headers.get("Content-Type") or "").lower()
    body = response.content.lstrip()[:2048]
    looks_like_feed = body.startswith((b"<?xml", b"<rss", b"<feed", b"<rdf:RDF"))
    if "text/html" in content_type and not looks_like_feed:
        # Landing pages (e.g. "RSS feeds" index) are not feeds
        return RssFetchResult(
            ok=False,
            reason="response is HTML, not RSS/Atom (check CSV feed URL)",
        )

    feed = feedparser.parse(response.content)
    if feed.bozo and not feed.entries:
        exc = getattr(feed, "bozo_exception", None)
        return RssFetchResult(
            ok=False,
            feed=feed,
            reason=f"parse error with no entries: {exc}",
        )

    if not feed.entries:
        return RssFetchResult(ok=False, feed=feed, reason="feed returned zero entries")

    if feed.bozo:
        logger.warning(
            "Feed parsed with warnings (%s entries): %s",
            len(feed.entries),
            getattr(feed, "bozo_exception", "unknown"),
        )

    return RssFetchResult(ok=True, feed=feed)


def _process_entries(journal_name: str, feed: feedparser.FeedParserDict) -> int:
    new_count = 0
    for entry in feed.entries[: config.MAX_ENTRIES]:
        title = entry.get("title", "No Title")
        link = entry.get("link", "")
        published = entry.get("published", "")

        if not link:
            logger.warning("Skipping entry without link in %s", journal_name)
            continue

        if not is_article_seen(link):
            save_article(journal_name, title, link, published)
            notify_new_article(journal_name, title, link)
            new_count += 1
    return new_count


def try_rss_feed(journal_name: str, rss_url: str) -> tuple[int, bool]:
    """
    Fetch RSS and process entries.

    Returns (new_article_count, feed_was_usable).
    """
    result = fetch_rss_feed(rss_url)
    if not result.ok:
        logger.warning(
            "RSS not usable for %s (%s)",
            journal_name,
            result.reason,
        )
        return 0, False

    assert result.feed is not None
    try:
        return _process_entries(journal_name, result.feed), True
    except Exception as e:
        logger.error("Error processing RSS entries for %s: %s", journal_name, e)
        return 0, False


def process_rss_feed(journal_name: str, rss_url: str) -> int:
    """Parse an RSS feed; returns new article count (0 if feed unusable)."""
    count, _ = try_rss_feed(journal_name, rss_url)
    return count


def fallback_scraper(journal_name: str, website_url: str) -> int:
    """
    Generic fallback for journals without RSS.
    Finds links matching common academic URL patterns.
    """
    normalized = normalize_http_url(website_url)
    if not normalized or not is_valid_http_url(normalized):
        logger.warning("No valid website URL for %s, skipping fallback.", journal_name)
        return 0

    try:
        response = requests.get(
            normalized,
            headers=DEFAULT_HEADERS,
            timeout=config.REQUEST_TIMEOUT,
        )
        response.raise_for_status()
    except requests.RequestException as e:
        logger.error("Failed to fetch website for %s: %s", journal_name, e)
        return 0

    soup = BeautifulSoup(response.text, "html.parser")
    article_links: list[str] = []
    for a in soup.find_all("a", href=True):
        href = a["href"]
        if any(
            pattern in href.lower()
            for pattern in ("/doi/", "/abs/", "/full/", "/article/", "/pdf/")
        ):
            full_link = (
                href
                if href.startswith("http")
                else requests.compat.urljoin(normalized, href)
            )
            article_links.append(full_link)

    seen_links: set[str] = set()
    new_count = 0
    for link in article_links[: config.MAX_ENTRIES]:
        if link in seen_links:
            continue
        seen_links.add(link)

        if not is_article_seen(link):
            title = f"Article from {journal_name} (scraped)"
            save_article(journal_name, title, link, "")
            notify_new_article(journal_name, title, link)
            new_count += 1

    logger.info(
        "Fallback scraper found %s new articles for %s", new_count, journal_name
    )
    return new_count


def process_journal(journal_name: str, rss_url: str, website_url: str) -> int:
    """
    Try RSS first; on missing/invalid/failed feed, fall back to the journal website.
    """
    rss_normalized = normalize_http_url(rss_url)
    web_normalized = normalize_http_url(website_url)

    if not rss_normalized and not web_normalized:
        logger.warning("No RSS or website URL for %s, skipping.", journal_name)
        return 0

    total = 0
    rss_ok = False

    if rss_normalized and is_valid_http_url(rss_normalized):
        new, rss_ok = try_rss_feed(journal_name, rss_normalized)
        total += new
    elif rss_normalized:
        logger.warning(
            "Invalid RSS URL for %s (%r), will try website if available.",
            journal_name,
            rss_url,
        )

    if rss_ok:
        return total

    if web_normalized:
        if rss_normalized:
            logger.info("Using website fallback for %s", journal_name)
        return total + fallback_scraper(journal_name, web_normalized)

    if rss_normalized:
        logger.warning(
            "RSS failed for %s and no website URL for fallback.", journal_name
        )
    return total
