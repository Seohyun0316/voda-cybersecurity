/**
 * ML 백엔드(/detect) 원격 분석기 (F2 담당).
 *
 * API 스펙은 저장소 docs/api-spec.md v1.0 (F 파트 확정안) 기준.
 * 백엔드 응답(snake_case)을 내부 모델(types.ts)로 변환하는
 * 어댑터(mapDetectResponse)를 포함한다.
 */
import {
  AnalysisResult,
  Analyzer,
  Category,
  Finding,
  LiabilityLevel,
  SanctionType,
  SanctionLevel,
  Severity,
  computeRiskScore,
  normalizeRiskScore,
} from './types';

/** /detect 응답 스키마 (docs/api-spec.md v1.0 — snake_case) */
export interface DetectLegal {
  law: string;
  article: string;
  description: string;
  liability: LiabilityLevel | null; // 1~3 또는 법적 가중치 정보 없음
  sanction: SanctionLevel | null;   // 0.5~2 또는 법적 가중치 정보 없음
  sanction_type?: SanctionType;
}

export interface DetectFinding {
  rule_id: string;                       // 예: "A04-798-001"
  cwe?: string;                          // 예: "CWE-798"
  category?: string;                     // 백엔드 상세 category 또는 Extension category
  severity: 'high' | 'medium' | 'low';
  line: number;                          // ★ 0-based (스펙 확정)
  start_col: number;                     // 0-based
  end_col: number;
  message: string;
  detail?: string;
  risk_score?: number;
  legal?: DetectLegal | null;
  fix?: { title: string; replacement?: string } | null;
}

export interface DetectResponse {
  risk_score?: number | null;            // 파일 전체 점수 (생략/null 시 클라이언트 계산)
  findings: DetectFinding[];
  analyzed_at?: string;
}

const SEVERITY_MAP: Record<DetectFinding['severity'], Severity> = {
  high: 'error',
  medium: 'warning',
  low: 'info',
};

const ALLOWED_SEVERITIES = new Set<unknown>(['high', 'medium', 'low']);
const ALLOWED_LIABILITY_LEVELS = new Set<unknown>([1, 2, 3]);
const ALLOWED_SANCTION_LEVELS = new Set<unknown>([0.5, 1, 2]);
const ALLOWED_SANCTION_TYPES = new Set<unknown>([
  '형사처벌',
  '과징금·과태료',
  '형사처벌, 과징금·과태료',
  '시정명령·권고',
]);
const INVALID_RESPONSE_PREFIX = '서버 응답 형식이 올바르지 않습니다';

const BACKEND_CATEGORY_MAP: Record<string, Category> = {
  secret: 'secret',
  privacy: 'secret',
  information_exposure: 'secret',
  logging: 'secret',
  input_validation: 'injection',
  path_traversal: 'injection',
  command_injection: 'injection',
  sql_injection: 'injection',
  code_injection: 'injection',
  xss: 'injection',
  insecure_deserialization: 'injection',
  ssrf: 'injection',
  cryptography: 'crypto',
  tls: 'crypto',
  resource_exhaustion: 'cost',
  csrf: 'other',
  file_upload: 'other',
  access_control: 'other',
  authentication: 'other',
  cost: 'cost',
  injection: 'injection',
  crypto: 'crypto',
  other: 'other',
};

/** category 누락 시 rule_id/cwe로 추정하는 방어 로직 */
function fallbackCategory(ruleId: string, cwe?: string): Category {
  if (cwe === 'CWE-798' || ruleId.startsWith('PII')) return 'secret';
  if (ruleId.startsWith('A04')) return 'crypto';
  if (ruleId.startsWith('A05')) return 'injection';
  return 'other';
}

function mapCategory(finding: DetectFinding): Category {
  // 백엔드는 CWE-798 전체를 secret으로 분류하지만, 이 룰은 API 키 노출 전용이라
  // 사용자에게 과금 위험으로 별도 표시해야 한다.
  if (finding.rule_id === 'A04-798-002') return 'cost';
  return BACKEND_CATEGORY_MAP[finding.category ?? '']
    ?? fallbackCategory(finding.rule_id, finding.cwe);
}

/**
 * /detect 응답을 런타임에서 검증한다.
 * 이전 백엔드와의 호환을 위해 risk_score, analyzed_at과 일부 표시 필드는
 * 생략을 허용하되, 결과 매핑에 필요한 필드와 좌표는 반드시 확인한다.
 */
export function validateDetectResponse(value: unknown): DetectResponse {
  const response = expectObject(value, '응답');
  if (!Array.isArray(response.findings)) {
    invalid('findings', '배열이어야 합니다');
  }

  validateOptionalScore(response.risk_score, 'risk_score', true);
  if (response.analyzed_at !== undefined) {
    const analyzedAt = expectString(response.analyzed_at, 'analyzed_at');
    if (analyzedAt.trim() === '' || !Number.isFinite(Date.parse(analyzedAt))) {
      invalid('analyzed_at', '유효한 날짜 문자열이어야 합니다');
    }
  }

  response.findings.forEach((finding, index) => {
    validateFinding(finding, `findings[${index}]`);
  });
  return value as DetectResponse;
}

/** /detect 응답 → 내부 AnalysisResult 변환 (순수 함수 — 유닛 테스트 대상) */
export function mapDetectResponse(
  value: unknown,
  text: string,
  fileName: string,
  languageId: string,
): AnalysisResult {
  const res = validateDetectResponse(value);
  const findings: Finding[] = (res.findings ?? []).map((d) => ({
    ruleId: d.rule_id,
    cwe: d.cwe,
    message: d.message,
    detail: d.detail ?? d.cwe ?? '',
    severity: SEVERITY_MAP[d.severity] ?? 'warning',
    category: mapCategory(d),
    line: d.line,
    startCol: d.start_col ?? 0,
    endCol: d.end_col ?? d.start_col + 1,
    legal: d.legal
      ? {
          law: d.legal.law,
          article: d.legal.article,
          description: d.legal.description,
          liability: d.legal.liability,
          sanction: d.legal.sanction,
          sanctionType: d.legal.sanction_type,
        }
      : undefined,
    fix: d.fix ?? undefined,
    riskScore: d.risk_score,
  }));

  return {
    fileName,
    languageId,
    // 백엔드가 전체 점수를 주면 사용, 없으면 PDF 산식으로 계산
    riskScore: normalizeRiskScore(res.risk_score ?? computeRiskScore(findings)),
    findings,
    engine: 'remote',
    analyzedAt: res.analyzed_at ?? new Date().toISOString(),
  };
}

export class RemoteAnalyzer implements Analyzer {
  readonly kind = 'remote' as const;

  constructor(
    private readonly endpoint: string,
    /** TODO(백엔드 연결 시): 인증 토큰 주입 */
    private readonly apiKey?: string,
  ) {}

  async analyze(text: string, fileName: string, languageId: string): Promise<AnalysisResult> {
    const res = await fetch(this.endpoint, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        // TODO(백엔드 연결 시): 'Authorization': `Bearer ${this.apiKey}`
      },
      // 요청 스키마 (api-spec.md v1.0)
      body: JSON.stringify({ code: text, language: languageId, file_name: fileName }),
      signal: AbortSignal.timeout(10_000),
    });

    if (!res.ok) {
      throw new Error(`VibeSafe 백엔드 오류: HTTP ${res.status}`);
    }

    let data: unknown;
    try {
      data = await res.json();
    } catch {
      throw new Error('서버 응답이 올바른 JSON이 아닙니다.');
    }
    return mapDetectResponse(data, text, fileName, languageId);
  }
}

function validateFinding(value: unknown, path: string): void {
  const finding = expectObject(value, path);
  expectNonEmptyString(finding.rule_id, `${path}.rule_id`);
  expectNonEmptyString(finding.message, `${path}.message`);

  if (!ALLOWED_SEVERITIES.has(finding.severity)) {
    invalid(`${path}.severity`, 'high, medium, low 중 하나여야 합니다');
  }

  expectNonNegativeInteger(finding.line, `${path}.line`);
  const startCol = expectNonNegativeInteger(
    finding.start_col,
    `${path}.start_col`,
  );
  const endCol = expectNonNegativeInteger(finding.end_col, `${path}.end_col`);
  if (endCol < startCol) {
    invalid(`${path}.end_col`, 'start_col보다 작을 수 없습니다');
  }
  validateOptionalString(finding.cwe, `${path}.cwe`, true);
  validateOptionalString(finding.category, `${path}.category`, true);
  validateOptionalString(finding.detail, `${path}.detail`);
  validateOptionalScore(finding.risk_score, `${path}.risk_score`);

  if (finding.legal !== undefined && finding.legal !== null) {
    validateLegal(finding.legal, `${path}.legal`);
  }
  if (finding.fix !== undefined && finding.fix !== null) {
    validateFix(finding.fix, `${path}.fix`);
  }
}

function validateLegal(value: unknown, path: string): void {
  const legal = expectObject(value, path);
  expectNonEmptyString(legal.law, `${path}.law`);
  expectNonEmptyString(legal.article, `${path}.article`);
  expectString(legal.description, `${path}.description`);

  if (legal.liability !== null && !ALLOWED_LIABILITY_LEVELS.has(legal.liability)) {
    invalid(`${path}.liability`, 'null 또는 1, 2, 3 중 하나여야 합니다');
  }
  if (legal.sanction !== null && !ALLOWED_SANCTION_LEVELS.has(legal.sanction)) {
    invalid(`${path}.sanction`, 'null 또는 0.5, 1, 2 중 하나여야 합니다');
  }
  if (
    legal.sanction_type !== undefined
    && !ALLOWED_SANCTION_TYPES.has(legal.sanction_type)
  ) {
    invalid(`${path}.sanction_type`, '지원하는 제재 유형이어야 합니다');
  }
}

function validateFix(value: unknown, path: string): void {
  const fix = expectObject(value, path);
  expectNonEmptyString(fix.title, `${path}.title`);
  validateOptionalString(fix.replacement, `${path}.replacement`);
}

function validateOptionalScore(
  value: unknown,
  path: string,
  allowNull = false,
): void {
  if (value === undefined || (allowNull && value === null)) return;
  if (
    typeof value !== 'number'
    || !Number.isFinite(value)
    || value < 0
    || value > 100
  ) {
    invalid(path, '0~100 범위의 유한한 숫자여야 합니다');
  }
}

function validateOptionalString(
  value: unknown,
  path: string,
  nonEmpty = false,
): void {
  if (value === undefined) return;
  if (nonEmpty) {
    expectNonEmptyString(value, path);
  } else {
    expectString(value, path);
  }
}

function expectObject(value: unknown, path: string): Record<string, unknown> {
  if (typeof value !== 'object' || value === null || Array.isArray(value)) {
    invalid(path, 'JSON 객체여야 합니다');
  }
  return value as Record<string, unknown>;
}

function expectString(value: unknown, path: string): string {
  if (typeof value !== 'string') {
    invalid(path, '문자열이어야 합니다');
  }
  return value;
}

function expectNonEmptyString(value: unknown, path: string): string {
  const stringValue = expectString(value, path);
  if (stringValue.trim() === '') {
    invalid(path, '비어 있지 않은 문자열이어야 합니다');
  }
  return stringValue;
}

function expectNonNegativeInteger(value: unknown, path: string): number {
  if (!Number.isInteger(value) || (value as number) < 0) {
    invalid(path, '0 이상의 정수여야 합니다');
  }
  return value as number;
}

function invalid(path: string, expectation: string): never {
  throw new Error(`${INVALID_RESPONSE_PREFIX}: ${path}은(는) ${expectation}.`);
}
