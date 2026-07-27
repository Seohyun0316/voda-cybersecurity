/**
 * 수정 제안 제공자 (F2 담당).
 * Finding.fix.replacement가 있으면 원본 코드를 변경하지 않고 hover로 미리 보여준다.
 */
import * as vscode from 'vscode';
import { AnalysisResult, Finding, computeRiskScore } from './analyzer';
import {
  DocumentSnapshot,
  createDocumentSnapshot,
  isDocumentSnapshotCurrent,
} from './documentSnapshot';
import {
  buildSuggestedCodeDiff,
  buildSuggestedCodePreview,
} from './fixSuggestionPreview';
import { rebaseFindings } from './findingRebase';

interface CachedAnalysis {
  result: AnalysisResult;
  snapshot: DocumentSnapshot;
}

const STALE_DOCUMENT_MESSAGE =
  'VibeSafe: 검사 후 코드가 변경되어 수정 제안을 표시하지 않았습니다. 다시 검사해 주세요.';

export class VibeSafeCodeActionProvider implements vscode.CodeActionProvider, vscode.HoverProvider {
  static readonly metadata: vscode.CodeActionProviderMetadata = {
    providedCodeActionKinds: [vscode.CodeActionKind.QuickFix],
  };

  /** uri.toString() → 최신 분석 결과와 분석 당시 문서 상태 */
  private readonly results = new Map<string, CachedAnalysis>();

  setResult(result: AnalysisResult, snapshot: DocumentSnapshot): void {
    this.results.set(snapshot.uri, { result, snapshot });
  }

  /**
   * 한 취약점을 수정한 뒤에도 나머지 결과를 계속 사용할 수 있도록 위치를 보정한다.
   * 편집과 겹친 결과만 제거하며 새 취약점 탐지는 다음 수동 검사에서 수행한다.
   */
  handleDocumentChange(event: vscode.TextDocumentChangeEvent): AnalysisResult | undefined {
    const key = event.document.uri.toString();
    const cached = this.results.get(key);
    if (!cached || event.contentChanges.length === 0) return undefined;

    const currentSnapshot = snapshotFromDocument(event.document);
    const findings = rebaseFindings(
      cached.result.findings,
      cached.snapshot.text,
      currentSnapshot.text,
      event.contentChanges.map((change) => ({
        rangeOffset: change.rangeOffset,
        rangeLength: change.rangeLength,
        text: change.text,
      })),
    );
    cached.result = {
      ...cached.result,
      findings,
      riskScore: computeRiskScore(findings),
    };
    cached.snapshot = currentSnapshot;
    return cached.result;
  }

  provideCodeActions(
    document: vscode.TextDocument,
    range: vscode.Range,
  ): vscode.CodeAction[] {
    const cached = this.results.get(document.uri.toString());
    if (!cached || !isCurrentDocument(document, cached.snapshot)) return [];

    const actions: vscode.CodeAction[] = [];
    for (const f of cached.result.findings) {
      if (!f.fix?.replacement) continue;
      const fRange = new vscode.Range(f.line, f.startCol, f.line, f.endCol);
      if (!fRange.intersection(range)) continue;

      const action = new vscode.CodeAction(
        `수정 제안 보기: ${f.fix.title}`,
        vscode.CodeActionKind.QuickFix,
      );
      action.command = {
        command: 'vibesafe.showFixSuggestion',
        title: f.fix.title,
        arguments: [document.uri, f],
      };
      actions.push(action);
    }
    return actions;
  }

  provideHover(
    document: vscode.TextDocument,
    position: vscode.Position,
  ): vscode.Hover | undefined {
    const cached = this.results.get(document.uri.toString());
    if (!cached || !isCurrentDocument(document, cached.snapshot)) return undefined;

    const finding = cached.result.findings.find(
      (candidate) =>
        Boolean(candidate.fix?.replacement)
        && findingRange(document, candidate).contains(position),
    );
    const replacement = finding?.fix?.replacement;
    if (!replacement) return undefined;

    const range = findingRange(document, finding);
    const originalLine = document.lineAt(range.start.line).text;
    const preview = buildSuggestedCodePreview(
      originalLine,
      range.start.character,
      range.end.character,
      replacement,
    );
    const contents = new vscode.MarkdownString(undefined, true);
    contents.appendMarkdown('$(lightbulb) **VibeSafe 수정 제안**\n\n');
    contents.appendMarkdown('**제안 내용:** ');
    contents.appendText(finding.fix?.title ?? '안전한 코드로 변경');
    contents.appendMarkdown('\n\n');
    contents.appendMarkdown('🛡️ **변경 전 → 안전 코드**\n\n');
    contents.appendCodeblock(
      buildSuggestedCodeDiff(originalLine, preview),
      'diff',
    );
    contents.isTrusted = false;

    return new vscode.Hover(contents, range);
  }

  /** 전구 메뉴에서 선택한 한 건의 수정 제안을 코드 위에 표시한다. */
  async showSuggestion(uri: vscode.Uri, finding: Finding): Promise<void> {
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

    const editor = await vscode.window.showTextDocument(document, {
      preview: false,
      preserveFocus: false,
    });
    await this.presentSuggestion(editor, currentFinding);
  }

  private async presentSuggestion(
    editor: vscode.TextEditor,
    finding: Finding,
  ): Promise<void> {
    const range = findingRange(editor.document, finding);
    editor.selection = new vscode.Selection(range.start, range.start);
    editor.revealRange(range, vscode.TextEditorRevealType.InCenterIfOutsideViewport);

    // selection 변경 뒤 hover provider가 해당 줄의 분석 결과를 읽도록 다음 이벤트 루프에서 실행한다.
    await new Promise<void>((resolve) => setTimeout(resolve, 0));
    await vscode.commands.executeCommand('editor.action.showHover');
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

function findingRange(
  document: vscode.TextDocument,
  finding: Finding,
): vscode.Range {
  const line = Math.min(Math.max(finding.line, 0), Math.max(document.lineCount - 1, 0));
  const lineLength = document.lineAt(line).text.length;
  const start = Math.min(Math.max(finding.startCol, 0), lineLength);
  const end = Math.min(Math.max(finding.endCol, start), lineLength);
  return new vscode.Range(line, start, line, end);
}
