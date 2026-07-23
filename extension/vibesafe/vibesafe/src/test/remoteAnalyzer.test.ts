/**
 * /detect 응답 어댑터(mapDetectResponse) 유닛 테스트 (F2 담당).
 * 스키마: docs/api-spec.md v1.0
 */
import { test } from 'node:test';
import * as assert from 'node:assert';
import { mapDetectResponse } from '../analyzer/remoteAnalyzer';

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
  assert.strictEqual(f.fix?.replacement, 'API_KEY = os.environ["API_KEY"]');
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

test('risk_score 없으면 계약 공식(§1)으로 계산', () => {
  const result = mapDetectResponse(
    {
      findings: [
        {
          rule_id: 'A04-798-001', severity: 'high', line: 0, start_col: 0, end_col: 5, message: 'm',
          legal: { law: '개인정보보호법', article: '§29', description: '', liability: 2, sanction: 1 },
        },
      ],
    },
    'x = 1',
    'a.py',
    'python',
  );
  assert.strictEqual(result.riskScore, 75, 'error 25 × (2+1) = 75');
});

test('빈 응답은 안전(0점)', () => {
  const result = mapDetectResponse({ findings: [] }, '', 'a.py', 'python');
  assert.strictEqual(result.riskScore, 0);
  assert.strictEqual(result.findings.length, 0);
});
