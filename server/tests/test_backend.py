import re

import pytest

from app import create_app
from vibesafe.rule_engine import (
    CATEGORY_BY_CWE,
    FIX_BY_CWE,
    LEGAL_BY_CWE,
    WARNING_BY_CWE,
    CompiledRule,
    RuleEngine,
)


@pytest.fixture()
def client():
    app = create_app()
    app.config.update(TESTING=True)
    with app.test_client() as test_client:
        yield test_client


def test_health_reports_rule_and_model_readiness(client):
    response = client.get("/health")

    assert response.status_code == 200
    body = response.get_json()
    assert body["status"] == "ok"
    assert body["rule_engine"] == {"status": "ready", "rules_loaded": 29}
    assert body["ml"]["status"] == "ready"
    assert body["ml"]["available"] is True
    assert body["ml"]["feature_count"] == 10
    assert body["ml"]["known_rule_count"] == 29
    assert body["ml"]["risk_score_policy"] == "pending_team_decision"


def test_detect_returns_candidate_accepted_by_ml_filter(client):
    code = 'password = "super-secret-value"'
    response = client.post(
        "/detect",
        json={"code": code, "language": "python", "file_name": "auth.py"},
    )

    assert response.status_code == 200
    body = response.get_json()
    finding = next(item for item in body["findings"] if item["rule_id"] == "A04-798-001")
    assert body["risk_score"] is None
    assert "ml_probability" not in finding
    assert finding["cwe"] == "CWE-798"
    assert finding["category"] == "secret"
    assert finding["severity"] == "high"
    assert finding["line"] == 0
    assert finding["start_col"] == 0
    assert finding["end_col"] == len(code)
    assert finding["legal"]["law"] == "개인정보보호법"
    assert finding["fix"]["title"] == "환경변수로 교체"
    assert re.fullmatch(r"\d{4}-\d{2}-\d{2}T.*Z", body["analyzed_at"])


def test_detect_returns_pending_risk_when_no_rule_candidate_exists(client):
    response = client.post(
        "/detect",
        json={
            "code": "def add(left, right):\n    return left + right",
            "language": "python",
            "file_name": "math_utils.py",
        },
    )

    assert response.status_code == 200
    assert response.get_json()["findings"] == []
    assert response.get_json()["risk_score"] is None


def test_detect_uses_zero_based_line_and_column(client):
    response = client.post(
        "/detect",
        json={
            "code": 'safe = True\n    api_key = "1234567890abcdef"',
            "language": "Python",
            "file_name": "settings.py",
        },
    )

    finding = next(
        item
        for item in response.get_json()["findings"]
        if item["rule_id"] == "A04-798-002"
    )
    assert finding["line"] == 1
    assert finding["start_col"] == 4


@pytest.mark.parametrize(
    "payload,error_fragment",
    [
        (None, "JSON 객체"),
        ({"language": "python", "file_name": "a.py"}, "code"),
        ({"code": "", "language": "java", "file_name": "A.java"}, "python"),
        ({"code": "", "language": "python", "file_name": ""}, "file_name"),
    ],
)
def test_detect_validates_request(client, payload, error_fragment):
    response = client.post("/detect", json=payload)

    assert response.status_code == 400
    assert error_fragment in response.get_json()["error"]


def test_test_path_is_excluded_by_path_allowlist():
    engine = RuleEngine("config/ruleset.toml")
    code = 'open(request.args["path"]).read()'

    normal_findings = engine.detect(code, "python", "handlers/download.py")
    test_findings = engine.detect(code, "python", "tests/test_download.py")

    assert any(item["rule_id"] == "A05-22-001" for item in normal_findings)
    assert not any(item["rule_id"] == "A05-22-001" for item in test_findings)


def test_project_rule_scope():
    engine = RuleEngine("config/ruleset.toml")
    active_rule_ids = {rule.rule_id for rule in engine.rules}
    excluded_rule_ids = {
        "PII-359-001",
        "A02-352-003",
        "A02-434-002",
        "A02-434-003",
        "A02-862-002",
        "A05-918-002",
        "A05-918-005",
        "A10-770-001",
        "A04-256-001",
        "A04-798-004",
        "A10-770-003",
    }

    assert len(active_rule_ids) == 29
    assert excluded_rule_ids.isdisjoint(active_rule_ids)


def test_every_documented_cwe_has_hardcoded_finding_metadata():
    expected_weights = {
        "CWE-20": 4,
        "CWE-22": 4,
        "CWE-77": 5,
        "CWE-78": 5,
        "CWE-79": 4,
        "CWE-89": 5,
        "CWE-94": 5,
        "CWE-200": 5,
        "CWE-201": 3,
        "CWE-209": 1.5,
        "CWE-256": 4,
        "CWE-295": 4,
        "CWE-307": 3,
        "CWE-327": 4,
        "CWE-330": 1.5,
        "CWE-352": 4,
        "CWE-359": 5,
        "CWE-434": 5,
        "CWE-502": 5,
        "CWE-532": 4,
        "CWE-770": 1.5,
        "CWE-798": 5,
        "CWE-862": 4,
        "CWE-918": 5,
    }
    documented_cwes = set(expected_weights)

    assert set(CATEGORY_BY_CWE) == documented_cwes
    assert set(FIX_BY_CWE) == documented_cwes
    assert set(WARNING_BY_CWE) == documented_cwes
    assert set(LEGAL_BY_CWE) == documented_cwes

    for cwe, expected_weight in expected_weights.items():
        rule = CompiledRule(
            rule_id=f"TEST-{cwe}",
            name="테스트 규칙",
            description="테스트 설명",
            severity="high",
            cwes=(cwe,),
            pattern=re.compile("unsafe"),
            allowlist=(),
            path_allowlist=(),
        )

        finding = RuleEngine._to_finding(rule, line=0, start_col=0, end_col=6)
        legal = finding["legal"]

        assert finding["category"] == CATEGORY_BY_CWE[cwe]
        assert finding["message"] == WARNING_BY_CWE[cwe]
        assert finding["fix"]["title"] == FIX_BY_CWE[cwe][0]
        assert legal == LEGAL_BY_CWE[cwe]
        assert legal["liability"] + legal["sanction"] == expected_weight
        assert "위반 소지가 있습니다" in legal["description"]


def test_every_active_rule_uses_a_documented_legal_mapping():
    engine = RuleEngine("config/ruleset.toml")

    for rule in engine.rules:
        assert rule.cwes
        assert rule.cwes[0] in LEGAL_BY_CWE


def test_critical_deserialization_rule_is_normalized_to_high():
    engine = RuleEngine("config/ruleset.toml")
    rule = next(rule for rule in engine.rules if rule.rule_id == "A05-502-001")

    assert rule.severity == "high"

    findings = engine.detect(
        "pickle.loads(request.data)",
        language="python",
        file_name="deserialize.py",
    )
    finding = next(item for item in findings if item["rule_id"] == "A05-502-001")

    assert finding["severity"] == "high"
