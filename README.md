# Sports Science RSS Tracker 🧬📚

This repository contains a curated master database of 150+ academic journals and industry blogs covering Sports Science, Nutrition, Biomechanics, Physiology, and Sports Medicine.

It includes a Python scheduling script that continuously monitors the RSS feeds of these publications, prevents duplicate alerts using a local SQLite database, and can be hooked into Slack, Discord, or Notion to provide a live feed of the latest industry research.

## Features

- **Master Journal Database:** Track topics, subtopics, and active RSS links across 150+ sources.
- **Curated Top 20s:** Filtered lists of the highest-impact journals per category to prevent information overload.
- **Automated Python Monitor:** Uses `feedparser` and `schedule` to fetch the latest abstracts and alert you to new studies in real-time.

## Run the monitor

```bash
python -m venv .venv && source .venv/bin/activate
pip install -e .
python -m rssagent --once   # single cycle (recommended for testing)
python -m rssagent          # loop every 6 hours
```

Journal list: `Journals.csv`. If an RSS URL is missing, invalid, or returns HTML/errors, the monitor falls back to scraping the journal `Website` column. Optional: `NOTIFICATION_WEBHOOK_URL` for Slack/Discord alerts.
