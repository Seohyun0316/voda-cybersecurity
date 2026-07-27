/**
 * VibeSafe 진입점 — 모든 모듈을 조립한다.
 *
 * 동작 방식 (팀 확정): 자동 검사 없음.
 * 사용자가 검사 버튼을 눌렀을 때만 현재 열린 파일 하나를 검사한다.
 * 검사 진입점: 에디터 타이틀 방패 버튼 / 사이드 패널 "검사 실행" 버튼 /
 *             상태바 클릭 / 명령 팔레트 "VibeSafe: 현재 파일 검사"
 */
import * as vscode from 'vscode';
import { createAnalyzer, Analyzer } from './analyzer';
import { RuleEngineAnalyzer } from './analyzer/ruleEngine';
import { DiagnosticsManager } from './diagnostics';
import { RiskPanelProvider } from './riskPanel';
import { StatusBarManager } from './statusBar';
import { VibeSafeCodeActionProvider } from './codeActions';
import { createDocumentSnapshot } from './documentSnapshot';
import { isAnalysisResultCurrent } from './analysisFreshness';

/** 분석 대상 언어 */
const SUPPORTED = new Set(['python', 'javascript', 'typescript', 'javascriptreact', 'typescriptreact', 'java', 'go', 'php', 'ruby']);

export function activate(context: vscode.ExtensionContext): void {
  const diagnostics = new DiagnosticsManager(context);
  const statusBar = new StatusBarManager(context);
  const codeActions = new VibeSafeCodeActionProvider();
  let latestScanId = 0;
  const panel = new RiskPanelProvider(
    context.extensionUri,
    {
      onScan: () => vscode.commands.executeCommand('vibesafe.analyzeFile'),
    },
  );

  context.subscriptions.push(
    vscode.window.registerWebviewViewProvider(RiskPanelProvider.viewId, panel),
    vscode.languages.registerCodeActionsProvider(
      [...SUPPORTED].map((language) => ({ language })),
      codeActions,
      VibeSafeCodeActionProvider.metadata,
    ),
    vscode.languages.registerHoverProvider(
      [...SUPPORTED].map((language) => ({ language })),
      codeActions,
    ),
  );

  /** 검사 1회 실행 — 유일한 분석 진입점 (버튼/명령에서만 호출됨) */
  async function runScan(
    retrying = false,
    activeAnalyzer?: Analyzer,
    existingScanId?: number,
  ): Promise<void> {
    const scanId = existingScanId ?? ++latestScanId;
    const editor = vscode.window.activeTextEditor;
    if (!editor) {
      vscode.window.showInformationMessage('VibeSafe: 검사할 파일을 먼저 열어주세요.');
      return;
    }
    const doc = editor.document;
    if (!SUPPORTED.has(doc.languageId)) {
      vscode.window.showInformationMessage(`VibeSafe: 지원하지 않는 파일 형식입니다 (${doc.languageId}).`);
      return;
    }
    const selectedAnalyzer = activeAnalyzer ?? createAnalyzer(doc.languageId);
    const analyzedText = doc.getText();
    const analyzedSnapshot = createDocumentSnapshot(
      doc.uri.toString(),
      doc.version,
      analyzedText,
    );

    statusBar.setScanning();
    try {
      const result = await selectedAnalyzer.analyze(
        analyzedText,
        doc.fileName,
        doc.languageId,
      );
      if (!isCurrentScan(scanId, analyzedSnapshot)) {
        if (scanId === latestScanId) statusBar.setIdle();
        return;
      }
      diagnostics.update(doc.uri, result);
      codeActions.setResult(result, analyzedSnapshot);
      statusBar.update(result);
      panel.update(result);
    } catch (err) {
      if (!isCurrentScan(scanId, analyzedSnapshot)) {
        if (scanId === latestScanId) statusBar.setIdle();
        return;
      }
      if (retrying) {
        statusBar.setIdle();
        return;
      }
      if (selectedAnalyzer.kind !== 'remote') {
        statusBar.setIdle();
        vscode.window.showErrorMessage(
          `VibeSafe: 로컬 분석 실패 (${err instanceof Error ? err.message : err}).`,
        );
        return;
      }
      // 원격 엔진 실패 시 이번 검사만 로컬 규칙으로 재시도한다.
      // 사용자 설정은 변경하지 않아 다음 검사에서 백엔드 연결을 다시 시도한다.
      vscode.window.showWarningMessage(
        `VibeSafe: 백엔드 분석 실패 (${err instanceof Error ? err.message : err}). 이번 검사만 로컬 규칙 엔진을 사용합니다.`,
      );
      await runScan(true, new RuleEngineAnalyzer(), scanId);
    }
  }

  function isCurrentScan(
    scanId: number,
    analyzedSnapshot: ReturnType<typeof createDocumentSnapshot>,
  ): boolean {
    const activeDocument = vscode.window.activeTextEditor?.document;
    const currentSnapshot = activeDocument
      ? createDocumentSnapshot(
          activeDocument.uri.toString(),
          activeDocument.version,
          activeDocument.getText(),
        )
      : undefined;

    return isAnalysisResultCurrent(
      scanId,
      latestScanId,
      analyzedSnapshot,
      currentSnapshot,
    );
  }

  context.subscriptions.push(
    vscode.commands.registerCommand('vibesafe.analyzeFile', () => runScan()),
    vscode.commands.registerCommand(
      'vibesafe.showFixSuggestion',
      (uri: vscode.Uri, finding: Parameters<VibeSafeCodeActionProvider['showSuggestion']>[1]) =>
        codeActions.showSuggestion(uri, finding),
    ),
    vscode.commands.registerCommand('vibesafe.showPanel', () => {
      vscode.commands.executeCommand('workbench.view.extension.vibesafe');
    }),
    // 파일 전환 시 상태바만 대기 상태로 되돌림 (이미 검사한 파일의 밑줄은 유지)
    vscode.window.onDidChangeActiveTextEditor(() => statusBar.setIdle()),
  );
}

export function deactivate(): void {
  // 정리할 리소스는 context.subscriptions가 자동 처리
}
