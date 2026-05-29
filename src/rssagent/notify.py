"""Alert notifications (console and optional webhook)."""

import logging

import requests

from rssagent import config
from rssagent.generation import enqueue_article_processing

logger = logging.getLogger(__name__)


def notify_new_article(
    journal_name: str, title: str, link: str, published_date: str = ""
) -> None:
    """Log a new article and optionally POST to NOTIFICATION_WEBHOOK_URL."""
    message = f"🚨 NEW STUDY | {journal_name} | {title}\nLink: {link}\n"
    logger.info(message)

    # Non-blocking generation path: queue async digestion regardless of webhook setup.
    enqueue_article_processing(
        journal_name=journal_name,
        title=title,
        link=link,
        published_date=published_date,
    )

    if config.WEBHOOK_URL:
        try:
            payload = {"text": f"New from {journal_name}: {title}\n{link}"}
            response = requests.post(config.WEBHOOK_URL, json=payload, timeout=5)
            response.raise_for_status()
            logger.info("Notification sent to webhook.")
        except Exception as e:
            logger.error("Failed to send webhook notification: %s", e)
