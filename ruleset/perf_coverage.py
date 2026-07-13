"""Performance and full positive-coverage check for ruleset.toml v1.x.

Usage: python perf_coverage.py
"""

from pathlib import Path
from statistics import median
import re
import sys
import time
import tomllib

import regex

from smoke import POSITIVE_CASES

RULE_FILE = Path(__file__).resolve().parent / "ruleset.toml"
SEARCH_TIMEOUT_SECONDS = 1.0
BENCHMARK_REPEATS = 5


def load_ruleset():
    with RULE_FILE.open("rb") as f:
        data = tomllib.load(f)

    version = str(data.get("version", ""))
    if not version.startswith("1."):
        raise ValueError(f"ruleset v1.x is required, got {version!r}")

    keyword_sets = data.get("keyword_sets")
    rules = data.get("rules")
    if not isinstance(keyword_sets, dict) or not isinstance(rules, list):
        raise ValueError("ruleset must contain keyword_sets and rules")

    alternatives = {
        name: "(?:" + "|".join(values) + ")" for name, values in keyword_sets.items()
    }

    def expand(pattern):
        return re.sub(
            r"\{([a-z_]+)\}",
            lambda match: alternatives.get(match.group(1), match.group(0)),
            pattern,
        )

    return data, rules, expand


def compile_rules(rules, expand):
    compiled = []
    timings = []
    for rule in rules:
        start = time.perf_counter()
        pattern = regex.compile(expand(rule["regex"]))
        timings.append(((time.perf_counter() - start) * 1000, rule["id"]))
        compiled.append((rule["id"], pattern))
    return compiled, timings


def timed_search(pattern, source):
    samples = []
    for _ in range(BENCHMARK_REPEATS):
        start = time.perf_counter()
        pattern.search(source, timeout=SEARCH_TIMEOUT_SECONDS)
        samples.append((time.perf_counter() - start) * 1000)
    return median(samples)


def main():
    data, rules, expand = load_ruleset()
    failures = []

    rule_ids = [rule.get("id") for rule in rules]
    if len(rule_ids) != len(set(rule_ids)):
        failures.append("duplicate rule IDs found")

    fixture_ids = set(POSITIVE_CASES)
    missing_fixtures = set(rule_ids) - fixture_ids
    stale_fixtures = fixture_ids - set(rule_ids)
    failures.extend(
        f"missing coverage fixture: {rid}" for rid in sorted(missing_fixtures)
    )
    failures.extend(
        f"unknown coverage fixture: {rid}" for rid in sorted(stale_fixtures)
    )

    try:
        compiled, compile_timings = compile_rules(rules, expand)
    except Exception as exc:
        print(f"COMPILE FAILURE: {exc}")
        return 1

    normal = (
        "import os\n" + "def handler(req):\n    value = compute(req.data)\n"
        "    result = value * 2\n    return result\n" * 100
    )
    pathological = {
        "normal500": normal,
        "open-call": "print(" + "aaa, " * 800 + "\n" + "logger.info(" + "x" * 2000,
        "secret-list": "db.session.add(" + "password, " * 300,
    }

    search_timings = []
    for rule_id, pattern in compiled:
        for scenario, source in pathological.items():
            try:
                duration = timed_search(pattern, source)
                search_timings.append((duration, rule_id, scenario))
            except TimeoutError:
                failures.append(
                    f"{rule_id} timed out on {scenario} "
                    f"(>{SEARCH_TIMEOUT_SECONDS:.1f}s)"
                )

    print(f"ruleset v{data['version']}: {len(rules)} rules")
    print("\nSlowest compile operations (ms):")
    for duration, rule_id in sorted(compile_timings, reverse=True)[:10]:
        print(f"  {duration:8.2f} ms  {rule_id}")

    print(
        f"\nSlowest searches: median of {BENCHMARK_REPEATS} runs "
        f"(timeout {SEARCH_TIMEOUT_SECONDS:.1f}s)"
    )
    for duration, rule_id, scenario in sorted(search_timings, reverse=True)[:10]:
        print(f"  {duration:8.2f} ms  {rule_id:12s} on {scenario}")

    print("\nFull v1 positive coverage:")
    coverage_passed = 0
    for expected_id in sorted(set(rule_ids) & fixture_ids):
        source = POSITIVE_CASES[expected_id]
        try:
            hits = [
                rule_id
                for rule_id, pattern in compiled
                if pattern.search(source, timeout=SEARCH_TIMEOUT_SECONDS)
            ]
        except TimeoutError:
            failures.append(f"coverage search timed out for fixture {expected_id}")
            print(f"  FAIL {expected_id}: timeout")
            continue

        passed = expected_id in hits
        print(f"  {'PASS' if passed else 'FAIL'} {expected_id} -> {hits}")
        if passed:
            coverage_passed += 1
        else:
            failures.append(f"{expected_id} did not match its positive fixture")

    if failures:
        print("\nPERFORMANCE/COVERAGE FAILURES:")
        for failure in failures:
            print(f"  - {failure}")
        return 1

    print(
        f"\nAll {coverage_passed}/{len(rules)} rules detected their v1 fixtures; "
        "no performance timeout occurred."
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
