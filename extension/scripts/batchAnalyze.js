/**
 * LLM 생성 코드 일괄 분석 스크립트.
 *
 * data/ai_generated/ 같은 폴더의 .py/.js 파일 전체에 룰 엔진을 돌려
 * findings를 JSONL로 저장한다. 결과는 RF 오탐 필터 라벨링용 후보 데이터,
 * 룰 커버리지 통계, 발표용 수치 산출에 사용.
 *
 * 사용법:
 *   npm run compile                                # 먼저 빌드
 *   node scripts/batchAnalyze.js <대상 폴더> [출력.jsonl]
 * 예:
 *   node scripts/batchAnalyze.js ../data/ai_generated findings.jsonl
 */
const fs = require('fs');
const path = require('path');
const { RuleEngineAnalyzer } = require('../out/analyzer/ruleEngine');

const EXT_LANG = { '.py': 'python', '.js': 'javascript', '.ts': 'typescript' };

function walk(dir, files = []) {
  for (const name of fs.readdirSync(dir)) {
    const p = path.join(dir, name);
    const stat = fs.statSync(p);
    if (stat.isDirectory()) walk(p, files);
    else if (EXT_LANG[path.extname(name)]) files.push(p);
  }
  return files;
}

async function main() {
  const targetDir = process.argv[2];
  const outFile = process.argv[3] || 'findings.jsonl';
  if (!targetDir || !fs.existsSync(targetDir)) {
    console.error('사용법: node scripts/batchAnalyze.js <대상 폴더> [출력.jsonl]');
    process.exit(1);
  }

  const engine = new RuleEngineAnalyzer();
  const files = walk(targetDir);
  const out = fs.createWriteStream(outFile);

  let filesWithFindings = 0;
  let totalFindings = 0;
  const byRule = {};
  const scoreBuckets = { 높음: 0, 중간: 0, 낮음: 0, 안전: 0 };

  for (const file of files) {
    const code = fs.readFileSync(file, 'utf8');
    const lang = EXT_LANG[path.extname(file)];
    const result = await engine.analyze(code, file, lang);

    // 한 파일 = 한 줄 (JSONL) — DB 적재(schema.sql)나 pandas 읽기 쉬움
    out.write(JSON.stringify({
      file: path.relative(targetDir, file),
      language: lang,
      risk_score: result.riskScore,
      finding_count: result.findings.length,
      findings: result.findings.map((f) => ({
        rule_id: f.ruleId,
        severity: f.severity,
        category: f.category,
        line: f.line,
        start_col: f.startCol,
        end_col: f.endCol,
        message: f.message,
        has_legal: Boolean(f.legal),
        // RF 라벨링용 컨텍스트: 매치된 줄 원문
        line_text: code.split(/\r?\n/)[f.line] ?? '',
        label: null, // ← 사람이 채움: true(진짜 위험) / false(오탐)
      })),
    }) + '\n');

    if (result.findings.length > 0) filesWithFindings++;
    totalFindings += result.findings.length;
    for (const f of result.findings) byRule[f.ruleId] = (byRule[f.ruleId] || 0) + 1;
    const s = result.riskScore;
    scoreBuckets[s >= 70 ? '높음' : s >= 40 ? '중간' : s > 0 ? '낮음' : '안전']++;
  }
  out.end();

  console.log(`\n=== VibeSafe 일괄 분석 결과 ===`);
  console.log(`분석 파일        : ${files.length}개`);
  console.log(`위험 발견 파일    : ${filesWithFindings}개 (${files.length ? Math.round((filesWithFindings / files.length) * 100) : 0}%)`);
  console.log(`총 findings     : ${totalFindings}건`);
  console.log(`위험도 분포      : 높음 ${scoreBuckets['높음']} / 중간 ${scoreBuckets['중간']} / 낮음 ${scoreBuckets['낮음']} / 안전 ${scoreBuckets['안전']}`);
  console.log(`룰별 발화 횟수   :`);
  for (const [rule, n] of Object.entries(byRule).sort((a, b) => b[1] - a[1])) {
    console.log(`  ${rule.padEnd(22)} ${n}건`);
  }
  console.log(`\n저장: ${outFile} (findings[].label을 채우면 RF 학습 데이터가 됩니다)`);
}

main();
