import type { Analyzer } from './types';

/**
 * The backend currently accepts Python only. Other supported editor languages
 * use the local rule engine directly instead of producing an expected HTTP 400
 * and treating it as a backend outage.
 */
export function resolveAnalyzerKind(
  configuredEngine: string,
  languageId?: string,
): Analyzer['kind'] {
  if (configuredEngine !== 'remote') return 'rules';
  if (languageId === undefined) return 'remote';
  return languageId.trim().toLowerCase() === 'python' ? 'remote' : 'rules';
}
