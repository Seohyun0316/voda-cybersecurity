/**
 * Mock ML 백엔드 서버 (F2 담당) — docs/api-spec.md v1.0의 살아있는 레퍼런스.
 *
 * 백엔드(M 파트)가 Flask로 /detect를 구현할 때 이 파일의 응답 형태를
 * 그대로 따라 하면 extension과 바로 연결된다.
 *
 * 실행: npm run mock-server  (포트 8788)
 * 테스트: 설정 vibesafe.engine = "remote",
 *        vibesafe.remoteEndpoint = "http://localhost:8788/detect"
 */
const http = require('http');

const PORT = 8788;

// CONTRACT.md §1 확정 공식용 가중치
const SEVERITY_WEIGHT = { high: 25, medium: 12, low: 4 };
const legalWeight = (legal) => (legal ? legal.liability + legal.sanction : 1);

/** 진짜 ML 대신 단순 패턴 매칭으로 스키마 형태만 흉내낸다 */
function fakeDetect(code, fileName) {
  const findings = [];
  const lines = code.split(/\r?\n/);

  lines.forEach((lineText, i) => {
    const pw = lineText.match(/(password|secret)\s*=\s*["'][^"']+["']/i);
    if (pw) {
      findings.push({
        rule_id: 'A04-798-001',
        cwe: 'CWE-798',
        category: 'secret',
        severity: 'high',
        line: i, // ★ 0-based (api-spec.md v1.0)
        start_col: pw.index,
        end_col: pw.index + pw[0].length,
        message: '[ML] 하드코딩된 비밀번호가 감지되었습니다.',
        detail: '환경변수(.env) 또는 Secrets Manager 사용을 권장합니다.',
        legal: {
          law: '개인정보보호법',
          article: '§29',
          description: '안전조치 의무 위반 소지',
          liability: 2, // 과징금·과태료 부과 가능한 의무조항
          sanction: 1,  // 과징금·과태료 사례
        },
        fix: {
          title: '환경변수로 교체',
          replacement: `${pw[0].split('=')[0].trim()} = os.environ["${pw[0].split('=')[0].trim().toUpperCase()}"]`,
        },
      });
    }
    const key = lineText.match(/sk-[a-zA-Z0-9_-]{8,}/);
    if (key) {
      findings.push({
        rule_id: 'A04-798-002',
        cwe: 'CWE-798',
        category: 'cost',
        severity: 'high',
        line: i,
        start_col: key.index,
        end_col: key.index + key[0].length,
        message: '[ML] 하드코딩된 API 키가 감지되었습니다.',
        detail: 'Git 푸시 시 무단 과금 위험. 즉시 키 재발급 필요.',
      });
    }
  });

  // finding별 점수 + 전체 점수 (§1 공식)
  let total = 0;
  for (const f of findings) {
    f.risk_score = Math.round(SEVERITY_WEIGHT[f.severity] * legalWeight(f.legal));
    total += SEVERITY_WEIGHT[f.severity] * legalWeight(f.legal);
  }

  return {
    risk_score: Math.min(100, Math.round(total)),
    findings,
    analyzed_at: new Date().toISOString(),
  };
}

const server = http.createServer((req, res) => {
  if (req.method !== 'POST' || req.url !== '/detect') {
    res.writeHead(404, { 'Content-Type': 'application/json' });
    res.end(JSON.stringify({ error: 'not found' }));
    return;
  }
  let body = '';
  req.on('data', (chunk) => (body += chunk));
  req.on('end', () => {
    try {
      const { code, file_name } = JSON.parse(body);
      res.writeHead(200, { 'Content-Type': 'application/json' });
      res.end(JSON.stringify(fakeDetect(code ?? '', file_name ?? '')));
    } catch (e) {
      res.writeHead(400, { 'Content-Type': 'application/json' });
      res.end(JSON.stringify({ error: String(e) }));
    }
  });
});

server.listen(PORT, () => {
  console.log(`[VibeSafe mock /detect server] http://localhost:${PORT}/detect (api-spec v1.0)`);
});
