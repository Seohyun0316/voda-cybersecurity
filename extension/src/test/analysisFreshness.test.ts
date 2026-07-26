import { test } from 'node:test';
import * as assert from 'node:assert';
import { isAnalysisResultCurrent } from '../analysisFreshness';
import { createDocumentSnapshot } from '../documentSnapshot';

const analyzed = createDocumentSnapshot(
  'file:///auth.py',
  7,
  'password = "secret"',
);

test('최신 검사이고 활성 문서가 그대로면 결과를 반영함', () => {
  const current = createDocumentSnapshot(
    'file:///auth.py',
    7,
    'password = "secret"',
  );

  assert.strictEqual(isAnalysisResultCurrent(3, 3, analyzed, current), true);
});

test('더 최근 검사가 시작됐으면 이전 결과를 무시함', () => {
  const current = createDocumentSnapshot(
    'file:///auth.py',
    7,
    'password = "secret"',
  );

  assert.strictEqual(isAnalysisResultCurrent(2, 3, analyzed, current), false);
});

test('분석 중 문서 버전이나 원문이 바뀌면 결과를 무시함', () => {
  const changedVersion = createDocumentSnapshot(
    'file:///auth.py',
    8,
    'password = "secret"',
  );
  const changedText = createDocumentSnapshot(
    'file:///auth.py',
    7,
    'password = "changed"',
  );

  assert.strictEqual(
    isAnalysisResultCurrent(3, 3, analyzed, changedVersion),
    false,
  );
  assert.strictEqual(
    isAnalysisResultCurrent(3, 3, analyzed, changedText),
    false,
  );
});

test('활성 파일이 바뀌거나 닫혔으면 결과를 무시함', () => {
  const otherDocument = createDocumentSnapshot(
    'file:///other.py',
    7,
    'password = "secret"',
  );

  assert.strictEqual(
    isAnalysisResultCurrent(3, 3, analyzed, otherDocument),
    false,
  );
  assert.strictEqual(isAnalysisResultCurrent(3, 3, analyzed, undefined), false);
});
