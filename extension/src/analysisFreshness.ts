import {
  DocumentSnapshot,
  isDocumentSnapshotCurrent,
} from './documentSnapshot';

/**
 * 분석 응답을 현재 UI에 반영해도 되는지 확인한다.
 * 최신 검사 ID와 분석 당시 문서 상태가 모두 유지되어야 한다.
 */
export function isAnalysisResultCurrent(
  scanId: number,
  latestScanId: number,
  analyzedDocument: DocumentSnapshot,
  currentDocument: DocumentSnapshot | undefined,
): boolean {
  return scanId === latestScanId
    && currentDocument !== undefined
    && isDocumentSnapshotCurrent(analyzedDocument, currentDocument);
}
