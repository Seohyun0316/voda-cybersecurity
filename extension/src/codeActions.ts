/**
 * Quick Fix 제공자 (F2 담당). 목업의 "자동 수정 제안 보기" 버튼과 연결.
 * Finding.fix.replacement 가 있으면 전구(💡) 메뉴에 수정 제안을 띄운다.
 */
import * as vscode from 'vscode';
import { AnalysisResult, Finding, createAnalyzer } from './analyzer';
import {
  DocumentSnapshot,
  createDocumentSnapshot,
  isDocumentSnapshotCurrent,
  refreshDocumentSnapshot,
} from './documentSnapshot';

interface CachedAnalysis {
  result: AnalysisResult;
  snapshot: DocumentSnapshot;
}

const STALE_DOCUMENT_MESSAGE =
  'VibeSafe: 검사 후 코드가 변경되어 수정을 적용하지 않았습니다. 다시 검사해 주세요.';

export class VibeSafeCodeActionProvider implements vscode.CodeActionProvider {
  static readonly metadata: vscode.CodeActionProviderMetadata = {
    providedCodeActionKinds: [vscode.CodeActionKind.QuickFix],
  };

  /** uri.toString() → 최신 분석 결과와 분석 당시 문서 상태 */
  private readonly results = new Map<string, CachedAnalysis>();

  setResult(result: AnalysisResult, snapshot: DocumentSnapshot): void {
    this.results.set(snapshot.uri, { result, snapshot });
  }

  provideCodeActions(
    document: vscode.TextDocument,
    range: vscode.Range,
  ): vscode.CodeAction[] {
    const cached = this.results.get(document.uri.toString());
    if (!cached) return [];

    const actions: vscode.CodeAction[] = [];
    for (const f of cached.result.findings) {
      if (!f.fix?.replacement) continue;
      const fRange = new vscode.Range(f.line, f.startCol, f.line, f.endCol);
      if (!fRange.intersection(range)) continue;

      const action = new vscode.CodeAction(f.fix.title, vscode.CodeActionKind.QuickFix);
      action.command = {
        command: 'vibesafe.applyQuickFix',
        title: f.fix.title,
        arguments: [document.uri, f],
      };
      action.isPreferred = true;
      actions.push(action);
    }
    return actions;
  }

  async applyFix(uri: vscode.Uri, finding: Finding): Promise<void> {
    const key = uri.toString();
    const cached = this.results.get(key);
    if (!cached) {
      vscode.window.showInformationMessage(STALE_DOCUMENT_MESSAGE);
      return;
    }

    const document = await vscode.workspace.openTextDocument(uri);
    if (!isCurrentDocument(document, cached.snapshot)) {
      this.results.delete(key);
      vscode.window.showInformationMessage(STALE_DOCUMENT_MESSAGE);
      return;
    }

    const currentFinding = cached.result.findings.find((candidate) =>
      candidate === finding
      || (
        candidate.ruleId === finding.ruleId
        && candidate.line === finding.line
        && candidate.startCol === finding.startCol
        && candidate.endCol === finding.endCol
        && candidate.fix?.replacement === finding.fix?.replacement
      ));
    if (!currentFinding?.fix?.replacement) {
      vscode.window.showInformationMessage(STALE_DOCUMENT_MESSAGE);
      return;
    }

    const edit = new vscode.WorkspaceEdit();
    edit.replace(
      uri,
      new vscode.Range(
        currentFinding.line,
        currentFinding.startCol,
        currentFinding.line,
        currentFinding.endCol,
      ),
      currentFinding.fix.replacement,
    );

    const success = await vscode.workspace.applyEdit(edit);
    if (!success) {
      vscode.window.showErrorMessage('VibeSafe: 자동 수정을 적용하지 못했습니다.');
      return;
    }

    // 적용 직후 기존 좌표와 스냅샷은 더 이상 유효하지 않다.
    this.results.delete(key);
  }
}

/** "자동 수정 제안 적용" — 위에서부터 한 건씩 적용하고 다음 수정 위치를 다시 계산 */
export async function applyAllFixes(
  result: AnalysisResult | undefined,
  snapshot: DocumentSnapshot | undefined,
): Promise<void> {
  const editor = vscode.window.activeTextEditor;
  if (!editor || !result || !snapshot) {
    vscode.window.showInformationMessage('VibeSafe: 적용할 수정 제안이 없습니다.');
    return;
  }
  if (editor.document.fileName !== result.fileName) {
    vscode.window.showInformationMessage('VibeSafe: 현재 파일을 먼저 검사한 뒤 자동 수정을 적용해 주세요.');
    return;
  }
  if (!isCurrentDocument(editor.document, snapshot)) {
    vscode.window.showInformationMessage(STALE_DOCUMENT_MESSAGE);
    return;
  }
  const fixable = result.findings.filter((f): f is Finding & { fix: { replacement: string; title: string } } =>
    Boolean(f.fix?.replacement),
  );
  if (fixable.length === 0) {
    vscode.window.showInformationMessage('VibeSafe: 자동 수정 가능한 항목이 없습니다.');
    return;
  }

  const target = fixable[0];
  const edit = new vscode.WorkspaceEdit();
  edit.replace(
    editor.document.uri,
    new vscode.Range(target.line, target.startCol, target.line, target.endCol),
    target.fix.replacement,
  );

  const success = await vscode.workspace.applyEdit(edit);
  if (!success) {
    vscode.window.showErrorMessage('VibeSafe: 자동 수정을 적용하지 못했습니다.');
    return;
  }

  const remainingCount = fixable.length - 1;
  vscode.window.showInformationMessage(
    `VibeSafe: 1건 자동 수정 적용 완료 ${remainingCount > 0 ? `(남은 수정 ${remainingCount}건)` : '(모든 수정 완료!)'}`,
  );

  // 다음 버튼 클릭에서 이미 수정한 항목을 다시 적용하지 않도록 즉시 제거한다.
  result.findings = result.findings.filter((finding) => finding !== target);

  // 교체 문자열의 길이가 달라져도 다음 항목의 위치가 정확하도록 조용히 재분석한다.
  try {
    const doc = editor.document;
    const currentSnapshot = snapshotFromDocument(doc);
    const analyzer = createAnalyzer(doc.languageId);
    const updatedResult = await analyzer.analyze(
      currentSnapshot.text,
      doc.fileName,
      doc.languageId,
    );
    if (!isCurrentDocument(doc, currentSnapshot)) return;
    result.findings = updatedResult.findings;
    refreshDocumentSnapshot(snapshot, currentSnapshot);
  } catch {
    // 원격 분석이 일시적으로 실패해도 이미 적용된 수정은 유지한다.
  }
}

function snapshotFromDocument(document: vscode.TextDocument): DocumentSnapshot {
  return createDocumentSnapshot(
    document.uri.toString(),
    document.version,
    document.getText(),
  );
}

function isCurrentDocument(
  document: vscode.TextDocument,
  snapshot: DocumentSnapshot,
): boolean {
  return isDocumentSnapshotCurrent(snapshot, snapshotFromDocument(document));
}
