/**
 * /detect 응답 어댑터(mapDetectResponse) 유닛 테스트 (F2 담당).
 * 스키마: docs/api-spec.md v1.0
 */
import { test } from 'node:test';
import * as assert from 'node:assert';
import {
  RemoteAnalyzer,
  mapDetectResponse,
  validateDetectResponse,
} from '../analyzer/remoteAnalyzer';

const CODE = ['import os', 'API_KEY = "sk-proj-xK92abcdef"', 'print(1)'].join('\n');

test('/detect v1.0 응답을 내부 모델로 변환', () => {
  const result = mapDetectResponse(
    {
      risk_score: 75,
      findings: [
        {
          rule_id: 'A04-798-001',
          cwe: 'CWE-798',
          category: 'secret',
          severity: 'high',
          line: 1, // 0-based
          start_col: 10,
          end_col: 30,
          message: '하드코딩된 API 키가 감지되었습니다.',
          detail: '환경변수 사용 권장',
          risk_score: 75,
          legal: {
            law: '개인정보보호법',
            article: '§29',
            description: '안전조치 의무 위반 소지',
            liability: 2,
            sanction: 1,
            sanction_type: '과징금·과태료',
          },
          fix: { title: '환경변수로 교체', replacement: 'API_KEY = os.environ["API_KEY"]' },
        },
      ],
    },
    CODE,
    'auth.py',
    'python',
  );

  const f = result.findings[0];
  assert.strictEqual(f.line, 1, '0-based 그대로 사용 (변환 없음)');
  assert.strictEqual(f.severity, 'error', 'high → error');
  assert.strictEqual(f.category, 'secret');
  assert.strictEqual(f.startCol, 10);
  assert.strictEqual(f.endCol, 30);
  assert.strictEqual(f.legal?.liability, 2, '구조화된 legal 그대로 전달');
  assert.strictEqual(f.legal?.sanctionType, '과징금·과태료', '표시용 제재 유형 변환');
  assert.strictEqual(f.fix?.replacement, 'API_KEY = os.environ["API_KEY"]');
  assert.strictEqual(f.riskScore, 75, '개별 finding 점수 전달');
  assert.strictEqual(result.riskScore, 75, '백엔드 전체 점수 사용');
  assert.strictEqual(result.engine, 'remote');
});

test('severity 매핑: medium→warning, low→info + category 추정', () => {
  const result = mapDetectResponse(
    {
      findings: [
        { rule_id: 'A05-089-001', severity: 'medium', line: 0, start_col: 0, end_col: 5, message: 'm' },
        { rule_id: 'A10-770-001', severity: 'low', line: 0, start_col: 0, end_col: 5, message: 'l' },
      ],
    },
    'x = 1',
    'a.py',
    'python',
  );
  assert.strictEqual(result.findings[0].severity, 'warning');
  assert.strictEqual(result.findings[0].category, 'injection', 'category 누락 시 A05 → injection');
  assert.strictEqual(result.findings[1].severity, 'info');
});

test('백엔드 API 키 룰은 secret 응답이어도 과금 경보 category로 변환', () => {
  const result = mapDetectResponse(
    {
      findings: [
        {
          rule_id: 'A04-798-002',
          cwe: 'CWE-798',
          category: 'secret',
          severity: 'high',
          line: 0,
          start_col: 10,
          end_col: 30,
          message: '하드코딩된 API 키가 감지되었습니다.',
          detail: 'Git 푸시 시 무단 과금 위험',
        },
      ],
    },
    'API_KEY = "sk-proj-xK92abcdef"',
    'auth.py',
    'python',
  );

  assert.strictEqual(result.findings[0].category, 'cost');
});

test('백엔드 상세 category를 Extension UI category로 변환', () => {
  const result = mapDetectResponse(
    {
      findings: [
        {
          rule_id: 'A05-089-001',
          category: 'sql_injection',
          severity: 'medium',
          line: 0,
          start_col: 0,
          end_col: 5,
          message: 'SQL Injection',
        },
        {
          rule_id: 'A10-770-001',
          category: 'resource_exhaustion',
          severity: 'low',
          line: 1,
          start_col: 0,
          end_col: 5,
          message: '자원 제한 없음',
        },
      ],
    },
    'line1\nline2',
    'a.py',
    'python',
  );

  assert.strictEqual(result.findings[0].category, 'injection');
  assert.strictEqual(result.findings[1].category, 'cost');
});

test('risk_score 없으면 PDF 산식으로 계산', () => {
  const result = mapDetectResponse(
    {
      findings: [
        {
          rule_id: 'A04-798-001', cwe: 'CWE-798', severity: 'high', line: 0, start_col: 0, end_col: 5, message: 'm',
          legal: { law: '개인정보보호법', article: '§29', description: '', liability: 2, sanction: 1 },
        },
      ],
    },
    'x = 1',
    'a.py',
    'python',
  );
  assert.strictEqual(result.riskScore, 75, '3 × 3 × 5 / 60 × 100 = 75');
});

test('빈 응답은 안전(0점)', () => {
  const result = mapDetectResponse({ findings: [] }, '', 'a.py', 'python');
  assert.strictEqual(result.riskScore, 0);
  assert.strictEqual(result.findings.length, 0);
});

test('필수 필드가 없거나 잘못된 severity면 응답을 거부', () => {
  assert.throws(
    () => validateDetectResponse({}),
    /findings.*배열/,
  );
  assert.throws(
    () => validateDetectResponse({
      findings: [
        {
          rule_id: 'A05-89-001',
          severity: 'critical',
          line: 0,
          start_col: 0,
          end_col: 5,
          message: 'SQL Injection',
        },
      ],
    }),
    /findings\[0\]\.severity/,
  );
});

test('음수·소수 좌표와 역전된 범위를 거부', () => {
  const finding = {
    rule_id: 'A05-89-001',
    severity: 'high',
    line: 0,
    start_col: 0,
    end_col: 5,
    message: 'SQL Injection',
  };

  assert.throws(
    () => validateDetectResponse({
      findings: [{ ...finding, line: -1 }],
    }),
    /findings\[0\]\.line.*0 이상의 정수/,
  );
  assert.throws(
    () => validateDetectResponse({
      findings: [{ ...finding, start_col: 1.5 }],
    }),
    /findings\[0\]\.start_col.*0 이상의 정수/,
  );
  assert.throws(
    () => validateDetectResponse({
      findings: [{ ...finding, start_col: 6, end_col: 5 }],
    }),
    /end_col.*start_col보다 작을 수 없습니다/,
  );
});

test('전체·개별 위험도 점수는 유한한 0~100 값만 허용', () => {
  const finding = {
    rule_id: 'A04-798-001',
    severity: 'high',
    line: 0,
    start_col: 0,
    end_col: 5,
    message: '하드코딩 비밀값',
  };

  for (const invalidScore of [-1, 101, Number.NaN, Number.POSITIVE_INFINITY]) {
    assert.throws(
      () => validateDetectResponse({
        risk_score: invalidScore,
        findings: [finding],
      }),
      /risk_score.*0~100/,
    );
    assert.throws(
      () => validateDetectResponse({
        findings: [{ ...finding, risk_score: invalidScore }],
      }),
      /findings\[0\]\.risk_score.*0~100/,
    );
  }
});

test('legal null 가중치와 fix null은 API 계약에 따라 허용', () => {
  const response = validateDetectResponse({
    risk_score: null,
    findings: [
      {
        rule_id: 'A04-798-001',
        severity: 'high',
        line: 0,
        start_col: 0,
        end_col: 5,
        message: '하드코딩 비밀값',
        legal: {
          law: '개인정보보호법',
          article: '§29',
          description: '',
          liability: null,
          sanction: null,
        },
        fix: null,
      },
    ],
  });

  assert.strictEqual(response.findings[0].legal?.liability, null);
  assert.strictEqual(response.findings[0].fix, null);
});

test('잘못된 날짜와 legal·fix 중첩 구조를 거부', () => {
  const finding = {
    rule_id: 'A04-798-001',
    severity: 'high',
    line: 0,
    start_col: 0,
    end_col: 5,
    message: '하드코딩 비밀값',
  };

  assert.throws(
    () => validateDetectResponse({
      analyzed_at: 'not-a-date',
      findings: [finding],
    }),
    /analyzed_at.*유효한 날짜/,
  );
  assert.throws(
    () => validateDetectResponse({
      findings: [{
        ...finding,
        legal: {
          law: '개인정보보호법',
          article: '§29',
          description: '',
          liability: 4,
          sanction: 1,
        },
      }],
    }),
    /legal\.liability/,
  );
  assert.throws(
    () => validateDetectResponse({
      findings: [{ ...finding, fix: { replacement: 'safe_code' } }],
    }),
    /fix\.title/,
  );
});

test('잘못된 JSON은 사용자 친화적인 오류로 변환', async () => {
  const originalFetch = globalThis.fetch;
  globalThis.fetch = (async () => ({
    ok: true,
    json: async () => {
      throw new SyntaxError('Unexpected token');
    },
  })) as unknown as typeof fetch;

  try {
    await assert.rejects(
      new RemoteAnalyzer('http://localhost/detect').analyze('', 'a.py', 'python'),
      /서버 응답이 올바른 JSON이 아닙니다/,
    );
  } finally {
    globalThis.fetch = originalFetch;
  }
});
