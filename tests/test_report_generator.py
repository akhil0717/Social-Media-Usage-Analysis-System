from modules.report_generator import generate_html_report


def test_report_includes_summary_chart_and_escapes_dynamic_text():
    report = generate_html_report(
        "Dataset <summary>",
        2,
        {"Positive": 1, "Neutral": 0, "Negative": 1},
        [("<script>", 3)],
        ["Two analyzed posts."],
    )
    assert "Dataset &lt;summary&gt;" in report
    assert "<svg" in report
    assert "&lt;script&gt;" in report
    assert "<script>" not in report
