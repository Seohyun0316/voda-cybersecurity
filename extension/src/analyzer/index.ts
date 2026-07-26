/**
 * 분석기 팩토리 — 설정(vibesafe.engine)에 따라 엔진 선택.
 * UI 코드(F1)는 이 함수만 호출하면 되고, 엔진 내부는 몰라도 된다.
 */
import * as vscode from 'vscode';
import { Analyzer } from './types';
import { RuleEngineAnalyzer } from './ruleEngine';
import { RemoteAnalyzer } from './remoteAnalyzer';
import { resolveAnalyzerKind } from './routing';

export function createAnalyzer(languageId?: string): Analyzer {
  const config = vscode.workspace.getConfiguration('vibesafe');
  const engine = config.get<string>('engine', 'remote');

  if (resolveAnalyzerKind(engine, languageId) === 'remote') {
    const endpoint = config.get<string>('remoteEndpoint', 'http://localhost:5000/detect');
    return new RemoteAnalyzer(endpoint);
  }
  return new RuleEngineAnalyzer();
}

export * from './types';
