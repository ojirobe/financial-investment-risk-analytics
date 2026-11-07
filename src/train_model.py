"""Train a chronological, leakage-safe next-day market-stress classifier."""

from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.calibration import CalibratedClassifierCV
from sklearn.compose import ColumnTransformer
from sklearn.impute import SimpleImputer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import average_precision_score, balanced_accuracy_score, brier_score_loss, roc_auc_score
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import TimeSeriesSplit


ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data" / "processed" / "market_features.csv"
REPORT = ROOT / "reports" / "model_metrics.json"
PREDICTIONS = ROOT / "data" / "processed" / "model_predictions.csv"

FEATURES = [
    "sp500_return", "nasdaq_return", "gold_return", "bonds_return",
    "sp500_vol_21d", "nasdaq_vol_21d", "gold_vol_21d", "bonds_vol_21d",
    "vix", "vix_change", "treasury_10y",
]


def make_dataset(frame: pd.DataFrame, train_end: int) -> tuple[pd.DataFrame, pd.Series, float]:
    data = frame.copy()
    next_abs_return = data["sp500_return"].shift(-1).abs()
    threshold = float(next_abs_return.iloc[:train_end].quantile(0.90))
    data["target_next_day_stress"] = (next_abs_return >= threshold).astype(int)
    data = data.iloc[:-1].copy()
    return data[FEATURES], data["target_next_day_stress"], threshold


def main() -> None:
    frame = pd.read_csv(DATA, parse_dates=["date"])
    split = int(len(frame) * 0.80)
    features, target, threshold = make_dataset(frame, split)
    x_train, x_test = features.iloc[:split], features.iloc[split:]
    y_train, y_test = target.iloc[:split], target.iloc[split:]

    base_pipeline = Pipeline([
        ("imputer", SimpleImputer(strategy="median")),
        ("scaler", StandardScaler()),
        ("model", LogisticRegression(max_iter=2000, class_weight="balanced", random_state=42)),
    ])
    pipeline = CalibratedClassifierCV(
        estimator=base_pipeline,
        method="sigmoid",
        cv=TimeSeriesSplit(n_splits=5),
    )
    pipeline.fit(x_train, y_train)
    probability = pipeline.predict_proba(x_test)[:, 1]
    decision_threshold = float(y_train.mean())
    prediction = (probability >= decision_threshold).astype(int)
    pr_auc = float(average_precision_score(y_test, probability))

    metrics = {
        "objective": "Predict whether the next trading day's absolute S&P 500 return exceeds the training-set 90th percentile",
        "chronological_split": True,
        "training_rows": int(len(x_train)),
        "test_rows": int(len(x_test)),
        "training_end_date": frame["date"].iloc[split - 1].date().isoformat(),
        "test_start_date": frame["date"].iloc[split].date().isoformat(),
        "stress_threshold_abs_return_pct": threshold * 100,
        "test_stress_rate": float(y_test.mean()),
        "roc_auc": float(roc_auc_score(y_test, probability)),
        "pr_auc": pr_auc,
        "decision_threshold_training_prevalence": decision_threshold,
        "balanced_accuracy": float(balanced_accuracy_score(y_test, prediction)),
        "brier_score": float(brier_score_loss(y_test, probability)),
        "baseline_brier_training_prevalence": float(brier_score_loss(y_test, np.repeat(y_train.mean(), len(y_test)))),
        "not_for_trading": True,
    }
    REPORT.write_text(json.dumps(metrics, indent=2) + "\n")
    pd.DataFrame({
        "date": frame["date"].iloc[split:-1].dt.date,
        "actual_stress": y_test.values,
        "predicted_probability": probability,
    }).to_csv(PREDICTIONS, index=False)
    print(json.dumps(metrics, indent=2))


if __name__ == "__main__":
    main()

