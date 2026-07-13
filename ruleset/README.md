# Ruleset

- `ruleset.toml` — 정규식 룰셋 (현재 v1.1.1)
- 검증 워크플로: `validate.py` → `smoke.py` (0 FAIL 확인) → `perf_coverage.py` → commit

```bash
pip install regex
python validate.py && python smoke.py && python perf_coverage.py
```
