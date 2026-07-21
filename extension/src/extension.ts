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
import { DiagnosticsManager } from './diagnostics';
import { RiskPanelProvider } from './riskPanel';
import { StatusBarManager } from './statusBar';
import { VibeSafeCodeActionProvider, applyAllFixes } from './codeActions';

/** 분석 대상 언어 */
const SUPPORTED = new Set(['python', 'javascript', 'typescript', 'javascriptreact', 'typescriptreact', 'java', 'go', 'php', 'ruby']);

export function activate(context: vscode.ExtensionContext): void {
  let analyzer: Analyzer = createAnalyzer();
  const diagnostics = new DiagnosticsManager(context);
  const statusBar = new StatusBarManager(context);
  const codeActions = new VibeSafeCodeActionProvider();
  const panel = new RiskPanelProvider({
    onApplyFixes: () => applyAllFixes(panel.getLastResult()),
    onScan: () => vscode.commands.executeCommand('vibesafe.analyzeFile'),
  });

  context.subscriptions.push(
    vscode.window.registerWebviewViewProvider(RiskPanelProvider.viewId, panel),
    vscode.languages.registerCodeActionsProvider(
      [...SUPPORTED].map((language) => ({ language })),
      codeActions,
      VibeSafeCodeActionProvider.metadata,
    ),
  );

  /** 검사 1회 실행 — 유일한 분석 진입점 (버튼/명령에서만 호출됨) */
  async function runScan(retrying = false): Promise<void> {
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

    statusBar.setScanning();
    try {
      const result = await analyzer.analyze(doc.getText(), doc.fileName, doc.languageId);
      diagnostics.update(doc.uri, result);
      codeActions.setResult(doc.uri, result);
      statusBar.update(result);
      panel.update(result);
    } catch (err) {
      if (retrying) {
        statusBar.setIdle();
        return;
      }
      // 원격(서버) 엔진 실패 시: 알리고 로컬 규칙으로 폴백해 1회 재시도
      vscode.window.showWarningMessage(
        `VibeSafe: 백엔드 분석 실패 (${err instanceof Error ? err.message : err}). 로컬 규칙 엔진으로 전환합니다.`,
      );
      const config = vscode.workspace.getConfiguration('vibesafe');
      await config.update('engine', 'rules', vscode.ConfigurationTarget.Global);
      analyzer = createAnalyzer();
      await runScan(true);
    }
  }

  context.subscriptions.push(
    vscode.commands.registerCommand('vibesafe.analyzeFile', () => runScan()),
    vscode.commands.registerCommand('vibesafe.showPanel', () => {
      vscode.commands.executeCommand('workbench.view.extension.vibesafe');
    }),
    // 파일 전환 시 상태바만 대기 상태로 되돌림 (이미 검사한 파일의 밑줄은 유지)
    vscode.window.onDidChangeActiveTextEditor(() => statusBar.setIdle()),
    vscode.workspace.onDidChangeConfiguration((e) => {
      if (e.affectsConfiguration('vibesafe.engine') || e.affectsConfiguration('vibesafe.remoteEndpoint')) {
        analyzer = createAnalyzer();
      }
    }),
  );
}

export function deactivate(): void {
  // 정리할 리소스는 context.subscriptions가 자동 처리
}
