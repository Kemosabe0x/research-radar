"""SQLite persistence for seen articles."""

from __future__ import annotations

import logging
import sqlite3
from datetime import datetime, timedelta, timezone
from typing import Any

from rssagent import config

logger = logging.getLogger(__name__)


def setup_database() -> None:
    """Create the seen_articles table if it doesn't exist."""
    conn = sqlite3.connect(config.DB_FILE)
    cursor = conn.cursor()
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS seen_articles (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            journal_name TEXT,
            article_title TEXT,
            article_link TEXT UNIQUE,
            published_date TEXT,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP
        )
        """
    )
    _ensure_column(cursor, "seen_articles", "created_at", "TEXT")
    cursor.execute(
        """
        UPDATE seen_articles
        SET created_at = COALESCE(created_at, CURRENT_TIMESTAMP)
        WHERE created_at IS NULL OR created_at = ''
        """
    )
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS article_processing (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            article_link TEXT UNIQUE,
            journal_name TEXT,
            article_title TEXT,
            published_date TEXT,
            alert_summary TEXT,
            synthesis TEXT,
            status TEXT,
            provider TEXT,
            model TEXT,
            error TEXT,
            article_path TEXT,
            digest_path TEXT,
            updated_at TEXT DEFAULT CURRENT_TIMESTAMP
        )
        """
    )
    conn.commit()
    conn.close()
    logger.info("Database setup complete.")


def _ensure_column(cursor: sqlite3.Cursor, table: str, column: str, ddl: str) -> None:
    cursor.execute(f"PRAGMA table_info({table})")
    columns = {row[1] for row in cursor.fetchall()}
    if column not in columns:
        cursor.execute(f"ALTER TABLE {table} ADD COLUMN {column} {ddl}")


def is_article_seen(link: str) -> bool:
    """Return True if this article link is already in the database."""
    conn = sqlite3.connect(config.DB_FILE)
    cursor = conn.cursor()
    cursor.execute("SELECT 1 FROM seen_articles WHERE article_link = ?", (link,))
    result = cursor.fetchone()
    conn.close()
    return result is not None


def save_article(
    journal_name: str, title: str, link: str, published_date: str
) -> None:
    """Insert a new article into the database."""
    conn = sqlite3.connect(config.DB_FILE)
    cursor = conn.cursor()
    cursor.execute(
        """
        INSERT INTO seen_articles (journal_name, article_title, article_link, published_date)
        VALUES (?, ?, ?, ?)
        """,
        (journal_name, title, link, published_date),
    )
    conn.commit()
    conn.close()
    logger.info("Saved new article: %s... from %s", title[:50], journal_name)


def upsert_article_processing(
    *,
    article_link: str,
    journal_name: str,
    article_title: str,
    published_date: str,
    status: str,
    alert_summary: str = "",
    synthesis: str = "",
    provider: str = "",
    model: str = "",
    error: str = "",
    article_path: str = "",
    digest_path: str = "",
) -> None:
    """Create or update processing state for an article."""
    conn = sqlite3.connect(config.DB_FILE)
    cursor = conn.cursor()
    cursor.execute(
        """
        INSERT INTO article_processing (
            article_link, journal_name, article_title, published_date, alert_summary,
            synthesis, status, provider, model, error, article_path, digest_path, updated_at
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
        ON CONFLICT(article_link) DO UPDATE SET
            journal_name=excluded.journal_name,
            article_title=excluded.article_title,
            published_date=excluded.published_date,
            alert_summary=excluded.alert_summary,
            synthesis=excluded.synthesis,
            status=excluded.status,
            provider=excluded.provider,
            model=excluded.model,
            error=excluded.error,
            article_path=excluded.article_path,
            digest_path=excluded.digest_path,
            updated_at=CURRENT_TIMESTAMP
        """,
        (
            article_link,
            journal_name,
            article_title,
            published_date,
            alert_summary,
            synthesis,
            status,
            provider,
            model,
            error,
            article_path,
            digest_path,
        ),
    )
    conn.commit()
    conn.close()


def count_recent_articles(hours: int) -> int:
    """Count recently inserted articles for generation threshold checks."""
    cutoff = (datetime.now(timezone.utc) - timedelta(hours=hours)).strftime("%Y-%m-%d %H:%M:%S")
    conn = sqlite3.connect(config.DB_FILE)
    cursor = conn.cursor()
    cursor.execute(
        "SELECT COUNT(*) FROM seen_articles WHERE datetime(created_at) >= datetime(?)",
        (cutoff,),
    )
    count = int(cursor.fetchone()[0])
    conn.close()
    return count


def count_generated_today() -> int:
    """How many article generation records were completed today."""
    conn = sqlite3.connect(config.DB_FILE)
    cursor = conn.cursor()
    cursor.execute(
        """
        SELECT COUNT(*)
        FROM article_processing
        WHERE status = 'generated'
          AND date(updated_at) = date('now')
        """
    )
    count = int(cursor.fetchone()[0])
    conn.close()
    return count


def get_recent_articles(limit: int = 50) -> list[dict[str, Any]]:
    """Return latest articles with processing status metadata."""
    conn = sqlite3.connect(config.DB_FILE)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute(
        """
        SELECT
            s.journal_name,
            s.article_title,
            s.article_link,
            s.published_date,
            s.created_at,
            p.status,
            p.alert_summary,
            p.synthesis,
            p.provider,
            p.model,
            p.error,
            p.article_path,
            p.digest_path,
            p.updated_at AS processing_updated_at
        FROM seen_articles s
        LEFT JOIN article_processing p ON p.article_link = s.article_link
        ORDER BY datetime(s.created_at) DESC
        LIMIT ?
        """,
        (limit,),
    )
    rows = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return rows


def get_article_by_link(link: str) -> dict[str, Any] | None:
    """Lookup a single seen article by URL."""
    conn = sqlite3.connect(config.DB_FILE)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute(
        """
        SELECT journal_name, article_title, article_link, published_date
        FROM seen_articles
        WHERE article_link = ?
        """,
        (link,),
    )
    row = cursor.fetchone()
    conn.close()
    return dict(row) if row else None
