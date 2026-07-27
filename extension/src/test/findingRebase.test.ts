import { test } from 'node:test';
import * as assert from 'node:assert';
import { Finding } from '../analyzer';
import { rebaseFindings } from '../findingRebase';

function finding(
  ruleId: string,
  line: number,
  startCol: number,
  endCol: number,
): Finding {
  return {
    ruleId,
    message: ruleId,
    detail: '안전 코드 사용',
    severity: 'warning',
    category: 'other',
    line,
    startCol,
    endCol,
    fix: { title: '수정', replacement: 'safe()' },
  };
}

test('수정한 finding만 제거하고 다음 finding은 유지', () => {
  const original = 'first_bad()\nsecond_bad()';
  const current = 'first_safe()\nsecond_bad()';
  const findings = [
    finding('first', 0, 0, 11),
    finding('second', 1, 0, 12),
  ];

  const rebased = rebaseFindings(findings, original, current, [{
    rangeOffset: 0,
    rangeLength: 11,
    text: 'first_safe()',
  }]);

  assert.deepStrictEqual(
    rebased.map(({ ruleId, line, startCol, endCol }) => ({
      ruleId,
      line,
      startCol,
      endCol,
    })),
    [{ ruleId: 'second', line: 1, startCol: 0, endCol: 12 }],
  );
});

test('앞선 수정에서 줄이 추가되면 다음 finding의 줄 번호도 이동', () => {
  const original = 'first_bad()\nsecond_bad()';
  const current = 'setup()\nfirst_safe()\nsecond_bad()';
  const findings = [
    finding('first', 0, 0, 11),
    finding('second', 1, 0, 12),
  ];

  const rebased = rebaseFindings(findings, original, current, [{
    rangeOffset: 0,
    rangeLength: 11,
    text: 'setup()\nfirst_safe()',
  }]);

  assert.strictEqual(rebased.length, 1);
  assert.strictEqual(rebased[0].ruleId, 'second');
  assert.strictEqual(rebased[0].line, 2);
  assert.strictEqual(rebased[0].startCol, 0);
  assert.strictEqual(rebased[0].endCol, 12);
});

test('같은 줄 앞부분의 삽입은 다음 finding의 열 위치를 이동', () => {
  const original = 'prefix target()';
  const current = 'long_prefix target()';
  const target = finding('target', 0, 7, 15);

  const rebased = rebaseFindings([target], original, current, [{
    rangeOffset: 0,
    rangeLength: 6,
    text: 'long_prefix',
  }]);

  assert.strictEqual(rebased.length, 1);
  assert.strictEqual(rebased[0].line, 0);
  assert.strictEqual(rebased[0].startCol, 12);
  assert.strictEqual(rebased[0].endCol, 20);
});

test('finding 내부에 삽입된 편집은 해당 finding을 제거', () => {
  const original = 'dangerous()';
  const current = 'danger_safeous()';
  const target = finding('danger', 0, 0, original.length);

  const rebased = rebaseFindings([target], original, current, [{
    rangeOffset: 6,
    rangeLength: 0,
    text: '_safe',
  }]);

  assert.deepStrictEqual(rebased, []);
});

test('finding 시작 경계에 삽입된 편집도 해당 finding을 제거', () => {
  const original = 'dangerous()';
  const current = 'safe_dangerous()';
  const target = finding('danger', 0, 0, original.length);

  const rebased = rebaseFindings([target], original, current, [{
    rangeOffset: 0,
    rangeLength: 0,
    text: 'safe_',
  }]);

  assert.deepStrictEqual(rebased, []);
});
