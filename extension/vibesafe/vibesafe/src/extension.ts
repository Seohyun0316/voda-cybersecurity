/**
 * VibeSafe 진입점 — 모든 모듈을 조립한다.
 *
 * 흐름: [지금 코드 검사하기] 버튼 클릭 → analyzer.analyze()
 *      → diagnostics + 사이드 패널 + 상태바 + quick fix 캐시 갱신
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

  // 현재 열려 있는 에디터 문서를 검사하는 메인 함수
  async function analyzeDocument(doc: vscode.TextDocument): Promise<void> {
    if (!SUPPORTED.has(doc.languageId)) return;
    try {
      const result = await analyzer.analyze(doc.getText(), doc.fileName, doc.languageId);
      diagnostics.update(doc.uri, result);
      codeActions.setResult(doc.uri, result);
      statusBar.update(result);
      panel.update(result);
    } catch (err) {
      // 원격 엔진 실패 시 사용자에게 알리고 로컬 규칙으로 폴백
      vscode.window.showWarningMessage(
        `VibeSafe: 백엔드 분석 실패 (${err instanceof Error ? err.message : err}). 로컬 규칙 엔진으로 전환합니다.`,
      );
      const config = vscode.workspace.getConfiguration('vibesafe');
      await config.update('engine', 'rules', vscode.ConfigurationTarget.Global);
      analyzer = createAnalyzer();
      await analyzeDocument(doc);
    }
  }

  // 현재 활성화된 에디터의 문서를 검사하는 도우미 함수
  function analyzeActiveDocument() {
    const editor = vscode.window.activeTextEditor;
    if (editor) {
      analyzeDocument(editor.document);
    }
  }

  // RiskPanel 생성 시 context.extensionUri 전달
  const panel = new RiskPanelProvider(
    context.extensionUri,                      // 1번째 인자: extensionUri (media/ 접근용)
    () => applyAllFixes(panel.getLastResult()), // 2번째 인자: 자동 수정 버튼
    () => analyzeActiveDocument()               // 3번째 인자: [🔍 지금 코드 검사하기] 버튼
  );

  context.subscriptions.push(
    vscode.window.registerWebviewViewProvider(RiskPanelProvider.viewId, panel),
    vscode.languages.registerCodeActionsProvider(
      [...SUPPORTED].map((language) => ({ language })),
      codeActions,
      VibeSafeCodeActionProvider.metadata,
    ),
  );

  context.subscriptions.push(
    // 💡 탭 전환 시 0.7초 지연 후 검사 실행
    vscode.window.onDidChangeActiveTextEditor((editor) => {
      if (editor) {
        const targetDoc = editor.document;
        setTimeout(() => {
          if (vscode.window.activeTextEditor?.document === targetDoc) {
            analyzeDocument(targetDoc);
          }
        }, 700);
      } else {
        statusBar.setIdle();
      }
    }),
    vscode.workspace.onDidChangeConfiguration((e) => {
      if (e.affectsConfiguration('vibesafe.engine') || e.affectsConfiguration('vibesafe.remoteEndpoint')) {
        analyzer = createAnalyzer();
        const editor = vscode.window.activeTextEditor;
        if (editor) analyzeDocument(editor.document);
      }
    }),
    vscode.commands.registerCommand('vibesafe.analyzeFile', () => {
      analyzeActiveDocument();
    }),
    vscode.commands.registerCommand('vibesafe.showPanel', () => {
      vscode.commands.executeCommand('workbench.view.extension.vibesafe');
    }),
  );

  // 💡 시작 시에도 0.7초 지연 후 검사 실행
  if (vscode.window.activeTextEditor) {
    const initialDoc = vscode.window.activeTextEditor.document;
    setTimeout(() => {
      if (vscode.window.activeTextEditor?.document === initialDoc) {
        analyzeDocument(initialDoc);
      }
    }, 700);
  }
}

export function deactivate(): void {
  // 정리할 리소스는 context.subscriptions가 자동 처리
}