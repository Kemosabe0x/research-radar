"""Asynchronous digestion and conditional generation pipeline."""

from __future__ import annotations

import json
import logging
import re
from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path

from rssagent import config
from rssagent.db import (
    count_generated_today,
    count_recent_articles,
    upsert_article_processing,
)
from rssagent.llm.router import complete

logger = logging.getLogger(__name__)

_EXECUTOR = ThreadPoolExecutor(max_workers=2, thread_name_prefix="rssagent-llm")


@dataclass(frozen=True)
class GenerationDecision:
    """Decision output for generation trigger checks."""

    should_generate: bool
    reason: str


def should_generate_for_article(journal_name: str) -> GenerationDecision:
    """Evaluate threshold-driven generation rules."""
    if journal_name in config.PRIORITY_GENERATION_JOURNALS:
        return GenerationDecision(True, "priority journal override")

    if count_generated_today() >= config.GENERATE_DAILY_CAP:
        return GenerationDecision(False, "daily generation cap reached")

    recent_articles = count_recent_articles(config.GENERATE_WINDOW_HOURS)
    if recent_articles < config.GENERATE_MIN_NEW_ARTICLES:
        return GenerationDecision(
            False,
            (
                f"recent volume below threshold "
                f"({recent_articles} < {config.GENERATE_MIN_NEW_ARTICLES})"
            ),
        )

    return GenerationDecision(True, "volume threshold met")


def enqueue_article_processing(
    *, journal_name: str, title: str, link: str, published_date: str
) -> None:
    """Queue async processing so alert delivery never blocks."""
    if not config.ENABLE_ALERT_DIGESTION:
        return
    _EXECUTOR.submit(
        _process_article,
        journal_name=journal_name,
        title=title,
        link=link,
        published_date=published_date,
    )


def _slugify(text: str) -> str:
    slug = re.sub(r"[^a-zA-Z0-9]+", "-", text.lower()).strip("-")
    return slug[:80] or "article"


def _frontmatter(data: dict[str, object]) -> str:
    lines = ["---"]
    for key, value in data.items():
        if isinstance(value, (dict, list)):
            encoded = json.dumps(value, ensure_ascii=True)
            lines.append(f"{key}: {encoded}")
        else:
            escaped = str(value).replace("\n", " ").strip()
            lines.append(f"{key}: {escaped}")
    lines.append("---")
    return "\n".join(lines)


def _write_article_markdown(
    *,
    journal_name: str,
    title: str,
    link: str,
    published_date: str,
    provider: str,
    model: str,
    synthesis: str,
    generated_text: str,
) -> str:
    config.ARTICLES_DIR.mkdir(parents=True, exist_ok=True)
    stamp = datetime.now(timezone.utc).strftime("%Y%m%d-%H%M%S")
    filename = f"{stamp}-{_slugify(title)}.md"
    path = config.ARTICLES_DIR / filename
    fm = _frontmatter(
        {
            "title": title,
            "sources": [
                {"journal": journal_name, "url": link, "published": published_date or ""}
            ],
            "provider": provider,
            "model": model,
            "generated_at": datetime.now(timezone.utc).isoformat(),
            "kind": "article",
        }
    )
    path.write_text(f"{fm}\n\n## Synthesis\n\n{synthesis}\n\n## Draft\n\n{generated_text}\n")
    return str(path.relative_to(config.REPO_ROOT))


def _upsert_daily_digest(
    *,
    journal_name: str,
    title: str,
    link: str,
    provider: str,
    model: str,
    synthesis: str,
) -> str:
    config.DIGESTS_DIR.mkdir(parents=True, exist_ok=True)
    date_str = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    path = config.DIGESTS_DIR / f"{date_str}.md"
    fm = _frontmatter(
        {
            "title": f"Daily Digest {date_str}",
            "sources": [{"journal": journal_name, "url": link}],
            "provider": provider,
            "model": model,
            "generated_at": datetime.now(timezone.utc).isoformat(),
            "kind": "digest",
        }
    )
    entry = (
        f"\n### {title}\n\n"
        f"- Journal: {journal_name}\n"
        f"- Link: {link}\n"
        f"- Synthesis: {synthesis}\n"
    )
    if path.exists():
        path.write_text(path.read_text() + entry)
    else:
        path.write_text(f"{fm}\n\n## Highlights\n{entry}")
    return str(path.relative_to(config.REPO_ROOT))


def _process_article(
    *,
    journal_name: str,
    title: str,
    link: str,
    published_date: str,
) -> None:
    upsert_article_processing(
        article_link=link,
        journal_name=journal_name,
        article_title=title,
        published_date=published_date,
        status="pending",
    )

    alert_prompt = [
        {
            "role": "system",
            "content": (
                "Write a concise one-sentence research alert summary for sports-science users."
            ),
        },
        {
            "role": "user",
            "content": f"Journal: {journal_name}\nTitle: {title}\nLink: {link}",
        },
    ]
    digest_result = complete(task="alert", messages=alert_prompt)
    if not digest_result.ok:
        upsert_article_processing(
            article_link=link,
            journal_name=journal_name,
            article_title=title,
            published_date=published_date,
            status="skipped",
            error=digest_result.error,
        )
        return

    upsert_article_processing(
        article_link=link,
        journal_name=journal_name,
        article_title=title,
        published_date=published_date,
        status="digested",
        alert_summary=digest_result.text,
        provider=digest_result.provider,
        model=digest_result.model,
    )

    decision = should_generate_for_article(journal_name)
    if not decision.should_generate:
        logger.info("Skipping generation for %s: %s", journal_name, decision.reason)
        return

    synth_result = complete(
        task="synthesize",
        messages=[
            {
                "role": "system",
                "content": "Extract a short synthesis (themes, relevance, audience impact).",
            },
            {"role": "user", "content": f"Journal: {journal_name}\nTitle: {title}\nLink: {link}"},
        ],
    )
    if not synth_result.ok:
        upsert_article_processing(
            article_link=link,
            journal_name=journal_name,
            article_title=title,
            published_date=published_date,
            status="digested",
            alert_summary=digest_result.text,
            error=synth_result.error,
            provider=digest_result.provider,
            model=digest_result.model,
        )
        return

    gen_result = complete(
        task="generate",
        messages=[
            {
                "role": "system",
                "content": (
                    "Write a concise markdown brief for coaches: context, practical takeaway, caveat."
                ),
            },
            {
                "role": "user",
                "content": (
                    f"Journal: {journal_name}\nTitle: {title}\n"
                    f"Link: {link}\nSynthesis: {synth_result.text}"
                ),
            },
        ],
    )
    if not gen_result.ok:
        upsert_article_processing(
            article_link=link,
            journal_name=journal_name,
            article_title=title,
            published_date=published_date,
            status="digested",
            alert_summary=digest_result.text,
            synthesis=synth_result.text,
            error=gen_result.error,
            provider=synth_result.provider,
            model=synth_result.model,
        )
        return

    article_path = _write_article_markdown(
        journal_name=journal_name,
        title=title,
        link=link,
        published_date=published_date,
        provider=gen_result.provider,
        model=gen_result.model,
        synthesis=synth_result.text,
        generated_text=gen_result.text,
    )
    digest_path = _upsert_daily_digest(
        journal_name=journal_name,
        title=title,
        link=link,
        provider=gen_result.provider,
        model=gen_result.model,
        synthesis=synth_result.text,
    )
    upsert_article_processing(
        article_link=link,
        journal_name=journal_name,
        article_title=title,
        published_date=published_date,
        status="generated",
        alert_summary=digest_result.text,
        synthesis=synth_result.text,
        provider=gen_result.provider,
        model=gen_result.model,
        article_path=article_path,
        digest_path=digest_path,
    )
