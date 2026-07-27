import type { AnalysisResult, Finding } from './analyzer/types';
import type { DocumentSnapshot } from './documentSnapshot';
import { rebaseFindings, type OffsetTextChange } from './findingRebase';

/**
 * 마지막 수동 검사에서 확정된 결과와 편집 중 사용할 finding을 분리한다.
 *
 * confirmedResult는 다음 수동 검사가 성공할 때까지 절대 변경하지 않는다.
 * workingFindings와 snapshot만 문서 편집에 맞춰 갱신한다.
 */
export class DocumentAnalysisState {
  readonly confirmedResult: AnalysisResult;
  private currentFindings: Finding[];
  private currentSnapshot: DocumentSnapshot;

  constructor(result: AnalysisResult, snapshot: DocumentSnapshot) {
    this.confirmedResult = result;
    this.currentFindings = result.findings;
    this.currentSnapshot = snapshot;
  }

  get workingFindings(): readonly Finding[] {
    return this.currentFindings;
  }

  get snapshot(): DocumentSnapshot {
    return this.currentSnapshot;
  }

  rebase(
    snapshot: DocumentSnapshot,
    changes: OffsetTextChange[],
  ): readonly Finding[] {
    this.currentFindings = rebaseFindings(
      this.currentFindings,
      this.currentSnapshot.text,
      snapshot.text,
      changes,
    );
    this.currentSnapshot = snapshot;
    return this.currentFindings;
  }
}

/**
 * 패널이 표시하는 마지막 확정 결과와 stale 전이를 관리한다.
 * markStale()은 false → true 전이에서만 true를 반환하므로 Webview를 한 번만
 * 다시 렌더링하는 기준으로 사용할 수 있다.
 */
export class ConfirmedAnalysisState {
  private currentResult?: AnalysisResult;
  private stale = false;

  get result(): AnalysisResult | undefined {
    return this.currentResult;
  }

  get isStale(): boolean {
    return this.stale;
  }

  confirm(result: AnalysisResult): void {
    this.currentResult = result;
    this.stale = false;
  }

  markStale(): boolean {
    if (!this.currentResult || this.stale) return false;
    this.stale = true;
    return true;
  }
}
