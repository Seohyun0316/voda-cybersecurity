/**
 * 사이드 위험 분석 패널 (F1 담당).
 * 위험도 점수, 유형별로 묶은 탐지 결과, 법적 리스크, 과금 경보를 표시한다.
 */
import * as vscode from 'vscode';
import { ConfirmedAnalysisState } from './analysisState';
import {
  AnalysisResult,
  Finding,
  compactLegalDescription,
  compactSanctionLabel,
  groupLegalRisks,
  riskLabel,
} from './analyzer';

interface PanelCallbacks {
  onScan: () => void;
}

interface FindingGroup {
  representative: Finding;
  findings: Finding[];
}

export class RiskPanelProvider implements vscode.WebviewViewProvider {
  static readonly viewId = 'vibesafe.riskPanel';

  private view?: vscode.WebviewView;
  private readonly analysis = new ConfirmedAnalysisState();

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
      if (msg.type === 'gotoLine') this.gotoLine(msg.line);
    });
    view.webview.html = this.render();
  }

  update(result: AnalysisResult): void {
    this.analysis.confirm(result);
    if (this.view) this.view.webview.html = this.render();
  }

  /**
   * 첫 문서 변경에서만 stale 상태로 전환하고 Webview를 다시 렌더링한다.
   * 이후 키 입력에서는 false를 반환하며 기존 DOM과 스크롤을 유지한다.
   */
  markStale(): boolean {
    if (!this.analysis.markStale()) return false;
    if (this.view) this.view.webview.html = this.render();
    return true;
  }

  get isStale(): boolean {
    return this.analysis.isStale;
  }

  get lastResult(): AnalysisResult | undefined {
    return this.analysis.result;
  }

  private async gotoLine(line: number): Promise<void> {
    if (this.analysis.isStale) return;
    const editor = vscode.window.activeTextEditor;
    if (!editor) return;
    const pos = new vscode.Position(line, 0);
    editor.selection = new vscode.Selection(pos, pos);
    editor.revealRange(new vscode.Range(pos, pos), vscode.TextEditorRevealType.InCenter);
  }

  private render(): string {
    const result = this.analysis.result;
    const stale = this.analysis.isStale;
    const score = result?.riskScore ?? 0;
    const findings = result?.findings ?? [];
    const findingGroups = groupFindings(findings);
    const legalGroups = groupLegalRisks(findings);
    const apiKeyCostFindings = findings.filter(isApiKeyCostFinding);
    const resourceCostFindings = findings.filter(
      (finding) => finding.category === 'cost' && !isApiKeyCostFinding(finding),
    );
    const costFindingCount = apiKeyCostFindings.length + resourceCostFindings.length;
    const scoreTone = score >= 70 ? 'high' : score >= 40 ? 'medium' : score > 0 ? 'low' : 'safe';
    const scoreColor = score >= 70 ? '#e05d44' : score >= 40 ? '#c98200' : '#2e9b65';
    const fileName = baseName(result?.fileName ?? '');

    const logoUri = this.view
      ? this.view.webview
          .asWebviewUri(vscode.Uri.joinPath(this.extensionUri, 'media', 'vibesafe-logo.png'))
          .toString()
      : '';

    const findingCards = findingGroups
      .map((group) => renderFindingGroup(group, fileName, stale))
      .join('');

    const legalCards = legalGroups
      .map(
        (group) => `
        <div class="legal-card">
          <div class="legal-heading">
            <span class="legal-icon" aria-hidden="true">⚖️</span>
            <div>
              <strong>${escapeHtml(group.law)}</strong>
              <span>${escapeHtml(group.article)}</span>
            </div>
          </div>
          <ul class="legal-list">
            ${group.items
              .map(({ legal }) => {
                const description = compactLegalDescription(legal.description) || legal.description;
                return `<li>
                  <span>${escapeHtml(description)}</span>
                  <small>${escapeHtml(compactSanctionLabel(legal))} 가능</small>
                </li>`;
              })
              .join('')}
          </ul>
        </div>`,
      )
      .join('');

    const analyzedAt = result
      ? new Date(result.analyzedAt).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
      : '';

    return /* html */ `<!DOCTYPE html>
<html lang="ko">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<style>
  * { box-sizing: border-box; }

  body {
    margin: 0;
    padding: 10px 12px 16px;
    color: var(--vscode-foreground);
    background: var(--vscode-sideBar-background);
    font-family: var(--vscode-font-family);
    font-size: 12px;
    line-height: 1.5;
  }

  button, summary { font: inherit; }

  .header {
    display: flex;
    align-items: center;
    gap: 9px;
    margin: 1px 0 12px;
  }

  .logo {
    display: grid;
    width: 36px;
    height: 36px;
    flex: 0 0 36px;
    place-items: center;
    overflow: hidden;
    border: 1px solid color-mix(in srgb, var(--vscode-focusBorder) 55%, transparent);
    border-radius: 10px;
    background: #fff;
  }

  .logo img {
    width: 100%;
    height: 100%;
    object-fit: contain;
  }

  .brand {
    color: var(--vscode-descriptionForeground);
    font-size: 9px;
    font-weight: 700;
    letter-spacing: 1.1px;
  }

  .page-title {
    margin-top: -1px;
    font-size: 15px;
    font-weight: 700;
    letter-spacing: -0.2px;
  }

  .analyze-btn {
    display: flex;
    width: 100%;
    align-items: center;
    justify-content: center;
    gap: 6px;
    margin-bottom: 12px;
    padding: 8px 10px;
    border: 1px solid #389ac1;
    border-radius: 6px;
    color: #fff;
    background: #389ac1;
    font-weight: 600;
    cursor: pointer;
  }

  .analyze-btn:hover { background: #389ac1; }
  .analyze-btn:focus-visible,
  summary:focus-visible,
  .location-link:focus-visible {
    outline: 1px solid var(--vscode-focusBorder);
    outline-offset: 2px;
  }

  .stale-notice {
    margin: 0 0 12px;
    padding: 8px 10px;
    border: 1px solid color-mix(in srgb, #c98200 40%, transparent);
    border-radius: 6px;
    color: var(--vscode-foreground);
    background: color-mix(in srgb, #c98200 10%, var(--vscode-sideBar-background));
    font-weight: 650;
  }

  .score-card {
    margin-bottom: 18px;
    padding: 12px;
    border: 1px solid var(--vscode-widget-border, transparent);
    border-radius: 8px;
    background: var(--vscode-editorWidget-background, var(--vscode-editor-background));
  }

  .score-top {
    display: flex;
    align-items: center;
    justify-content: space-between;
    margin-bottom: 7px;
  }

  .score-label {
    color: var(--vscode-descriptionForeground);
    font-size: 10px;
    font-weight: 600;
  }

  .status-badge {
    padding: 1px 7px;
    border-radius: 999px;
    color: ${scoreColor};
    background: color-mix(in srgb, ${scoreColor} 14%, transparent);
    font-size: 10px;
    font-weight: 700;
  }

  .score-value {
    display: flex;
    align-items: baseline;
    gap: 4px;
    margin-bottom: 8px;
  }

  .score-value strong {
    color: ${scoreColor};
    font-size: 24px;
    line-height: 1;
  }

  .score-value span {
    color: var(--vscode-descriptionForeground);
    font-size: 10px;
  }

  .bar {
    height: 5px;
    overflow: hidden;
    border-radius: 999px;
    background: color-mix(in srgb, var(--vscode-descriptionForeground) 18%, transparent);
  }

  .bar-fill {
    width: ${score}%;
    height: 100%;
    border-radius: inherit;
    background: ${scoreColor};
    transition: width 180ms ease;
  }

  .section { margin-top: 18px; }

  .section-heading {
    display: flex;
    align-items: baseline;
    justify-content: space-between;
    gap: 8px;
    margin: 0 1px 8px;
  }

  .section-heading h2 {
    margin: 0;
    font-size: 12px;
    font-weight: 700;
  }

  .section-heading span {
    color: var(--vscode-descriptionForeground);
    font-size: 10px;
    white-space: nowrap;
  }

  .finding-card {
    margin-bottom: 7px;
    overflow: hidden;
    border: 1px solid var(--vscode-widget-border, transparent);
    border-left: 3px solid var(--severity-color);
    border-radius: 7px;
    background: var(--vscode-editorWidget-background, var(--vscode-editor-background));
  }

  .finding-card.error { --severity-color: #e05d44; }
  .finding-card.warning { --severity-color: #c98200; }
  .finding-card.info { --severity-color: #3c8dd9; }

  .finding-card summary {
    display: flex;
    align-items: flex-start;
    gap: 8px;
    padding: 10px 9px 9px;
    list-style: none;
    cursor: pointer;
  }

  .finding-card summary::-webkit-details-marker { display: none; }
  .finding-card summary:hover { background: var(--vscode-list-hoverBackground); }

  .severity-mark {
    width: 18px;
    flex: 0 0 18px;
    margin-top: 1px;
    font-size: 14px;
    line-height: 1;
    text-align: center;
  }

  .finding-main {
    min-width: 0;
    flex: 1;
  }

  .finding-title-row {
    display: flex;
    align-items: flex-start;
    gap: 6px;
  }

  .finding-title {
    min-width: 0;
    flex: 1;
    font-weight: 650;
    line-height: 1.35;
  }

  .count-badge {
    flex: 0 0 auto;
    padding: 1px 6px;
    border-radius: 999px;
    color: var(--vscode-descriptionForeground);
    background: color-mix(in srgb, var(--vscode-descriptionForeground) 12%, transparent);
    font-size: 9px;
    white-space: nowrap;
  }

  .finding-summary {
    display: -webkit-box;
    margin: 4px 0 0;
    overflow: hidden;
    color: var(--vscode-descriptionForeground);
    line-height: 1.4;
    -webkit-box-orient: vertical;
    -webkit-line-clamp: 2;
  }

  .finding-meta {
    margin-top: 5px;
    color: var(--vscode-descriptionForeground);
    font-family: var(--vscode-editor-font-family);
    font-size: 9px;
  }

  .chevron {
    flex: 0 0 auto;
    margin-top: 1px;
    color: var(--vscode-descriptionForeground);
    font-size: 16px;
    line-height: 1;
    transition: transform 120ms ease;
  }

  details[open] .chevron { transform: rotate(90deg); }

  .finding-detail {
    margin-left: 25px;
    padding: 0 10px 10px;
    border-top: 1px solid var(--vscode-widget-border, transparent);
  }

  .detail-label {
    margin: 8px 0 2px;
    color: var(--vscode-descriptionForeground);
    font-size: 9px;
    font-weight: 700;
  }

  .detail-copy { margin: 0; }

  .locations {
    display: flex;
    flex-wrap: wrap;
    gap: 4px;
    margin-top: 6px;
  }

  .location-link {
    padding: 2px 6px;
    border: 1px solid var(--vscode-widget-border, transparent);
    border-radius: 4px;
    color: var(--vscode-textLink-foreground);
    background: var(--vscode-button-secondaryBackground);
    font-size: 9px;
    cursor: pointer;
  }

  .location-link:hover { background: var(--vscode-button-secondaryHoverBackground); }

  .location-link:disabled {
    color: var(--vscode-disabledForeground);
    background: var(--vscode-button-secondaryBackground);
    cursor: not-allowed;
    opacity: 0.75;
  }

  .legal-card {
    padding: 10px;
    border: 1px solid var(--vscode-widget-border, transparent);
    border-radius: 7px;
    background: var(--vscode-editorWidget-background, var(--vscode-editor-background));
  }

  .legal-card + .legal-card { margin-top: 7px; }

  .legal-heading {
    display: flex;
    align-items: center;
    gap: 7px;
  }

  .legal-heading > div {
    display: flex;
    min-width: 0;
    align-items: baseline;
    gap: 5px;
  }

  .legal-heading strong { font-size: 11px; }

  .legal-heading span {
    color: var(--vscode-descriptionForeground);
    font-size: 10px;
  }

  .legal-icon {
    width: 20px;
    flex: 0 0 20px;
    border-radius: 5px;
    font-size: 14px;
    line-height: 1;
    text-align: center;
  }

  .legal-list {
    margin: 8px 0 0 25px;
    padding: 0;
    list-style: none;
  }

  .legal-list li {
    display: flex;
    flex-direction: column;
    margin-top: 6px;
  }

  .legal-list small {
    color: var(--vscode-descriptionForeground);
    font-size: 9px;
  }

  .cost-alert {
    display: flex;
    gap: 8px;
    padding: 10px;
    border: 1px solid color-mix(in srgb, #c98200 35%, transparent);
    border-radius: 7px;
    background: color-mix(in srgb, #c98200 8%, var(--vscode-sideBar-background));
  }

  .cost-alert strong {
    display: block;
    margin-bottom: 2px;
    font-size: 11px;
  }

  .cost-alert p {
    margin: 0;
    color: var(--vscode-descriptionForeground);
  }

  .cost-alert + .cost-alert { margin-top: 7px; }

  .empty {
    padding: 12px 10px;
    border: 1px dashed var(--vscode-widget-border, var(--vscode-descriptionForeground));
    border-radius: 7px;
    color: var(--vscode-descriptionForeground);
    text-align: center;
  }

  .engine {
    margin-top: 16px;
    color: var(--vscode-descriptionForeground);
    font-size: 9px;
    text-align: right;
  }
</style>
</head>
<body data-score-tone="${scoreTone}">
  <header class="header">
    <div class="logo">
      ${logoUri ? `<img src="${logoUri}" alt="" />` : ''}
    </div>
    <div>
      <div class="brand">VIBESAFE</div>
      <div class="page-title">위험 분석</div>
    </div>
  </header>

  <button id="run-analysis" class="analyze-btn">
    <span aria-hidden="true">🔍</span>
    현재 코드 검사하기
  </button>

  ${stale ? '<div class="stale-notice" role="status">코드 변경됨 · 재검사 필요</div>' : ''}

  <section class="score-card" aria-label="마지막 검사 위험도">
    <div class="score-top">
      <span class="score-label">마지막 검사 위험도</span>
      <span class="status-badge">${riskLabel(score)}</span>
    </div>
    <div class="score-value">
      <strong>${score}</strong>
      <span>/ 100</span>
    </div>
    <div
      class="bar"
      role="progressbar"
      aria-label="위험도 점수"
      aria-valuemin="0"
      aria-valuemax="100"
      aria-valuenow="${score}"
    >
      <div class="bar-fill"></div>
    </div>
  </section>

  <section class="section">
    <div class="section-heading">
      <h2>감지된 위험</h2>
      <span>${findings.length}건 · ${findingGroups.length}개 유형</span>
    </div>
    ${findingCards || '<div class="empty">감지된 위험이 없습니다</div>'}
  </section>

  ${legalCards ? `
  <section class="section">
    <div class="section-heading">
      <h2>법적 리스크</h2>
      <span>${legalGroups.length}개 조항</span>
    </div>
    ${legalCards}
  </section>` : ''}

  ${costFindingCount > 0 ? `
  <section class="section">
    <div class="section-heading">
      <h2>${apiKeyCostFindings.length > 0 && resourceCostFindings.length > 0
        ? '비용·자원 경고'
        : apiKeyCostFindings.length > 0
          ? 'API 과금 경고'
          : '자원 사용 경고'}</h2>
      <span>${costFindingCount}건</span>
    </div>
    ${apiKeyCostFindings.length > 0 ? `
    <div class="cost-alert">
      <span aria-hidden="true">💸</span>
      <div>
        <strong>노출된 키를 즉시 확인하세요</strong>
        <p>무단 사용을 막기 위해 키를 폐기하고 새 키로 교체하는 것을 권장합니다.</p>
      </div>
    </div>` : ''}
    ${resourceCostFindings.length > 0 ? `
    <div class="cost-alert">
      <span aria-hidden="true">⚠️</span>
      <div>
        <strong>요청량과 자원 제한을 설정하세요</strong>
        <p>속도·반복 횟수·파일 크기에 상한을 두어 장애와 예상치 못한 비용을 방지하세요.</p>
      </div>
    </div>` : ''}
  </section>` : ''}

  <div class="engine">
    ${result ? `${result.engine === 'remote' ? 'ML 백엔드' : '로컬 규칙'} · ${escapeHtml(analyzedAt)}` : '검사 대기 중'}
  </div>

<script>
  const vscode = acquireVsCodeApi();
  document.getElementById('run-analysis')?.addEventListener('click', () => {
    vscode.postMessage({ type: 'runAnalysis' });
  });
  document.querySelectorAll('.location-link[data-line]').forEach((element) => {
    element.addEventListener('click', () => {
      vscode.postMessage({ type: 'gotoLine', line: Number(element.dataset.line) });
    });
  });
</script>
</body>
</html>`;
  }
}

function groupFindings(findings: Finding[]): FindingGroup[] {
  const groups = new Map<string, FindingGroup>();

  for (const finding of findings) {
    const key = [
      finding.ruleId,
      finding.severity,
      finding.category,
      normalizeText(finding.message),
      normalizeText(finding.detail),
    ].join('\u0000');
    const group = groups.get(key);
    if (group) {
      group.findings.push(finding);
    } else {
      groups.set(key, { representative: finding, findings: [finding] });
    }
  }

  return [...groups.values()];
}

function isApiKeyCostFinding(finding: Finding): boolean {
  return finding.ruleId === 'exposed-api-key'
    || finding.ruleId === 'A04-798-002'
    || (finding.category === 'cost' && finding.cwe?.includes('CWE-798') === true);
}

function renderFindingGroup(
  group: FindingGroup,
  fileName: string,
  stale: boolean,
): string {
  const finding = group.representative;
  const { title, summary } = presentFinding(finding);
  const lineNumbers = [...new Set(group.findings.map((item) => item.line + 1))]
    .sort((a, b) => a - b);
  const severityLabel =
    finding.severity === 'error' ? '높은 위험' : finding.severity === 'warning' ? '주의' : '정보';
  const severityMark =
    finding.severity === 'error' ? '⛔' : finding.severity === 'warning' ? '⚠️' : 'ℹ️';
  const locationSummary = formatLineSummary(lineNumbers);

  return `
    <details class="finding-card ${finding.severity}">
      <summary>
        <span class="severity-mark" aria-label="${severityLabel}">${severityMark}</span>
        <div class="finding-main">
          <div class="finding-title-row">
            <span class="finding-title">${escapeHtml(title)}</span>
            <span class="count-badge">${group.findings.length}건</span>
          </div>
          ${summary ? `<p class="finding-summary">${escapeHtml(summary)}</p>` : ''}
          <div class="finding-meta">${escapeHtml(fileName)} · ${escapeHtml(locationSummary)}</div>
        </div>
        <span class="chevron" aria-hidden="true">›</span>
      </summary>
      <div class="finding-detail">
        <div class="detail-label">권장 조치</div>
        <p class="detail-copy">${escapeHtml(finding.detail)}</p>
        <div class="detail-label">탐지 위치</div>
        <div class="locations">
          ${lineNumbers
            .map(
              (lineNumber) =>
                stale
                  ? `<button class="location-link" disabled title="코드가 변경되었습니다. 재검사 후 이동할 수 있습니다.">${lineNumber}번 line · 재검사 후 이동 가능</button>`
                  : `<button class="location-link" data-line="${lineNumber - 1}" title="${escapeHtml(fileName)} ${lineNumber}번 line으로 이동">${lineNumber}번 line</button>`,
            )
            .join('')}
        </div>
      </div>
    </details>`;
}

function presentFinding(finding: Finding): { title: string; summary: string } {
  const sentences =
    finding.message
      .trim()
      .match(/[^.!?]+[.!?]?/g)
      ?.map((sentence) => sentence.trim())
      .filter(Boolean) ?? [];
  const firstSentence = sentences.shift() ?? finding.message;
  let title = firstSentence
    .replace(/^\[ML\]\s*/i, '')
    .replace(/[.!?]+$/, '')
    .replace(/\s*(?:이|가|을|를)?\s*(?:탐지|발견|사용)되었습니다$/, '')
    .trim();

  if (
    finding.legal &&
    (title.includes(finding.legal.law) || title.includes(finding.legal.article))
  ) {
    title = title.split(/\s+[—–]\s+/)[0].trim();
  }

  const summary = sentences
    .filter((sentence) => !isLegalBoilerplate(sentence, finding))
    .slice(0, 2)
    .join(' ');

  return {
    title: title || finding.message,
    summary,
  };
}

function isLegalBoilerplate(sentence: string, finding: Finding): boolean {
  return Boolean(
    sentence.includes('관련 보안조치') ||
      sentence.includes('개인정보보호법') ||
      (finding.legal &&
        (sentence.includes(finding.legal.law) || sentence.includes(finding.legal.article))),
  );
}

function formatLineSummary(lines: number[]): string {
  if (lines.length === 0) return '위치 정보 없음';
  if (lines.length <= 3) return `${lines.join(', ')}번 line`;
  return `${lines.slice(0, 2).join(', ')}번 line 외 ${lines.length - 2}곳`;
}

function normalizeText(value: string): string {
  return value.trim().replace(/\s+/g, ' ');
}

function escapeHtml(value: string): string {
  return value
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;')
    .replace(/'/g, '&#39;');
}

function baseName(path: string): string {
  return path.split(/[\\/]/).pop() ?? path;
}
