"""LLM 생성 코드(data/ai_generated) 대상 실제 ruleset.toml 배치 스캔.

collect_github_code.py의 load_rule_set / prepare_rules / scan_content를 그대로
재사용한다. GitHub 스캔과 완전히 같은 룰 로딩·확장·컴파일 경로를 타므로,
"진짜 프로덕션 룰셋"과 다른 결과가 나올 걱정이 없다 (스캔 대상만 로컬 파일로 교체).

각 파일 x 각 룰에 대해 scan_content()가 찾은 매치 하나하나가 finding 한 줄(JSONL)이
된다. label 필드만 비워두는데, 이걸 사람이 true(진짜 위험)/false(오탐)로 채우면
그대로 LightGBM 학습(2차 오탐 필터) 라벨 데이터가 된다.

사용법:
  cd ruleset
  pip install regex requests          # 아직 없다면
  python scan_local_dataset.py ../data/ai_generated
  python scan_local_dataset.py ../data/ai_generated output/my_findings.jsonl

data/ai_generated/<모델명>/<파일> 구조를 그대로 이용해 모델명(ChatGPT/Claude/Gemini)을
자동으로 채워 넣는다.
"""

from __future__ import annotations

import json
import sys
from collections import Counter
from pathlib import Path
from typing import Iterator

from collect_github_code import (
    RULE_FILE,
    is_probably_binary_path,
    is_scannable_path,
    load_rule_set,
    prepare_rules,
    scan_content,
)

DEFAULT_OUTPUT = Path("output") / "ai_generated_findings.jsonl"

# ChatGPT 폴더 파일 다수가 Windows에서 CP949(EUC-KR)로 저장돼 있어 utf-8 디코딩이
# 실패한다. 실패하면 순서대로 재시도한다.
TEXT_ENCODINGS = ("utf-8", "utf-8-sig", "cp949")


def read_text_robust(path: Path) -> "tuple[str | None, str | None]":
    """여러 인코딩을 순서대로 시도한다. 전부 실패하면 (None, 에러메시지)."""
    raw = path.read_bytes()
    for encoding in TEXT_ENCODINGS:
        try:
            return raw.decode(encoding), None
        except UnicodeDecodeError:
            continue
    return None, f"decode failed with {TEXT_ENCODINGS}"


def iter_source_files(root: Path) -> Iterator[Path]:
    """collect_github_code.py와 동일한 확장자 필터(.py/.js)로 대상 파일을 고른다."""
    for path in sorted(root.rglob("*")):
        if not path.is_file():
            continue
        rel = str(path.relative_to(root))
        if not is_scannable_path(rel) or is_probably_binary_path(rel):
            continue
        yield path


def infer_model(path: Path, root: Path) -> str:
    """data/ai_generated/<모델명>/파일 구조에서 최상위 폴더명을 모델명으로 쓴다."""
    rel_parts = path.relative_to(root).parts
    return rel_parts[0] if len(rel_parts) > 1 else "unknown"


def main() -> None:
    if len(sys.argv) < 2:
        print("사용법: python scan_local_dataset.py <대상 폴더> [출력.jsonl]")
        sys.exit(1)

    target_dir = Path(sys.argv[1]).resolve()
    if not target_dir.is_dir():
        print(f"[ERROR] 폴더를 찾을 수 없습니다: {target_dir}")
        sys.exit(1)

    out_path = Path(sys.argv[2]) if len(sys.argv) > 2 else DEFAULT_OUTPUT
    out_path.parent.mkdir(parents=True, exist_ok=True)

    rule_set = load_rule_set(RULE_FILE)
    rules = prepare_rules(rule_set)
    print(f"[INFO] 룰 {len(rules)}개 로드 (ruleset v{rule_set['version']})")

    files = list(iter_source_files(target_dir))
    print(f"[INFO] 대상 파일 {len(files)}개 ({target_dir})")

    skipped_decode = []
    total_findings = 0
    files_with_findings = 0
    by_rule = Counter()
    by_model = Counter()
    by_severity = Counter()

    with out_path.open("w", encoding="utf-8") as out:
        for index, path in enumerate(files, start=1):
            if index == 1 or index % 50 == 0 or index == len(files):
                print(f"[INFO] 스캔 중: {index}/{len(files)}")

            content, decode_err = read_text_robust(path)
            if content is None:
                skipped_decode.append(f"{path.relative_to(target_dir)} ({decode_err})")
                continue

            rel_path = str(path.relative_to(target_dir))
            model = infer_model(path, target_dir)
            file_finding_count = 0

            for rule in rules:
                for finding in scan_content(content, rule, file_path=rel_path):
                    total_findings += 1
                    file_finding_count += 1
                    by_rule[rule["id"]] += 1
                    by_model[model] += 1
                    by_severity[rule["severity"]] += 1

                    out.write(
                        json.dumps(
                            {
                                "file": rel_path,
                                "model": model,
                                "rule_id": rule["id"],
                                "rule_name": rule["name"],
                                "desc": rule["desc"],
                                "owasp": rule["owasp"],
                                "cwe": rule["cwe"],
                                "severity": rule["severity"],
                                "line": finding["line"],
                                "column": finding["column"],
                                "end_line": finding["end_line"],
                                "end_column": finding["end_column"],
                                "line_preview": finding["line_preview"],
                                "match_masked": finding["match_masked"],
                                "match_hash": finding["match_hash"],
                                # 사람이 채움: true(진짜 위험) / false(오탐)
                                "label": None,
                            },
                            ensure_ascii=False,
                        )
                        + "\n"
                    )

            if file_finding_count > 0:
                files_with_findings += 1

    print("\n=== VibeSafe 로컬 데이터셋 스캔 결과 ===")
    print(f"대상 파일        : {len(files)}개")
    print(
        f"위험 발견 파일    : {files_with_findings}개 "
        f"({round(files_with_findings / len(files) * 100) if files else 0}%)"
    )
    print(f"총 findings     : {total_findings}건")
    if skipped_decode:
        print(f"디코딩 실패(스킵) : {len(skipped_decode)}개 -> {skipped_decode[:5]}")

    print("\n모델별 findings:")
    for model, n in by_model.most_common():
        print(f"  {model:<10} {n}건")

    print("\nseverity별 findings:")
    for sev in ("critical", "high", "medium", "low"):
        if by_severity.get(sev):
            print(f"  {sev:<10} {by_severity[sev]}건")

    print("\n룰별 발화 횟수 (상위 20):")
    for rule_id, n in by_rule.most_common(20):
        print(f"  {rule_id:<16} {n}건")

    print(f"\n저장: {out_path} (findings[].label을 사람이 채우면 LightGBM 학습 데이터가 됩니다)")


if __name__ == "__main__":
    main()
