"""Convert a trusted joblib training bundle into portable runtime artifacts.

XGBoost pickle snapshots can fail across operating systems. The backend loads a
stable JSON model and plain preprocessing metadata instead. Only run this script
on a pickle received through a trusted channel because pickle loading can execute
code.
"""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import struct
from typing import Any

import joblib
import xgboost as xgb
from xgboost.core import Booster


class UbjsonReader:
    INTEGER_FORMATS = {"U": ">B", "i": ">b", "I": ">h", "l": ">i", "L": ">q"}

    def __init__(self, data: bytes) -> None:
        self.data = data
        self.position = 0

    def take(self, size: int) -> bytes:
        value = self.data[self.position : self.position + size]
        if len(value) != size:
            raise ValueError("XGBoost snapshot ended unexpectedly.")
        self.position += size
        return value

    def marker(self) -> str:
        return chr(self.take(1)[0])

    def integer(self, marker: str | None = None) -> int:
        marker = marker or self.marker()
        if marker not in self.INTEGER_FORMATS:
            raise ValueError(f"Unsupported UBJSON integer marker: {marker!r}")
        format_string = self.INTEGER_FORMATS[marker]
        return int(struct.unpack(format_string, self.take(struct.calcsize(format_string)))[0])

    def value(self, marker: str | None = None) -> Any:
        marker = marker or self.marker()
        if marker == "Z":
            return None
        if marker == "T":
            return True
        if marker == "F":
            return False
        if marker in self.INTEGER_FORMATS:
            return self.integer(marker)
        if marker == "d":
            return struct.unpack(">f", self.take(4))[0]
        if marker == "D":
            return struct.unpack(">d", self.take(8))[0]
        if marker == "C":
            return self.take(1).decode("utf-8")
        if marker in {"S", "H"}:
            return self.take(self.integer()).decode("utf-8")
        if marker == "[":
            return self.container("]", is_object=False)
        if marker == "{":
            return self.container("}", is_object=True)
        raise ValueError(f"Unsupported UBJSON value marker: {marker!r}")

    def container(self, closing: str, is_object: bool) -> Any:
        value_type = None
        count = None
        if self.data[self.position : self.position + 1] == b"$":
            self.position += 1
            value_type = self.marker()
        if self.data[self.position : self.position + 1] == b"#":
            self.position += 1
            count = self.integer()

        result: Any = {} if is_object else []
        index = 0
        while count is None or index < count:
            if count is None and self.data[self.position : self.position + 1] == closing.encode():
                self.position += 1
                break
            if is_object:
                key = self.take(self.integer()).decode("utf-8")
                result[key] = self.value(value_type)
            else:
                result.append(self.value(value_type))
            index += 1
        return result


def load_bundle_snapshot(path: Path) -> tuple[dict[str, Any], bytes]:
    original_setstate = Booster.__setstate__

    def capture_setstate(booster: Booster, state: dict[str, Any]) -> None:
        booster.__dict__.update(state)

    Booster.__setstate__ = capture_setstate
    try:
        bundle = joblib.load(path)
    finally:
        Booster.__setstate__ = original_setstate

    expected_keys = {"model", "encoder", "scaler", "feature_columns"}
    if not isinstance(bundle, dict) or not expected_keys <= set(bundle):
        raise ValueError(f"Bundle must contain: {sorted(expected_keys)}")

    captured_booster = bundle["model"]._Booster
    snapshot = bytes(captured_booster.handle)
    captured_booster.handle = None
    return bundle, snapshot


def convert(source: Path, model_output: Path, metadata_output: Path) -> dict[str, Any]:
    bundle, snapshot = load_bundle_snapshot(source)
    reader = UbjsonReader(snapshot)
    snapshot_data = reader.value()
    if reader.position != len(snapshot) or not isinstance(snapshot_data, dict):
        raise ValueError("Could not parse the complete XGBoost snapshot.")
    portable_model = snapshot_data.get("Model")
    if not isinstance(portable_model, dict):
        raise ValueError("Snapshot does not contain a Model object.")

    booster = xgb.Booster()
    booster.load_model(
        bytearray(json.dumps(portable_model, separators=(",", ":")).encode("utf-8"))
    )
    encoder = bundle["encoder"]
    scaler = bundle["scaler"]
    columns = [str(value) for value in bundle["feature_columns"]]
    if len(encoder.categories_) != 1:
        raise ValueError("Expected a one-column rule_id encoder.")
    if getattr(encoder, "drop_idx_", None) is not None or getattr(
        encoder, "_infrequent_enabled", False
    ):
        raise ValueError("Encoders using drop or infrequent categories are unsupported.")

    rule_ids = [str(value) for value in encoder.categories_[0]]
    expected_width = len(rule_ids) + len(columns)
    if booster.num_features() != expected_width:
        raise ValueError(
            f"Model width {booster.num_features()} does not match preprocessing width {expected_width}."
        )

    model_output.parent.mkdir(parents=True, exist_ok=True)
    metadata_output.parent.mkdir(parents=True, exist_ok=True)
    booster.save_model(model_output)
    metadata = {
        "format_version": 1,
        "source_bundle_sha256": hashlib.sha256(source.read_bytes()).hexdigest(),
        "xgboost_version": ".".join(str(value) for value in portable_model["version"]),
        "objective": portable_model["learner"]["objective"]["name"],
        "positive_class": 1,
        "rule_ids": rule_ids,
        "feature_columns": columns,
        "scaler_mean": [float(value) for value in scaler.mean_],
        "scaler_scale": [float(value) for value in scaler.scale_],
    }
    metadata_output.write_text(
        json.dumps(metadata, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    return metadata


def main() -> None:
    project_root = Path(__file__).resolve().parents[1]
    model_dir = project_root / "models" / "xgboost_10f"
    parser = argparse.ArgumentParser(description="Convert a trusted model bundle.")
    parser.add_argument("source", type=Path, nargs="?", default=model_dir / "source_bundle.pkl")
    parser.add_argument("--model-output", type=Path, default=model_dir / "model.json")
    parser.add_argument("--metadata-output", type=Path, default=model_dir / "metadata.json")
    args = parser.parse_args()

    metadata = convert(args.source, args.model_output, args.metadata_output)
    print(
        json.dumps(
            {
                "model": str(args.model_output),
                "metadata": str(args.metadata_output),
                "known_rules": len(metadata["rule_ids"]),
                "feature_count": len(metadata["feature_columns"]),
            },
            ensure_ascii=False,
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
