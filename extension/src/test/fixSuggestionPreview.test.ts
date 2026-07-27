import { test } from 'node:test';
import * as assert from 'node:assert';
import {
  buildSuggestedCodeDiff,
  buildSuggestedCodePreview,
} from '../fixSuggestionPreview';

test('완성형 SQL 제안 뒤에 원본의 남은 인자를 중복하지 않음', () => {
  const original = 'cursor.execute("SELECT * FROM users WHERE name = " + name)';
  const detectedEnd = original.indexOf('+') + 1;

  assert.strictEqual(
    buildSuggestedCodePreview(
      original,
      0,
      detectedEnd,
      'cursor.execute("SELECT ... WHERE id = %s", (user_id,))',
    ),
    'cursor.execute("SELECT ... WHERE id = %s", (user_id,))',
  );
});

test('들여쓰기된 완성형 제안은 기존 들여쓰기를 유지함', () => {
  const original = '    cursor.execute(query + name)';
  const detectedEnd = original.indexOf('+') + 1;

  assert.strictEqual(
    buildSuggestedCodePreview(
      original,
      4,
      detectedEnd,
      'cursor.execute("SELECT ... WHERE id = %s", (user_id,))',
    ),
    '    cursor.execute("SELECT ... WHERE id = %s", (user_id,))',
  );
});

test('식 일부에 대한 제안은 앞뒤 코드 문맥을 유지함', () => {
  const original = 'hashed = hashlib.md5(password.encode())';
  const start = original.indexOf('md5(');

  assert.strictEqual(
    buildSuggestedCodePreview(original, start, start + 4, 'sha256('),
    'hashed = hashlib.sha256(password.encode())',
  );
});

test('hover diff에서 기존 코드는 제거, 안전 코드는 추가 행으로 표시', () => {
  assert.strictEqual(
    buildSuggestedCodeDiff(
      'secret = "hardcoded-secret"',
      'secret = os.environ["SECRET"]',
    ),
    [
      '- secret = "hardcoded-secret"',
      '+ secret = os.environ["SECRET"]',
    ].join('\n'),
  );
});

test('여러 줄 안전 코드도 모든 행을 추가 행으로 표시', () => {
  assert.strictEqual(
    buildSuggestedCodeDiff(
      'run(user_input)',
      'validated = validate(user_input)\nrun(validated)',
    ),
    [
      '- run(user_input)',
      '+ validated = validate(user_input)',
      '+ run(validated)',
    ].join('\n'),
  );
});
