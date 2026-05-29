"""SQLite persistence for seen articles."""

import logging
import sqlite3

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
            published_date TEXT
        )
        """
    )
    conn.commit()
    conn.close()
    logger.info("Database setup complete.")


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
