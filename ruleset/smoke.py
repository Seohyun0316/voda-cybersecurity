"""End-to-end smoke/regression tests for ruleset.toml v1.x."""

import sys

from collect_github_code import RULE_FILE, load_rule_set, prepare_rules, scan_content

DATA = load_rule_set(RULE_FILE)
if not str(DATA.get("version", "")).startswith("1."):
    raise ValueError(f"ruleset v1.x is required, got {DATA.get('version')!r}")
RULES = {rule["id"]: rule for rule in prepare_rules(DATA)}


# One intentional positive fixture for every v1.0.0 rule. Exact ID coverage is
# checked below, so adding/removing a rule requires an explicit smoke decision.
POSITIVE_CASES = {
    "PII-200-001": 'password = "hunter22"',
    "PII-201-001": "return jsonify(current_user)",
    "PII-201-002": 'return jsonify({"password": password})',
    "PII-209-001": 'return jsonify({"error": str(e)})',
    "PII-359-001": "admin@company.com",
    "PII-359-003": "990101-1234567",
    "PII-532-001": "logger.info(password)",
    "PII-598-001": 'requests.get(url, params={"token": token})',
    "A02-352-001": "@csrf_exempt",
    "A02-352-002": "WTF_CSRF_ENABLED = False",
    "A02-352-003": 'excluded_methods = ["POST", "DELETE"]',
    "A02-434-001": "uploaded_file.save(uploaded_file.filename)",
    "A02-434-002": "request.files['file'].save('/tmp/uploaded')",
    "A02-434-003": "files = request.files.getlist('file')",
    "A02-862-001": 'app.get("/admin", handler)',
    "A02-862-002": '@app.get("/admin")\ndef admin_panel():',
    "A02-862-003": "class AdminView(APIView):\n    permission_classes = [AllowAny]",
    "A02-295-001": "requests.get(url, verify=False)",
    "A02-295-002": "ssl._create_unverified_context()",
    "A02-295-003": 'process.env.NODE_TLS_REJECT_UNAUTHORIZED = "0"',
    "A04-256-001": "user.password = password\ndb.session.add(user)",
    "A04-327-001": "hashlib.md5(data)",
    "A04-330-001": "token = random.randint(0, 999999)",
    "A04-798-001": 'DB_PASSWORD = "supersecret1"',
    "A04-798-002": 'OPENAI_API_KEY = "sk-abc123def456ghi789"',
    "A04-798-003": 'ACCESS_TOKEN = "ghp_1234567890abcdefghij"',
    "A04-798-004": "-----BEGIN PRIVATE KEY-----\nsecret\n-----END PRIVATE KEY-----",
    "A04-798-005": 'uri = "postgres://user:hunter2@db/app"',
    "A05-20-001": 'redirect(request.args["next"])',
    "A05-20-002": "res.redirect(req.query.next)",
    "A05-22-001": 'open(request.args["path"])',
    "A05-78-001": "os.system(command)",
    "A05-78-002": "subprocess.run(command, shell=True)",
    "A05-78-003": "exec(`ls ${userInput}`)",
    "A05-78-004": "spawn(command, { shell: true })",
    "A05-89-001": 'cursor.execute("SELECT * FROM users WHERE id=" + user_id)',
    "A05-89-002": "db.query(`SELECT * FROM users WHERE id=${userId}`)",
    "A05-94-001": "eval(request.data)",
    "A05-94-002": "eval(req.body.code)",
    "A05-79-001": "element.innerHTML = userInput",
    "A05-79-002": 'element.insertAdjacentHTML("beforeend", userContent)',
    "A05-79-003": "dangerouslySetInnerHTML={{ __html: userContent }}",
    "A05-79-004": "res.send(`<div>${userInput}</div>`)",
    "A05-79-005": "render_template_string(request.data)",
    "A05-502-001": "pickle.loads(request.data)",
    "A05-502-002": "pickle.loads(untrusted_data)",
    "A05-502-003": "yaml.load(untrusted_data)",
    "A05-502-004": "serializer.deserialize(req.body)",
    "A05-918-001": 'requests.get(request.args["url"])',
    "A05-918-002": "requests.get(target_url)",
    "A05-918-003": "fetch(req.query.url)",
    "A05-918-004": "axios.get(targetUrl)",
    "A05-918-005": "axios({ url: req.body.url })",
    "A10-770-001": 'for i in range(int(request.args["count"])):',
    "A10-770-002": "for (let i = 0; i < req.query.count; i++) {}",
    "A10-770-003": 'buf = bytearray(int(request.args["size"]))',
    "A10-770-004": "const buf = Buffer.alloc(Number(req.body.size))",
    "A10-770-005": "requests.get(url, timeout=None)",
    "A10-770-006": "server.setTimeout(0)",
    "A10-770-007": "MAX_CONTENT_LENGTH = None",
}


# High-value false-positive regressions. These supplement full positive coverage.
NEGATIVE_CASES = [
    ("A04-327-001", 'crypto.createHash("sha256")'),
    ("A04-327-001", 'hashlib.new("sha256", data)'),
    ("PII-201-002", 'return jsonify({"masked_password": masked_password})'),
    ("PII-200-001", 'API_KEY = os.getenv("API_KEY")'),
    ("A04-798-005", "postgres://user:${PW}@host/db"),
    ("A04-330-001", "token = secrets.token_hex(16)"),
    ("A05-502-003", "yaml.load(data, Loader=yaml.SafeLoader)"),
    ("A02-295-001", "requests.get(url, verify=True)"),
]


# Naming-style regressions for sensitive identifiers. These ensure the scoped
# camelCase boundary remains compatible with the existing snake/constant cases.
NAMING_CASES = [
    ("PII-200-001", 'userApiKey = "prod-secret-value"'),
    ("PII-532-001", "logger.info(userApiKey)"),
    ("A04-330-001", "userToken = random.randint(0, 999999)"),
    ("A04-798-001", 'userPassword = "prod-secret-value"'),
    ("A04-798-002", 'userApiKey = "sk-abc123def456ghi789"'),
    ("A04-798-003", 'adminToken = "ghp_1234567890abcdefghij"'),
]


# Each source must match the raw rule and then be suppressed by a content allowlist.
ALLOWLIST_CASES = [
    ("PII-200-001", 'test_token = "test"'),
    ("A04-798-003", 'sample_token = "sample"'),
    ("PII-200-001", '"Access-Control-Allow-Credentials": "true"'),
    ("A04-798-001", "'Access-Control-Allow-Credentials': 'true'"),
    ("PII-532-001", "print(masked(password))"),
    ("A04-327-001", "hashlib.md5(data, usedforsecurity=False)"),
    (
        "A04-798-004",
        "-----BEGIN PRIVATE KEY-----\nplaceholder\n-----END PRIVATE KEY-----",
    ),
    ("A04-798-005", "postgres://user:placeholder@db/app"),
]


def run():
    failures = []
    rule_ids = set(RULES)
    fixture_ids = set(POSITIVE_CASES)

    for missing in sorted(rule_ids - fixture_ids):
        failures.append(f"missing positive fixture: {missing}")
    for stale in sorted(fixture_ids - rule_ids):
        failures.append(f"fixture references unknown rule: {stale}")

    for rule_id in sorted(rule_ids & fixture_ids):
        try:
            matched = bool(
                scan_content(
                    POSITIVE_CASES[rule_id],
                    RULES[rule_id],
                    file_path="src/smoke_target.py",
                )
            )
        except Exception as exc:
            failures.append(f"{rule_id} end-to-end scan error: {exc}")
            continue
        print(f"{'PASS' if matched else 'FAIL':4s} positive {rule_id}")
        if not matched:
            failures.append(f"{rule_id} missed positive fixture")

    for rule_id, source in NEGATIVE_CASES:
        matched = bool(
            scan_content(source, RULES[rule_id], file_path="src/smoke_target.py")
        )
        print(f"{'PASS' if not matched else 'FAIL':4s} negative {rule_id}")
        if matched:
            failures.append(f"{rule_id} matched negative fixture: {source!r}")

    for rule_id, source in NAMING_CASES:
        matched = bool(
            scan_content(source, RULES[rule_id], file_path="src/smoke_target.py")
        )
        print(f"{'PASS' if matched else 'FAIL':4s} naming {rule_id}")
        if not matched:
            failures.append(f"{rule_id} missed naming fixture: {source!r}")

    for rule_id, source in ALLOWLIST_CASES:
        raw_match = bool(RULES[rule_id]["_pattern"].search(source))
        suppressed = not scan_content(
            source, RULES[rule_id], file_path="src/smoke_target.py"
        )
        passed = raw_match and suppressed
        print(f"{'PASS' if passed else 'FAIL':4s} content allowlist {rule_id}")
        if not passed:
            failures.append(
                f"{rule_id} content allowlist was not exercised: "
                f"raw_match={raw_match}, suppressed={suppressed}, source={source!r}"
            )

    path_rules = {
        rule_id: rule for rule_id, rule in RULES.items() if rule.get("path_allowlist")
    }
    for rule_id, rule in sorted(path_rules.items()):
        source = POSITIVE_CASES[rule_id]
        production_match = bool(scan_content(source, rule, file_path="src/app.py"))
        suppressed_paths = all(
            not scan_content(source, rule, file_path=path)
            for path in (
                "test/app.py",
                "tests/app.py",
                "example/app.py",
                "examples/app.py",
                "fixture/app.py",
                "fixtures/app.py",
            )
        )
        boundary_safe = all(
            scan_content(source, rule, file_path=path)
            for path in ("contest/app.py", "src/examples_old/app.py")
        )
        passed = production_match and suppressed_paths and boundary_safe
        print(f"{'PASS' if passed else 'FAIL':4s} path allowlist {rule_id}")
        if not passed:
            failures.append(
                f"{rule_id} path allowlist failed: production_match={production_match}, "
                f"suppressed_paths={suppressed_paths}, boundary_safe={boundary_safe}"
            )

    if failures:
        print("\nSMOKE FAILURES:")
        for failure in failures:
            print(f"  - {failure}")
        return 1

    print(
        f"\nAll {len(POSITIVE_CASES)} v{DATA['version']} rules passed; "
        f"{len(NEGATIVE_CASES)} negative, {len(NAMING_CASES)} naming, "
        f"{len(ALLOWLIST_CASES)} content allowlist, "
        f"and {len(path_rules)} path allowlist checks passed."
    )
    return 0


if __name__ == "__main__":
    sys.exit(run())
