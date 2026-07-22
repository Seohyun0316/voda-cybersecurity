"""Coordinates rule detection and the optional ML candidate scorer."""

from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from vibesafe.ml.features import extract_features
from vibesafe.ml.predictor import Predictor
from vibesafe.rule_engine import RuleEngine


PROJECT_ROOT = Path(__file__).resolve().parent.parent
DEFAULT_RULESET = PROJECT_ROOT / "config" / "ruleset.toml"
DEFAULT_MODEL = PROJECT_ROOT / "models" / "xgboost_10f" / "model.json"
DEFAULT_MODEL_METADATA = PROJECT_ROOT / "models" / "xgboost_10f" / "metadata.json"


class Detector:
    def __init__(
        self,
        ruleset_path: str | Path = DEFAULT_RULESET,
        model_path: str | Path = DEFAULT_MODEL,
        model_metadata_path: str | Path = DEFAULT_MODEL_METADATA,
    ) -> None:
        self.rule_engine = RuleEngine(ruleset_path)
        self.predictor = Predictor(model_path, model_metadata_path)

    @property
    def rule_count(self) -> int:
        return self.rule_engine.rule_count

    @property
    def ml_status(self) -> dict[str, object]:
        return {
            "status": "ready" if self.predictor.available else "unavailable",
            "available": self.predictor.available,
            "reason": self.predictor.unavailable_reason,
            "feature_count": len(self.predictor.feature_columns),
            "known_rule_count": self.predictor.known_rule_count,
            "risk_score_policy": "pending_team_decision",
        }

    def score_candidates(
        self, code: str, findings: list[dict[str, Any]]
    ) -> dict[str, float]:
        """Return per-rule probabilities without imposing an aggregation policy."""
        if not self.predictor.available:
            return {}
        features = extract_features(code)
        return {
            rule_id: self.predictor.predict_vulnerable_probability(rule_id, features)
            for rule_id in {str(finding["rule_id"]) for finding in findings}
        }

    def detect(self, code: str, language: str, file_name: str) -> dict[str, object]:
        findings = self.rule_engine.detect(code, language, file_name)

        # The model produces a probability per rule candidate. The team has not
        # defined how multiple probabilities become one API risk score, so the
        # public field intentionally remains null instead of inventing a policy.
        analyzed_at = datetime.now(timezone.utc).isoformat(timespec="milliseconds")
        return {
            "risk_score": None,
            "findings": findings,
            "analyzed_at": analyzed_at.replace("+00:00", "Z"),
        }
