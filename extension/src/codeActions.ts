/**
 * Quick Fix 제공자 (F2 담당). 목업의 "자동 수정 제안 보기" 버튼과 연결.
 * Finding.fix.replacement 가 있으면 전구(💡) 메뉴에 수정 제안을 띄운다.
 */
import * as vscode from 'vscode';
import { AnalysisResult, Finding, createAnalyzer } from './analyzer';

export class VibeSafeCodeActionProvider implements vscode.CodeActionProvider {
  static readonly metadata: vscode.CodeActionProviderMetadata = {
    providedCodeActionKinds: [vscode.CodeActionKind.QuickFix],
  };

  /** uri.toString() → 최신 분석 결과 캐시 */
  private readonly results = new Map<string, AnalysisResult>();

  setResult(uri: vscode.Uri, result: AnalysisResult): void {
    this.results.set(uri.toString(), result);
  }

  provideCodeActions(
    document: vscode.TextDocument,
    range: vscode.Range,
  ): vscode.CodeAction[] {
    const result = this.results.get(document.uri.toString());
    if (!result) return [];

    const actions: vscode.CodeAction[] = [];
    for (const f of result.findings) {
      if (!f.fix?.replacement) continue;
      const fRange = new vscode.Range(f.line, f.startCol, f.line, f.endCol);
      if (!fRange.intersection(range)) continue;

      const action = new vscode.CodeAction(f.fix.title, vscode.CodeActionKind.QuickFix);
      action.edit = new vscode.WorkspaceEdit();
      action.edit.replace(document.uri, fRange, f.fix.replacement);
      action.isPreferred = true;
      actions.push(action);
    }
    return actions;
  }
}

/** "자동 수정 제안 적용" — 위에서부터 한 건씩 적용하고 다음 수정 위치를 다시 계산 */
export async function applyAllFixes(result: AnalysisResult | undefined): Promise<void> {
  const editor = vscode.window.activeTextEditor;
  if (!editor || !result) {
    vscode.window.showInformationMessage('VibeSafe: 적용할 수정 제안이 없습니다.');
    return;
  }
  if (editor.document.fileName !== result.fileName) {
    vscode.window.showInformationMessage('VibeSafe: 현재 파일을 먼저 검사한 뒤 자동 수정을 적용해 주세요.');
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
    const analyzer = createAnalyzer();
    const updatedResult = await analyzer.analyze(doc.getText(), doc.fileName, doc.languageId);
    result.findings = updatedResult.findings;
  } catch {
    // 원격 분석이 일시적으로 실패해도 이미 적용된 수정은 유지한다.
  }
}
