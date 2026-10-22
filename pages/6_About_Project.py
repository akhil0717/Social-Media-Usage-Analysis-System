"""Project overview, feature tour, workflow, and limitations."""

import streamlit as st

st.title("About Social Media Sage")
st.write(
    "Social Media Sage is a local-first educational application for exploring sentiment, "
    "topics, and engagement patterns in short-form social media text. It includes fictional "
    "demo posts for an immediately populated demonstration and accepts user-provided CSV files."
)

st.subheader("Project features")
feature_columns = st.columns(2)
with feature_columns[0]:
    st.markdown(
        """
        - Interactive dashboard with sentiment, engagement, platforms, and feed filters
        - Positive, negative, and neutral estimates for single or batch text
        - CSV upload, text-column selection, invalid-row reporting, and searchable results
        - Platform, date, sentiment, hashtag, topic, and engagement visualizations
        """
    )
with feature_columns[1]:
    st.markdown(
        """
        - Frequent terms, ranked topics, hashtags, and word clouds
        - Local SQLite history for real analysis summaries
        - Downloadable sample/analyzed CSVs and HTML summary report
        - Deterministic fictional sample data; no paid APIs, credentials, or scraping
        """
    )

st.subheader("Technology used")
tech_columns = st.columns(4)
tech_columns[0].markdown("**Interface**  \nStreamlit")
tech_columns[1].markdown("**Data**  \nPandas, NumPy, SQLite")
tech_columns[2].markdown("**Charts**  \nPlotly, Matplotlib, WordCloud")
tech_columns[3].markdown("**Sentiment**  \nVADER")

st.subheader("How to use the application")
st.markdown(
    """
    1. Start on the dashboard to review the current demo or your latest analysis.
    2. Try the example texts, or paste one comment per line in **Single Text Analysis**.
    3. In **Dataset Analysis**, explore or download the sample CSV, or upload your own data.
    4. Use **Trending Topics** to compare topic and hashtag frequencies.
    5. Visit **Analysis History** to distinguish demo snapshots from actual saved analyses.
    """
)
st.subheader("Sentiment methodology")
st.write(
    "VADER is a lexicon-and-rule-based model designed for short social text. Its compound "
    "score ranges from -1 to +1. A score at least 0.05 is labeled Positive, at most -0.05 "
    "Negative, and the interval between them Neutral. It does not produce a calibrated "
    "confidence probability, so this application does not display a confidence percentage."
)
st.subheader("Privacy, limitations, and responsible use")
st.markdown(
    """
    - Demo posts and usernames are fictional, locally generated, and not fetched from social APIs.
    - Uploaded CSVs are analyzed locally by the application; original post text is not stored in history.
    - History contains summary counts and metadata in a local SQLite database.
    - Sarcasm, slang, regional expressions, mixed-language text, and missing context may lead to errors.
    - Frequent terms are dataset counts, not proof of live or emerging real-time trends.
    - Sentiment outputs are illustrative and must not be presented as scientifically certain public-opinion measurements.
    """
)
