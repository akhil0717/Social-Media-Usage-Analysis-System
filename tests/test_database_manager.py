from modules.database_manager import delete_analysis, get_history, save_analysis


def test_history_round_trip_and_delete(tmp_path):
    db_path = tmp_path / "history.sqlite3"
    entry_id = save_analysis(
        "CSV dataset",
        2,
        {"Positive": 1, "Neutral": 1, "Negative": 0},
        {"average_engagement": 3.5},
        db_path=db_path,
    )
    history = get_history(db_path=db_path)
    assert history[0]["id"] == entry_id
    assert history[0]["metadata"]["average_engagement"] == 3.5
    assert delete_analysis(entry_id, db_path=db_path)
    assert get_history(db_path=db_path) == []
