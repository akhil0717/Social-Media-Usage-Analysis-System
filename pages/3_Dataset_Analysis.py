"""Analyze an uploaded CSV or explore the complete built-in demo dataset."""

import pandas as pd
import streamlit as st

from modules.data_service import calculate_metrics, get_display_posts
from modules.database_manager import save_analysis
from modules.dataset_analyzer import (
    DatasetValidationError,
    analyze_dataset,
    engagement_average,
    engagement_count,
    sentiment_summary,
)
from modules.demo_data import get_demo_posts
from modules.report_generator import generate_html_report
from modules.topic_analysis import extract_terms
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

st.title("Dataset Analysis")
st.write(
    "Explore the sample dataset immediately or upload your own CSV. Uploaded data replaces "
    "the demo for this session after a successful analysis."
)

demo_posts = get_demo_posts()
st.download_button(
    "Download built-in demo dataset (CSV)",
    data=demo_posts.to_csv(index=False).encode("utf-8-sig"),
    file_name="social_media_sage_demo_posts.csv",
    mime="text/csv",
)
st.subheader("Built-in dataset preview")
st.dataframe(demo_posts.head(10), hide_index=True, use_container_width=True)
st.caption(
    f"Deterministic fictional data · {len(demo_posts):,} posts · "
    f"{demo_posts['platform'].nunique()} platforms · dates across the previous 30 days."
)

upload = st.file_uploader("Choose a CSV file to analyze", type=["csv"])
uploaded_data: pd.DataFrame | None = None
if upload is not None:
    try:
        upload.seek(0)
        uploaded_data = pd.read_csv(upload)
        if uploaded_data.empty or len(uploaded_data.columns) == 0:
            st.error("The uploaded CSV has no usable rows or columns. The current dataset remains unchanged.")
            uploaded_data = None
        else:
            st.subheader("Uploaded file preview")
            st.dataframe(uploaded_data.head(8), hide_index=True, use_container_width=True)
    except (pd.errors.ParserError, UnicodeDecodeError, ValueError) as error:
        st.error(f"Could not read this CSV: {error}. The current dataset remains unchanged.")

if uploaded_data is not None:
    normalized_names = {
        str(column).strip().lower(): column for column in uploaded_data.columns
    }
    detected = next(
        (
            normalized_names[name]
            for name in ("text", "post", "content", "comment", "message")
            if name in normalized_names
        ),
        uploaded_data.columns[0],
    )
    selected_text = st.selectbox(
        "Select the column containing post text",
        uploaded_data.columns.tolist(),
        index=uploaded_data.columns.tolist().index(detected),
    )
    st.caption(
        "Optional recognized fields: "
        + (
            ", ".join(
                str(column)
                for column in uploaded_data.columns
                if str(column).strip().lower()
                in {"date", "platform", "likes", "shares", "comments", "engagement"}
            )
            or "none"
        )
    )
    if st.button("Analyze uploaded CSV", type="primary"):
        try:
            with st.spinner("Validating rows and analyzing sentiment…"):
                analysis = analyze_dataset(uploaded_data, selected_text)
            results = analysis.results
            results["sentiment"] = results["label"]
            results["sentiment_score"] = results["score"]
            results["text"] = results["clean_text"]
            results.attrs["text_column"] = selected_text
            summary = sentiment_summary(results)
            terms = extract_terms(results["clean_text"], limit=10)
            metadata = {
                "average_engagement": engagement_average(results),
                "engagement_post_count": engagement_count(results),
                "terms": terms,
            }
            save_analysis("CSV dataset", len(results), summary, metadata)
            st.session_state["active_analysis_results"] = results
            st.session_state["dataset_results"] = results
            st.session_state["dataset_invalid_rows"] = analysis.invalid_rows
            st.session_state["dataset_terms"] = terms
            st.session_state["dataset_metadata"] = metadata
            st.success(f"Analyzed {len(results):,} valid posts.")
            st.rerun()
        except DatasetValidationError as error:
            st.error(f"Could not analyze the uploaded CSV: {error}")

posts, is_demo = get_display_posts(st.session_state)
st.divider()
st.subheader("Current analysis")
st.caption("Built-in sample dataset" if is_demo else "Latest valid analysis from this session")
summary_metrics = calculate_metrics(posts)
metric_columns = st.columns(5)
metric_columns[0].metric("Valid posts", f"{summary_metrics['total_posts']:,}")
for column, label in zip(metric_columns[1:], ("Positive", "Negative", "Neutral", "Platforms")):
    if label == "Platforms":
        column.metric(label, f"{summary_metrics['total_platforms']:,}")
    else:
        count = summary_metrics["sentiment_counts"][label]
        percent = summary_metrics["sentiment_percentages"][label]
        column.metric(label, f"{percent:.1f}%", f"{count:,} posts")

invalid_rows = st.session_state.get("dataset_invalid_rows")
if isinstance(invalid_rows, pd.DataFrame) and not invalid_rows.empty:
    with st.expander(f"Invalid uploaded rows ({len(invalid_rows):,})"):
        st.warning("Rows with missing or empty text are excluded from sentiment analysis.")
        st.dataframe(invalid_rows, hide_index=True, use_container_width=True)

first_row, second_row = st.columns(2)
with first_row:
    st.plotly_chart(sentiment_chart(summary_metrics["sentiment_counts"]), use_container_width=True)
with second_row:
    st.plotly_chart(
        sentiment_comparison_chart(summary_metrics["sentiment_counts"]),
        use_container_width=True,
    )

trend = daily_sentiment_trend_chart(posts)
if trend is not None:
    st.plotly_chart(trend, use_container_width=True)
chart_row = st.columns(2)
with chart_row[0]:
    chart = platform_distribution_chart(posts)
    if chart is not None:
        st.plotly_chart(chart, use_container_width=True)
with chart_row[1]:
    chart = engagement_by_platform_chart(posts)
    if chart is not None:
        st.plotly_chart(chart, use_container_width=True)
chart = engagement_by_sentiment_chart(posts)
if chart is not None:
    st.plotly_chart(chart, use_container_width=True)

topic_columns = st.columns(2)
with topic_columns[0]:
    st.markdown("**Most discussed topics**")
    chart = terms_chart(
        sorted(summary_metrics["topic_counts"].items(), key=lambda item: item[1], reverse=True)[:10]
    )
    if chart is not None:
        st.plotly_chart(chart, use_container_width=True)
with topic_columns[1]:
    st.markdown("**Top hashtags**")
    chart = terms_chart(
        sorted(summary_metrics["hashtag_counts"].items(), key=lambda item: item[1], reverse=True)[:10]
    )
    if chart is not None:
        st.plotly_chart(chart, use_container_width=True)

cloud = word_cloud_png(posts["text"].tolist())
if cloud:
    st.subheader("Word cloud")
    st.image(cloud, use_container_width=True)

st.subheader("Searchable post results")
result_filters = st.columns([2, 1, 1])
search = result_filters[0].text_input("Search posts")
platform_options = sorted(posts["platform"].unique().tolist())
selected_platforms = result_filters[1].multiselect(
    "Filter platforms", platform_options, default=platform_options
)
selected_sentiments = result_filters[2].multiselect(
    "Filter sentiment", ["Positive", "Negative", "Neutral"],
    default=["Positive", "Negative", "Neutral"],
)
table = posts.copy()
if search.strip():
    table = table[table["text"].str.contains(search.strip(), case=False, na=False, regex=False)]
table = table[table["platform"].isin(selected_platforms)]
table = table[table["sentiment"].isin(selected_sentiments)].sort_values(
    "engagement", ascending=False
)
display_columns = [
    column for column in (
        "post_id", "date", "platform", "username", "text", "sentiment",
        "sentiment_score", "likes", "comments", "shares", "engagement",
        "hashtags", "topic",
    ) if column in table.columns
]
st.dataframe(table[display_columns], hide_index=True, use_container_width=True)
st.download_button(
    "Download analyzed results (CSV)",
    data=table.to_csv(index=False).encode("utf-8-sig"),
    file_name="social_media_sage_analysis.csv",
    mime="text/csv",
)

observations = [
    f"{label} is the largest sentiment group with {summary_metrics['sentiment_counts'][label]} posts "
    f"({summary_metrics['sentiment_percentages'][label]:.1f}%)."
    for label in ("Positive", "Negative", "Neutral")
    if summary_metrics["sentiment_counts"][label] == max(summary_metrics["sentiment_counts"].values())
]
observations.append(
    "Frequent topics describe this dataset and are not necessarily real-time trends."
)
report = generate_html_report(
    "Social Media Sage — Dataset Summary",
    summary_metrics["total_posts"],
    summary_metrics["sentiment_counts"],
    summary_metrics["frequent_terms"],
    observations,
    {
        "average_engagement": summary_metrics["average_engagement"],
        "platform": f"{summary_metrics['total_platforms']} platforms",
    },
)
st.download_button(
    "Download summary report (HTML)",
    data=report.encode("utf-8"),
    file_name="social_media_sage_report.html",
    mime="text/html",
)
show_limitations_notice()
