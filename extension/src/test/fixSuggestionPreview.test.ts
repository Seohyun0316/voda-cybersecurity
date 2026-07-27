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

test('명시적인 부분 교체는 줄 시작 매치여도 원본 suffix를 유지함', () => {
  const original = 'eval(request.data)';
  const detectedEnd = 'eval('.length;

  assert.strictEqual(
    buildSuggestedCodePreview(
      original,
      0,
      detectedEnd,
      'ast.literal_eval(',
      false,
    ),
    'ast.literal_eval(request.data)',
  );
});

test('명시적인 줄 전체 교체는 매치 밖의 원본 코드를 붙이지 않음', () => {
  const original = 'uri = "postgres://user:password@db/app"';
  const start = original.indexOf('postgres:');

  assert.strictEqual(
    buildSuggestedCodePreview(
      original,
      start,
      original.length - 1,
      'import os\nuri = os.environ["DATABASE_URL"]',
      true,
    ),
    'import os\nuri = os.environ["DATABASE_URL"]',
  );
});

test('여러 줄 완성형 제안은 모든 줄에 기존 들여쓰기를 적용함', () => {
  const original = '    return jsonify({"error": str(error)})';

  assert.strictEqual(
    buildSuggestedCodePreview(
      original,
      4,
      original.length,
      'app.logger.exception("request failed")\n'
        + 'return jsonify({"error": "Internal server error"}), 500',
      true,
    ),
    '    app.logger.exception("request failed")\n'
      + '    return jsonify({"error": "Internal server error"}), 500',
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
