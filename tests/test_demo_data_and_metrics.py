from datetime import date, timedelta
from io import StringIO

import pandas as pd

from modules.data_service import calculate_metrics, filter_posts, get_display_posts
from modules.demo_data import build_demo_posts, get_demo_posts


def test_demo_dataset_is_deterministic_complete_and_recent():
    today = date(2026, 10, 22)
    first = build_demo_posts(today)
    second = build_demo_posts(today)
    pd.testing.assert_frame_equal(first, second)
    assert len(first) >= 100
    assert first["post_id"].is_unique
    assert first["text"].nunique() == len(first)
    assert set(first["platform"]) == {"Instagram", "X", "Reddit", "Facebook"}
    assert set(first["sentiment"]) == {"Positive", "Negative", "Neutral"}
    assert set(first["topic"]) == {
        "Technology", "AI", "Education", "Gaming", "Fitness", "Entertainment",
        "Customer Service", "Shopping",
    }
    assert (first["date"].dt.date >= today - timedelta(days=29)).all()
    assert (first["date"].dt.date <= today).all()
    assert {"post_id", "date", "platform", "username", "text", "sentiment",
            "sentiment_score", "likes", "comments", "shares", "hashtags", "topic"} <= set(first)


def test_metrics_reconcile_to_the_displayed_rows():
    posts = get_demo_posts()
    metrics = calculate_metrics(posts)
    assert metrics["total_posts"] == len(posts) == 120
    assert metrics["total_platforms"] == posts["platform"].nunique() == 4
    assert sum(metrics["sentiment_counts"].values()) == len(posts)
    assert round(sum(metrics["sentiment_percentages"].values()), 8) == 100
    assert metrics["total_shares"] == int(posts["shares"].sum())
    assert metrics["total_engagement"] == int(posts[["likes", "comments", "shares"]].sum().sum())
    assert metrics["most_discussed_topic"] in posts["topic"].unique()
    assert metrics["most_frequent_hashtag"].startswith("#")


def test_optional_engagement_metrics_are_missing_not_fake_zeroes():
    source = pd.DataFrame(
        {"text": ["An analyzed text"], "label": ["Neutral"], "score": [0.0]}
    )
    metrics = calculate_metrics(source)
    assert metrics["average_likes"] is None
    assert metrics["average_comments"] is None
    assert metrics["total_shares"] is None
    assert metrics["total_engagement"] is None


def test_user_analysis_takes_precedence_over_demo_and_filters_are_consistent():
    custom = pd.DataFrame(
        {
            "text": ["Wonderful product! #Shop", "Awful delivery #Shop"],
            "label": ["Positive", "Negative"],
            "score": [0.8, -0.8],
            "platform": ["X", "Reddit"],
        }
    )
    selected, is_demo = get_display_posts({"active_analysis_results": custom})
    assert not is_demo
    assert len(selected) == 2
    filtered = filter_posts(selected, platforms=["X"], sentiments=["Positive"])
    assert filtered["text"].tolist() == ["Wonderful product! #Shop"]
    assert len(get_display_posts({})[0]) == len(get_demo_posts())


def test_uploaded_csv_round_trip_analyzes_every_valid_sample_post():
    from modules.dataset_analyzer import analyze_dataset, sentiment_summary

    source = get_demo_posts()
    uploaded_copy = pd.read_csv(StringIO(source.to_csv(index=False)))
    analysis = analyze_dataset(uploaded_copy, "text")
    assert len(analysis.results) == len(source)
    assert analysis.invalid_rows.empty
    assert sentiment_summary(analysis.results) == {
        label: int(source["sentiment"].eq(label).sum())
        for label in ("Positive", "Neutral", "Negative")
    }
