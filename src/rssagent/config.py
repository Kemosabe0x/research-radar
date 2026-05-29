"""Environment-backed configuration for the ingestion loop."""

import os
from pathlib import Path

# Repo root (src/rssagent/config.py → parents[2])
REPO_ROOT = Path(__file__).resolve().parents[2]

CSV_FILE = os.environ.get("RSSAGENT_CSV", str(REPO_ROOT / "Journals.csv"))
DB_FILE = os.environ.get("RSSAGENT_DB", str(REPO_ROOT / "journal_tracker.db"))
CONTENT_ROOT = Path(os.environ.get("RSSAGENT_CONTENT_ROOT", str(REPO_ROOT / "content")))
ARTICLES_DIR = CONTENT_ROOT / "articles"
DIGESTS_DIR = CONTENT_ROOT / "digests"

WEBHOOK_URL = os.environ.get("NOTIFICATION_WEBHOOK_URL")

SCHEDULE_INTERVAL_HOURS = int(os.environ.get("RSSAGENT_SCHEDULE_HOURS", "6"))
REQUEST_DELAY = float(os.environ.get("RSSAGENT_REQUEST_DELAY", "2"))
REQUEST_TIMEOUT = float(os.environ.get("RSSAGENT_REQUEST_TIMEOUT", "15"))
MAX_ENTRIES = int(os.environ.get("RSSAGENT_MAX_ENTRIES", "5"))

# LLM router config
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY", "")
GEMINI_MODEL = os.environ.get("GEMINI_MODEL", "gemini-2.0-flash")
AWS_REGION = os.environ.get("AWS_REGION", "us-east-1")
BEDROCK_MODEL_ID = os.environ.get("BEDROCK_MODEL_ID", "")
LLM_PROVIDER_ALERT = os.environ.get("LLM_PROVIDER_ALERT", "gemini")
LLM_PROVIDER_SYNTHESIZE = os.environ.get("LLM_PROVIDER_SYNTHESIZE", "gemini")
LLM_PROVIDER_GENERATE = os.environ.get("LLM_PROVIDER_GENERATE", "bedrock")
LLM_REQUEST_TIMEOUT = float(os.environ.get("RSSAGENT_LLM_TIMEOUT", "12"))

# Async digestion / generation controls
ENABLE_ALERT_DIGESTION = (
    os.environ.get("RSSAGENT_ENABLE_ALERT_DIGESTION", "true").strip().lower()
    in ("1", "true", "yes")
)
GENERATE_MIN_NEW_ARTICLES = int(
    os.environ.get("RSSAGENT_GENERATE_MIN_NEW_ARTICLES", "5")
)
GENERATE_DAILY_CAP = int(os.environ.get("RSSAGENT_GENERATE_DAILY_CAP", "3"))
GENERATE_WINDOW_HOURS = int(os.environ.get("RSSAGENT_GENERATE_WINDOW_HOURS", "24"))
PRIORITY_GENERATION_JOURNALS = tuple(
    item.strip()
    for item in os.environ.get("RSSAGENT_PRIORITY_JOURNALS", "").split(",")
    if item.strip()
)
