"""Analyze sample, single, or batch post text."""

import pandas as pd
import streamlit as st

from modules.data_service import calculate_metrics
from modules.database_manager import save_analysis
from modules.sentiment import analyze_sentiment
from modules.topic_analysis import extract_terms
from modules.ui import show_limitations_notice
from modules.visualizations import sentiment_chart, sentiment_comparison_chart

EXAMPLE_POSTS = {
    "Positive - technology": "The new phone update is fantastic — the battery finally lasts all day! #TechWin",
    "Negative - customer service": "Really disappointed with the support chat; I waited an hour and still have no answer. #NeedsWork",
    "Neutral - education": "The library study room is open until 9 PM this week. #CampusInfo",
    "Positive - fitness": "That morning yoga class was so refreshing. Already looking forward to next week! #Fitness",
    "Negative - shopping": "My order arrived late and the return process is confusing. #Shopping",
}

st.title("Single Text Analysis")
st.write("Choose an example or enter one post per line to analyze several comments together.")

selected_example = st.selectbox("Load a sample text", ["Choose an example…", *EXAMPLE_POSTS])
if st.button("Use selected example", disabled=selected_example == "Choose an example…"):
    st.session_state["text_input_area"] = EXAMPLE_POSTS[selected_example]

with st.form("text_analysis_form"):
    raw_text = st.text_area(
        "Post or comments",
        height=190,
        key="text_input_area",
        placeholder="Example: I love the new campus library! #study",
        help="Separate individual posts with line breaks. Blank lines are ignored.",
    )
    submitted = st.form_submit_button("Analyze text", type="primary")

if submitted:
    texts = [line.strip() for line in raw_text.splitlines() if line.strip()]
    if not texts:
        st.warning("Enter at least one non-empty post or comment.")
    else:
        rows = []
        for text in texts:
            result = analyze_sentiment(text).to_dict()
            rows.append(
                {
                    "post_id": f"TEXT-{len(rows) + 1:03d}",
                    "text": text,
                    **result,
                    "sentiment": result["label"],
                    "sentiment_score": result["score"],
                    "platform": "Text input",
                    "username": "you",
                    "date": pd.Timestamp.now(),
                    "likes": None,
                    "comments": None,
                    "shares": None,
                    "hashtags": " ".join(word for word in text.split() if word.startswith("#")),
                    "topic": "Text analysis",
                }
            )
        results = pd.DataFrame(rows)
        counts = {
            name: int(results["label"].eq(name).sum())
            for name in ("Positive", "Negative", "Neutral")
        }
        save_analysis(
            "Text input",
            len(results),
            counts,
            {"comments": len(results), "terms": extract_terms(results["text"], limit=10)},
        )
        st.session_state["latest_text_results"] = results
        st.session_state["active_analysis_results"] = results

results = st.session_state.get("latest_text_results")
is_example_preview = not isinstance(results, pd.DataFrame) or results.empty
if is_example_preview:
    example_text = EXAMPLE_POSTS["Positive - technology"]
    example_result = analyze_sentiment(example_text).to_dict()
    results = pd.DataFrame(
        [
            {
                "text": example_text,
                **example_result,
                "sentiment": example_result["label"],
                "sentiment_score": example_result["score"],
            }
        ]
    )
if isinstance(results, pd.DataFrame) and not results.empty:
    st.subheader("Analysis results")
    if is_example_preview:
        st.caption("Example preview — this text is illustrative and has not been saved to analysis history.")
    summary = {
        label: int(results["label"].eq(label).sum())
        for label in ("Positive", "Negative", "Neutral")
    }
    metrics = calculate_metrics(results)
    metric_columns = st.columns(4)
    metric_columns[0].metric("Posts analyzed", f"{len(results):,}")
    for column, label in zip(metric_columns[1:], ("Positive", "Negative", "Neutral")):
        column.metric(
            label,
            f"{metrics['sentiment_percentages'][label]:.1f}%",
            f"{summary[label]} posts",
        )
    charts = st.columns(2)
    charts[0].plotly_chart(sentiment_chart(summary), use_container_width=True)
    charts[1].plotly_chart(sentiment_comparison_chart(summary), use_container_width=True)
    display = results.rename(
        columns={
            "text": "Text",
            "label": "Sentiment",
            "score": "VADER score",
            "confidence": "Confidence",
            "explanation": "Explanation",
        }
    )
    st.dataframe(
        display[["Text", "Sentiment", "VADER score", "Confidence", "Explanation"]],
        hide_index=True,
        use_container_width=True,
    )
    st.caption(
        "VADER scores range from -1 (most negative) to +1 (most positive). "
        "VADER does not provide a calibrated confidence probability."
    )
show_limitations_notice()
