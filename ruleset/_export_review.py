import json, sys
from pathlib import Path

TEXT_ENCODINGS = ("utf-8", "utf-8-sig", "cp949")

def read_text(path):
    raw = path.read_bytes()
    for enc in TEXT_ENCODINGS:
        try:
            return raw.decode(enc)
        except UnicodeDecodeError:
            continue
    return None

findings_path = Path(sys.argv[1])
source_root = Path(sys.argv[2])
out_path = Path(sys.argv[3])

findings = []
with findings_path.open(encoding="utf-8") as f:
    for line in f:
        line = line.strip()
        if line:
            findings.append(json.loads(line))

with out_path.open("w", encoding="utf-8") as out:
    for idx, fnd in enumerate(findings):
        content = read_text(source_root / fnd["file"])
        lines = content.splitlines() if content else []
        start = fnd["line"]; end = fnd.get("end_line", start)
        ws = max(start - 2, 1); we = min(end + 1, len(lines))
        ctx = []
        for ln in range(ws, we + 1):
            text = lines[ln-1] if ln-1 < len(lines) else ""
            marker = ">>" if start <= ln <= end else "  "
            ctx.append(f"{marker}{ln}:{text}")
        out.write(f"### [{idx}] {fnd['file']} L{fnd['line']} {fnd['rule_id']} {fnd['severity']} model={fnd['model']}\n")
        out.write(f"desc: {fnd['desc']}\n")
        out.write("\n".join(ctx) + "\n\n")

print(f"wrote {len(findings)} entries to {out_path}")
