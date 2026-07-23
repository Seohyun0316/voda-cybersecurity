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
  SanctionLevel,
  Severity,
  computeRiskScore,
} from './types';

/** /detect 응답 스키마 (docs/api-spec.md v1.0 — snake_case) */
export interface DetectLegal {
  law: string;
  article: string;
  description: string;
  liability: LiabilityLevel; // 1~3 (CONTRACT.md §1 표)
  sanction: SanctionLevel;   // 0.5~2
}

export interface DetectFinding {
  rule_id: string;                       // 예: "A04-798-001"
  cwe?: string;                          // 예: "CWE-798"
  category?: Category;
  severity: 'high' | 'medium' | 'low';
  line: number;                          // ★ 0-based (스펙 확정)
  start_col: number;                     // 0-based
  end_col: number;
  message: string;
  detail?: string;
  risk_score?: number;
  legal?: DetectLegal;
  fix?: { title: string; replacement?: string };
}

export interface DetectResponse {
  risk_score?: number;                   // 파일 전체 점수 (생략 시 클라이언트 계산)
  findings: DetectFinding[];
  analyzed_at?: string;
}

const SEVERITY_MAP: Record<DetectFinding['severity'], Severity> = {
  high: 'error',
  medium: 'warning',
  low: 'info',
};

/** category 누락 시 rule_id/cwe로 추정하는 방어 로직 */
function fallbackCategory(ruleId: string, cwe?: string): Category {
  if (cwe === 'CWE-798' || ruleId.startsWith('PII')) return 'secret';
  if (ruleId.startsWith('A04')) return 'crypto';
  if (ruleId.startsWith('A05')) return 'injection';
  return 'other';
}

/** /detect 응답 → 내부 AnalysisResult 변환 (순수 함수 — 유닛 테스트 대상) */
export function mapDetectResponse(
  res: DetectResponse,
  text: string,
  fileName: string,
  languageId: string,
): AnalysisResult {
  const findings: Finding[] = (res.findings ?? []).map((d) => ({
    ruleId: d.rule_id,
    message: d.message,
    detail: d.detail ?? d.cwe ?? '',
    severity: SEVERITY_MAP[d.severity] ?? 'warning',
    category: d.category ?? fallbackCategory(d.rule_id, d.cwe),
    line: d.line,
    startCol: d.start_col ?? 0,
    endCol: d.end_col ?? d.start_col + 1,
    legal: d.legal,
    fix: d.fix,
  }));

  return {
    fileName,
    languageId,
    // 백엔드가 전체 점수를 주면 사용, 없으면 계약 공식(§1)으로 계산
    riskScore: Math.min(100, Math.round(res.risk_score ?? computeRiskScore(findings))),
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

    const data = (await res.json()) as DetectResponse;
    return mapDetectResponse(data, text, fileName, languageId);
  }
}
