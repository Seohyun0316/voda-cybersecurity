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
  cwe: string;
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
  description: '하드코딩된 인증정보 또는 개인정보 노출',
  liability: 3,
  sanction: 2,
  sanctionType: '형사처벌, 과징금·과태료',
};

const SQLI_LEGAL: LegalRisk = {
  law: '개인정보보호법, 정보통신망법, 형법',
  article: 'CWE-89',
  description: 'SQL Injection으로 개인정보 유출 가능',
  liability: 3,
  sanction: 2,
  sanctionType: '형사처벌, 과징금·과태료',
};

const COMMAND_INJECTION_LEGAL: LegalRisk = {
  law: '정보통신망법',
  article: 'CWE-77,78',
  description: 'OS Command Injection',
  liability: 3,
  sanction: 2,
  sanctionType: '형사처벌',
};

const FILE_UPLOAD_LEGAL: LegalRisk = {
  law: '정보통신망법',
  article: 'CWE-434',
  description: '위험한 파일 업로드',
  liability: 3,
  sanction: 2,
  sanctionType: '형사처벌',
};

const DESERIALIZATION_LEGAL: LegalRisk = {
  law: '정보통신망법',
  article: 'CWE-502',
  description: '안전하지 않은 역직렬화',
  liability: 3,
  sanction: 2,
  sanctionType: '형사처벌',
};

const SSRF_LEGAL: LegalRisk = {
  law: '정보통신망법',
  article: 'CWE-918',
  description: 'Server Side Request Forgery',
  liability: 3,
  sanction: 2,
  sanctionType: '형사처벌',
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
  {
    id: 'hardcoded-password',
    cwe: 'CWE-798',
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
  {
    id: 'exposed-api-key',
    cwe: 'CWE-798',
    pattern: /(["']?)(sk-[a-zA-Z0-9_-]{8,}|AKIA[0-9A-Z]{16}|ghp_[A-Za-z0-9]{20,}|AIza[0-9A-Za-z_-]{20,})\1/g,
    severity: 'error',
    category: 'cost',
    message: 'API 키 노출 — 과금 위험',
    detail: 'Git 푸시 시 무단 과금 발생 가능. 즉시 키 재발급 필요',
    makeFix: (_match, lang) => ({
      title: 'API 키 환경변수로 숨기기',
      replacement: lang === 'python' ? 'os.environ.get("OPENAI_API_KEY")' : 'process.env.OPENAI_API_KEY',
    }),
  },
  {
    id: 'sql-injection',
    cwe: 'CWE-89',
    pattern: /["'].*?\b(SELECT|INSERT|UPDATE|DELETE)\b.*?["']\s*\+/gi,
    severity: 'warning',
    category: 'injection',
    message: 'SQL Injection 위험',
    detail: 'parameterized query 또는 ORM 사용 필요',
    makeFix: () => ({
      title: 'SQL 바인딩 파라미터 사용(? 사용)',
      replacement: '"SELECT * FROM users WHERE id=?" #',
    }),
  },
  {
    id: 'weak-hash',
    cwe: 'CWE-327',
    pattern: /\b(md5|sha1)\s*\(/gi,
    severity: 'warning',
    category: 'crypto',
    message: '취약한 해시 알고리즘 (비밀번호 해싱 부적합)',
    detail: 'bcrypt, scrypt, argon2 사용 권장',
    makeFix: () => ({
      title: 'sha256 해시 알고리즘으로 교체',
      replacement: 'sha256(',
    }),
  },
  {
    id: 'dangerous-eval',
    cwe: 'CWE-94',
    pattern: /\beval\s*\(/g,
    severity: 'warning',
    category: 'injection',
    message: 'eval() 사용 — 코드 주입 위험',
    detail: '사용자 입력이 eval에 전달되면 원격 코드 실행 가능',
    makeFix: () => ({
      title: 'eval()을 ast.literal_eval()로 교체',
      replacement: 'ast.literal_eval(',
    }),
  },
  {
    id: 'debug-mode',
    cwe: 'CWE-209',
    pattern: /\bdebug\s*=\s*True\b/g,
    severity: 'info',
    category: 'other',
    message: '디버그 모드 활성화',
    detail: '운영 배포 시 내부 정보 노출 위험',
    makeFix: () => ({
      title: '디버그 모드 비활성화 (False)',
      replacement: 'debug = False',
    }),
  },
  {
  id: 'dangerous-file-upload',
  cwe: 'CWE-434',
  pattern: /\b(move_uploaded_file|MultipartFile|IFormFile|multer|upload)\b/g,
  severity: 'warning',
  category: 'other',
  message: '위험한 파일 업로드 가능성',
  detail: '확장자, MIME Type, 파일명을 검증하세요.',
  legal: FILE_UPLOAD_LEGAL,
  },
  {
  id: 'hardcoded-credential',
  cwe: 'CWE-798',
  pattern: /\b(api[_-]?key|token|access[_-]?key|secret[_-]?key)\s*=\s*["'][^"']+["']/gi,
  severity: 'error',
  category: 'secret',
  message: '하드코딩된 자격증명',
  detail: '환경변수 또는 Secret Manager 사용 권장',
  legal: PIPA_29,
  },
  {
  id: 'path-traversal',
  cwe: 'CWE-22',
  pattern: /\.\.\//g,
  severity: 'warning',
  category: 'injection',
  message: 'Path Traversal 가능성',
  detail: '사용자 입력으로 경로를 생성하지 마세요.',
  legal: {
    law: '정보통신망법',
    article: 'CWE-22',
    description: '경로 탐색',
    liability: 2,
    sanction: 2,
    sanctionType: '형사처벌',
  },
  },
  {
  id: 'os-command-injection',
  cwe: 'CWE-77, CWE-78',
  pattern: /\b(exec|system|Runtime\.getRuntime\(\)|subprocess\.Popen|os\.system)\b/g,
  severity: 'error',
  category: 'injection',
  message: 'OS Command Injection 위험',
  detail: '쉘 명령에 사용자 입력을 전달하지 마세요.',
  legal: COMMAND_INJECTION_LEGAL,
  },
  {
  id: 'unsafe-deserialization',
  cwe: 'CWE-502',
  pattern: /\b(pickle\.loads|ObjectInputStream|BinaryFormatter|deserialize)\b/g,
  severity: 'error',
  category: 'other',
  message: '안전하지 않은 역직렬화',
  detail: '신뢰할 수 없는 데이터를 역직렬화하지 마세요.',
  legal: DESERIALIZATION_LEGAL,
  },
  {
  id: 'ssrf',
  cwe: 'CWE-918',
  pattern: /\b(requests\.get|axios\.get|fetch|http\.get|urllib\.request)\b/g,
  severity: 'warning',
  category: 'injection',
  message: 'SSRF 가능성',
  detail: '사용자 입력 URL을 직접 요청하지 마세요.',
  legal: SSRF_LEGAL,
  },
  {
  id: 'personal-info',
  cwe: 'CWE-200, CWE-359',
  pattern: /\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b/g,
  severity: 'warning',
  category: 'secret',
  message: '개인정보(이메일) 노출',
  detail: '소스코드에 개인정보를 저장하지 마세요.',
  legal: PIPA_29,
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
            cwe: rule.cwe,
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
