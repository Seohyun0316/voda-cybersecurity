/**
 * VibeSafe 공통 타입 정의.
 *
 * ⚠️ 이 파일이 F1(UI)과 F2(엔진) 사이의 "계약(contract)"이다.
 * ML 백엔드 API도 이 스키마(AnalysisResult JSON)를 그대로 반환하면
 * 프론트 코드 수정 없이 연결된다. 확정 규칙은 CONTRACT.md 참고.
 */

export type Severity = 'error' | 'warning' | 'info';

export type Category =
  | 'secret'     // 하드코딩 비밀번호/키
  | 'injection'  // SQL Injection 등
  | 'crypto'     // 취약한 암호화/해싱
  | 'cost'       // API 과금 위험
  | 'other';

/**
 * 법적 책임도 (CONTRACT.md §1)
 *  3 = 형사처벌 규정
 *  2 = 과징금·과태료 부과 가능한 의무조항
 *  1 = 일반 관리·안전조치 의무
 */
export type LiabilityLevel = 1 | 2 | 3;

/**
 * 제재 수준 (CONTRACT.md §1)
 *  2   = 형사처벌 또는 1억 이상 과징금 사례
 *  1   = 과징금·과태료 사례
 *  0.5 = 시정명령·권고 또는 사례 없음
 */
export type SanctionLevel = 0.5 | 1 | 2;

/** 법적 리스크 메타데이터 (사이드 패널 '법적 리스크' 섹션 + 점수 가중에 사용) */
export interface LegalRisk {
  law: string;              // 예: "개인정보보호법"
  article: string;          // 예: "§29"
  description: string;      // 예: "안전조치 의무 위반 가능"
  liability: LiabilityLevel; // 법적 책임도
  sanction: SanctionLevel;   // 제재 수준
}

/** 자동 수정 제안 (quick fix) */
export interface FixSuggestion {
  title: string;        // 예: "환경변수로 교체"
  replacement?: string; // 있으면 해당 범위를 이 문자열로 치환
}

/** 탐지된 위험 1건 */
export interface Finding {
  ruleId: string;         // 예: "hardcoded-password"
  message: string;        // 예: "하드코딩 비밀번호 — 개인정보보호법 §29"
  detail: string;         // 예: "환경변수(.env) 또는 Secrets Manager 사용 권장"
  severity: Severity;
  category: Category;
  line: number;           // 0-based
  startCol: number;       // 0-based
  endCol: number;
  legal?: LegalRisk;
  fix?: FixSuggestion;
}

/** 파일 1개에 대한 분석 결과 */
export interface AnalysisResult {
  fileName: string;
  languageId: string;
  riskScore: number;      // 0~100
  findings: Finding[];
  engine: 'rules' | 'remote';
  analyzedAt: string;     // ISO 8601
}

/** 분석 엔진 인터페이스 — 룰 엔진과 ML 원격 분석기가 모두 구현 */
export interface Analyzer {
  readonly kind: 'rules' | 'remote';
  analyze(text: string, fileName: string, languageId: string): Promise<AnalysisResult>;
}

/**
 * 위험도 점수 (확정 공식 — CONTRACT.md §1)
 *
 *   위험 점수 = Σ (빈도 × 기술 심각도 가중치 × 법적 가중치), 100점 만점
 *
 * - 기술 심각도 가중치: error 25, warning 12, info 4
 * - 법적 가중치 = 법적 책임도(liability) + 제재 수준(sanction), legal 없으면 1.0
 *   (범위: 1+0.5=1.5 ~ 3+2=5)
 * - 빈도: 같은 위험이 n번 탐지되면 n번 합산 (reduce가 담당)
 * - 총합 반올림 후 상한 100
 */
const SEVERITY_WEIGHT: Record<Severity, number> = { error: 25, warning: 12, info: 4 };

export function legalWeight(legal?: LegalRisk): number {
  if (!legal) return 1;
  return (legal.liability ?? 1) + (legal.sanction ?? 0.5); // 백엔드가 누락 시 최소값으로 방어
}

export function computeRiskScore(findings: Finding[]): number {
  const score = findings.reduce(
    (sum, f) => sum + SEVERITY_WEIGHT[f.severity] * legalWeight(f.legal),
    0,
  );
  return Math.min(100, Math.round(score));
}

export function riskLabel(score: number): string {
  if (score >= 70) return '높음';
  if (score >= 40) return '중간';
  if (score > 0) return '낮음';
  return '안전';
}
