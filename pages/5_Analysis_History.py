"""Separate illustrative demo snapshots from genuine locally saved analyses."""

import pandas as pd
import streamlit as st

from modules.database_manager import delete_analysis, get_history
from modules.demo_data import get_demo_posts

st.title("Analysis History")
st.caption("Real analysis history is saved locally in SQLite. Demo snapshots below are illustrative only.")

posts = get_demo_posts()
posts = posts.copy()
posts["_day"] = pd.to_datetime(posts["date"], errors="coerce").dt.date
daily = posts.dropna(subset=["_day"]).groupby("_day", observed=True)
demo_snapshots = []
for day, rows in list(daily)[-5:]:
    demo_snapshots.append(
        {
            "Date": f"{day.isoformat()} · sample",
            "Record type": "DEMO snapshot",
            "Input type": "Fictional sample posts",
            "Posts": len(rows),
            "Positive": int(rows["sentiment"].eq("Positive").sum()),
            "Neutral": int(rows["sentiment"].eq("Neutral").sum()),
            "Negative": int(rows["sentiment"].eq("Negative").sum()),
        }
    )
demo_snapshots.reverse()
st.subheader("Example activity (demo)")
st.info(
    "These sample snapshots are calculated from the fictional demo posts. They do not represent "
    "saved user actions and are not stored in the history database."
)
st.dataframe(pd.DataFrame(demo_snapshots), hide_index=True, use_container_width=True)

st.subheader("Your saved analyses")
history = get_history()
if not history:
    st.info("No real analyses have been saved on this device yet. Run a text or CSV analysis to record one.")
else:
    table = pd.DataFrame(
        [
            {
                "ID": record["id"],
                "Date (UTC)": record["created_at"].replace("T", " ")[:19],
                "Record type": "SAVED USER ANALYSIS",
                "Input type": record["input_type"],
                "Posts": record["post_count"],
                "Positive": record["summary"].get("Positive", 0),
                "Neutral": record["summary"].get("Neutral", 0),
                "Negative": record["summary"].get("Negative", 0),
            }
            for record in history
        ]
    )
    st.dataframe(table, hide_index=True, use_container_width=True)
    identifiers = [record["id"] for record in history]
    with st.form("delete_history_form"):
        selected_id = st.selectbox("Select a saved entry to delete", identifiers)
        confirmed = st.checkbox(
            "I understand this permanently removes the selected local history entry."
        )
        submitted = st.form_submit_button("Delete selected entry")
    if submitted:
        if not confirmed:
            st.warning("Confirm deletion before continuing.")
        elif delete_analysis(int(selected_id)):
            st.success(f"Deleted saved history entry {selected_id}.")
            st.rerun()
        else:
            st.error("That history entry no longer exists.")
