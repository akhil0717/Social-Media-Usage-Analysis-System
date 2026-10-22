import pandas as pd
import pytest

from modules.dataset_analyzer import (
    DatasetValidationError,
    analyze_dataset,
    engagement_average,
    engagement_count,
    sentiment_summary,
)


def test_dataset_with_missing_optional_columns_and_invalid_text_rows():
    data = pd.DataFrame(
        {"post": ["Love the event! #great", None, "   "], "likes": ["4", "2", "1"]}
    )
    result = analyze_dataset(data, "post")
    assert len(result.results) == 1
    assert len(result.invalid_rows) == 2
    assert result.results.iloc[0]["label"] == "Positive"
    assert sentiment_summary(result.results) == {"Positive": 1, "Neutral": 0, "Negative": 0}
    assert engagement_average(result.results) == 4.0


def test_dataset_handles_optional_date_platform_and_engagement():
    data = pd.DataFrame(
        {
            "text": ["Great day", "Bad day"],
            "date": ["2025-01-01", "not a date"],
            "platform": ["Forum", "Forum"],
            "shares": [2, "unknown"],
        }
    )
    result = analyze_dataset(data, "text")
    assert result.results["date"].notna().sum() == 1
    assert result.results["shares"].notna().sum() == 1


def test_optional_headers_are_case_insensitive_and_text_column_is_preserved():
    data = pd.DataFrame(
        {"comments": ["I love this!", "This is disappointing."], "Likes": ["4", "2"],
         "Platform": ["Forum", "Forum"]}
    )
    result = analyze_dataset(data, "comments")
    assert result.results["comments"].tolist() == data["comments"].tolist()
    assert result.results["likes"].tolist() == [4, 2]
    assert result.results["platform"].tolist() == ["Forum", "Forum"]
    assert engagement_average(result.results) == 3.0
    assert engagement_count(result.results) == 2


def test_invalid_dataset_inputs_raise_clear_errors():
    with pytest.raises(DatasetValidationError, match="no rows"):
        analyze_dataset(pd.DataFrame(), "text")
    with pytest.raises(DatasetValidationError, match="not found"):
        analyze_dataset(pd.DataFrame({"post": ["hello"]}), "text")
    with pytest.raises(DatasetValidationError, match="No rows contain usable text"):
        analyze_dataset(pd.DataFrame({"text": [None, " "]}), "text")


def test_no_engagement_columns_returns_none():
    assert engagement_average(pd.DataFrame({"label": ["Neutral"]})) is None


def test_total_engagement_column_is_not_added_to_component_counts():
    data = pd.DataFrame({"engagement": [10], "likes": [7], "shares": [2], "comments": [1]})
    assert engagement_average(data) == 10.0
