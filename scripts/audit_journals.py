#!/usr/bin/env python3
"""
Live audit of Journals.csv active entries for RSSAgent ingestion readiness.

Uses the same fetch/validation logic as src/rssagent/feeds.py.
Rate-limited (2s between journals) to be polite to publishers.

Usage (from repo root, after pip install -e .):
    python scripts/audit_journals.py
    python scripts/audit_journals.py --output-json docs/journals-audit-raw.json
"""

from __future__ import annotations

import argparse
import csv
import json
import re
import sys
import time
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import urlparse

import pandas as pd
import requests
from bs4 import BeautifulSoup

# Allow running without install when repo root is on path
REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "src"))

from rssagent.feeds import DEFAULT_HEADERS, fetch_rss_feed  # noqa: E402
from rssagent.urls import is_valid_http_url, normalize_http_url  # noqa: E402

REQUEST_DELAY = 2.0
REQUEST_TIMEOUT = 15.0
CSV_FILE = REPO_ROOT / "Journals.csv"
REPORT_MD = REPO_ROOT / "docs" / "journals-audit.md"
FIXES_CSV = REPO_ROOT / "docs" / "journals-audit-fixes.csv"

ARTICLE_PATTERNS = ("/doi/", "/abs/", "/full/", "/article/", "/pdf/")


@dataclass
class FixSuggestion:
    field: str
    current_value: str
    suggested_value: str
    reason: str
    verified: bool = False


@dataclass
class JournalAudit:
    journal_name: str
    rss_raw: str
    website_raw: str
    rss_normalized: str
    website_normalized: str
    category: str
    rss_status: str
    rss_detail: str
    website_status: str
    website_detail: str
    entry_count: int = 0
    fixes: list[FixSuggestion] = field(default_factory=list)
    priority: str = "Medium"


def _cell_str(row: pd.Series, *columns: str) -> str:
    for col in columns:
        raw = row.get(col, "")
        if pd.isna(raw):
            continue
        text = str(raw).strip()
        if text and text.lower() not in ("nan", "none", "n/a", "(general website integration)"):
            return text
    return ""


def _needs_scheme_fix(raw: str) -> bool:
    if not raw:
        return False
    parsed = urlparse(raw.strip())
    return not parsed.scheme and bool(raw.strip())


def _is_truncated(raw: str) -> bool:
    return raw.rstrip().endswith("...")


def _extract_physiology_jc(url: str) -> str | None:
    m = re.search(r"/journal/([a-z0-9]+)", url, re.I)
    return m.group(1).lower() if m else None


def _extract_sage_jc(url: str) -> str | None:
    m = re.search(r"[?&]jc=([a-z0-9]+)", url, re.I)
    if m:
        return m.group(1).lower()
    m = re.search(r"/home/([a-z0-9]+)", url, re.I)
    return m.group(1).lower() if m else None


def _extract_tandf_jc(url: str) -> str | None:
    m = re.search(r"[?&]jc=([a-z0-9]+)", url, re.I)
    if m:
        return m.group(1).lower()
    m = re.search(r"/toc/([a-z0-9]+)/", url, re.I)
    return m.group(1).lower() if m else None


def _extract_springer_id(url: str) -> str | None:
    m = re.search(r"facet-journal-id=(\d+)", url, re.I)
    if m:
        return m.group(1)
    m = re.search(r"/journal/(\d+)", url, re.I)
    return m.group(1) if m else None


def _extract_bmj_feed(url: str) -> str | None:
    parsed = urlparse(url)
    if "bmj.com" not in parsed.netloc:
        return None
    host = parsed.netloc
    return f"https://{host}/rss/current.xml"


def _extract_wiley_issn(url: str) -> str | None:
    m = re.search(r"/feed/([0-9Xx]+)/", url, re.I)
    if m:
        return m.group(1).upper()
    m = re.search(r"/journal/([0-9x]+)", url, re.I)
    return m.group(1).upper() if m else None


def _extract_ojs_gateway(website: str) -> str | None:
    """OJS WebFeedGatewayPlugin pattern from journal site URL."""
    if not website:
        return None
    base = website.rstrip("/")
    if "index.php" in base:
        return f"{base}/gateway/plugin/WebFeedGatewayPlugin/rss2"
    return None


def _candidate_fixes(
    journal_name: str, rss_raw: str, rss_norm: str, web_norm: str, rss_reason: str
) -> list[FixSuggestion]:
    fixes: list[FixSuggestion] = []
    raw = rss_raw.strip()

    if raw and _needs_scheme_fix(raw):
        suggested = normalize_http_url(raw)
        fixes.append(
            FixSuggestion(
                field="RSS Feed",
                current_value=raw,
                suggested_value=suggested,
                reason="Missing https:// scheme; normalize_http_url prepends it",
            )
        )

    if _is_truncated(raw):
        fixes.append(
            FixSuggestion(
                field="RSS Feed",
                current_value=raw,
                suggested_value="",
                reason="URL appears truncated (...); restore full feed URL manually",
            )
        )

    reason_lower = rss_reason.lower()

    if "html" in reason_lower and "not rss" in reason_lower:
        if "bmj.com" in rss_norm or "pages/rss" in rss_norm:
            alt = _extract_bmj_feed(rss_norm or web_norm)
            if alt:
                fixes.append(
                    FixSuggestion(
                        field="RSS Feed",
                        current_value=raw,
                        suggested_value=alt,
                        reason="BMJ RSS index page; use /rss/current.xml feed",
                    )
                )
        if "physiology.org" in (rss_norm or web_norm):
            jc = _extract_physiology_jc(rss_norm or web_norm)
            if jc:
                alt = (
                    f"https://journals.physiology.org/action/showFeed"
                    f"?jc={jc}&type=etoc&feed=rss"
                )
                fixes.append(
                    FixSuggestion(
                        field="RSS Feed",
                        current_value=raw,
                        suggested_value=alt,
                        reason="Physiology.org journal landing page; use showFeed etoc RSS",
                    )
                )

    if rss_norm and "physiology.org/journal/" in rss_norm and "showFeed" not in rss_norm:
        jc = _extract_physiology_jc(rss_norm)
        if jc:
            alt = (
                f"https://journals.physiology.org/action/showFeed"
                f"?jc={jc}&type=etoc&feed=rss"
            )
            fixes.append(
                FixSuggestion(
                    field="RSS Feed",
                    current_value=raw,
                    suggested_value=alt,
                    reason="Journal page URL used instead of RSS showFeed endpoint",
                )
            )

    if "rupress.org" in (rss_norm or web_norm) and "physiology" in journal_name.lower():
        fixes.append(
            FixSuggestion(
                field="RSS Feed",
                current_value=raw,
                suggested_value=(
                    "https://journals.physiology.org/action/showFeed"
                    "?jc=jphysiol&type=etoc&feed=rss"
                ),
                reason="Wrong publisher domain (rupress/jgp); Journal of Physiology is on physiology.org",
            )
        )

    if web_norm and not raw:
        ojs = _extract_ojs_gateway(web_norm)
        if ojs:
            fixes.append(
                FixSuggestion(
                    field="RSS Feed",
                    current_value=raw,
                    suggested_value=ojs,
                    reason="OJS site detected; try WebFeedGatewayPlugin RSS",
                )
            )

    if web_norm and "springer.com/journal/" in web_norm and not raw:
        jid = re.search(r"/journal/(\d+)", web_norm)
        if jid:
            alt = f"https://link.springer.com/search.rss?facet-journal-id={jid.group(1)}"
            fixes.append(
                FixSuggestion(
                    field="RSS Feed",
                    current_value=raw,
                    suggested_value=alt,
                    reason="Springer journal site; standard search.rss pattern",
                )
            )

    if web_norm and "tandfonline.com/toc/" in web_norm and not raw:
        jc = _extract_tandf_jc(web_norm)
        if jc:
            alt = (
                f"https://www.tandfonline.com/action/showFeed"
                f"?jc={jc}&type=etoc&feed=rss"
            )
            fixes.append(
                FixSuggestion(
                    field="RSS Feed",
                    current_value=raw,
                    suggested_value=alt,
                    reason="Taylor & Francis journal; standard showFeed etoc pattern",
                )
            )

    if web_norm and "wiley.com/journal/" in web_norm and not raw:
        issn = _extract_wiley_issn(web_norm)
        if issn:
            alt = f"https://onlinelibrary.wiley.com/feed/{issn}/most-recent"
            fixes.append(
                FixSuggestion(
                    field="RSS Feed",
                    current_value=raw,
                    suggested_value=alt,
                    reason="Wiley journal site; standard /feed/{issn}/most-recent pattern",
                )
            )

    # Deduplicate by suggested_value
    seen: set[tuple[str, str]] = set()
    unique: list[FixSuggestion] = []
    for fix in fixes:
        key = (fix.field, fix.suggested_value)
        if key not in seen:
            seen.add(key)
            unique.append(fix)
    return unique


def _verify_fix(fix: FixSuggestion) -> bool:
    if not fix.suggested_value or fix.reason.startswith("URL appears truncated"):
        return False
    result = fetch_rss_feed(fix.suggested_value)
    return result.ok


def _check_website(website_url: str) -> tuple[str, str, int]:
    """Returns (status, detail, article_link_count)."""
    normalized = normalize_http_url(website_url)
    if not normalized or not is_valid_http_url(normalized):
        return "missing", "no valid website URL", 0

    try:
        response = requests.get(
            normalized,
            headers=DEFAULT_HEADERS,
            timeout=REQUEST_TIMEOUT,
            allow_redirects=True,
        )
        if response.status_code == 403:
            return "blocked", "HTTP 403 Forbidden", 0
        if response.status_code == 401:
            return "blocked", "HTTP 401 Unauthorized", 0
        if response.status_code == 429:
            return "blocked", "HTTP 429 Too Many Requests", 0
        response.raise_for_status()
    except requests.RequestException as e:
        err = str(e)
        if "403" in err:
            return "blocked", f"HTTP error: {e}", 0
        if "404" in err:
            return "broken", f"HTTP error: {e}", 0
        return "error", f"HTTP error: {e}", 0

    soup = BeautifulSoup(response.text, "html.parser")
    links = 0
    for a in soup.find_all("a", href=True):
        href = a["href"].lower()
        if any(p in href for p in ARTICLE_PATTERNS):
            links += 1
    if links:
        return "ok", f"found {links} article-like links", links
    return "no_articles", "page loads but no article-like links matched", 0


def _classify(
    rss_raw: str,
    rss_norm: str,
    web_norm: str,
    rss_ok: bool,
    rss_reason: str,
    rss_entries: int,
    web_status: str,
    fixes: list[FixSuggestion],
) -> tuple[str, str]:
    has_rss = bool(rss_norm and is_valid_http_url(rss_norm))
    has_web = bool(web_norm and is_valid_http_url(web_norm))

    if not has_rss and not has_web:
        return "no_usable_url", "Neither RSS nor website URL is fetchable"

    if rss_ok:
        return "rss_ok", f"{rss_entries} entries"

    verified_fix = any(f.verified for f in fixes)
    unverified_fix = bool(fixes) and not verified_fix

    if has_rss:
        reason_l = rss_reason.lower()
        fixable_signals = (
            "html" in reason_l and "not rss" in reason_l,
            "physiology.org/journal/" in rss_norm,
            "pages/rss" in rss_norm,
            _needs_scheme_fix(rss_raw),
            verified_fix,
            unverified_fix and any(f.suggested_value for f in fixes),
        )
        if verified_fix:
            return "rss_fixable", rss_reason + " (verified fix available)"
        if any(fixable_signals):
            return "rss_fixable", rss_reason

        if "403" in reason_l or "401" in reason_l or "429" in reason_l:
            if has_web and web_status == "ok":
                return "rss_broken_web_ok", rss_reason
            if has_web and web_status == "blocked":
                return "rss_broken_web_blocked", rss_reason
            return "rss_broken", rss_reason

        if has_web and web_status == "blocked":
            return "rss_broken_web_blocked", rss_reason

        return "rss_broken", rss_reason

    # No RSS URL in CSV
    if has_web:
        if web_status == "ok":
            return "no_rss_web_ok", "empty RSS; website fallback usable"
        if web_status == "blocked":
            return "no_rss_web_blocked", "empty RSS; website fallback blocked"
        if web_status == "no_articles":
            return "no_rss_web_weak", "empty RSS; website loads but scraper may find nothing"
        return "no_rss_web_error", f"empty RSS; website: {web_status}"

    return "no_usable_url", "RSS empty and website invalid"


def audit_journal(row: pd.Series, *, verify_fixes: bool = True) -> JournalAudit:
    name = str(row.get("Journal Name", "Unknown"))
    rss_raw = _cell_str(row, "RSS Feed")
    website_raw = _cell_str(row, "Website URL", "Website")
    priority = _cell_str(row, "Priority") or "Medium"
    rss_norm = normalize_http_url(rss_raw)
    web_norm = normalize_http_url(website_raw)

    rss_ok = False
    rss_reason = ""
    rss_entries = 0

    if rss_norm and is_valid_http_url(rss_norm):
        result = fetch_rss_feed(rss_norm)
        rss_ok = result.ok
        rss_reason = result.reason if not result.ok else "ok"
        if result.ok and result.feed is not None:
            rss_entries = len(result.feed.entries)
    elif rss_raw:
        rss_reason = f"invalid URL after normalize: {rss_raw!r}"
    else:
        rss_reason = "no RSS URL in CSV"

    fixes = _candidate_fixes(name, rss_raw, rss_norm, web_norm, rss_reason)

    # Verify fix candidates (one network call each for high-confidence)
    if verify_fixes:
        for fix in fixes:
            if fix.suggested_value and not fix.reason.startswith("URL appears truncated"):
                fix.verified = _verify_fix(fix)
                time.sleep(0.5)  # brief pause between fix probes

    web_status, web_detail, _ = _check_website(website_raw)

    category, detail = _classify(
        rss_raw, rss_norm, web_norm, rss_ok, rss_reason, rss_entries, web_status, fixes
    )

    return JournalAudit(
        journal_name=name,
        rss_raw=rss_raw,
        website_raw=website_raw,
        rss_normalized=rss_norm,
        website_normalized=web_norm,
        category=category,
        rss_status="ok" if rss_ok else "fail",
        rss_detail=detail if category == "rss_ok" else rss_reason,
        website_status=web_status,
        website_detail=web_detail,
        entry_count=rss_entries,
        fixes=fixes,
        priority=priority,
    )


def _category_label(cat: str) -> str:
    labels = {
        "rss_ok": "RSS OK",
        "rss_fixable": "RSS fixable",
        "rss_broken": "RSS broken / manual research",
        "rss_broken_web_ok": "RSS broken; website fallback OK",
        "rss_broken_web_blocked": "RSS broken; website fallback blocked",
        "no_rss_web_ok": "No RSS — website fallback OK",
        "no_rss_web_blocked": "No RSS — website fallback blocked",
        "no_rss_web_weak": "No RSS — website weak fallback",
        "no_rss_web_error": "No RSS — website error",
        "no_usable_url": "No usable URL",
    }
    return labels.get(cat, cat)


def write_report(audits: list[JournalAudit], generated_at: str) -> None:
    counts: dict[str, int] = {}
    for a in audits:
        counts[a.category] = counts.get(a.category, 0) + 1

    verified_fixes: list[tuple[JournalAudit, FixSuggestion]] = []
    unverified_fixes: list[tuple[JournalAudit, FixSuggestion]] = []
    for a in audits:
        for f in a.fixes:
            if f.verified and f.suggested_value:
                verified_fixes.append((a, f))
            elif f.suggested_value and not f.reason.startswith("URL appears truncated"):
                unverified_fixes.append((a, f))

    lines: list[str] = [
        "# Journals.csv ingestion audit",
        "",
        f"Generated: {generated_at}",
        "",
        "Live audit of every **Active** journal in `Journals.csv`, using the same",
        "validation rules as `src/rssagent/feeds.py` (`fetch_rss_feed`, URL normalization,",
        "HTML-vs-feed detection, website fallback link patterns).",
        "",
        "## How to re-run",
        "",
        "```bash",
        "pip install -e .",
        "python scripts/audit_journals.py",
        "```",
        "",
        "Optional: `--output-json docs/journals-audit-raw.json` saves machine-readable results.",
        "",
        "Rate limit: 2 seconds between journals (+ brief probes for suggested fixes).",
        "",
        "## Executive summary",
        "",
        f"**Active journals audited:** {len(audits)}",
        "",
        "| Category | Count |",
        "| --- | ---: |",
    ]

    category_order = [
        "rss_ok",
        "rss_fixable",
        "rss_broken_web_ok",
        "no_rss_web_ok",
        "rss_broken",
        "rss_broken_web_blocked",
        "no_rss_web_blocked",
        "no_rss_web_weak",
        "no_rss_web_error",
        "no_usable_url",
    ]
    for cat in category_order:
        if counts.get(cat):
            lines.append(f"| {_category_label(cat)} | {counts[cat]} |")
    for cat, n in sorted(counts.items()):
        if cat not in category_order:
            lines.append(f"| {_category_label(cat)} | {n} |")

    rss_ok = counts.get("rss_ok", 0)
    fixable = counts.get("rss_fixable", 0)
    web_only = counts.get("no_rss_web_ok", 0) + counts.get("rss_broken_web_ok", 0)
    blocked = (
        counts.get("rss_broken_web_blocked", 0)
        + counts.get("no_rss_web_blocked", 0)
        + counts.get("no_usable_url", 0)
    )
    manual = counts.get("rss_broken", 0)

    lines.extend(
        [
            "",
            "### Headline",
            "",
            f"- **{rss_ok}** journals have working RSS feeds ({100 * rss_ok // max(len(audits), 1)}%).",
            f"- **{fixable}** have fixable RSS URLs (scheme, wrong landing page, publisher pattern).",
            f"- **{web_only}** can fall back to website scraping today (no/broken RSS but site OK).",
            f"- **{manual + blocked}** need manual CSV research or are fully blocked.",
            f"- **{len(verified_fixes)}** high-confidence fixes verified live (see fixes CSV). "
            f"Applying them would raise working RSS from **{rss_ok} → ~{rss_ok + len(verified_fixes)}** "
            f"(~{100 * (rss_ok + len(verified_fixes)) // max(len(audits), 1)}%).",
            "",
            "### Projected impact after verified fixes",
            "",
            "Applying verified rows in `docs/journals-audit-fixes.csv` recovers journals currently "
            "classified as **RSS fixable** (wrong landing page, missing scheme, wrong publisher). "
            "Remaining gaps: LWW/Ovid HTML wrapper URLs, truncated blog feeds (`...`), empty RSS "
            "with weak websites, and publisher 403/404 feeds (OUP, MDPI, Cambridge).",
            "",
            "## Recommended actions (priority order)",
            "",
            "1. **Apply verified fixes** in `docs/journals-audit-fixes.csv` (prepend https, publisher feed URLs).",
            "2. **Fix truncated blog URLs** (rows ending in `...`) — restore full WordPress/blog feed paths.",
            "3. **Replace HTML landing pages** with real feed endpoints (BMJ `/rss/current.xml`, physiology.org `showFeed`, etc.).",
            "4. **Add OJS/Springer/T&F RSS** for journals with empty RSS but known publisher patterns.",
            "5. **Manual research** for 403/paywall/broken feeds where website fallback also fails.",
            "",
            "## Quick wins — verified RSS fixes",
            "",
        ]
    )

    if verified_fixes:
        lines.extend(
            ["| Journal | Field | Suggested value | Reason |", "| --- | --- | --- | --- |"]
        )
        for a, f in sorted(verified_fixes, key=lambda x: x[0].journal_name):
            lines.append(
                f"| {a.journal_name} | {f.field} | `{f.suggested_value}` | {f.reason} |"
            )
    else:
        lines.append("_None verified in this run._")

    lines.extend(["", "## Quick wins — unverified suggestions (test before applying)", ""])
    if unverified_fixes:
        lines.extend(
            ["| Journal | Field | Suggested value | Reason |", "| --- | --- | --- | --- |"]
        )
        for a, f in sorted(unverified_fixes, key=lambda x: x[0].journal_name):
            lines.append(
                f"| {a.journal_name} | {f.field} | `{f.suggested_value}` | {f.reason} |"
            )
    else:
        lines.append("_None._")

    def _section(title: str, items: list[JournalAudit]) -> None:
        lines.extend(["", f"## {title}", ""])
        if not items:
            lines.append("_None._")
            return
        for a in sorted(items, key=lambda x: x.journal_name):
            lines.append(f"### {a.journal_name}")
            lines.append(f"- **Category:** {_category_label(a.category)}")
            if a.rss_raw:
                lines.append(f"- **RSS (CSV):** `{a.rss_raw}`")
            else:
                lines.append("- **RSS (CSV):** _(empty)_")
            if a.website_raw:
                lines.append(f"- **Website:** `{a.website_raw}`")
            lines.append(f"- **RSS detail:** {a.rss_detail}")
            lines.append(f"- **Website:** {a.website_status} — {a.website_detail}")
            if a.fixes:
                lines.append("- **Suggested fixes:**")
                for f in a.fixes:
                    tag = "verified" if f.verified else "unverified"
                    if f.suggested_value:
                        lines.append(
                            f"  - [{tag}] `{f.field}` → `{f.suggested_value}` — {f.reason}"
                        )
                    else:
                        lines.append(f"  - [{tag}] `{f.field}` — {f.reason}")
            lines.append("")

    _section(
        "RSS fixable (CSV corrections likely)",
        [a for a in audits if a.category == "rss_fixable"],
    )
    _section(
        "No RSS — website fallback OK",
        [a for a in audits if a.category in ("no_rss_web_ok", "no_rss_web_weak")],
    )
    _section(
        "RSS broken — website fallback OK",
        [a for a in audits if a.category == "rss_broken_web_ok"],
    )
    _section(
        "Manual research / blocked",
        [
            a
            for a in audits
            if a.category
            in (
                "rss_broken",
                "rss_broken_web_blocked",
                "no_rss_web_blocked",
                "no_rss_web_error",
                "no_usable_url",
            )
        ],
    )

    lines.extend(
        [
            "",
            "## RSS OK (no action needed)",
            "",
            f"{rss_ok} journals. See raw JSON for full list if needed.",
            "",
        ]
    )
    for a in sorted(
        [x for x in audits if x.category == "rss_ok"], key=lambda x: x.journal_name
    ):
        lines.append(
            f"- **{a.journal_name}** — {a.entry_count} entries — `{a.rss_normalized}`"
        )

    REPORT_MD.parent.mkdir(parents=True, exist_ok=True)
    REPORT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")


def write_fixes_csv(audits: list[JournalAudit]) -> int:
    rows: list[dict[str, str]] = []
    seen_journals: set[str] = set()
    for a in audits:
        verified = [f for f in a.fixes if f.verified and f.suggested_value]
        for f in verified:
            rows.append(
                {
                    "Journal Name": a.journal_name,
                    "field": f.field,
                    "current_value": f.current_value,
                    "suggested_value": f.suggested_value,
                    "reason": f.reason,
                }
            )
            seen_journals.add(a.journal_name)
        if a.journal_name in seen_journals:
            continue
        for f in a.fixes:
            if (
                _needs_scheme_fix(f.current_value)
                and f.suggested_value
                and not _is_truncated(f.current_value)
            ):
                rows.append(
                    {
                        "Journal Name": a.journal_name,
                        "field": f.field,
                        "current_value": f.current_value,
                        "suggested_value": f.suggested_value,
                        "reason": f.reason
                        + " (scheme fix; feed may still need URL research)",
                    }
                )
                break

    if not rows:
        FIXES_CSV.write_text(
            "Journal Name,field,current_value,suggested_value,reason\n",
            encoding="utf-8",
        )
        return 0

    with FIXES_CSV.open("w", newline="", encoding="utf-8") as fh:
        writer = csv.DictWriter(
            fh,
            fieldnames=[
                "Journal Name",
                "field",
                "current_value",
                "suggested_value",
                "reason",
            ],
        )
        writer.writeheader()
        writer.writerows(rows)
    return len(rows)


def _audit_to_dict(a: JournalAudit) -> dict:
    d = asdict(a)
    d["fixes"] = [asdict(f) for f in a.fixes]
    return d


def _audit_from_dict(d: dict) -> JournalAudit:
    fixes = [FixSuggestion(**f) for f in d.get("fixes", [])]
    d = {k: v for k, v in d.items() if k != "fixes"}
    return JournalAudit(**d, fixes=fixes)


def _save_progress(path: Path, audits: list[JournalAudit]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps([_audit_to_dict(a) for a in audits], indent=2),
        encoding="utf-8",
    )


def main() -> int:
    parser = argparse.ArgumentParser(description="Audit Journals.csv for ingestion")
    parser.add_argument(
        "--output-json",
        type=Path,
        default=REPO_ROOT / "docs" / "journals-audit-raw.json",
        help="Write raw audit JSON here",
    )
    parser.add_argument(
        "--delay",
        type=float,
        default=REQUEST_DELAY,
        help="Seconds between journal checks",
    )
    parser.add_argument(
        "--resume",
        action="store_true",
        help="Skip journals already present in --output-json",
    )
    parser.add_argument(
        "--skip-fix-verify",
        action="store_true",
        help="Skip live verification of suggested fixes (faster)",
    )
    parser.add_argument(
        "--report-only",
        action="store_true",
        help="Regenerate markdown/CSV from existing --output-json (no network)",
    )
    args = parser.parse_args()

    if args.report_only:
        if not args.output_json.exists():
            print(f"No audit JSON at {args.output_json}", file=sys.stderr)
            return 1
        audits = [_audit_from_dict(d) for d in json.loads(args.output_json.read_text())]
        generated_at = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
        write_report(audits, generated_at)
        fix_rows = write_fixes_csv(audits)
        print(f"Report: {REPORT_MD}")
        print(f"Fixes CSV: {FIXES_CSV} ({fix_rows} rows)")
        return 0

    df = pd.read_csv(CSV_FILE)
    active = df[df["Tracking Status"] == "Active"]
    print(f"Auditing {len(active)} active journals from {CSV_FILE} ...")

    audits: list[JournalAudit] = []
    done_names: set[str] = set()
    if args.resume and args.output_json.exists():
        raw_existing = json.loads(args.output_json.read_text(encoding="utf-8"))
        audits = [_audit_from_dict(d) for d in raw_existing]
        done_names = {a.journal_name for a in audits}
        print(f"Resuming: {len(done_names)} journals already audited.")

    for i, (_, row) in enumerate(active.iterrows(), 1):
        name = str(row.get("Journal Name", "?"))
        if name in done_names:
            continue
        print(f"[{i}/{len(active)}] {name}", flush=True)
        audit = audit_journal(row, verify_fixes=not args.skip_fix_verify)
        audits.append(audit)
        _save_progress(args.output_json, audits)
        time.sleep(args.delay)

    generated_at = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    write_report(audits, generated_at)
    fix_rows = write_fixes_csv(audits)

    _save_progress(args.output_json, audits)

    counts: dict[str, int] = {}
    for a in audits:
        counts[a.category] = counts.get(a.category, 0) + 1

    print("\n=== Summary ===")
    for cat in sorted(counts, key=lambda c: -counts[c]):
        print(f"  {_category_label(cat)}: {counts[cat]}")
    print(f"\nReport: {REPORT_MD}")
    print(f"Fixes CSV: {FIXES_CSV} ({fix_rows} rows)")
    print(f"Raw JSON: {args.output_json}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
