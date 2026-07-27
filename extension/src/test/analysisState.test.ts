import { test } from 'node:test';
import * as assert from 'node:assert';
import {
  ConfirmedAnalysisState,
  DocumentAnalysisState,
} from '../analysisState';
import type { AnalysisResult, Finding } from '../analyzer/types';
import { createDocumentSnapshot } from '../documentSnapshot';

function finding(
  ruleId: string,
  line: number,
  category: Finding['category'] = 'other',
): Finding {
  return {
    ruleId,
    cwe: category === 'cost' ? 'CWE-798' : 'CWE-89',
    message: ruleId,
    detail: '안전 코드 사용',
    severity: 'error',
    category,
    line,
    startCol: 0,
    endCol: 5,
    legal: {
      law: '개인정보보호법',
      article: '§29',
      description: '안전조치 의무 위반 가능',
      liability: 2,
      sanction: 1,
    },
    fix: { title: '수정', replacement: 'safe()' },
  };
}

function result(
  findings: Finding[],
  riskScore = 87,
  analyzedAt = '2026-07-27T08:00:00.000Z',
): AnalysisResult {
  return {
    fileName: 'sample.py',
    languageId: 'python',
    riskScore,
    findings,
    engine: 'remote',
    analyzedAt,
  };
}

test('편집용 finding이 제거돼도 확정 점수와 법적·비용 경고는 유지', () => {
  const confirmed = result([
    finding('exposed-api-key', 0, 'cost'),
    finding('sql-injection', 1),
  ]);
  const state = new DocumentAnalysisState(
    confirmed,
    createDocumentSnapshot('file:///sample.py', 1, 'token\nquery'),
  );

  const working = state.rebase(
    createDocumentSnapshot('file:///sample.py', 2, 'safe_\nquery'),
    [{ rangeOffset: 0, rangeLength: 5, text: 'safe_' }],
  );

  assert.strictEqual(working.length, 1);
  assert.strictEqual(working[0].ruleId, 'sql-injection');
  assert.strictEqual(state.confirmedResult.riskScore, 87);
  assert.strictEqual(state.confirmedResult.analyzedAt, '2026-07-27T08:00:00.000Z');
  assert.strictEqual(state.confirmedResult.findings.length, 2);
  assert.strictEqual(state.confirmedResult.findings[0].category, 'cost');
  assert.strictEqual(state.confirmedResult.findings[0].legal?.law, '개인정보보호법');
});

test('stale 상태는 첫 코드 변경에서만 활성화됨', () => {
  const display = new ConfirmedAnalysisState();
  display.confirm(result([finding('existing-risk', 0)]));

  assert.strictEqual(display.markStale(), true);
  assert.strictEqual(display.isStale, true);
  assert.strictEqual(display.markStale(), false);
  assert.strictEqual(display.markStale(), false);
});

test('반복 입력은 stale 렌더링 신호를 한 번만 발생시킴', () => {
  const display = new ConfirmedAnalysisState();
  display.confirm(result([finding('existing-risk', 0)]));

  let renderCount = 0;
  for (let i = 0; i < 20; i += 1) {
    if (display.markStale()) renderCount += 1;
  }

  assert.strictEqual(renderCount, 1);
});

test('stale 중에는 새 취약점이 확정 결과에 추가되지 않음', () => {
  const display = new ConfirmedAnalysisState();
  const previous = result([finding('existing-risk', 0)], 42);
  display.confirm(previous);

  display.markStale();

  assert.strictEqual(display.result, previous);
  assert.strictEqual(display.result?.riskScore, 42);
  assert.deepStrictEqual(
    display.result?.findings.map(({ ruleId }) => ruleId),
    ['existing-risk'],
  );
  assert.strictEqual(display.isStale, true);
});

test('수동 재검사 성공 결과를 확정하면 stale이 해제되고 새 결과로 교체됨', () => {
  const display = new ConfirmedAnalysisState();
  display.confirm(result([finding('old-risk', 0)], 42));
  display.markStale();

  const rescanned = result(
    [finding('old-risk', 0), finding('new-risk', 2)],
    91,
    '2026-07-27T09:00:00.000Z',
  );
  display.confirm(rescanned);

  assert.strictEqual(display.isStale, false);
  assert.strictEqual(display.result, rescanned);
  assert.strictEqual(display.result?.riskScore, 91);
  assert.deepStrictEqual(
    display.result?.findings.map(({ ruleId }) => ruleId),
    ['old-risk', 'new-risk'],
  );
});
