import re

import pytest

from app import create_app
from vibesafe.rule_engine import RuleEngine


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
    assert body["rule_engine"] == {"status": "ready", "rules_loaded": 32}
    assert body["ml"]["status"] == "ready"
    assert body["ml"]["available"] is True
    assert body["ml"]["feature_count"] == 10
    assert body["ml"]["known_rule_count"] == 29
    assert body["ml"]["risk_score_policy"] == "pending_team_decision"


def test_detect_returns_rule_finding_and_pending_score(client):
    code = 'password = "super-secret-value"'
    response = client.post(
        "/detect",
        json={"code": code, "language": "python", "file_name": "auth.py"},
    )

    assert response.status_code == 200
    body = response.get_json()
    finding = next(item for item in body["findings"] if item["rule_id"] == "A04-798-001")
    assert body["risk_score"] is None
    assert finding["cwe"] == "CWE-798"
    assert finding["category"] == "secret"
    assert finding["severity"] == "high"
    assert finding["line"] == 0
    assert finding["start_col"] == 0
    assert finding["end_col"] == len(code)
    assert finding["legal"]["law"] == "개인정보보호법"
    assert finding["fix"]["title"] == "환경변수로 교체"
    assert re.fullmatch(r"\d{4}-\d{2}-\d{2}T.*Z", body["analyzed_at"])


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
    }
    rule_only_ids = {"A04-256-001", "A04-798-004", "A10-770-003"}

    assert len(active_rule_ids) == 32
    assert excluded_rule_ids.isdisjoint(active_rule_ids)
    assert rule_only_ids <= active_rule_ids
