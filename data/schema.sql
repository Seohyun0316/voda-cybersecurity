-- VibeSafe 데이터셋 스키마 (2테이블: 코드 단위 / 위반 건 단위)

CREATE TABLE samples (
    sample_id    INTEGER PRIMARY KEY,
    source       TEXT NOT NULL,     -- ai_generated | github | experiment
    language     TEXT NOT NULL,     -- python | javascript
    code         TEXT NOT NULL,     -- 마스킹 처리된 코드
    is_safe      INTEGER,           -- 1: 안전 샘플, 0: 위험 포함
    collected_at TEXT
);

CREATE TABLE findings (
    finding_id       INTEGER PRIMARY KEY,
    sample_id        INTEGER NOT NULL REFERENCES samples(sample_id),
    cwe              TEXT NOT NULL, -- 예: CWE-798
    rule_id          TEXT,          -- 매칭된 룰 ID
    line             INTEGER,
    is_true_positive INTEGER        -- 라벨: 1 진짜 위험 / 0 오탐(더미 값 등)
);
