# Ruleset

- `ruleset.toml` — 정규식 룰셋 (현재 v0.3.1) ← 파일 추가 필요
- 검증 워크플로: `validate.py` → `smoke.py` (0 FAIL 확인) → `perf_coverage.py` → commit

```bash
pip install regex
python validate.py && python smoke.py && python perf_coverage.py
```
