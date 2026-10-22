from modules.demo_data import get_demo_posts
from modules.topic_analysis import extract_terms
from modules.data_service import calculate_metrics
from modules.visualizations import (
    daily_sentiment_trend_chart,
    engagement_by_platform_chart,
    engagement_by_sentiment_chart,
    engagement_chart,
    hashtag_chart,
    platform_distribution_chart,
    platform_sentiment_chart,
    sentiment_chart,
    sentiment_comparison_chart,
    sentiment_trend_chart,
    terms_chart,
    topic_chart,
    word_cloud_png,
)


def test_demo_visualizations_have_non_empty_plot_data():
    posts = get_demo_posts()
    metrics = calculate_metrics(posts)
    terms = extract_terms(posts["text"], limit=10)
    charts = [
        sentiment_chart(metrics["sentiment_counts"]),
        sentiment_comparison_chart(metrics["sentiment_counts"]),
        daily_sentiment_trend_chart(posts),
        platform_distribution_chart(posts),
        engagement_by_platform_chart(posts),
        engagement_by_sentiment_chart(posts),
        platform_sentiment_chart(posts, "platform"),
        sentiment_trend_chart(posts),
        engagement_chart(posts),
        terms_chart(terms),
        hashtag_chart(metrics["hashtag_counts"]),
        topic_chart(metrics["topic_counts"]),
    ]
    assert all(chart is not None and len(chart.data) > 0 for chart in charts)
    assert word_cloud_png(posts["text"].tolist()).startswith(b"\x89PNG")
