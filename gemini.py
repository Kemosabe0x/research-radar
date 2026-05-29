import pandas as pd
import feedparser
import sqlite3
import time
import schedule
import requests

# 1. Database Setup: Create a table to track articles we've already seen
def setup_database():
    conn = sqlite3.connect('journal_tracker.db')
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

# 2. Function to send new articles to your workspace (Slack/Discord/Webhook)
def notify_new_article(journal_name, title, link):
    # Replace this with your actual webhook or saving logic
    print(f"🚨 NEW STUDY | {journal_name} | {title}\nLink: {link}\n")
    
    # Example Discord/Slack Webhook:
    # webhook_url = "YOUR_WEBHOOK_URL"
    # data = {"text": f"New from {journal_name}: {title} - {link}"}
    # requests.post(webhook_url, json=data)

# 3. Main tracking function
def check_journals():
    print("Starting journal check cycle...")
    
    # Load your CSV
    try:
        df = pd.read_csv('Journals - Master Journal List.csv')
    except Exception as e:
        print(f"Error loading CSV: {e}")
        return

    # Connect to DB
    conn = sqlite3.connect('journal_tracker.db')
    cursor = conn.cursor()

    # Loop through only active journals with RSS feeds
    active_feeds = df[(df['Tracking Status'] == 'Active') & (df['RSS Feed'].notna())]

    for index, row in active_feeds.iterrows():
        journal_name = row['Journal Name']
        rss_url = row['RSS Feed']
        
        try:
            # Parse the RSS feed
            feed = feedparser.parse(rss_url)
            
            # Look at the 5 most recent articles
            for entry in feed.entries[:5]:
                title = entry.get('title', 'No Title')
                link = entry.get('link', '')
                published = entry.get('published', '')

                # Check if this link is already in our database
                cursor.execute("SELECT 1 FROM seen_articles WHERE article_link = ?", (link,))
                is_seen = cursor.fetchone()

                if not is_seen:
                    # It's a new article! Save to DB and notify
                    cursor.execute('''
                        INSERT INTO seen_articles (journal_name, article_title, article_link, published_date)
                        VALUES (?, ?, ?, ?)
                    ''', (journal_name, title, link, published))
                    conn.commit()
                    
                    notify_new_article(journal_name, title, link)
            
            # Be polite to servers - wait 2 seconds before checking the next journal
            time.sleep(2)
            
        except Exception as e:
            print(f"Failed to parse {journal_name}: {e}")

    conn.close()
    print("Cycle complete. Waiting for next schedule.")

# 4. Scheduling the script to run continuously
if __name__ == "__main__":
    setup_database()
    
    # Run immediately on startup
    check_journals()
    
    # Schedule to run every 6 hours
    schedule.every(6).hours.do(check_journals)
    
    print("Scheduler running. Press Ctrl+C to exit.")
    while True:
        schedule.run_pending()
        time.sleep(60) # check schedule every minute


# For the journals where the RSS Feed column is blank, you'll need a secondary fallback scraper. 
# Add this logic to the script using BeautifulSoup:
from bs4 import BeautifulSoup
import requests

def fallback_scraper(website_url):
    headers = {'User-Agent': 'Mozilla/5.0'}
    response = requests.get(website_url, headers=headers)
    soup = BeautifulSoup(response.text, 'html.parser')
    
    # You would need to target the specific CSS class where the journal posts its "Latest Articles"
    # Example: latest_link = soup.find('a', class_='latest-article-link')['href']