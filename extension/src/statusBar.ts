/**
 * 상태바 아이템 (F1 담당). 목업의 "VibeSafe: 위험 3" 부분.
 * 클릭하면 현재 파일 검사를 실행한다 (버튼 트리거 방식).
 */
import * as vscode from 'vscode';
import { AnalysisResult } from './analyzer';

export class StatusBarManager {
  private readonly item: vscode.StatusBarItem;

  constructor(context: vscode.ExtensionContext) {
    this.item = vscode.window.createStatusBarItem(vscode.StatusBarAlignment.Left, 100);
    this.item.command = 'vibesafe.analyzeFile'; // 클릭 = 검사 실행
    context.subscriptions.push(this.item);
    this.item.show();
    this.setIdle();
  }

  setIdle(): void {
    this.item.text = '$(shield) VibeSafe: 검사 대기';
    this.item.backgroundColor = undefined;
    this.item.tooltip = '클릭하면 현재 파일을 검사합니다';
  }

  setScanning(): void {
    this.item.text = '$(sync~spin) VibeSafe: 검사 중...';
    this.item.backgroundColor = undefined;
    this.item.tooltip = '분석 중';
  }

  update(result: AnalysisResult): void {
    const n = result.findings.length;
    if (n > 0) {
      this.item.text = `$(shield) VibeSafe: 위험 ${n}`;
      this.item.backgroundColor = new vscode.ThemeColor('statusBarItem.errorBackground');
      this.item.tooltip = `위험도 ${result.riskScore}/100 — 클릭하면 다시 검사합니다`;
    } else {
      this.item.text = `$(shield) VibeSafe: 안전`;
      this.item.backgroundColor = undefined;
      this.item.tooltip = '감지된 위험 없음 — 클릭하면 다시 검사합니다';
    }
  }
}
