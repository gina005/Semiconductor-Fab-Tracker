import requests
import feedparser
import pandas as pd
import sqlite3
import os
from datetime import datetime

FEEDS = {
    "SemiEngineering": "https://semiengineering.com/feed/",
    "SemiconductorDigest": "https://www.semiconductor-digest.com/feed/",
    "GoogleNews_FabCapacity": "https://news.google.com/rss/search?q=semiconductor+fab+capacity&hl=en-US&gl=US&ceid=US:en",
}

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36"
}

DB_PATH = "data/fab_tracker.db"

def fetch_feed(url):
    response = requests.get(url, headers=HEADERS, timeout=10)
    return feedparser.parse(response.content)

def scrape_feeds():
    records = []
    for source, url in FEEDS.items():
        try:
            feed = fetch_feed(url)
            print(f"{source}: {len(feed.entries)} entries")
            for entry in feed.entries:
                records.append({
                    "source": source,
                    "title": entry.get("title", ""),
                    "link": entry.get("link", ""),
                    "published": entry.get("published", ""),
                    "summary": entry.get("summary", ""),
                    "scraped_at": datetime.now().isoformat()
                })
        except Exception as e:
            print(f"{source}: FAILED - {e}")
    return pd.DataFrame(records)

def save_to_db(df):
    conn = sqlite3.connect(DB_PATH)
    
    # Create table if it doesn't exist, with a UNIQUE constraint on link
    # so we don't save the same article twice
    conn.execute("""
        CREATE TABLE IF NOT EXISTS articles (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            source TEXT,
            title TEXT,
            link TEXT UNIQUE,
            published TEXT,
            summary TEXT,
            scraped_at TEXT
        )
    """)
    
    inserted = 0
    for _, row in df.iterrows():
        try:
            conn.execute("""
                INSERT INTO articles (source, title, link, published, summary, scraped_at)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (row["source"], row["title"], row["link"], row["published"], row["summary"], row["scraped_at"]))
            inserted += 1
        except sqlite3.IntegrityError:
            # This link already exists in the database, skip it
            pass
    
    conn.commit()
    conn.close()
    return inserted

if __name__ == "__main__":
    os.makedirs("data", exist_ok=True)
    
    df = scrape_feeds()
    print(f"\nTotal scraped this run: {len(df)} articles")
    
    new_count = save_to_db(df)
    print(f"New articles added to database: {new_count}")
    print(f"(Duplicates skipped: {len(df) - new_count})")