"""Environment-backed configuration for the ingestion loop."""

import os
from pathlib import Path

# Repo root (src/rssagent/config.py → parents[2])
REPO_ROOT = Path(__file__).resolve().parents[2]

CSV_FILE = os.environ.get("RSSAGENT_CSV", str(REPO_ROOT / "Journals.csv"))
DB_FILE = os.environ.get("RSSAGENT_DB", str(REPO_ROOT / "journal_tracker.db"))

WEBHOOK_URL = os.environ.get("NOTIFICATION_WEBHOOK_URL")

SCHEDULE_INTERVAL_HOURS = int(os.environ.get("RSSAGENT_SCHEDULE_HOURS", "6"))
REQUEST_DELAY = float(os.environ.get("RSSAGENT_REQUEST_DELAY", "2"))
REQUEST_TIMEOUT = float(os.environ.get("RSSAGENT_REQUEST_TIMEOUT", "15"))
MAX_ENTRIES = int(os.environ.get("RSSAGENT_MAX_ENTRIES", "5"))
