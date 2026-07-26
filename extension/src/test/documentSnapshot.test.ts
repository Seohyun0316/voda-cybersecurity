import { test } from 'node:test';
import * as assert from 'node:assert';
import {
  createDocumentSnapshot,
  isDocumentSnapshotCurrent,
  refreshDocumentSnapshot,
} from '../documentSnapshot';

test('URI, 버전, 원문이 모두 같으면 분석 스냅샷이 유효함', () => {
  const analyzed = createDocumentSnapshot('file:///auth.py', 7, 'password = "secret"');
  const current = createDocumentSnapshot('file:///auth.py', 7, 'password = "secret"');

  assert.strictEqual(isDocumentSnapshotCurrent(analyzed, current), true);
});

test('원문이 같아도 문서 버전이 달라지면 분석 스냅샷이 무효함', () => {
  const analyzed = createDocumentSnapshot('file:///auth.py', 7, 'password = "secret"');
  const current = createDocumentSnapshot('file:///auth.py', 8, 'password = "secret"');

  assert.strictEqual(isDocumentSnapshotCurrent(analyzed, current), false);
});

test('문서 버전이 같아도 원문이나 URI가 다르면 분석 스냅샷이 무효함', () => {
  const analyzed = createDocumentSnapshot('file:///auth.py', 7, 'password = "secret"');

  assert.strictEqual(
    isDocumentSnapshotCurrent(
      analyzed,
      createDocumentSnapshot('file:///auth.py', 7, 'password = "changed"'),
    ),
    false,
  );
  assert.strictEqual(
    isDocumentSnapshotCurrent(
      analyzed,
      createDocumentSnapshot('file:///other.py', 7, 'password = "secret"'),
    ),
    false,
  );
});

test('재분석 성공 후 공유 스냅샷을 최신 문서 상태로 갱신함', () => {
  const snapshot = createDocumentSnapshot('file:///auth.py', 7, 'before');
  const current = createDocumentSnapshot('file:///auth.py', 8, 'after');

  refreshDocumentSnapshot(snapshot, current);

  assert.deepStrictEqual(snapshot, current);
});
