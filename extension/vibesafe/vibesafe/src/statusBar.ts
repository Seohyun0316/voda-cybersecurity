/**
 * 상태바 아이템 (F1 담당). 목업의 "VibeSafe: 위험 3" 부분.
 */
import * as vscode from 'vscode';
import { AnalysisResult } from './analyzer';

export class StatusBarManager {
  private readonly item: vscode.StatusBarItem;

  constructor(context: vscode.ExtensionContext) {
    this.item = vscode.window.createStatusBarItem(vscode.StatusBarAlignment.Left, 100);
    this.item.command = 'vibesafe.showPanel';
    context.subscriptions.push(this.item);
    this.item.show();
    this.setIdle();
  }

  update(result: AnalysisResult): void {
    const n = result.findings.length;
    if (n > 0) {
      this.item.text = `$(shield) VibeSafe: 위험 ${n}`;
      this.item.backgroundColor = new vscode.ThemeColor('statusBarItem.errorBackground');
      this.item.tooltip = `위험도 ${result.riskScore}/100 — 클릭해서 상세 보기`;
    } else {
      this.item.text = `$(shield) VibeSafe: 안전`;
      this.item.backgroundColor = undefined;
      this.item.tooltip = '감지된 위험 없음';
    }
  }

  setIdle(): void {
    this.item.text = '$(shield) VibeSafe';
    this.item.backgroundColor = undefined;
    this.item.tooltip = 'VibeSafe 대기 중';
  }
}
