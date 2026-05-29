#!/usr/bin/env python3
"""
RSS Agent for Monitoring Academic Journals

This script continuously monitors a list of journals (from a CSV file) for new articles.
It checks RSS feeds for active journals, saves seen articles to a local SQLite database,
and sends notifications (via print, webhook, etc.). For journals without RSS feeds,
a fallback scraper using BeautifulSoup attempts to extract latest articles from the journal's website.

Configuration:
- CSV file: 'Journals - Master Journal List.csv' with columns:
    'Journal Name', 'Tracking Status', 'RSS Feed', 'Website URL'
- SQLite database: 'journal_tracker.db'
- Notification webhook URL: set via environment variable NOTIFICATION_WEBHOOK_URL or modify the code.
- Scheduling interval: every 6 hours (adjustable).

Usage: python rssagent.py
"""

import os
import time
import logging
import sqlite3
import pandas as pd
import feedparser
import requests
from bs4 import BeautifulSoup
import schedule

# ------------------------------
# Configuration
# ------------------------------

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

# Notification webhook URL (e.g., Slack, Discord)
# Override with environment variable or change here
WEBHOOK_URL = os.environ.get("NOTIFICATION_WEBHOOK_URL", None)

# Schedule interval (in hours)
SCHEDULE_INTERVAL_HOURS = 6

# Delay between requests to avoid rate limiting (seconds)
REQUEST_DELAY = 2

# Number of most recent entries to check per feed
MAX_ENTRIES = 5

# CSV file path
CSV_FILE = 'Journals - Master Journal List.csv'

# Database file
DB_FILE = 'journal_tracker.db'

# ------------------------------
# Database Functions
# ------------------------------

def setup_database():
    """Create the seen_articles table if it doesn't exist."""
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS seen_articles (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            journal_name TEXT,
            article_title TEXT,
            article_link TEXT UNIQUE,
            published_date TEXT
        )
    ''')
    conn.commit()
    conn.close()
    logging.info("Database setup complete.")

def is_article_seen(link):
    """Check if an article link already exists in the database."""
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("SELECT 1 FROM seen_articles WHERE article_link = ?", (link,))
    result = cursor.fetchone()
    conn.close()
    return result is not None

def save_article(journal_name, title, link, published_date):
    """Insert a new article into the database."""
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO seen_articles (journal_name, article_title, article_link, published_date)
        VALUES (?, ?, ?, ?)
    ''', (journal_name, title, link, published_date))
    conn.commit()
    conn.close()
    logging.info(f"Saved new article: {title[:50]}... from {journal_name}")

# ------------------------------
# Notification Functions
# ------------------------------

def notify_new_article(journal_name, title, link):
    """
    Send notification about a new article.
    By default, prints to console. If WEBHOOK_URL is set, sends a POST request.
    """
    message = f"🚨 NEW STUDY | {journal_name} | {title}\nLink: {link}\n"
    logging.info(message)

    if WEBHOOK_URL:
        try:
            payload = {"text": f"New from {journal_name}: {title}\n{link}"}
            response = requests.post(WEBHOOK_URL, json=payload, timeout=5)
            response.raise_for_status()
            logging.info(f"Notification sent to webhook: {WEBHOOK_URL}")
        except Exception as e:
            logging.error(f"Failed to send webhook notification: {e}")

# ------------------------------
# RSS Feed Processing
# ------------------------------

def process_rss_feed(journal_name, rss_url):
    """
    Parse an RSS feed, check for new articles, and notify.
    Returns number of new articles found.
    """
    try:
        feed = feedparser.parse(rss_url)
        if feed.bozo:  # feedparser may set bozo flag on parse errors
            logging.warning(f"Feed parsing warning for {journal_name}: {feed.bozo_exception}")

        new_count = 0
        for entry in feed.entries[:MAX_ENTRIES]:
            title = entry.get('title', 'No Title')
            link = entry.get('link', '')
            published = entry.get('published', '')

            if not link:
                logging.warning(f"Skipping entry without link in {journal_name}")
                continue

            if not is_article_seen(link):
                save_article(journal_name, title, link, published)
                notify_new_article(journal_name, title, link)
                new_count += 1
        return new_count
    except Exception as e:
        logging.error(f"Error processing RSS feed for {journal_name}: {e}")
        return 0

# ------------------------------
# Fallback Scraper (for journals without RSS)
# ------------------------------

def fallback_scraper(journal_name, website_url):
    """
    Generic fallback scraper for journals without RSS.
    Attempts to find links to latest articles on the website.
    This is a basic implementation; you may need to customize per journal.
    """
    if not website_url:
        logging.warning(f"No website URL provided for {journal_name}, skipping.")
        return 0

    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
    try:
        response = requests.get(website_url, headers=headers, timeout=15)
        response.raise_for_status()
    except Exception as e:
        logging.error(f"Failed to fetch website for {journal_name}: {e}")
        return 0

    soup = BeautifulSoup(response.text, 'html.parser')

    # Common patterns: look for links containing 'article', 'abstract', 'fulltext', etc.
    # This is a very generic approach; you should tailor the selector for each journal.
    # Example: find all <a> tags with href containing '/doi/' or '/abs/'
    article_links = []
    for a in soup.find_all('a', href=True):
        href = a['href']
        # Filter typical academic article patterns
        if any(pattern in href.lower() for pattern in ['/doi/', '/abs/', '/full/', '/article/', '/pdf/']):
            # Ensure absolute URL
            if href.startswith('http'):
                full_link = href
            else:
                full_link = requests.compat.urljoin(website_url, href)
            article_links.append(full_link)

    # Deduplicate and limit to first few
    seen_links = set()
    new_count = 0
    for link in article_links[:MAX_ENTRIES]:
        if link in seen_links:
            continue
        seen_links.add(link)

        if not is_article_seen(link):
            # Try to extract title: use link text or generate from URL
            # For simplicity, use a placeholder title
            title = f"Article from {journal_name} (scraped)"
            published = ''  # scraped date not easily available
            save_article(journal_name, title, link, published)
            notify_new_article(journal_name, title, link)
            new_count += 1

    logging.info(f"Fallback scraper found {new_count} new articles for {journal_name}")
    return new_count

# ------------------------------
# Main Check Function
# ------------------------------

def check_journals():
    """Main routine: load CSV, process each journal's RSS or fallback."""
    logging.info("Starting journal check cycle...")

    try:
        df = pd.read_csv(CSV_FILE)
    except Exception as e:
        logging.error(f"Error loading CSV file '{CSV_FILE}': {e}")
        return

    # Filter active journals
    active = df[df['Tracking Status'] == 'Active']
    if active.empty:
        logging.warning("No active journals found in CSV.")
        return

    # Process each journal
    for index, row in active.iterrows():
        journal_name = row.get('Journal Name', 'Unknown')
        rss_url = row.get('RSS Feed', '').strip()
        website_url = row.get('Website URL', '').strip()

        # Skip if both RSS and website are missing
        if not rss_url and not website_url:
            logging.warning(f"No RSS or website URL for {journal_name}, skipping.")
            continue

        new_articles = 0
        if rss_url:
            new_articles = process_rss_feed(journal_name, rss_url)
        else:
            # Fallback to scraper
            new_articles = fallback_scraper(journal_name, website_url)

        # Be polite to servers
        time.sleep(REQUEST_DELAY)

    logging.info("Journal check cycle complete.")

# ------------------------------
# Scheduling & Main Entry Point
# ------------------------------

def main():
    setup_database()

    # Run once immediately on start
    check_journals()

    # Schedule periodic runs
    schedule.every(SCHEDULE_INTERVAL_HOURS).hours.do(check_journals)
    logging.info(f"Scheduler started. Will run every {SCHEDULE_INTERVAL_HOURS} hours. Press Ctrl+C to exit.")

    try:
        while True:
            schedule.run_pending()
            time.sleep(60)  # check schedule every minute
    except KeyboardInterrupt:
        logging.info("Shutting down by user request.")
    except Exception as e:
        logging.error(f"Unexpected error in main loop: {e}")

if __name__ == "__main__":
    main()