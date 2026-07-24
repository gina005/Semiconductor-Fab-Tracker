import streamlit as st
import sqlite3
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="Semiconductor Fab Tracker", layout="wide")

DB_PATH = "data/fab_tracker.db"

@st.cache_data(ttl=3600)
def load_data():
    conn = sqlite3.connect(DB_PATH)
    df = pd.read_sql_query("SELECT * FROM articles", conn)
    conn.close()
    return df

df = load_data()

st.title("🔬 Semiconductor Fab Capacity & Investment Tracker")
st.caption("Automated daily tracking of global fab capacity, node technology, policy, and earnings news")

# Top metrics
col1, col2, col3 = st.columns(3)
col1.metric("Total Articles Tracked", len(df))
col2.metric("Sources", df["source"].nunique())
col3.metric("Categories Detected", df[df["tags"] != "uncategorized"]["tags"].nunique())

st.divider()

# Tag breakdown chart
st.subheader("Articles by Category")
tag_counts = df["tags"].value_counts().reset_index()
tag_counts.columns = ["tag", "count"]
fig = px.bar(tag_counts, x="tag", y="count", color="tag")
st.plotly_chart(fig, use_container_width=True)

st.divider()

# Filterable article table
st.subheader("Browse Articles")
tag_filter = st.multiselect("Filter by category", options=df["tags"].unique())
source_filter = st.multiselect("Filter by source", options=df["source"].unique())

filtered_df = df.copy()
if tag_filter:
    filtered_df = filtered_df[filtered_df["tags"].isin(tag_filter)]
if source_filter:
    filtered_df = filtered_df[filtered_df["source"].isin(source_filter)]

st.dataframe(
    filtered_df[["published", "source", "title", "tags", "link"]],
    use_container_width=True,
    hide_index=True
)