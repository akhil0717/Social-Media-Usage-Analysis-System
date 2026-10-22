"""Rank the most common hashtags, terms, and topics in the selected data."""

import pandas as pd
import streamlit as st

from modules.data_service import calculate_metrics, get_display_posts
from modules.topic_analysis import extract_terms
from modules.ui import show_limitations_notice
from modules.visualizations import (
    daily_sentiment_trend_chart,
    engagement_by_platform_chart,
    terms_chart,
    word_cloud_png,
)

st.title("Trending Topics")
posts, is_demo = get_display_posts(st.session_state)
st.caption(
    "Explore frequently mentioned terms in the selected dataset. Counts describe this sample, "
    "not real-time social trends."
)
st.caption("Current source: built-in sample posts." if is_demo else "Current source: your latest analysis.")

metrics = calculate_metrics(posts)
total_columns = st.columns(4)
total_columns[0].metric("Posts scanned", f"{len(posts):,}")
total_columns[1].metric("Most discussed topic", metrics["most_discussed_topic"])
total_columns[2].metric("Top hashtag", metrics["most_frequent_hashtag"])
total_columns[3].metric("Unique topics", f"{len(metrics['topic_counts']):,}")

rank_columns = st.columns(2)
with rank_columns[0]:
    st.subheader("Top hashtags")
    hashtags = sorted(
        metrics["hashtag_counts"].items(), key=lambda item: (-item[1], item[0])
    )[:10]
    hashtag_chart = terms_chart(hashtags)
    if hashtag_chart is not None:
        st.plotly_chart(hashtag_chart, use_container_width=True)
    st.dataframe(
        pd.DataFrame(
            [{"Rank": rank, "Hashtag": tag, "Posts": count}
             for rank, (tag, count) in enumerate(hashtags, start=1)]
        ),
        hide_index=True,
        use_container_width=True,
    )
with rank_columns[1]:
    st.subheader("Frequently discussed terms")
    terms = extract_terms(posts["text"], limit=10)
    term_chart = terms_chart(terms)
    if term_chart is not None:
        st.plotly_chart(term_chart, use_container_width=True)
    st.dataframe(
        pd.DataFrame(
            [{"Rank": rank, "Term": term, "Mentions": count}
             for rank, (term, count) in enumerate(terms, start=1)]
        ),
        hide_index=True,
        use_container_width=True,
    )

st.subheader("Topic summaries")
topic_table = []
for rank, (topic, count) in enumerate(
    sorted(metrics["topic_counts"].items(), key=lambda item: (-item[1], item[0]))[:10],
    start=1,
):
    topic_posts = posts[posts["topic"].eq(topic)]
    sentiment_counts = topic_posts["sentiment"].value_counts()
    dominant_sentiment = sentiment_counts.index[0] if not sentiment_counts.empty else "Neutral"
    topic_table.append(
        {
            "Rank": rank,
            "Topic": topic,
            "Posts": count,
            "Most common sentiment": dominant_sentiment,
            "Average engagement": round(float(topic_posts["engagement"].mean()), 1),
        }
    )
st.dataframe(pd.DataFrame(topic_table), hide_index=True, use_container_width=True)
topics_chart = terms_chart(
    sorted(metrics["topic_counts"].items(), key=lambda item: (-item[1], item[0]))[:10]
)
if topics_chart is not None:
    st.plotly_chart(topics_chart, use_container_width=True)

trend = daily_sentiment_trend_chart(posts)
if trend is not None:
    st.subheader("Daily sentiment pattern")
    st.plotly_chart(trend, use_container_width=True)
platform_engagement = engagement_by_platform_chart(posts)
if platform_engagement is not None:
    st.subheader("Engagement by platform")
    st.plotly_chart(platform_engagement, use_container_width=True)

cloud = word_cloud_png(posts["text"].tolist())
if cloud:
    st.subheader("Word cloud")
    st.image(cloud, use_container_width=True)
else:
    st.info("There is not enough varied text to create a meaningful word cloud.")

st.warning(
    "Frequently occurring words and hashtags are counts from the supplied dataset and are "
    "not necessarily trending in real time. This application does not access social platforms."
)
show_limitations_notice()
