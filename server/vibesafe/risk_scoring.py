"""PDF-defined VibeSafe risk scoring policy.

Each finding is scored independently and the file-level score is the highest
remaining finding score.  This makes the score fall as the most severe
findings are fixed instead of growing with duplicate matches.
"""

from __future__ import annotations

import re
from collections.abc import Iterable, Mapping
from typing import Any

MAX_RAW_SCORE = 3 * 4 * 5
DEFAULT_FREQUENCY_SCORE = 0.5
DEFAULT_LEGAL_WEIGHT = 1.5

FREQUENCY_SCORE_BY_CWE: dict[str, float] = {
    "CWE-798": 3,
    "CWE-532": 3,
    "CWE-295": 2,
    "CWE-79": 2,
    "CWE-89": 1,
    "CWE-434": 1,
    "CWE-256": 1,
    "CWE-201": 1,
    "CWE-502": 0.5,
    "CWE-200": 0.5,
    "CWE-359": 0.5,
    "CWE-918": 0.5,
    "CWE-209": 2,
    "CWE-352": 0.5,
    "CWE-862": 0.5,
    "CWE-327": 0.5,
    "CWE-22": 0.5,
    "CWE-77": 0.5,
    "CWE-78": 0.5,
    "CWE-94": 0.5,
    "CWE-20": 0.5,
    "CWE-330": 1,
    "CWE-770": 0.5,
}

LEGAL_WEIGHT_BY_CWE: dict[str, float] = {
    "CWE-798": 5,
    "CWE-532": 4,
    "CWE-295": 4,
    "CWE-79": 4,
    "CWE-89": 5,
    "CWE-434": 4,
    "CWE-256": 4,
    "CWE-201": 3,
    "CWE-502": 4,
    "CWE-200": 5,
    "CWE-359": 5,
    "CWE-918": 5,
    "CWE-209": 1.5,
    "CWE-352": 4,
    "CWE-862": 4,
    "CWE-327": 4,
    "CWE-22": 4,
    "CWE-77": 4,
    "CWE-78": 4,
    "CWE-94": 4,
    "CWE-20": 4,
    "CWE-330": 1.5,
    "CWE-770": 1.5,
}

TECHNICAL_SEVERITY_WEIGHT = {
    "high": 3,
    "medium": 2,
    "low": 1,
}

_CWE_PATTERN = re.compile(r"CWE-\d+", re.IGNORECASE)


def _cwes(value: object) -> tuple[str, ...]:
    if not isinstance(value, str):
        return ()
    return tuple(match.upper() for match in _CWE_PATTERN.findall(value))


def _fallback_legal_weight(finding: Mapping[str, Any]) -> float:
    legal = finding.get("legal")
    if not isinstance(legal, Mapping):
        return DEFAULT_LEGAL_WEIGHT

    liability = legal.get("liability")
    sanction = legal.get("sanction")
    if isinstance(liability, (int, float)) and isinstance(sanction, (int, float)):
        return min(5.0, max(DEFAULT_LEGAL_WEIGHT, float(liability + sanction)))
    return DEFAULT_LEGAL_WEIGHT


def finding_risk_score(finding: Mapping[str, Any]) -> float:
    """Return a finding's normalized 0-100 score, rounded to two decimals."""
    cwes = _cwes(finding.get("cwe"))
    severity = str(finding.get("severity", "")).lower()
    default_technical_weight = TECHNICAL_SEVERITY_WEIGHT.get(severity, 1)
    fallback_legal_weight = _fallback_legal_weight(finding)

    candidates = cwes or ("",)
    raw_scores = []
    for cwe in candidates:
        frequency = FREQUENCY_SCORE_BY_CWE.get(cwe, DEFAULT_FREQUENCY_SCORE)
        technical = 4 if cwe == "CWE-502" else default_technical_weight
        legal = LEGAL_WEIGHT_BY_CWE.get(cwe, fallback_legal_weight)
        raw_scores.append(frequency * technical * legal)

    normalized = max(raw_scores, default=0.0) / MAX_RAW_SCORE * 100
    return round(min(100.0, max(0.0, normalized)), 2)


def risk_score(findings: Iterable[Mapping[str, Any]]) -> float:
    """Return the maximum score among the currently remaining findings."""
    return max((finding_risk_score(finding) for finding in findings), default=0.0)
