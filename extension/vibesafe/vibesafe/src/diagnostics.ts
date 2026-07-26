/**
 * 진단(Diagnostics) 관리 (F1 담당).
 * Finding → vscode.Diagnostic 변환. 에디터 물결 밑줄 + '문제' 패널 표시를 담당.
 */
import * as vscode from 'vscode';
import { AnalysisResult, Finding, Severity } from './analyzer';

const SEVERITY_MAP: Record<Severity, vscode.DiagnosticSeverity> = {
  error: vscode.DiagnosticSeverity.Error,
  warning: vscode.DiagnosticSeverity.Warning,
  info: vscode.DiagnosticSeverity.Information,
};

export class DiagnosticsManager {
  private readonly collection: vscode.DiagnosticCollection;

  constructor(context: vscode.ExtensionContext) {
    this.collection = vscode.languages.createDiagnosticCollection('vibesafe');
    context.subscriptions.push(this.collection);
  }

  update(uri: vscode.Uri, result: AnalysisResult): void {
    this.collection.set(uri, result.findings.map(toDiagnostic));
  }

  clear(uri: vscode.Uri): void {
    this.collection.delete(uri);
  }
}

function toDiagnostic(f: Finding): vscode.Diagnostic {
  const range = new vscode.Range(f.line, f.startCol, f.line, f.endCol);
  const d = new vscode.Diagnostic(range, `${f.message} — ${f.detail}`, SEVERITY_MAP[f.severity]);
  d.source = 'VibeSafe';
  d.code = f.ruleId;
  return d;
}
