"""Journal polling loop and scheduler entrypoint."""

import argparse
import logging
import os
import time

import pandas as pd
import schedule

from rssagent import config
from rssagent.db import setup_database
from rssagent.feeds import process_journal

logger = logging.getLogger(__name__)


def _cell_str(row: pd.Series, *columns: str) -> str:
    """First non-empty CSV column value."""
    for col in columns:
        raw = row.get(col, "")
        if pd.isna(raw):
            continue
        text = str(raw).strip()
        if text and text.lower() not in ("nan", "none"):
            return text
    return ""


def check_journals() -> None:
    """Load Journals.csv and process each active journal."""
    logger.info("Starting journal check cycle...")

    try:
        df = pd.read_csv(config.CSV_FILE)
    except Exception as e:
        logger.error("Error loading CSV file '%s': %s", config.CSV_FILE, e)
        return

    active = df[df["Tracking Status"] == "Active"]
    if active.empty:
        logger.warning("No active journals found in CSV.")
        return

    for _, row in active.iterrows():
        journal_name = row.get("Journal Name", "Unknown")
        rss_url = _cell_str(row, "RSS Feed")
        website_url = _cell_str(row, "Website URL", "Website")

        process_journal(journal_name, rss_url, website_url)
        time.sleep(config.REQUEST_DELAY)

    logger.info("Journal check cycle complete.")


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="RSSAgent journal monitor")
    parser.add_argument(
        "--once",
        action="store_true",
        help="Run a single check cycle and exit (no scheduler)",
    )
    return parser.parse_args()


def main() -> None:
    """Run one check immediately, then on a fixed schedule unless --once."""
    args = _parse_args()
    run_once = args.once or os.environ.get("RSSAGENT_RUN_ONCE", "").lower() in (
        "1",
        "true",
        "yes",
    )

    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(levelname)s - %(message)s",
    )

    setup_database()
    check_journals()

    if run_once:
        logger.info("Single cycle complete (--once).")
        return

    schedule.every(config.SCHEDULE_INTERVAL_HOURS).hours.do(check_journals)
    logger.info(
        "Scheduler started. Will run every %s hours. Press Ctrl+C to exit.",
        config.SCHEDULE_INTERVAL_HOURS,
    )

    try:
        while True:
            schedule.run_pending()
            time.sleep(60)
    except KeyboardInterrupt:
        logger.info("Shutting down by user request.")
    except Exception as e:
        logger.error("Unexpected error in main loop: %s", e)
