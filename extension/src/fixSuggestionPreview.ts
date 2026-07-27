/**
 * replacement를 적용했을 때 사용자에게 보여줄 코드 미리보기.
 *
 * 새 응답은 replaceEntireLine으로 줄 전체/범위 교체를 명시한다. 이 값이 없는
 * 구버전 응답에는 기존 줄 시작 휴리스틱을 유지한다.
 */
export function buildSuggestedCodePreview(
  line: string,
  startColumn: number,
  endColumn: number,
  replacement: string,
  replaceEntireLine?: boolean,
): string {
  const firstCodeColumn = line.length - line.trimStart().length;
  if (
    replaceEntireLine === true
    || (
      replaceEntireLine === undefined
      && startColumn === firstCodeColumn
      && endColumn < line.length
    )
  ) {
    const indentation = line.slice(0, firstCodeColumn);
    return replacement
      .split(/\r?\n/)
      .map((replacementLine) => indentation + replacementLine)
      .join('\n');
  }
  return line.slice(0, startColumn)
    + replacement
    + line.slice(endColumn);
}

/** Hover에서 변경 전·후를 한눈에 비교할 수 있는 diff 코드 블록을 만든다. */
export function buildSuggestedCodeDiff(
  originalLine: string,
  suggestedCode: string,
): string {
  const removed = originalLine
    .split(/\r?\n/)
    .map((line) => `- ${line}`);
  const added = suggestedCode
    .split(/\r?\n/)
    .map((line) => `+ ${line}`);

  return [...removed, ...added].join('\n');
}
