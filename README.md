# Social Media Sage Analysis System

A local-first, college-level Python application for exploring sentiment, frequent terms, and engagement patterns in social media text. It processes user-provided posts and CSV datasets; it does not connect to or scrape social platforms.

The app opens in **DEMO MODE** with 120 deterministic, fictional posts from Instagram, X, Reddit, and Facebook. Demo metrics and charts are calculated directly from these rows. A successful text or CSV analysis takes precedence for the current session; the sample data is not written over your analysis or into the saved-history database.

## Features

- Streamlit dashboard with saved-analysis totals, sentiment percentages, and recent history.
- VADER sentiment analysis for one post or a batch of newline-separated comments.
- CSV upload with text-column selection, row validation, optional date/platform/engagement fields, search, and sentiment filters.
- Interactive Plotly charts for sentiment, platform comparisons, date trends, engagement, and frequent terms.
- Word-cloud generation with an informative message for insufficient text.
- Frequent word and hashtag counts with common stop words removed.
- SQLite analysis history with in-app deletion.
- Downloadable analyzed CSV and standalone HTML summary report.
- Demonstration dataset and automated tests.

## Technology stack

- Python 3.11+
- Streamlit, Pandas, NumPy
- Plotly
- VADER (`vaderSentiment`)
- WordCloud and Matplotlib
- SQLite (Python standard library)
- pytest

## Project structure

```text
.
├── app.py
├── requirements.txt
├── README.md
├── data/
│   └── sample_posts.csv
├── database/                 # SQLite history is created here at runtime
├── modules/
│   ├── database_manager.py
│   ├── data_service.py
│   ├── demo_data.py
│   ├── dataset_analyzer.py
│   ├── preprocessing.py
│   ├── report_generator.py
│   ├── sentiment.py
│   ├── topic_analysis.py
│   ├── ui.py
│   └── visualizations.py
├── pages/
│   ├── 1_Dashboard.py
│   ├── 2_Text_Analysis.py
│   ├── 3_Dataset_Analysis.py
│   ├── 4_Trending_Topics.py
│   ├── 5_Analysis_History.py
│   └── 6_About_Project.py
└── tests/
```

## Installation on Windows

Open PowerShell or Command Prompt in the project folder:

```powershell
python -m venv venv
venv\Scripts\activate
python -m pip install --upgrade pip
pip install -r requirements.txt
```

Run the application:

```powershell
streamlit run app.py
```

Streamlit opens the dashboard in your browser. The history database is created at `database/analysis_history.sqlite3` when the app starts. The database is local and ignored by Git.

## Using the sample dataset

The dashboard, text examples, topic charts, dataset preview, and demo history snapshots are populated on first launch. In **Dataset Analysis**, download the built-in dataset or upload your own CSV, select its text column, and choose **Analyze uploaded CSV**. A valid upload becomes the active dataset for this session. The separately provided `data/sample_posts.csv` includes a blank-text row to demonstrate validation; results and invalid rows are shown separately.

The built-in set is reproducible: it contains 120 fictional, varied posts dated over the last 30 days, with eight topics, three sentiment classes, and varied engagement. Demo history snapshots are visibly marked and are not saved analyses.

Expected CSV format:

| Column | Required? | Purpose |
| --- | --- | --- |
| `text` (or another selected column) | Yes | Post/comment text |
| `date` | No | Date for sentiment trend charts |
| `platform` | No | Grouped sentiment comparison |
| `likes`, `shares`, `comments`, `engagement` | No | Engagement comparisons |

Only a usable text column is mandatory. Column names are not case-sensitive when the app attempts to detect likely text and optional fields. Invalid dates and non-numeric engagement values become missing values; rows with missing or blank text are excluded from analysis and reported.

## How sentiment analysis works

The application runs the locally bundled VADER lexicon/rule model. VADER accounts for some social-text signals such as punctuation, capitalization, and emoji. Its compound score ranges from -1 to +1:

- `>= 0.05`: Positive
- `<= -0.05`: Negative
- Between those thresholds: Neutral

This score is not a confidence probability. The application does not display a confidence estimate because this model does not provide a calibrated probability. URL removal is limited to the cleaned display/topic text; hashtags, punctuation, and emoji are retained. VADER itself receives the entered text to preserve sentiment cues.

## Testing

Install dependencies as above, then run:

```powershell
python -m pytest
```

Tests cover sentiment labels and score semantics, text cleaning, missing values, datasets with missing optional fields, invalid datasets, engagement availability, and SQLite history operations.

## Limitations and privacy

- Sentiment can be inaccurate with sarcasm, slang, regional expressions, context-dependent wording, and mixed-language text.
- The analysis is an educational estimate, not a scientifically certain measurement of public opinion.
- Frequent words and hashtags are counts from the uploaded sample, not real-time trends.
- No live social data is fetched. Users must have authorization to use any data they provide.
- Uploaded data is analyzed in the running application process. Analysis history saves summary counts and metadata, not the original post text.
- The local history database can be removed by deleting its file after stopping the app; individual history entries can also be deleted in the interface.
