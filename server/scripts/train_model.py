"""Train and save the selected 10-feature XGBoost bundle."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys


PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from vibesafe.ml.features import FEATURE_COLUMNS  # noqa: E402


def train(dataset_path: Path, output_path: Path) -> dict[str, float]:
    import joblib
    import numpy as np
    import pandas as pd
    from sklearn.metrics import accuracy_score, f1_score
    from sklearn.model_selection import train_test_split
    from sklearn.preprocessing import OneHotEncoder, StandardScaler
    from xgboost import XGBClassifier

    rows = [
        json.loads(line)
        for line in dataset_path.read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]
    frame = pd.DataFrame(rows)
    inputs = frame[["rule_id", *FEATURE_COLUMNS]]
    labels = frame["label_binary"].astype(int)
    train_x, test_x, train_y, test_y = train_test_split(
        inputs, labels, test_size=0.2, random_state=42, stratify=labels
    )

    encoder = OneHotEncoder(handle_unknown="ignore")
    rule_train = encoder.fit_transform(train_x[["rule_id"]]).toarray()
    rule_test = encoder.transform(test_x[["rule_id"]]).toarray()
    scaler = StandardScaler()
    numeric_train = scaler.fit_transform(train_x[FEATURE_COLUMNS])
    numeric_test = scaler.transform(test_x[FEATURE_COLUMNS])

    model = XGBClassifier(
        n_estimators=100,
        max_depth=2,
        learning_rate=0.1,
        eval_metric="logloss",
        random_state=42,
    )
    model.fit(np.hstack([rule_train, numeric_train]), train_y)
    train_prediction = model.predict(np.hstack([rule_train, numeric_train]))
    test_prediction = model.predict(np.hstack([rule_test, numeric_test]))

    output_path.parent.mkdir(parents=True, exist_ok=True)
    joblib.dump(
        {
            "model": model,
            "encoder": encoder,
            "scaler": scaler,
            "feature_columns": FEATURE_COLUMNS,
        },
        output_path,
    )
    return {
        "train_accuracy": float(accuracy_score(train_y, train_prediction)),
        "train_f1": float(f1_score(train_y, train_prediction)),
        "test_accuracy": float(accuracy_score(test_y, test_prediction)),
        "test_f1": float(f1_score(test_y, test_prediction)),
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Train the VibeSafe 10-feature model.")
    parser.add_argument("dataset", type=Path)
    parser.add_argument(
        "--output",
        type=Path,
        default=PROJECT_ROOT / "models" / "xgboost_10f" / "source_bundle.pkl",
    )
    args = parser.parse_args()
    metrics = train(args.dataset, args.output)
    print(json.dumps({"output": str(args.output), **metrics}, indent=2))


if __name__ == "__main__":
    main()
