# RSS Agent

To continuously monitor a list of 150+ journals effectively, you need a Python architecture that can handle RSS parsing, task scheduling, duplicate prevention (so you don't get alerted about the same article twice), and error handling (since academic sites frequently timeout)

Here is the best-practice approach and a complete Python script to get you started.

## The Core Libraries You Will Need

- **feedparser**: The absolute best library for reading and extracting data from RSS/Atom feeds.

- **pandas**: To load and manage `Journals.csv`.

- **sqlite3** (Built-in): To maintain a lightweight local database of "seen" articles. This prevents your system from spamming you with duplicate content every time it runs.

- **schedule** or **APScheduler**: To run the script automatically at set intervals (e.g., every 6 hours).

- **requests** & **BeautifulSoup**: For the fallback journals that do not have RSS feeds, allowing you to scrape their website for new links.

## The Architecture Setup

To prevent "notification fatigue" and keep your script fast, follow this logic:

- Load the CSV.

- Loop through the RSS Feed column.

- Parse the feed and look at the guid or link of the latest articles.

- Check your SQLite database. If the link is new, save it, and trigger an alert (to a webhook, Notion, Slack, or an email). If it's old, ignore it.

- Sleep for 2-3 seconds between requests so academic publishers don't block your IP address.

## Best Practices for Scaling This

1. **Host it in the Cloud:** Don't run this on your laptop, as it will stop when your computer goes to sleep. Deploy the script to a cheap **$5**/month Virtual Private Server (VPS) on **DigitalOcean**, **Linode**, or run it as a Cron Job on **PythonAnywhere**.
2. **Add LLM Summarization:** Instead of just printing the title, you can pipe the `entry.description` (the abstract) into the `google-genai` or `openai` Python SDK. Have the AI read the abstract and generate a 2-sentence summary _before_ sending the notification to your Slack/Notion.
3. **Handle Rate Limits (403/429 Errors):** Academic publishers heavily protect their sites. Always include a `time.sleep(2)` between loops. If you get blocked, you may need to use a rotating proxy service or `cloudscraper` to bypass basic Cloudflare bot protections.
