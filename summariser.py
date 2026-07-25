import os
import sqlite3
from datetime import datetime
from dotenv import load_dotenv
import anthropic

load_dotenv()

DB_PATH = "data/fab_tracker.db"
DAILY_SUMMARY_CAP = 5  # keeps cost extremely low, adjust if you want more

client = anthropic.Anthropic(api_key=os.environ.get("ANTHROPIC_API_KEY"))


def get_important_articles(limit=15):
    """
    Pick 'important' articles: prioritise ones that are tagged
    (not uncategorised) and most recent.
    """
    conn = sqlite3.connect(DB_PATH)
    query = """
        SELECT id, source, title, link, summary, tags, published
        FROM articles
        WHERE tags != 'uncategorized'
        ORDER BY scraped_at DESC
        LIMIT ?
    """
    cursor = conn.execute(query, (limit,))
    columns = [desc[0] for desc in cursor.description]
    articles = [dict(zip(columns, row)) for row in cursor.fetchall()]
    conn.close()
    return articles


def summarise_article(title, summary_text):
    prompt = f"""Summarise this semiconductor industry article in exactly 3 sentences.
Focus on the business or technical significance - why does this matter for the semiconductor industry.

Title: {title}
Content: {summary_text}

Respond with ONLY the 3-sentence summary, nothing else."""

    response = client.messages.create(
        model="claude-haiku-4-5",
        max_tokens=150,
        messages=[{"role": "user", "content": prompt}]
    )
    return response.content[0].text.strip()


def ensure_summary_table():
    conn = sqlite3.connect(DB_PATH)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS ai_summaries (
            article_id INTEGER PRIMARY KEY,
            ai_summary TEXT,
            generated_at TEXT
        )
    """)
    conn.commit()
    conn.close()


def generate_summaries():
    ensure_summary_table()
    articles = get_important_articles(limit=15)

    conn = sqlite3.connect(DB_PATH)
    existing_ids = set(row[0] for row in conn.execute("SELECT article_id FROM ai_summaries"))

    new_summaries = 0

    for article in articles:
        if new_summaries >= DAILY_SUMMARY_CAP:
            print(f"Reached daily cap of {DAILY_SUMMARY_CAP} summaries, stopping.")
            break
        if article["id"] in existing_ids:
            continue  # already summarised, skip (saves API cost)
        try:
            ai_summary = summarise_article(article["title"], article["summary"])
            conn.execute(
                "INSERT INTO ai_summaries (article_id, ai_summary, generated_at) VALUES (?, ?, ?)",
                (article["id"], ai_summary, datetime.now().isoformat())
            )
            new_summaries += 1
            print(f"Summarised: {article['title'][:60]}...")
        except Exception as e:
            print(f"Failed to summarise article {article['id']}: {e}")

    conn.commit()
    conn.close()
    print(f"\nGenerated {new_summaries} new AI summaries")


if __name__ == "__main__":
    generate_summaries()