import streamlit as st
import sqlite3
import pandas as pd
import plotly.express as px
from collections import Counter

st.set_page_config(page_title="Semiconductor Fab Tracker", layout="wide")

DB_PATH = "data/fab_tracker.db"

ENTITY_KEYWORDS = {
    "TSMC": ["tsmc"],
    "Samsung": ["samsung"],
    "Intel": ["intel"],
    "ASML": ["asml"],
    "GlobalFoundries": ["globalfoundries"],
    "Micron": ["micron"],
    "SK Hynix": ["sk hynix", "hynix"],
    "3nm": ["3nm"],
    "2nm": ["2nm"],
    "EUV": ["euv"],
    "GAA": ["gate-all-around", "gaa"],
    "HBM": ["hbm"],
    "Chiplet": ["chiplet"],
}

SHORT_LABELS = {
    "capacity_expansion": "Capacity",
    "node_technology": "Node Tech",
    "policy_subsidy": "Policy",
    "company_earnings": "Earnings",
    "uncategorized": "Other",
}


@st.cache_data(ttl=3600)
def load_data():
    conn = sqlite3.connect(DB_PATH)
    df = pd.read_sql_query("SELECT * FROM articles", conn)
    conn.close()
    df["scraped_date"] = pd.to_datetime(df["scraped_at"]).dt.date
    return df


def load_summaries():
    conn = sqlite3.connect(DB_PATH)
    query = """
        SELECT a.title, a.source, a.link, a.published, a.tags, s.ai_summary, s.generated_at
        FROM ai_summaries s
        JOIN articles a ON a.id = s.article_id
        ORDER BY s.generated_at DESC
    """
    try:
        df = pd.read_sql_query(query, conn)
    except Exception:
        df = pd.DataFrame()
    conn.close()
    return df


def extract_entities(text):
    text_lower = str(text).lower()
    found = [entity for entity, keywords in ENTITY_KEYWORDS.items()
             if any(kw in text_lower for kw in keywords)]
    return found


def render_category_strip(tag_counts):
    cards = []
    for tag, count in tag_counts.items():
        label = SHORT_LABELS.get(tag, tag.replace("_", " ").title())
        cards.append(
            f'<div style="flex:1; padding:12px 16px; text-align:center; border-right:0.5px solid rgba(128,128,128,0.25);">'
            f'<p style="font-size:11px; color:gray; margin:0;">{label}</p>'
            f'<p style="font-size:18px; font-weight:600; margin:2px 0 0;">{count}</p>'
            f'</div>'
        )
    html = '<div style="display:flex; background:rgba(128,128,128,0.08); border-radius:12px; overflow:hidden;">' + "".join(cards) + '</div>'
    st.markdown(html, unsafe_allow_html=True)


def format_category_label(tag):
    return tag.replace("_", " ").title()


df = load_data()

st.title("🔬 Semiconductor Fab Capacity & Investment Tracker")
st.caption("Automated Daily Tracking Of Global Fab Capacity, Node Technology, Policy, And Earnings News")

tab1, tab2 = st.tabs(["📊 Full Dashboard", "✨ Key Article Summaries"])

with tab1:
    col1, col2, col3 = st.columns(3)
    col1.metric("Total Articles Tracked", len(df))
    col2.metric("Sources", df["source"].nunique())
    col3.metric("Days Of Data", df["scraped_date"].nunique())

    st.divider()

    st.subheader("Articles By Category")
    all_tags = df["tags"].str.split(", ").explode()
    tag_counts = all_tags.value_counts()
    render_category_strip(tag_counts)

    st.divider()

    st.subheader("📈 Article Volume Over Time By Category")
    trend_df = df.groupby(["scraped_date", "tags"]).size().reset_index(name="count")
    fig_trend = px.line(trend_df, x="scraped_date", y="count", color="tags", markers=True)
    fig_trend.update_layout(xaxis_title="Date", yaxis_title="Article Count", legend_title="Category")
    st.plotly_chart(fig_trend, use_container_width=True)

    st.divider()

    st.subheader("🏭 Most Mentioned Companies & Technologies")
    all_entities = []
    for _, row in df.iterrows():
        combined = f"{row['title']} {row['summary']}"
        all_entities.extend(extract_entities(combined))

    entity_counts = Counter(all_entities)
    if entity_counts:
        entity_df = pd.DataFrame(entity_counts.items(), columns=["Entity", "Mentions"]).sort_values(
            "Mentions", ascending=False
        )
        fig_entities = px.bar(entity_df, x="Entity", y="Mentions", color="Entity")
        fig_entities.update_layout(xaxis_title="Entity", yaxis_title="Mentions", legend_title="Entity")
        st.plotly_chart(fig_entities, use_container_width=True)
    else:
        st.info("No Tracked Entities Mentioned Yet — Check Back After More Data Is Collected.")

    st.divider()

    st.subheader("Browse Articles")
    tag_filter = st.multiselect(
        "Filter By Category",
        options=df["tags"].unique(),
        format_func=format_category_label
    )
    source_filter = st.multiselect("Filter By Source", options=df["source"].unique())

    filtered_df = df.copy()
    if tag_filter:
        filtered_df = filtered_df[filtered_df["tags"].isin(tag_filter)]
    if source_filter:
        filtered_df = filtered_df[filtered_df["source"].isin(source_filter)]

    display_df = filtered_df[["published", "source", "title", "tags", "link"]].rename(
        columns={
            "published": "Published Date",
            "source": "Source",
            "title": "Title",
            "tags": "Category",
            "link": "Link",
        }
    )

    st.dataframe(display_df, use_container_width=True, hide_index=True)

with tab2:
    st.subheader("AI-Generated Summaries Of Key Articles")
    st.caption("A Curated, AI-Summarised View Of The Most Significant Recent Articles")

    summaries_df = load_summaries()

    if summaries_df.empty:
        st.info("No Summaries Generated Yet. Run summariser.py To Generate Some.")
    else:
        for _, row in summaries_df.iterrows():
            with st.container(border=True):
                st.markdown(f"**{row['title']}**")
                st.caption(f"Source: {row['source']} · Published: {row['published']} · Category: {row['tags']}")
                st.write(row['ai_summary'])
                st.markdown(f"[Read Full Article]({row['link']})")