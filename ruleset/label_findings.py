"""findings.jsonl 대화형 라벨링 CLI.

scan_local_dataset.py가 뽑아낸 findings(label: null)를 하나씩 터미널에
보여주고, 사람이 y/n/s로 판정하면 그 자리에서 label을 채워 저장한다.
LightGBM 2차 오탐 필터 학습에 쓸 라벨 데이터를 만드는 게 목적이다.

사용법:
  cd ruleset
  python label_findings.py output/ai_generated_findings.jsonl ../data/ai_generated

조작:
  y = 진짜 위험            -> label: true
  n = 오탐(false positive)  -> label: false
  s = 모르겠음, 나중에      -> 건너뜀 (label은 null로 유지)
  u = 방금 판정 취소하고 다시 보기
  q = 저장하고 종료

한 건 답할 때마다 즉시 파일에 저장하므로 중간에 Ctrl+C로 끊어도 안전하다.
다시 실행하면 아직 label이 null인 항목부터 이어서 진행한다.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

TEXT_ENCODINGS = ("utf-8", "utf-8-sig", "cp949")


def read_text_robust(path: Path) -> str | None:
    try:
        raw = path.read_bytes()
    except OSError:
        return None
    for encoding in TEXT_ENCODINGS:
        try:
            return raw.decode(encoding)
        except UnicodeDecodeError:
            continue
    return None


def load_findings(path: Path) -> list[dict]:
    findings = []
    with path.open("r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                findings.append(json.loads(line))
    return findings


def save_findings(path: Path, findings: list[dict]) -> None:
    tmp_path = path.with_suffix(path.suffix + ".tmp")
    with tmp_path.open("w", encoding="utf-8") as f:
        for finding in findings:
            f.write(json.dumps(finding, ensure_ascii=False) + "\n")
    tmp_path.replace(path)


def render_context(source_root: Path, finding: dict, context_lines: int = 3) -> str:
    file_path = source_root / finding["file"]
    content = read_text_robust(file_path)
    if content is None:
        return f"  (소스 파일을 열 수 없습니다: {file_path})"

    lines = content.splitlines()
    start_line = finding["line"]
    end_line = finding.get("end_line", start_line)
    window_start = max(start_line - context_lines, 1)
    window_end = min(end_line + context_lines, len(lines))

    rendered = []
    for lineno in range(window_start, window_end + 1):
        text = lines[lineno - 1] if lineno - 1 < len(lines) else ""
        marker = ">>" if start_line <= lineno <= end_line else "  "
        rendered.append(f"  {marker} {lineno:>4} | {text}")
    return "\n".join(rendered)


def print_finding(index: int, total: int, finding: dict, source_root: Path) -> None:
    print("\n" + "=" * 78)
    print(f"[{index}/{total}] {finding['file']}  (line {finding['line']}, {finding['model']})")
    print(f"룰: {finding['rule_id']} · {finding['rule_name']}  [{finding['severity']}]")
    print(f"CWE: {', '.join(finding.get('cwe', []))}  OWASP: {', '.join(finding.get('owasp', []))}")
    print(f"설명: {finding.get('desc', '')}")
    print("-" * 78)
    print(render_context(source_root, finding))
    print("-" * 78)


def main() -> None:
    if len(sys.argv) < 3:
        print("사용법: python label_findings.py <findings.jsonl> <data/ai_generated 경로>")
        sys.exit(1)

    findings_path = Path(sys.argv[1]).resolve()
    source_root = Path(sys.argv[2]).resolve()

    if not findings_path.is_file():
        print(f"[ERROR] 파일을 찾을 수 없습니다: {findings_path}")
        sys.exit(1)
    if not source_root.is_dir():
        print(f"[ERROR] 폴더를 찾을 수 없습니다: {source_root}")
        sys.exit(1)

    findings = load_findings(findings_path)
    total = len(findings)
    pending_indices = [i for i, f in enumerate(findings) if f.get("label") is None]

    already_true = sum(1 for f in findings if f.get("label") is True)
    already_false = sum(1 for f in findings if f.get("label") is False)
    print(f"전체 {total}건 — 완료 {already_true + already_false}건 "
          f"(진짜 위험 {already_true} / 오탐 {already_false}), 남은 {len(pending_indices)}건")

    if not pending_indices:
        print("라벨링할 항목이 없습니다. 모두 완료됐습니다.")
        return

    history: list[int] = []  # 되돌리기(u)용 스택
    cursor = 0

    while cursor < len(pending_indices):
        idx = pending_indices[cursor]
        finding = findings[idx]

        done_count = already_true + already_false + len(history)
        print_finding(done_count + 1, total, finding, source_root)

        answer = input("진짜 위험(y) / 오탐(n) / 모르겠음(s) / 취소(u) / 종료(q) > ").strip().lower()

        if answer == "y":
            finding["label"] = True
            save_findings(findings_path, findings)
            history.append(idx)
            cursor += 1
        elif answer == "n":
            finding["label"] = False
            save_findings(findings_path, findings)
            history.append(idx)
            cursor += 1
        elif answer == "s":
            cursor += 1
        elif answer == "u":
            if not history:
                print("취소할 이전 판정이 없습니다.")
                continue
            last_idx = history.pop()
            findings[last_idx]["label"] = None
            save_findings(findings_path, findings)
            cursor -= 1
        elif answer == "q":
            break
        else:
            print("y / n / s / u / q 중 하나를 입력하세요.")

    final_true = sum(1 for f in findings if f.get("label") is True)
    final_false = sum(1 for f in findings if f.get("label") is False)
    final_pending = sum(1 for f in findings if f.get("label") is None)
    print("\n" + "=" * 78)
    print(f"저장 완료: {findings_path}")
    print(f"진짜 위험 {final_true} / 오탐 {final_false} / 남은 미라벨 {final_pending}")


if __name__ == "__main__":
    main()
