"""Interactive overview of the current analysis or built-in demo dataset."""

import pandas as pd
import streamlit as st

from modules.data_service import (
    SENTIMENTS,
    calculate_metrics,
    filter_posts,
    get_display_posts,
)
from modules.database_manager import get_history
from modules.ui import show_limitations_notice
from modules.visualizations import (
    daily_sentiment_trend_chart,
    engagement_by_platform_chart,
    engagement_by_sentiment_chart,
    platform_distribution_chart,
    sentiment_chart,
    sentiment_comparison_chart,
    terms_chart,
    word_cloud_png,
)


def display_number(value, decimals: int = 0) -> str:
    """Format available measurements without turning missing data into zero."""
    if value is None or pd.isna(value):
        return "—"
    return f"{value:,.{decimals}f}" if decimals else f"{int(value):,}"


st.title("Social Media Sage")
st.caption("A local-first view of sentiment patterns, platform activity, and conversation topics.")

source_posts, is_demo = get_display_posts(st.session_state)
st.caption(
    f"{'Built-in deterministic demo dataset' if is_demo else 'Latest user analysis'}"
    f" · {len(source_posts):,} posts available"
)

with st.expander("Filter dashboard posts", expanded=False):
    filter_columns = st.columns([2, 1, 1, 1])
    search = filter_columns[0].text_input("Search post text, username, or hashtag", key="dashboard_search")
    platforms = sorted(source_posts["platform"].unique().tolist())
    selected_platforms = filter_columns[1].multiselect(
        "Platform", platforms, default=platforms, key="dashboard_platforms"
    )
    selected_sentiments = filter_columns[2].multiselect(
        "Sentiment", list(SENTIMENTS), default=list(SENTIMENTS), key="dashboard_sentiments"
    )
    sort_engagement = filter_columns[3].checkbox("Top engagement first", key="dashboard_sort_engagement")

posts_for_search = source_posts.copy()
if search.strip():
    posts_for_search = posts_for_search[
        posts_for_search["text"].str.contains(search.strip(), case=False, na=False, regex=False)
        | posts_for_search["username"].str.contains(search.strip(), case=False, na=False, regex=False)
        | posts_for_search["hashtags"].str.contains(search.strip(), case=False, na=False, regex=False)
    ]
filtered_posts = filter_posts(
    posts_for_search,
    platforms=selected_platforms,
    sentiments=selected_sentiments,
    sort_by_engagement=sort_engagement,
)
if filtered_posts.empty:
    st.info("No posts match those filters. Adjust the platform, sentiment, or search filters.")
    st.stop()
metrics = calculate_metrics(filtered_posts)

metric_rows = st.columns(5)
metric_rows[0].metric("Total posts analyzed", f"{metrics['total_posts']:,}")
metric_rows[1].metric("Platforms", f"{metrics['total_platforms']:,}")
metric_rows[2].metric(
    "Positive posts",
    f"{metrics['sentiment_counts']['Positive']:,}",
    f"{metrics['sentiment_percentages']['Positive']:.1f}%",
)
metric_rows[3].metric(
    "Negative posts",
    f"{metrics['sentiment_counts']['Negative']:,}",
    f"{metrics['sentiment_percentages']['Negative']:.1f}%",
)
metric_rows[4].metric(
    "Neutral posts",
    f"{metrics['sentiment_counts']['Neutral']:,}",
    f"{metrics['sentiment_percentages']['Neutral']:.1f}%",
)

engagement_metrics = st.columns(5)
engagement_metrics[0].metric("Avg. likes", display_number(metrics["average_likes"], 1))
engagement_metrics[1].metric("Avg. comments", display_number(metrics["average_comments"], 1))
engagement_metrics[2].metric("Total shares", display_number(metrics["total_shares"]))
engagement_metrics[3].metric("Total engagement", display_number(metrics["total_engagement"]))
engagement_metrics[4].metric("Most discussed topic", metrics["most_discussed_topic"])
st.caption(
    f"Most used hashtag: **{metrics['most_frequent_hashtag']}** · "
    f"Sentiment percentages use the {metrics['total_posts']:,} posts currently matching filters."
)


top_post = metrics["highest_engagement_post"]
if top_post:
    with st.container(border=True):
        st.markdown("**Highest-engagement post in the current selection**")
        st.write(top_post.get("text", ""))
        st.caption(
            f"{top_post.get('platform', 'Unknown')} · @{top_post.get('username', 'unknown')} · "
            f"{int(top_post.get('engagement', 0)):,} total engagement · "
            f"{top_post.get('sentiment', 'Neutral')} sentiment"
        )

st.subheader("Sentiment overview")
chart_columns = st.columns(2)
with chart_columns[0]:
    st.plotly_chart(sentiment_chart(metrics["sentiment_counts"]), use_container_width=True)
with chart_columns[1]:
    st.plotly_chart(
        sentiment_comparison_chart(metrics["sentiment_counts"]), use_container_width=True
    )

st.subheader("Conversation and engagement patterns")
trend = daily_sentiment_trend_chart(filtered_posts)
platform_distribution = platform_distribution_chart(filtered_posts)
if trend is not None:
    st.plotly_chart(trend, use_container_width=True)
pattern_columns = st.columns(2)
with pattern_columns[0]:
    if platform_distribution is not None:
        st.plotly_chart(platform_distribution, use_container_width=True)
with pattern_columns[1]:
    platform_engagement = engagement_by_platform_chart(filtered_posts)
    if platform_engagement is not None:
        st.plotly_chart(platform_engagement, use_container_width=True)
sentiment_engagement = engagement_by_sentiment_chart(filtered_posts)
if sentiment_engagement is not None:
    st.plotly_chart(sentiment_engagement, use_container_width=True)
cloud = word_cloud_png(filtered_posts["text"].tolist())
if cloud:
    st.subheader("Word cloud")
    st.image(cloud, use_container_width=True)

st.subheader("Top topics and hashtags")
topic_columns = st.columns(2)
with topic_columns[0]:
    topic_chart = terms_chart(
        sorted(metrics["topic_counts"].items(), key=lambda item: item[1], reverse=True)[:10]
    )
    st.markdown("**Most discussed topics**")
    if topic_chart is not None:
        st.plotly_chart(topic_chart, use_container_width=True)
with topic_columns[1]:
    hashtag_chart = terms_chart(
        sorted(metrics["hashtag_counts"].items(), key=lambda item: item[1], reverse=True)[:10]
    )
    st.markdown("**Top hashtags**")
    if hashtag_chart is not None:
        st.plotly_chart(hashtag_chart, use_container_width=True)

st.subheader("Recent posts")
feed_columns = st.columns([1, 1, 2])
feed_platforms = feed_columns[0].multiselect(
    "Feed platforms", sorted(filtered_posts["platform"].unique()), key="feed_platforms"
)
feed_sentiments = feed_columns[1].multiselect(
    "Feed sentiments", list(SENTIMENTS), default=list(SENTIMENTS), key="feed_sentiments"
)
feed_order = feed_columns[2].selectbox(
    "Feed order", ["Most recent", "Highest engagement"], key="feed_order"
)
feed = filter_posts(
    filtered_posts,
    platforms=feed_platforms,
    sentiments=feed_sentiments,
    sort_by_engagement=feed_order == "Highest engagement",
).head(12)
if feed.empty:
    st.info("No posts match the selected filters.")
else:
    for _, post in feed.iterrows():
        timestamp = pd.Timestamp(post["date"]).strftime("%b %d, %Y · %I:%M %p")
        with st.container(border=True):
            st.markdown(
                f"**{post['platform']}** · @{post['username']} · "
                f"`{post['sentiment']}` · {timestamp}"
            )
            st.write(post["text"])
            st.caption(
                f"♥ {display_number(post['likes'])} likes  ·  "
                f"◉ {display_number(post['comments'])} comments  ·  "
                f"↗ {display_number(post['shares'])} shares  ·  "
                f"{display_number(post['engagement'])} total engagement"
            )

st.subheader("Recent analysis activity")
history = get_history()
if is_demo:
    sample_activity = filtered_posts.copy()
    sample_activity["_day"] = pd.to_datetime(sample_activity["date"]).dt.date
    day_groups = sample_activity.groupby("_day", observed=True)
    snapshots = []
    for day, day_posts in list(day_groups)[-5:]:
        snapshots.append(
            {
                "Date": f"{day.isoformat()} · sample",
                "Activity": "DEMO snapshot",
                "Posts": len(day_posts),
                "Positive": int(day_posts["sentiment"].eq("Positive").sum()),
                "Neutral": int(day_posts["sentiment"].eq("Neutral").sum()),
                "Negative": int(day_posts["sentiment"].eq("Negative").sum()),
            }
        )
    st.caption("Illustrative daily snapshots derived from the fictional demo posts, not saved analyses.")
    st.dataframe(
        pd.DataFrame(reversed(snapshots)),
        hide_index=True,
        use_container_width=True,
    )
if history:
    st.caption("Real analyses saved by you on this device.")
    activity = pd.DataFrame(
        [
            {
                "Date": record["created_at"].replace("T", " ")[:19],
                "Type": record["input_type"],
                "Posts": record["post_count"],
                "Positive": record["summary"].get("Positive", 0),
                "Neutral": record["summary"].get("Neutral", 0),
                "Negative": record["summary"].get("Negative", 0),
            }
            for record in history[:5]
        ]
    )
    st.dataframe(activity, hide_index=True, use_container_width=True)
else:
    st.caption("No real analyses saved yet. Saved user activity will appear here after an analysis.")

show_limitations_notice()
