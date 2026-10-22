from modules.sentiment import analyze_sentiment


def test_sentiment_classification_positive_negative_neutral():
    assert analyze_sentiment("I absolutely love this, it is wonderful!").label == "Positive"
    assert analyze_sentiment("This is awful and disappointing.").label == "Negative"
    assert analyze_sentiment("The meeting starts at noon.").label == "Neutral"


def test_vader_score_is_bounded_and_confidence_is_not_claimed():
    result = analyze_sentiment("Pretty good!")
    assert -1 <= result.score <= 1
    assert result.confidence is None
    assert result.explanation
