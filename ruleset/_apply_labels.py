import json
from pathlib import Path

FALSE_INDICES = {
    11, 12, 16, 36, 37, 65, 67, 69, 128, 167, 182, 185, 186,
    196, 200, 201, 204, 237, 252, 266, 267, 299, 321, 322, 329,
    334, 340, 341, 344, 347, 385, 386, 387, 389, 394, 395, 402,
    413, 414, 415, 416, 417, 429, 438, 440, 472, 483, 489, 496,
    504, 505, 512, 513, 516, 517, 520, 521, 527, 528,
}

path = Path("output/ai_generated_findings.jsonl")
findings = []
with path.open(encoding="utf-8") as f:
    for line in f:
        line = line.strip()
        if line:
            findings.append(json.loads(line))

assert len(findings) == 530, f"expected 530, got {len(findings)}"

for idx, fnd in enumerate(findings):
    fnd["label"] = False if idx in FALSE_INDICES else True
    fnd["labeled_by"] = "claude_review"

with path.open("w", encoding="utf-8") as f:
    for fnd in findings:
        f.write(json.dumps(fnd, ensure_ascii=False) + "\n")

true_n = sum(1 for f in findings if f["label"] is True)
false_n = sum(1 for f in findings if f["label"] is False)
print(f"total={len(findings)} true={true_n} false={false_n}")
