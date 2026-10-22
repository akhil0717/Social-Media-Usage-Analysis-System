import pandas as pd

from modules.preprocessing import clean_text, tokenize


def test_clean_text_removes_urls_but_keeps_hashtags_emoji_and_punctuation():
    assert clean_text("Love this! https://example.com #Campus 😊") == "Love this! #Campus 😊"


def test_clean_text_handles_missing_values():
    assert clean_text(None) == ""
    assert clean_text(float("nan")) == ""
    assert clean_text(pd.NA) == ""


def test_tokenize_keeps_hashtags_as_terms():
    assert tokenize("Great #CampusLife!") == ["great", "#campuslife"]
