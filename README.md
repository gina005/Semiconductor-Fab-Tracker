# 🔬 Semiconductor Fab Capacity & Investment Tracker

An automated pipeline that tracks global semiconductor industry news — fab capacity expansions, process node technology, policy/subsidy developments, and earnings — and visualises it in a live, filterable dashboard.

**🔗 Live Dashboard:** https://semiconductor-fab-tracker-1.streamlit.app/

## What it does

This project automatically collects and categorises semiconductor industry news on a daily basis, with zero manual intervention:

- **Scrapes** RSS feeds from industry publications (SemiEngineering, Semiconductor Digest) and targeted Google News queries
- **Stores** articles in a SQLite database with duplicate detection, so the dataset grows cleanly over time
- **Tags** each article by category — capacity expansion, node technology, policy/subsidy, or earnings — using keyword-based classification
- **Automates** the entire collection process daily via GitHub Actions
- **Visualizes** the data through a live Streamlit dashboard with category breakdowns and a filterable article browser

## Why I built this

As an EEE undergraduate specialising in semiconductors, I wanted a way to track real-time industry signals, such as where fab investment is flowing, which process nodes are gaining traction, and how different policies (CHIPS Act, export controls) are shaping the sector. Rather than manually reading through news, this pipeline does the collection and categorisation automatically, letting me focus on interpreting trends.

## Tech Stack

- **Python** — `requests`, `feedparser`, `pandas` for scraping and data processing
- **SQLite** — lightweight persistent storage with duplicate prevention
- **GitHub Actions** — scheduled daily automation (cron-based)
- **Streamlit + Plotly** — interactive dashboard, deployed on Streamlit Community Cloud

## Architecture
RSS Feeds (3 sources)
↓
Scraper (requests + feedparser)
↓
SQLite Database (with duplicate detection)
↓
Keyword Tagging (capacity / node tech / policy / earnings)
↓
Streamlit Dashboard (live, public, filterable)
↑
GitHub Actions (runs the above daily, no manual intervention)

## Running it locally

```bash
git clone https://github.com/gina005/Semiconductor-Fab-Tracker.git
cd Semiconductor-Fab-Tracker
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python3 scraper.py       # run the scraper manually
streamlit run app.py     # launch the dashboard locally
```

## Future improvements

- Expand source coverage (equipment makers, additional regional news)
- Add sentiment analysis on headlines to gauge market tone
- Correlate policy/capacity news with semiconductor stock price movements
- Refine keyword tagging with a proper NLP classifier instead of keyword matching