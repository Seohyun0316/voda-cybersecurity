"""Create the 10-feature JSONL consumed by the training script."""

from __future__ import annotations

import argparse
import collections
import json
from pathlib import Path
import sys


PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from vibesafe.ml.features import FEATURE_COLUMNS, extract_features  # noqa: E402


def transform(input_path: Path, output_path: Path) -> tuple[int, dict[int, int]]:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    count = 0
    label_counts: collections.Counter[int] = collections.Counter()

    with input_path.open("r", encoding="utf-8") as source, output_path.open(
        "w", encoding="utf-8", newline="\n"
    ) as destination:
        for line_number, line in enumerate(source, start=1):
            if not line.strip():
                continue
            try:
                row = json.loads(line)
                code = row.get("code")
                label = row.get("label_binary")
                if not isinstance(code, str):
                    raise ValueError("code must be a string")
                if label not in (0, 1):
                    raise ValueError("label_binary must be 0 or 1")
            except (json.JSONDecodeError, ValueError) as exc:
                raise ValueError(f"Invalid row at line {line_number}: {exc}") from exc

            result = {
                "rule_id": row.get("rule_id"),
                "code": code,
                "repo_url": row.get("repo_url"),
                "file_path": row.get("file_path"),
                **extract_features(code),
                "label_binary": label,
            }
            destination.write(json.dumps(result, ensure_ascii=False) + "\n")
            count += 1
            label_counts[label] += 1

    return count, dict(sorted(label_counts.items()))


def main() -> None:
    parser = argparse.ArgumentParser(description="Create the VibeSafe 10-feature dataset.")
    parser.add_argument("input_jsonl", type=Path)
    parser.add_argument("output_jsonl", type=Path)
    args = parser.parse_args()

    rows, labels = transform(args.input_jsonl, args.output_jsonl)
    print(
        json.dumps(
            {
                "rows": rows,
                "label_counts": labels,
                "feature_count": len(FEATURE_COLUMNS),
                "features": FEATURE_COLUMNS,
                "output": str(args.output_jsonl),
            },
            ensure_ascii=False,
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
