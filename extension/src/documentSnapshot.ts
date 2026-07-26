/**
 * 분석 시점의 문서 상태. VS Code API에 의존하지 않아 검증 로직을
 * 단위 테스트할 수 있다.
 */
export interface DocumentSnapshot {
  uri: string;
  version: number;
  text: string;
}

export function createDocumentSnapshot(
  uri: string,
  version: number,
  text: string,
): DocumentSnapshot {
  return { uri, version, text };
}

export function isDocumentSnapshotCurrent(
  snapshot: DocumentSnapshot,
  current: DocumentSnapshot,
): boolean {
  return snapshot.uri === current.uri
    && snapshot.version === current.version
    && snapshot.text === current.text;
}

export function refreshDocumentSnapshot(
  snapshot: DocumentSnapshot,
  current: DocumentSnapshot,
): void {
  snapshot.uri = current.uri;
  snapshot.version = current.version;
  snapshot.text = current.text;
}
