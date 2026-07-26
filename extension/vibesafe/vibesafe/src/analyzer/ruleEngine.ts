/**
 * 로컬 규칙 기반 분석 엔진 (F2 담당).
 *
 * ML 백엔드가 연결되기 전까지 실제 탐지를 담당한다.
 * 규칙을 추가하려면 RULES 배열에 항목을 추가하면 된다.
 */
import {
  AnalysisResult,
  Analyzer,
  Category,
  Finding,
  LegalRisk,
  Severity,
  computeRiskScore,
} from './types';

interface Rule {
  id: string;
  /** 한 줄 단위로 검사할 정규식 (g 플래그 필수 — 한 줄에 여러 건 탐지) */
  pattern: RegExp;
  severity: Severity;
  category: Category;
  message: string;
  detail: string;
  legal?: LegalRisk;
  /** 매치 텍스트를 받아 교체 문자열을 만드는 함수 (없으면 quick fix 없음) */
  makeFix?: (match: string, languageId: string) => { title: string; replacement: string } | undefined;
}

const PIPA_29: LegalRisk = {
  law: '개인정보보호법',
  article: '§29',
  description: '안전조치 의무 위반 가능 — 유출 시 과징금 부과 대상',
  liability: 2, // 과징금·과태료 부과 가능한 의무조항
  sanction: 1,  // 과징금·과태료 사례 있음
};

function envVarFix(varName: string, languageId: string): { title: string; replacement: string } {
  const name = varName.toUpperCase();
  const replacement =
    languageId === 'python'
      ? `os.environ.get("${name}")`
      : `process.env.${name}`;
  return { title: `환경변수 ${name}(으)로 교체`, replacement };
}

const RULES: Rule[] = [
  // 1. 하드코딩 비밀번호
  {
    id: 'hardcoded-password',
    pattern: /(password|passwd|pwd|secret|db_password)\s*=\s*["'][^"']{4,}["']/gi,
    severity: 'error',
    category: 'secret',
    message: '하드코딩 비밀번호 — 개인정보보호법 §29',
    detail: '환경변수(.env) 또는 Secrets Manager 사용 권장',
    legal: PIPA_29,
    makeFix: (match, lang) => {
      const varName = match.split('=')[0].trim();
      const { title } = envVarFix(varName, lang);
      return { title, replacement: `${varName} = ${envVarFix(varName, lang).replacement}` };
    },
  },
  // 2. API 키 노출
  {
    id: 'exposed-api-key',
    pattern: /(sk-[a-zA-Z0-9_-]{8,}|AKIA[0-9A-Z]{16}|ghp_[A-Za-z0-9]{20,}|AIza[0-9A-Za-z_-]{20,})/g,
    severity: 'error',
    category: 'cost',
    message: 'API 키 노출 — 과금 위험',
    detail: 'Git 푸시 시 무단 과금 발생 가능. 즉시 키 재발급 필요',
    makeFix: (match, lang) => {
      const replacement = lang === 'python' ? 'os.environ.get("OPENAI_API_KEY")' : 'process.env.OPENAI_API_KEY';
      return { title: 'API 키 환경변수로 숨기기', replacement };
    },
  },
  // 3. SQL Injection 위험
  {
    id: 'sql-injection',
    pattern: /["'].*?\b(SELECT|INSERT|UPDATE|DELETE)\b.*?["']\s*\+/gi,
    severity: 'warning',
    category: 'injection',
    message: 'SQL Injection 위험',
    detail: 'parameterized query 또는 ORM 사용 필요',
    makeFix: (match, lang) => {
      return { title: 'SQL 바인딩 파라미터 사용(? 사용)', replacement: '"SELECT * FROM users WHERE id=?" #' };
    },
  },
  // 4. 취약한 해시 알고리즘
  {
    id: 'weak-hash',
    pattern: /\b(md5|sha1)\s*\(/gi,
    severity: 'warning',
    category: 'crypto',
    message: '취약한 해시 알고리즘 (비밀번호 해싱 부적합)',
    detail: 'bcrypt, scrypt, argon2 사용 권장',
    makeFix: (match, lang) => {
      return { title: '안전한 sha256 해시 알고리즘으로 교체', replacement: 'sha256(' };
    },
  },
  // 5. dangerous-eval
  {
    id: 'dangerous-eval',
    pattern: /\beval\s*\(/g,
    severity: 'warning',
    category: 'injection',
    message: 'eval() 사용 — 코드 주입 위험',
    detail: '사용자 입력이 eval에 전달되면 원격 코드 실행 가능',
    makeFix: (match, lang) => {
      return { title: 'eval()을 안전한 ast.literal_eval()로 교체', replacement: 'ast.literal_eval(' };
    },
  },
  // 6. 디버그 모드 활성화
  {
    id: 'debug-mode',
    pattern: /\bdebug\s*=\s*True\b/g,
    severity: 'info',
    category: 'other',
    message: '디버그 모드 활성화',
    detail: '운영 배포 시 내부 정보 노출 위험',
    makeFix: (match, lang) => {
      return { title: '디버그 모드 비활성화 (False)', replacement: 'debug = False' };
    },
  },
];

export class RuleEngineAnalyzer implements Analyzer {
  readonly kind = 'rules' as const;

  async analyze(text: string, fileName: string, languageId: string): Promise<AnalysisResult> {
    const findings: Finding[] = [];
    const lines = text.split(/\r?\n/);

    lines.forEach((lineText, lineIdx) => {
      for (const rule of RULES) {
        rule.pattern.lastIndex = 0; // g 플래그 정규식 상태 초기화
        let m: RegExpExecArray | null;
        while ((m = rule.pattern.exec(lineText)) !== null) {
          findings.push({
            ruleId: rule.id,
            message: rule.message,
            detail: rule.detail,
            severity: rule.severity,
            category: rule.category,
            line: lineIdx,
            startCol: m.index,
            endCol: m.index + m[0].length,
            legal: rule.legal,
            fix: rule.makeFix?.(m[0], languageId),
          });
        }
      }
    });

    return {
      fileName,
      languageId,
      riskScore: computeRiskScore(findings),
      findings,
      engine: 'rules',
      analyzedAt: new Date().toISOString(),
    };
  }
}