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

/** docs/legal-mapping.md의 표시용 제재 유형 */
export type SanctionType =
  | '형사처벌'
  | '과징금·과태료'
  | '형사처벌, 과징금·과태료'
  | '시정명령·권고';

/** 법적 리스크 메타데이터 (사이드 패널 '법적 리스크' 섹션 + 점수 가중에 사용) */
export interface LegalRisk {
  law: string;              // 예: "개인정보보호법"
  article: string;          // 예: "§29"
  description: string;      // 예: "안전조치 의무 위반 가능"
  liability: LiabilityLevel | null; // 법적 책임도, 정보가 없으면 null
  sanction: SanctionLevel | null;   // 제재 수준, 정보가 없으면 null
  sanctionType?: SanctionType; // 사용자에게 보여줄 제재 유형
}

/** 자동 수정 제안 (quick fix) */
export interface FixSuggestion {
  title: string;        // 예: "환경변수로 교체"
  replacement?: string; // 있으면 해당 범위를 이 문자열로 치환
}

/** 탐지된 위험 1건 */
export interface Finding {
  ruleId: string;         // 예: "hardcoded-password"
  cwe?: string;           // 예: "CWE-798" 또는 "CWE-77, CWE-78"
  message: string;        // 예: "하드코딩 비밀번호 — 개인정보보호법 §29"
  detail: string;         // 예: "환경변수(.env) 또는 Secrets Manager 사용 권장"
  severity: Severity;
  category: Category;
  line: number;           // 0-based
  startCol: number;       // 0-based
  endCol: number;
  legal?: LegalRisk;
  fix?: FixSuggestion;
  riskScore?: number;     // 백엔드가 제공한 개별 finding 점수
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
 * 위험도 점수 (위험도_측정식.pdf)
 *
 *   개별 점수 = 빈도 × 기술 심각도 × 법적 가중치 / 60 × 100
 *   종합 점수 = 현재 남아있는 finding의 개별 점수 중 최댓값
 *
 * - 빈도는 오탐을 제외한 진짜위험 비중의 CWE별 등급이다.
 * - 기술 심각도: high/error=3, medium/warning=2, low/info=1,
 *   단 CWE-502는 Critical=4다.
 * - 알려진 CWE의 법적 가중치는 PDF 표를 사용한다.
 * - PDF에 없는 CWE는 희귀 빈도 0.5와 finding의 법적 메타데이터를 사용한다.
 */
const MAX_RAW_SCORE = 3 * 4 * 5;
const DEFAULT_FREQUENCY_SCORE = 0.5;
const DEFAULT_LEGAL_WEIGHT = 1.5;

const FREQUENCY_SCORE_BY_CWE: Record<string, number> = {
  'CWE-798': 3,
  'CWE-532': 3,
  'CWE-295': 2,
  'CWE-79': 2,
  'CWE-89': 1,
  'CWE-434': 1,
  'CWE-256': 1,
  'CWE-201': 1,
  'CWE-502': 0.5,
  'CWE-200': 0.5,
  'CWE-359': 0.5,
  'CWE-918': 0.5,
  'CWE-209': 2,
  'CWE-352': 0.5,
  'CWE-862': 0.5,
  'CWE-327': 0.5,
  'CWE-22': 0.5,
  'CWE-77': 0.5,
  'CWE-78': 0.5,
  'CWE-94': 0.5,
  'CWE-20': 0.5,
  'CWE-330': 1,
  'CWE-770': 0.5,
};

const LEGAL_WEIGHT_BY_CWE: Record<string, number> = {
  'CWE-798': 5,
  'CWE-532': 4,
  'CWE-295': 4,
  'CWE-79': 4,
  'CWE-89': 5,
  'CWE-434': 4,
  'CWE-256': 4,
  'CWE-201': 3,
  'CWE-502': 4,
  'CWE-200': 5,
  'CWE-359': 5,
  'CWE-918': 5,
  'CWE-209': 1.5,
  'CWE-352': 4,
  'CWE-862': 4,
  'CWE-327': 4,
  'CWE-22': 4,
  'CWE-77': 4,
  'CWE-78': 4,
  'CWE-94': 4,
  'CWE-20': 4,
  'CWE-330': 1.5,
  'CWE-770': 1.5,
};

const TECHNICAL_SEVERITY_WEIGHT: Record<Severity, number> = {
  error: 3,
  warning: 2,
  info: 1,
};

export function legalWeight(legal?: LegalRisk): number {
  if (!legal) return DEFAULT_LEGAL_WEIGHT;
  return Math.min(5, Math.max(
    DEFAULT_LEGAL_WEIGHT,
    (legal.liability ?? 1) + (legal.sanction ?? 0.5),
  ));
}

export interface LegalRiskGroup {
  law: string;
  article: string;
  items: Array<{ ruleId: string; legal: LegalRisk }>;
}

/**
 * 같은 법률·조항 아래 서로 다른 룰을 모은다.
 * 같은 사용자 설명과 제재가 여러 룰·위치에서 반복되면 한 번만 포함한다.
 */
export function groupLegalRisks(findings: Finding[]): LegalRiskGroup[] {
  const groups = new Map<
    string,
    { group: LegalRiskGroup; seenItemKeys: Set<string> }
  >();

  for (const finding of findings) {
    const legal = finding.legal;
    if (!legal) continue;

    const key = `${legal.law.trim().replace(/\s+/g, ' ')}\u0000${legal.article.trim().replace(/\s+/g, ' ')}`;
    let entry = groups.get(key);
    if (!entry) {
      entry = {
        group: { law: legal.law, article: legal.article, items: [] },
        seenItemKeys: new Set<string>(),
      };
      groups.set(key, entry);
    }

    const itemKey = `${legal.description.trim().replace(/\s+/g, ' ')}\u0000${legal.sanctionType ?? legal.sanction}`;
    if (entry.seenItemKeys.has(itemKey)) continue;
    entry.seenItemKeys.add(itemKey);
    entry.group.items.push({ ruleId: finding.ruleId, legal });
  }

  return [...groups.values()].map(({ group }) => group);
}

/** 반복되는 법률 문구를 덜어 패널에 표시할 짧은 룰 요약으로 만든다. */
export function compactLegalDescription(description: string): string {
  return description
    .replace(
      /(?:으)?로 (?:관련 )?(?:안전|보호|보안)조치 의무 위반 소지가 있습니다\.?$/,
      '',
    )
    .trim();
}

/** 룰 옆 괄호 안에 넣을 짧은 제재 유형을 반환한다. */
export function compactSanctionLabel(legal: LegalRisk): string {
  switch (legal.sanctionType) {
    case '형사처벌':
      return '형사처벌';
    case '과징금·과태료':
      return '과징금·과태료';
    case '형사처벌, 과징금·과태료':
      return '형사처벌/과징금·과태료';
    case '시정명령·권고':
      return '시정명령·권고';
    default:
      if (legal.sanction === 2) {
        return '형사처벌/과징금·과태료';
      }
      if (legal.sanction === 1) {
        return '과징금·과태료';
      }
      return '시정명령·권고';
  }
}

function cwes(value?: string): string[] {
  return value?.match(/CWE-\d+/gi)?.map((cwe) => cwe.toUpperCase()) ?? [];
}

export function normalizeRiskScore(score: number): number {
  if (!Number.isFinite(score)) return 0;
  return Math.round(Math.min(100, Math.max(0, score)) * 100) / 100;
}

export function computeFindingRiskScore(finding: Finding): number {
  const findingCwes = cwes(finding.cwe);
  const candidates = findingCwes.length > 0 ? findingCwes : [''];
  const fallbackLegalWeight = legalWeight(finding.legal);

  const rawScore = Math.max(...candidates.map((cwe) => {
    const frequency = FREQUENCY_SCORE_BY_CWE[cwe] ?? DEFAULT_FREQUENCY_SCORE;
    const technical = cwe === 'CWE-502'
      ? 4
      : TECHNICAL_SEVERITY_WEIGHT[finding.severity];
    const legal = LEGAL_WEIGHT_BY_CWE[cwe] ?? fallbackLegalWeight;
    return frequency * technical * legal;
  }));

  return normalizeRiskScore(rawScore / MAX_RAW_SCORE * 100);
}

export function computeRiskScore(findings: Finding[]): number {
  return Math.max(
    0,
    ...findings.map((finding) => normalizeRiskScore(
      finding.riskScore ?? computeFindingRiskScore(finding),
    )),
  );
}

export function riskLabel(score: number): string {
  if (score >= 70) return '높음';
  if (score >= 40) return '중간';
  if (score > 0) return '낮음';
  return '안전';
}
