/**
 * 룰 엔진 유닛 테스트 (F2 담당).
 * 실행: npm test  (vscode 모듈에 의존하지 않는 순수 로직만 테스트)
 */
import { test } from 'node:test';
import * as assert from 'node:assert';
import { RuleEngineAnalyzer } from '../analyzer/ruleEngine';
import { buildSuggestedCodePreview } from '../fixSuggestionPreview';
import {
  computeFindingRiskScore,
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
    'os.environ["OPENAI_API_KEY"]',
    '따옴표까지 포함한 키를 환경변수 표현식으로 교체해야 함',
  );
});

test('SQL Injection 탐지', async () => {
  const code = `query = "SELECT * FROM users WHERE id='" + username + "'"`;
  const result = await engine.analyze(code, 'auth.py', 'python');
  const f = result.findings.find((x) => x.ruleId === 'sql-injection');
  assert.ok(f);
  assert.ok(f!.fix?.replacement?.includes('%s'), '바인딩 파라미터 수정 제안이 있어야 함');
  assert.strictEqual(f!.fix?.replaceEntireLine, true);
});

test('SSRF 법 조항은 개인정보보호법 제29조로 표시', async () => {
  const result = await engine.analyze(
    'response = requests.get(request.args["url"])',
    'proxy.py',
    'python',
  );
  const f = result.findings.find((x) => x.ruleId === 'ssrf');

  assert.ok(f, 'SSRF를 탐지해야 함');
  assert.strictEqual(f!.legal?.law, '개인정보보호법');
  assert.strictEqual(f!.legal?.article, '§29');
});

test('MD5 해싱 탐지', async () => {
  const result = await engine.analyze('hashed = hashlib.md5(password.encode())', 'auth.py', 'python');
  const f = result.findings.find((x) => x.ruleId === 'weak-hash');
  assert.ok(f);
  assert.strictEqual(
    f!.fix?.replacement,
    'password_hash = PasswordHasher().hash(password)',
  );
  assert.strictEqual(f!.fix?.replaceEntireLine, true);
});

test('탐지된 수정 가능 룰 5건에 모두 대체 코드를 제공', async () => {
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
    [
      'hardcoded-password',
      'exposed-api-key',
      'hardcoded-credential',
      'sql-injection',
      'weak-hash',
    ],
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
    lines[target.line] = buildSuggestedCodePreview(
      line,
      target.startCol,
      target.endCol,
      target.fix.replacement,
      target.fix.replaceEntireLine,
    );
    code = lines.join('\n');
    applied += 1;
  }

  const finalResult = await engine.analyze(code, 'auth.py', 'python');
  assert.strictEqual(applied, 4);
  assert.ok(finalResult.findings.every((finding) => !finding.fix?.replacement));
  assert.ok(code.includes('DB_PASSWORD = os.environ["DB_PASSWORD"]'));
  assert.ok(code.includes('API_KEY = os.environ["OPENAI_API_KEY"]'));
  assert.ok(code.includes('password_hash = PasswordHasher().hash(password)'));
});

test('지원 언어별 환경변수 대체 코드를 제공', async () => {
  const cases = [
    ['python', 'password = "admin1234"', 'password = os.environ["PASSWORD"]'],
    ['javascript', 'const password = "admin1234"', 'const password = process.env.PASSWORD;'],
    ['typescript', 'const password = "admin1234"', 'const password = process.env.PASSWORD;'],
    ['java', 'String password = "admin1234"', 'String password = System.getenv("PASSWORD");'],
    ['go', 'var password = "admin1234"', 'password := os.Getenv("PASSWORD")'],
    ['php', '$password = "admin1234"', '$password = getenv("PASSWORD");'],
    ['ruby', 'password = "admin1234"', 'password = ENV.fetch("PASSWORD")'],
  ] as const;

  for (const [language, code, expected] of cases) {
    const result = await engine.analyze(code, `auth.${language}`, language);
    const finding = result.findings.find((item) => item.ruleId === 'hardcoded-password');

    assert.ok(finding, `${language} 하드코딩 비밀번호를 탐지해야 함`);
    assert.strictEqual(finding.fix?.replacement, expected);
    assert.strictEqual(finding.fix?.replaceEntireLine, true);
  }
});

test('명령 실행과 역직렬화에도 언어별 완성형 대체 코드를 제공', async () => {
  const commandResult = await engine.analyze(
    'os.system(user_input)',
    'commands.py',
    'python',
  );
  const commandFinding = commandResult.findings.find(
    (item) => item.ruleId === 'os-command-injection',
  );
  assert.strictEqual(
    commandFinding?.fix?.replacement,
    'subprocess.run(["command", str(argument)], shell=False, check=True)',
  );
  assert.strictEqual(commandFinding?.fix?.replaceEntireLine, true);

  const deserializeResult = await engine.analyze(
    'pickle.loads(request.data)',
    'payload.py',
    'python',
  );
  const deserializeFinding = deserializeResult.findings.find(
    (item) => item.ruleId === 'unsafe-deserialization',
  );
  assert.strictEqual(
    deserializeFinding?.fix?.replacement,
    'payload = json.loads(untrusted_data)',
  );
  assert.strictEqual(deserializeFinding?.fix?.replaceEntireLine, true);
});

test('업로드·경로·SSRF·개인정보 탐지도 범용 대체 코드를 제공', async () => {
  const cases = [
    {
      code: 'upload.save(upload.filename)',
      fileName: 'upload.py',
      ruleId: 'dangerous-file-upload',
      expected: 'secure_filename',
    },
    {
      code: 'open("../private.txt")',
      fileName: 'files.py',
      ruleId: 'path-traversal',
      expected: 'safe_path',
    },
    {
      code: 'requests.get(target_url)',
      fileName: 'proxy.py',
      ruleId: 'ssrf',
      expected: 'ALLOWED_HOSTS',
    },
    {
      code: 'email = "real.user@example.com"',
      fileName: 'profile.py',
      ruleId: 'personal-info',
      expected: 'os.environ["EMAIL"]',
    },
  ] as const;

  for (const item of cases) {
    const result = await engine.analyze(item.code, item.fileName, 'python');
    const finding = result.findings.find((candidate) => candidate.ruleId === item.ruleId);

    assert.ok(finding, `${item.ruleId}를 탐지해야 함`);
    assert.ok(finding.fix?.replacement?.includes(item.expected));
    assert.strictEqual(finding.fix?.replaceEntireLine, true);
  }
});

test('PHP 명령 실행에도 셸을 우회하는 대체 코드를 제공', async () => {
  const result = await engine.analyze('system($userInput);', 'command.php', 'php');
  const finding = result.findings.find(
    (candidate) => candidate.ruleId === 'os-command-injection',
  );

  assert.ok(finding);
  assert.ok(finding.fix?.replacement?.includes('proc_open(['));
  assert.strictEqual(finding.fix?.replaceEntireLine, true);
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
    { cwe: 'CWE-532', severity: 'error' } as never,
    { cwe: 'CWE-295', severity: 'error' } as never,
    { cwe: 'CWE-209', severity: 'warning' } as never,
  ]);
  assert.strictEqual(score, 60, '여러 finding 중 가장 높은 CWE-532 점수');
});

test('PDF 위험도 산식과 최대 finding 집계', () => {
  assert.strictEqual(
    computeFindingRiskScore({ cwe: 'CWE-798', severity: 'error' } as never),
    75,
    '3 × 3 × 5 / 60 × 100 = 75',
  );
  assert.strictEqual(
    computeFindingRiskScore({ cwe: 'CWE-532', severity: 'error' } as never),
    60,
    '3 × 3 × 4 / 60 × 100 = 60',
  );
  assert.strictEqual(
    computeFindingRiskScore({ cwe: 'CWE-502', severity: 'info' } as never),
    13.33,
    'CWE-502는 severity와 무관하게 Critical(4)',
  );
  assert.strictEqual(
    computeRiskScore([
      { cwe: 'CWE-798', severity: 'error' } as never,
      { cwe: 'CWE-532', severity: 'error' } as never,
    ]),
    75,
    '합계가 아니라 현재 finding 중 최댓값',
  );
  assert.strictEqual(
    computeRiskScore([{ cwe: 'CWE-532', severity: 'error' } as never]),
    60,
    '최고 위험을 수정하면 다음 finding 점수로 하락',
  );
  assert.strictEqual(computeRiskScore([]), 0);
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
