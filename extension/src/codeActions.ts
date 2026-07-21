/**
 * Quick Fix 제공자 (F2 담당). 목업의 "자동 수정 제안 보기" 버튼과 연결.
 * Finding.fix.replacement 가 있으면 전구(💡) 메뉴에 수정 제안을 띄운다.
 */
import * as vscode from 'vscode';
import { AnalysisResult, Finding } from './analyzer';

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

/** "자동 수정 제안 보기" — 적용 가능한 fix를 전부 한 번에 적용 */
export async function applyAllFixes(result: AnalysisResult | undefined): Promise<void> {
  const editor = vscode.window.activeTextEditor;
  if (!editor || !result) {
    vscode.window.showInformationMessage('VibeSafe: 적용할 수정 제안이 없습니다.');
    return;
  }
  const fixable = result.findings.filter((f): f is Finding & { fix: { replacement: string; title: string } } =>
    Boolean(f.fix?.replacement),
  );
  if (fixable.length === 0) {
    vscode.window.showInformationMessage('VibeSafe: 자동 수정 가능한 항목이 없습니다.');
    return;
  }
  const edit = new vscode.WorkspaceEdit();
  for (const f of fixable) {
    edit.replace(editor.document.uri, new vscode.Range(f.line, f.startCol, f.line, f.endCol), f.fix.replacement);
  }
  await vscode.workspace.applyEdit(edit);
  vscode.window.showInformationMessage(`VibeSafe: ${fixable.length}건 자동 수정 적용 완료`);
}
