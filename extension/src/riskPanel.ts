/**
 * 사이드 위험 분석 패널 (F1 담당). 목업 오른쪽 VibeSafe 패널을 WebviewView로 구현.
 * 상단 "검사 실행" 버튼(버튼 트리거 방식) + 위험도 점수 바 + 위험 목록 +
 * 법적 리스크 + 과금 경보 + 자동 수정 버튼.
 */
import * as vscode from 'vscode';
import { AnalysisResult, Finding, riskLabel } from './analyzer';

interface PanelCallbacks {
  onApplyFixes: () => void;
  onScan: () => void;
}

export class RiskPanelProvider implements vscode.WebviewViewProvider {
  static readonly viewId = 'vibesafe.riskPanel';

  private view?: vscode.WebviewView;
  private lastResult?: AnalysisResult;

  constructor(private readonly callbacks: PanelCallbacks) {}

  resolveWebviewView(view: vscode.WebviewView): void {
    this.view = view;
    view.webview.options = { enableScripts: true };
    view.webview.onDidReceiveMessage((msg) => {
      if (msg.type === 'scan') this.callbacks.onScan();
      if (msg.type === 'applyFixes') this.callbacks.onApplyFixes();
      if (msg.type === 'gotoLine') this.gotoLine(msg.line);
    });
    view.webview.html = this.render();
  }

  update(result: AnalysisResult): void {
    this.lastResult = result;
    if (this.view) this.view.webview.html = this.render();
  }

  getLastResult(): AnalysisResult | undefined {
    return this.lastResult;
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
    const legal = findings.filter((f) => f.legal);
    const cost = findings.filter((f) => f.category === 'cost');
    const scoreColor = score >= 70 ? '#f48771' : score >= 40 ? '#f0a500' : '#4caf50';

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
        (f) => `
        <div class="item">
          <span class="icon legal">⚖️</span>
          <div class="text">${escapeHtml(f.legal!.law)} ${escapeHtml(f.legal!.article)}<small>${escapeHtml(f.legal!.description)}</small></div>
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

    const body = r
      ? /* html */ `
  <div class="label">위험도 점수</div>
  <div class="bar-wrap"><div class="bar-bg"></div><div class="bar-fill" style="width:${score}%"></div></div>
  <div class="score" style="color:${scoreColor}">${score} <span>/ 100 — ${riskLabel(score)}</span></div>

  <div class="label">감지된 위험 (${findings.length})</div>
  ${findingItems || '<div class="empty">감지된 위험이 없습니다 ✅</div>'}

  <div class="label">법적 리스크</div>
  ${legalItems || '<div class="empty">해당 없음</div>'}

  <div class="label">💸 API 과금 경보</div>
  ${costItems || '<div class="empty">해당 없음</div>'}

  <button id="fix" class="secondary">자동 수정 제안 적용 →</button>
  <div class="engine">엔진: ${r.engine === 'remote' ? 'ML 백엔드' : '로컬 규칙'} · ${new Date(r.analyzedAt).toLocaleTimeString()}</div>`
      : /* html */ `
  <div class="empty" style="margin-top:14px">아직 검사한 결과가 없습니다.<br>위의 <b>▶ 현재 파일 검사</b> 버튼을 눌러 시작하세요.</div>`;

    return /* html */ `<!DOCTYPE html>
<html lang="ko">
<head>
<meta charset="UTF-8">
<style>
  body { font-family: var(--vscode-font-family); color: var(--vscode-foreground); font-size: 12px; padding: 0 8px; }
  .sub { color: var(--vscode-descriptionForeground); font-size: 10px; margin-bottom: 8px; }
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
  .empty { color: var(--vscode-descriptionForeground); padding: 4px 0; line-height: 1.6; }
  button { width: 100%; background: var(--vscode-button-background); color: var(--vscode-button-foreground); border: none; border-radius: 4px; padding: 6px; cursor: pointer; font-weight: 600; }
  button:hover { background: var(--vscode-button-hoverBackground); }
  button.secondary { margin-top: 14px; font-weight: 400; background: var(--vscode-button-secondaryBackground, var(--vscode-button-background)); color: var(--vscode-button-secondaryForeground, var(--vscode-button-foreground)); }
  .engine { margin-top: 8px; font-size: 10px; color: var(--vscode-descriptionForeground); }
</style>
</head>
<body>
  <div class="sub">실시간 보안 · 법적 위험 분석</div>

  <button id="scan">▶ 현재 파일 검사</button>
  ${body}

<script>
  const vscode = acquireVsCodeApi();
  document.getElementById('scan').addEventListener('click', () => vscode.postMessage({ type: 'scan' }));
  const fixBtn = document.getElementById('fix');
  if (fixBtn) fixBtn.addEventListener('click', () => vscode.postMessage({ type: 'applyFixes' }));
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
