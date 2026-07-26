import hashlib
import json
from pathlib import Path

import pytest

from vibesafe.detector import DEFAULT_MODEL, DEFAULT_MODEL_METADATA, Detector
from vibesafe.ml.features import FEATURE_COLUMNS, extract_features
from vibesafe.ml.predictor import Predictor


MODEL_DIR = Path("models/xgboost_10f")
EXPECTED_SECRET_PROBABILITY = 0.961687445640564


def test_feature_extractor_returns_training_order():
    features = extract_features(
        'cmd = request.args["cmd"]\nsubprocess.run(cmd, shell=True)'
    )

    assert list(features) == FEATURE_COLUMNS
    assert len(features) == 10
    assert features["has_direct_source_to_sink"] == 1.0
    assert features["has_dangerous_option"] == 1.0
    assert features["has_safe_pattern"] == 0.0


def test_portable_model_and_metadata_are_consistent():
    metadata = json.loads(DEFAULT_MODEL_METADATA.read_text(encoding="utf-8"))
    source_hash = hashlib.sha256((MODEL_DIR / "source_bundle.pkl").read_bytes()).hexdigest()

    assert DEFAULT_MODEL.is_file()
    assert metadata["feature_columns"] == FEATURE_COLUMNS
    assert metadata["source_bundle_sha256"] == source_hash
    assert len(metadata["rule_ids"]) == 29
    assert len(metadata["scaler_mean"]) == 10
    assert len(metadata["scaler_scale"]) == 10


def test_predictor_scores_known_rule():
    predictor = Predictor(DEFAULT_MODEL, DEFAULT_MODEL_METADATA)
    features = extract_features('password = "super-secret-value"')

    assert predictor.available is True
    assert predictor.knows_rule("A04-798-001") is True
    probability = predictor.predict_vulnerable_probability("A04-798-001", features)
    assert probability == pytest.approx(EXPECTED_SECRET_PROBABILITY, abs=1e-6)


# 프로젝트에서 미학습 룰을 모두 제외하여 더 이상 활성 룰 대상 테스트가 아니다.
# def test_predictor_handles_rule_unseen_during_training():
#     predictor = Predictor(DEFAULT_MODEL, DEFAULT_MODEL_METADATA)
#     features = extract_features(
#         'user = User(password=request.form["password"]); db.session.add(user)'
#     )
#
#     assert predictor.knows_rule("A04-256-001") is False
#     probability = predictor.predict_vulnerable_probability("A04-256-001", features)
#     assert 0.0 <= probability <= 1.0


def test_detector_exposes_probabilities_without_aggregating():
    detector = Detector()
    code = 'password = "super-secret-value"'
    result = detector.detect(code, "python", "auth.py")

    scores = detector.score_candidates(code, result["findings"])
    assert result["risk_score"] is None
    assert scores["A04-798-001"] == pytest.approx(
        EXPECTED_SECRET_PROBABILITY, abs=1e-6
    )
