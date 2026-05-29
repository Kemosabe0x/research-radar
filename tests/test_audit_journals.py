"""Tests for scripts/audit_journals.py classification helpers."""

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT / "scripts"))

from audit_journals import FixSuggestion, _classify  # noqa: E402


def test_classify_rss_ok_detail_is_entry_count() -> None:
    category, detail = _classify(
        rss_raw="https://example.com/feed.xml",
        rss_norm="https://example.com/feed.xml",
        web_norm="https://example.com/",
        rss_ok=True,
        rss_reason="ok",
        rss_entries=12,
        web_status="ok",
        fixes=[],
    )
    assert category == "rss_ok"
    assert detail == "12 entries"


def test_classify_rss_fixable_preserves_verified_fix_suffix_in_detail() -> None:
    rss_reason = "response is HTML, not RSS/Atom (check CSV feed URL)"
    fixes = [
        FixSuggestion(
            field="RSS Feed",
            current_value="https://bjsm.bmj.com/pages/rss-feeds",
            suggested_value="https://bjsm.bmj.com/rss/current.xml",
            reason="BMJ RSS index page; use /rss/current.xml feed",
            verified=True,
        )
    ]
    category, detail = _classify(
        rss_raw="https://bjsm.bmj.com/pages/rss-feeds",
        rss_norm="https://bjsm.bmj.com/pages/rss-feeds",
        web_norm="https://bjsm.bmj.com/",
        rss_ok=False,
        rss_reason=rss_reason,
        rss_entries=0,
        web_status="ok",
        fixes=fixes,
    )
    assert category == "rss_fixable"
    assert detail == rss_reason + " (verified fix available)"
    assert detail != rss_reason
