/**
 * 사이드 위험 분석 패널 (F1 담당). 목업 오른쪽 VibeSafe 패널을 WebviewView로 구현.
 * 위험도 점수 바, 감지된 위험 목록, 법적 리스크, 과금 경보, 수동 검사 버튼, 자동 수정 버튼.
 */
import * as vscode from 'vscode';
import {
  AnalysisResult,
  Finding,
  compactLegalDescription,
  compactSanctionLabel,
  groupLegalRisks,
  riskLabel,
} from './analyzer';
import { DocumentSnapshot } from './documentSnapshot';

interface PanelCallbacks {
  onApplyFixes: () => void;
  onScan: () => void;
}

export class RiskPanelProvider implements vscode.WebviewViewProvider {
  static readonly viewId = 'vibesafe.riskPanel';

  private view?: vscode.WebviewView;
  private lastResult?: AnalysisResult;
  private lastSnapshot?: DocumentSnapshot;

  constructor(
    private readonly extensionUri: vscode.Uri,
    private readonly callbacks: PanelCallbacks,
  ) {}

  resolveWebviewView(view: vscode.WebviewView): void {
    this.view = view;
    view.webview.options = {
      enableScripts: true,
      localResourceRoots: [vscode.Uri.joinPath(this.extensionUri, 'media')],
    };
    view.webview.onDidReceiveMessage((msg) => {
      if (msg.type === 'runAnalysis') this.callbacks.onScan();
      if (msg.type === 'applyFixes') this.callbacks.onApplyFixes();
      if (msg.type === 'gotoLine') this.gotoLine(msg.line);
    });
    view.webview.html = this.render();
  }

  update(result: AnalysisResult, snapshot: DocumentSnapshot): void {
    this.lastResult = result;
    this.lastSnapshot = snapshot;
    if (this.view) this.view.webview.html = this.render();
  }

  getLastResult(): AnalysisResult | undefined {
    return this.lastResult;
  }

  getLastSnapshot(): DocumentSnapshot | undefined {
    return this.lastSnapshot;
  }

  private async gotoLine(line: number): Promise<void> {
    const editor = vscode.window.activeTextEditor;
    if (!editor) return;
    const pos = new vscode.Position(line, 0);
    editor.selection = new vscode.Selection(pos, pos);
    editor.revealRange(new vscode.Range(pos, pos), vscode.TextEditorRevealType.InCenter);
  }

  private render(): string {
    const r = this.lastResult;
    const score = r?.riskScore ?? 0;
    const findings = r?.findings ?? [];
    const legal = groupLegalRisks(findings);
    const cost = findings.filter(
      (f) =>
        f.category === 'cost' ||
        f.ruleId === 'exposed-api-key' ||
        f.ruleId === 'A04-798-002',
    );
    const scoreColor = score >= 70 ? '#f48771' : score >= 40 ? '#f0a500' : '#4caf50';

    const logoUri = this.view
      ? this.view.webview
          .asWebviewUri(vscode.Uri.joinPath(this.extensionUri, 'media', 'vibesafe-logo.png'))
          .toString()
      : '';

    const findingItems = findings
      .map(
        (f: Finding) => `
        <div class="item" data-line="${f.line}">
          <span class="icon ${f.severity}">${f.severity === 'error' ? '⛔' : f.severity === 'warning' ? '⚠️' : 'ℹ️'}</span>
          <div class="text">${escapeHtml(f.message)}<small>${escapeHtml(baseName(r?.fileName ?? ''))} ${f.line + 1}번 줄 — ${escapeHtml(f.detail)}</small></div>
        </div>`,
      )
      .join('');

    const legalItems = legal
      .map(
        (group) => `
        <div class="item">
          <span class="icon legal">⚖️</span>
          <div class="text">${escapeHtml(group.law)} ${escapeHtml(group.article)}
            <ul class="legal-list">${group.items
              .map(
                ({ legal: item }) =>
                  `<li>${escapeHtml(`${compactLegalDescription(item.description)} (${compactSanctionLabel(item)} 가능)`)}</li>`,
              )
              .join('')}</ul>
          </div>
        </div>`,
      )
      .join('');

    const costItems = cost
      .map(
        (f) => `
        <div class="item">
          <span class="icon cost">💸</span>
          <div class="text">${escapeHtml(f.message)}<small>${escapeHtml(f.detail)}</small></div>
        </div>`,
      )
      .join('');

    return /* html */ `<!DOCTYPE html>
<html lang="ko">
<head>
<meta charset="UTF-8">
<style>
  body { font-family: var(--vscode-font-family); color: var(--vscode-foreground); font-size: 12px; padding: 0 8px; }

  .header-container {
    display: flex;
    align-items: center;
    gap: 10px;
    margin-top: 6px;
    margin-bottom: 12px;
  }
  .logo-wrapper {
    width: 44px;
    height: 44px;
    flex-shrink: 0;
    border-radius: 50%;
    overflow: hidden;
    display: flex;
    align-items: center;
    justify-content: center;
    background: #ffffff;
    border: 1px solid #4b8bec;
    box-shadow: 0 2px 4px rgba(0, 0, 0, 0.3);
  }
  .logo-wrapper img {
    width: 100%;
    height: 100%;
    object-fit: contain;
  }
  .header-text {
    display: flex;
    flex-direction: column;
    justify-content: center;
  }
  .title-text {
    font-size: 14px;
    font-weight: 800;
    letter-spacing: 0.3px;
    color: #4b8bec;
  }
  .sub-desc {
    font-size: 11px;
    color: var(--vscode-descriptionForeground);
    margin-top: 3px;
  }
  .analyze-btn {
    width: 100%;
    margin-bottom: 12px;
    background: var(--vscode-button-secondaryBackground, #3a3d41);
    color: var(--vscode-button-secondaryForeground, #ffffff);
    border: 1px solid var(--vscode-button-border, transparent);
    border-radius: 4px;
    padding: 7px;
    font-weight: 600;
    cursor: pointer;
  }
  .analyze-btn:hover { background: var(--vscode-button-secondaryHoverBackground, #45494e); }
  .label { font-size: 10px; text-transform: uppercase; letter-spacing: 0.6px; color: var(--vscode-descriptionForeground); margin: 12px 0 6px; }
  .bar-bg { background: var(--vscode-progressBar-background, #3a3a3a); opacity: 0.3; border-radius: 3px; height: 6px; }
  .bar-wrap { position: relative; height: 6px; }
  .bar-fill { position: absolute; top: 0; left: 0; background: linear-gradient(90deg, #f0a500, #e51400); height: 6px; border-radius: 3px; }
  .score { font-size: 18px; font-weight: 600; margin-top: 6px; }
  .score span { font-size: 10px; font-weight: 400; color: var(--vscode-descriptionForeground); }
  .item { display: flex; gap: 6px; padding: 4px 0; align-items: flex-start; cursor: pointer; }
  .item:hover { background: var(--vscode-list-hoverBackground); }
  .icon { flex-shrink: 0; font-size: 12px; }
  .text { line-height: 1.4; }
  .text small { display: block; color: var(--vscode-descriptionForeground); font-size: 10px; }
  .legal-list { margin: 2px 0 0; padding-left: 14px; color: var(--vscode-descriptionForeground); font-size: 10px; line-height: 1.4; }
  .legal-list li { margin: 1px 0; }
  .empty { color: var(--vscode-descriptionForeground); padding: 4px 0; }
  button.fix-btn { width: 100%; margin-top: 14px; background: var(--vscode-button-background); color: var(--vscode-button-foreground); border: none; border-radius: 4px; padding: 6px; cursor: pointer; }
  button.fix-btn:hover { background: var(--vscode-button-hoverBackground); }
  .engine { margin-top: 8px; font-size: 10px; color: var(--vscode-descriptionForeground); }
</style>
</head>
<body>
  <div class="header-container">
    <div class="logo-wrapper">
      ${logoUri ? `<img src="${logoUri}" alt="VibeSafe Logo" />` : ''}
    </div>
    <div class="header-text">
      <div class="title-text">VIBESAFE : 위험 분석</div>
      <div class="sub-desc">실시간 보안 · 법적 위험 분석</div>
    </div>
  </div>

  <button id="run-analysis" class="analyze-btn">🔍 지금 코드 검사하기</button>

  <div class="label">위험도 점수</div>
  <div class="bar-wrap"><div class="bar-bg"></div><div class="bar-fill" style="width:${score}%"></div></div>
  <div class="score" style="color:${scoreColor}">${score} <span>/ 100 — ${riskLabel(score)}</span></div>

  <div class="label">감지된 위험 (${findings.length})</div>
  ${findingItems || '<div class="empty">감지된 위험이 없습니다 ✅</div>'}

  <div class="label">법적 리스크</div>
  ${legalItems || '<div class="empty">해당 없음</div>'}

  <div class="label">💸 API 과금 경보</div>
  ${costItems || '<div class="empty">해당 없음</div>'}

  <button id="fix" class="fix-btn">자동 수정 제안 적용 →</button>
  <div class="engine">엔진: ${r?.engine === 'remote' ? 'ML 백엔드' : '로컬 규칙'}${r ? ` · ${new Date(r.analyzedAt).toLocaleTimeString()}` : ''}</div>

<script>
  const vscode = acquireVsCodeApi();
  document.getElementById('run-analysis')?.addEventListener('click', () => {
    vscode.postMessage({ type: 'runAnalysis' });
  });
  document.getElementById('fix')?.addEventListener('click', () => vscode.postMessage({ type: 'applyFixes' }));
  document.querySelectorAll('.item[data-line]').forEach(el => {
    el.addEventListener('click', () => vscode.postMessage({ type: 'gotoLine', line: Number(el.dataset.line) }));
  });
</script>
</body>
</html>`;
  }
}

function escapeHtml(s: string): string {
  return s.replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;').replace(/"/g, '&quot;');
}

function baseName(p: string): string {
  return p.split(/[\\/]/).pop() ?? p;
}
