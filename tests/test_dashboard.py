from streamlit.testing.v1 import AppTest


def test_dashboard_smoke():
    app = AppTest.from_file("app.py").run(timeout=60)
    assert not list(app.exception)
    assert [title.value for title in app.title] == ["Financial & Investment Risk Analytics"]
    labels = {metric.label for metric in app.metric}
    assert {"Observations", "Annualized volatility", "ROC AUC", "Brier score"} <= labels

