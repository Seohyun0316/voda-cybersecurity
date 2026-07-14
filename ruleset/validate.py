from pathlib import Path

import tomllib, re, regex, sys

RULE_FILE = Path(__file__).resolve().parent / "ruleset.toml"

with RULE_FILE.open("rb") as f:
    data = tomllib.load(f)

ks = data["keyword_sets"]
alts = {k: "(?:" + "|".join(v) + ")" for k, v in ks.items()}


def expand(pat):
    def repl(m):
        name = m.group(1)
        if name in alts:
            return alts[name]
        return m.group(0)

    return re.sub(r"\{([a-z_]+)\}", repl, pat)


def try_compile(label, pat):
    results = []
    for mod, name in ((re, "re"), (regex, "regex")):
        try:
            mod.compile(pat)
            results.append((name, "OK", None))
        except Exception as e:
            results.append((name, "FAIL", str(e)))
    return results


report = []
for rule in data["rules"]:
    rid = rule["id"]
    pat = expand(rule["regex"])
    for name, status, err in try_compile("regex", pat):
        if status == "FAIL":
            report.append(f"[{rid}] regex ({name}): {err}")
    for i, al in enumerate(rule.get("allowlist", [])):
        for name, status, err in try_compile("allow", expand(al)):
            if status == "FAIL":
                report.append(f"[{rid}] allowlist[{i}] ({name}): {err}")
    for i, al in enumerate(rule.get("path_allowlist", [])):
        for name, status, err in try_compile("path_allow", expand(al)):
            if status == "FAIL":
                report.append(f"[{rid}] path_allowlist[{i}] ({name}): {err}")

if report:
    print("COMPILE ERRORS:")
    print("\n".join(report))
else:
    print("All patterns compile under both re and regex.")
