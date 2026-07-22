"""Portable XGBoost inference for one rule candidate."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Mapping

from vibesafe.ml.features import FEATURE_COLUMNS


class Predictor:
    def __init__(self, model_path: str | Path, metadata_path: str | Path) -> None:
        self.model = None
        self.feature_columns: list[str] = []
        self.rule_ids: list[str] = []
        self._rule_indexes: dict[str, int] = {}
        self._scaler_mean: list[float] = []
        self._scaler_scale: list[float] = []
        self.unavailable_reason = ""
        self._load(Path(model_path), Path(metadata_path))

    @property
    def available(self) -> bool:
        return self.model is not None

    @property
    def known_rule_count(self) -> int:
        return len(self.rule_ids)

    def knows_rule(self, rule_id: str) -> bool:
        return rule_id in self._rule_indexes

    def _load(self, model_path: Path, metadata_path: Path) -> None:
        try:
            import xgboost as xgb

            metadata = json.loads(metadata_path.read_text(encoding="utf-8"))
            self._validate_metadata(metadata)
            model = xgb.Booster()
            model.load_model(model_path)

            expected_width = len(metadata["rule_ids"]) + len(metadata["feature_columns"])
            if model.num_features() != expected_width:
                raise ValueError(
                    f"모델 입력 폭({model.num_features()})과 메타데이터({expected_width})가 다릅니다."
                )
        except Exception as exc:
            self.unavailable_reason = f"ML 모델을 불러올 수 없습니다: {exc}"
            return

        self.model = model
        self.feature_columns = list(metadata["feature_columns"])
        self.rule_ids = list(metadata["rule_ids"])
        self._rule_indexes = {value: index for index, value in enumerate(self.rule_ids)}
        self._scaler_mean = [float(value) for value in metadata["scaler_mean"]]
        self._scaler_scale = [float(value) for value in metadata["scaler_scale"]]

    @staticmethod
    def _validate_metadata(metadata: object) -> None:
        if not isinstance(metadata, dict):
            raise ValueError("모델 메타데이터는 JSON 객체여야 합니다.")
        for key in ("rule_ids", "feature_columns", "scaler_mean", "scaler_scale"):
            if not isinstance(metadata.get(key), list):
                raise ValueError(f"모델 메타데이터에 배열 {key}가 필요합니다.")

        if metadata["feature_columns"] != FEATURE_COLUMNS:
            raise ValueError("모델 피처 순서가 런타임 10피처 정의와 다릅니다.")
        if len(metadata["scaler_mean"]) != len(FEATURE_COLUMNS):
            raise ValueError("scaler_mean과 피처 개수가 다릅니다.")
        if len(metadata["scaler_scale"]) != len(FEATURE_COLUMNS):
            raise ValueError("scaler_scale과 피처 개수가 다릅니다.")
        if any(float(value) == 0.0 for value in metadata["scaler_scale"]):
            raise ValueError("scaler_scale에는 0이 포함될 수 없습니다.")

    def predict_vulnerable_probability(
        self, rule_id: str, features: Mapping[str, float]
    ) -> float:
        if not self.available:
            raise RuntimeError(self.unavailable_reason or "ML 모델을 사용할 수 없습니다.")

        import numpy as np
        import xgboost as xgb

        rule_vector = [0.0] * len(self.rule_ids)
        rule_index = self._rule_indexes.get(rule_id)
        if rule_index is not None:
            rule_vector[rule_index] = 1.0

        numeric_vector = [
            (float(features[column]) - self._scaler_mean[index])
            / self._scaler_scale[index]
            for index, column in enumerate(self.feature_columns)
        ]
        matrix = np.asarray([rule_vector + numeric_vector], dtype=np.float32)
        probability = float(self.model.predict(xgb.DMatrix(matrix))[0])
        return max(0.0, min(1.0, probability))
