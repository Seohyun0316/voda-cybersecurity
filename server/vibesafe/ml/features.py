"""The exact 10-feature extraction used by the selected XGBoost model."""

from __future__ import annotations

import collections
import math
import re


FEATURE_COLUMNS = [
    "has_direct_source_to_sink",
    "has_dangerous_option",
    "has_safe_pattern",
    "has_hardcoded_sensitive_literal",
    "has_dynamic_string_construction",
    "has_resource_bound",
    "code_entropy",
    "code_length",
    "digit_ratio",
    "has_repeated_pattern",
]

SOURCE_RE = re.compile(
    r"""(?ix)
    \b(?:request|req)\s*\.\s*(?:args|form|values|GET|POST|json|data|body|query|params|files|stream|rawBody)\b
    |\brequest\s*\.\s*get_(?:json|data)\s*\(
    |\binput\s*\(
    |\bsys\s*\.\s*argv\b
    |\bsys\s*\.\s*stdin\b
    |\bstdin\b
    |\buser[_-]?(?:input|data|content|url|path|code|payload)\b
    |\buntrusted[_-]?(?:input|data|payload|url|file)\b
    |\buploaded[_-]?file\b
    |\b(?:response|resp)\s*\.\s*(?:content|raw|data)\b
    """
)

SINK_RE = re.compile(
    r"""(?ix)
    \b(?:execute|executemany|query|raw)\s*\(
    |\b(?:os\s*\.\s*(?:system|popen)|subprocess\s*\.\s*(?:run|call|Popen|check_call|check_output|getoutput|getstatusoutput))\s*\(
    |\b(?:eval|exec|compile)\s*\(
    |\b(?:requests|httpx)\s*\.\s*(?:get|post|put|patch|delete|request)\s*\(
    |\b(?:urllib\s*\.\s*request\s*\.\s*urlopen|urlopen)\s*\(
    |\b(?:open|send_file|send_from_directory)\s*\(
    |\.\s*(?:save|write|write_text|write_bytes)\s*\(
    |\b(?:pickle|dill|cloudpickle|marshal)\s*\.\s*(?:load|loads)\s*\(
    |\bjoblib\s*\.\s*load\s*\(
    |\byaml\s*\.\s*(?:load|load_all|unsafe_load)\s*\(
    |\b(?:render_template_string|mark_safe|Markup)\s*\(
    |\b(?:jsonify|JSONResponse|Response)\s*\(
    |\b(?:print|logger\s*\.\s*(?:debug|info|warning|warn|error|critical|exception)|logging\s*\.\s*(?:debug|info|warning|warn|error|critical|exception))\s*\(
    |\b(?:redirect|HttpResponseRedirect)\s*\(
    """
)

SANITIZE_RE = re.compile(
    r"""(?ix)
    \b(?:validate|validated|validation|sanitize|sanitized|escape|escaped|clean|cleaned|normalize|normalized
    |secure_filename|safe_join|realpath|abspath|resolve|whitelist|allowlist
    |bcrypt|argon2?|scrypt|pbkdf2|hashpw|generate_password_hash|make_password
    |secrets\s*\.\s*(?:token_[A-Za-z_]*|choice|randbelow)
    |yaml\s*\.\s*safe_load|SafeLoader|CSafeLoader|DOMPurify
    |mask|masked|redact|redacted|obfuscate|obfuscated)\b
    """
)

PARAM_QUERY_RE = re.compile(
    r"""(?ix)
    \b(?:execute|executemany|query)\s*\(
    \s*(?:[rubf]{0,2})?["'][^"'\r\n]*(?:\?|%s|%\([A-Za-z_][A-Za-z0-9_]*\)s|:[A-Za-z_][A-Za-z0-9_]*|\$\d+)[^"'\r\n]*["']
    \s*,\s*
    """
)

ENV_PLACEHOLDER_RE = re.compile(
    r"""(?ix)
    \bos\s*\.\s*getenv\s*\(
    |\bos\s*\.\s*environ\b
    |\benviron\s*\.\s*get\s*\(
    |\bprocess\s*\.\s*env\b
    |\b(?:placeholder|replace[_-]?me|your[_-]?(?:password|secret|api[_-]?key|token)
    |dummy|example|sample|mock|fixture|redacted|masked|xxxx+|test[_-]?(?:key|token|secret|password))\b
    |\busedforsecurity\s*=\s*False\b
    """
)

RESOURCE_BOUND_RE = re.compile(
    r"""(?ix)
    \b(?:timeout|connect_timeout|read_timeout|write_timeout|sock_read|sock_connect|max_size|max_length
    |max_content_length|content_length|file_size_limit|upload_limit|memory_limit|rate_limit|limit)
    \s*[:=]\s*(?!None\b|null\b|0\b)\d+(?:\.\d+)?\b
    |\b(?:ClientTimeout|Timeout)\s*\([^)\r\n]{0,300}
    \b(?:total|connect|read|sock_read|sock_connect)\s*=\s*(?!None\b)\d+(?:\.\d+)?\b
    |\b(?:MAX_CONTENT_LENGTH|DATA_UPLOAD_MAX_MEMORY_SIZE|FILE_UPLOAD_MAX_MEMORY_SIZE)
    \s*=\s*(?!None\b)\d+\b
    """
)

DANGEROUS_RE = re.compile(
    r"""(?ix)
    \bverify\s*=\s*False\b
    |\bverify_ssl\s*=\s*False\b
    |\bssl\s*=\s*False\b
    |\bcheck_hostname\s*=\s*False\b
    |\bverify_mode\s*=\s*(?:ssl\s*\.\s*)?CERT_NONE\b
    |\bcert_reqs\s*=\s*(?:ssl\s*\.\s*)?["']?CERT_NONE["']?\b
    |\bassert_hostname\s*=\s*False\b
    |\bshell\s*=\s*True\b
    |\btimeout\s*=\s*None\b
    |\bWTF_CSRF_ENABLED\b[^\r\n]{0,40}=\s*False\b
    |\bcsrf[_-]?(?:enabled|protection|protect|check|validation)\b[^\r\n]{0,20}[:=]\s*(?:False|0|None)\b
    |@\s*(?:csrf\s*\.\s*exempt|csrf_exempt)\b
    |\bpermission_classes\s*=\s*(?:\[[^\]]*\bAllowAny\b|\(\s*\)|\[\s*\])
    |\bLoader\s*=\s*(?:yaml\s*\.\s*)?(?:Loader|FullLoader|UnsafeLoader)\b
    |\b(?:DATA_UPLOAD_MAX_MEMORY_SIZE|FILE_UPLOAD_MAX_MEMORY_SIZE|MAX_CONTENT_LENGTH)\s*=\s*None\b
    """
)

SENSITIVE_ASSIGN_RE = re.compile(
    r"""(?ix)
    (?<![A-Za-z0-9_])
    (?:[A-Za-z0-9]+[_-]){0,3}
    (?:password|passwd|pwd|secret|api[_-]?key|access[_-]?key|token|credential|private[_-]?key|jwt[_-]?secret)
    (?:[_-][A-Za-z0-9]+){0,2}
    \s*(?::[^=\r\n]{0,80})?\s*[:=]\s*
    (?:[rubf]{0,2})?["'][^"'\r\n]{4,}["']
    |\b(?:AKIA|ASIA)[A-Z0-9]{16}\b
    |\b(?:sk-(?:ant-)?[A-Za-z0-9_-]{12,}|gh[pousr]_[A-Za-z0-9]{20,}|github_pat_[A-Za-z0-9_]{20,})\b
    |-----BEGIN (?:RSA |EC |DSA |OPENSSH |ENCRYPTED )?PRIVATE KEY-----
    |\b(?:mysql|postgres(?:ql)?|mongodb(?:\+srv)?|redis(?:s)?|mariadb)://[^:@\s]+:[^@\s]+@
    """
)

DYNAMIC_RE = re.compile(
    r"""(?x)
    (?:\b[fr]{1,2}["'][^"'\r\n]*\{[^}\r\n]+\}[^"'\r\n]*["'])
    |(?:["'][^"'\r\n]*["']\s*\+\s*[A-Za-z_(])
    |(?:[A-Za-z_][A-Za-z0-9_.]*\s*\+\s*["'])
    |(?:["'][^"'\r\n]*["']\s*%\s*(?:\(|[A-Za-z_]))
    |(?:["'][^"'\r\n]*["']\s*\.\s*format\s*\()
    |(?:`[^`\r\n]*\$\{[^}\r\n]+\}[^`\r\n]*`)
    """
)

STRING_RE = re.compile(
    r"""(?sx)
    (?:
        '{3}.*?'{3}
        |"{3}.*?"{3}
        |'(?:\\.|[^'\\\r\n])*'
        |"(?:\\.|[^"\\\r\n])*"
        |`(?:\\.|[^`\\\r\n])*`
    )
    """
)

SOURCE_ASSIGN_RE = re.compile(
    r"""(?ix)
    \b([A-Za-z_][A-Za-z0-9_]*)\s*=\s*
    (?:
        (?:request|req)\s*\.\s*(?:args|form|values|GET|POST|json|data|body|query|params|files)
        |request\s*\.\s*get_(?:json|data)\s*\(
        |input\s*\(
        |sys\s*\.\s*argv
        |sys\s*\.\s*stdin
        |(?:response|resp)\s*\.\s*(?:content|raw|data)
    )
    """
)


def _string_literals(code: str) -> list[str]:
    return STRING_RE.findall(code)


def _shannon_entropy(code: str) -> float:
    normalized = re.sub(r"\s", "", code)
    if not normalized:
        return 0.0
    counts = collections.Counter(normalized)
    length = len(normalized)
    return -sum(
        (count / length) * math.log2(count / length) for count in counts.values()
    )


def _has_repeated_pattern(code: str) -> int:
    for literal in _string_literals(code):
        compact = re.sub(r"\s+", "", literal.strip("'\"`"))
        if re.search(r"([^\s])\1{3,}", compact):
            return 1
        if re.search(r"([A-Za-z0-9_-]{2,8})\1{2,}", compact):
            return 1
    return 0


def _has_direct_source_to_sink(code: str) -> int:
    for line in code.splitlines():
        if SOURCE_RE.search(line) and SINK_RE.search(line):
            return 1

    for sink_match in SINK_RE.finditer(code):
        if SOURCE_RE.search(code[sink_match.start() : sink_match.start() + 500]):
            return 1

    for assignment in SOURCE_ASSIGN_RE.finditer(code):
        variable = assignment.group(1)
        flow_window = code[assignment.end() : assignment.end() + 700]
        for sink_match in SINK_RE.finditer(flow_window):
            sink_window = flow_window[sink_match.start() : sink_match.start() + 350]
            if re.search(rf"\b{re.escape(variable)}\b", sink_window):
                return 1
    return 0


def extract_features(code: str) -> dict[str, float]:
    """Return the model's 10 numeric features in training order."""
    non_whitespace = re.sub(r"\s", "", code)
    validation = bool(SANITIZE_RE.search(code))
    parameterized_query = bool(PARAM_QUERY_RE.search(code))
    environment_or_placeholder = bool(ENV_PLACEHOLDER_RE.search(code))
    resource_bound = bool(RESOURCE_BOUND_RE.search(code))

    features = {
        "has_direct_source_to_sink": _has_direct_source_to_sink(code),
        "has_dangerous_option": int(bool(DANGEROUS_RE.search(code))),
        "has_safe_pattern": int(
            validation or parameterized_query or environment_or_placeholder or resource_bound
        ),
        "has_hardcoded_sensitive_literal": int(bool(SENSITIVE_ASSIGN_RE.search(code))),
        "has_dynamic_string_construction": int(bool(DYNAMIC_RE.search(code))),
        "has_resource_bound": int(resource_bound),
        "code_entropy": round(_shannon_entropy(code), 6),
        "code_length": len(code),
        "digit_ratio": round(
            sum(character.isdigit() for character in non_whitespace) / len(non_whitespace),
            6,
        )
        if non_whitespace
        else 0.0,
        "has_repeated_pattern": _has_repeated_pattern(code),
    }
    if list(features) != FEATURE_COLUMNS:
        raise AssertionError("Feature order changed unexpectedly.")
    return {name: float(value) for name, value in features.items()}
