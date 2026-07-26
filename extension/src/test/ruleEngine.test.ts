/**
 * 룰 엔진 유닛 테스트 (F2 담당).
 * 실행: npm test  (vscode 모듈에 의존하지 않는 순수 로직만 테스트)
 */
import { test } from 'node:test';
import * as assert from 'node:assert';
import { RuleEngineAnalyzer } from '../analyzer/ruleEngine';
import {
  computeRiskScore,
  compactLegalDescription,
  compactSanctionLabel,
  groupLegalRisks,
  riskLabel,
} from '../analyzer/types';

const engine = new RuleEngineAnalyzer();

test('하드코딩 비밀번호 탐지', async () => {
  const result = await engine.analyze('DB_PASSWORD = "admin1234"', 'auth.py', 'python');
  const f = result.findings.find((x) => x.ruleId === 'hardcoded-password');
  assert.ok(f, '하드코딩 비밀번호를 탐지해야 함');
  assert.strictEqual(f!.severity, 'error');
  assert.strictEqual(f!.legal?.article, '§29');
  assert.ok(f!.fix?.replacement?.includes('os.environ'), 'python이면 os.environ 제안');
});

test('OpenAI API 키 탐지', async () => {
  const result = await engine.analyze('API_KEY = "sk-proj-xK92abcdef123"', 'auth.py', 'python');
  const f = result.findings.find((x) => x.ruleId === 'exposed-api-key');
  assert.ok(f, 'sk- 키를 탐지해야 함');
  assert.strictEqual(f!.category, 'cost');
  assert.strictEqual(
    f!.fix?.replacement,
    'os.environ.get("OPENAI_API_KEY")',
    '따옴표까지 포함한 키를 환경변수 표현식으로 교체해야 함',
  );
});

test('SQL Injection 탐지', async () => {
  const code = `query = "SELECT * FROM users WHERE id='" + username + "'"`;
  const result = await engine.analyze(code, 'auth.py', 'python');
  const f = result.findings.find((x) => x.ruleId === 'sql-injection');
  assert.ok(f);
  assert.ok(f!.fix?.replacement?.includes('?'), '바인딩 파라미터 수정 제안이 있어야 함');
});

test('MD5 해싱 탐지', async () => {
  const result = await engine.analyze('hashed = hashlib.md5(password.encode())', 'auth.py', 'python');
  const f = result.findings.find((x) => x.ruleId === 'weak-hash');
  assert.ok(f);
  assert.strictEqual(f!.fix?.replacement, 'sha256(');
});

test('팀원 구현의 자동 수정 대상 4건을 모두 제공', async () => {
  const code = [
    'DB_PASSWORD = "admin1234"',
    'API_KEY = "sk-proj-xK92abcdef123"',
    `query = "SELECT * FROM users WHERE id='" + username + "'"`,
    'hashed = hashlib.md5(password.encode())',
  ].join('\n');
  const result = await engine.analyze(code, 'auth.py', 'python');
  const fixableRuleIds = result.findings
    .filter((finding) => Boolean(finding.fix?.replacement))
    .map((finding) => finding.ruleId);

  assert.deepStrictEqual(
    fixableRuleIds,
    ['hardcoded-password', 'exposed-api-key', 'sql-injection', 'weak-hash'],
  );
});

test('자동 수정을 위에서부터 1건씩 적용해도 다음 위치를 다시 계산할 수 있음', async () => {
  let code = [
    'DB_PASSWORD = "admin1234"',
    'API_KEY = "sk-proj-xK92abcdef123"',
    `query = "SELECT * FROM users WHERE id='" + username + "'"`,
    'hashed = hashlib.md5(password.encode())',
  ].join('\n');
  let applied = 0;

  while (applied < 10) {
    const result = await engine.analyze(code, 'auth.py', 'python');
    const target = result.findings.find((finding) => Boolean(finding.fix?.replacement));
    if (!target?.fix?.replacement) break;

    const lines = code.split('\n');
    const line = lines[target.line];
    lines[target.line] =
      line.slice(0, target.startCol) +
      target.fix.replacement +
      line.slice(target.endCol);
    code = lines.join('\n');
    applied += 1;
  }

  const finalResult = await engine.analyze(code, 'auth.py', 'python');
  assert.strictEqual(applied, 4);
  assert.ok(finalResult.findings.every((finding) => !finding.fix?.replacement));
  assert.ok(code.includes('DB_PASSWORD = os.environ.get("DB_PASSWORD")'));
  assert.ok(code.includes('API_KEY = os.environ.get("OPENAI_API_KEY")'));
  assert.ok(code.includes('hashlib.sha256(password.encode())'));
});

test('안전한 코드는 탐지 없음', async () => {
  const code = 'import os\nDB_PASSWORD = os.environ["DB_PASSWORD"]';
  const result = await engine.analyze(code, 'safe.py', 'python');
  assert.strictEqual(result.findings.length, 0);
  assert.strictEqual(result.riskScore, 0);
});

test('위험도 점수 계산과 라벨', () => {
  assert.strictEqual(riskLabel(0), '안전');
  assert.strictEqual(riskLabel(30), '낮음');
  assert.strictEqual(riskLabel(50), '중간');
  assert.strictEqual(riskLabel(72), '높음');
  const score = computeRiskScore([
    { severity: 'error' } as never,
    { severity: 'error' } as never,
    { severity: 'warning' } as never,
  ]);
  assert.strictEqual(score, 62, '법적 가중 없으면 25+25+12');
});

test('법적 가중치 = 책임도 + 제재 수준', () => {
  // §29: 과징금·과태료 의무조항(2) + 과징금·과태료 사례(1) = 가중치 3
  const pipa29 = { law: '개인정보보호법', article: '§29', description: '', liability: 2, sanction: 1 };
  assert.strictEqual(
    computeRiskScore([{ severity: 'error', legal: pipa29 } as never]),
    75,
    'error 25 × (2+1) = 75',
  );

  // 형사처벌 규정(3) + 형사처벌 사례(2) = 가중치 5 → 25×5=125 → 상한 100
  const criminal = { law: '정보통신망법', article: '§48', description: '', liability: 3, sanction: 2 };
  assert.strictEqual(
    computeRiskScore([{ severity: 'error', legal: criminal } as never]),
    100,
    '상한 100 적용',
  );

  // 최소 가중치: 일반 의무(1) + 사례 없음(0.5) = 1.5 → warning 12×1.5=18
  const mild = { law: '개인정보보호법', article: '§28', description: '', liability: 1, sanction: 0.5 };
  assert.strictEqual(
    computeRiskScore([{ severity: 'warning', legal: mild } as never]),
    18,
    'warning 12 × 1.5 = 18',
  );

  // sample/auth.py 시나리오: 75 + 25 + 12 + 12 = 124 → 100
  assert.strictEqual(
    computeRiskScore([
      { severity: 'error', legal: pipa29 } as never, // 75
      { severity: 'error' } as never,                // 25
      { severity: 'warning' } as never,              // 12
      { severity: 'warning' } as never,              // 12
    ]),
    100,
    'auth.py: 124 → 상한 100',
  );
});

test('여러 줄 파일에서 줄 번호 정확성', async () => {
  const code = ['# comment', 'import sqlite3', '', 'DB_PASSWORD = "admin1234"'].join('\n');
  const result = await engine.analyze(code, 'auth.py', 'python');
  const f = result.findings.find((x) => x.ruleId === 'hardcoded-password');
  assert.strictEqual(f!.line, 3, '0-based로 3번째 줄');
});

test('법적 리스크는 법률·조항별로 묶고 같은 설명·제재의 반복 탐지는 제거', () => {
  const mild = {
    law: '개인정보보호법',
    article: '§29',
    description: '일반 안전조치 의무 위반 소지가 있습니다.',
    liability: 2,
    sanction: 1,
    sanctionType: '과징금·과태료',
  } as const;
  const severe = {
    law: '개인정보보호법',
    article: '§29',
    description: '하드코딩된 인증정보로 안전조치 의무 위반 소지가 있습니다.',
    liability: 3,
    sanction: 2,
    sanctionType: '형사처벌, 과징금·과태료',
  } as const;

  const groups = groupLegalRisks([
    { ruleId: 'mild-rule', legal: mild } as never,
    { ruleId: 'another-mild-rule', legal: mild } as never,
    { ruleId: 'severe-rule', legal: severe } as never,
  ]);

  assert.strictEqual(groups.length, 1);
  assert.strictEqual(groups[0].items.length, 2, '서로 다른 위험 설명은 모두 유지');
  assert.strictEqual(
    compactLegalDescription(severe.description),
    '하드코딩된 인증정보',
  );
  assert.strictEqual(
    compactSanctionLabel(severe),
    '형사처벌/과징금·과태료',
  );
});
