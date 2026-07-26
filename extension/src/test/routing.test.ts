import { test } from 'node:test';
import * as assert from 'node:assert';
import { resolveAnalyzerKind } from '../analyzer/routing';

test('remote 설정은 Python만 백엔드로 라우팅', () => {
  assert.strictEqual(resolveAnalyzerKind('remote', 'python'), 'remote');
  assert.strictEqual(resolveAnalyzerKind('remote', 'Python'), 'remote');

  for (const language of [
    'javascript',
    'typescript',
    'javascriptreact',
    'typescriptreact',
    'java',
    'go',
    'php',
    'ruby',
  ]) {
    assert.strictEqual(
      resolveAnalyzerKind('remote', language),
      'rules',
      `${language}는 로컬 엔진을 사용해야 함`,
    );
  }
});

test('rules 설정은 언어와 관계없이 로컬 엔진 사용', () => {
  assert.strictEqual(resolveAnalyzerKind('rules', 'python'), 'rules');
  assert.strictEqual(resolveAnalyzerKind('rules', 'javascript'), 'rules');
});

test('활성화 시 언어가 아직 없으면 configured remote 유지', () => {
  assert.strictEqual(resolveAnalyzerKind('remote'), 'remote');
});
