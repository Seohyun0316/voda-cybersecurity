import pytest

from vibesafe.risk_scoring import finding_risk_score, risk_score


@pytest.mark.parametrize(
    ("cwe", "severity", "expected"),
    [
        ("CWE-798", "high", 75),
        ("CWE-532", "high", 60),
        ("CWE-295", "high", 40),
        ("CWE-79", "high", 40),
        ("CWE-89", "high", 25),
        ("CWE-434", "high", 20),
        ("CWE-256", "high", 20),
        ("CWE-201", "high", 15),
        ("CWE-502", "high", 13.33),
        ("CWE-200", "high", 12.5),
        ("CWE-359", "high", 12.5),
        ("CWE-918", "high", 12.5),
        ("CWE-209", "medium", 10),
        ("CWE-352", "high", 10),
        ("CWE-862", "high", 10),
        ("CWE-327", "high", 10),
        ("CWE-22", "high", 10),
        ("CWE-77, CWE-78", "high", 10),
        ("CWE-94", "high", 10),
        ("CWE-20", "medium", 6.67),
        ("CWE-330", "medium", 5),
        ("CWE-770", "high", 3.75),
    ],
)
def test_pdf_risk_table(cwe, severity, expected):
    finding = {
        "cwe": cwe,
        "severity": severity,
        # Known CWE mappings must use the PDF's legal weights, even if display
        # metadata differs.
        "legal": {"liability": 3, "sanction": 2},
    }

    assert finding_risk_score(finding) == expected


def test_critical_deserialization_uses_technical_weight_four():
    assert finding_risk_score({"cwe": "CWE-502", "severity": "low"}) == 13.33


def test_file_score_is_maximum_remaining_finding_not_sum():
    hardcoded_credential = {"cwe": "CWE-798", "severity": "high"}
    sensitive_log = {"cwe": "CWE-532", "severity": "high"}

    assert risk_score([hardcoded_credential, sensitive_log]) == 75
    assert risk_score([sensitive_log]) == 60
    assert risk_score([]) == 0
