"""Manually exercise the production predictor with one code sample."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys


PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from vibesafe.detector import DEFAULT_MODEL, DEFAULT_MODEL_METADATA  # noqa: E402
from vibesafe.ml.features import extract_features  # noqa: E402
from vibesafe.ml.predictor import Predictor  # noqa: E402


def main() -> None:
    parser = argparse.ArgumentParser(description="Predict one rule candidate.")
    parser.add_argument("rule_id")
    source = parser.add_mutually_exclusive_group(required=True)
    source.add_argument("--code")
    source.add_argument("--file", type=Path)
    args = parser.parse_args()

    code = args.code if args.code is not None else args.file.read_text(encoding="utf-8")
    predictor = Predictor(DEFAULT_MODEL, DEFAULT_MODEL_METADATA)
    if not predictor.available:
        raise SystemExit(predictor.unavailable_reason)
    probability = predictor.predict_vulnerable_probability(
        args.rule_id, extract_features(code)
    )
    print(
        json.dumps(
            {
                "rule_id": args.rule_id,
                "known_rule": predictor.knows_rule(args.rule_id),
                "label": "vulnerable" if probability >= 0.5 else "safe",
                "vulnerable_probability": round(probability, 4),
            },
            ensure_ascii=False,
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
